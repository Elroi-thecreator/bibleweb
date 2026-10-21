"""
Data models and schemas for WA-AKG API and incoming webhooks.
Uses Pydantic v2 for robust validation and serialization.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MediaType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class SendTextMessageRequest(BaseModel):
    """Payload to send a plain text message via WA-AKG."""
    session_id: str = Field(..., alias="sessionId")
    to: str
    text: str

    class Config:
        populate_by_name = True


class SendMediaMessageRequest(BaseModel):
    """Payload to send media (audio, image, document) via WA-AKG."""
    session_id: str = Field(..., alias="sessionId")
    to: str
    media_type: MediaType = Field(MediaType.AUDIO, alias="mediaType")
    caption: Optional[str] = None
    file_name: Optional[str] = Field(None, alias="fileName")
    ptt: bool = Field(False, description="Push-to-talk voice note mode for audio")
    # Base64 or direct URL
    media_url: Optional[str] = Field(None, alias="mediaUrl")
    media_base64: Optional[str] = Field(None, alias="mediaBase64")

    class Config:
        populate_by_name = True


class SendMessageResponse(BaseModel):
    """Normalized response from WA-AKG message dispatch."""
    success: bool
    message_id: Optional[str] = None
    to: Optional[str] = None
    error: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class IncomingWebhookPayload(BaseModel):
    """
    Robust webhook parser supporting both raw Baileys format
    and simplified WA-AKG REST wrapper schemas.
    """
    event: Optional[str] = None
    session_id: Optional[str] = Field(None, alias="sessionId")
    # Simplified format fields
    sender: Optional[str] = Field(None, alias="from")
    body: Optional[str] = None
    push_name: Optional[str] = Field(None, alias="pushName")
    # Baileys standard format fields
    data: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        extra = "allow"

    def is_from_me(self) -> bool:
        """Determines if the message originated from the bot itself."""
        if self.data and isinstance(self.data, dict):
            if self.data.get("fromMe") is True:
                return True
            key = self.data.get("key", {})
            if isinstance(key, dict) and key.get("fromMe") is True:
                return True
        return False

    def get_sender_jid(self) -> str:
        """Extracts the sender phone number/JID from either format."""
        if self.sender:
            return self.sender
        if self.data and isinstance(self.data, dict):
            if "from" in self.data and self.data["from"]:
                return str(self.data["from"])
            if "sender" in self.data and self.data["sender"] and "@" in str(self.data["sender"]):
                return str(self.data["sender"])
            key = self.data.get("key", {})
            if isinstance(key, dict):
                remote_jid = key.get("remoteJid", "")
                # Handle group participant if in group
                participant = key.get("participant") or self.data.get("participant")
                return participant or remote_jid
        return ""

    def get_sender_name(self) -> str:
        """Extracts push name or sender identity."""
        if self.push_name:
            return self.push_name
        if self.data and isinstance(self.data, dict):
            return self.data.get("pushName") or self.data.get("name") or "User"
        return "User"

    def get_text_content(self) -> str:
        """Extracts text content across conversation, extendedTextMessage, or caption."""
        if self.body is not None:
            return self.body.strip()
        if self.data and isinstance(self.data, dict):
            # 0. WA-AKG simplified fields: content, caption, text
            if "content" in self.data and self.data["content"] is not None:
                return str(self.data["content"]).strip()
            if "caption" in self.data and self.data["caption"] is not None:
                return str(self.data["caption"]).strip()
            if "text" in self.data and self.data["text"] is not None:
                return str(self.data["text"]).strip()

            msg = self.data.get("message", {})
            if isinstance(msg, dict):
                # 1. Plain text conversation
                if "conversation" in msg and msg["conversation"]:
                    return str(msg["conversation"]).strip()
                # 2. Extended text (links, formatted, replies)
                if "extendedTextMessage" in msg and isinstance(msg["extendedTextMessage"], dict):
                    return str(msg["extendedTextMessage"].get("text", "")).strip()
                # 3. Media caption (image or document caption)
                for media_key in ("imageMessage", "videoMessage", "documentMessage"):
                    if media_key in msg and isinstance(msg[media_key], dict):
                        caption = msg[media_key].get("caption")
                        if caption:
                            return str(caption).strip()
                # 4. Buttons / interactive response
                if "buttonsResponseMessage" in msg and isinstance(msg["buttonsResponseMessage"], dict):
                    return str(msg["buttonsResponseMessage"].get("selectedButtonId", "")).strip()
                if "listResponseMessage" in msg and isinstance(msg["listResponseMessage"], dict):
                    single_select = msg["listResponseMessage"].get("singleSelectReply", {})
                    return str(single_select.get("selectedRowId", "")).strip()
        return ""
