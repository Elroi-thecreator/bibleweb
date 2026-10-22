"""
RabbitMQ Task Publisher for WhatsApp Gateway.
"""

import json
import logging
from typing import Optional

from whatsapp_gateway.queue.connection import RabbitMQConnection
from whatsapp_gateway.queue.models import QueueTask

logger = logging.getLogger("whatsapp_gateway.queue.publisher")


class QueuePublisher:
    """Publishes QueueTask instances to persistent RabbitMQ queues."""

    def __init__(self, connection_manager: RabbitMQConnection):
        self.conn = connection_manager

    async def publish_task(
        self,
        task: QueueTask,
        queue_name: str,
        durable: bool = True,
    ) -> bool:
        """
        Publishes a task payload to the designated queue with message persistence.
        """
        try:
            import aio_pika

            channel = await self.conn.get_channel()

            # Declare durable queue
            queue = await channel.declare_queue(
                queue_name,
                durable=durable,
                auto_delete=False,
            )

            body = task.model_dump_json().encode("utf-8")
            message = aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                message_id=task.task_id,
                headers={"task_type": task.task_type.value, "retries": task.retries},
            )

            await channel.default_exchange.publish(
                message,
                routing_key=queue_name,
            )

            logger.debug(
                "Enqueued task %s (%s) onto RabbitMQ queue '%s'",
                task.task_id,
                task.task_type.value,
                queue_name,
            )
            return True

        except Exception as exc:
            logger.error(
                "Failed to publish task %s to queue '%s': %s",
                task.task_id,
                queue_name,
                exc,
            )
            return False
