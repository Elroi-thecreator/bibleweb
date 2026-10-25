"""
Asynchronous HTTP Client for WA-AKG & Meta Cloud WhatsApp Gateways.
Provides clean methods for sending messages, audio clips, and checking session statuses
with pluggable provider delegation across Meta WhatsApp Business Cloud API, WA-AKG, and Simulation.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import urllib.parse
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
from whatsapp_gateway.providers.meta_cloud_provider import MetaCloudApiProvider

logger = logging.getLogger("whatsapp_gateway.client")


class WAClient:
    """
    Async Client to interact with WhatsApp Providers (WA-AKG, Meta Cloud API, Simulator).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        simulation_mode: Optional[bool] = None,
        provider: Optional[str] = None,
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
        self.provider = (provider or default_config.provider or "wa_akg").lower()

        self._client: Optional[httpx.AsyncClient] = None
        self.simulated_outbox: List[Dict[str, Any]] = []

        # Built-in Meta Cloud API Provider delegator
        self.meta_provider = MetaCloudApiProvider(
            phone_number_id=default_config.meta_phone_number_id,
            waba_id=default_config.meta_waba_id,
            access_token=default_config.meta_access_token,
            verify_token=default_config.meta_verify_token,
            app_secret=default_config.meta_app_secret,
            api_version=default_config.meta_api_version,
            timeout=self.timeout,
        )

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Returns active AsyncClient, recreating if closed or loop changed."""
        if self._client is None or getattr(self._client, "is_closed", False) is True:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["x-api-key"] = self.api_key
            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    def update_config(
        self,
        base_url: Optional[str] = None,
        default_session_id: Optional[str] = None,
        api_key: Optional[str] = None,
        simulation_mode: Optional[bool] = None,
        provider: Optional[str] = None,
        meta_phone_number_id: Optional[str] = None,
        meta_waba_id: Optional[str] = None,
        meta_access_token: Optional[str] = None,
        meta_verify_token: Optional[str] = None,
        meta_app_secret: Optional[str] = None,
        meta_api_version: Optional[str] = None,
    ) -> None:
        """Dynamically update client endpoint, credentials, provider, and simulation mode."""
        if base_url is not None:
            self.base_url = base_url.strip().rstrip("/")
        if default_session_id is not None:
            self.default_session_id = default_session_id.strip()
        if api_key is not None:
            clean_key = api_key.strip()
            self.api_key = clean_key if clean_key else None
        if simulation_mode is not None:
            self.simulation_mode = bool(simulation_mode)
        if provider is not None:
            self.provider = provider.strip().lower()

        # Update Meta credentials
        self.meta_provider.update_credentials(
            phone_number_id=meta_phone_number_id,
            waba_id=meta_waba_id,
            access_token=meta_access_token,
            verify_token=meta_verify_token,
            app_secret=meta_app_secret,
            api_version=meta_api_version,
        )

        # Sync provider registry
        try:
            from whatsapp_gateway.providers.registry import provider_registry
            target_prov = "simulation" if self.simulation_mode else (self.provider or "wa_akg")
            if target_prov in provider_registry._providers:
                provider_registry.set_active_provider(target_prov)
        except Exception:
            pass

        if self._client and not self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["x-api-key"] = self.api_key
            if "Content-Type" in self._client.headers:
                del self._client.headers["Content-Type"]
            self._client.headers.update(headers)

    def toggle_simulation(self, enable: Optional[bool] = None) -> bool:
        """Toggles or sets simulation mode."""
        if enable is None:
            self.simulation_mode = not self.simulation_mode
        else:
            self.simulation_mode = bool(enable)

        try:
            from whatsapp_gateway.providers.registry import provider_registry
            target = "simulation" if self.simulation_mode else (self.provider or "wa_akg")
            provider_registry.set_active_provider(target)
        except Exception:
            pass

        return self.simulation_mode

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None
        await self.meta_provider.close()

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

    async def is_gateway_running(self, timeout: float = 5.0) -> bool:
        """
        Checks if the active gateway is alive, awake, and responding.
        """
        if self.simulation_mode:
            return True

        if self.provider == "meta_cloud_api":
            st = await self.meta_provider.get_status()
            return st.get("status") == "CONNECTED"

        # Targeted check on WA-AKG session endpoint
        sess = self.default_session_id
        session_endpoint = f"{self.base_url}/sessions/{sess}"
        try:
            res = await self.http_client.get(session_endpoint, timeout=timeout)
            if res.status_code in (200, 201, 204, 401):
                return True
            if res.status_code in (502, 503, 504):
                return False
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError):
            pass
        except Exception:
            pass

        # Fallback to origin root ping for Render cold-starts
        try:
            parsed = urllib.parse.urlparse(self.base_url)
            origin = f"{parsed.scheme}://{parsed.netloc}/"
            res = await self.http_client.get(origin, timeout=timeout)
            return res.status_code in (200, 201, 204, 301, 302, 307, 308, 401)
        except Exception:
            return False

    async def wait_until_gateway_running(
        self,
        poll_interval: float = 5.0,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Polls the gateway periodically until it is awake, running, and accepting requests.
        """
        if self.simulation_mode:
            return True

        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                if await self.is_gateway_running(timeout=poll_interval):
                    return True
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.debug("Gateway health check ping error: %s", exc)

            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    return False

            await asyncio.sleep(poll_interval)

    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
        direct_http: bool = False,
    ) -> SendMessageResponse:
        """
        Send a plain text message to a user or group across active provider.
        """
        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id

        # Push to RabbitMQ outgoing queue when enabled and ready
        if not direct_http:
            try:
                from whatsapp_gateway.queue.manager import queue_manager
                if queue_manager.is_ready:
                    res = await queue_manager.enqueue_outgoing_text(to=target, text=text, session_id=sess)
                    if res.get("backend") == "rabbitmq":
                        return SendMessageResponse(
                            success=True,
                            message_id=res.get("task_id", "queued"),
                            to=target,
                            raw=res,
                        )
            except Exception as q_err:
                logger.debug("RabbitMQ queue enqueue bypassed (%s); using direct dispatch", q_err)

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

        # Provider: Meta WhatsApp Business Cloud API
        if self.provider == "meta_cloud_api":
            return await self.meta_provider.send_text(to=target, text=text, session_id=sess)

        # Provider: WA-AKG Baileys
        endpoint_native = f"{self.base_url}/messages/{sess}/{target}/send"
        payload_native = {"message": {"text": text}}

        try:
            response = await self.http_client.post(endpoint_native, json=payload_native)
            if response.status_code == 404:
                endpoint_fallback = f"{self.base_url}/messages/send-text"
                payload_fallback = {
                    "sessionId": sess,
                    "to": target,
                    "text": text,
                }
                response = await self.http_client.post(endpoint_fallback, json=payload_fallback)
            elif response.status_code >= 400 and "Invalid media type" in response.text:
                response = await self.http_client.post(endpoint_native, json={"message": text})

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
        direct_http: bool = False,
    ) -> SendMessageResponse:
        """
        Send media (voice notes, audio clips, images, docs) to a recipient.
        """
        target = self._normalize_recipient(to)
        sess = session_id or self.default_session_id
        m_type = media_type.value if isinstance(media_type, MediaType) else str(media_type)

        # Push to RabbitMQ outgoing queue when enabled and ready
        if not direct_http:
            try:
                from whatsapp_gateway.queue.manager import queue_manager
                if queue_manager.is_ready:
                    res = await queue_manager.enqueue_outgoing_media(
                        to=target,
                        media_type=m_type,
                        file_path=file_path,
                        file_bytes=file_bytes,
                        caption=caption,
                        file_name=file_name,
                        ptt=ptt,
                        session_id=sess,
                    )
                    if res.get("backend") == "rabbitmq":
                        return SendMessageResponse(
                            success=True,
                            message_id=res.get("task_id", "queued"),
                            to=target,
                            raw=res,
                        )
            except Exception as q_err:
                logger.debug("RabbitMQ queue media enqueue bypassed (%s); using direct dispatch", q_err)

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

        # Provider: Meta WhatsApp Business Cloud API
        if self.provider == "meta_cloud_api":
            return await self.meta_provider.send_media(
                to=target,
                media_type=media_type,
                file_bytes=raw_bytes,
                caption=caption,
                file_name=resolved_name,
                ptt=ptt,
                session_id=sess,
            )

        # Provider: WA-AKG Baileys
        # Auto-transcode audio payloads for WhatsApp compatibility (ISO MP4 container with AAC)
        if m_type == "audio" and not self.simulation_mode:
            try:
                from whatsapp_gateway.audio_converter import prepare_whatsapp_audio_payload
                raw_bytes, resolved_name, m_type, _ = prepare_whatsapp_audio_payload(
                    raw_bytes, preferred_name=resolved_name, ptt=ptt
                )
            except Exception as conv_err:
                logger.warning("WhatsApp audio transcoding pre-flight check failed (%s); sending original payload", conv_err)

        type_param = "voice" if (m_type == "audio" and ptt) else m_type
        ext = Path(resolved_name or ("voice.m4a" if ptt else "audio.m4a")).suffix.lower()
        mime_map = {
            ".m4a": "audio/mp4",
            ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg",
            ".wav": "audio/wav",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".pdf": "application/pdf",
        }
        mime_type = mime_map.get(ext, "audio/mp4" if m_type == "audio" else "application/octet-stream")

        file_tuple_name = resolved_name or ("voice.m4a" if ptt else "audio.m4a")
        files = {
            "file": (file_tuple_name, raw_bytes, mime_type)
        }
        form_data = {
            "type": type_param,
            "caption": caption or "",
        }

        encoded_target = urllib.parse.quote(target, safe="")
        endpoint_native = f"{self.base_url}/messages/{sess}/{encoded_target}/media"

        try:
            response = await self.http_client.post(endpoint_native, files=files, data=form_data)
            if response.status_code == 404:
                endpoint_unencoded = f"{self.base_url}/messages/{sess}/{target}/media"
                response = await self.http_client.post(endpoint_unencoded, files=files, data=form_data)

            if response.status_code >= 400:
                logger.error("WA-AKG media error %s: %s", response.status_code, response.text)
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
            logger.error("Failed to dispatch media to WA-AKG gateway at %s: %s", endpoint_native, exc)
            raise WAGatewayConnectionError(f"Could not reach WA-AKG: {exc}") from exc

    async def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Query connection status for the active WhatsApp session or provider."""
        sess = session_id or self.default_session_id
        if self.simulation_mode:
            return {
                "sessionId": sess,
                "status": "CONNECTED",
                "simulation": True,
                "provider": "simulation",
            }

        if self.provider == "meta_cloud_api":
            return await self.meta_provider.get_status()

        endpoint = f"{self.base_url}/sessions/{sess}"
        try:
            res = await self.http_client.get(endpoint)
            if res.status_code == 200:
                raw_json = res.json()
                inner_data = raw_json.get("data", {}) if isinstance(raw_json, dict) else {}
                conn_status = inner_data.get("status") if isinstance(inner_data, dict) else None
                return {
                    "provider": "wa_akg",
                    "status": conn_status or ("CONNECTED" if raw_json.get("status") is True else "UNKNOWN"),
                    "is_connected": conn_status == "CONNECTED",
                    "data": inner_data,
                    "raw": raw_json,
                }
            return {"provider": "wa_akg", "status": "UNKNOWN", "http_status": res.status_code, "detail": res.text}
        except Exception as exc:
            return {"provider": "wa_akg", "status": "UNREACHABLE", "error": str(exc)}

    async def ping(self) -> Dict[str, Any]:
        """Probes the active WhatsApp provider."""
        if self.simulation_mode:
            return {
                "provider": "simulation",
                "status": "ok",
                "message": "Virtual Simulator active (no phone required).",
            }

        if self.provider == "meta_cloud_api":
            return await self.meta_provider.ping()

        # WA-AKG
        is_alive = await self.is_gateway_running()
        if is_alive:
            status_info = await self.get_session_status()
            return {
                "provider": "wa_akg",
                "status": "ok",
                "message": f"Connected to WA-AKG Gateway! Session: {self.default_session_id} ({status_info.get('status')})",
                "details": status_info,
            }
        return {
            "provider": "wa_akg",
            "status": "error",
            "message": f"WA-AKG Gateway at {self.base_url} is unreachable or offline.",
            "details": {"base_url": self.base_url, "session_id": self.default_session_id},
        }
