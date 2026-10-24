"""
Ephemeral Sync Code Store for Web Bible and WhatsApp Account Linking.
Provides time-limited (15-minute) one-time magic linking codes to synchronize
reading progress, streaks, and preferences between WhatsApp and the Web App.
"""

from datetime import datetime, timedelta
import random
import string
import threading
from typing import Any, Dict, Optional

_lock = threading.Lock()
_SYNC_CODES: Dict[str, Dict[str, Any]] = {}


def generate_sync_code(phone: str, ttl_minutes: int = 15) -> str:
    """
    Generates an ephemeral 6-digit sync code for a subscriber.
    Format: 'BIBLE-XXXX' (e.g. 'BIBLE-7492')
    """
    clean_phone = phone.split("@")[0].replace("+", "").replace(" ", "").replace("-", "").strip()
    digits = "".join(random.choices(string.digits, k=4))
    code = f"BIBLE-{digits}"

    with _lock:
        now = datetime.now()
        _SYNC_CODES[code.upper()] = {
            "phone_number": clean_phone,
            "created_at": now,
            "expires_at": now + timedelta(minutes=ttl_minutes),
        }
        # Also map raw digits without prefix for flexible mobile input
        _SYNC_CODES[digits] = _SYNC_CODES[code.upper()]

    return code


def verify_sync_code(code: str) -> Optional[str]:
    """
    Validates a sync code and returns the associated phone_number.
    One-time use: invalidates the code upon successful verification.
    """
    clean_code = code.strip().upper()
    with _lock:
        entry = _SYNC_CODES.get(clean_code)
        if not entry:
            return None

        if datetime.now() > entry["expires_at"]:
            del _SYNC_CODES[clean_code]
            return None

        phone = entry["phone_number"]
        # Remove used code and any alias
        keys_to_delete = [k for k, v in _SYNC_CODES.items() if v.get("phone_number") == phone]
        for k in keys_to_delete:
            _SYNC_CODES.pop(k, None)

        return phone
