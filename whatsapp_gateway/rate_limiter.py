"""
Thread-safe Tiered Rate Limiter and Quota Manager for WhatsApp Bot.
Provides:
1. Sliding Window Rate Limiting (per rolling 60-second window).
2. Daily Heavy Operation Quotas (dedicated daily counter for Edge-TTS audio requests).
3. Whitelist / Admin Bypass support.
4. User-friendly bilingual cooldown & quota exhaustion notices.
"""

from collections import defaultdict
from datetime import datetime
import logging
import math
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from whatsapp_gateway.config import config

logger = logging.getLogger("whatsapp_gateway.rate_limiter")


def normalize_phone_number(raw_jid_or_phone: str) -> str:
    """Extracts clean digits-only phone number or normalized identifier."""
    if not raw_jid_or_phone:
        return ""
    clean = raw_jid_or_phone.strip()
    # Strip WhatsApp JID suffix if present
    if "@" in clean:
        clean = clean.split("@")[0]
    # Keep only digits
    digits = re.sub(r"\D", "", clean)
    return digits if digits else clean.lower()


class WhatsAppRateLimiter:
    """
    Tiered Rate Limiter:
    - Sliding window requests-per-minute per user.
    - Daily audio request limits per user (Edge-TTS / FFmpeg protection).
    - Whitelist bypassing.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # sender -> list of Unix timestamps
        self._requests: Dict[str, List[float]] = defaultdict(list)
        # sender -> {"date": "YYYY-MM-DD", "count": int}
        self._audio_quotas: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Telemetry metrics
        self.total_checked = 0
        self.total_throttled = 0
        self.total_audio_blocks = 0
        self.today_audio_requests = 0
        self._today_date = datetime.now().strftime("%Y-%m-%d")

    def is_whitelisted(self, sender: str) -> bool:
        """Checks if the sender is whitelisted from rate limits."""
        if not sender:
            return False
        clean_num = normalize_phone_number(sender)
        raw_sender = sender.strip().lower()

        for w in config.rate_limit_whitelist:
            w_str = str(w).strip().lower()
            if not w_str:
                continue
            if w_str == raw_sender:
                return True
            w_num = normalize_phone_number(w_str)
            if w_num and (w_num == clean_num or clean_num.endswith(w_num) or w_num.endswith(clean_num)):
                return True

        return False

    def check_request_allowed(self, sender: str) -> Tuple[bool, int, str]:
        """
        Validates whether sender is permitted to make a request under sliding window limit.
        Returns: (allowed: bool, cooldown_seconds: int, reason: str)
        """
        if not config.rate_limit_enabled:
            return True, 0, ""

        if self.is_whitelisted(sender):
            return True, 0, ""

        phone_key = normalize_phone_number(sender)
        now = time.time()
        window_seconds = 60.0
        max_rpm = config.rate_limit_requests_per_minute

        with self._lock:
            self.total_checked += 1
            timestamps = self._requests[phone_key]

            # Drop timestamps older than 60 seconds
            cutoff = now - window_seconds
            valid_timestamps = [t for t in timestamps if t > cutoff]
            self._requests[phone_key] = valid_timestamps

            if len(valid_timestamps) >= max_rpm:
                self.total_throttled += 1
                # Cooldown is time until earliest request expires from window
                earliest = valid_timestamps[0]
                remaining = max(1, math.ceil(earliest + window_seconds - now))
                logger.warning(
                    "[RateLimiter] Throttled sender %s (used %d/%d reqs). Cooldown: %ds",
                    sender, len(valid_timestamps), max_rpm, remaining,
                )
                return False, remaining, "rate_limit_exceeded"

            # Record current request timestamp
            self._requests[phone_key].append(now)
            return True, 0, ""

    def check_audio_quota_allowed(self, sender: str) -> Tuple[bool, int, int]:
        """
        Validates daily audio synthesis quota for high-cost TTS/FFmpeg requests.
        Returns: (allowed: bool, current_usage: int, max_limit: int)
        """
        max_audio = config.rate_limit_audio_per_day

        if not config.rate_limit_enabled:
            return True, 0, max_audio

        if self.is_whitelisted(sender):
            return True, 0, max_audio

        phone_key = normalize_phone_number(sender)
        today = datetime.now().strftime("%Y-%m-%d")

        with self._lock:
            # Check calendar day reset for global audio telemetry
            if today != self._today_date:
                self._today_date = today
                self.today_audio_requests = 0

            quota_entry = self._audio_quotas[phone_key]
            entry_date = quota_entry.get("date")
            entry_count = quota_entry.get("count", 0)

            if entry_date != today:
                entry_date = today
                entry_count = 0

            if entry_count >= max_audio:
                self.total_audio_blocks += 1
                logger.warning(
                    "[RateLimiter] Audio quota exceeded for sender %s (%d/%d audio requests today)",
                    sender, entry_count, max_audio,
                )
                return False, entry_count, max_audio

            # Allow and increment
            entry_count += 1
            self._audio_quotas[phone_key] = {"date": today, "count": entry_count}
            self.today_audio_requests += 1
            return True, entry_count, max_audio

    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic and performance telemetry for the admin dashboard."""
        now = time.time()
        with self._lock:
            # Count active users in sliding window
            cutoff = now - 60.0
            active_count = sum(1 for ts_list in self._requests.values() if any(t > cutoff for t in ts_list))

            return {
                "enabled": config.rate_limit_enabled,
                "requests_per_minute": config.rate_limit_requests_per_minute,
                "daily_audio_limit": config.rate_limit_audio_per_day,
                "cooldown_seconds": config.rate_limit_cooldown_seconds,
                "whitelist": config.rate_limit_whitelist,
                "active_window_users": active_count,
                "total_requests_evaluated": self.total_checked,
                "total_throttled_requests": self.total_throttled,
                "total_audio_quota_blocks": self.total_audio_blocks,
                "today_audio_requests": self.today_audio_requests,
            }

    def reset_user(self, sender: str) -> None:
        """Clears all rate limit & audio quota tracking for a single user."""
        phone_key = normalize_phone_number(sender)
        with self._lock:
            self._requests.pop(phone_key, None)
            self._audio_quotas.pop(phone_key, None)

    def clear_all(self) -> None:
        """Resets all active tracking and metrics."""
        with self._lock:
            self._requests.clear()
            self._audio_quotas.clear()
            self.total_checked = 0
            self.total_throttled = 0
            self.total_audio_blocks = 0
            self.today_audio_requests = 0

    # Aliases and helper methods
    def check_rate_limit(self, sender: str) -> Tuple[bool, int, str]:
        """Convenience alias for check_request_allowed."""
        return self.check_request_allowed(sender)

    def check_audio_quota(self, sender: str) -> Tuple[bool, int, int]:
        """Convenience alias for check_audio_quota_allowed."""
        return self.check_audio_quota_allowed(sender)

    @staticmethod
    def build_cooldown_message(cooldown_seconds: int, is_tamil: bool = False) -> str:
        """Builds user-friendly rate limit warning message."""
        return build_cooldown_message(cooldown_seconds, is_tamil)

    @staticmethod
    def build_audio_quota_message(max_limit: int, is_tamil: bool = False) -> str:
        """Builds user-friendly daily audio limit notice."""
        return build_audio_quota_message(max_limit, is_tamil)


# Friendly Conversational Response Builders
def build_cooldown_message(cooldown_seconds: int, is_tamil: bool = False) -> str:
    """Builds user-friendly rate limit warning message."""
    if is_tamil:
        return (
            f"⏳ *அதிக கோரிக்கைகள் (Rate Limit)!*\n\n"
            f"குறுகிய நேரத்தில் அதிக செய்திகளை அனுப்பியுள்ளீர்கள். "
            f"தயவுசெய்து *{cooldown_seconds} வினாடிகள்* காத்திருந்து மீண்டும் அனுப்பவும்."
        )
    return (
        f"⏳ *Too Many Requests!* ⏳\n\n"
        f"You have sent too many requests in a short time. "
        f"Please wait *{cooldown_seconds} seconds* before sending another message."
    )


def build_audio_quota_message(max_limit: int, is_tamil: bool = False) -> str:
    """Builds user-friendly daily audio limit notice."""
    if is_tamil:
        return (
            f"⚠️ *தினசரி ஆடியோ வரம்பு முடிந்தது!* 🎧\n\n"
            f"இன்றைய தினத்திற்கான உங்கள் {max_limit} ஆடியோ பதிவுகளின் வரம்பு முடிவடைந்தது. "
            f"நள்ளிரவு 12:00 மணிக்கு இது மீண்டும் புதுப்பிக்கப்படும்.\n\n"
            f"_வேத வசனங்களை உடனடியாக வாசிக்க அதிகாரத்தின் பெயரை அனுப்பவும் (எ.கா. 'யோவான் 1')._"
        )
    return (
        f"⚠️ *Daily Audio Limit Reached!* 🎧\n\n"
        f"You have reached your daily quota of *{max_limit} audio voice notes*. "
        f"Your audio quota will reset at midnight.\n\n"
        f"_You can still read any chapter text right now by sending its reference (e.g. 'John 1')!_"
    )


# Global singleton instance
rate_limiter = WhatsAppRateLimiter()


def get_rate_limiter() -> WhatsAppRateLimiter:
    """Returns global WhatsApp rate limiter singleton."""
    return rate_limiter

