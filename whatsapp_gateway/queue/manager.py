"""
Unified Queue Manager for WhatsApp Gateway.
Provides an optional RabbitMQ asynchronous queue layer with transparent
fallback to direct in-memory execution when the queue is disabled or unreachable.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from whatsapp_gateway.config import config, save_persisted_config
from whatsapp_gateway.client.models import IncomingWebhookPayload, MediaType, SendMessageResponse
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher
from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.bot.session_store import BaseSessionStore
from whatsapp_gateway.queue.connection import RabbitMQConnection, mask_amqp_url
from whatsapp_gateway.queue.publisher import QueuePublisher
from whatsapp_gateway.queue.consumer import QueueConsumer
from whatsapp_gateway.queue.models import QueueTask, TaskType
from whatsapp_gateway.queue.constants import (
    DEFAULT_INCOMING_QUEUE,
    DEFAULT_OUTGOING_QUEUE,
)

logger = logging.getLogger("whatsapp_gateway.queue.manager")


class QueueManager:
    """
    Central queue manager orchestrating optional RabbitMQ background task workers
    with seamless fallback to direct in-memory dispatch.
    """

    def __init__(self):
        self._dispatcher: Optional[BotDispatcher] = None
        self._client: Optional[WAClient] = None
        self._session_store: Optional[BaseSessionStore] = None

        self._conn: Optional[RabbitMQConnection] = None
        self._publisher: Optional[QueuePublisher] = None
        self._consumer: Optional[QueueConsumer] = None

        self._started = False
        self._lock = asyncio.Lock()

        # Telemetry metrics
        self.enqueued_incoming = 0
        self.enqueued_outgoing = 0
        self.direct_dispatches = 0

    @property
    def is_enabled(self) -> bool:
        """Whether queue mode is enabled in configuration."""
        return bool(config.queue_enabled)

    @property
    def is_connected(self) -> bool:
        """Whether active connection to RabbitMQ is established."""
        return bool(self._conn and self._conn.is_connected)

    @property
    def is_ready(self) -> bool:
        """Whether queue is both enabled and actively connected."""
        return self.is_enabled and self.is_connected

    @property
    def backend_name(self) -> str:
        """Current operational backend name ('rabbitmq' or 'direct')."""
        return "rabbitmq" if self.is_ready else "direct"

    def initialize(
        self,
        dispatcher: BotDispatcher,
        client: WAClient,
        session_store: BaseSessionStore,
    ) -> None:
        """Registers the bot runtime dependencies."""
        self._dispatcher = dispatcher
        self._client = client
        self._session_store = session_store

        self._conn = RabbitMQConnection(url=config.rabbitmq_url)
        self._publisher = QueuePublisher(self._conn)
        self._consumer = QueueConsumer(
            connection_manager=self._conn,
            dispatcher=dispatcher,
            client=client,
            session_store=session_store,
            prefetch_count=config.queue_prefetch,
        )

    async def start(self) -> bool:
        """
        Starts the queue manager. If queue is enabled, connects to RabbitMQ
        and begins consuming background tasks. Falls back gracefully if broker is offline.
        """
        async with self._lock:
            if not self.is_enabled:
                logger.info("WhatsApp Queue is disabled (mode=direct); using direct in-memory execution.")
                return True

            if not self._conn:
                self._conn = RabbitMQConnection(url=config.rabbitmq_url)
                self._publisher = QueuePublisher(self._conn)

            logger.info("WhatsApp Queue is enabled. Attempting RabbitMQ connection to %s...", mask_amqp_url(config.rabbitmq_url))
            connected = await self._conn.connect(timeout=4.0)

            if connected and self._consumer:
                await self._consumer.start(
                    incoming_queue=config.queue_incoming_name or DEFAULT_INCOMING_QUEUE,
                    outgoing_queue=config.queue_outgoing_name or DEFAULT_OUTGOING_QUEUE,
                )
                self._started = True
                return True
            else:
                logger.warning(
                    "RabbitMQ unavailable at %s. Gracefully falling back to direct mode.",
                    mask_amqp_url(config.rabbitmq_url),
                )
                return False

    async def stop(self) -> None:
        """Stops background consumers and closes RabbitMQ connection."""
        async with self._lock:
            if self._consumer:
                await self._consumer.stop()
            if self._conn:
                await self._conn.close()
            self._started = False

    async def enqueue_incoming(
        self,
        payload: IncomingWebhookPayload,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Handles incoming webhook messages.
        If RabbitMQ is ready, enqueues to incoming queue for worker consumption.
        Otherwise, executes synchronously via direct dispatcher.
        """
        sess = session_id or payload.session_id or (self._client.default_session_id if self._client else "default")

        if self.is_ready and self._publisher:
            task = QueueTask(
                task_type=TaskType.INCOMING_MESSAGE,
                payload=payload.model_dump(),
                session_id=sess,
            )
            incoming_q = config.queue_incoming_name or DEFAULT_INCOMING_QUEUE
            success = await self._publisher.publish_task(task, queue_name=incoming_q)

            if success:
                self.enqueued_incoming += 1
                return {
                    "status": "queued",
                    "task_id": task.task_id,
                    "queue": incoming_q,
                    "backend": "rabbitmq",
                }
            logger.warning("Failed to enqueue task %s to RabbitMQ. Falling back to direct dispatch.", task.task_id)

        # Direct in-memory fallback
        self.direct_dispatches += 1
        if not self._dispatcher or not self._client or not self._session_store:
            raise RuntimeError("QueueManager has not been initialized with dispatcher and client.")

        ctx = MessageContext(
            payload=payload,
            client=self._client,
            session_store=self._session_store,
            session_id=sess,
        )
        dispatched = await self._dispatcher.dispatch(ctx)
        return {
            "status": "success" if dispatched else "unhandled",
            "backend": "direct",
            "dispatched": dispatched,
        }

    async def enqueue_outgoing_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enqueues an outgoing text message to the outgoing queue or dispatches directly.
        """
        sess = session_id or (self._client.default_session_id if self._client else "default")

        if self.is_ready and self._publisher:
            task = QueueTask(
                task_type=TaskType.OUTGOING_TEXT,
                payload={"to": to, "text": text},
                session_id=sess,
            )
            outgoing_q = config.queue_outgoing_name or DEFAULT_OUTGOING_QUEUE
            success = await self._publisher.publish_task(task, queue_name=outgoing_q)

            if success:
                self.enqueued_outgoing += 1
                return {
                    "status": "queued",
                    "task_id": task.task_id,
                    "queue": outgoing_q,
                    "backend": "rabbitmq",
                }

        # Direct fallback
        if not self._client:
            raise RuntimeError("QueueManager has not been initialized with client.")
        res = await self._client.send_text(to=to, text=text, session_id=sess, direct_http=True)
        return {
            "status": "dispatched",
            "backend": "direct",
            "success": res.success,
            "message_id": res.message_id,
            "error": res.error,
        }

    async def enqueue_outgoing_media(
        self,
        to: str,
        media_type: Union[MediaType, str] = MediaType.AUDIO,
        file_path: Optional[Union[str, Path]] = None,
        file_bytes: Optional[bytes] = None,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        ptt: bool = False,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enqueues an outgoing media message (audio clip, voice note) to RabbitMQ
        or dispatches directly in-memory if queue is offline.
        """
        sess = session_id or (self._client.default_session_id if self._client else "default")
        m_type = media_type.value if hasattr(media_type, "value") else str(media_type)

        raw_bytes = file_bytes
        resolved_name = file_name
        if file_path:
            p = Path(file_path)
            if not resolved_name:
                resolved_name = p.name
            if not raw_bytes and p.is_file():
                raw_bytes = p.read_bytes()

        bytes_b64 = base64.b64encode(raw_bytes).decode("ascii") if raw_bytes else None

        if self.is_ready and self._publisher:
            task = QueueTask(
                task_type=TaskType.OUTGOING_MEDIA,
                payload={
                    "to": to,
                    "media_type": m_type,
                    "bytes_b64": bytes_b64,
                    "caption": caption,
                    "file_name": resolved_name,
                    "ptt": ptt,
                },
                session_id=sess,
            )
            outgoing_q = config.queue_outgoing_name or DEFAULT_OUTGOING_QUEUE
            success = await self._publisher.publish_task(task, queue_name=outgoing_q)

            if success:
                self.enqueued_outgoing += 1
                return {
                    "status": "queued",
                    "task_id": task.task_id,
                    "queue": outgoing_q,
                    "backend": "rabbitmq",
                }

        # Direct fallback
        if not self._client:
            raise RuntimeError("QueueManager has not been initialized with client.")
        res = await self._client.send_media(
            to=to,
            media_type=media_type,
            file_path=file_path,
            file_bytes=raw_bytes,
            caption=caption,
            file_name=resolved_name,
            ptt=ptt,
            session_id=sess,
            direct_http=True,
        )
        return {
            "status": "dispatched",
            "backend": "direct",
            "success": res.success,
            "message_id": res.message_id,
            "error": res.error,
        }

    async def set_enabled(
        self,
        enabled: bool,
        rabbitmq_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Toggles queue mode at runtime, optionally updating the RabbitMQ URL.
        Persists selection to data/whatsapp_config.json.
        """
        config.queue_enabled = bool(enabled)
        if rabbitmq_url:
            config.rabbitmq_url = rabbitmq_url.strip()

        save_persisted_config(
            queue_enabled=config.queue_enabled,
            rabbitmq_url=config.rabbitmq_url,
        )

        if enabled:
            if self._conn:
                await self._conn.close()
            self._conn = RabbitMQConnection(url=config.rabbitmq_url)
            self._publisher = QueuePublisher(self._conn)
            if self._dispatcher and self._client and self._session_store:
                self._consumer = QueueConsumer(
                    connection_manager=self._conn,
                    dispatcher=self._dispatcher,
                    client=self._client,
                    session_store=self._session_store,
                    prefetch_count=config.queue_prefetch,
                )
            await self.start()
        else:
            await self.stop()

        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive queue status and telemetry metrics."""
        consumer_processed = self._consumer.processed_count if self._consumer else 0
        consumer_failed = self._consumer.failed_count if self._consumer else 0

        return {
            "enabled": self.is_enabled,
            "backend": self.backend_name,
            "connected": self.is_connected,
            "rabbitmq_url": mask_amqp_url(config.rabbitmq_url),
            "gateway_url": self._client.base_url if self._client else config.gateway_url,
            "queues": {
                "incoming": config.queue_incoming_name or DEFAULT_INCOMING_QUEUE,
                "outgoing": config.queue_outgoing_name or DEFAULT_OUTGOING_QUEUE,
            },
            "prefetch": config.queue_prefetch,
            "metrics": {
                "enqueued_incoming": self.enqueued_incoming,
                "enqueued_outgoing": self.enqueued_outgoing,
                "consumer_processed": consumer_processed,
                "consumer_failed": consumer_failed,
                "direct_dispatches": self.direct_dispatches,
            },
        }


# Global singleton instance
queue_manager = QueueManager()
