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

# Cross-platform root directory and persistent local machine storage resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _get_persistent_paths(filename: str) -> tuple[Path, Optional[Path]]:
    """
    Returns (primary_path, machine_backup_path) for persistent configurations.
    - If running frozen in PyInstaller, primary is in %LOCALAPPDATA%/HolyBible/config
      so settings never disappear across builds or restarts.
    - If running from source, primary is project_root/data, and secondary is %LOCALAPPDATA%/HolyBible/config
      as an immutable machine-level backup across git cleans or workspace rebuilds.
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        machine_dir = Path(local_app_data) / "HolyBible" / "config"
    else:
        machine_dir = Path.home() / ".holybible" / "config"
    machine_file = machine_dir / filename

    if getattr(sys, "frozen", False):
        return machine_file, None
    else:
        project_file = PROJECT_ROOT / "data" / filename
        return project_file, machine_file


PRIMARY_CONFIG_FILE, BACKUP_CONFIG_FILE = _get_persistent_paths("bible_ai_config.json")
CONFIG_FILE = PRIMARY_CONFIG_FILE


def load_persisted_config() -> Dict[str, Any]:
    """Reads persistent configuration overrides from primary or machine backup location."""
    primary, secondary = _get_persistent_paths("bible_ai_config.json")

    # 1. Try primary location (project data/ in dev, %LOCALAPPDATA% in frozen)
    if primary.is_file():
        try:
            return json.loads(primary.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[AskBibleAIConfig] Warning reading config file: {e}")

    # 2. Try secondary/machine backup location (survives rebuilds/git cleans)
    if secondary and secondary.is_file():
        try:
            data = json.loads(secondary.read_text(encoding="utf-8"))
            # Mirror back to primary if writable
            try:
                primary.parent.mkdir(parents=True, exist_ok=True)
                primary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            return data
        except Exception as e:
            print(f"[AskBibleAIConfig] Warning reading machine backup config: {e}")

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

    # AI in Scripture Quiz Settings
    quiz_ai_enabled: bool = Field(
        default_factory=lambda: os.getenv("BIBLE_QUIZ_AI_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    quiz_ai_default_count: int = Field(
        default_factory=lambda: int(os.getenv("BIBLE_QUIZ_AI_COUNT", "5"))
    )
    quiz_ai_difficulty: str = Field(
        default_factory=lambda: os.getenv("BIBLE_QUIZ_AI_DIFFICULTY", "medium")
    )

    # AI Scripture Study & Verse Exegesis Settings
    study_ai_enabled: bool = Field(
        default_factory=lambda: os.getenv("BIBLE_STUDY_AI_ENABLED", "true").lower() in ("true", "1", "yes")
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
    """Persists runtime configuration changes to disk and machine backup."""
    global config
    current = load_persisted_config()
    current.update(updates)

    primary, secondary = _get_persistent_paths("bible_ai_config.json")
    json_str = json.dumps(current, indent=2, ensure_ascii=False)

    for p in (primary, secondary):
        if p:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json_str, encoding="utf-8")
            except Exception as e:
                print(f"[AskBibleAIConfig] Failed to save config to {p}: {e}")

    new_cfg = get_config()
    for field_name in config.model_fields.keys():
        setattr(config, field_name, getattr(new_cfg, field_name))

    return config


# Global singleton instance
config: AskBibleAIConfig = get_config()
