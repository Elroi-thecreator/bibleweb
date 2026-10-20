"""
WhatsApp Gateway Configuration Module.
Loads environment variables or defaults for connecting to the WA-AKG gateway.
Completely standalone with zero dependencies on external application domains.
"""

from os import getenv
from typing import Optional
from pydantic import BaseModel, Field


class WhatsAppGatewayConfig(BaseModel):
    """Configuration settings for WA-AKG WhatsApp Gateway."""

    gateway_url: str = Field(
        default_factory=lambda: getenv("WA_GATEWAY_URL", "http://localhost:3000/api")
    )
    session_id: str = Field(
        default_factory=lambda: getenv("WA_SESSION_ID", "default")
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: getenv("WA_API_KEY", None)
    )
    webhook_secret: Optional[str] = Field(
        default_factory=lambda: getenv("WA_WEBHOOK_SECRET", None)
    )
    command_prefix: str = Field(
        default_factory=lambda: getenv("WA_COMMAND_PREFIX", "")
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(getenv("WA_TIMEOUT_SECONDS", "15.0"))
    )
    session_ttl_seconds: int = Field(
        default_factory=lambda: int(getenv("WA_SESSION_TTL_SECONDS", "900"))  # 15 minutes default
    )
    enable_simulation_mode: bool = Field(
        default_factory=lambda: getenv("WA_SIMULATION_MODE", "false").lower() in ("true", "1", "yes")
    )


# Default singleton instance
config = WhatsAppGatewayConfig()
