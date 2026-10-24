"""
Automated Scripture Push & Devotional Scheduler.
Provides background tasks to broadcast daily verses and reading plan checkpoints
to all active subscribers stored in data/whatsapp_subscribers.sqlite.db.
Supports filtering by configured reminder time (default: 5:00 AM / '05:00') and reading plans.
"""

import asyncio
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from app.db import BOOK_MAP, CATHOLIC_BOOK_MAP
from app.plans_data import READING_PLANS, get_plan, get_today_plan_reading
from whatsapp_gateway.client.client import WAClient
from whatsapp_gateway.subscribers import get_active_subscribers, get_subscribers_due

logger = logging.getLogger("whatsapp_gateway.scheduler")


async def push_daily_devotional(
    recipients: Optional[List[str]] = None,
    client: Optional[WAClient] = None,
    plan_id: Optional[str] = None,
    target_time: Optional[str] = None,
) -> Dict[str, int]:
    """
    Broadcasts assigned reading checkpoints to subscribers.
    - If recipients is provided, broadcasts directly to those numbers.
    - If target_time is provided (e.g. '05:00'), broadcasts to active subscribers due at that time.
    - If neither is provided, broadcasts to all active subscribers.
    - If plan_id is provided, overrides subscriber plan choice; otherwise uses each subscriber's selected plan.
    """
    if client is not None:
        wa = client
    else:
        from whatsapp_gateway.routes.webhook import get_client
        wa = get_client()

    targets: List[Dict[str, Any]] = []
    if recipients:
        targets = [
            {
                "phone_number": r,
                "language": "en",
                "plan_id": plan_id or "full-bible-365",
                "plan_start_date": datetime.now().strftime("%Y-%m-%d"),
            }
            for r in recipients
        ]
    elif target_time:
        targets = await get_subscribers_due(target_time)
    else:
        targets = await get_active_subscribers()

    if not targets:
        logger.info("No active subscribers due for devotional push (target_time=%s).", target_time)
        return {"total": 0, "success": 0, "failed": 0, "delivered": 0}

    success_count = 0
    failed_count = 0

    for target in targets:
        phone = target["phone_number"]
        lang = target.get("language", "en")
        sub_plan = plan_id or target.get("plan_id") or "full-bible-365"
        sub_start = target.get("plan_start_date")
        reading = get_today_plan_reading(sub_plan, start_date=sub_start)

        if not reading:
            reading = get_today_plan_reading("full-bible-365", start_date=sub_start)

        curr_day = reading.get("current_day", 1)
        total_days = reading.get("total_days", 365)
        ref_text = reading.get("ref_ta" if lang == "ta" else "ref_en") or reading.get("ref")
        plan_title = reading.get("plan_title_ta" if lang == "ta" else "plan_title_en", "Holy Bible Reading Plan")

        b_id = reading.get("book_id", 1)
        ch_num = reading.get("chapter", 1)
        b_meta = CATHOLIC_BOOK_MAP.get(b_id, BOOK_MAP.get(b_id, {"name_en": "Genesis", "name_ta": "ஆதியாகமம்"}))
        book_name = b_meta.get("name_ta" if lang == "ta" else "name_en", "Genesis")

        if lang == "both":
            ref_ta = reading.get("ref_ta") or reading.get("ref", "")
            ref_en = reading.get("ref_en") or reading.get("ref", "")
            plan_ta = reading.get("plan_title_ta", "வேதாகம வாசிப்பு")
            plan_en = reading.get("plan_title_en", "Bible Plan")
            b_ta = b_meta.get("name_ta", "Genesis")
            b_en = b_meta.get("name_en", "Genesis")
            message = (
                f"☀️ *Daily Scripture Devotional • தினசரி தியானம்* ☀️\n\n"
                f"🇮🇳 📖 *இன்றைய வாசிப்பு:* {ref_ta}\n"
                f"🇬🇧 📖 *Today's Portion:* {ref_en}\n"
                f"📅 *Day {curr_day} of {total_days}* • _{plan_en} / {plan_ta}_\n\n"
                f"✨ _Meditate on God's Word today! • இறைவார்த்தையை தியானியுங்கள்!_\n\n"
                f"• Read chapter: reply *{b_en} {ch_num}* or *{b_ta} {ch_num}*\n"
                f"• Audio voice note: reply *audio {b_en} {ch_num}*\n"
                f"• Mark completed: reply *done*\n"
                f"• Change reminder: reply *remind <time>*\n"
                f"• Unsubscribe: reply *stop*"
            )
        elif lang == "ta":
            message = (
                f"☀️ *தினசரி வேதாகம தியானம் & வாசிப்பு* ☀️\n\n"
                f"📖 *இன்றைய வாசிப்பு:* {ref_text}\n"
                f"📅 *நாள் {curr_day} / {total_days}* • _{plan_title}_\n\n"
                f"✨ _இன்றைய நாளில் இறைவார்த்தையை தியானித்து ஆசீர்வதிக்கப்படுங்கள்!_\n\n"
                f"• முழு அதிகாரத்தை வாசிக்க *{book_name} {ch_num}* என அனுப்பவும்.\n"
                f"• ஆடியோ கேட்க *audio {book_name} {ch_num}* என அனுப்பவும்.\n"
                f"• பகுதியை முடித்த பின் குறிக்க *done* என அனுப்பவும்.\n"
                f"• நினைவூட்டல் நேரத்தை மாற்ற *remind <நேரம்>* (எ.கா. `remind 5 AM`) என அனுப்பவும்.\n"
                f"• விலக *stop* என அனுப்பவும்."
            )
        else:
            message = (
                f"☀️ *Daily Scripture Devotional & Reading* ☀️\n\n"
                f"📖 *Today's Reading:* {ref_text}\n"
                f"📅 *Day {curr_day} of {total_days}* • _{plan_title}_\n\n"
                f"✨ _Take a quiet moment today to reflect on this passage. Have a blessed day!_\n\n"
                f"• Reply *{book_name} {ch_num}* to read full chapter.\n"
                f"• Reply *audio {book_name} {ch_num}* for instant audio voice note.\n"
                f"• Mark reading completed: reply *done*\n"
                f"• Change reminder time: reply *remind <time>* (e.g. `remind 5 AM`).\n"
                f"• Reply *stop* anytime to unsubscribe."
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

    return {
        "total": len(targets),
        "success": success_count,
        "failed": failed_count,
        "delivered": success_count,
    }
