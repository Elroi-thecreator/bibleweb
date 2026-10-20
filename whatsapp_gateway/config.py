"""
WhatsApp Gateway Configuration Module.
Loads environment variables or defaults for connecting to the WA-AKG gateway,
with persistent disk override support via data/whatsapp_config.json.
Completely standalone with zero dependencies on external application domains.
"""

import json
from os import getenv
from pathlib import Path
import sys
from typing import Optional
from pydantic import BaseModel, Field

# Cross-platform root directory resolution
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = BASE_DIR / "data" / "whatsapp_config.json"


def load_persisted_config() -> dict:
    """Reads persistent configuration overrides from data/whatsapp_config.json if available."""
    if CONFIG_FILE.is_file():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WAConfig] Warning reading config file: {e}")
    return {}


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
        default_factory=lambda: getenv("WA_SIMULATION_MODE", "true").lower() in ("true", "1", "yes")
    )


# Load initial config with persistent overrides
_persisted = load_persisted_config()
config = WhatsAppGatewayConfig(
    gateway_url=_persisted.get("gateway_url", getenv("WA_GATEWAY_URL", "http://localhost:3000/api")),
    session_id=_persisted.get("session_id", getenv("WA_SESSION_ID", "default")),
    api_key=_persisted.get("api_key", getenv("WA_API_KEY", None)),
    enable_simulation_mode=_persisted.get(
        "enable_simulation_mode",
        getenv("WA_SIMULATION_MODE", "true").lower() in ("true", "1", "yes"),
    ),
)


def save_persisted_config(
    gateway_url: Optional[str] = None,
    session_id: Optional[str] = None,
    api_key: Optional[str] = None,
    enable_simulation_mode: Optional[bool] = None,
) -> dict:
    """Updates the live singleton and writes overrides to data/whatsapp_config.json."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    current = load_persisted_config()

    if gateway_url is not None:
        clean_url = gateway_url.strip().rstrip("/")
        current["gateway_url"] = clean_url
        config.gateway_url = clean_url

    if session_id is not None:
        clean_session = session_id.strip()
        current["session_id"] = clean_session
        config.session_id = clean_session

    if api_key is not None:
        clean_key = api_key.strip()
        current["api_key"] = clean_key if clean_key else None
        config.api_key = current["api_key"]

    if enable_simulation_mode is not None:
        current["enable_simulation_mode"] = bool(enable_simulation_mode)
        config.enable_simulation_mode = current["enable_simulation_mode"]

    try:
        CONFIG_FILE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[WAConfig] Error saving config file: {e}")

    return current
