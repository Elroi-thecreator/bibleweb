"""
RabbitMQ Asynchronous Task Queue Package for WhatsApp Gateway.
"""

from whatsapp_gateway.queue.constants import (
    DEFAULT_DEAD_LETTER_QUEUE,
    DEFAULT_INCOMING_QUEUE,
    DEFAULT_OUTGOING_QUEUE,
)
from whatsapp_gateway.queue.models import QueueTask, TaskType
from whatsapp_gateway.queue.manager import QueueManager, queue_manager

__all__ = [
    "QueueManager",
    "queue_manager",
    "QueueTask",
    "TaskType",
    "DEFAULT_INCOMING_QUEUE",
    "DEFAULT_OUTGOING_QUEUE",
    "DEFAULT_DEAD_LETTER_QUEUE",
]
