"""
Ask Bible AI Configuration Module.
Provides centralized, decoupled configuration for OpenAI-compatible LLM endpoints
(such as FreeLLMAPI, Ollama, Groq Cloud, GitHub Models, or OpenAI).
Supports environment variables with persistent JSON overrides on disk.
Zero dependencies on external application domains.
"""

import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

# Cross-platform root directory resolution
if getattr(sys, "frozen", False):
    ROOT_DIR = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT_DIR / "data" / "bible_ai_config.json"


def load_persisted_config() -> Dict[str, Any]:
    """Reads persistent configuration overrides from data/bible_ai_config.json if available."""
    if CONFIG_FILE.is_file():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[AskBibleAIConfig] Warning reading config file: {e}")
    return {}


class AskBibleAIConfig(BaseModel):
    """Configuration settings for Ask Bible AI Plugin."""

    # General toggle
    enabled: bool = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_ENABLED", "true").lower() in ("true", "1", "yes")
    )

    # Provider identification (e.g., 'freellmapi', 'ollama', 'groq', 'openai', 'simulation')
    provider_name: str = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_PROVIDER", "freellmapi")
    )

    # OpenAI-compatible API base URL (Default targets local FreeLLMAPI gateway or Ollama)
    base_url: str = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_BASE_URL", "http://localhost:3000/v1")
    )

    # API Key (FreeLLMAPI uses dummy key, Groq/OpenAI use their API keys)
    api_key: str = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_API_KEY", "free-tier")
    )

    # Model name to request from provider
    model: str = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_MODEL", "gemini-2.0-flash")
    )

    # Generation parameters
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("BIBLE_AI_TEMPERATURE", "0.3"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("BIBLE_AI_MAX_TOKENS", "1024"))
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("BIBLE_AI_TIMEOUT", "30.0"))
    )

    # Grounding & Verification
    enable_grounding: bool = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_GROUNDING", "true").lower() in ("true", "1", "yes")
    )
    max_grounding_passages: int = Field(
        default_factory=lambda: int(os.getenv("BIBLE_AI_MAX_PASSAGES", "4"))
    )

    # Offline / Simulation mode (when True, uses rich theological mock responses without network calls)
    simulation_mode: bool = Field(
        default_factory=lambda: os.getenv("BIBLE_AI_SIMULATION", "false").lower() in ("true", "1", "yes")
    )

    def to_dict(self) -> Dict[str, Any]:
        """Returns safe dictionary representation masking sensitive keys."""
        d = self.model_dump()
        if d.get("api_key") and len(d["api_key"]) > 8 and d["api_key"] != "free-tier":
            d["api_key"] = d["api_key"][:4] + "..." + d["api_key"][-4:]
        return d


def get_config() -> AskBibleAIConfig:
    """Builds config merging environment defaults with persistent overrides."""
    overrides = load_persisted_config()
    cfg = AskBibleAIConfig()
    for key, val in overrides.items():
        if hasattr(cfg, key):
            setattr(cfg, key, val)
    return cfg


def save_persisted_config(updates: Dict[str, Any]) -> AskBibleAIConfig:
    """Persists runtime configuration changes to disk and updates singleton."""
    global config
    current = load_persisted_config()
    current.update(updates)

    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[AskBibleAIConfig] Failed to save config to disk: {e}")

    config = get_config()
    return config


# Global singleton instance
config: AskBibleAIConfig = get_config()
