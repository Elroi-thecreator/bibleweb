"""
Holy Bible Domain Adapter for WhatsApp Gateway.
Bridges the decoupled WhatsApp bot engine to scripture databases,
audio text-to-speech, bilingual quiz banks, hymnal lyrics, and reading plans.
Includes automatic Tamil/English language intelligence and subscriber persistence.
"""

import asyncio
from datetime import datetime
import io
import logging
import random
import re
from typing import Dict, List, Optional, Tuple

from app.db import (
    BOOK_MAP,
    CATHOLIC_BOOK_MAP,
    get_chapter_verses,
    get_song_by_id,
    get_songs_list,
    search_verses,
)
from app.plans_data import READING_PLANS, get_plan, get_today_plan_reading
from app.quiz_data import QUIZ_QUESTIONS
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher
from whatsapp_gateway.subscribers import (
    add_subscriber,
    remove_subscriber,
    is_subscribed,
    update_subscriber_reminder_time,
    update_subscriber_plan,
    update_subscriber_language,
    mark_subscriber_day_done,
    get_subscriber_streak,
    get_subscriber,
)
from whatsapp_gateway.adapters.card_generator import generate_verse_card
from whatsapp_gateway.sync_store import generate_sync_code
from whatsapp_gateway.rate_limiter import (
    rate_limiter,
    build_cooldown_message,
    build_audio_quota_message,
)

logger = logging.getLogger("whatsapp_gateway.bible_adapter")


def is_tamil_text(text: str) -> bool:
    """Checks whether the text contains Tamil Unicode block characters."""
    return bool(re.search(r"[\u0B80-\u0BFF]", text))


# Common abbreviations mapping to English canonical book names
BOOK_ABBREVIATIONS = {
    # Old Testament
    "gen": "Genesis", "ge": "Genesis", "gn": "Genesis",
    "exo": "Exodus", "ex": "Exodus", "exod": "Exodus",
    "lev": "Leviticus", "le": "Leviticus", "lv": "Leviticus",
    "num": "Numbers", "nu": "Numbers", "nm": "Numbers",
    "deu": "Deuteronomy", "dt": "Deuteronomy", "deut": "Deuteronomy",
    "jos": "Joshua", "josh": "Joshua",
    "jdg": "Judges", "judg": "Judges",
    "rut": "Ruth", "ru": "Ruth",
    "1sa": "1 Samuel", "1sam": "1 Samuel", "1 sam": "1 Samuel",
    "2sa": "2 Samuel", "2sam": "2 Samuel", "2 sam": "2 Samuel",
    "1ki": "1 Kings", "1kgs": "1 Kings", "1 kgs": "1 Kings",
    "2ki": "2 Kings", "2kgs": "2 Kings", "2 kgs": "2 Kings",
    "1ch": "1 Chronicles", "1chron": "1 Chronicles", "1 chr": "1 Chronicles",
    "2ch": "2 Chronicles", "2chron": "2 Chronicles", "2 chr": "2 Chronicles",
    "ezr": "Ezra",
    "neh": "Nehemiah",
    "est": "Esther",
    "job": "Job",
    "ps": "Psalm", "psa": "Psalm", "psalm": "Psalm", "psalms": "Psalm",
    "pro": "Proverbs", "prov": "Proverbs", "prv": "Proverbs",
    "ecc": "Ecclesiastes", "eccl": "Ecclesiastes",
    "sng": "Song of Solomon", "song": "Song of Solomon", "sos": "Song of Solomon",
    "isa": "Isaiah", "is": "Isaiah",
    "jer": "Jeremiah", "jr": "Jeremiah",
    "lam": "Lamentations",
    "ezk": "Ezekiel", "ezek": "Ezekiel",
    "dan": "Daniel", "dn": "Daniel",
    "hos": "Hosea",
    "jol": "Joel",
    "amo": "Amos",
    "oba": "Obadiah",
    "jon": "Jonah",
    "mic": "Micah",
    "nam": "Nahum",
    "hab": "Habakkuk",
    "zep": "Zephaniah",
    "hag": "Haggai",
    "zec": "Zechariah",
    "mal": "Malachi",
    # Deuterocanonical / Catholic
    "tob": "Tobit", "tobit": "Tobit",
    "jdt": "Judith", "judith": "Judith",
    "wis": "Wisdom of Solomon", "wisdom": "Wisdom of Solomon",
    "sir": "Sirach", "ecclesiasticus": "Sirach",
    "bar": "Baruch", "baruch": "Baruch",
    "1ma": "1 Maccabees", "1mac": "1 Maccabees", "1 mac": "1 Maccabees",
    "2ma": "2 Maccabees", "2mac": "2 Maccabees", "2 mac": "2 Maccabees",
    # New Testament
    "mat": "Matthew", "matt": "Matthew", "mt": "Matthew",
    "mrk": "Mark", "mk": "Mark",
    "luk": "Luke", "lk": "Luke",
    "jhn": "John", "jn": "John",
    "act": "Acts", "ac": "Acts",
    "rom": "Romans", "ro": "Romans", "rm": "Romans",
    "1co": "1 Corinthians", "1cor": "1 Corinthians", "1 cor": "1 Corinthians",
    "2co": "2 Corinthians", "2cor": "2 Corinthians", "2 cor": "2 Corinthians",
    "gal": "Galatians", "ga": "Galatians",
    "eph": "Ephesians",
    "php": "Philippians", "phil": "Philippians",
    "col": "Colossians",
    "1th": "1 Thessalonians", "1thess": "1 Thessalonians", "1 th": "1 Thessalonians",
    "2th": "2 Thessalonians", "2thess": "2 Thessalonians", "2 th": "2 Thessalonians",
    "1ti": "1 Timothy", "1tim": "1 Timothy", "1 tim": "1 Timothy",
    "2ti": "2 Timothy", "2tim": "2 Timothy", "2 tim": "2 Timothy",
    "tit": "Titus",
    "phm": "Philemon",
    "heb": "Hebrews",
    "jas": "James", "jm": "James",
    "1pe": "1 Peter", "1pet": "1 Peter", "1 pt": "1 Peter",
    "2pe": "2 Peter", "2pet": "2 Peter", "2 pt": "2 Peter",
    "1jn": "1 John", "1jhn": "1 John", "1 jn": "1 John",
    "2jn": "2 John", "2jhn": "2 John", "2 jn": "2 John",
    "3jn": "3 John", "3jhn": "3 John", "3 jn": "3 John",
    "jud": "Jude",
    "rev": "Revelation", "re": "Revelation",
}


def resolve_book_id(book_query: str) -> Optional[int]:
    """Resolves an English or Tamil book string/abbreviation to a book_id."""
    clean = book_query.strip().lower().replace(".", "")
    clean_no_spaces = re.sub(r"\s+", " ", clean)

    # 1. Check direct abbreviations map
    if clean in BOOK_ABBREVIATIONS:
        target_name = BOOK_ABBREVIATIONS[clean].lower()
        for b_id, b_meta in CATHOLIC_BOOK_MAP.items():
            if b_meta["name_en"].lower() == target_name:
                return b_id

    # 2. Check exact matches across English and Tamil names
    for b_id, b_meta in CATHOLIC_BOOK_MAP.items():
        if b_meta["name_en"].lower() == clean_no_spaces:
            return b_id
        if b_meta["name_ta"] == book_query.strip():
            return b_id

    # 3. Check prefix / startswith match
    for b_id, b_meta in CATHOLIC_BOOK_MAP.items():
        if b_meta["name_en"].lower().startswith(clean_no_spaces):
            return b_id

    return None


async def handle_scripture_lookup(ctx: MessageContext) -> None:
    """Handles incoming scripture reference lookups like 'John 3:16' or 'Genesis 1:1-5'."""
    match = ctx.matches
    if not match:
        return

    raw_book = match.group(1).strip()
    chapter = int(match.group(2))
    verse_start = int(match.group(3)) if match.group(3) else None
    verse_end = int(match.group(4)) if match.group(4) else verse_start

    book_id = resolve_book_id(raw_book)
    if not book_id:
        return

    book_meta = CATHOLIC_BOOK_MAP.get(book_id, BOOK_MAP.get(book_id))
    if not book_meta:
        await ctx.reply_text(f"❌ *Book not found*: '{raw_book}' is not recognized.")
        return

    # Check chapter validity
    if chapter < 1 or chapter > book_meta["total_chapters"]:
        await ctx.reply_text(
            f"❌ *Invalid Chapter*: {book_meta['name_en']} has {book_meta['total_chapters']} chapters."
        )
        return

    # Offload blocking SQLite query to worker thread (as per DEV-PY-001)
    verses = await asyncio.to_thread(get_chapter_verses, book_id, chapter)
    if not verses:
        await ctx.reply_text("❌ No scripture text found for this chapter.")
        return

    book_en = book_meta["name_en"]
    book_ta = book_meta["name_ta"]
    is_tamil = is_tamil_text(ctx.text)
    sub = await get_subscriber(ctx.sender)
    pref_lang = sub.get("language") if sub else None
    is_parallel = (pref_lang == "both")

    if verse_start is not None:
        # Verse range filter
        selected = [
            v for v in verses
            if verse_start <= v["verse"] <= (verse_end or verse_start)
        ]
        if not selected:
            await ctx.reply_text(
                f"❌ Verse {verse_start} not found in {book_en} {chapter}."
            )
            return

        ref_header = (
            f"*{book_en} {chapter}:{verse_start}*"
            if verse_start == verse_end
            else f"*{book_en} {chapter}:{verse_start}-{verse_end}*"
        )
        lines = [f"📖 {ref_header} _({book_ta})_", ""]

        for v in selected:
            num = v["verse_display"] or v["verse"]
            t_ta = v.get("text_ta") or ""
            t_en = v.get("text_en") or ""
            if is_parallel and t_ta and t_en:
                lines.append(f"*{num}* 🇮🇳 {t_ta}\n🇬🇧 _{t_en}_")
            else:
                primary_text = t_ta if (is_tamil or pref_lang == "ta") else t_en
                secondary_text = t_en if (is_tamil or pref_lang == "ta") else t_ta
                if secondary_text and secondary_text != primary_text:
                    lines.append(f"*{num}* {primary_text}\n_{secondary_text}_")
                else:
                    lines.append(f"*{num}* {primary_text}")

        await ctx.reply_text("\n\n".join(lines))
    else:
        # Entire chapter requested -> Return summary and initial verses
        total_verses = len(verses)
        preview_count = min(5, total_verses)
        lines = [
            f"📖 *{book_en} Chapter {chapter}* _({book_ta})_",
            f"_{total_verses} verses in total._",
            "",
        ]
        for v in verses[:preview_count]:
            num = v["verse_display"] or v["verse"]
            t_ta = v.get("text_ta") or ""
            t_en = v.get("text_en") or ""
            if is_parallel and t_ta and t_en:
                lines.append(f"*{num}* {t_ta}\n_{t_en}_")
            else:
                txt = t_ta if (is_tamil or pref_lang == "ta") else t_en
                lines.append(f"*{num}* {txt}")

        if total_verses > preview_count:
            lines.append("")
            lines.append(
                f"_Showing first {preview_count} verses. Reply '{book_en} {chapter}:1-{min(preview_count+5, total_verses)}' to read more, or 'audio {book_en} {chapter}' to listen._"
            )

        await ctx.reply_text("\n\n".join(lines))


async def handle_search_command(ctx: MessageContext) -> None:
    """Search scriptures by keyword (e.g. 'search love' or 'find faith')."""
    parts = ctx.text.strip().split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await ctx.reply_text("💡 *Usage*: `search <keyword>` (e.g. `search faith` or `search peace`)")
        return

    query = parts[1].strip()
    results = await asyncio.to_thread(search_verses, query, canon="catholic", limit=5)

    if not results:
        await ctx.reply_text(f"🔍 No scripture verses found matching *'{query}'*.")
        return

    lines = [f"🔍 *Scripture Search Results for '{query}':*", ""]
    for i, r in enumerate(results, start=1):
        book_name = r.get("book_name_en") or r.get("book_name", "")
        ch = r.get("chapter")
        vs = r.get("verse_display") or r.get("verse")
        snippet = r.get("snippet") or r.get("text_en") or r.get("text_ta") or ""
        clean_snippet = re.sub(r"<[^>]+>", "*", snippet).strip()
        lines.append(f"{i}. *{book_name} {ch}:{vs}*\n_{clean_snippet}_")

    lines.append("")
    lines.append("_Send any reference above (e.g. 'John 3:16') to read the full context!_")
    await ctx.reply_text("\n\n".join(lines))


async def handle_quiz_start(ctx: MessageContext) -> None:
    """Starts an interactive Bible trivia quiz with Tamil/English support."""
    if not QUIZ_QUESTIONS:
        await ctx.reply_text("⚠️ Quiz questions dataset is currently empty.")
        return

    is_tamil = is_tamil_text(ctx.text)
    q = random.choice(QUIZ_QUESTIONS)
    options = q.get("options_ta" if is_tamil else "options_en", q.get("options_en", []))
    question_text = q.get("question_ta" if is_tamil else "question_en", q.get("question_en", ""))
    correct_idx = q.get("correct_index", 0)

    # Save state in conversational session store
    await ctx.set_state(
        state="QUIZ_WAITING_ANSWER",
        data={
            "question_id": q.get("id"),
            "question": question_text,
            "options": options,
            "correct_index": correct_idx,
            "reference": q.get("reference", ""),
            "explanation": q.get("explanation_ta" if is_tamil else "explanation_en", ""),
            "is_tamil": is_tamil,
        },
        ttl_seconds=300,
    )

    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    option_lines = [
        f"{number_emojis[i]} {opt}" for i, opt in enumerate(options)
    ]

    header = "❓ *வேதாகம வினாடி வினா:*" if is_tamil else "❓ *Daily Bible Trivia:*"
    prompt = "_பதிலளிக்க *1, 2, 3, அல்லது 4* என அனுப்பவும்!_" if is_tamil else "_Reply with *1, 2, 3, or 4* (or *A, B, C, D*) to answer!_"

    msg = f"{header}\n\n*{question_text}*\n\n{chr(10).join(option_lines)}\n\n{prompt}"
    await ctx.reply_text(msg)


async def handle_quiz_answer(ctx: MessageContext) -> None:
    """Evaluates the user's answer for the active quiz."""
    session = await ctx.get_state()
    if not session or session.get("state") != "QUIZ_WAITING_ANSWER":
        await ctx.reply_text("Type *quiz* to start a new Bible trivia challenge!")
        return

    data = session.get("data", {})
    user_input = ctx.text.strip().upper()
    is_tamil = data.get("is_tamil", False)

    char_map = {"1": 0, "A": 0, "2": 1, "B": 1, "3": 2, "C": 2, "4": 3, "D": 3}
    if user_input not in char_map:
        prompt = "தயவுசெய்து *1, 2, 3, அல்லது 4* என பதிலளிக்கவும்." if is_tamil else "Please reply with a valid choice: *1, 2, 3, or 4*."
        await ctx.reply_text(prompt)
        return

    selected_idx = char_map[user_input]
    correct_idx = data.get("correct_index", 0)
    options = data.get("options", [])
    explanation = data.get("explanation", "")
    ref = data.get("reference", "")

    # Clear state once answered
    await ctx.clear_state()

    if selected_idx == correct_idx:
        if is_tamil:
            reply = (
                f"🎉 *சரியான பதில்! வாழ்த்துகள்!*\n\n"
                f"✅ உங்கள் விடை: *{options[selected_idx]}*\n"
                f"📖 *வசன ஆதாரம்:* {ref}\n"
                f"💡 _{explanation}_\n\n"
                f"_அடுத்த கேள்விக்கு *quiz* என அனுப்பவும்!_"
            )
        else:
            reply = (
                f"🎉 *Correct! Excellent job!*\n\n"
                f"✅ You answered: *{options[selected_idx]}*\n"
                f"📖 *Reference:* {ref}\n"
                f"💡 _{explanation}_\n\n"
                f"_Reply *quiz* to play another round!_"
            )
    else:
        correct_answer = options[correct_idx] if correct_idx < len(options) else "Unknown"
        if is_tamil:
            reply = (
                f"❌ *தவறான விடை!*\n\n"
                f"சரியான விடை: *{correct_answer}*\n"
                f"📖 *வசன ஆதாரம்:* {ref}\n"
                f"💡 _{explanation}_\n\n"
                f"_மீண்டும் முயற்சிக்க *quiz* என அனுப்பவும்!_"
            )
        else:
            reply = (
                f"❌ *Not quite!*\n\n"
                f"The correct answer was: *{correct_answer}*\n"
                f"📖 *Reference:* {ref}\n"
                f"💡 _{explanation}_\n\n"
                f"_Reply *quiz* to try another question!_"
            )

    await ctx.reply_text(reply)


async def handle_songs_command(ctx: MessageContext) -> None:
    """Look up Christian hymn and worship song lyrics."""
    parts = ctx.text.strip().split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await ctx.reply_text("🎵 *Usage*: `song <title or number>` (e.g. `song Amazing Grace` or `song 2281`)")
        return

    arg = parts[1].strip()

    # If numeric ID
    if arg.isdigit():
        song_id = int(arg)
        song = await asyncio.to_thread(get_song_by_id, song_id)
        if not song:
            await ctx.reply_text(f"❌ Song ID *{song_id}* not found.")
            return

        is_ta = is_tamil_text(ctx.text)
        lyrics = (song.get("lyrics_ta") if is_ta else song.get("lyrics_en")) or song.get("lyrics_en") or song.get("lyrics_ta") or "No lyrics available."
        if len(lyrics) > 3500:
            lyrics = lyrics[:3500] + "\n\n_...[Lyrics truncated for length]..._"

        title_en = song.get("title_en", "")
        title_ta = song.get("title_ta", "")
        book_name = song.get("songbook_name_en", "")

        header = f"🎵 *{title_en}* _({title_ta})_\n_{book_name} • Song #{song.get('song_number', song_id)}_\n\n"
        await ctx.reply_text(header + lyrics)
        return

    # Text search
    res = await asyncio.to_thread(get_songs_list, query=arg, limit=5)
    songs = res.get("songs", [])

    if not songs:
        await ctx.reply_text(f"🔍 No songs found matching *'{arg}'*.")
        return

    if len(songs) == 1:
        full_song = await asyncio.to_thread(get_song_by_id, songs[0]["id"])
        is_ta = is_tamil_text(ctx.text)
        lyrics = (full_song.get("lyrics_ta") if is_ta else full_song.get("lyrics_en")) or full_song.get("lyrics_en") or ""
        if len(lyrics) > 3500:
            lyrics = lyrics[:3500] + "\n\n_...[Lyrics truncated for length]..._"
        title = full_song.get("title_en") or full_song.get("title_ta") or "Hymn"
        await ctx.reply_text(f"🎵 *{title}*\n\n{lyrics}")
        return

    lines = [f"🎵 *Songs matching '{arg}':*", ""]
    for i, s in enumerate(songs, start=1):
        s_title = s.get("title_en") or s.get("title_ta") or "Song"
        s_id = s.get("id")
        lines.append(f"{i}. *{s_title}* (ID: `{s_id}`)")

    lines.append("")
    lines.append("_Send 'song <ID>' (e.g. 'song 2281') to view full lyrics._")
    await ctx.reply_text("\n\n".join(lines))


def parse_reminder_time(text: str) -> Optional[str]:
    """
    Parses user input string into standardized 24-hour 'HH:MM' format.
    Supports: '5 AM', '5am', '5:00 AM', '05:00', '6:30 PM', '18:30', '5', 'காலை 5', 'மாலை 6:30', 'status', 'off'.
    """
    clean = text.strip().lower()
    if not clean:
        return None
    if clean in ("status", "current", "check", "show", "நிலவரம்"):
        return "status"
    if clean in ("off", "stop", "cancel", "disable", "நிறுத்து", "முடக்கு"):
        return "off"

    is_pm = False
    is_am = False
    if any(k in clean for k in ("மாலை", "இரவு", "pm", "p.m.")):
        is_pm = True
    elif any(k in clean for k in ("காலை", "am", "a.m.")):
        is_am = True

    num_part = re.sub(r"[^\d:.]", " ", clean).strip()
    tokens = num_part.split()
    if not tokens:
        return None
    time_str = tokens[0]

    hour = 0
    minute = 0
    if ":" in time_str or "." in time_str:
        sep = ":" if ":" in time_str else "."
        parts = time_str.split(sep)
        try:
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            return None
    else:
        try:
            hour = int(time_str)
            minute = 0
        except ValueError:
            return None

    if is_pm and hour < 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0

    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return f"{hour:02d}:{minute:02d}"
    return None


def format_time_display(time_24: str) -> str:
    """Formats 'HH:MM' into friendly 12-hour string (e.g. '05:00' -> '5:00 AM')."""
    try:
        dt = datetime.strptime(time_24, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return time_24


async def handle_plan_command(ctx: MessageContext) -> None:
    """View today's reading plan, explore available plans, or switch plan."""
    text = ctx.text.strip()
    is_ta = is_tamil_text(text)

    # Strip command prefix
    clean = re.sub(r"^(?:plan|plans|reading|திட்டம்)\s*", "", text, flags=re.IGNORECASE).strip()

    sub = await get_subscriber(ctx.sender)
    active_plan_id = sub.get("plan_id", "full-bible-365") if sub else "full-bible-365"
    plan_start = sub.get("plan_start_date") if sub else None

    target_plan = get_plan(clean) if clean else None
    day_match = re.match(r"^(?:day\s*)?(\d+)$", clean, re.IGNORECASE)
    day_num = int(day_match.group(1)) if day_match else None

    # Switching active plan
    if target_plan and not day_num:
        new_plan_id = target_plan["id"]
        today_str = datetime.now().strftime("%Y-%m-%d")
        await update_subscriber_plan(ctx.sender, new_plan_id, plan_start_date=today_str)
        reading = get_today_plan_reading(new_plan_id, start_date=today_str)
        curr_day = reading.get("current_day", 1)
        tot_days = reading.get("total_days", 365)
        ref_text = reading.get("ref_ta" if is_ta else "ref_en") or reading.get("ref")
        plan_name = target_plan.get("title_ta" if is_ta else "title_en")

        b_id = reading.get("book_id", 1)
        ch_num = reading.get("chapter", 1)
        b_meta = CATHOLIC_BOOK_MAP.get(b_id, BOOK_MAP.get(b_id, {"name_en": "Genesis", "name_ta": "ஆதியாகமம்"}))
        book_name = b_meta.get("name_ta" if is_ta else "name_en", "Genesis")

        if is_ta:
            reply = (
                f"✅ *உங்கள் வாசிப்புத் திட்டம் மாற்றப்பட்டது!*\n\n"
                f"📜 *திட்டம்:* {plan_name} ({tot_days} நாட்கள்)\n"
                f"📅 *இன்றைய வாசிப்பு (நாள் {curr_day}):* {ref_text}\n\n"
                f"• முழு அதிகாரத்தை வாசிக்க *{book_name} {ch_num}* என அனுப்பவும்.\n"
                f"• ஆடியோ கேட்க *audio {book_name} {ch_num}* என அனுப்பவும்.\n"
                f"• அனைத்து திட்டங்களை பார்க்க *plan* என அனுப்பவும்."
            )
        else:
            reply = (
                f"✅ *Reading Plan Switched Successfully!*\n\n"
                f"📜 *Plan:* {plan_name} ({tot_days} Days)\n"
                f"📅 *Today's Reading (Day {curr_day}):* {ref_text}\n\n"
                f"• Reply *{book_name} {ch_num}* to read full chapter.\n"
                f"• Reply *audio {book_name} {ch_num}* for instant voice note.\n"
                f"• Reply *plan* to see all plans or switch anytime."
            )
        await ctx.reply_text(reply)
        return

    # Reading display
    target_plan_id = active_plan_id
    if day_num:
        reading = get_today_plan_reading(target_plan_id, day_number=day_num)
    else:
        reading = get_today_plan_reading(target_plan_id, start_date=plan_start)

    if not reading:
        reading = get_today_plan_reading("full-bible-365", day_number=day_num, start_date=plan_start)

    curr_day = reading.get("current_day", 1)
    tot_days = reading.get("total_days", 365)
    ref_text = reading.get("ref_ta" if is_ta else "ref_en") or reading.get("ref")
    plan_name = reading.get("plan_title_ta" if is_ta else "plan_title_en", "Full Bible in 365 Days")

    b_id = reading.get("book_id", 1)
    ch_num = reading.get("chapter", 1)
    b_meta = CATHOLIC_BOOK_MAP.get(b_id, BOOK_MAP.get(b_id, {"name_en": "Genesis", "name_ta": "ஆதியாகமம்"}))
    book_name = b_meta.get("name_ta" if is_ta else "name_en", "Genesis")

    if is_ta:
        lines = [
            "📅 *தினசரி வேதாகம வாசிப்புத் திட்டம்* 📅",
            f"📜 *நடப்பு திட்டம்:* {plan_name}",
            f"✨ *இன்றைய வாசிப்பு (நாள் {curr_day}/{tot_days}):*",
            f"📖 *{ref_text}*",
            "",
            f"• வாசிக்க: *{book_name} {ch_num}*",
            f"• ஆடியோ கேட்க: *audio {book_name} {ch_num}*",
            "",
            "*கிடைக்கும் வாசிப்புத் திட்டங்கள்:*",
            "1. *முழு வேதாகமம் (365 நாட்கள்)* - மாற்ற: `plan full`",
            "2. *புதிய ஏற்பாடு (90 நாட்கள்)* - மாற்ற: `plan nt`",
            "3. *நீதிமொழிகள் (31 நாட்கள்)* - மாற்ற: `plan proverbs`",
            "4. *தேறுதலின் சங்கீதங்கள் (30 நாட்கள்)* - மாற்ற: `plan psalms`",
            "5. *இரண்டாம் திருமுறை (30 நாட்கள்)* - மாற்ற: `plan deuterocanon`",
            "",
            "_குறிப்பிட்ட நாளின் பகுதியை பார்க்க: `plan <நாள்>` (எ.கா. `plan 50`)_"
        ]
    else:
        lines = [
            "📅 *Daily Scripture Reading Plan* 📅",
            f"📜 *Current Plan:* {plan_name}",
            f"✨ *Today's Assigned Reading (Day {curr_day}/{tot_days}):*",
            f"📖 *{ref_text}*",
            "",
            f"• Read chapter: *{book_name} {ch_num}*",
            f"• Audio voice note: *audio {book_name} {ch_num}*",
            "",
            "*Available Reading Plans:*",
            "1. *Full Bible in 365 Days* (~3.2 ch/day) - `plan full`",
            "2. *New Testament in 90 Days* (~2.9 ch/day) - `plan nt`",
            "3. *Proverbs in 31 Days* (1 ch/day) - `plan proverbs`",
            "4. *Psalms of Peace & Comfort* (30 Days) - `plan psalms`",
            "5. *Deuterocanonical Books* (30 Days) - `plan deuterocanon`",
            "",
            "_To switch plan, reply e.g. `plan full` or `plan nt`._\n_To view a specific day, reply `plan <day>` (e.g. `plan 50`)._"
        ]
    await ctx.reply_text("\n".join(lines))


async def handle_done_command(ctx: MessageContext) -> None:
    """Marks today's reading plan portion as completed, updating consecutive reading streak."""
    text = ctx.text.strip()
    is_ta = is_tamil_text(text)

    # Optional explicit day specified (e.g. 'done 5')
    day_match = re.search(r"\b(\d+)\b", text)
    explicit_day = int(day_match.group(1)) if day_match else None

    sub = await get_subscriber(ctx.sender)
    active_plan_id = sub.get("plan_id", "full-bible-365") if sub else "full-bible-365"
    plan_meta = get_plan(active_plan_id) or READING_PLANS["full-bible-365"]
    total_days = plan_meta.get("total_days", 365)
    plan_title = plan_meta.get("title_ta" if is_ta else "title_en", "Bible Reading Plan")

    res = await mark_subscriber_day_done(ctx.sender, day=explicit_day)
    curr_day = res.get("day", 1)
    streak = res.get("streak_count", 1)
    completed_count = res.get("completed_count", 1)
    pct = min(100, int((completed_count / total_days) * 100))

    next_day_num = curr_day + 1 if curr_day < total_days else 1
    next_item = get_today_plan_reading(active_plan_id, day_number=next_day_num)
    next_ref = (next_item.get("ref_ta" if is_ta else "ref_en") or next_item.get("ref", "")) if next_item else ""

    filled = min(10, max(0, pct // 10))
    bar = "▓" * filled + "░" * (10 - filled)

    if is_ta:
        reply = (
            f"🎉 *வாசிப்பு நிறைவடைந்தது! நாள் {curr_day} குறிக்கப்பட்டது!* ✅\n\n"
            f"🔥 *தொடர் வாசிப்பு (Streak):* *{streak} நாட்கள்* 🚀\n"
            f"📊 *திட்டம்:* {plan_title}\n"
            f"📈 *முன்னேற்றம்:* [{bar}] *{pct}%* ({completed_count}/{total_days} நாட்கள்)\n\n"
            f"📖 *அடுத்த பகுதி (நாள் {next_day_num}):* {next_ref}\n"
            f"✨ _உங்களின் அர்ப்பணிப்பான வேத வாசிப்பு தொடரட்டும்!_"
        )
    else:
        reply = (
            f"🎉 *Reading Completed! Day {curr_day} Marked as Done!* ✅\n\n"
            f"🔥 *Current Streak:* *{streak} Days* 🚀\n"
            f"📊 *Plan:* {plan_title}\n"
            f"📈 *Progress:* [{bar}] *{pct}%* ({completed_count}/{total_days} Days)\n\n"
            f"📖 *Next Portion (Day {next_day_num}):* {next_ref}\n"
            f"✨ _Keep up the faithful reading journey!_"
        )
    await ctx.reply_text(reply)


async def handle_streak_command(ctx: MessageContext) -> None:
    """Displays current reading streak, progress bar, and completion summary."""
    is_ta = is_tamil_text(ctx.text)
    sub = await get_subscriber(ctx.sender)
    active_plan_id = sub.get("plan_id", "full-bible-365") if sub else "full-bible-365"
    plan_meta = get_plan(active_plan_id) or READING_PLANS["full-bible-365"]
    total_days = plan_meta.get("total_days", 365)
    plan_title = plan_meta.get("title_ta" if is_ta else "title_en", "Bible Reading Plan")

    stats = await get_subscriber_streak(ctx.sender)
    streak = stats.get("streak_count", 0)
    completed_count = stats.get("completed_count", 0)
    pct = min(100, int((completed_count / total_days) * 100)) if total_days > 0 else 0
    last_date = stats.get("last_read_date") or "None"

    filled = min(10, max(0, pct // 10))
    bar = "▓" * filled + "░" * (10 - filled)

    if is_ta:
        reply = (
            f"🏆 *உங்கள் வேத வாசிப்பு நிலை & சாதனை* 🏆\n\n"
            f"🔥 *நடப்பு தொடர் (Streak):* *{streak} நாட்கள்*\n"
            f"📜 *நடப்பு திட்டம்:* {plan_title}\n"
            f"📊 *நிறைவு:* [{bar}] *{pct}%* ({completed_count}/{total_days} நாட்கள்)\n"
            f"📅 *கடைசி வாசிப்பு:* {last_date}\n\n"
            f"• இன்றைய பகுதியை முடிக்க: *done*\n"
            f"• வாசிப்புப் பகுதியை பார்க்க: *plan*"
        )
    else:
        reply = (
            f"🏆 *Your Bible Reading Streak & Progress* 🏆\n\n"
            f"🔥 *Current Streak:* *{streak} Days*\n"
            f"📜 *Current Plan:* {plan_title}\n"
            f"📊 *Progress:* [{bar}] *{pct}%* ({completed_count}/{total_days} Days)\n"
            f"📅 *Last Completed:* {last_date}\n\n"
            f"• Mark today's reading done: reply *done*\n"
            f"• View today's portion: reply *plan*"
        )
    await ctx.reply_text(reply)


async def handle_card_command(ctx: MessageContext) -> None:
    """Generates an aesthetic, shareable 1080x1080 Scripture Status Card image."""
    text = ctx.text.strip()
    is_ta = is_tamil_text(text)
    clean_arg = re.sub(r"^(?:card|image|pic|photo|status|படம்)\s*", "", text, flags=re.IGNORECASE).strip()

    book_meta = None
    selected_verses = []
    ref_display = ""

    if clean_arg:
        # User specified a scripture reference (e.g. 'card John 3:16' or 'image Psalm 23:1')
        ref_match = re.match(r"^([1-3]?\s*[a-zA-Z\u0B80-\u0BFF\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$", clean_arg, re.IGNORECASE)
        if ref_match:
            raw_book = ref_match.group(1).strip()
            chapter = int(ref_match.group(2))
            v_start = int(ref_match.group(3)) if ref_match.group(3) else 1
            v_end = int(ref_match.group(4)) if ref_match.group(4) else v_start

            b_id = resolve_book_id(raw_book)
            if b_id:
                book_meta = CATHOLIC_BOOK_MAP.get(b_id, BOOK_MAP.get(b_id))
                all_verses = await asyncio.to_thread(get_chapter_verses, b_id, chapter)
                if all_verses:
                    selected_verses = [v for v in all_verses if v_start <= v["verse"] <= v_end][:3]
                    b_en = book_meta.get("name_en", raw_book)
                    b_ta = book_meta.get("name_ta", "")
                    ref_display = f"{b_en} {chapter}:{v_start}" if v_start == v_end else f"{b_en} {chapter}:{v_start}-{v_end}"
                    if b_ta:
                        ref_display += f" • {b_ta}"

    if not selected_verses:
        # Default to today's assigned reading or popular verse (John 3:16)
        sub = await get_subscriber(ctx.sender)
        active_plan = sub.get("plan_id", "full-bible-365") if sub else "full-bible-365"
        plan_start = sub.get("plan_start_date") if sub else None
        reading = get_today_plan_reading(active_plan, start_date=plan_start) or get_today_plan_reading("full-bible-365")
        b_id = reading.get("book_id", 43)  # default to John if not found
        ch_num = reading.get("chapter", 3)
        book_meta = CATHOLIC_BOOK_MAP.get(b_id, BOOK_MAP.get(b_id, {"name_en": "John", "name_ta": "யோவான்"}))
        all_verses = await asyncio.to_thread(get_chapter_verses, b_id, ch_num)
        selected_verses = all_verses[:1] if all_verses else []
        b_en = book_meta.get("name_en", "John")
        b_ta = book_meta.get("name_ta", "யோவான்")
        ref_display = f"{b_en} {ch_num}:1 • {b_ta} {ch_num}:1"

    if not selected_verses:
        await ctx.reply_text("⚠️ Could not generate card: scripture text unavailable.")
        return

    en_texts = [v.get("text_en") or "" for v in selected_verses if v.get("text_en")]
    ta_texts = [v.get("text_ta") or "" for v in selected_verses if v.get("text_ta")]
    combined_en = " ".join(en_texts)
    combined_ta = " ".join(ta_texts)

    try:
        card_bytes = await asyncio.to_thread(
            generate_verse_card,
            ref_text=ref_display,
            scripture_en=combined_en,
            scripture_ta=combined_ta,
        )
        caption = (
            f"🖼️ *வேத வசனப் படம்:* {ref_display}\n"
            f"✨ _வாட்ஸ்அப் ஸ்டேட்டஸ் அல்லது நண்பர்களுடன் பகிரவும்!_"
            if is_ta else
            f"🖼️ *Scripture Status Card:* {ref_display}\n"
            f"✨ _Share this blessing with your family or WhatsApp Status!_"
        )
        await ctx.reply_image(card_bytes, caption=caption, file_name="verse_card.jpg")
    except Exception as exc:
        logger.error("Failed to generate verse card: %s", exc)
        await ctx.reply_text(
            f"📖 *{ref_display}*\n\n{combined_ta}\n\n_{combined_en}_\n\n"
            f"⚠️ _(Image card generation encountered an error: {exc})_"
        )


async def handle_language_command(ctx: MessageContext) -> None:
    """Configures language delivery preference: 'en', 'ta', or 'both' (bilingual parallel)."""
    text = ctx.text.strip()
    is_ta = is_tamil_text(text)
    clean_arg = re.sub(r"^(?:lang|language|parallel|bilingual|மொழி)\s*", "", text, flags=re.IGNORECASE).strip().lower()

    if clean_arg in ("both", "parallel", "bilingual", "இரண்டும்", "இருமொழி"):
        await update_subscriber_language(ctx.sender, "both")
        reply = (
            "✅ *இருமொழி இணையான முறை (Bilingual Parallel Mode) தேர்வு செய்யப்பட்டது!* 📖\n\n"
            "இனி வேத வசனங்கள் மற்றும் தினசரி தியானங்கள் தமிழ் மற்றும் ஆங்கிலம் இரண்டிலும் இணையாக அனுப்பப்படும்.\n\n"
            "• மாற்ற: `lang ta` (தமிழ்) அல்லது `lang en` (ஆங்கிலம்)"
            if is_ta else
            "✅ *Bilingual Parallel Mode Enabled!* 📖\n\n"
            "All scripture lookups and daily devotionals will now be delivered in both Tamil and English side-by-side.\n\n"
            "• Switch anytime: reply *lang ta* (Tamil) or *lang en* (English)."
        )
        await ctx.reply_text(reply)
    elif clean_arg in ("ta", "tamil", "தமிழ்"):
        await update_subscriber_language(ctx.sender, "ta")
        await ctx.reply_text("✅ *மொழி தமிழுக்கு மாற்றப்பட்டது!* (பரிசுத்த வேதாகமம்) 📖\n\nமாற்ற: `lang both` அல்லது `lang en`.")
    elif clean_arg in ("en", "english", "ஆங்கிலம்"):
        await update_subscriber_language(ctx.sender, "en")
        await ctx.reply_text("✅ *Language set to English!* (KJV Holy Bible) 📖\n\nSwitch anytime: reply *lang both* or *lang ta*.")
    else:
        sub = await get_subscriber(ctx.sender)
        curr = (sub.get("language") or "en") if sub else "en"
        curr_label = "Bilingual Parallel (🇮🇳 Tamil + 🇬🇧 English)" if curr == "both" else ("Tamil (தமிழ்)" if curr == "ta" else "English")
        reply = (
            f"🌐 *மொழி அமைப்புகள் (Language Settings)* 🌐\n\n"
            f"நடப்பு மொழி: *{curr_label}*\n\n"
            "• `lang both` — இருமொழி இணையாக (Tamil + English Parallel)\n"
            "• `lang ta` — தமிழ் மட்டும் (Tamil Only)\n"
            "• `lang en` — ஆங்கிலம் மட்டும் (English Only)"
            if is_ta else
            f"🌐 *Language Settings* 🌐\n\n"
            f"Current Preference: *{curr_label}*\n\n"
            "• *lang both* — Bilingual Parallel (Tamil + English side-by-side)\n"
            "• *lang ta* — Tamil Only (தமிழ்)\n"
            "• *lang en* — English Only (KJV)"
        )
        await ctx.reply_text(reply)


async def handle_sync_command(ctx: MessageContext) -> None:
    """Generates an ephemeral 15-minute sync code to connect WhatsApp with the Web App."""
    is_ta = is_tamil_text(ctx.text)
    code = generate_sync_code(ctx.sender)
    if is_ta:
        reply = (
            "🔗 *இணையதள இணைப்பு & ஒத்திசைவு (Web Bible Sync)* 🔗\n\n"
            f"உங்களின் 15 நிமிட இணைப்பு குறியீடு: *{code}*\n\n"
            "இக்குறியீட்டை இணையதளத்தில் (*https://webbible.app/sync* அல்லது Plans பக்கத்தில்) உள்ளீடு செய்து, "
            "உங்கள் வாட்ஸ்அப் தொடர் வாசிப்பு (Streak), திட்ட முன்னேற்றம் மற்றும் அமைப்புகளை உடனடியாக இணையதளத்துடன் இணைத்துக் கொள்ளலாம்!"
        )
    else:
        reply = (
            "🔗 *Web Bible & WhatsApp Account Sync* 🔗\n\n"
            f"Your 15-minute Linking Code is: *{code}*\n\n"
            "Enter this code on the website at *https://webbible.app/sync* (or on your Web Plans page) to instantly "
            "synchronize your reading streak, plan progress, and preferences with your browser reader!"
        )
    await ctx.reply_text(reply)


async def handle_reminder_command(ctx: MessageContext) -> None:
    """View or set daily reminder dispatch time (default: 5:00 AM)."""
    text = ctx.text.strip()
    is_ta = is_tamil_text(text)

    clean_arg = re.sub(r"^(?:remind|reminder|time|alarm|நேரம்|நினைவூட்டல்)\s*", "", text, flags=re.IGNORECASE).strip()

    sub = await get_subscriber(ctx.sender)
    current_time_24 = sub.get("reminder_time", "05:00") if sub else "05:00"
    current_time_display = format_time_display(current_time_24)

    if not clean_arg or clean_arg.lower() in ("status", "current", "check", "நிலவரம்"):
        if is_ta:
            reply = (
                f"⏰ *தினசரி வேத நினைவூட்டல் நேரம்: {current_time_display} ({current_time_24})* ☀️\n\n"
                f"இயல்புநிலை நேரம்: *காலை 5:00 மணி (05:00)*.\n\n"
                f"*நேரத்தை மாற்ற கீழ்கண்டவாறு அனுப்பவும்:*\n"
                f"• `remind 5 AM` (காலை 5:00 மணி - இயல்புநிலை)\n"
                f"• `remind 6:00 AM` (காலை 6:00 மணி)\n"
                f"• `remind 6:30 AM` (காலை 6:30 மணி)\n"
                f"• `remind 9:00 PM` (இரவு 9:00 மணி)\n"
                f"• `remind off` (நினைவூட்டலை நிறுத்த)"
            )
        else:
            reply = (
                f"⏰ *Your Daily Scripture Reminder: {current_time_display} ({current_time_24})* ☀️\n\n"
                f"System default reminder time is *5:00 AM (05:00)*.\n\n"
                f"*To set or change your reminder time:*\n"
                f"• `remind 5 AM` (Default morning 5:00 AM)\n"
                f"• `remind 6:00 AM`\n"
                f"• `remind 6:30 AM`\n"
                f"• `remind 9:00 PM`\n"
                f"• `remind 05:00` (24-hour format)\n"
                f"• `remind off` (disable daily reminder)"
            )
        await ctx.reply_text(reply)
        return

    parsed = parse_reminder_time(clean_arg)
    if parsed == "off":
        await remove_subscriber(ctx.sender)
        if is_ta:
            await ctx.reply_text("👋 *உங்கள் தினசரி நினைவூட்டல் நிறுத்தப்பட்டது.* மீண்டும் தொடங்க *remind 5 AM* அல்லது *subscribe* என அனுப்பவும்.")
        else:
            await ctx.reply_text("👋 *Your daily reminders have been stopped.* Reply *remind 5 AM* or *subscribe* anytime to re-enable.")
        return

    if not parsed or parsed == "status":
        if is_ta:
            await ctx.reply_text(
                "❌ *நேர வடிவம் தவறானது.*\n"
                "சரியான வடிவங்கள்: `remind 5 AM`, `remind 6:30 AM`, `remind 05:00`, `remind காலை 5`"
            )
        else:
            await ctx.reply_text(
                "❌ *Invalid time format.*\n"
                "Please use formats like: `remind 5 AM`, `remind 6:30 AM`, `remind 05:00`, or `remind 9 PM`."
            )
        return

    success = await update_subscriber_reminder_time(ctx.sender, parsed)
    disp = format_time_display(parsed)
    if success:
        if is_ta:
            await ctx.reply_text(
                f"⏰ *தினசரி வேத நினைவூட்டல் நேரம் மாற்றப்பட்டது: {disp} ({parsed})!* ☀️\n\n"
                f"ஒவ்வொரு நாளும் இந்த நேரத்தில் இன்றைய வேத வாசிப்பு மற்றும் வசனம் உங்கள் வாட்ஸ்அப்பிற்கு வந்து சேரும்.\n\n"
                f"_நேரத்தை மீண்டும் மாற்ற `remind <நேரம்>` (எ.கா. `remind 5 AM`) என அனுப்பவும்._"
            )
        else:
            await ctx.reply_text(
                f"⏰ *Daily Scripture Reminder Set to: {disp} ({parsed})!* ☀️\n\n"
                f"You will receive your daily Scripture verse and reading checkpoint every morning at {disp}.\n\n"
                f"_To change time, reply `remind <time>` (e.g. `remind 5 AM`)._"
            )
    else:
        await ctx.reply_text("⚠️ Could not update reminder time. Please try again.")


async def handle_subscribe(ctx: MessageContext) -> None:
    """Subscribes the user to daily scripture devotionals (default: 5:00 AM, Full Bible plan)."""
    is_ta = is_tamil_text(ctx.text)
    lang = "ta" if is_ta else "en"
    today_str = datetime.now().strftime("%Y-%m-%d")
    success = await add_subscriber(
        phone=ctx.sender,
        name=ctx.sender_name,
        language=lang,
        plan_id="full-bible-365",
        reminder_time="05:00",
        plan_start_date=today_str,
    )
    if success:
        if is_ta:
            await ctx.reply_text(
                "✅ *தினசரி வேதாகம பகிர்வில் இணைந்ததற்கு நன்றி!* ☀️\n\n"
                "ஒவ்வொரு நாளும் *காலை 5:00 மணிக்கு (05:00)* உங்கள் வாட்ஸ்அப்பிற்கு தினசரி வசனம் மற்றும் வாசிப்புத் திட்டம் அனுப்பப்படும்.\n\n"
                "• நினைவூட்டல் நேரத்தை மாற்ற: *remind <நேரம்>* (எ.கா. `remind 6 AM`)\n"
                "• வாசிப்புத் திட்டத்தை மாற்ற: *plan*\n"
                "• விலக விரும்பினால் *stop* என அனுப்பவும்."
            )
        else:
            await ctx.reply_text(
                "✅ *Subscribed to Daily Scripture Devotionals!* ☀️\n\n"
                "You will receive each day's scripture reading directly on WhatsApp *every morning at 5:00 AM (05:00)*.\n\n"
                "• To change reminder time: reply *remind <time>* (e.g. `remind 6 AM`)\n"
                "• To customize reading plan: reply *plan*\n"
                "• Reply *stop* anytime to unsubscribe."
            )
    else:
        await ctx.reply_text("⚠️ Could not complete subscription. Please try again.")


async def handle_unsubscribe(ctx: MessageContext) -> None:
    """Unsubscribes the user from daily devotionals."""
    await remove_subscriber(ctx.sender)
    if is_tamil_text(ctx.text):
        await ctx.reply_text("👋 *நீங்கள் தினசரி பகிர்விலிருந்து விலகினீர்கள்.* மீண்டும் இணைய *subscribe* என அனுப்பவும்.")
    else:
        await ctx.reply_text("👋 *You have been unsubscribed from daily devotionals.* Reply *subscribe* anytime to re-join.")


async def handle_audio_command(ctx: MessageContext) -> None:
    """Handles audio voice note generation (e.g. 'audio John 1' or 'listen Psalm 23' or 'audio யோவான் 1')."""
    raw_text = ctx.text.strip()
    cmd_match = re.match(r"^(?:audio|listen|voice|கேட்க)\s*(.*)$", raw_text, re.IGNORECASE)
    ref = cmd_match.group(1).strip() if cmd_match else ""

    if not ref:
        await ctx.reply_text(
            "🎧 *Audio Bible Voice Notes*\n\n"
            "• `audio John 1` (Listen to John chapter 1)\n"
            "• `audio 1 John 1:1-5` (Listen to specific verses)\n"
            "• `audio Psalm 23` (Listen to Psalm 23)\n"
            "• `audio யோவான் 1` (Listen in Tamil)\n\n"
            "_Send `audio <book> <chapter>` to receive an instant WhatsApp voice note!_"
        )
        return

    ref_match = re.match(
        r"^([1-3]?\s*[a-zA-Z\u0B80-\u0BFF\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$",
        ref,
        re.IGNORECASE,
    )
    if not ref_match:
        await ctx.reply_text(
            "❌ *Invalid format*. Please specify book and chapter:\n"
            "• `audio John 1`\n"
            "• `audio 1 John 1`\n"
            "• `audio Psalm 23`\n"
            "• `audio John 1:1-5`"
        )
        return

    raw_book = ref_match.group(1).strip()
    chapter = int(ref_match.group(2))
    v_start = int(ref_match.group(3)) if ref_match.group(3) else None
    v_end = int(ref_match.group(4)) if ref_match.group(4) else v_start

    book_id = resolve_book_id(raw_book)
    if not book_id:
        await ctx.reply_text(f"❌ Book '{raw_book}' not recognized. Please check spelling (e.g. `audio John 1`).")
        return

    book_meta = CATHOLIC_BOOK_MAP.get(book_id, BOOK_MAP.get(book_id))
    verses = await asyncio.to_thread(get_chapter_verses, book_id, chapter)
    if not verses:
        await ctx.reply_text(f"❌ No chapter text available for {book_meta.get('name_en', raw_book)} chapter {chapter}.")
        return

    total_verses = len(verses)
    if v_start is not None:
        start_idx = max(1, min(v_start, total_verses))
        end_idx = max(start_idx, min(v_end or start_idx, total_verses))
        if end_idx - start_idx + 1 > 7:
            end_idx = start_idx + 6
        selected_verses = verses[start_idx - 1:end_idx]
        range_label = f"{chapter}:{start_idx}-{end_idx}" if start_idx != end_idx else f"{chapter}:{start_idx}"
    else:
        take = min(5, total_verses)
        selected_verses = verses[:take]
        range_label = f"{chapter}:1-{take}"

    is_ta = is_tamil_text(raw_text) or is_tamil_text(raw_book)
    book_name = book_meta["name_ta"] if is_ta else book_meta["name_en"]
    lang_code = "ta" if is_ta else "en"
    text_key = "text_ta" if is_ta else "text_en"

    cleaned_lines = []
    for v in selected_verses:
        t = v.get(text_key) or (v.get("text_en") if is_ta else "") or ""
        t_clean = re.sub(r"\[.*?\]|\{.*?\}", "", t).strip()
        if t_clean:
            cleaned_lines.append(t_clean)

    if not cleaned_lines:
        await ctx.reply_text(f"❌ Scripture text unavailable for {book_name} {range_label}.")
        return

    scripture_speech = " ".join(cleaned_lines)
    caption_title = f"வேத ஆடியோ: {book_name} {range_label}" if is_ta else f"Audio Bible: {book_name} {range_label}"
    caption = f"🎧 {caption_title}\n\n_Reply '{book_name} {chapter}' to read full text._"

    # Check daily audio request quota (protects Edge-TTS and FFmpeg transcoding resources)
    allowed, usage, max_limit = rate_limiter.check_audio_quota_allowed(ctx.sender)
    if not allowed:
        quota_msg = build_audio_quota_message(max_limit, is_tamil=is_ta)
        await ctx.reply_text(quota_msg)
        return

    # Send immediate notification that the audio request is processing
    processing_notice = (
        f"⏳ *உங்கள் ஆடியோ பதிவு தயாராகிறது...* ({caption_title})\n_சிறிது நேரம் காத்திருக்கவும்._"
        if is_ta
        else f"⏳ *Processing your audio request...* ({caption_title})\n_Please wait a moment while the audio is prepared._"
    )
    await ctx.reply_text(processing_notice)

    # Neural speech synthesis with -8Hz deep bass
    voice_name = "ta-LK-KumarNeural" if is_ta else "en-US-ChristopherNeural"
    audio_bytes = b""
    try:
        import edge_tts
        comm = edge_tts.Communicate(scripture_speech, voice_name, pitch="-8Hz")
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
    except Exception as tts_err:
        logger.warning("Edge-TTS error (%s), falling back to gTTS", tts_err)

    if not audio_bytes:
        try:
            from gtts import gTTS
            fp = io.BytesIO()
            tts = gTTS(text=scripture_speech, lang=lang_code)
            await asyncio.to_thread(tts.write_to_fp, fp)
            audio_bytes = fp.getvalue()
        except Exception as gtts_err:
            logger.error("gTTS fallback failed: %s", gtts_err)
            await ctx.reply_text(
                f"⚠️ Could not synthesize audio voice note.\n\n"
                f"📖 *{book_name} {range_label}*:\n\n{scripture_speech[:800]}"
            )
            return

    safe_file_name = f"{book_meta['name_en'].replace(' ', '_')}_{chapter}.m4a"
    try:
        res = await ctx.reply_audio(
            file_path_or_bytes=audio_bytes,
            caption=caption,
            ptt=False,
            file_name=safe_file_name,
        )
        if not res or not res.success:
            err_detail = res.error if res else "Unknown dispatch error"
            logger.error("Failed to deliver WhatsApp audio note to %s: %s", ctx.sender, err_detail)
            await ctx.reply_text(
                f"🎧 *{caption_title}*\n\n"
                f"⚠️ _(Voice note delivery could not be completed: {err_detail})_\n\n"
                f"📖 *Scripture Text:*\n{scripture_speech[:900]}\n\n"
                f"_Reply '{book_name} {chapter}' to read the chapter._"
            )
    except Exception as exc:
        logger.error("Error dispatching audio note: %s", exc)
        await ctx.reply_text(
            f"🎧 *{caption_title}*\n\n"
            f"📖 *Scripture Text:*\n{scripture_speech[:900]}\n\n"
            f"_Reply '{book_name} {chapter}' to read the chapter._"
        )


async def handle_help_menu(ctx: MessageContext) -> None:
    """Displays the branded Holy Bible WhatsApp Assistant menu with available options."""
    is_ta = is_tamil_text(ctx.text)
    if is_ta:
        menu = (
            "🕊️ *வேதாகம வாட்ஸ்அப் உதவியாளருக்கு வரவேற்கிறோம்!* 🕊️\n"
            "வணக்கம்! உங்களுக்கு உதவ மகிழ்ச்சி அடைகிறோம். இதோ உங்களுக்குக் கிடைக்கக்கூடிய *விருப்பங்கள்* (Options Available):\n\n"
            "1️⃣ *வேத வாசிப்பு* 📖\n"
            "• ஏதேனும் ஒரு வேத வசனத்தை அனுப்பவும்:\n"
            "  `யோவான் 3:16`, `சங்கீதம் 23`, `ஆதியாகமம் 1:1-5`\n"
            "• கத்தோலிக்க திருமுறை: `தோபித்து 4:7`, `சீராக் 2:1`\n\n"
            "2️⃣ *வேத ஆடியோ* 🎧\n"
            "• `audio <நூல்> <அதிகாரம்>` (எ.கா. `audio யோவான் 1`)\n"
            "• ஆடியோ வசன பகுதி: `audio யோவான் 1:1-5`\n"
            "  _(தெளிவான குரல் பதிவு ஆடியோ உடனே அனுப்பப்படும்)_\n\n"
            "3️⃣ *வசனம் தேடுதல்* 🔍\n"
            "• `search <வார்த்தை>` (எ.கா. `search விசுவாசம்`, `search அன்பு`)\n\n"
            "4️⃣ *வேதாகம வினாடி வினா* ❓\n"
            "• `quiz` (4-விடைகள் கொண்ட வேதாகம வினாடி வினா விளையாட)\n\n"
            "5️⃣ *தினசரி வசனம் & நினைவூட்டல்* 🔔\n"
            "• `subscribe` (தினசரி காலை 5:00 மணிக்கு வசனம் பெற)\n"
            "• `remind <நேரம்>` (எ.கா. `remind 5 AM` அல்லது `remind 6 AM`)\n"
            "• `stop` (விலக)\n\n"
            "6️⃣ *கிறிஸ்தவ பாடல்கள்* 🎵\n"
            "• `song <எண்/தலைப்பு>` (எ.கா. `song 2281`, `song என்ன என் ஆனந்தம்`)\n\n"
            "7️⃣ *முழு வேதாகம வாசிப்புத் திட்டங்கள்* 📅\n"
            "• `plan` (இன்றைய வாசிப்புப் பகுதி & அட்டவணை)\n"
            "• `plan full` (365 நாட்கள் முழு வேதாகமம்)\n"
            "• `plan nt` (90 நாட்கள் புதிய ஏற்பாடு)\n\n"
            "8️⃣ *வாசிப்புத் தொடர் சாதனை (Habit Streak)* 🔥\n"
            "• `done` அல்லது `முடித்தேன்` (இன்றைய வாசிப்பை முடித்து தொடரை அதிகரிக்க)\n"
            "• `streak` அல்லது `progress` (உங்கள் தொடர் நாட்கள் & சதவீதத்தை அறிய)\n\n"
            "9️⃣ *வசன ஸ்டேட்டஸ் படம் (Status Card)* 🖼️\n"
            "• `card` அல்லது `image` அல்லது `படம்` (இன்றைய வசனத்தின் அழகிய 1080x1080 வாட்ஸ்அப் ஸ்டேட்டஸ் படம்)\n"
            "• தனிப்பயன் வசன படம்: `card யோவான் 3:16` அல்லது `card சங்கீதம் 23`\n\n"
            "🔟 *இருமொழி ஒப்புநோக்கு (Parallel Scripture)* 🌐\n"
            "• `lang both` அல்லது `parallel` (தமிழ் + ஆங்கிலம் அருகருகே வாசிக்க)\n"
            "• `lang ta` (தமிழ் மட்டும்), `lang en` (ஆங்கிலம் மட்டும்)\n\n"
            "1️⃣1️⃣ *இணையதள இணைப்பு (Web Bible Sync)* 📱\n"
            "• `sync` அல்லது `link` அல்லது `இணைப்பு` (15 நிமிட குறியீட்டைப் பெற்று இணையதளத்தில் /sync பக்கத்தில் உங்கள் தொடரை இணைக்க)\n\n"
            "👉 _தொடங்க மேலே உள்ள ஏதேனும் ஒரு எண் (1-11) அல்லது கட்டளையை அனுப்பவும்!_"
        )
    else:
        menu = (
            "🕊️ *Welcome to Holy Bible WhatsApp Assistant!* 🕊️\n"
            "Hello! Here are the *options available* for you:\n\n"
            "1️⃣ *Scripture Reading* 📖\n"
            "• Send any Bible passage to read immediately:\n"
            "  `John 3:16`, `Psalm 23`, `Genesis 1:1-5`\n"
            "• Catholic canon included: `Tobit 4:7`, `Sirach 2:1`\n\n"
            "2️⃣ *Audio Bible Voice Notes* 🎧\n"
            "• `audio <book> <chapter>` (e.g. `audio John 1`, `audio Psalm 23`)\n"
            "• Verse range: `audio John 1:1-5`\n"
            "  _(Listen to spoken chapter audio clips)_\n\n"
            "3️⃣ *Scripture Search* 🔍\n"
            "• `search <keyword>` (e.g. `search love`, `search grace`, `search faith`)\n\n"
            "4️⃣ *Daily Bible Quiz* ❓\n"
            "• `quiz` (interactive 4-choice trivia to test your knowledge)\n\n"
            "5️⃣ *Daily Devotional & Reminder* 🔔\n"
            "• `subscribe` (daily morning verses, default 5:00 AM)\n"
            "• `remind <time>` (e.g. `remind 5 AM` or `remind 6:30 AM`)\n"
            "• `stop` (unsubscribe anytime)\n\n"
            "6️⃣ *Hymns & Song Lyrics* 🎵\n"
            "• `song <title/ID>` (e.g. `song Amazing Grace` or `song 2281`)\n\n"
            "7️⃣ *Full Bible Reading Plans* 📅\n"
            "• `plan` (view today's assigned chapters & schedule)\n"
            "• `plan full` (Full Bible in 365 Days)\n"
            "• `plan nt` (New Testament in 90 Days)\n\n"
            "8️⃣ *Habit Streak & Mark as Done* 🔥\n"
            "• `done` (mark today's reading complete and advance your daily streak)\n"
            "• `streak` or `progress` (view streak count, progress bar, and completion stats)\n\n"
            "9️⃣ *Status Image Card Generator* 🖼️\n"
            "• `card` or `image` or `status` (generate 1080x1080 gold-bordered status image card)\n"
            "• Custom scripture card: `card John 3:16` or `card Psalm 23`\n\n"
            "🔟 *Bilingual Parallel Mode* 🌐\n"
            "• `lang both` or `parallel` (side-by-side Tamil + English verses)\n"
            "• `lang en` (English only), `lang ta` (Tamil only)\n\n"
            "1️⃣1️⃣ *Web Bible Magic Sync* 📱\n"
            "• `sync` or `link` (get 15-minute code to link reading streak with Web Bible at `/sync`)\n\n"
            "👉 _Reply with any option number (1-11) or type a command/scripture reference to begin!_"
        )
    await ctx.reply_text(menu)


async def handle_fallback(ctx: MessageContext) -> None:
    """Graceful fallback when input does not match commands or scripture citations."""
    text = ctx.text.strip()
    clean_text = re.sub(r"[^\w\s\u0B80-\u0BFF]", "", text).strip().lower()

    # Greetings matching (e.g. "hi", "hello", "hey", "hi there", "vanakkam", "வணக்கம்")
    greeting_tokens = ("hi", "hello", "hey", "vanakkam", "வணக்கம்", "praise the lord", "shalom", "good morning", "good evening", "namaste")
    if clean_text in greeting_tokens or any(clean_text.startswith(g + " ") for g in ("hi", "hello", "hey", "வணக்கம்", "vanakkam")):
        await handle_help_menu(ctx)
        return

    # Direct selection by menu option numbers 1 to 11
    if clean_text in ("1", "option 1", "opt 1", "விருப்பம் 1"):
        await ctx.reply_text(
            "📖 *Option 1: Scripture Reading*\n\n"
            "Send any Bible reference to read scripture immediately!\n"
            "• Examples: `John 3:16`, `Psalm 23`, `Genesis 1:1-5`, `Tobit 4:7`"
        )
        return
    elif clean_text in ("2", "option 2", "opt 2", "விருப்பம் 2"):
        await ctx.reply_text(
            "🎧 *Option 2: Audio Bible*\n\n"
            "Listen to high-quality audio chapter voice notes!\n"
            "• Type: `audio <book> <chapter>` (e.g. `audio John 3` or `audio Psalm 23`)\n"
            "• Verse range: `audio John 1:1-5`\n"
            "• Tamil audio: `audio யோவான் 1`"
        )
        return
    elif clean_text in ("3", "option 3", "opt 3", "விருப்பம் 3"):
        await ctx.reply_text(
            "🔍 *Option 3: Scripture Search*\n\n"
            "Search verses across the Old and New Testaments by keyword!\n"
            "• Type: `search <keyword>` (e.g. `search love`, `search grace`, `search peace`)"
        )
        return
    elif clean_text in ("4", "option 4", "opt 4", "விருப்பம் 4"):
        await handle_quiz_start(ctx)
        return
    elif clean_text in ("5", "option 5", "opt 5", "விருப்பம் 5"):
        await ctx.reply_text(
            "🔔 *Option 5: Daily Devotional & Reminder*\n\n"
            "Receive daily verses and reading checkpoints directly on WhatsApp!\n"
            "• Default reminder time: *5:00 AM (05:00)*\n"
            "• Type `subscribe` to join\n"
            "• Type `remind 5 AM` (or `remind 6:30 AM`, `remind 9 PM`) to set reminder time\n"
            "• Type `remind` to check your current reminder time\n"
            "• Type `stop` to unsubscribe anytime"
        )
        return
    elif clean_text in ("6", "option 6", "opt 6", "விருப்பம் 6"):
        await ctx.reply_text(
            "🎵 *Option 6: Christian Songs & Hymns*\n\n"
            "Look up lyrics from Christian songbooks and hymnals!\n"
            "• Type: `song <title>` (e.g. `song Amazing Grace`)\n"
            "• Type: `song <number>` (e.g. `song 2281`)"
        )
        return
    elif clean_text in ("7", "option 7", "opt 7", "விருப்பம் 7"):
        await ctx.reply_text(
            "📅 *Option 7: Full Bible Reading Plans*\n\n"
            "Follow structured reading plans right inside WhatsApp!\n"
            "• Type `plan` to view today's assigned reading\n"
            "• Type `plan full` for Full Bible in 365 Days (~3.2 ch/day)\n"
            "• Type `plan nt` for New Testament in 90 Days (~2.9 ch/day)\n"
            "• Type `plan proverbs` for Proverbs in 31 Days (1 ch/day)\n"
            "• Type `plan <day>` (e.g. `plan 50`) for a specific day's reading"
        )
        return
    elif clean_text in ("8", "option 8", "opt 8", "விருப்பம் 8"):
        await ctx.reply_text(
            "🔥 *Option 8: Habit Streak & Mark as Done*\n\n"
            "Build a continuous daily Bible reading habit!\n"
            "• Reply *done* (or *read*, *முடித்தேன்*) to mark today's reading complete and advance your streak.\n"
            "• Reply *streak* (or *progress*, *தொடர்*) to view your current streak, progress bar, and completion summary."
        )
        return
    elif clean_text in ("9", "option 9", "opt 9", "விருப்பம் 9"):
        await ctx.reply_text(
            "🖼️ *Option 9: Status Image Card Generator*\n\n"
            "Generate beautiful 1080x1080 graphic cards for your WhatsApp Status or friends!\n"
            "• Type *card* (or *image*, *status*, *படம்*) to receive today's verse card with gold borders.\n"
            "• Or specify any passage: *card John 3:16* or *card Psalm 23*."
        )
        return
    elif clean_text in ("10", "option 10", "opt 10", "விருப்பம் 10"):
        await ctx.reply_text(
            "🌐 *Option 10: Bilingual Parallel Mode*\n\n"
            "Read Tamil and English verses side-by-side in all lookups and devotionals!\n"
            "• Type *lang both* (or *parallel*) for Tamil + English side-by-side.\n"
            "• Type *lang ta* for Tamil only.\n"
            "• Type *lang en* for English only."
        )
        return
    elif clean_text in ("11", "option 11", "opt 11", "விருப்பம் 11"):
        await ctx.reply_text(
            "📱 *Option 11: Web Bible 15-Minute Magic Sync*\n\n"
            "Connect your WhatsApp reading streak with the Web Bible reader!\n"
            "• Type *sync* (or *link*, *இணைப்பு*) to get your 15-minute linking code.\n"
            "• Enter the code on the website at */sync* to sync your streaks and reading progress with zero passwords."
        )
        return

    await ctx.reply_text(
        f"🤔 I didn't recognize: *\"{text[:40]}\"*\n\n"
        "Try sending a scripture reference like *John 3:16*, type *Hi* to see all available options, or type *help*!"
    )


def register_bible_handlers(dispatcher: BotDispatcher) -> None:
    """Registers all Holy Bible domain handlers with the decoupled BotDispatcher."""
    # 0. Global Rate Limiter Pre-Dispatch Middleware
    async def rate_limit_guard(ctx: MessageContext) -> bool:
        allowed, cooldown, reason = rate_limiter.check_request_allowed(ctx.sender)
        if not allowed:
            cooldown_msg = build_cooldown_message(cooldown, is_tamil=is_tamil_text(ctx.text))
            await ctx.reply_text(cooldown_msg)
            return False
        return True

    dispatcher.middleware(rate_limit_guard)

    # 1. Menu, Greeting & Help Commands
    dispatcher.command("help", aliases=["start", "menu", "info", "உதவி", "hi", "hello", "hey", "options", "வணக்கம்", "vanakkam"], description="Show greeting and available options")(handle_help_menu)

    # 2. Daily Quiz & Trivia
    dispatcher.command("quiz", aliases=["trivia", "game", "வினாடி"], description="Play interactive Bible trivia")(handle_quiz_start)
    dispatcher.state("QUIZ_WAITING_ANSWER")(handle_quiz_answer)

    # 3. Scripture Keyword Search
    dispatcher.command("search", aliases=["find", "தேடு"], description="Search scriptures by topic or keyword")(handle_search_command)

    # 4. Christian Hymns & Lyrics
    dispatcher.command("song", aliases=["songs", "lyrics", "hymn", "hymns", "பாடல்"], description="Search Christian song lyrics and hymns")(handle_songs_command)

    # 5. Audio Bible Voice Notes
    dispatcher.command("audio", aliases=["listen", "voice", "கேட்க"], description="Listen to chapter audio notes")(handle_audio_command)

    # 6. Reading Plans, Streak Tracking & Done Checkoffs
    dispatcher.command("plan", aliases=["plans", "reading", "திட்டம்"], description="View reading plans and today's reading")(handle_plan_command)
    dispatcher.command("done", aliases=["read", "check", "முடித்தேன்", "வாசித்துவிட்டேன்"], description="Mark reading portion completed and advance streak")(handle_done_command)
    dispatcher.command("streak", aliases=["progress", "stats", "முன்னேற்றம்", "தொடர்"], description="View reading streak and progress")(handle_streak_command)

    # 7. Shareable Scripture Status Image Cards
    dispatcher.command("card", aliases=["image", "pic", "photo", "status", "படம்"], description="Generate shareable scripture image card for status")(handle_card_command)

    # 8. Language Preference & Bilingual Parallel Mode
    dispatcher.command("lang", aliases=["language", "parallel", "bilingual", "மொழி"], description="Set language (en, ta, or both for parallel)")(handle_language_command)

    # 9. Web Bible Sync Code
    dispatcher.command("sync", aliases=["link", "connect", "இணைப்பு"], description="Generate 15-minute Web Bible sync code")(handle_sync_command)

    # 10. Daily Reminders (Configurable dispatch time, default 5:00 AM)
    dispatcher.command("remind", aliases=["reminder", "time", "alarm", "நேரம்", "நினைவூட்டல்"], description="Set or view daily reminder time (default: 5 AM)")(handle_reminder_command)

    # 11. Subscriptions
    dispatcher.command("subscribe", aliases=["join", "இணை", "பதிவு"], description="Subscribe to daily scripture devotionals")(handle_subscribe)
    dispatcher.command("unsubscribe", aliases=["stop", "cancel", "நிறுத்து"], description="Unsubscribe from daily devotionals")(handle_unsubscribe)

    # 12. Regex Scripture Reference Lookup (e.g., 'John 3:16', 'Genesis 1:1-5', 'Psalm 23', 'யோவான் 3:16')
    scripture_pattern = r"^([1-3]?\s*[a-zA-Z\u0B80-\u0BFF\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$"
    dispatcher.regex(
        pattern=scripture_pattern,
        description="Lookup any Bible passage (e.g., John 3:16, Psalm 23)",
    )(handle_scripture_lookup)

    # 9. Fallback Handler
    dispatcher.fallback(handle_fallback)
