"""
Centralized Database Persistence for System & Admin Settings.
Single source of truth for all runtime administrative configurations
(Ask Bible AI, WhatsApp Gateway, Rate Limiting, Quotas, Study, and Quiz parameters).

Supports:
1. External PostgreSQL / Supabase if DATABASE_URL / POSTGRES_URL is configured.
2. Embedded SQLite (data/admin_settings.sqlite.db) with seamless /tmp fallback
   for serverless platforms (Vercel, AWS Lambda) and %LOCALAPPDATA% for PyInstaller desktop.
Eliminates ephemeral local JSON loss and browser LocalStorage reliance.
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import threading
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("app.settings_db")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_lock = threading.Lock()
_initialized = False
_using_postgres = False


def _get_postgres_url() -> Optional[str]:
    """Retrieves PostgreSQL / Supabase database connection URL if provided."""
    url = (
        os.getenv("SETTINGS_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("SUPABASE_DATABASE_URL")
    )
    if url and (url.startswith("postgres://") or url.startswith("postgresql://")):
        # SQLAlchemy / psycopg2 compatibility: normalize postgres:// to postgresql://
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url
    return None


def _resolve_settings_db_path() -> Path:
    """
    Resolves the writable SQLite database path across platforms:
    - Custom override via SETTINGS_DATABASE_PATH
    - Frozen PyInstaller desktop app -> %LOCALAPPDATA%/HolyBible/data/admin_settings.sqlite.db
    - Vercel Serverless / AWS Lambda -> /tmp/admin_settings.sqlite.db (hydrated from bundled data/)
    - Standard server/local dev -> PROJECT_ROOT / "data" / "admin_settings.sqlite.db"
    - Read-only filesystem fallback -> /tmp/admin_settings.sqlite.db
    """
    custom = os.getenv("SETTINGS_DATABASE_PATH")
    if custom:
        return Path(custom)

    # 1. PyInstaller frozen desktop mode
    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        base_dir = Path(local_app_data) / "HolyBible" if local_app_data else Path.home() / ".holybible"
        return base_dir / "data" / "admin_settings.sqlite.db"

    # 2. Vercel Serverless or AWS Lambda environment
    is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if is_serverless:
        tmp_dir = Path(tempfile.gettempdir())
        tmp_db = tmp_dir / "admin_settings.sqlite.db"
        bundled_db = PROJECT_ROOT / "data" / "admin_settings.sqlite.db"
        if not tmp_db.exists() and bundled_db.exists():
            try:
                shutil.copy2(bundled_db, tmp_db)
            except Exception as e:
                logger.warning("Could not copy bundled settings db to /tmp: %s", e)
        return tmp_db

    # 3. Standard local dev / persistent server
    std_db = PROJECT_ROOT / "data" / "admin_settings.sqlite.db"
    try:
        std_db.parent.mkdir(parents=True, exist_ok=True)
        # Verify write permission
        test_file = std_db.parent / ".perm_check"
        test_file.touch()
        test_file.unlink()
        return std_db
    except (OSError, PermissionError):
        # Fallback to /tmp if read-only filesystem detected
        tmp_dir = Path(tempfile.gettempdir())
        tmp_db = tmp_dir / "admin_settings.sqlite.db"
        bundled_db = PROJECT_ROOT / "data" / "admin_settings.sqlite.db"
        if not tmp_db.exists() and bundled_db.exists():
            try:
                shutil.copy2(bundled_db, tmp_db)
            except Exception:
                pass
        return tmp_db


def _get_sqlite_connection() -> sqlite3.Connection:
    """Returns an SQLite connection configured with journal mode and row factory."""
    db_path = _resolve_settings_db_path()
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    conn = sqlite3.connect(str(db_path), timeout=15.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        try:
            conn.execute("PRAGMA journal_mode=DELETE;")
        except Exception:
            pass
    return conn


def _get_pg_connection():
    """Attempts to connect to external PostgreSQL / Supabase cluster."""
    pg_url = _get_postgres_url()
    if not pg_url:
        return None
    try:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(pg_url, connect_timeout=5)
        return conn
    except Exception as e:
        logger.warning("PostgreSQL connection failed, falling back to SQLite: %s", e)
        return None


def _seed_initial_settings(conn: sqlite3.Connection) -> None:
    """
    Seeds the admin_settings database with existing configurations if empty.
    Checks existing JSON files (whatsapp_config.json, bible_ai_config.json) first,
    or falls back to environment variable defaults.
    """
    wa_json = PROJECT_ROOT / "data" / "whatsapp_config.json"
    ai_json = PROJECT_ROOT / "data" / "bible_ai_config.json"

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
    """Initializes admin_settings table across PostgreSQL or SQLite and ensures schema and seed."""
    global _initialized, _using_postgres
    if _initialized:
        return

    with _lock:
        if _initialized:
            return

        # 1. Try PostgreSQL if available
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn:
                    with pg_conn.cursor() as cur:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS admin_settings (
                                section VARCHAR(128) NOT NULL,
                                key VARCHAR(128) NOT NULL,
                                value TEXT NOT NULL,
                                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                                PRIMARY KEY (section, key)
                            )
                        """)
                        cur.execute("SELECT COUNT(*) FROM admin_settings")
                        count = cur.fetchone()[0]
                        if count == 0:
                            # Seed PostgreSQL from local SQLite or defaults
                            local_conn = _get_sqlite_connection()
                            try:
                                _seed_initial_settings(local_conn)
                                local_conn.commit()
                                cursor = local_conn.execute("SELECT section, key, value FROM admin_settings")
                                for row in cursor.fetchall():
                                    cur.execute("""
                                        INSERT INTO admin_settings (section, key, value, updated_at)
                                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                                        ON CONFLICT (section, key) DO UPDATE SET
                                            value = EXCLUDED.value,
                                            updated_at = CURRENT_TIMESTAMP
                                    """, (row["section"], row["key"], row["value"]))
                            finally:
                                local_conn.close()
                _using_postgres = True
                _initialized = True
                return
            except Exception as e:
                logger.warning("Error initializing PostgreSQL settings table: %s", e)
            finally:
                pg_conn.close()

        # 2. SQLite local / fallback
        try:
            conn = _get_sqlite_connection()
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
        except Exception as sq_err:
            logger.warning("Error initializing SQLite settings table: %s", sq_err)


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """Fetches a single setting from the database, decoding from JSON."""
    init_settings_db()

    # Try PostgreSQL first if active
    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn.cursor() as cur:
                    cur.execute(
                        "SELECT value FROM admin_settings WHERE section = %s AND key = %s",
                        (section, key),
                    )
                    row = cur.fetchone()
                    if row:
                        try:
                            return json.loads(row[0])
                        except Exception:
                            return row[0]
            except Exception as e:
                logger.warning("Postgres get_setting error: %s", e)
            finally:
                pg_conn.close()

    try:
        conn = _get_sqlite_connection()
        try:
            cursor = conn.execute(
                "SELECT value FROM admin_settings WHERE section = ? AND key = ?",
                (section, key),
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["value"])
                except Exception:
                    return row["value"]
            return default
        finally:
            conn.close()
    except Exception as e:
        logger.warning("SQLite get_setting error: %s", e)
        return default


def set_setting(section: str, key: str, value: Any) -> None:
    """Persists a single setting into the database encoded as JSON."""
    init_settings_db()
    val_json = json.dumps(value, ensure_ascii=False)

    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn:
                    with pg_conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO admin_settings (section, key, value, updated_at)
                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                            ON CONFLICT (section, key) DO UPDATE SET
                                value = EXCLUDED.value,
                                updated_at = CURRENT_TIMESTAMP
                            """,
                            (section, key, val_json),
                        )
            except Exception as e:
                logger.warning("Postgres set_setting error: %s", e)
            finally:
                pg_conn.close()

    with _lock:
        try:
            conn = _get_sqlite_connection()
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
        except Exception as e:
            logger.warning("SQLite set_setting error: %s", e)


def get_section(section: str) -> Dict[str, Any]:
    """Retrieves all settings within a section as a dictionary."""
    init_settings_db()

    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn.cursor() as cur:
                    cur.execute(
                        "SELECT key, value FROM admin_settings WHERE section = %s",
                        (section,),
                    )
                    results: Dict[str, Any] = {}
                    for row in cur.fetchall():
                        k = row[0]
                        raw_v = row[1]
                        try:
                            results[k] = json.loads(raw_v)
                        except Exception:
                            results[k] = raw_v
                    if results:
                        return results
            except Exception as e:
                logger.warning("Postgres get_section error: %s", e)
            finally:
                pg_conn.close()

    try:
        conn = _get_sqlite_connection()
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
                except Exception:
                    results[k] = raw_v
            return results
        finally:
            conn.close()
    except Exception as e:
        logger.warning("SQLite get_section error: %s", e)
        return {}


def set_section(section: str, values: Dict[str, Any]) -> None:
    """Atomically saves multiple settings within a section."""
    if not values:
        return
    init_settings_db()

    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn:
                    with pg_conn.cursor() as cur:
                        for k, v in values.items():
                            val_json = json.dumps(v, ensure_ascii=False)
                            cur.execute(
                                """
                                INSERT INTO admin_settings (section, key, value, updated_at)
                                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                                ON CONFLICT (section, key) DO UPDATE SET
                                    value = EXCLUDED.value,
                                    updated_at = CURRENT_TIMESTAMP
                                """,
                                (section, k, val_json),
                            )
            except Exception as e:
                logger.warning("Postgres set_section error: %s", e)
            finally:
                pg_conn.close()

    with _lock:
        try:
            conn = _get_sqlite_connection()
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
        except Exception as e:
            logger.warning("SQLite set_section error: %s", e)


def get_all_settings() -> Dict[str, Dict[str, Any]]:
    """Retrieves all settings across all sections grouped by section name."""
    init_settings_db()

    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn.cursor() as cur:
                    cur.execute("SELECT section, key, value FROM admin_settings ORDER BY section, key")
                    grouped: Dict[str, Dict[str, Any]] = {}
                    for row in cur.fetchall():
                        sec = row[0]
                        k = row[1]
                        raw_v = row[2]
                        try:
                            val = json.loads(raw_v)
                        except Exception:
                            val = raw_v
                        if sec not in grouped:
                            grouped[sec] = {}
                        grouped[sec][k] = val
                    if grouped:
                        return grouped
            except Exception as e:
                logger.warning("Postgres get_all_settings error: %s", e)
            finally:
                pg_conn.close()

    try:
        conn = _get_sqlite_connection()
        try:
            cursor = conn.execute("SELECT section, key, value FROM admin_settings ORDER BY section, key")
            grouped: Dict[str, Dict[str, Any]] = {}
            for row in cursor.fetchall():
                sec = row["section"]
                k = row["key"]
                raw_v = row["value"]
                try:
                    val = json.loads(raw_v)
                except Exception:
                    val = raw_v
                if sec not in grouped:
                    grouped[sec] = {}
                grouped[sec][k] = val
            return grouped
        finally:
            conn.close()
    except Exception as e:
        logger.warning("SQLite get_all_settings error: %s", e)
        return {}


def save_all_settings(data: Dict[str, Dict[str, Any]]) -> None:
    """Atomically saves all sections and their key-value pairs."""
    init_settings_db()

    if _using_postgres:
        pg_conn = _get_pg_connection()
        if pg_conn:
            try:
                with pg_conn:
                    with pg_conn.cursor() as cur:
                        for section, values in data.items():
                            if isinstance(values, dict):
                                for k, v in values.items():
                                    val_json = json.dumps(v, ensure_ascii=False)
                                    cur.execute(
                                        """
                                        INSERT INTO admin_settings (section, key, value, updated_at)
                                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                                        ON CONFLICT (section, key) DO UPDATE SET
                                            value = EXCLUDED.value,
                                            updated_at = CURRENT_TIMESTAMP
                                        """,
                                        (section, k, val_json),
                                    )
            except Exception as e:
                logger.warning("Postgres save_all_settings error: %s", e)
            finally:
                pg_conn.close()

    with _lock:
        try:
            conn = _get_sqlite_connection()
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
        except Exception as e:
            logger.warning("SQLite save_all_settings error: %s", e)


def get_settings_db_stats() -> Dict[str, Any]:
    """Returns database telemetry: file path, size in KB, total rows, and connection health."""
    try:
        init_settings_db()
        db_path = _resolve_settings_db_path()
        exists = db_path.exists()
        size_kb = round(db_path.stat().st_size / 1024, 1) if exists else 0.0
        row_count = 0
        last_updated = None

        if _using_postgres:
            pg_conn = _get_pg_connection()
            if pg_conn:
                try:
                    with pg_conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*), MAX(updated_at) FROM admin_settings")
                        row = cur.fetchone()
                        if row:
                            row_count = row[0]
                            last_updated = str(row[1]) if row[1] else None
                    return {
                        "path": "PostgreSQL / Supabase (Cloud Cluster)",
                        "size_kb": size_kb,
                        "row_count": row_count,
                        "last_updated": last_updated,
                        "is_connected": True,
                        "engine": "postgresql",
                    }
                except Exception:
                    pass
                finally:
                    pg_conn.close()

        if exists:
            conn = _get_sqlite_connection()
            try:
                cursor = conn.execute("SELECT COUNT(*), MAX(updated_at) FROM admin_settings")
                row = cursor.fetchone()
                if row:
                    row_count = row[0]
                    last_updated = row[1]
            finally:
                conn.close()

        return {
            "path": str(db_path),
            "size_kb": size_kb,
            "row_count": row_count,
            "last_updated": last_updated,
            "is_connected": True,
            "engine": "sqlite",
        }
    except Exception as e:
        logger.warning("Error fetching settings db telemetry: %s", e)
        return {
            "path": "admin_settings.sqlite.db",
            "size_kb": 0.0,
            "row_count": 0,
            "last_updated": None,
            "is_connected": False,
            "engine": "fallback",
            "error": str(e),
        }


def load_all_settings_into_app() -> Dict[str, Any]:
    """
    Loads all administrative runtime settings from the database and updates the
    in-memory singletons across the application:
    - whatsapp_gateway.config.config
    - whatsapp_gateway.routes.webhook._client (WAClient)
    - ask_bible_ai.config.config
    - ask_bible_ai.service.ai_service
    This is called:
    1. During app startup / restart (in lifespan).
    2. When an administrator saves/changes settings (via API or admin portal).
    3. When the administrator explicitly reloads from the database.
    Never run on a timer or background loop.
    """
    init_settings_db()
    all_settings = get_all_settings()
    wa_settings = all_settings.get("whatsapp", {})
    ai_settings = all_settings.get("ai", {})

    wa_dict: Dict[str, Any] = {}
    ai_dict: Dict[str, Any] = {}

    # 1. Apply WhatsApp settings to singleton & WAClient
    try:
        from whatsapp_gateway.config import config as wa_cfg
        for k, v in wa_settings.items():
            if hasattr(wa_cfg, k):
                setattr(wa_cfg, k, v)
        wa_dict = wa_cfg.model_dump()

        try:
            from whatsapp_gateway.routes.webhook import get_client
            client = get_client()
            if client:
                client.update_config(
                    base_url=wa_cfg.gateway_url,
                    default_session_id=wa_cfg.session_id,
                    api_key=wa_cfg.api_key,
                    simulation_mode=wa_cfg.enable_simulation_mode,
                    provider=wa_cfg.provider,
                    meta_phone_number_id=wa_cfg.meta_phone_number_id,
                    meta_waba_id=wa_cfg.meta_waba_id,
                    meta_access_token=wa_cfg.meta_access_token,
                    meta_verify_token=wa_cfg.meta_verify_token,
                    meta_app_secret=wa_cfg.meta_app_secret,
                    meta_api_version=wa_cfg.meta_api_version,
                )
        except Exception as client_err:
            logger.debug("Could not update WA client during settings load: %s", client_err)
    except Exception as wa_err:
        logger.warning("Error loading WA settings into app: %s", wa_err)

    # 2. Apply Ask Bible AI settings to singleton & AIService
    try:
        from ask_bible_ai.config import config as ai_cfg
        for k, v in ai_settings.items():
            if hasattr(ai_cfg, k):
                setattr(ai_cfg, k, v)
        ai_dict = ai_cfg.to_dict()

        try:
            from ask_bible_ai.service import ai_service
            if ai_service:
                ai_service.config = ai_cfg
                if hasattr(ai_service, "client") and ai_service.client:
                    ai_service.client.config = ai_cfg
        except Exception as ai_svc_err:
            logger.debug("Could not update AI service during settings load: %s", ai_svc_err)
    except Exception as ai_err:
        logger.warning("Error loading AI settings into app: %s", ai_err)

    logger.info("Admin settings loaded into app memory from database")
    return {"whatsapp": wa_dict, "ai": ai_dict}
