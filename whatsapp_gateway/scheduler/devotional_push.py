"""
Automated Scripture Push & Devotional Scheduler.
Provides background tasks to broadcast daily verses and reading plan checkpoints
to all active subscribers stored in data/whatsapp_subscribers.sqlite.db.
"""

import asyncio
from datetime import datetime
import logging
from typing import Dict, List, Optional

from app.plans_data import READING_PLANS
from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.subscribers import get_active_subscribers

logger = logging.getLogger("whatsapp_gateway.scheduler")


async def push_daily_devotional(
    recipients: Optional[List[str]] = None,
    client: Optional[WAClient] = None,
    plan_id: str = "proverbs-31",
) -> Dict[str, int]:
    """
    Broadcasts today's assigned reading to subscribers.
    If recipients is None, broadcasts to all active subscribers in SQLite database.
    Returns dictionary with counts: {'total': int, 'success': int, 'failed': int}.
    """
    if client is not None:
        wa = client
    else:
        from whatsapp_gateway.routes.webhook import get_client
        wa = get_client()
    day_of_month = datetime.now().day

    plan = READING_PLANS.get(plan_id, {})
    days = plan.get("days", [])
    today_reading = days[day_of_month - 1] if day_of_month <= len(days) else None

    if not today_reading:
        logger.warning("No reading found for day %s in plan %s", day_of_month, plan_id)
        return {"total": 0, "success": 0, "failed": 0}

    targets: List[Dict[str, str]] = []
    if recipients:
        targets = [{"phone_number": r, "language": "en"} for r in recipients]
    else:
        active = await get_active_subscribers()
        targets = [{"phone_number": s["phone_number"], "language": s.get("language", "en")} for s in active]

    if not targets:
        logger.info("No active subscribers found for daily devotional push.")
        return {"total": 0, "success": 0, "failed": 0}

    success_count = 0
    failed_count = 0

    for target in targets:
        phone = target["phone_number"]
        lang = target.get("language", "en")

        if lang == "ta":
            message = (
                f"☀️ *தினசரி வேதாகம தியானம்* ☀️\n\n"
                f"📖 *இன்றைய வாசிப்பு:* {today_reading.get('ref')}\n"
                f"📅 நாள் {day_of_month} ({plan.get('title_ta', 'வாசிப்புத் திட்டம்')})\n\n"
                f"_இன்றைய நாளில் இந்த வார்த்தைகளை தியானித்து ஆசீர்வதிக்கப்படுங்கள்!_\n\n"
                f"_முழு அதிகாரத்தை வாசிக்க 'Proverbs {day_of_month}' என பதிலளிக்கவும்._\n"
                f"_விலக *stop* என அனுப்பவும்._"
            )
        else:
            message = (
                f"☀️ *Daily Scripture Devotional* ☀️\n\n"
                f"📖 *Today's Reading:* {today_reading.get('ref')}\n"
                f"📅 Day {day_of_month} of {plan.get('title_en', 'Reading Plan')}\n\n"
                f"_Take a quiet moment today to reflect on this passage. Have a blessed day!_\n\n"
                f"_Reply 'Proverbs {day_of_month}' to read the chapter right here!_\n"
                f"_Reply *stop* anytime to unsubscribe._"
            )

        try:
            res = await wa.send_text(to=phone, text=message)
            if res.success:
                success_count += 1
            else:
                failed_count += 1
        except Exception as exc:
            logger.error("Failed to push daily devotional to %s: %s", phone, exc)
            failed_count += 1

    return {"total": len(targets), "success": success_count, "failed": failed_count}
