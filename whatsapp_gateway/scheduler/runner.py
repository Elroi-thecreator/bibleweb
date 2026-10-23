"""
Background Periodic Task Runner for WhatsApp Scheduled Devotionals & Reminders.
Checks active subscriber reminder times every 30 seconds and triggers dispatches.
"""

import asyncio
from datetime import datetime
import logging
from typing import Optional

from whatsapp_gateway.scheduler.devotional_push import push_daily_devotional

logger = logging.getLogger("whatsapp_gateway.scheduler.runner")


class DevotionalScheduler:
    """Lightweight background loop checking for due devotional dispatches."""

    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval_seconds = check_interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_dispatched_minute: Optional[str] = None

    @property
    def is_running(self) -> bool:
        return self._running and self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.is_running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="whatsapp_devotional_scheduler")
        logger.info("[DevotionalScheduler] Background task started (default reminder time: 05:00 AM).")

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[DevotionalScheduler] Background task stopped.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                now_str = datetime.now().strftime("%H:%M")
                if now_str != self._last_dispatched_minute:
                    # Check if any subscribers are due for this minute
                    from whatsapp_gateway.subscribers import get_subscribers_due
                    due = await get_subscribers_due(now_str)
                    if due:
                        logger.info("[DevotionalScheduler] Dispatching devotionals for minute %s to %d subscribers", now_str, len(due))
                        await push_daily_devotional(target_time=now_str)
                    self._last_dispatched_minute = now_str
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("[DevotionalScheduler] Error during schedule check: %s", exc)

            try:
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break


# Global singleton scheduler
devotional_scheduler = DevotionalScheduler()
