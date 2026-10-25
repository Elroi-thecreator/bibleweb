"""
WhatsApp Gateway Providers Package.
Exposes the pluggable provider interfaces and registry for Meta Cloud API, WA-AKG, and Simulation.
"""

from whatsapp_gateway.providers.base import BaseWhatsAppProvider
from whatsapp_gateway.providers.simulation_provider import SimulationProvider
from whatsapp_gateway.providers.wa_akg_provider import WaAkgProvider
from whatsapp_gateway.providers.meta_cloud_provider import MetaCloudApiProvider, normalize_meta_phone
from whatsapp_gateway.providers.registry import (
    ProviderRegistry,
    get_active_provider,
    get_provider_registry,
    provider_registry,
)

__all__ = [
    "BaseWhatsAppProvider",
    "SimulationProvider",
    "WaAkgProvider",
    "MetaCloudApiProvider",
    "normalize_meta_phone",
    "ProviderRegistry",
    "provider_registry",
    "get_provider_registry",
    "get_active_provider",
]
