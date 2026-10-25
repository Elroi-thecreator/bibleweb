"""
WA-AKG (Baileys) WhatsApp Gateway Provider Plugin.
Implements the multi-device Baileys gateway connection protocol via WA-AKG REST API.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import urllib.parse
import httpx

from whatsapp_gateway.config import config
from whatsapp_gateway.providers.base import BaseWhatsAppProvider
from whatsapp_gateway.client.models import (
    IncomingWebhookPayload,
    MediaType,
    SendMessageResponse,
)

logger = logging.getLogger("whatsapp_gateway.providers.wa_akg")


class WaAkgProvider(BaseWhatsAppProvider):
    """
    WA-AKG Baileys Multi-Device WhatsApp Gateway Provider Plugin.
    Connects to WA-AKG REST service with QR Code authentication.
    """

    name: str = "wa_akg"
    display_name: str = "WA-AKG Gateway (Baileys Multi-Device)"
    description: str = "Self-hosted Baileys multi-device gateway connecting via WhatsApp Web QR code."

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.base_url = (base_url or config.gateway_url).rstrip("/")
        self.default_session_id = default_session_id or config.session_id
        self.api_key = api_key or config.api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Returns or instantiates an AsyncClient."""
        if self._client is None or getattr(self._client, "is_closed", False):
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["x-api-key"] = self.api_key
            self._client = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(self.timeout))
        return self._client

    def update_config(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Dynamically update client endpoint and credentials."""
        if base_url is not None:
            self.base_url = base_url.strip().rstrip("/")
        if default_session_id is not None:
            self.default_session_id = default_session_id.strip()
        if api_key is not None:
            clean_key = api_key.strip()
            self.api_key = clean_key if clean_key else None

        if self._client and not self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["x-api-key"] = self.api_key
            if "Content-Type" in self._client.headers:
                del self._client.headers["Content-Type"]
            self._client.headers.update(headers)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    def _normalize_recipient(self, to: str) -> str:
        """Ensures phone number has @s.whatsapp.net or group suffix."""
        clean = to.strip().replace(" ", "").replace("+", "").replace("-", "")
        if "@" not in clean:
            clean = f"{clean}@s.whatsapp.net"
        return clean

    async def is_gateway_running(self, timeout: float = 5.0) -> bool:
        """Probes the remote WA-AKG gateway."""
        sess = self.default_session_id
        session_endpoint = f"{self.base_url}/sessions/{sess}"
        try:
            res = await self.http_client.get(session_endpoint, timeout=timeout)
            if res.status_code in (200, 201, 204, 401):
                return True
            if res.status_code in (502, 503, 504):
                return False
        except Exception:
            pass

        try:
            parsed = urllib.parse.urlparse(self.base_url)
            origin = f"{parsed.scheme}://{parsed.netloc}/"
            res = await self.http_client.get(origin, timeout=timeout)
            return res.status_code in (200, 201, 204, 301, 302, 307, 308, 401)
        except Exception:
            return False

    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
        direct_http: bool = False,
        **kwargs: Any,
    ) -> SendMessageResponse:
        """Dispatches plain text to WA-AKG."""
        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id

        # Native WA-AKG endpoint: POST /api/messages/{sessionId}/{jid}/send
        endpoint_native = f"{self.base_url}/messages/{sess}/{target}/send"
        payload_native = {"message": {"text": text}}

        try:
            response = await self.http_client.post(endpoint_native, json=payload_native)
            if response.status_code == 404:
                # Fallback to generic endpoint
                endpoint_fallback = f"{self.base_url}/messages/send-text"
                payload_fallback = {"sessionId": sess, "to": target, "text": text}
                response = await self.http_client.post(endpoint_fallback, json=payload_fallback)

            if response.status_code >= 400:
                return SendMessageResponse(
                    success=False,
                    to=target,
                    error=f"HTTP {response.status_code}: {response.text}",
                )

            data = response.json()
            return SendMessageResponse(
                success=True,
                message_id=data.get("id") or data.get("key", {}).get("id"),
                to=target,
                raw=data,
            )
        except Exception as exc:
            return SendMessageResponse(
                success=False,
                to=target,
                error=str(exc),
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
        direct_http: bool = False,
        **kwargs: Any,
    ) -> SendMessageResponse:
        """Dispatches multipart media to WA-AKG."""
        from whatsapp_gateway.audio_converter import transcode_audio_to_mp4

        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id
        m_type_str = media_type.value if isinstance(media_type, MediaType) else str(media_type).lower()

        # Resolve bytes
        raw_bytes: Optional[bytes] = file_bytes
        if not raw_bytes and file_path:
            p = Path(file_path)
            if p.is_file():
                raw_bytes = p.read_bytes()

        if not raw_bytes:
            return SendMessageResponse(
                success=False,
                to=target,
                error="No file bytes or valid file path provided for media send.",
            )

        # Transcode MP3 -> MP4 for audio/voice if needed
        is_audio = m_type_str in ("audio", "voice")
        is_mp3 = raw_bytes[:3] == b"ID3" or raw_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")

        if is_audio and is_mp3:
            transcoded = transcode_audio_to_mp4(raw_bytes)
            if transcoded:
                raw_bytes = transcoded
                m_type_str = "voice" if ptt else "audio"
                default_name = "devotional_audio.m4a"
                mime = "audio/mp4"
            else:
                m_type_str = "document"
                default_name = file_name or "devotional_audio.mp3"
                mime = "audio/mpeg"
        else:
            if is_audio:
                default_name = file_name or ("devotional_audio.m4a" if not ptt else "voice_note.m4a")
                mime = "audio/mp4"
            elif m_type_str == "image":
                default_name = file_name or "status_card.jpg"
                mime = "image/jpeg"
            else:
                default_name = file_name or "document.bin"
                mime = "application/octet-stream"

        filename = file_name or default_name
        encoded_jid = urllib.parse.quote(target, safe="")
        endpoint = f"{self.base_url}/messages/{sess}/{encoded_jid}/media"

        files = {"file": (filename, raw_bytes, mime)}
        data = {"type": m_type_str}
        if caption:
            data["caption"] = caption

        try:
            response = await self.http_client.post(endpoint, files=files, data=data)
            if response.status_code >= 400:
                return SendMessageResponse(
                    success=False,
                    to=target,
                    error=f"HTTP {response.status_code}: {response.text}",
                )
            res_data = response.json()
            return SendMessageResponse(
                success=True,
                message_id=res_data.get("id") or res_data.get("key", {}).get("id"),
                to=target,
                raw=res_data,
            )
        except Exception as exc:
            return SendMessageResponse(
                success=False,
                to=target,
                error=str(exc),
            )

    async def get_status(self) -> Dict[str, Any]:
        """Retrieves session status from WA-AKG."""
        sess = self.default_session_id
        endpoint = f"{self.base_url}/sessions/{sess}"
        try:
            resp = await self.http_client.get(endpoint)
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            if resp.status_code == 200:
                raw_status = str(data.get("status", "")).upper()
                norm = "CONNECTED" if raw_status in ("CONNECTED", "AUTHENTICATED") else "INITIALIZING"
                return {
                    "provider": self.name,
                    "display_name": self.display_name,
                    "status": norm,
                    "session_id": sess,
                    "raw": data,
                }
            return {
                "provider": self.name,
                "display_name": self.display_name,
                "status": "DISCONNECTED",
                "session_id": sess,
                "error": resp.text,
            }
        except Exception as exc:
            return {
                "provider": self.name,
                "display_name": self.display_name,
                "status": "UNREACHABLE",
                "session_id": sess,
                "error": str(exc),
            }

    async def ping(self) -> Dict[str, Any]:
        """Probes the WA-AKG service."""
        is_alive = await self.is_gateway_running()
        if is_alive:
            status_info = await self.get_status()
            return {
                "provider": self.name,
                "status": "ok",
                "message": f"WA-AKG Gateway is online and responding! Session: '{self.default_session_id}' ({status_info.get('status')})",
                "details": status_info,
            }
        return {
            "provider": self.name,
            "status": "error",
            "message": f"WA-AKG Gateway at {self.base_url} is unreachable or offline.",
            "details": {"base_url": self.base_url, "session_id": self.default_session_id},
        }

    def parse_webhook_payload(
        self,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[IncomingWebhookPayload]:
        if not isinstance(data, dict):
            return None
        # WA-AKG payloads have 'event', 'data', or simplified 'sender'/'from'
        if "event" in data or "data" in data or "sessionId" in data:
            try:
                return IncomingWebhookPayload.model_validate(data)
            except Exception:
                return None
        return None
