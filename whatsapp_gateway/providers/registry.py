"""
WhatsApp Provider Registry & Plugin Manager.
Allows dynamic registration, listing, and runtime hot-swapping of WhatsApp providers.
"""

import logging
from typing import Any, Dict, List, Optional, Type
from whatsapp_gateway.config import config
from whatsapp_gateway.providers.base import BaseWhatsAppProvider
from whatsapp_gateway.providers.simulation_provider import SimulationProvider
from whatsapp_gateway.providers.wa_akg_provider import WaAkgProvider
from whatsapp_gateway.providers.meta_cloud_provider import MetaCloudApiProvider

logger = logging.getLogger("whatsapp_gateway.providers.registry")


class ProviderRegistry:
    """
    Singleton registry managing WhatsApp Gateway Provider Plugins.
    """

    def __init__(self):
        self._providers: Dict[str, BaseWhatsAppProvider] = {}
        self._active_provider_name: str = "simulation"

        # Auto-register core built-in providers
        self.register(SimulationProvider())
        self.register(WaAkgProvider())
        self.register(MetaCloudApiProvider())

        # Determine initial active provider from config
        self._sync_active_provider_from_config()

    def _sync_active_provider_from_config(self) -> None:
        """Determines active provider based on current config."""
        cfg_provider = getattr(config, "provider", None)
        if cfg_provider and cfg_provider in self._providers:
            self._active_provider_name = cfg_provider
        elif getattr(config, "enable_simulation_mode", False):
            self._active_provider_name = "simulation"
        else:
            self._active_provider_name = "wa_akg"

    def register(self, provider: BaseWhatsAppProvider) -> None:
        """Registers a provider instance into the registry."""
        self._providers[provider.name] = provider
        logger.info("[ProviderRegistry] Registered WhatsApp provider plugin: '%s' (%s)", provider.name, provider.display_name)

    def get_provider(self, name: str) -> Optional[BaseWhatsAppProvider]:
        """Returns provider instance by name."""
        return self._providers.get(name)

    def list_providers(self) -> List[Dict[str, Any]]:
        """Returns metadata list of all registered providers."""
        return [
            {
                "name": p.name,
                "display_name": p.display_name,
                "description": p.description,
                "is_active": (p.name == self._active_provider_name),
            }
            for p in self._providers.values()
        ]

    def get_active_provider_name(self) -> str:
        return self._active_provider_name

    def get_active_provider(self) -> BaseWhatsAppProvider:
        """Returns the currently active provider instance."""
        return self._providers.get(self._active_provider_name) or self._providers["simulation"]

    def set_active_provider(self, name: str) -> BaseWhatsAppProvider:
        """
        Hot-swaps the active provider at runtime with zero downtime.
        """
        if name not in self._providers:
            raise ValueError(f"Unknown provider: '{name}'. Available: {list(self._providers.keys())}")
        self._active_provider_name = name
        logger.info("[ProviderRegistry] Active WhatsApp Provider switched to: '%s'", name)
        return self._providers[name]


# Global singleton instance
provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    return provider_registry


def get_active_provider() -> BaseWhatsAppProvider:
    return provider_registry.get_active_provider()
