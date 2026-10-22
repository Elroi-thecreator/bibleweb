"""
Data models and schemas for queued WhatsApp tasks.
"""

from enum import Enum
import time
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Supported WhatsApp task types."""
    INCOMING_MESSAGE = "incoming_message"
    OUTGOING_TEXT = "outgoing_text"
    OUTGOING_MEDIA = "outgoing_media"
    BROADCAST = "broadcast"


class QueueTask(BaseModel):
    """Task payload published to and consumed from RabbitMQ queues."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType
    payload: Dict[str, Any]
    created_at: float = Field(default_factory=time.time)
    session_id: Optional[str] = None
    retries: int = 0
    max_retries: int = 3

    model_config = {"extra": "ignore"}
