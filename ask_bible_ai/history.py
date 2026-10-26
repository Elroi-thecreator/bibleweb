"""
Ask Bible AI Persistent Chat History Store.
Provides thread-safe, embedded SQLite persistence for conversational sessions and messages.
Completely decoupled with zero dependencies on application-specific databases.
Can be used standalone in any Python or FastAPI project.
"""

import asyncio
from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any, Dict, List, Optional
import uuid

# Cross-platform root directory resolution
if getattr(sys, "frozen", False):
    ROOT_DIR = Path(getattr(sys, "_MEIPASS", sys.executable)).resolve()
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent

DEFAULT_HISTORY_DB_PATH = ROOT_DIR / "data" / "bible_ai_history.sqlite.db"


class ChatHistoryStore:
    """Thread-safe SQLite storage for Ask Bible AI conversation sessions and messages."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_HISTORY_DB_PATH
        self._initialized = False

    @contextmanager
    def _get_connection(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        if self._initialized:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    citations TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id ASC);")
            conn.commit()
            self._initialized = True

    # -------------------------------------------------------------
    # Sync Worker Implementations (wrapped in asyncio.to_thread)
    # -------------------------------------------------------------

    def _sync_create_session(self, title: Optional[str] = None, session_id: Optional[str] = None) -> str:
        self._ensure_schema()
        sid = session_id or str(uuid.uuid4())
        clean_title = (title or "New Scripture Inquiry")[:80]
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (sid, clean_title, now, now),
            )
            conn.commit()
        return sid

    def _sync_get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_schema()
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if not row:
                return None
            return dict(row)

    def _sync_list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        self._ensure_schema()
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT s.id, s.title, s.created_at, s.updated_at,
                       COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def _sync_add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[str]] = None,
    ) -> int:
        self._ensure_schema()
        # Verify or auto-create session
        sess = self._sync_get_session(session_id)
        if not sess:
            # Derive title from content
            title = content.strip().split("\n")[0][:60]
            self._sync_create_session(title=title, session_id=session_id)
        elif sess["title"] == "New Scripture Inquiry" and role == "user":
            # Auto-title session with the first question
            clean_title = content.strip().split("\n")[0][:60]
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE sessions SET title = ? WHERE id = ?",
                    (clean_title, session_id),
                )
                conn.commit()

        now = datetime.utcnow().isoformat()
        citations_json = json.dumps(citations or [], ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, citations, created_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, citations_json, now),
            )
            msg_id = cursor.lastrowid
            # Update session timestamp
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id),
            )
            conn.commit()
            return msg_id

    def _sync_get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        self._ensure_schema()
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT id, role, content, citations, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
            """, (session_id, limit)).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                try:
                    d["citations"] = json.loads(d.get("citations") or "[]")
                except Exception:
                    d["citations"] = []
                results.append(d)
            return results

    def _sync_delete_session(self, session_id: str) -> bool:
        self._ensure_schema()
        with self._get_connection() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _sync_clear_all(self) -> bool:
        self._ensure_schema()
        with self._get_connection() as conn:
            conn.execute("DELETE FROM messages;")
            conn.execute("DELETE FROM sessions;")
            conn.commit()
            return True

    # -------------------------------------------------------------
    # Async Public API (DEV-PY-001 compliant non-blocking)
    # -------------------------------------------------------------

    async def create_session(self, title: Optional[str] = None, session_id: Optional[str] = None) -> str:
        return await asyncio.to_thread(self._sync_create_session, title, session_id)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_get_session, session_id)

    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_list_sessions, limit)

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[str]] = None,
    ) -> int:
        return await asyncio.to_thread(self._sync_add_message, session_id, role, content, citations)

    async def get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_get_messages, session_id, limit)

    async def delete_session(self, session_id: str) -> bool:
        return await asyncio.to_thread(self._sync_delete_session, session_id)

    async def clear_all(self) -> bool:
        return await asyncio.to_thread(self._sync_clear_all)


# Global singleton instance
history_store = ChatHistoryStore()
