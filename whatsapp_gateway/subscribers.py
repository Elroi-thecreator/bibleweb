"""
SQLite-backed persistent subscriber manager for WhatsApp Daily Scripture & Quiz alerts.
Completely isolated in data/whatsapp_subscribers.sqlite.db.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sqlite3
import threading
from typing import Any, Dict, List, Optional

# Path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "whatsapp_subscribers.sqlite.db"

_lock = threading.Lock()


def get_db_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_subscribers_db() -> None:
    """Creates the subscribers table if it does not already exist."""
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_subscribers (
                        phone_number TEXT PRIMARY KEY,
                        push_name TEXT,
                        language TEXT DEFAULT 'en',
                        plan_id TEXT DEFAULT 'proverbs-31',
                        is_active INTEGER DEFAULT 1,
                        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        finally:
            conn.close()


# Initialize on import
init_subscribers_db()


def _add_subscriber_sync(phone: str, name: str = "", language: str = "en", plan_id: str = "proverbs-31") -> bool:
    clean_phone = phone.strip()
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO whatsapp_subscribers (phone_number, push_name, language, plan_id, is_active, updated_at)
                    VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(phone_number) DO UPDATE SET
                        push_name = excluded.push_name,
                        language = excluded.language,
                        plan_id = excluded.plan_id,
                        is_active = 1,
                        updated_at = CURRENT_TIMESTAMP
                """, (clean_phone, name, language, plan_id))
            return True
        except Exception:
            return False
        finally:
            conn.close()


def _remove_subscriber_sync(phone: str) -> bool:
    clean_phone = phone.strip()
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number = ?
                """, (clean_phone,))
                return cursor.rowcount > 0
        except Exception:
            return False
        finally:
            conn.close()


def _get_active_subscribers_sync() -> List[Dict[str, Any]]:
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT phone_number, push_name, language, plan_id, subscribed_at, updated_at
                FROM whatsapp_subscribers
                WHERE is_active = 1
                ORDER BY subscribed_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()


def _get_subscriber_count_sync() -> int:
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM whatsapp_subscribers WHERE is_active = 1")
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            conn.close()


def _is_subscribed_sync(phone: str) -> bool:
    clean_phone = phone.strip()
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT 1 FROM whatsapp_subscribers WHERE phone_number = ? AND is_active = 1", (clean_phone,))
            return cursor.fetchone() is not None
        finally:
            conn.close()


# Async non-blocking wrappers adhering to DEV-PY-001
async def add_subscriber(phone: str, name: str = "", language: str = "en", plan_id: str = "proverbs-31") -> bool:
    return await asyncio.to_thread(_add_subscriber_sync, phone, name, language, plan_id)


async def remove_subscriber(phone: str) -> bool:
    return await asyncio.to_thread(_remove_subscriber_sync, phone)


async def get_active_subscribers() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_active_subscribers_sync)


async def get_subscriber_count() -> int:
    return await asyncio.to_thread(_get_subscriber_count_sync)


async def is_subscribed(phone: str) -> bool:
    return await asyncio.to_thread(_is_subscribed_sync, phone)
