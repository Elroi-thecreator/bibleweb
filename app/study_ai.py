"""
AI Scripture Study Engine: Chapter Overviews, Historical Context & Verse Exegesis.
Provides deep theological commentary, original language insights (Greek / Hebrew),
cross-references, and spiritual applications in bilingual English and Tamil.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ask_bible_ai.config import config as ai_config
from ask_bible_ai.routes import ai_service

logger = logging.getLogger("holy_bible.study_ai")

# In-memory LRU-like caches to avoid repeated LLM calls for the same chapters/verses
_CHAPTER_OVERVIEW_CACHE: Dict[str, Dict[str, Any]] = {}
_VERSE_EXEGESIS_CACHE: Dict[str, Dict[str, Any]] = {}

# =====================================================================
# Curated Biblical Metadata & Overviews for Core Chapters
# =====================================================================

CURATED_BOOK_METADATA: Dict[int, Dict[str, Any]] = {
    1: {  # Genesis
        "author_en": "Moses",
        "author_ta": "மோசே",
        "period": "c. 1446–1406 BC",
        "audience_en": "Israelites preparing to enter the Promised Land",
        "audience_ta": "வாக்குப்பண்ணப்பட்ட தேசத்திற்குள் பிரவேசிக்க ஆயத்தமான இஸ்ரவேலர்",
        "theme_en": "Creation, the Fall, God's Sovereign Election, and Covenant Promises",
        "theme_ta": "சிருஷ்டிப்பு, பாவ வீழ்ச்சி, தேவனுடைய உடன்படிக்கை வாக்குத்தத்தங்கள்",
    },
    19: {  # Psalms
        "author_en": "David, Asaph, Sons of Korah, Moses, and others",
        "author_ta": "தாவீது, ஆசாப், கோராகின் புத்திரர், மோசே மற்றும் பிறர்",
        "period": "c. 1400–450 BC",
        "audience_en": "The worshipping community of Israel",
        "audience_ta": "இஸ்ரவேலின் ஆராதனைச் சமூகம்",
        "theme_en": "Praise, Lament, Trust in God's Faithfulness, and Messianic Hope",
        "theme_ta": "துதி, புலம்பல், தேவனுடைய உண்மைத்துவத்தின் மீதான நம்பிக்கை, மேசியாவின் எதிர்பார்ப்பு",
    },
    20: {  # Proverbs
        "author_en": "King Solomon and other sages",
        "author_ta": "சாலொமோன் ராஜா மற்றும் ஞானிகள்",
        "period": "c. 970–700 BC",
        "audience_en": "Young people and believers seeking practical godliness",
        "audience_ta": "வாலிபர்கள் மற்றும் தேவபக்தியுள்ள வாழ்க்கையைத் தேடும் விசுவாசிகள்",
        "theme_en": "The Fear of the Lord as the Beginning of Wisdom",
        "theme_ta": "கர்த்தருக்குப் பயப்படுதலே ஞானத்தின் ஆரம்பம்",
    },
    23: {  # Isaiah
        "author_en": "Prophet Isaiah son of Amoz",
        "author_ta": "ஆமோத்சின் குமாரனாகிய ஏசாயா தீர்க்கதரிசி",
        "period": "c. 740–680 BC",
        "audience_en": "Judah, Jerusalem, and all nations",
        "audience_ta": "யூதா, எருசலேம் மற்றும் அனைத்து புறஜாதிகள்",
        "theme_en": "The Holy One of Israel, Judgment, and the Suffering Servant Redeemer",
        "theme_ta": "இஸ்ரவேலின் பரிசுத்தர், தேவ நியாயத்தீர்ப்பு மற்றும் பாடுபடும் மேசியா மீட்பர்",
    },
    40: {  # Matthew
        "author_en": "Matthew (Levi), apostle and former tax collector",
        "author_ta": "மத்தேயு (லேவி), அப்போஸ்தலன் மற்றும் வரி வசூலிப்பவர்",
        "period": "c. AD 60–70",
        "audience_en": "Jewish Christians and seekers of the promised Messiah",
        "audience_ta": "யூத கிறிஸ்தவர்கள் மற்றும் வாக்குப்பண்ணப்பட்ட மேசியாவை எதிர்பார்த்த மக்கள்",
        "theme_en": "Jesus as King of the Jews and Fulfillment of Old Testament Prophecy",
        "theme_ta": "இயேசு கிறிஸ்து யூதர்களின் ராஜா மற்றும் பழைய ஏற்பாட்டுத் தீர்க்கதரிசனங்களின் நிறைவேறுதல்",
    },
    43: {  # John
        "author_en": "John the Apostle, the beloved disciple",
        "author_ta": "அப்போஸ்தலனாகிய யோவான் (இயேசுவுக்கு அன்பான சீஷன்)",
        "period": "c. AD 85–95",
        "audience_en": "All believers and seekers across the Greco-Roman world",
        "audience_ta": "உலகெங்கிலும் உள்ள விசுவாசிகள் மற்றும் சத்தியத்தைத் தேடும் மக்கள்",
        "theme_en": "The Deity of Jesus Christ, Eternal Life, and Believing in His Name",
        "theme_ta": "இயேசு கிறிஸ்துவின் தேவத்துவம், நித்திய ஜீவன், அவருடைய நாமத்தின் மீதான விசுவாசம்",
    },
    45: {  # Romans
        "author_en": "Apostle Paul",
        "author_ta": "அப்போஸ்தலனாகிய பவுல்",
        "period": "c. AD 57 from Corinth",
        "audience_en": "The church in Rome (Jewish and Gentile believers)",
        "audience_ta": "ரோமிலுள்ள திருச்சபை (யூத மற்றும் புறஜாதி விசுவாசிகள்)",
        "theme_en": "Justification by Faith, God's Righteousness, and Life in the Spirit",
        "theme_ta": "விசுவாசத்தினால் நீதிமானாக்கப்படுதல், தேவ நீதி மற்றும் ஆவியின் புதிய ஜீவன்",
    },
    66: {  # Revelation
        "author_en": "Apostle John (exiled on the Isle of Patmos)",
        "author_ta": "அப்போஸ்தலனாகிய யோவான் (பத்மு தீவில் சிறைப்பட்டிருந்தபோது)",
        "period": "c. AD 95",
        "audience_en": "The Seven Churches of Asia Minor and the universal Church",
        "audience_ta": "ஆசியாவிலுள்ள ஏழு திருச்சபைகள் மற்றும் அகில உலக சபை",
        "theme_en": "The Ultimate Triumph of the Lamb, Christ's Return, and the New Creation",
        "theme_ta": "ஆட்டுக்குட்டியானவரின் இறுதி வெற்றி, கிறிஸ்துவின் இரண்டாம் வருகை, புதிய வானமும் புதிய பூமியும்",
    },
}


def _get_fallback_chapter_overview(
    book_id: int,
    book_name_en: str,
    book_name_ta: str,
    chapter: int,
    verses: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Generates structured theological overview for any chapter using curated metadata."""
    meta = CURATED_BOOK_METADATA.get(book_id, {
        "author_en": "Inspired Biblical Author",
        "author_ta": "பரிசுத்த ஆவியினால் ஏவப்பட்ட வேதாகம ஆசிரியர்",
        "period": "Biblical Era",
        "audience_en": "God's covenant people and disciples of Christ",
        "audience_ta": "தேவனுடைய உடன்படிக்கையின் மக்கள் மற்றும் கிறிஸ்துவின் சீஷர்கள்",
        "theme_en": "God's Revelation, Holiness, and Covenant Faithfulness",
        "theme_ta": "தேவனுடைய வெளிப்பாடு, பரிசுத்தம் மற்றும் உண்மைத்துவம்",
    })

    verse_count = len(verses) if verses else 30
    title_en = f"Divine Revelation & Covenant Message of {book_name_en} {chapter}"
    title_ta = f"{book_name_ta} {chapter} - தேவ வெளிப்பாடு மற்றும் ஆவிக்குரிய சத்தியங்கள்"

    themes = [
        {
            "theme_en": f"Opening Divine Proclamation (Verses 1–{min(10, verse_count)})",
            "theme_ta": f"தொடக்க இறை பிரகடனம் (வசனங்கள் 1–{min(10, verse_count)})",
            "summary_en": "Establishes God's sovereignty, command, or prophetic narrative calling the audience to attentiveness.",
            "summary_ta": "தேவனுடைய இறையாண்மை, கட்டளை மற்றும் மனிதகுலத்தை விழிப்படையச் செய்யும் அழைப்பு.",
        },
        {
            "theme_en": f"Core Spiritual Conflict & Instruction (Verses {min(11, verse_count)}–{min(20, verse_count)})",
            "theme_ta": f"மைய ஆவிக்குரிய போதனை (வசனங்கள் {min(11, verse_count)}–{min(20, verse_count)})",
            "summary_en": "Addresses the reality of faith, human weakness, and obedience to divine instruction.",
            "summary_ta": "விசுவாசப் போராட்டம், மனித பலவீனம் மற்றும் தேவ கட்டளைகளுக்குக் கீழ்ப்படிதல்.",
        },
        {
            "theme_en": f"Promise of Grace and Restoration (Verses {min(21, verse_count)}–{verse_count})",
            "theme_ta": f"கிருபையின் வாக்குத்தத்தம் (வசனங்கள் {min(21, verse_count)}–{verse_count})",
            "summary_en": "Culminates in an affirmation of God's redemptive power, protection, and eternal covenant.",
            "summary_ta": "தேவனுடைய மீட்பின் வல்லமை, பாதுகாப்பு மற்றும் நித்திய உடன்படிக்கையின் உறுதிப்பாடு.",
        },
    ]

    takeaway_en = (
        f"In {book_name_en} {chapter}, the Holy Spirit calls believers to examine their hearts in light of God's holy word. "
        "Every verse anchors us in the unwavering trustworthiness of God's promises, urging us to walk in faith, prayer, and obedience."
    )
    takeaway_ta = (
        f"{book_name_ta} {chapter}-ல், பரிசுத்த ஆவியானவர் நம்முடைய இருதயங்களை தேவனுடைய பரிசுத்த வார்த்தையின் வெளிச்சத்தில் ஆராய்ந்து பார்க்க அழைக்கிறார். "
        "கர்த்தருடைய வாக்குத்தத்தங்கள் மாறாதவை; நாம் விசுவாசத்தோடும், ஜெபத்தோடும், கீழ்ப்படிதலோடும் வாழ இச்சத்தியங்கள் வழிகாட்டுகின்றன."
    )

    hist = {
        "author_en": meta["author_en"],
        "author_ta": meta["author_ta"],
        "period": meta["period"],
        "audience_purpose_en": meta["audience_en"],
        "audience_purpose_ta": meta["audience_ta"],
        "central_theme_en": meta["theme_en"],
        "central_theme_ta": meta["theme_ta"],
        "en": f"Author: {meta['author_en']}. Period: {meta['period']}. Audience & Purpose: {meta['audience_en']}. Central Theme: {meta['theme_en']}.",
        "ta": f"ஆசிரியர்: {meta['author_ta']}. காலம்: {meta['period']}. நோக்கம்: {meta['audience_ta']}. மையக் கருத்து: {meta['theme_ta']}.",
    }

    return {
        "status": "ok",
        "book_id": book_id,
        "book_name_en": book_name_en,
        "book_name_ta": book_name_ta,
        "chapter": chapter,
        "title_en": title_en,
        "title_ta": title_ta,
        "author": f"{meta['author_en']} ({meta['author_ta']})",
        "date_written": meta["period"],
        "historical_context": hist,
        "key_themes": themes,
        "outline": themes,
        "theological_takeaway_en": takeaway_en,
        "theological_takeaway_ta": takeaway_ta,
        "spiritual_takeaway": {
            "en": takeaway_en,
            "ta": takeaway_ta,
        },
        "mode": "curated",
    }


async def get_chapter_overview_ai(
    book_id: int,
    book_name_en: str,
    book_name_ta: str,
    chapter: int,
    verses: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Retrieves or generates an AI-powered Chapter Overview with historical context,
    thematic outlines, and spiritual takeaways.
    """
    cache_key = f"{book_id}:{chapter}"
    if cache_key in _CHAPTER_OVERVIEW_CACHE:
        return _CHAPTER_OVERVIEW_CACHE[cache_key]

    # If AI service is disabled or in simulation mode, return curated overview
    if not ai_config.enabled or ai_config.simulation_mode or not ai_config.study_ai_enabled:
        result = _get_fallback_chapter_overview(book_id, book_name_en, book_name_ta, chapter, verses)
        _CHAPTER_OVERVIEW_CACHE[cache_key] = result
        return result

    # Build concise prompt for LLM
    verse_sample = ""
    if verses and len(verses) > 0:
        v_lines = [f"{v.get('verse')}: {v.get('text_en', '')[:90]}" for v in verses[:6]]
        verse_sample = "\nSample Verses:\n" + "\n".join(v_lines)

    system_prompt = (
        "You are an expert biblical theologian and historian. Provide a concise, structured chapter overview of the Holy Bible.\n"
        "STRICT RULE: Output ONLY a valid JSON object matching this schema. No markdown fences outside the JSON.\n"
        "{\n"
        '  "title_en": "Short descriptive chapter title in English",\n'
        '  "title_ta": "Short descriptive chapter title in Tamil",\n'
        '  "historical_context": {\n'
        '    "author_en": "Author", "author_ta": "ஆசிரியர்",\n'
        '    "period": "Approximate date or era",\n'
        '    "audience_purpose_en": "Audience & Purpose in English",\n'
        '    "audience_purpose_ta": "நோக்கம் & வாசகர்கள் in Tamil",\n'
        '    "central_theme_en": "Central theme",\n'
        '    "central_theme_ta": "மையக் கருத்து"\n'
        '  },\n'
        '  "key_themes": [\n'
        '    {"theme_en": "Section 1 Title", "theme_ta": "பிரிவு 1 தலைப்பு", "summary_en": "1-2 sentence summary", "summary_ta": "சுருக்கம்"},\n'
        '    {"theme_en": "Section 2 Title", "theme_ta": "பிரிவு 2 தலைப்பு", "summary_en": "1-2 sentence summary", "summary_ta": "சுருக்கம்"},\n'
        '    {"theme_en": "Section 3 Title", "theme_ta": "பிரிவு 3 தலைப்பு", "summary_en": "1-2 sentence summary", "summary_ta": "சுருக்கம்"}\n'
        '  ],\n'
        '  "theological_takeaway_en": "2-3 sentence devotional and spiritual takeaway",\n'
        '  "theological_takeaway_ta": "2-3 sentence devotional takeaway in Tamil"\n'
        "}"
    )

    user_prompt = f"Book: {book_name_en} ({book_name_ta}), Chapter: {chapter}.{verse_sample}"

    try:
        raw_res = await ai_service.client.generate_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=ai_config.model,
            temperature=0.2,
            max_tokens=1024,
        )

        content = raw_res["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content).strip()

        parsed = json.loads(content)
        parsed["status"] = "ok"
        parsed["book_id"] = book_id
        parsed["book_name_en"] = book_name_en
        parsed["book_name_ta"] = book_name_ta
        parsed["chapter"] = chapter
        parsed["mode"] = "live"

        _CHAPTER_OVERVIEW_CACHE[cache_key] = parsed
        return parsed

    except Exception as e:
        logger.warning(f"[StudyAI] Chapter overview LLM generation failed: {e}. Falling back to curated metadata.")
        result = _get_fallback_chapter_overview(book_id, book_name_en, book_name_ta, chapter, verses)
        _CHAPTER_OVERVIEW_CACHE[cache_key] = result
        return result


# =====================================================================
# Curated Famous Verse Exegesis Knowledge Bank
# =====================================================================

CURATED_FAMOUS_VERSES: Dict[str, Dict[str, Any]] = {
    "43:3:16": {  # John 3:16
        "word_insights": [
            {
                "word": "Agapēsen (ἠγάπησεν)",
                "language": "Koine Greek",
                "meaning_en": "Unconditional, sacrificial divine love that gives without expecting repayment.",
                "meaning_ta": "எந்த பிரதிபலனும் எதிர்பாராத, தியாகமும் சுயநலமற்றதுமான இறை அன்பு.",
            },
            {
                "word": "Monogenē (μονογενῆ)",
                "language": "Koine Greek",
                "meaning_en": "Unique, one-of-a-kind, eternally begotten Son of the same divine essence.",
                "meaning_ta": "ஒரே தன்மை கொண்ட, பிதாவுக்கு இணையான ஒரேபேறான குமாரன்.",
            },
        ],
        "cross_refs": [
            {"ref": "Romans 5:8", "note_en": "God demonstrates His own love toward us in that while we were sinners, Christ died for us."},
            {"ref": "1 John 4:9-10", "note_en": "In this the love of God was manifested, that He sent His only begotten Son into the world."},
        ],
        "application_en": "Salvation is entirely by grace through faith in Jesus Christ. No sin is greater than God's redeeming love.",
        "application_ta": "இரட்சிப்பு என்பது விசுவாசத்தினால் மட்டுமே கிடைக்கிற கிருபையின் ஈவு. தேவனுடைய மாறாத அன்பை உணர்ந்து அனுதினமும் அவரில் நிலைத்திருக்க வேண்டும்.",
        "prayer_en": "Heavenly Father, thank You for loving me so deeply that You gave Your only begotten Son. Help me to trust You completely today. Amen.",
        "prayer_ta": "பரலோக பிதாவே, உம்முடைய ஒரேபேறான குமாரனைத் தரும் அளவிற்கு என்னை நேசித்த உம்முடைய அன்பிற்காக நன்றி. விசுவாசத்தோடு வாழ எனக்கு அருள்தாரும். ஆமென்.",
    },
    "19:23:1": {  # Psalm 23:1
        "word_insights": [
            {
                "word": "Yahweh Rohi (יְהוָה רֹעִי)",
                "language": "Biblical Hebrew",
                "meaning_en": "The LORD is my personal Shepherd who tends, guides, and protects His flock.",
                "meaning_ta": "கர்த்தர் என்னை வழிநடத்தி, பாதுகாத்து, பராமரிக்கும் என் சொந்த மேய்ப்பர்.",
            },
            {
                "word": "Lo Echsar (לֹא אֶחְסָר)",
                "language": "Biblical Hebrew",
                "meaning_en": "I lack nothing necessary for life and godliness; complete spiritual sufficiency.",
                "meaning_ta": "எனக்கு எவ்வித நன்மையும் குறையாது; ஆவிக்குரிய முழுமையான திருப்தி.",
            },
        ],
        "cross_refs": [
            {"ref": "John 10:11", "note_en": "Jesus declared: 'I am the good shepherd. The good shepherd gives His life for the sheep.'"},
            {"ref": "Philippians 4:19", "note_en": "My God shall supply all your need according to His riches in glory by Christ Jesus."},
        ],
        "application_en": "Because God is our loving shepherd, we can let go of anxiety and rest in His daily provision and sovereign guidance.",
        "application_ta": "கர்த்தரே நமது மேய்ப்பராய் இருப்பதால், எதிர்காலத்தைக் குறித்த பயத்தை நீக்கி, அவருடைய பராமரிப்பில் மன அமைதியோடு வாழலாம்.",
        "prayer_en": "Lord Jesus, my Good Shepherd, thank You for caring for my soul. Lead me beside still waters and renew my strength. Amen.",
        "prayer_ta": "நல்ல மேய்ப்பராகிய இயேசுவே, என்னை வழிநடத்தி போஷிப்பதற்காக நன்றி. அமர்ந்த தண்ணீர்கள் அருகே என்னை நடத்தி, என் ஆத்துமாவைத் தேற்றும். ஆமென்.",
    },
    "45:8:28": {  # Romans 8:28
        "word_insights": [
            {
                "word": "Synergei (συνεργεῖ)",
                "language": "Koine Greek",
                "meaning_en": "Works together harmoniously, weaving every triumph and trial into God's sovereign masterpiece.",
                "meaning_ta": "அனைத்தையும் ஒன்றாக இணைத்து, நன்மையாக மாற்றும் தேவனுடைய இறையாண்மை வல்லமை.",
            },
            {
                "word": "Agathon (ἀγαθόν)",
                "language": "Koine Greek",
                "meaning_en": "Ultimate, eternal spiritual good (conforming believers into the image of Christ).",
                "meaning_ta": "கிறிஸ்துவின் சாயலுக்கு ஒப்பாக நம்மை மாற்றும் நித்திய ஆவிக்குரிய நன்மை.",
            },
        ],
        "cross_refs": [
            {"ref": "Genesis 50:20", "note_en": "Joseph said: 'You meant evil against me, but God meant it for good.'"},
            {"ref": "Jeremiah 29:11", "note_en": "'For I know the plans I have for you,' declares the Lord, 'plans for peace and not for evil.'"},
        ],
        "application_en": "Even when going through difficult or confusing valleys, God never wastes our tears. He weaves every circumstance for our spiritual growth.",
        "application_ta": "கடினமான சூழ்நிலைகள் வழியாக நாம் கடந்து சென்றாலும், தேவன் நம்முடைய வேதனைகளை வீணாக்குவதில்லை; அனைத்தையும் நமது ஆவிக்குரிய நன்மைக்கேதுவாக மாற்றுகிறார்.",
        "prayer_en": "Sovereign Lord, when I cannot see the path ahead, help me trust that You are working all things for my good and Your glory. Amen.",
        "prayer_ta": "சர்வவல்லமையுள்ள ஆண்டவரே, சூழ்நிலைகள் புரியாதபோதும், நீர் அனைத்தையும் நன்மைக்கு ஏதுவாக நடத்துகிறீர் என்று உம்மை முழுமையாக நம்புகிறேன். ஆமென்.",
    },
}


def _get_fallback_verse_exegesis(
    book_id: int,
    book_name_en: str,
    book_name_ta: str,
    chapter: int,
    verse: int,
    text_en: str,
    text_ta: str,
) -> Dict[str, Any]:
    """Provides structured theological exegesis and linguistic insights with grounded fallback."""
    key = f"{book_id}:{chapter}:{verse}"
    curated = CURATED_FAMOUS_VERSES.get(key)

    ref_en = f"{book_name_en} {chapter}:{verse}"
    ref_ta = f"{book_name_ta} {chapter}:{verse}"

    if curated:
        return {
            "status": "ok",
            "reference_en": ref_en,
            "reference_ta": ref_ta,
            "text_en": text_en,
            "text_ta": text_ta,
            "literary_context_en": f"Situated in the sacred context of {book_name_en} chapter {chapter}, this passage highlights foundational biblical doctrine.",
            "literary_context_ta": f"{book_name_ta} அதிகாரம் {chapter}-ன் வரலாற்றுப் பின்னணியில் அமைந்துள்ள இவ்வசனம், விசுவாசத்தின் அடிப்படை சத்தியத்தை வெளிப்படுத்துகிறது.",
            "literary_and_theological_context": {
                "en": f"Situated in the sacred context of {book_name_en} chapter {chapter}, this passage highlights foundational biblical doctrine.",
                "ta": f"{book_name_ta} அதிகாரம் {chapter}-ன் வரலாற்றுப் பின்னணியில் அமைந்துள்ள இவ்வசனம், விசுவாசத்தின் அடிப்படை சத்தியத்தை வெளிப்படுத்துகிறது.",
            },
            "original_language_insights": curated["word_insights"],
            "original_language": {
                "language": curated["word_insights"][0].get("language", "Koine Greek") if curated["word_insights"] else "Koine Greek",
                "terms": curated["word_insights"],
            },
            "cross_references": [
                {
                    "ref": cr.get("ref", ""),
                    "reference": cr.get("ref", ""),
                    "note_en": cr.get("note_en", ""),
                    "explanation_en": cr.get("note_en", ""),
                }
                for cr in curated["cross_refs"]
            ],
            "spiritual_application_en": curated["application_en"],
            "spiritual_application_ta": curated["application_ta"],
            "practical_application": {
                "en": curated["application_en"],
                "ta": curated["application_ta"],
            },
            "prayer_en": curated["prayer_en"],
            "prayer_ta": curated["prayer_ta"],
            "guided_prayer": {
                "en": curated["prayer_en"],
                "ta": curated["prayer_ta"],
            },
            "mode": "curated",
        }

    # Universal theological exegesis generator
    lang_name = "Koine Greek" if book_id >= 40 else "Biblical Hebrew"
    lit_en = (
        f"This verse forms a pivotal moment in {ref_en}. It reveals God's divine character, "
        "instruction for righteousness, and the covenant bond between God and His people."
    )
    lit_ta = (
        f"இவ்வசனம் {ref_ta}-ல் மிக முக்கியமான தேவ வெளிப்பாடாக அமைந்துள்ளது. "
        "தேவனுடைய பரிசுத்த சுபாவத்தையும், மனிதகுலத்தின் மீது அவர் கொண்டுள்ள மாறாத அன்பையும் இது சுட்டிக்காட்டுகிறது."
    )
    app_en = (
        "Meditate on this verse today by applying it directly to your thoughts and decisions. "
        "Allow the Holy Spirit to transform your perspective through God's eternal truth."
    )
    app_ta = (
        "இவ்வசனத்தை அனுதின வாழ்க்கையில் சிந்தித்து, தேவனுடைய சித்தத்திற்கு உங்களை ஒப்புக்கொடுங்கள். "
        "பரிசுத்த ஆவியானவர் உங்கள் சிந்தனைகளை தேவ வார்த்தையினால் மறுரூபப்படுத்துவாராக."
    )
    pray_en = f"Lord God, thank You for the living truth in {ref_en}. Open my eyes to understand Your word and walk in Your ways. Amen."
    pray_ta = f"அன்பின் பரலோக பிதாவே, {ref_ta} வசனத்தின் ஜீவனுள்ள வார்த்தைகளுக்காக நன்றி. உம்முடைய வசனத்தின்படி வாழ எனக்கு கிருபை தாரும். ஆமென்."
    terms = [
        {
            "word": "Covenant Term",
            "language": lang_name,
            "meaning_en": "Carries deep biblical authority, faithfulness (Emunah / Pistis), and divine truth (Alētheia).",
            "meaning_ta": "வேதாகம உடன்படிக்கையின் உண்மைத்துவத்தையும், தெய்வீக சத்தியத்தையும் குறிக்கிறது.",
        }
    ]
    xrefs = [
        {"ref": "Psalm 119:105", "reference": "Psalm 119:105", "note_en": "Your word is a lamp to my feet and a light to my path.", "explanation_en": "Your word is a lamp to my feet and a light to my path."},
        {"ref": "2 Timothy 3:16", "reference": "2 Timothy 3:16", "note_en": "All Scripture is given by inspiration of God, and is profitable for doctrine.", "explanation_en": "All Scripture is given by inspiration of God, and is profitable for doctrine."},
    ]

    return {
        "status": "ok",
        "reference_en": ref_en,
        "reference_ta": ref_ta,
        "text_en": text_en,
        "text_ta": text_ta,
        "literary_context_en": lit_en,
        "literary_context_ta": lit_ta,
        "literary_and_theological_context": {
            "en": lit_en,
            "ta": lit_ta,
        },
        "original_language_insights": terms,
        "original_language": {
            "language": lang_name,
            "terms": terms,
        },
        "cross_references": xrefs,
        "spiritual_application_en": app_en,
        "spiritual_application_ta": app_ta,
        "practical_application": {
            "en": app_en,
            "ta": app_ta,
        },
        "prayer_en": pray_en,
        "prayer_ta": pray_ta,
        "guided_prayer": {
            "en": pray_en,
            "ta": pray_ta,
        },
        "mode": "curated",
    }


async def get_verse_exegesis_ai(
    book_id: int,
    book_name_en: str,
    book_name_ta: str,
    chapter: int,
    verse: int,
    text_en: str,
    text_ta: str,
) -> Dict[str, Any]:
    """
    Generates in-depth verse-by-verse theological exegesis, linguistic root analysis,
    cross-references, and devotional application.
    """
    cache_key = f"{book_id}:{chapter}:{verse}"
    if cache_key in _VERSE_EXEGESIS_CACHE:
        return _VERSE_EXEGESIS_CACHE[cache_key]

    # If AI service is disabled or in simulation mode, return curated exegesis
    if not ai_config.enabled or ai_config.simulation_mode or not ai_config.study_ai_enabled:
        result = _get_fallback_verse_exegesis(book_id, book_name_en, book_name_ta, chapter, verse, text_en, text_ta)
        _VERSE_EXEGESIS_CACHE[cache_key] = result
        return result

    ref_en = f"{book_name_en} {chapter}:{verse}"
    ref_ta = f"{book_name_ta} {chapter}:{verse}"
    original_lang = "Koine Greek" if book_id >= 40 else "Biblical Hebrew"

    system_prompt = (
        "You are an expert Bible scholar, linguist, and pastoral theologian. Provide an in-depth verse exegesis.\n"
        "STRICT RULE: Output ONLY a valid JSON object matching this schema. No conversational preamble or code blocks outside the JSON.\n"
        "{\n"
        '  "literary_context_en": "2-3 sentences explaining immediate context within chapter",\n'
        '  "literary_context_ta": "அதிகாரப் பின்னணி மற்றும் சூழல் விளக்கம் (2-3 sentences)",\n'
        '  "original_language_insights": [\n'
        f'    {{"word": "Transliterated original word", "language": "{original_lang}", "meaning_en": "Deep linguistic and theological meaning", "meaning_ta": "மூல மொழி விளக்கம்"}}\n'
        '  ],\n'
        '  "cross_references": [\n'
        '    {"ref": "Book Chapter:Verse", "note_en": "How this connects to the verse", "note_ta": "இணைப்பு விளக்கம்"},\n'
        '    {"ref": "Book Chapter:Verse", "note_en": "How this connects to the verse", "note_ta": "இணைப்பு விளக்கம்"}\n'
        '  ],\n'
        '  "spiritual_application_en": "2-3 sentences practical Christian application",\n'
        '  "spiritual_application_ta": "அனுதின கிறிஸ்தவ வாழ்க்கைக்கான ஆவிக்குரிய பிரயோகம்",\n'
        '  "prayer_en": "Short, reverent closing prayer",\n'
        '  "prayer_ta": "சமர்ப்பண ஜெபம்"\n'
        "}"
    )

    user_prompt = (
        f"Scripture Reference: {ref_en} ({ref_ta})\n"
        f"English Text: {text_en}\n"
        f"Tamil Text: {text_ta}"
    )

    try:
        raw_res = await ai_service.client.generate_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=ai_config.model,
            temperature=0.2,
            max_tokens=1024,
        )

        content = raw_res["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content).strip()

        parsed = json.loads(content)
        parsed["status"] = "ok"
        parsed["reference_en"] = ref_en
        parsed["reference_ta"] = ref_ta
        parsed["text_en"] = text_en
        parsed["text_ta"] = text_ta
        parsed["mode"] = "live"

        _VERSE_EXEGESIS_CACHE[cache_key] = parsed
        return parsed

    except Exception as e:
        logger.warning(f"[StudyAI] Verse exegesis LLM generation failed: {e}. Falling back to curated exegesis.")
        result = _get_fallback_verse_exegesis(book_id, book_name_en, book_name_ta, chapter, verse, text_en, text_ta)
        _VERSE_EXEGESIS_CACHE[cache_key] = result
        return result
