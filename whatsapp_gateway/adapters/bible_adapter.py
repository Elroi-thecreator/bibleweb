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
from app.plans_data import READING_PLANS
from app.quiz_data import QUIZ_QUESTIONS
from whatsapp_gateway.bot.context import MessageContext
from whatsapp_gateway.bot.dispatcher import BotDispatcher
from whatsapp_gateway.subscribers import add_subscriber, remove_subscriber, is_subscribed

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
            primary_text = v.get("text_ta") if is_tamil else v.get("text_en")
            secondary_text = v.get("text_en") if is_tamil else v.get("text_ta")
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
            txt = v.get("text_ta") if is_tamil else v.get("text_en")
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


async def handle_plan_command(ctx: MessageContext) -> None:
    """View today's reading plan or explore available plans."""
    today_day_of_month = datetime.now().day

    prov_plan = READING_PLANS.get("proverbs-31", {})
    prov_days = prov_plan.get("days", [])
    today_prov = prov_days[today_day_of_month - 1] if today_day_of_month <= len(prov_days) else None

    lines = [
        "📅 *Daily Scripture Reading Plan:*",
        f"Today is Day {today_day_of_month} of the month.",
        "",
    ]

    if today_prov:
        lines.append(f"✨ *Today's Wisdom Reading:* {today_prov['ref']}")
        lines.append(f"_Reply 'Proverbs {today_day_of_month}' to read today's chapter!_")
        lines.append("")

    lines.append("*Available Reading Plans:*")
    for p_id, p_meta in READING_PLANS.items():
        lines.append(f"• *{p_meta.get('title_en')}* ({p_meta.get('total_days')} Days)")

    await ctx.reply_text("\n\n".join(lines))


async def handle_subscribe(ctx: MessageContext) -> None:
    """Subscribes the user to daily scripture devotionals."""
    is_ta = is_tamil_text(ctx.text)
    lang = "ta" if is_ta else "en"
    success = await add_subscriber(
        phone=ctx.sender,
        name=ctx.sender_name,
        language=lang,
        plan_id="proverbs-31",
    )
    if success:
        if is_ta:
            await ctx.reply_text(
                "✅ *தினசரி வேதாகம பகிர்வில் இணைந்ததற்கு நன்றி!*\n\n"
                "ஒவ்வொரு நாளும் உங்கள் வாட்ஸ்அப்பிற்கு தினசரி வசனம் மற்றும் வாசிப்புத் திட்டம் அனுப்பப்படும்.\n"
                "விலக விரும்பினால் *stop* என அனுப்பவும்."
            )
        else:
            await ctx.reply_text(
                "✅ *Subscribed to Daily Scripture Devotionals!*\n\n"
                "You will receive each day's scripture reading directly on WhatsApp.\n"
                "Reply *stop* anytime to unsubscribe."
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
    """Handles audio voice note generation (e.g. 'audio John 3' or 'listen Psalm 23')."""
    parts = ctx.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await ctx.reply_text("🎧 *Usage*: `audio <book> <chapter>` (e.g. `audio John 3` or `listen Psalm 23`)")
        return

    raw_book = parts[1]
    raw_chapter = parts[2]
    if not raw_chapter.isdigit():
        await ctx.reply_text("❌ Chapter must be a valid number (e.g. `audio John 3`).")
        return

    chapter = int(raw_chapter)
    book_id = resolve_book_id(raw_book)
    if not book_id:
        await ctx.reply_text(f"❌ Book '{raw_book}' not recognized.")
        return

    book_meta = CATHOLIC_BOOK_MAP.get(book_id, BOOK_MAP.get(book_id))
    verses = await asyncio.to_thread(get_chapter_verses, book_id, chapter)
    if not verses:
        await ctx.reply_text("❌ No chapter text available for audio playback.")
        return

    scripture_text = " ".join([v.get("text_en") or "" for v in verses[:5]])
    caption = f"🎧 Audio Bible: {book_meta['name_en']} {chapter}:1-5"

    try:
        from gtts import gTTS
        fp = io.BytesIO()
        tts = gTTS(text=scripture_text, lang="en")
        await asyncio.to_thread(tts.write_to_fp, fp)
        audio_bytes = fp.getvalue()

        await ctx.reply_audio(
            file_path_or_bytes=audio_bytes,
            caption=caption,
            ptt=True,
            file_name=f"{book_meta['name_en']}_{chapter}.mp3",
        )
    except Exception as exc:
        logger.error("TTS audio generation error: %s", exc)
        await ctx.reply_text(f"⚠️ Could not generate audio clip: {exc}")


async def handle_help_menu(ctx: MessageContext) -> None:
    """Displays the branded Holy Bible WhatsApp Assistant menu."""
    is_ta = is_tamil_text(ctx.text)
    if is_ta:
        menu = (
            "🕊️ *வேதாகம வாட்ஸ்அப் உதவியாளருக்கு வரவேற்கிறோம்!* 🕊️\n\n"
            "📖 *வேத வாசிப்பு:*\n"
            "• `யோவான் 3:16`, `சங்கீதம் 23`, `ஆதியாகமம் 1:1-5`\n"
            "• கத்தோலிக்க திருமுறை: `தோபித்து 4:7`, `சீராக் 2:1`\n\n"
            "🔍 *தேடுதல்:*\n"
            "• `search <வார்த்தை>` (எ.கா. `search விசுவாசம்`)\n\n"
            "❓ *வினாடி வினா:*\n"
            "• `quiz` (வேதாகம வினாடி வினா விளையாட)\n\n"
            "🔔 *தினசரி பகிர்வு:*\n"
            "• `subscribe` (தினசரி வசனங்களை வாட்ஸ்அப்பில் பெற)\n"
            "• `stop` (விலக)\n\n"
            "🎵 *பாடல்கள்:*\n"
            "• `song <எண்/தலைப்பு>` (எ.கா. `song 2281`)\n\n"
            "_தொடங்க மேலே உள்ள ஏதேனும் ஒரு கட்டளையை அனுப்பவும்!_"
        )
    else:
        menu = (
            "🕊️ *Welcome to Holy Bible WhatsApp Assistant!* 🕊️\n\n"
            "Here is what you can do:\n\n"
            "📖 *Scripture Lookup:*\n"
            "• Text any passage: `John 3:16`, `Genesis 1:1-5`, `Psalm 23`\n"
            "• Catholic canon included: `Tobit 4:7`, `Sirach 2:1`\n\n"
            "🔍 *Scripture Search:*\n"
            "• `search <keyword>` (e.g. `search love`, `search grace`)\n\n"
            "🎧 *Audio Bible Clips:*\n"
            "• `audio <book> <chapter>` (e.g. `audio John 3`)\n\n"
            "❓ *Bible Trivia / Quiz:*\n"
            "• `quiz` (test your scripture knowledge)\n\n"
            "🔔 *Daily Devotional Subscription:*\n"
            "• `subscribe` (receive daily scripture & reading plan)\n"
            "• `stop` (unsubscribe anytime)\n\n"
            "🎵 *Hymns & Lyrics:*\n"
            "• `song <title/ID>` (e.g. `song Amazing Grace`)\n\n"
            "📅 *Reading Plans:*\n"
            "• `plan` (view today's assigned chapter)\n\n"
            "_Send any command or scripture citation above to begin!_"
        )
    await ctx.reply_text(menu)


async def handle_fallback(ctx: MessageContext) -> None:
    """Graceful fallback when input does not match commands or scripture citations."""
    text = ctx.text.strip()
    if text.lower() in ("hi", "hello", "hey", "vanakkam", "வணக்கம்", "praise the lord", "shalom"):
        await handle_help_menu(ctx)
        return

    await ctx.reply_text(
        f"🤔 I didn't recognize: *\"{text[:40]}\"*\n\n"
        "Try sending a scripture reference like *John 3:16* or type *help* to see all available commands!"
    )


def register_bible_handlers(dispatcher: BotDispatcher) -> None:
    """Registers all Holy Bible domain handlers with the decoupled BotDispatcher."""
    # 1. Menu & Help Commands
    dispatcher.command("help", aliases=["start", "menu", "info", "உதவி"], description="Show available features and instructions")(handle_help_menu)

    # 2. Daily Quiz & Trivia
    dispatcher.command("quiz", aliases=["trivia", "game", "வினாடி"], description="Play interactive Bible trivia")(handle_quiz_start)
    dispatcher.state("QUIZ_WAITING_ANSWER")(handle_quiz_answer)

    # 3. Scripture Keyword Search
    dispatcher.command("search", aliases=["find", "தேடு"], description="Search scriptures by topic or keyword")(handle_search_command)

    # 4. Christian Hymns & Lyrics
    dispatcher.command("song", aliases=["songs", "lyrics", "hymn", "hymns", "பாடல்"], description="Search Christian song lyrics and hymns")(handle_songs_command)

    # 5. Audio Bible Voice Notes
    dispatcher.command("audio", aliases=["listen", "voice", "கேட்க"], description="Listen to chapter audio notes")(handle_audio_command)

    # 6. Reading Plans
    dispatcher.command("plan", aliases=["plans", "reading", "திட்டம்"], description="View reading plans and today's reading")(handle_plan_command)

    # 7. Subscriptions
    dispatcher.command("subscribe", aliases=["join", "இணை", "பதிவு"], description="Subscribe to daily scripture devotionals")(handle_subscribe)
    dispatcher.command("unsubscribe", aliases=["stop", "cancel", "நிறுத்து"], description="Unsubscribe from daily devotionals")(handle_unsubscribe)

    # 8. Regex Scripture Reference Lookup (e.g., 'John 3:16', 'Genesis 1:1-5', 'Psalm 23', 'யோவான் 3:16')
    scripture_pattern = r"^([1-3]?\s*[a-zA-Z\u0B80-\u0BFF\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$"
    dispatcher.regex(
        pattern=scripture_pattern,
        description="Lookup any Bible passage (e.g., John 3:16, Psalm 23)",
    )(handle_scripture_lookup)

    # 9. Fallback Handler
    dispatcher.fallback(handle_fallback)
