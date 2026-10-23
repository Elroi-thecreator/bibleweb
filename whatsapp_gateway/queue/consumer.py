"""
RabbitMQ Task Consumer & Worker Engine for WhatsApp Gateway.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Callable, Dict, Optional

from whatsapp_gateway.client.models import IncomingWebhookPayload
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher
from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.bot.session_store import BaseSessionStore
from whatsapp_gateway.queue.connection import RabbitMQConnection
from whatsapp_gateway.queue.models import QueueTask, TaskType

logger = logging.getLogger("whatsapp_gateway.queue.consumer")


class QueueConsumer:
    """Consumes tasks from RabbitMQ and dispatches them asynchronously."""

    def __init__(
        self,
        connection_manager: RabbitMQConnection,
        dispatcher: BotDispatcher,
        client: WAClient,
        session_store: BaseSessionStore,
        prefetch_count: int = 10,
    ):
        self.conn = connection_manager
        self.dispatcher = dispatcher
        self.client = client
        self.session_store = session_store
        self.prefetch_count = prefetch_count

        self._running = False
        self._incoming_task: Optional[asyncio.Task] = None
        self._outgoing_task: Optional[asyncio.Task] = None

        # Metrics counters
        self.processed_count = 0
        self.failed_count = 0

    async def start(
        self,
        incoming_queue: str,
        outgoing_queue: str,
    ) -> None:
        """Starts background consumption loops for incoming and outgoing queues."""
        if self._running:
            return

        self._running = True
        self._incoming_task = asyncio.create_task(
            self._consume_queue(incoming_queue, self._handle_incoming_task),
            name="whatsapp-consumer-incoming",
        )
        self._outgoing_task = asyncio.create_task(
            self._consume_queue(outgoing_queue, self._handle_outgoing_task),
            name="whatsapp-consumer-outgoing",
        )
        logger.info(
            "RabbitMQ WhatsApp consumers started for queues '%s' and '%s' (prefetch=%d)",
            incoming_queue,
            outgoing_queue,
            self.prefetch_count,
        )

    async def stop(self) -> None:
        """Stops background consumption tasks cleanly."""
        self._running = False
        for task in (self._incoming_task, self._outgoing_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._incoming_task = None
        self._outgoing_task = None
        logger.info("RabbitMQ WhatsApp consumers stopped.")

    async def _consume_queue(
        self,
        queue_name: str,
        handler: Callable[[QueueTask], Any],
    ) -> None:
        """Continuously consumes messages from the specified queue."""
        while self._running:
            try:
                channel = await self.conn.get_channel()
                await channel.set_qos(prefetch_count=self.prefetch_count)

                queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        if not self._running:
                            break

                        async with message.process(requeue=True):
                            try:
                                raw_body = message.body.decode("utf-8")
                                task_dict = json.loads(raw_body)
                                task = QueueTask.model_validate(task_dict)

                                await handler(task)
                                self.processed_count += 1

                            except asyncio.CancelledError:
                                raise
                            except Exception as task_err:
                                self.failed_count += 1
                                logger.error(
                                    "Error processing queued task from '%s': %s",
                                    queue_name,
                                    task_err,
                                    exc_info=True,
                                )

            except asyncio.CancelledError:
                break
            except Exception as conn_err:
                if self._running:
                    logger.warning(
                        "Consumer connection error on '%s' (%s). Retrying in 3 seconds...",
                        queue_name,
                        conn_err,
                    )
                    await asyncio.sleep(3.0)

    async def _handle_incoming_task(self, task: QueueTask) -> None:
        """Processes an incoming WhatsApp message payload consumed from queue."""
        logger.debug("Executing incoming task %s from queue", task.task_id)
        payload = IncomingWebhookPayload.model_validate(task.payload)

        ctx = MessageContext(
            payload=payload,
            client=self.client,
            session_store=self.session_store,
            session_id=task.session_id or payload.session_id or self.client.default_session_id,
        )

        await self.dispatcher.dispatch(ctx)

    async def _handle_outgoing_task(self, task: QueueTask) -> None:
        """
        Processes an outgoing text or media task consumed from RabbitMQ.
        Guarantees dispatch only when the WA-AKG gateway is actively running,
        automatically polling and waiting if the gateway is sleeping (Render cold start) or restarting.
        """
        logger.debug("Executing outgoing task %s (%s) from queue", task.task_id, task.task_type.value)
        data = task.payload

        # In live gateway mode, ensure gateway is actively running before attempting dispatch
        if not self.client.simulation_mode:
            is_running = await self.client.is_gateway_running()
            if not is_running:
                logger.warning(
                    "WA-AKG Gateway (%s) is offline/sleeping. "
                    "Holding task %s until gateway is awake and running...",
                    self.client.base_url,
                    task.task_id,
                )
                is_running = await self.client.wait_until_gateway_running(poll_interval=5.0)
                if not is_running and not self._running:
                    raise asyncio.CancelledError()
                logger.info(
                    "WA-AKG Gateway (%s) is now RUNNING! Resuming dispatch for task %s...",
                    self.client.base_url,
                    task.task_id,
                )

        # Attempt dispatch with automatic retry if gateway drops connection during dispatch
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                if task.task_type == TaskType.OUTGOING_TEXT:
                    res = await self.client.send_text(
                        to=data["to"],
                        text=data["text"],
                        session_id=task.session_id,
                        direct_http=True,
                    )
                elif task.task_type == TaskType.OUTGOING_MEDIA:
                    file_bytes = None
                    if "bytes_b64" in data and data["bytes_b64"]:
                        file_bytes = base64.b64decode(data["bytes_b64"])
                    elif "bytes_hex" in data and data["bytes_hex"]:
                        file_bytes = bytes.fromhex(data["bytes_hex"])

                    res = await self.client.send_media(
                        to=data["to"],
                        media_type=data.get("media_type", "audio"),
                        file_bytes=file_bytes,
                        caption=data.get("caption"),
                        file_name=data.get("file_name"),
                        ptt=data.get("ptt", False),
                        session_id=task.session_id,
                        direct_http=True,
                    )
                else:
                    logger.warning("Unrecognized outgoing task type %s for task %s", task.task_type, task.task_id)
                    return

                if res.success:
                    logger.info("Successfully dispatched task %s (message_id=%s)", task.task_id, res.message_id)
                    return

                # If connection error occurs mid-dispatch, wait for gateway recovery
                if not self.client.simulation_mode and attempt < max_attempts:
                    err_text = str(res.error or "").lower()
                    if any(x in err_text for x in ("connect", "timeout", "502", "503", "504", "refused", "unreachable")):
                        logger.warning(
                            "Gateway connection error on task %s (attempt %d/%d): %s. Waiting for gateway...",
                            task.task_id, attempt, max_attempts, res.error,
                        )
                        await self.client.wait_until_gateway_running(poll_interval=5.0)
                        continue

                logger.error("Failed to dispatch task %s: %s", task.task_id, res.error)
                return

            except Exception as exc:
                if not self.client.simulation_mode and attempt < max_attempts:
                    logger.warning(
                        "Exception during dispatch of task %s (attempt %d/%d): %s. Waiting for gateway...",
                        task.task_id, attempt, max_attempts, exc,
                    )
                    await self.client.wait_until_gateway_running(poll_interval=5.0)
                    continue
                raise
