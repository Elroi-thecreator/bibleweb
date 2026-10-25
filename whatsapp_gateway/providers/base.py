"""
Base WhatsApp Provider Plugin Interface.
Defines the standard abstract contract that all WhatsApp gateway providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from whatsapp_gateway.client.models import (
    IncomingWebhookPayload,
    MediaType,
    SendMessageResponse,
)


class BaseWhatsAppProvider(ABC):
    """
    Abstract Base Class for WhatsApp Gateway Providers (Plugins).
    Enables pluggable integration of different WhatsApp services:
    - Meta WhatsApp Business Cloud API (Official Cloud API & Developer Sandbox)
    - WA-AKG (Baileys Multi-Device REST Gateway)
    - Simulation / Mock Provider (In-Browser Virtual Assistant)
    """

    name: str = "base"
    display_name: str = "Base Provider"
    description: str = "Base WhatsApp Provider"

    @abstractmethod
    async def send_text(
        self,
        to: str,
        text: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SendMessageResponse:
        """
        Sends a plain text message to a recipient phone number or JID.
        """
        pass

    @abstractmethod
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
        Sends a media attachment (audio note, image card, document) to a recipient.
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Returns the connectivity, session, or account status of the provider.
        """
        pass

    @abstractmethod
    async def ping(self) -> Dict[str, Any]:
        """
        Performs an active reachability probe to test upstream provider connectivity.
        """
        pass

    def parse_webhook_payload(
        self,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[IncomingWebhookPayload]:
        """
        Optionally parses raw webhook JSON into normalized IncomingWebhookPayload.
        Returns None if the payload does not belong to this provider.
        """
        return None
