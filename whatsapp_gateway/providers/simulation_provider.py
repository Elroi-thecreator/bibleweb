"""
Simulation WhatsApp Provider Plugin.
Provides an in-memory virtual assistant provider for local development, automated testing,
and browser simulator without requiring any physical phone or cloud service.
"""

from typing import Any, Dict, List, Optional, Union
import uuid

from whatsapp_gateway.providers.base import BaseWhatsAppProvider
from whatsapp_gateway.client.models import (
    IncomingWebhookPayload,
    MediaType,
    SendMessageResponse,
)


class SimulationProvider(BaseWhatsAppProvider):
    """
    Simulated in-memory provider.
    Captures all outbound messages and media in `simulated_outbox` for assertion and browser playback.
    """

    name: str = "simulation"
    display_name: str = "Simulation Provider (Virtual)"
    description: str = "In-memory virtual assistant simulator for offline and automated testing."

    def __init__(self):
        self.simulated_outbox: List[Dict[str, Any]] = []

    def clear_outbox(self) -> None:
        """Clears the simulated outbox buffer."""
        self.simulated_outbox.clear()

    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SendMessageResponse:
        msg_id = f"sim-{uuid.uuid4().hex[:8]}"
        record = {
            "type": "text",
            "message_id": msg_id,
            "to": to,
            "text": text,
            "session_id": session_id or "default",
        }
        self.simulated_outbox.append(record)
        return SendMessageResponse(
            success=True,
            message_id=msg_id,
            to=to,
            raw=record,
        )

    async def send_media(
        self,
        to: str,
        media_type: Union[MediaType, str] = MediaType.AUDIO,
        file_path: Optional[Any] = None,
        file_bytes: Optional[bytes] = None,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        ptt: bool = False,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SendMessageResponse:
        m_type = media_type.value if isinstance(media_type, MediaType) else str(media_type)
        msg_id = f"sim-media-{uuid.uuid4().hex[:8]}"
        record = {
            "type": "media",
            "message_id": msg_id,
            "to": to,
            "media_type": m_type,
            "caption": caption,
            "file_name": file_name,
            "ptt": ptt,
            "bytes_length": len(file_bytes) if file_bytes else (file_path and 100 or 0),
            "session_id": session_id or "default",
        }
        self.simulated_outbox.append(record)
        return SendMessageResponse(
            success=True,
            message_id=msg_id,
            to=to,
            raw=record,
        )

    async def get_status(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "CONNECTED",
            "simulation_mode": True,
            "outbox_count": len(self.simulated_outbox),
            "message": "Virtual simulator running in-memory",
        }

    async def ping(self) -> Dict[str, Any]:
        return {
            "provider": self.name,
            "status": "ok",
            "message": "Simulation provider is active and ready (no phone required)",
            "outbox_count": len(self.simulated_outbox),
        }
