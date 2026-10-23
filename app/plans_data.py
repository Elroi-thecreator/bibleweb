"""
Holy Bible Reading Plans Data Repository.
Provides complete, canonical reading schedules:
1. Full Bible in 365 Days (1,189 chapters, ~3.2 ch/day covering OT & NT)
2. New Testament in 90 Days (260 chapters, ~2.9 ch/day)
3. Proverbs in 31 Days (1 chapter/day)
4. Psalms for Peace & Comfort (30 Days)
5. Deuterocanonical Books in 30 Days (137 chapters, ~4.5 ch/day)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.db import BIBLE_BOOKS, DEUTEROCANONICAL_BOOKS


def _generate_sequential_plan(books_list: list, total_days: int) -> List[Dict[str, Any]]:
    """Divides all chapters in the provided books list across total_days evenly."""
    all_chs = []
    for b in books_list:
        b_id, name_en, name_ta, total_ch = b[0], b[1], b[2], b[3]
        for c in range(1, total_ch + 1):
            all_chs.append({
                "book_id": b_id,
                "name_en": name_en,
                "name_ta": name_ta,
                "chapter": c,
            })

    total = len(all_chs)
    days = []
    for d in range(1, total_days + 1):
        start = (d - 1) * total // total_days
        end = d * total // total_days
        sub = all_chs[start:end]
        first = sub[0]
        last = sub[-1]
        if first["book_id"] == last["book_id"]:
            if first["chapter"] == last["chapter"]:
                ref_en = f"{first['name_en']} {first['chapter']}"
                ref_ta = f"{first['name_ta']} {first['chapter']}"
            else:
                ref_en = f"{first['name_en']} {first['chapter']}-{last['chapter']}"
                ref_ta = f"{first['name_ta']} {first['chapter']}-{last['chapter']}"
        else:
            ref_en = f"{first['name_en']} {first['chapter']} - {last['name_en']} {last['chapter']}"
            ref_ta = f"{first['name_ta']} {first['chapter']} - {last['name_ta']} {last['chapter']}"

        days.append({
            "day": d,
            "book_id": first["book_id"],
            "chapter": first["chapter"],
            "ref": f"{ref_en} / {ref_ta}",
            "ref_en": ref_en,
            "ref_ta": ref_ta,
            "chapter_count": len(sub),
        })
    return days


# 1. Whole Bible in 365 Days (All 66 Canonical Books, 1,189 Chapters)
_FULL_BIBLE_DAYS = _generate_sequential_plan(BIBLE_BOOKS, 365)

# 2. New Testament in 90 Days (Books 40-66, 260 Chapters)
_NT_BOOKS = [b for b in BIBLE_BOOKS if b[0] >= 40]
_NT_90_DAYS = _generate_sequential_plan(_NT_BOOKS, 90)

# 3. Deuterocanonical Books in 30 Days (7 Books, 137 Chapters)
_DEUTEROCANON_30_DAYS = _generate_sequential_plan(DEUTEROCANONICAL_BOOKS, 30)

# 4. Curated Psalms of Peace & Comfort (30 Days)
_PSALM_NUMBERS = [
    1, 23, 27, 34, 46, 51, 63, 91, 103, 116,
    121, 127, 139, 145, 150, 8, 16, 18, 19, 25,
    30, 31, 32, 40, 42, 62, 84, 100, 118, 138,
]
_PSALMS_30_DAYS = [
    {
        "day": i + 1,
        "book_id": 19,
        "chapter": p,
        "ref": f"Psalm {p} / சங்கீதம் {p}",
        "ref_en": f"Psalm {p}",
        "ref_ta": f"சங்கீதம் {p}",
        "chapter_count": 1,
    }
    for i, p in enumerate(_PSALM_NUMBERS)
]

# 5. Proverbs in 31 Days (Book 20, 31 Chapters)
_PROVERBS_31_DAYS = [
    {
        "day": d,
        "book_id": 20,
        "chapter": d,
        "ref": f"Proverbs {d} / நீதிமொழிகள் {d}",
        "ref_en": f"Proverbs {d}",
        "ref_ta": f"நீதிமொழிகள் {d}",
        "chapter_count": 1,
    }
    for d in range(1, 32)
]


READING_PLANS: Dict[str, Dict[str, Any]] = {
    "full-bible-365": {
        "id": "full-bible-365",
        "title_en": "Full Bible in 365 Days",
        "title_ta": "365 நாட்களில் முழு வேதாகமம்",
        "tagline": "Entire Bible from Genesis to Revelation • ~3.2 Chapters a day",
        "total_days": 365,
        "badge": "Canonical",
        "days": _FULL_BIBLE_DAYS,
    },
    "one-year-bible": {
        "id": "one-year-bible",
        "title_en": "One Year Bible Plan",
        "title_ta": "ஒரு வருட வேதாகம வாசிப்பு",
        "tagline": "Entire Bible from Genesis to Revelation • 365 Days",
        "total_days": 365,
        "badge": "Canonical",
        "days": _FULL_BIBLE_DAYS,
    },
    "nt-90": {
        "id": "nt-90",
        "title_en": "New Testament in 90 Days",
        "title_ta": "90 நாட்களில் புதிய ஏற்பாடு",
        "tagline": "Gospels, Acts & Epistles • ~2.9 Chapters a day",
        "total_days": 90,
        "badge": "Canonical",
        "days": _NT_90_DAYS,
    },
    "proverbs-31": {
        "id": "proverbs-31",
        "title_en": "Proverbs in 31 Days",
        "title_ta": "31 நாட்களில் நீதிமொழிகள்",
        "tagline": "Wisdom for daily living • 1 Chapter a day",
        "total_days": 31,
        "badge": "Wisdom",
        "days": _PROVERBS_31_DAYS,
    },
    "psalms-comfort": {
        "id": "psalms-comfort",
        "title_en": "Psalms for Peace & Comfort",
        "title_ta": "தேறுதலின் சங்கீதங்கள்",
        "tagline": "Selected Psalms for prayer and reflection • 30 Days",
        "total_days": 30,
        "badge": "Devotional",
        "days": _PSALMS_30_DAYS,
    },
    "deuterocanon-30": {
        "id": "deuterocanon-30",
        "title_en": "Deuterocanonical Books in 30 Days",
        "title_ta": "இரண்டாம் திருமுறை 30 நாட்களில்",
        "tagline": "Tobit, Judith, Wisdom, Sirach, Baruch & Maccabees • ~4.5 Chapters a day",
        "total_days": 30,
        "badge": "Catholic",
        "days": _DEUTEROCANON_30_DAYS,
    },
}


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a reading plan by canonical id or common alias."""
    if not plan_id:
        return READING_PLANS.get("full-bible-365")
    clean = plan_id.strip().lower()
    alias_map = {
        "full": "full-bible-365",
        "whole": "full-bible-365",
        "year": "full-bible-365",
        "bible": "full-bible-365",
        "365": "full-bible-365",
        "full-bible": "full-bible-365",
        "nt": "nt-90",
        "new-testament": "nt-90",
        "proverbs": "proverbs-31",
        "psalms": "psalms-comfort",
        "deuterocanon": "deuterocanon-30",
        "dc": "deuterocanon-30",
        "catholic": "deuterocanon-30",
    }
    resolved_id = alias_map.get(clean, clean)
    return READING_PLANS.get(resolved_id)


def get_today_plan_reading(plan_id: str = "full-bible-365", day_number: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Returns the reading item for the specified plan and day (or today's calculated day)."""
    plan = get_plan(plan_id)
    if not plan:
        plan = READING_PLANS["full-bible-365"]

    days = plan.get("days", [])
    total_days = plan.get("total_days", len(days))
    if not days:
        return None

    if day_number is not None:
        calc_day = max(1, min(day_number, total_days))
    else:
        now = datetime.now()
        if total_days == 365:
            calc_day = ((now.timetuple().tm_yday - 1) % 365) + 1
        elif total_days == 90:
            calc_day = ((now.timetuple().tm_yday - 1) % 90) + 1
        elif total_days == 31:
            calc_day = min(now.day, 31)
        elif total_days == 30:
            calc_day = min(now.day, 30)
        else:
            calc_day = ((now.timetuple().tm_yday - 1) % total_days) + 1

    idx = max(0, min(calc_day - 1, len(days) - 1))
    reading = dict(days[idx])
    reading["current_day"] = calc_day
    reading["total_days"] = total_days
    reading["plan_title_en"] = plan.get("title_en")
    reading["plan_title_ta"] = plan.get("title_ta")
    return reading
