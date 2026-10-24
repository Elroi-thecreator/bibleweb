"""
SQLite-backed persistent subscriber manager for WhatsApp Daily Scripture & Quiz alerts.
Completely isolated in data/whatsapp_subscribers.sqlite.db.
Supports configurable reminder dispatch times (default: 5:00 AM / '05:00') and reading plans.
"""

import asyncio
from datetime import datetime
import json
import logging
from pathlib import Path
import sqlite3
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger("whatsapp_gateway.subscribers")

# Path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "whatsapp_subscribers.sqlite.db"
JSON_BACKUP_PATH = DATA_DIR / "whatsapp_subscribers.json"

_lock = threading.Lock()


def get_db_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _save_json_backup(conn: sqlite3.Connection) -> None:
    """Persists active subscribers to JSON file for zero-loss recovery across ephemeral restarts."""
    try:
        cursor = conn.execute("""
            SELECT phone_number, push_name, language, plan_id, reminder_time, plan_start_date,
                   streak_count, last_read_date, completed_days, is_active, subscribed_at, updated_at
            FROM whatsapp_subscribers
            WHERE is_active = 1
            ORDER BY subscribed_at DESC
        """)
        subs = [dict(row) for row in cursor.fetchall()]
        with open(JSON_BACKUP_PATH, "w", encoding="utf-8") as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Failed to save JSON backup: %s", e)


def init_subscribers_db() -> None:
    """Creates the subscribers table, runs migrations, and hydrates from JSON backup if empty."""
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_subscribers (
                        phone_number TEXT PRIMARY KEY,
                        push_name TEXT,
                        language TEXT DEFAULT 'en',
                        plan_id TEXT DEFAULT 'full-bible-365',
                        reminder_time TEXT DEFAULT '05:00',
                        plan_start_date TEXT,
                        streak_count INTEGER DEFAULT 0,
                        last_read_date TEXT DEFAULT '',
                        completed_days TEXT DEFAULT '[]',
                        is_active INTEGER DEFAULT 1,
                        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Automatic schema migration: ensure reminder_time, plan_start_date, streak_count, last_read_date, completed_days exist
                cursor = conn.execute("PRAGMA table_info(whatsapp_subscribers)")
                existing_cols = [row["name"] for row in cursor.fetchall()]
                if "reminder_time" not in existing_cols:
                    conn.execute("ALTER TABLE whatsapp_subscribers ADD COLUMN reminder_time TEXT DEFAULT '05:00'")
                if "plan_start_date" not in existing_cols:
                    conn.execute("ALTER TABLE whatsapp_subscribers ADD COLUMN plan_start_date TEXT")
                    conn.execute("UPDATE whatsapp_subscribers SET plan_start_date = DATE(subscribed_at) WHERE plan_start_date IS NULL OR plan_start_date = ''")
                if "streak_count" not in existing_cols:
                    conn.execute("ALTER TABLE whatsapp_subscribers ADD COLUMN streak_count INTEGER DEFAULT 0")
                if "last_read_date" not in existing_cols:
                    conn.execute("ALTER TABLE whatsapp_subscribers ADD COLUMN last_read_date TEXT DEFAULT ''")
                if "completed_days" not in existing_cols:
                    conn.execute("ALTER TABLE whatsapp_subscribers ADD COLUMN completed_days TEXT DEFAULT '[]'")

                # Hydrate from JSON backup if table is brand new/empty
                cursor = conn.execute("SELECT COUNT(*) FROM whatsapp_subscribers WHERE is_active = 1")
                count = cursor.fetchone()[0]
                if count == 0 and JSON_BACKUP_PATH.exists():
                    try:
                        with open(JSON_BACKUP_PATH, "r", encoding="utf-8") as f:
                            saved = json.load(f)
                            for item in saved:
                                conn.execute("""
                                    INSERT OR REPLACE INTO whatsapp_subscribers
                                    (phone_number, push_name, language, plan_id, reminder_time, plan_start_date,
                                     streak_count, last_read_date, completed_days, is_active, subscribed_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                """, (
                                    item.get("phone_number"),
                                    item.get("push_name", ""),
                                    item.get("language", "en"),
                                    item.get("plan_id", "full-bible-365"),
                                    item.get("reminder_time", "05:00"),
                                    item.get("plan_start_date") or (item.get("subscribed_at")[:10] if item.get("subscribed_at") else datetime.now().strftime("%Y-%m-%d")),
                                    item.get("streak_count", 0),
                                    item.get("last_read_date", ""),
                                    item.get("completed_days", "[]"),
                                    item.get("is_active", 1),
                                    item.get("subscribed_at", datetime.now().isoformat()),
                                ))
                    except Exception as err:
                        logger.warning("Error during JSON hydration: %s", err)
        finally:
            conn.close()


# Initialize on import
init_subscribers_db()


def _phone_variants(phone: str) -> tuple[str, str, str]:
    """Returns (raw_clean, pure_digits, whatsapp_jid) for flexible identifier matching."""
    clean = phone.strip()
    digits = clean.split("@")[0].replace("+", "").replace(" ", "").replace("-", "").strip()
    jid = f"{digits}@s.whatsapp.net"
    return clean, digits, jid


def _add_subscriber_sync(
    phone: str,
    name: str = "",
    language: str = "en",
    plan_id: str = "full-bible-365",
    reminder_time: str = "05:00",
    plan_start_date: Optional[str] = None,
) -> bool:
    clean_phone = phone.strip()
    clean_time = reminder_time.strip() if reminder_time else "05:00"
    clean_start_date = plan_start_date.strip() if plan_start_date else datetime.now().strftime("%Y-%m-%d")
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO whatsapp_subscribers (phone_number, push_name, language, plan_id, reminder_time, plan_start_date, is_active, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(phone_number) DO UPDATE SET
                        push_name = excluded.push_name,
                        language = excluded.language,
                        plan_id = excluded.plan_id,
                        reminder_time = excluded.reminder_time,
                        plan_start_date = CASE
                            WHEN whatsapp_subscribers.plan_id != excluded.plan_id THEN excluded.plan_start_date
                            WHEN whatsapp_subscribers.plan_start_date IS NULL OR whatsapp_subscribers.plan_start_date = '' THEN excluded.plan_start_date
                            ELSE whatsapp_subscribers.plan_start_date
                        END,
                        is_active = 1,
                        updated_at = CURRENT_TIMESTAMP
                """, (clean_phone, name, language, plan_id, clean_time, clean_start_date))
                _save_json_backup(conn)
            return True
        except Exception as exc:
            logger.error("Failed to add subscriber %s: %s", clean_phone, exc)
            return False
        finally:
            conn.close()


def _update_subscriber_reminder_time_sync(phone: str, reminder_time: str) -> bool:
    """Updates the daily reminder dispatch time for an active subscriber."""
    clean, digits, jid = _phone_variants(phone)
    clean_time = reminder_time.strip()
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET reminder_time = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number IN (?, ?, ?)
                """, (clean_time, clean, digits, jid))
                if cursor.rowcount == 0:
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    # If not yet registered, auto-register with default plan and specified time
                    conn.execute("""
                        INSERT INTO whatsapp_subscribers (phone_number, reminder_time, plan_start_date, is_active, updated_at)
                        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                    """, (clean, clean_time, today_str))
                _save_json_backup(conn)
                return True
        except Exception as exc:
            logger.error("Failed to update reminder time for %s: %s", clean, exc)
            return False
        finally:
            conn.close()


def _update_subscriber_plan_sync(phone: str, plan_id: str, plan_start_date: Optional[str] = None) -> bool:
    """Updates the assigned reading plan for an active subscriber, resetting their individual start date to today."""
    clean, digits, jid = _phone_variants(phone)
    clean_plan = plan_id.strip()
    clean_start_date = plan_start_date.strip() if plan_start_date else datetime.now().strftime("%Y-%m-%d")
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET plan_id = ?, plan_start_date = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number IN (?, ?, ?)
                """, (clean_plan, clean_start_date, clean, digits, jid))
                if cursor.rowcount == 0:
                    conn.execute("""
                        INSERT INTO whatsapp_subscribers (phone_number, plan_id, plan_start_date, is_active, updated_at)
                        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                    """, (clean, clean_plan, clean_start_date))
                _save_json_backup(conn)
                return True
        except Exception as exc:
            logger.error("Failed to update plan for %s: %s", clean, exc)
            return False
        finally:
            conn.close()


def _remove_subscriber_sync(phone: str) -> bool:
    clean, digits, jid = _phone_variants(phone)
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number IN (?, ?, ?)
                """, (clean, digits, jid))
                _save_json_backup(conn)
                return cursor.rowcount > 0
        except Exception as exc:
            logger.error("Failed to remove subscriber %s: %s", clean, exc)
            return False
        finally:
            conn.close()


def _update_subscriber_language_sync(phone: str, language: str) -> bool:
    """Updates preferred language: 'en', 'ta', or 'both' (bilingual parallel)."""
    clean, digits, jid = _phone_variants(phone)
    clean_lang = language.strip().lower()
    if clean_lang not in ("en", "ta", "both"):
        clean_lang = "both"
    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET language = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number IN (?, ?, ?)
                """, (clean_lang, clean, digits, jid))
                if cursor.rowcount == 0:
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    conn.execute("""
                        INSERT INTO whatsapp_subscribers (phone_number, language, plan_start_date, is_active, updated_at)
                        VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                    """, (clean, clean_lang, today_str))
                _save_json_backup(conn)
                return True
        except Exception as exc:
            logger.error("Failed to update language for %s: %s", clean, exc)
            return False
        finally:
            conn.close()


def _mark_subscriber_day_done_sync(phone: str, day: Optional[int] = None) -> Dict[str, Any]:
    """Marks a reading plan day as completed, calculating consecutive daily streaks."""
    from datetime import date, timedelta
    clean, digits, jid = _phone_variants(phone)
    today_date = datetime.now().date()
    today_str = today_date.strftime("%Y-%m-%d")
    yesterday_str = (today_date - timedelta(days=1)).strftime("%Y-%m-%d")

    with _lock:
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.execute("""
                    SELECT phone_number, push_name, language, plan_id, plan_start_date,
                           streak_count, last_read_date, completed_days
                    FROM whatsapp_subscribers
                    WHERE phone_number IN (?, ?, ?)
                """, (clean, digits, jid))
                row = cursor.fetchone()
                if not row:
                    # Auto-register subscriber if not yet in database
                    conn.execute("""
                        INSERT INTO whatsapp_subscribers (phone_number, plan_start_date, streak_count, last_read_date, completed_days, is_active, updated_at)
                        VALUES (?, ?, 1, ?, ?, 1, CURRENT_TIMESTAMP)
                    """, (clean, today_str, today_str, json.dumps([day or 1])))
                    _save_json_backup(conn)
                    return {
                        "success": True,
                        "day": day or 1,
                        "streak_count": 1,
                        "completed_count": 1,
                        "already_marked": False,
                        "plan_id": "full-bible-365",
                    }

                sub = dict(row)
                target_phone = sub.get("phone_number") or clean
                plan_id = sub.get("plan_id") or "full-bible-365"
                start_str = sub.get("plan_start_date") or today_str
                try:
                    s_date = datetime.strptime(start_str.split("T")[0], "%Y-%m-%d").date()
                except Exception:
                    s_date = today_date
                elapsed = max(0, (today_date - s_date).days)
                target_day = day if day is not None else (elapsed + 1)

                try:
                    completed_list = json.loads(sub.get("completed_days") or "[]")
                    if not isinstance(completed_list, list):
                        completed_list = []
                except Exception:
                    completed_list = []

                already_marked = (sub.get("last_read_date") == today_str)
                last_read = sub.get("last_read_date") or ""
                current_streak = int(sub.get("streak_count") or 0)

                if already_marked:
                    # Already completed a reading today -> keep current streak
                    new_streak = max(1, current_streak)
                elif last_read == yesterday_str:
                    # Read yesterday -> advance streak
                    new_streak = current_streak + 1
                else:
                    # Missed yesterday or new reader -> restart streak at 1
                    new_streak = 1

                if target_day not in completed_list:
                    completed_list.append(target_day)
                    completed_list.sort()

                conn.execute("""
                    UPDATE whatsapp_subscribers
                    SET streak_count = ?, last_read_date = ?, completed_days = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number = ?
                """, (new_streak, today_str, json.dumps(completed_list), target_phone))
                _save_json_backup(conn)

                return {
                    "success": True,
                    "day": target_day,
                    "streak_count": new_streak,
                    "completed_count": len(completed_list),
                    "already_marked": already_marked,
                    "plan_id": plan_id,
                }
        except Exception as exc:
            logger.error("Failed to mark day done for %s: %s", clean, exc)
            return {"success": False, "error": str(exc), "streak_count": 0, "completed_count": 0, "day": 1, "already_marked": False}
        finally:
            conn.close()


def _get_subscriber_streak_sync(phone: str) -> Dict[str, Any]:
    """Retrieves current streak, completed chapters count, and last read date."""
    clean, digits, jid = _phone_variants(phone)
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT phone_number, plan_id, plan_start_date, streak_count, last_read_date, completed_days
                FROM whatsapp_subscribers
                WHERE phone_number IN (?, ?, ?)
            """, (clean, digits, jid))
            row = cursor.fetchone()
            if not row:
                return {"streak_count": 0, "completed_count": 0, "completed_days": [], "last_read_date": "", "plan_id": "full-bible-365"}
            sub = dict(row)
            try:
                c_list = json.loads(sub.get("completed_days") or "[]")
            except Exception:
                c_list = []
            return {
                "streak_count": int(sub.get("streak_count") or 0),
                "completed_count": len(c_list),
                "completed_days": c_list,
                "last_read_date": sub.get("last_read_date") or "",
                "plan_id": sub.get("plan_id") or "full-bible-365",
                "plan_start_date": sub.get("plan_start_date") or "",
            }
        finally:
            conn.close()


def _get_active_subscribers_sync() -> List[Dict[str, Any]]:
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT phone_number, push_name, language, plan_id, reminder_time, plan_start_date,
                       streak_count, last_read_date, completed_days, subscribed_at, updated_at
                FROM whatsapp_subscribers
                WHERE is_active = 1
                ORDER BY subscribed_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()


def _get_subscribers_due_sync(target_time: str) -> List[Dict[str, Any]]:
    """Retrieves all active subscribers whose configured reminder_time matches target_time (HH:MM)."""
    clean_time = target_time.strip()
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT phone_number, push_name, language, plan_id, reminder_time, plan_start_date,
                       streak_count, last_read_date, completed_days, subscribed_at, updated_at
                FROM whatsapp_subscribers
                WHERE is_active = 1 AND reminder_time = ?
                ORDER BY subscribed_at DESC
            """, (clean_time,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()


def _get_subscriber_sync(phone: str) -> Optional[Dict[str, Any]]:
    """Retrieves single subscriber profile if exists."""
    clean, digits, jid = _phone_variants(phone)
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT phone_number, push_name, language, plan_id, reminder_time, plan_start_date,
                       streak_count, last_read_date, completed_days, is_active, subscribed_at, updated_at
                FROM whatsapp_subscribers
                WHERE phone_number IN (?, ?, ?)
            """, (clean, digits, jid))
            row = cursor.fetchone()
            return dict(row) if row else None
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
    clean, digits, jid = _phone_variants(phone)
    with _lock:
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT 1 FROM whatsapp_subscribers WHERE phone_number IN (?, ?, ?) AND is_active = 1", (clean, digits, jid))
            return cursor.fetchone() is not None
        finally:
            conn.close()


# Async non-blocking wrappers adhering to DEV-PY-001
async def add_subscriber(
    phone: str,
    name: str = "",
    language: str = "en",
    plan_id: str = "full-bible-365",
    reminder_time: str = "05:00",
    plan_start_date: Optional[str] = None,
) -> bool:
    return await asyncio.to_thread(_add_subscriber_sync, phone, name, language, plan_id, reminder_time, plan_start_date)


async def update_subscriber_reminder_time(phone: str, reminder_time: str) -> bool:
    return await asyncio.to_thread(_update_subscriber_reminder_time_sync, phone, reminder_time)


async def update_subscriber_plan(phone: str, plan_id: str, plan_start_date: Optional[str] = None) -> bool:
    return await asyncio.to_thread(_update_subscriber_plan_sync, phone, plan_id, plan_start_date)


async def update_subscriber_language(phone: str, language: str) -> bool:
    return await asyncio.to_thread(_update_subscriber_language_sync, phone, language)


async def mark_subscriber_day_done(phone: str, day: Optional[int] = None) -> Dict[str, Any]:
    return await asyncio.to_thread(_mark_subscriber_day_done_sync, phone, day)


async def get_subscriber_streak(phone: str) -> Dict[str, Any]:
    return await asyncio.to_thread(_get_subscriber_streak_sync, phone)


async def get_subscriber(phone: str) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_subscriber_sync, phone)


async def get_subscribers_due(target_time: str) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_subscribers_due_sync, target_time)


async def remove_subscriber(phone: str) -> bool:
    return await asyncio.to_thread(_remove_subscriber_sync, phone)


async def get_active_subscribers() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_active_subscribers_sync)


async def get_subscriber_count() -> int:
    return await asyncio.to_thread(_get_subscriber_count_sync)


async def is_subscribed(phone: str) -> bool:
    return await asyncio.to_thread(_is_subscribed_sync, phone)
