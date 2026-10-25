"""
WhatsApp Gateway Configuration Module.
Loads environment variables or defaults for connecting to WhatsApp providers:
- Meta WhatsApp Business Cloud API (Official Cloud API & Developer Sandbox)
- WA-AKG (Baileys Multi-Device REST Gateway)
- Simulation Mode (Virtual In-Browser Assistant)
with persistent disk override support via data/whatsapp_config.json.
Completely standalone with zero dependencies on external application domains.
"""

import json
from os import getenv
from pathlib import Path
import sys
from typing import List, Optional
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
    """Configuration settings for WhatsApp Gateway and Providers."""

    # Provider selection: 'wa_akg', 'meta_cloud_api', 'simulation'
    provider: str = Field(
        default_factory=lambda: getenv("WA_PROVIDER", "wa_akg")
    )

    # WA-AKG Settings
    gateway_url: str = Field(
        default_factory=lambda: getenv("WA_GATEWAY_URL", "https://wa-akg-gateway-ub6a.onrender.com/api")
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

    # Meta WhatsApp Business Cloud API Settings
    meta_phone_number_id: Optional[str] = Field(
        default_factory=lambda: getenv("WA_META_PHONE_NUMBER_ID", None)
    )
    meta_waba_id: Optional[str] = Field(
        default_factory=lambda: getenv("WA_META_WABA_ID", None)
    )
    meta_access_token: Optional[str] = Field(
        default_factory=lambda: getenv("WA_META_ACCESS_TOKEN", None)
    )
    meta_verify_token: str = Field(
        default_factory=lambda: getenv("WA_META_VERIFY_TOKEN", "elroi_bible_verify_token")
    )
    meta_app_secret: Optional[str] = Field(
        default_factory=lambda: getenv("WA_META_APP_SECRET", None)
    )
    meta_api_version: str = Field(
        default_factory=lambda: getenv("WA_META_API_VERSION", "v21.0")
    )

    # General bot settings
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

    # RabbitMQ Queue Settings
    queue_enabled: bool = Field(
        default_factory=lambda: getenv("WA_QUEUE_ENABLED", "false").lower() in ("true", "1", "yes")
    )
    rabbitmq_url: str = Field(
        default_factory=lambda: getenv("WA_RABBITMQ_URL") or getenv("CLOUDAMQP_URL") or getenv("RABBITMQ_URL") or "amqp://guest:guest@localhost:5672/"
    )
    queue_incoming_name: str = Field(
        default_factory=lambda: getenv("WA_QUEUE_INCOMING_NAME", "whatsapp_incoming_messages")
    )
    queue_outgoing_name: str = Field(
        default_factory=lambda: getenv("WA_QUEUE_OUTGOING_NAME", "whatsapp_outgoing_messages")
    )
    queue_prefetch: int = Field(
        default_factory=lambda: int(getenv("WA_QUEUE_PREFETCH", "10"))
    )

    # Rate Limiting & User Quotas
    rate_limit_enabled: bool = Field(
        default_factory=lambda: getenv("WA_RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    rate_limit_requests_per_minute: int = Field(
        default_factory=lambda: int(getenv("WA_RATE_LIMIT_RPM", "20"))
    )
    rate_limit_audio_per_day: int = Field(
        default_factory=lambda: int(getenv("WA_RATE_LIMIT_AUDIO_PER_DAY", "15"))
    )
    rate_limit_cooldown_seconds: int = Field(
        default_factory=lambda: int(getenv("WA_RATE_LIMIT_COOLDOWN_SECONDS", "30"))
    )
    rate_limit_whitelist: List[str] = Field(
        default_factory=list
    )

    # Web Bible Application URL (for sync and links)
    web_app_url: str = Field(
        default_factory=lambda: getenv("WEB_APP_URL", "https://elroi-bible.vercel.app")
    )


# Load initial config with persistent overrides
_persisted = load_persisted_config()

# Derive initial provider
_initial_sim_mode = _persisted.get(
    "enable_simulation_mode",
    getenv("WA_SIMULATION_MODE", "true").lower() in ("true", "1", "yes"),
)
_initial_provider = _persisted.get(
    "provider",
    getenv("WA_PROVIDER", "simulation" if _initial_sim_mode else "wa_akg"),
)

config = WhatsAppGatewayConfig(
    provider=_initial_provider,
    gateway_url=_persisted.get("gateway_url", getenv("WA_GATEWAY_URL", "https://wa-akg-gateway-ub6a.onrender.com/api")),
    session_id=_persisted.get("session_id", getenv("WA_SESSION_ID", "default")),
    api_key=_persisted.get("api_key", getenv("WA_API_KEY", None)),
    enable_simulation_mode=_initial_sim_mode,
    meta_phone_number_id=_persisted.get("meta_phone_number_id", getenv("WA_META_PHONE_NUMBER_ID", None)),
    meta_waba_id=_persisted.get("meta_waba_id", getenv("WA_META_WABA_ID", None)),
    meta_access_token=_persisted.get("meta_access_token", getenv("WA_META_ACCESS_TOKEN", None)),
    meta_verify_token=_persisted.get("meta_verify_token", getenv("WA_META_VERIFY_TOKEN", "elroi_bible_verify_token")),
    meta_app_secret=_persisted.get("meta_app_secret", getenv("WA_META_APP_SECRET", None)),
    meta_api_version=_persisted.get("meta_api_version", getenv("WA_META_API_VERSION", "v21.0")),
    queue_enabled=_persisted.get(
        "queue_enabled",
        getenv("WA_QUEUE_ENABLED", "false").lower() in ("true", "1", "yes"),
    ),
    rabbitmq_url=_persisted.get(
        "rabbitmq_url",
        getenv("WA_RABBITMQ_URL") or getenv("CLOUDAMQP_URL") or getenv("RABBITMQ_URL") or "amqp://guest:guest@localhost:5672/",
    ),
    rate_limit_enabled=_persisted.get(
        "rate_limit_enabled",
        getenv("WA_RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes"),
    ),
    rate_limit_requests_per_minute=int(_persisted.get(
        "rate_limit_requests_per_minute",
        getenv("WA_RATE_LIMIT_RPM", "20"),
    )),
    rate_limit_audio_per_day=int(_persisted.get(
        "rate_limit_audio_per_day",
        getenv("WA_RATE_LIMIT_AUDIO_PER_DAY", "15"),
    )),
    rate_limit_cooldown_seconds=int(_persisted.get(
        "rate_limit_cooldown_seconds",
        getenv("WA_RATE_LIMIT_COOLDOWN_SECONDS", "30"),
    )),
    rate_limit_whitelist=list(_persisted.get(
        "rate_limit_whitelist",
        [],
    )),
    web_app_url=_persisted.get("web_app_url", getenv("WEB_APP_URL", "https://elroi-bible.vercel.app")),
)


def save_persisted_config(
    provider: Optional[str] = None,
    gateway_url: Optional[str] = None,
    session_id: Optional[str] = None,
    api_key: Optional[str] = None,
    enable_simulation_mode: Optional[bool] = None,
    meta_phone_number_id: Optional[str] = None,
    meta_waba_id: Optional[str] = None,
    meta_access_token: Optional[str] = None,
    meta_verify_token: Optional[str] = None,
    meta_app_secret: Optional[str] = None,
    meta_api_version: Optional[str] = None,
    queue_enabled: Optional[bool] = None,
    rabbitmq_url: Optional[str] = None,
    rate_limit_enabled: Optional[bool] = None,
    rate_limit_requests_per_minute: Optional[int] = None,
    rate_limit_audio_per_day: Optional[int] = None,
    rate_limit_cooldown_seconds: Optional[int] = None,
    rate_limit_whitelist: Optional[List[str]] = None,
    web_app_url: Optional[str] = None,
) -> dict:
    """Updates the live singleton and writes overrides to data/whatsapp_config.json."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    current = load_persisted_config()

    if provider is not None:
        clean_prov = provider.strip().lower()
        current["provider"] = clean_prov
        config.provider = clean_prov
        if clean_prov == "simulation":
            current["enable_simulation_mode"] = True
            config.enable_simulation_mode = True
        elif clean_prov in ("wa_akg", "meta_cloud_api"):
            current["enable_simulation_mode"] = False
            config.enable_simulation_mode = False

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
        if current["enable_simulation_mode"] and config.provider != "simulation":
            current["provider"] = "simulation"
            config.provider = "simulation"
        elif not current["enable_simulation_mode"] and config.provider == "simulation":
            current["provider"] = "wa_akg"
            config.provider = "wa_akg"

    if meta_phone_number_id is not None:
        clean_val = meta_phone_number_id.strip()
        current["meta_phone_number_id"] = clean_val if clean_val else None
        config.meta_phone_number_id = current["meta_phone_number_id"]

    if meta_waba_id is not None:
        clean_val = meta_waba_id.strip()
        current["meta_waba_id"] = clean_val if clean_val else None
        config.meta_waba_id = current["meta_waba_id"]

    if meta_access_token is not None:
        clean_val = meta_access_token.strip()
        current["meta_access_token"] = clean_val if clean_val else None
        config.meta_access_token = current["meta_access_token"]

    if meta_verify_token is not None:
        clean_val = meta_verify_token.strip()
        current["meta_verify_token"] = clean_val if clean_val else "elroi_bible_verify_token"
        config.meta_verify_token = current["meta_verify_token"]

    if meta_app_secret is not None:
        clean_val = meta_app_secret.strip()
        current["meta_app_secret"] = clean_val if clean_val else None
        config.meta_app_secret = current["meta_app_secret"]

    if meta_api_version is not None:
        clean_val = meta_api_version.strip().lstrip("v")
        current["meta_api_version"] = f"v{clean_val}" if clean_val else "v21.0"
        config.meta_api_version = current["meta_api_version"]

    if queue_enabled is not None:
        current["queue_enabled"] = bool(queue_enabled)
        config.queue_enabled = current["queue_enabled"]

    if rabbitmq_url is not None:
        clean_rmq = rabbitmq_url.strip()
        current["rabbitmq_url"] = clean_rmq
        config.rabbitmq_url = clean_rmq

    if rate_limit_enabled is not None:
        current["rate_limit_enabled"] = bool(rate_limit_enabled)
        config.rate_limit_enabled = current["rate_limit_enabled"]

    if rate_limit_requests_per_minute is not None:
        current["rate_limit_requests_per_minute"] = max(1, int(rate_limit_requests_per_minute))
        config.rate_limit_requests_per_minute = current["rate_limit_requests_per_minute"]

    if rate_limit_audio_per_day is not None:
        current["rate_limit_audio_per_day"] = max(1, int(rate_limit_audio_per_day))
        config.rate_limit_audio_per_day = current["rate_limit_audio_per_day"]

    if rate_limit_cooldown_seconds is not None:
        current["rate_limit_cooldown_seconds"] = max(1, int(rate_limit_cooldown_seconds))
        config.rate_limit_cooldown_seconds = current["rate_limit_cooldown_seconds"]

    if rate_limit_whitelist is not None:
        current["rate_limit_whitelist"] = [str(x).strip() for x in rate_limit_whitelist if str(x).strip()]
        config.rate_limit_whitelist = current["rate_limit_whitelist"]

    if web_app_url is not None:
        clean_web = web_app_url.strip().rstrip("/")
        current["web_app_url"] = clean_web
        config.web_app_url = clean_web

    try:
        CONFIG_FILE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[WAConfig] Error saving config file: {e}")

    return current
