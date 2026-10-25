"""
Meta WhatsApp Business Cloud API Provider Plugin.
Implements the official Meta WhatsApp Business Cloud API & Developer Sandbox.
Supports sending text, audio voice notes, status images, webhook verification (hub.challenge),
and bidirectional payload parsing.
"""

import logging
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import httpx

from whatsapp_gateway.config import config
from whatsapp_gateway.providers.base import BaseWhatsAppProvider
from whatsapp_gateway.client.models import (
    IncomingWebhookPayload,
    MediaType,
    SendMessageResponse,
)

logger = logging.getLogger("whatsapp_gateway.providers.meta_cloud")


def normalize_meta_phone(phone: str) -> str:
    """
    Normalizes a recipient phone identifier to raw international digits.
    Meta Cloud API expects digits without '+', spaces, dashes, or '@s.whatsapp.net'.
    Example: '+91 98765-43210' -> '919876543210'
    Example: '919876543210@s.whatsapp.net' -> '919876543210'
    """
    clean = str(phone).strip()
    if "@" in clean:
        clean = clean.split("@")[0]
    return re.sub(r"[^\d]", "", clean)


class MetaCloudApiProvider(BaseWhatsAppProvider):
    """
    Official Meta WhatsApp Business Cloud API Provider Plugin.
    Works seamlessly with both Meta's Free Developer Sandbox (Test Number)
    and live Production WhatsApp Business Accounts (WABA).
    """

    name: str = "meta_cloud_api"
    display_name: str = "Meta WhatsApp Business Cloud API"
    description: str = "Official Meta Cloud API / Developer Sandbox with free 1,000 monthly service conversations."

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        waba_id: Optional[str] = None,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.phone_number_id = (phone_number_id or getattr(config, "meta_phone_number_id", None) or "").strip()
        self.waba_id = (waba_id or getattr(config, "meta_waba_id", None) or "").strip()
        self.access_token = (access_token or getattr(config, "meta_access_token", None) or "").strip()
        self.verify_token = (verify_token or getattr(config, "meta_verify_token", "elroi_bible_verify_token") or "elroi_bible_verify_token").strip()
        self.app_secret = (app_secret or getattr(config, "meta_app_secret", None) or "").strip()
        self.api_version = (api_version or getattr(config, "meta_api_version", "v21.0") or "v21.0").strip().lstrip("v")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Returns or instantiates an AsyncClient."""
        if self._client is None or getattr(self._client, "is_closed", False):
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self._client

    @property
    def graph_base_url(self) -> str:
        """Meta Graph API base URL."""
        return f"https://graph.facebook.com/v{self.api_version}"

    @property
    def is_configured(self) -> bool:
        """Checks if minimal credentials to call Meta Cloud API are present."""
        return bool(self.phone_number_id and self.access_token)

    def update_credentials(
        self,
        phone_number_id: Optional[str] = None,
        waba_id: Optional[str] = None,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: Optional[str] = None,
    ) -> None:
        """Hot-updates credentials at runtime."""
        if phone_number_id is not None:
            self.phone_number_id = phone_number_id.strip()
        if waba_id is not None:
            self.waba_id = waba_id.strip()
        if access_token is not None:
            self.access_token = access_token.strip()
        if verify_token is not None:
            self.verify_token = verify_token.strip()
        if app_secret is not None:
            self.app_secret = app_secret.strip()
        if api_version is not None:
            self.api_version = api_version.strip().lstrip("v")

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SendMessageResponse:
        """
        Sends text message via Meta Graph API:
        POST https://graph.facebook.com/v{version}/{phone_number_id}/messages
        """
        clean_recipient = normalize_meta_phone(to)
        if not clean_recipient:
            return SendMessageResponse(
                success=False,
                error="Recipient phone number could not be resolved to valid digits.",
            )

        if not self.is_configured:
            logger.warning("[MetaCloudApi] Credentials not configured; cannot dispatch live message.")
            return SendMessageResponse(
                success=False,
                to=to,
                error="Meta Cloud API is not configured (Phone Number ID or Access Token missing).",
            )

        url = f"{self.graph_base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text,
            },
        }

        try:
            resp = await self.http_client.post(url, json=payload, headers=headers)
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

            if resp.status_code >= 400:
                err_msg = data.get("error", {}).get("message", resp.text)
                logger.error("[MetaCloudApi] Send text failed (HTTP %s): %s", resp.status_code, err_msg)
                return SendMessageResponse(
                    success=False,
                    to=to,
                    error=f"Meta Graph API error (HTTP {resp.status_code}): {err_msg}",
                    raw=data,
                )

            messages = data.get("messages", [])
            msg_id = messages[0].get("id") if messages else None
            return SendMessageResponse(
                success=True,
                message_id=msg_id,
                to=to,
                raw=data,
            )

        except Exception as exc:
            logger.error("[MetaCloudApi] Exception during send_text: %s", exc)
            return SendMessageResponse(
                success=False,
                to=to,
                error=f"Network exception calling Meta Graph API: {exc}",
            )

    async def _upload_media(
        self,
        file_bytes: bytes,
        file_name: str,
        mime_type: str,
    ) -> Optional[str]:
        """
        Uploads media file to Meta Graph API media endpoint:
        POST https://graph.facebook.com/v{version}/{phone_number_id}/media
        Returns media_id on success, or None on failure.
        """
        url = f"{self.graph_base_url}/{self.phone_number_id}/media"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        files = {
            "file": (file_name, file_bytes, mime_type),
        }
        data = {
            "messaging_product": "whatsapp",
            "type": mime_type,
        }

        try:
            resp = await self.http_client.post(url, headers=headers, files=files, data=data)
            res_json = resp.json()
            if resp.status_code == 200 and "id" in res_json:
                return res_json["id"]
            logger.error("[MetaCloudApi] Media upload error (%s): %s", resp.status_code, resp.text)
            return None
        except Exception as exc:
            logger.error("[MetaCloudApi] Exception uploading media: %s", exc)
            return None

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
        """
        Uploads media to Meta and dispatches an audio or image message.
        Falls back automatically to sending caption/scripture text if media upload fails.
        """
        clean_recipient = normalize_meta_phone(to)
        if not clean_recipient:
            return SendMessageResponse(
                success=False,
                error="Recipient phone number could not be resolved to valid digits.",
            )

        if not self.is_configured:
            return SendMessageResponse(
                success=False,
                to=to,
                error="Meta Cloud API is not configured (Phone Number ID or Access Token missing).",
            )

        # 1. Resolve raw bytes
        raw_data: Optional[bytes] = file_bytes
        if not raw_data and file_path:
            p = Path(file_path)
            if p.is_file():
                raw_data = p.read_bytes()

        m_type_str = media_type.value if isinstance(media_type, MediaType) else str(media_type).lower()

        # Determine MIME type and default file name
        if m_type_str in ("audio", "voice"):
            mime_type = "audio/mp4"
            fname = file_name or "devotional_audio.m4a"
            meta_media_key = "audio"
        elif m_type_str == "image":
            mime_type = "image/jpeg"
            fname = file_name or "scripture_card.jpg"
            meta_media_key = "image"
        else:
            mime_type = "application/octet-stream"
            fname = file_name or "document.bin"
            meta_media_key = "document"

        if not raw_data:
            # If no bytes available, send text fallback if caption provided
            if caption:
                return await self.send_text(to=to, text=caption, session_id=session_id)
            return SendMessageResponse(
                success=False,
                to=to,
                error="No media bytes or file path provided for media upload.",
            )

        # 2. Upload media
        media_id = await self._upload_media(file_bytes=raw_data, file_name=fname, mime_type=mime_type)
        if not media_id:
            # Fallback to text if caption exists
            if caption:
                logger.info("[MetaCloudApi] Media upload failed; falling back to text caption.")
                return await self.send_text(to=to, text=caption, session_id=session_id)
            return SendMessageResponse(
                success=False,
                to=to,
                error="Failed to upload media to Meta Graph API.",
            )

        # 3. Dispatch media message referencing media_id
        url = f"{self.graph_base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        media_obj: Dict[str, Any] = {"id": media_id}
        if caption and meta_media_key in ("image", "document"):
            media_obj["caption"] = caption

        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": meta_media_key,
            meta_media_key: media_obj,
        }

        try:
            resp = await self.http_client.post(url, json=payload, headers=headers)
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}

            if resp.status_code >= 400:
                err_msg = data.get("error", {}).get("message", resp.text)
                logger.error("[MetaCloudApi] Send media failed (%s): %s", resp.status_code, err_msg)
                # Fallback to text caption if available
                if caption:
                    return await self.send_text(to=to, text=caption, session_id=session_id)
                return SendMessageResponse(
                    success=False,
                    to=to,
                    error=f"Meta Graph API error (HTTP {resp.status_code}): {err_msg}",
                    raw=data,
                )

            messages = data.get("messages", [])
            msg_id = messages[0].get("id") if messages else None
            return SendMessageResponse(
                success=True,
                message_id=msg_id,
                to=to,
                raw=data,
            )
        except Exception as exc:
            logger.error("[MetaCloudApi] Exception sending media message: %s", exc)
            if caption:
                return await self.send_text(to=to, text=caption, session_id=session_id)
            return SendMessageResponse(
                success=False,
                to=to,
                error=f"Exception calling Meta Graph API: {exc}",
            )

    async def get_status(self) -> Dict[str, Any]:
        """
        Retrieves phone number metadata and verification state from Meta Graph API.
        """
        if not self.is_configured:
            return {
                "provider": self.name,
                "display_name": self.display_name,
                "status": "DISCONNECTED",
                "configured": False,
                "message": "Meta Cloud API credentials not configured (Phone Number ID or Access Token missing).",
                "phone_number_id": self.phone_number_id or None,
            }

        url = f"{self.graph_base_url}/{self.phone_number_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            resp = await self.http_client.get(
                url,
                headers=headers,
                params={"fields": "verified_name,display_phone_number,quality_rating,code_verification_status"},
            )
            data = resp.json()
            if resp.status_code == 200:
                return {
                    "provider": self.name,
                    "display_name": self.display_name,
                    "status": "CONNECTED",
                    "configured": True,
                    "phone_number_id": self.phone_number_id,
                    "display_phone_number": data.get("display_phone_number"),
                    "verified_name": data.get("verified_name"),
                    "quality_rating": data.get("quality_rating", "GREEN"),
                    "code_verification_status": data.get("code_verification_status"),
                    "raw": data,
                }
            return {
                "provider": self.name,
                "display_name": self.display_name,
                "status": "UNREACHABLE",
                "configured": True,
                "phone_number_id": self.phone_number_id,
                "error": data.get("error", {}).get("message", resp.text),
            }
        except Exception as exc:
            return {
                "provider": self.name,
                "display_name": self.display_name,
                "status": "UNREACHABLE",
                "configured": True,
                "phone_number_id": self.phone_number_id,
                "error": str(exc),
            }

    async def ping(self) -> Dict[str, Any]:
        """
        Pings Meta Graph API to test phone number reachability and token validity.
        """
        status_info = await self.get_status()
        if status_info.get("status") == "CONNECTED":
            return {
                "provider": self.name,
                "status": "ok",
                "message": f"Connected to Meta Cloud API! Verified Name: '{status_info.get('verified_name')}' | Phone: {status_info.get('display_phone_number')}",
                "details": status_info,
            }
        if not status_info.get("configured"):
            return {
                "provider": self.name,
                "status": "warning",
                "message": "Meta Cloud API credentials are not set. Fill in Phone Number ID and Access Token in Admin Settings.",
                "details": status_info,
            }
        return {
            "provider": self.name,
            "status": "error",
            "message": f"Meta Graph API Ping Failed: {status_info.get('error', 'Unknown error')}",
            "details": status_info,
        }

    def verify_webhook(
        self,
        hub_mode: Optional[str],
        hub_verify_token: Optional[str],
        hub_challenge: Optional[str],
    ) -> Optional[str]:
        """
        Validates Meta's GET webhook subscription request.
        Returns the challenge string if token matches, or None.
        """
        if hub_mode == "subscribe" and hub_verify_token == self.verify_token and hub_challenge:
            return str(hub_challenge)
        return None

    def parse_webhook_payload(
        self,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[IncomingWebhookPayload]:
        """
        Translates Meta Cloud API Webhook JSON structure into a normalized IncomingWebhookPayload.
        Meta format:
        {
          "object": "whatsapp_business_account",
          "entry": [
            {
              "id": "WABA_ID",
              "changes": [
                {
                  "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{"profile": {"name": "..."}}],
                    "messages": [{"from": "91...", "id": "...", "type": "text", "text": {"body": "..."}}]
                  }
                }
              ]
            }
          ]
        }
        """
        if not isinstance(data, dict):
            return None

        # Check if this payload has the Meta Cloud API signature
        if data.get("object") != "whatsapp_business_account" and "entry" not in data:
            return None

        entry_list = data.get("entry", [])
        if not entry_list or not isinstance(entry_list, list):
            return None

        for entry in entry_list:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    # Could be delivery status update (sent, delivered, read)
                    continue

                msg = messages[0]
                sender_digits = msg.get("from", "")
                sender_jid = f"{sender_digits}@s.whatsapp.net" if sender_digits else ""
                msg_id = msg.get("id", "")
                msg_type = msg.get("type", "text")

                # Extract push name from contacts list
                push_name = "User"
                contacts = value.get("contacts", [])
                if contacts and isinstance(contacts, list):
                    push_name = contacts[0].get("profile", {}).get("name", "User")

                # Extract text content
                text_content = ""
                if msg_type == "text":
                    text_content = msg.get("text", {}).get("body", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    i_type = interactive.get("type")
                    if i_type == "button_reply":
                        text_content = interactive.get("button_reply", {}).get("title") or interactive.get("button_reply", {}).get("id", "")
                    elif i_type == "list_reply":
                        text_content = interactive.get("list_reply", {}).get("title") or interactive.get("list_reply", {}).get("id", "")
                elif msg_type == "button":
                    text_content = msg.get("button", {}).get("text", "")

                return IncomingWebhookPayload(
                    event="messages.upsert",
                    sessionId=self.phone_number_id or "meta_cloud",
                    sender=sender_jid,
                    body=text_content,
                    pushName=push_name,
                    data={
                        "key": {
                            "remoteJid": sender_jid,
                            "fromMe": False,
                            "id": msg_id,
                        },
                        "pushName": push_name,
                        "message": {"conversation": text_content},
                        "meta_raw": msg,
                    },
                )

        return None
