"""
Conversational Session Store for multi-turn dialogues (e.g. Quizzes, Checkouts, Surveys).
Provides an abstract base interface and a robust in-memory implementation with TTL expiration.
"""

from abc import ABC, abstractmethod
import time
import threading
from typing import Any, Dict, Optional

from whatsapp_gateway.config import config


class BaseSessionStore(ABC):
    """Abstract interface for session storage."""

    @abstractmethod
    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user session if active and not expired."""
        pass

    @abstractmethod
    async def set_session(
        self,
        user_id: str,
        state: str,
        data: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Store or update user conversational state."""
        pass

    @abstractmethod
    async def clear_session(self, user_id: str) -> None:
        """Clear user conversation state."""
        pass


class InMemorySessionStore(BaseSessionStore):
    """
    Thread-safe in-memory session store with automatic TTL eviction.
    Suitable for single-instance FastAPI deployments without requiring Redis.
    """

    def __init__(self, default_ttl: Optional[int] = None):
        self._default_ttl = default_ttl or config.session_ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._store.get(user_id)
            if not record:
                return None
            now = time.time()
            if now > record["expires_at"]:
                del self._store[user_id]
                return None
            return {
                "state": record["state"],
                "data": record["data"],
                "updated_at": record["updated_at"],
            }

    async def set_session(
        self,
        user_id: str,
        state: str,
        data: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        now = time.time()
        with self._lock:
            self._store[user_id] = {
                "state": state,
                "data": data or {},
                "updated_at": now,
                "expires_at": now + ttl,
            }

    async def clear_session(self, user_id: str) -> None:
        with self._lock:
            self._store.pop(user_id, None)

    def cleanup_expired(self) -> int:
        """Manually purge expired keys. Returns count of purged keys."""
        now = time.time()
        purged = 0
        with self._lock:
            expired_keys = [k for k, v in self._store.items() if now > v["expires_at"]]
            for k in expired_keys:
                del self._store[k]
                purged += 1
        return purged
