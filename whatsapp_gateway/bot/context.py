"""
Message Context abstraction encapsulating an incoming WhatsApp message,
providing seamless helpers to reply with text or audio, and access session states.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import re

from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.client.models import (
    IncomingWebhookPayload,
    MediaType,
    SendMessageResponse,
)
from whatsapp_gateway.bot.session_store import BaseSessionStore


class MessageContext:
    """Represents the context of an incoming WhatsApp message."""

    def __init__(
        self,
        payload: IncomingWebhookPayload,
        client: WAClient,
        session_store: BaseSessionStore,
        session_id: Optional[str] = None,
    ):
        self.payload = payload
        self.client = client
        self.session_store = session_store
        self.session_id = session_id or client.default_session_id

        self.sender = payload.get_sender_jid()
        self.sender_name = payload.get_sender_name()
        self.text = payload.get_text_content()
        self.matches: Optional[re.Match] = None

    async def reply_text(self, text: str) -> SendMessageResponse:
        """Reply to the message sender with a text message."""
        return await self.client.send_text(
            to=self.sender,
            text=text,
            session_id=self.session_id,
        )

    async def reply_audio(
        self,
        file_path_or_bytes: Union[str, Path, bytes],
        caption: Optional[str] = None,
        ptt: bool = True,
        file_name: Optional[str] = "audio.mp3",
    ) -> SendMessageResponse:
        """Reply to the sender with an audio clip or voice note (push-to-talk)."""
        if isinstance(file_path_or_bytes, bytes):
            return await self.client.send_media(
                to=self.sender,
                media_type=MediaType.AUDIO,
                file_bytes=file_path_or_bytes,
                caption=caption,
                file_name=file_name,
                ptt=ptt,
                session_id=self.session_id,
            )
        else:
            return await self.client.send_media(
                to=self.sender,
                media_type=MediaType.AUDIO,
                file_path=Path(file_path_or_bytes),
                caption=caption,
                file_name=file_name,
                ptt=ptt,
                session_id=self.session_id,
            )

    async def get_state(self) -> Optional[Dict[str, Any]]:
        """Retrieve active multi-turn conversational state for this sender."""
        return await self.session_store.get_session(self.sender)

    async def set_state(
        self,
        state: str,
        data: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set multi-turn conversational state for this sender."""
        await self.session_store.set_session(
            user_id=self.sender,
            state=state,
            data=data or {},
            ttl_seconds=ttl_seconds,
        )

    async def clear_state(self) -> None:
        """Clear active conversational state for this sender."""
        await self.session_store.clear_session(self.sender)
