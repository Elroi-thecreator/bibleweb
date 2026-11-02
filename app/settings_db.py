"""
Centralized SQLite Database Persistence for System & Admin Settings.
Single source of truth for all runtime administrative configurations
(Ask Bible AI, WhatsApp Gateway, Rate Limiting, Quotas, Study, and Quiz parameters).
Eliminates ephemeral local JSON file loss and browser LocalStorage reliance.
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
import sqlite3
import sys
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger("app.settings_db")

# Cross-platform persistent database path resolution (supports dev, server & frozen PyInstaller exe)
if getattr(sys, "frozen", False):
    local_app_data = os.environ.get("LOCALAPPDATA")
    _base_dir = Path(local_app_data) / "HolyBible" if local_app_data else Path.home() / ".holybible"
    DEFAULT_SETTINGS_DB_PATH = _base_dir / "data" / "admin_settings.sqlite.db"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DEFAULT_SETTINGS_DB_PATH = PROJECT_ROOT / "data" / "admin_settings.sqlite.db"

SETTINGS_DB_PATH = Path(os.getenv("SETTINGS_DATABASE_PATH", str(DEFAULT_SETTINGS_DB_PATH)))

_lock = threading.Lock()
_initialized = False


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection configured with WAL mode and row factory."""
    SETTINGS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SETTINGS_DB_PATH), timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def _seed_initial_settings(conn: sqlite3.Connection) -> None:
    """
    Seeds the admin_settings database with existing configurations if empty.
    Checks existing JSON files (whatsapp_config.json, bible_ai_config.json) first,
    or falls back to environment variable defaults.
    """
    project_root = Path(__file__).resolve().parent.parent
    wa_json = project_root / "data" / "whatsapp_config.json"
    ai_json = project_root / "data" / "bible_ai_config.json"

    # 1. Seed WhatsApp settings
    wa_data: Dict[str, Any] = {}
    if wa_json.is_file():
        try:
            wa_data = json.loads(wa_json.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Could not read whatsapp_config.json during seed: %s", e)

    if not wa_data:
        wa_data = {
            "provider": os.getenv("WA_PROVIDER", "wa_akg"),
            "gateway_url": os.getenv("WA_GATEWAY_URL", "https://wa-akg-gateway-ub6a.onrender.com/api"),
            "session_id": os.getenv("WA_SESSION_ID", "default"),
            "api_key": os.getenv("WA_API_KEY", None),
            "enable_simulation_mode": os.getenv("WA_SIMULATION_MODE", "true").lower() in ("true", "1", "yes"),
            "meta_phone_number_id": os.getenv("WA_META_PHONE_NUMBER_ID", None),
            "meta_waba_id": os.getenv("WA_META_WABA_ID", None),
            "meta_access_token": os.getenv("WA_META_ACCESS_TOKEN", None),
            "meta_verify_token": os.getenv("WA_META_VERIFY_TOKEN", "elroi_bible_verify_token"),
            "meta_app_secret": os.getenv("WA_META_APP_SECRET", None),
            "meta_api_version": os.getenv("WA_META_API_VERSION", "v21.0"),
            "queue_enabled": os.getenv("WA_QUEUE_ENABLED", "false").lower() in ("true", "1", "yes"),
            "rabbitmq_url": os.getenv("WA_RABBITMQ_URL") or os.getenv("CLOUDAMQP_URL") or os.getenv("RABBITMQ_URL") or "amqp://guest:guest@localhost:5672/",
            "rate_limit_enabled": os.getenv("WA_RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes"),
            "rate_limit_requests_per_minute": int(os.getenv("WA_RATE_LIMIT_RPM", "20")),
            "rate_limit_audio_per_day": int(os.getenv("WA_RATE_LIMIT_AUDIO_PER_DAY", "15")),
            "rate_limit_cooldown_seconds": int(os.getenv("WA_RATE_LIMIT_COOLDOWN_SECONDS", "30")),
            "rate_limit_whitelist": [],
            "web_app_url": os.getenv("WEB_APP_URL", "https://elroi-bible.vercel.app"),
        }

    for k, v in wa_data.items():
        val_json = json.dumps(v, ensure_ascii=False)
        conn.execute(
            """
            INSERT OR REPLACE INTO admin_settings (section, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            ("whatsapp", k, val_json),
        )

    # 2. Seed Ask Bible AI settings
    ai_data: Dict[str, Any] = {}
    if ai_json.is_file():
        try:
            ai_data = json.loads(ai_json.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Could not read bible_ai_config.json during seed: %s", e)

    if not ai_data:
        ai_data = {
            "enabled": os.getenv("BIBLE_AI_ENABLED", "true").lower() in ("true", "1", "yes"),
            "provider_name": os.getenv("BIBLE_AI_PROVIDER", "freellmapi"),
            "base_url": os.getenv("BIBLE_AI_BASE_URL", "http://localhost:3000/v1"),
            "api_key": os.getenv("BIBLE_AI_API_KEY", "free-tier"),
            "model": os.getenv("BIBLE_AI_MODEL", "gemini-2.0-flash"),
            "temperature": float(os.getenv("BIBLE_AI_TEMPERATURE", "0.3")),
            "max_tokens": int(os.getenv("BIBLE_AI_MAX_TOKENS", "1024")),
            "enable_grounding": os.getenv("BIBLE_AI_GROUNDING", "true").lower() in ("true", "1", "yes"),
            "max_grounding_passages": int(os.getenv("BIBLE_AI_MAX_PASSAGES", "4")),
            "simulation_mode": os.getenv("BIBLE_AI_SIMULATION", "false").lower() in ("true", "1", "yes"),
            "quiz_ai_enabled": os.getenv("BIBLE_QUIZ_AI_ENABLED", "true").lower() in ("true", "1", "yes"),
            "quiz_ai_default_count": int(os.getenv("BIBLE_QUIZ_AI_COUNT", "5")),
            "quiz_ai_difficulty": os.getenv("BIBLE_QUIZ_AI_DIFFICULTY", "medium"),
            "study_ai_enabled": os.getenv("BIBLE_STUDY_AI_ENABLED", "true").lower() in ("true", "1", "yes"),
        }

    for k, v in ai_data.items():
        val_json = json.dumps(v, ensure_ascii=False)
        conn.execute(
            """
            INSERT OR REPLACE INTO admin_settings (section, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            ("ai", k, val_json),
        )


def init_settings_db() -> None:
    """Initializes the admin_settings SQLite database and ensures schema and initial seed."""
    global _initialized
    if _initialized:
        return

    with _lock:
        if _initialized:
            return
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS admin_settings (
                        section TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (section, key)
                    )
                """)
                cursor = conn.execute("SELECT COUNT(*) FROM admin_settings")
                count = cursor.fetchone()[0]
                if count == 0:
                    _seed_initial_settings(conn)
            _initialized = True
        finally:
            conn.close()


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """Fetches a single setting from the database, decoding from JSON."""
    init_settings_db()
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT value FROM admin_settings WHERE section = ? AND key = ?",
            (section, key),
        )
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except (json.JSONDecodeError, TypeError):
                return row["value"]
        return default
    finally:
        conn.close()


def set_setting(section: str, key: str, value: Any) -> None:
    """Persists a single setting into the database encoded as JSON."""
    init_settings_db()
    val_json = json.dumps(value, ensure_ascii=False)
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO admin_settings (section, key, value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(section, key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (section, key, val_json),
                )
        finally:
            conn.close()


def get_section(section: str) -> Dict[str, Any]:
    """Retrieves all settings within a section as a dictionary."""
    init_settings_db()
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT key, value FROM admin_settings WHERE section = ?",
            (section,),
        )
        results: Dict[str, Any] = {}
        for row in cursor.fetchall():
            k = row["key"]
            raw_v = row["value"]
            try:
                results[k] = json.loads(raw_v)
            except (json.JSONDecodeError, TypeError):
                results[k] = raw_v
        return results
    finally:
        conn.close()


def set_section(section: str, values: Dict[str, Any]) -> None:
    """Atomically saves multiple settings within a section in a transaction."""
    if not values:
        return
    init_settings_db()
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                for k, v in values.items():
                    val_json = json.dumps(v, ensure_ascii=False)
                    conn.execute(
                        """
                        INSERT INTO admin_settings (section, key, value, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(section, key) DO UPDATE SET
                            value = excluded.value,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (section, k, val_json),
                    )
        finally:
            conn.close()


def get_all_settings() -> Dict[str, Dict[str, Any]]:
    """Retrieves all settings across all sections grouped by section name."""
    init_settings_db()
    conn = get_db_connection()
    try:
        cursor = conn.execute("SELECT section, key, value FROM admin_settings ORDER BY section, key")
        grouped: Dict[str, Dict[str, Any]] = {}
        for row in cursor.fetchall():
            sec = row["section"]
            k = row["key"]
            raw_v = row["value"]
            try:
                val = json.loads(raw_v)
            except (json.JSONDecodeError, TypeError):
                val = raw_v
            if sec not in grouped:
                grouped[sec] = {}
            grouped[sec][k] = val
        return grouped
    finally:
        conn.close()


def save_all_settings(data: Dict[str, Dict[str, Any]]) -> None:
    """Atomically saves all sections and their key-value pairs in a single transaction."""
    init_settings_db()
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                for section, values in data.items():
                    if isinstance(values, dict):
                        for k, v in values.items():
                            val_json = json.dumps(v, ensure_ascii=False)
                            conn.execute(
                                """
                                INSERT INTO admin_settings (section, key, value, updated_at)
                                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                                ON CONFLICT(section, key) DO UPDATE SET
                                    value = excluded.value,
                                    updated_at = CURRENT_TIMESTAMP
                                """,
                                (section, k, val_json),
                            )
        finally:
            conn.close()


def get_settings_db_stats() -> Dict[str, Any]:
    """Returns database telemetry: file path, size in KB, total rows, and connection health."""
    init_settings_db()
    exists = SETTINGS_DB_PATH.exists()
    size_kb = round(SETTINGS_DB_PATH.stat().st_size / 1024, 1) if exists else 0.0
    row_count = 0
    last_updated = None

    if exists:
        try:
            conn = get_db_connection()
            cursor = conn.execute("SELECT COUNT(*), MAX(updated_at) FROM admin_settings")
            row = cursor.fetchone()
            if row:
                row_count = row[0]
                last_updated = row[1]
            conn.close()
        except Exception as e:
            logger.warning("Error fetching settings db telemetry: %s", e)

    return {
        "path": str(SETTINGS_DB_PATH),
        "size_kb": size_kb,
        "row_count": row_count,
        "last_updated": last_updated,
        "is_connected": True,
    }
