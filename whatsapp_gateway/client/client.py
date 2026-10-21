"""
Asynchronous HTTP Client for WA-AKG WhatsApp Gateway.
Provides clean methods for sending messages, audio clips, and checking session statuses.
"""

import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import httpx

from whatsapp_gateway.config import config as default_config
from whatsapp_gateway.client.exceptions import (
    WAGatewayConnectionError,
    WAMessageSendError,
    WASessionError,
)
from whatsapp_gateway.client.models import (
    MediaType,
    SendMessageResponse,
)

logger = logging.getLogger("whatsapp_gateway.client")


class WAClient:
    """Async Client to interact with WA-AKG REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        simulation_mode: Optional[bool] = None,
    ):
        self.base_url = (base_url or default_config.gateway_url).rstrip("/")
        self.default_session_id = default_session_id or default_config.session_id
        self.api_key = api_key or default_config.api_key
        self.timeout = timeout or default_config.timeout_seconds
        self.simulation_mode = (
            simulation_mode
            if simulation_mode is not None
            else default_config.enable_simulation_mode
        )

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["x-api-key"] = self.api_key

        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(self.timeout),
        )
        self.simulated_outbox: List[Dict[str, Any]] = []

    def update_config(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        simulation_mode: Optional[bool] = None,
    ) -> None:
        """Dynamically update client endpoint, credentials, and simulation mode."""
        if base_url is not None:
            self.base_url = base_url.strip().rstrip("/")
        if default_session_id is not None:
            self.default_session_id = default_session_id.strip()
        if api_key is not None:
            clean_key = api_key.strip()
            self.api_key = clean_key if clean_key else None
        if simulation_mode is not None:
            self.simulation_mode = bool(simulation_mode)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["x-api-key"] = self.api_key
        self._client.headers.update(headers)

    def toggle_simulation(self, enable: Optional[bool] = None) -> bool:
        """Toggles or sets simulation mode."""
        if enable is None:
            self.simulation_mode = not self.simulation_mode
        else:
            self.simulation_mode = bool(enable)
        return self.simulation_mode

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _normalize_recipient(self, to: str) -> str:
        """Ensures phone number has @s.whatsapp.net or group suffix."""
        clean = to.strip().replace(" ", "").replace("+", "").replace("-", "")
        if "@" not in clean:
            clean = f"{clean}@s.whatsapp.net"
        return clean

    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
    ) -> SendMessageResponse:
        """
        Send a plain text message to a user or group.
        """
        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id

        if self.simulation_mode:
            logger.info("[SIMULATION] Dispatching WhatsApp Text to %s: %s", target, text[:60])
            record = {"to": target, "text": text, "session_id": sess, "type": "text"}
            self.simulated_outbox.append(record)
            return SendMessageResponse(
                success=True,
                message_id="sim-msg-id-123",
                to=target,
                raw=record,
            )

        # WA-AKG native endpoint: POST /api/messages/{sessionId}/{jid}/send with {"message": text}
        endpoint_native = f"{self.base_url}/messages/{sess}/{target}/send"
        payload_native = {"message": text}

        try:
            response = await self._client.post(endpoint_native, json=payload_native)
            if response.status_code == 404:
                # Fallback to generic endpoint: POST /api/messages/send-text
                endpoint_fallback = f"{self.base_url}/messages/send-text"
                payload_fallback = {
                    "sessionId": sess,
                    "to": target,
                    "text": text,
                }
                response = await self._client.post(endpoint_fallback, json=payload_fallback)

            if response.status_code >= 400:
                logger.error("WA-AKG error %s: %s", response.status_code, response.text)
                return SendMessageResponse(
                    success=False,
                    to=target,
                    error=f"HTTP {response.status_code}: {response.text}",
                )

            data = response.json()
            msg_id = (
                data.get("id")
                or data.get("messageId")
                or (data.get("data") or {}).get("key", {}).get("id")
                or "sent"
            )
            return SendMessageResponse(
                success=True,
                message_id=msg_id,
                to=target,
                raw=data,
            )
        except httpx.RequestError as exc:
            logger.error("Failed to connect to WA-AKG gateway at %s: %s", endpoint_native, exc)
            raise WAGatewayConnectionError(f"Could not reach WA-AKG: {exc}") from exc

    async def send_media(
        self,
        to: str,
        media_type: Union[MediaType, str] = MediaType.AUDIO,
        file_path: Optional[Union[str, Path]] = None,
        file_bytes: Optional[bytes] = None,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        ptt: bool = False,
        session_id: Optional[str] = None,
    ) -> SendMessageResponse:
        """
        Send media (voice notes, audio clips, images, docs) to a WhatsApp recipient.
        """
        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id
        m_type = media_type.value if isinstance(media_type, MediaType) else str(media_type)

        # Read bytes if path provided
        raw_bytes = file_bytes
        resolved_name = file_name
        if file_path:
            p = Path(file_path)
            if not resolved_name:
                resolved_name = p.name
            if not raw_bytes:
                with open(p, "rb") as f:
                    raw_bytes = f.read()

        if not raw_bytes:
            raise ValueError("Either file_path or file_bytes must be provided for send_media.")

        b64_content = base64.b64encode(raw_bytes).decode("ascii")

        if self.simulation_mode:
            logger.info("[SIMULATION] Dispatching WhatsApp Media (%s) to %s (len: %d bytes)", m_type, target, len(raw_bytes))
            record = {
                "to": target,
                "media_type": m_type,
                "caption": caption,
                "file_name": resolved_name,
                "ptt": ptt,
                "session_id": sess,
                "bytes_len": len(raw_bytes),
            }
            self.simulated_outbox.append(record)
            return SendMessageResponse(
                success=True,
                message_id="sim-media-id-456",
                to=target,
                raw=record,
            )

        endpoint = f"{self.base_url}/messages/send-media"
        payload = {
            "sessionId": sess,
            "to": target,
            "mediaType": m_type,
            "caption": caption or "",
            "fileName": resolved_name or "file",
            "ptt": ptt,
            "mediaBase64": b64_content,
        }

        try:
            response = await self._client.post(endpoint, json=payload)
            if response.status_code >= 400:
                logger.error("WA-AKG media error %s: %s", response.status_code, response.text)
                return SendMessageResponse(
                    success=False,
                    to=target,
                    error=f"HTTP {response.status_code}: {response.text}",
                )

            data = response.json()
            return SendMessageResponse(
                success=True,
                message_id=data.get("id") or data.get("messageId"),
                to=target,
                raw=data,
            )
        except httpx.RequestError as exc:
            logger.error("Failed to dispatch media to WA-AKG gateway: %s", exc)
            raise WAGatewayConnectionError(f"Could not reach WA-AKG: {exc}") from exc

    async def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Query connection status for the given WhatsApp session."""
        sess = session_id or self.default_session_id
        if self.simulation_mode:
            return {"sessionId": sess, "status": "CONNECTED", "simulation": True}

        endpoint = f"{self.base_url}/sessions/{sess}"
        try:
            res = await self._client.get(endpoint)
            if res.status_code == 200:
                return res.json()
            return {"status": "UNKNOWN", "http_status": res.status_code, "detail": res.text}
        except Exception as exc:
            return {"status": "UNREACHABLE", "error": str(exc)}
