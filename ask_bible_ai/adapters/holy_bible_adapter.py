"""
Holy Bible SQLite Grounding Adapter for Ask Bible AI.
Bridges the decoupled `BaseGroundingProvider` interface to the local Holy Bible SQLite database.
Performs:
1. Regex citation extraction (e.g., 'John 3:16', 'யோவான் 3:16', 'Ps 23:1')
2. Full-text search (FTS5) fallback across both Tamil and English scripture corpora.
3. Completely asynchronous execution using `asyncio.to_thread` per DEV-PY-001.
"""

import asyncio
import re
from typing import Dict, List, Optional
from ask_bible_ai.grounding import BaseGroundingProvider, GroundingPassage

# Canonical English and Tamil book mapping
TAMIL_BOOK_MAP = {
    "ஆதியாகமம்": (1, "Genesis"),
    "யாத்திராகமம்": (2, "Exodus"),
    "லேவியராகமம்": (3, "Leviticus"),
    "எண்ணாகமம்": (4, "Numbers"),
    "உபாகமம்": (5, "Deuteronomy"),
    "யோசுவா": (6, "Joshua"),
    "நியாயாதிபதிகள்": (7, "Judges"),
    "ரூத்": (8, "Ruth"),
    "1 சாமுவேல்": (9, "1 Samuel"),
    "2 சாமுவேல்": (10, "2 Samuel"),
    "1 இராஜாக்கள்": (11, "1 Kings"),
    "2 இராஜாக்கள்": (12, "2 Kings"),
    "1 நாளாகமம்": (13, "1 Chronicles"),
    "2 நாளாகமம்": (14, "2 Chronicles"),
    "எஸ்றா": (15, "Ezra"),
    "நெகேமியா": (16, "Nehemiah"),
    "எஸ்தர்": (17, "Esther"),
    "யோபு": (18, "Job"),
    "சங்கீதம்": (19, "Psalm"),
    "நீதிமொழிகள்": (20, "Proverbs"),
    "பிரசங்கி": (21, "Ecclesiastes"),
    "உன்னதப்பாட்டு": (22, "Song of Solomon"),
    "ஏசாயா": (23, "Isaiah"),
    "எரேமியா": (24, "Jeremiah"),
    "புலம்பல்": (25, "Lamentations"),
    "எசேக்கியேல்": (26, "Ezekiel"),
    "தானியேல்": (27, "Daniel"),
    "ஓசியா": (28, "Hosea"),
    "யோவேல்": (29, "Joel"),
    "ஆமோஸ்": (30, "Amos"),
    "ஒபதியா": (31, "Obadiah"),
    "யோனா": (32, "Jonah"),
    "மீகா": (33, "Micah"),
    "நாகூம்": (34, "Nahum"),
    "அபகூக்": (35, "Habakkuk"),
    "செப்பனியா": (36, "Zephaniah"),
    "ஆகாய்": (37, "Haggai"),
    "சகரியா": (38, "Zechariah"),
    "மல்கியா": (39, "Malachi"),
    "மத்தேயு": (40, "Matthew"),
    "மாற்கு": (41, "Mark"),
    "லூக்கா": (42, "Luke"),
    "யோவான்": (43, "John"),
    "அப்போஸ்தலர்": (44, "Acts"),
    "ரோமர்": (45, "Romans"),
    "1 கொரிந்தியர்": (46, "1 Corinthians"),
    "2 கொரிந்தியர்": (47, "2 Corinthians"),
    "கலாத்தியர்": (48, "Galatians"),
    "எபேசியர்": (49, "Ephesians"),
    "பிலிப்பியர்": (50, "Philippians"),
    "கொலோசெயர்": (51, "Colossians"),
    "1 தெசலோனிக்கேயர்": (52, "1 Thessalonians"),
    "2 தெசலோனிக்கேயர்": (53, "2 Thessalonians"),
    "1 தீமோத்தேயு": (54, "1 Timothy"),
    "2 தீமோத்தேயு": (55, "2 Timothy"),
    "தீத்து": (56, "Titus"),
    "பிலேமோன்": (57, "Philemon"),
    "எபிரெயர்": (58, "Hebrews"),
    "யாக்கோபு": (59, "James"),
    "1 பேதுரு": (60, "1 Peter"),
    "2 பேதுரு": (61, "2 Peter"),
    "1 யோவான்": (62, "1 John"),
    "2 யோவான்": (63, "2 John"),
    "3 யோவான்": (64, "3 John"),
    "யூதா": (65, "Jude"),
    "வெளிப்படுத்தின விசேஷம்": (66, "Revelation"),
    "வெளிப்படுத்தல்": (66, "Revelation"),
}

# Regex to capture citations like "John 3:16", "1 John 1:9", "சங்கீதம் 23:1", "ரோமர் 8:28"
CITATION_REGEX = re.compile(
    r"\b([1-3]?\s*[A-Za-z\u0B80-\u0BFF]+)\s+(\d{1,3}):(\d{1,3})(?:-(\d{1,3}))?\b"
)


class HolyBibleGroundingAdapter(BaseGroundingProvider):
    """
    Adapter implementing BaseGroundingProvider backed by Holy Bible's dual-corpus SQLite DB.
    """

    def __init__(self):
        try:
            from app.db import search_verses, get_chapter_verses, BOOK_MAP, CATHOLIC_BOOK_MAP
            self._search_verses = search_verses
            self._get_chapter_verses = get_chapter_verses
            self._book_map = BOOK_MAP
            self._catholic_map = CATHOLIC_BOOK_MAP
            self._available = True
        except ImportError:
            self._available = False

    async def retrieve_context(
        self,
        query: str,
        language: str = "auto",
        max_passages: int = 4,
    ) -> List[GroundingPassage]:
        if not self._available:
            return []

        passages: List[GroundingPassage] = []

        # 1. First, check if specific chapter & verse citations are mentioned directly in query
        citations = self._extract_citations(query)
        if citations:
            for book_id, book_name, ch, v_start, v_end in citations[:max_passages]:
                verses = await asyncio.to_thread(self._get_chapter_verses, book_id, ch)
                for v in verses:
                    v_num = v.get("verse", 0)
                    if v_start <= v_num <= v_end:
                        passages.append(
                            GroundingPassage(
                                reference=f"{book_name} {ch}:{v_num}",
                                text_en=v.get("text_en") or v.get("text_en_drb"),
                                text_ta=v.get("text_ta") or v.get("text_ta_poc"),
                                book=book_name,
                                chapter=ch,
                                verse=v_num,
                                relevance_score=2.0,
                            )
                        )
                        if len(passages) >= max_passages:
                            return passages

        # 2. If no direct citations or need more context, execute FTS5 scripture search
        remaining = max_passages - len(passages)
        if remaining > 0:
            tokens = self._extract_search_tokens(query)
            for token in tokens:
                if len(passages) >= max_passages:
                    break
                results = await asyncio.to_thread(
                    self._search_verses,
                    token,
                    canon="catholic",
                    limit=max_passages - len(passages),
                )
                for r in results:
                    book_title = r.get('book_name_en') or r.get('book_name') or ''
                    ref = f"{book_title} {r.get('chapter', 1)}:{r.get('verse', 1)}"
                    if not any(p.reference == ref for p in passages):
                        passages.append(
                            GroundingPassage(
                                reference=ref,
                                text_en=r.get("text_en") or r.get("text_en_drb"),
                                text_ta=r.get("text_ta") or r.get("text_ta_poc"),
                                book=book_title,
                                chapter=r.get("chapter"),
                                verse=r.get("verse"),
                                relevance_score=1.0,
                            )
                        )

        return passages[:max_passages]

    def _extract_citations(self, text: str) -> List[tuple]:
        """Parses scripture citations from query text."""
        citations = []
        for match in CITATION_REGEX.finditer(text):
            raw_book = match.group(1).strip()
            ch = int(match.group(2))
            v_start = int(match.group(3))
            v_end = int(match.group(4)) if match.group(4) else v_start

            # Resolve book name
            book_id, canon_name = self._resolve_book(raw_book)
            if book_id:
                citations.append((book_id, canon_name, ch, v_start, v_end))
        return citations

    def _resolve_book(self, raw_book: str) -> tuple:
        """Resolves raw English or Tamil book string to (book_id, canonical_name)."""
        normalized = raw_book.strip()

        # Check Tamil book map
        if normalized in TAMIL_BOOK_MAP:
            bid, name = TAMIL_BOOK_MAP[normalized]
            return bid, name

        # Check English map (case-insensitive) or Tamil name
        norm_lower = normalized.lower().replace(".", "")
        for bid, info in self._book_map.items():
            if info.get("name_en", "").lower() == norm_lower or info.get("name_ta") == normalized:
                return bid, info.get("name_en")

        # Check Catholic books
        for bid, info in self._catholic_map.items():
            if info.get("name_en", "").lower() == norm_lower or info.get("name_ta") == normalized:
                return bid, info.get("name_en")

        return None, None

    def _extract_search_tokens(self, query: str) -> List[str]:
        """Extracts core topical keywords while stripping common filler words."""
        # Strip punctuation
        cleaned = re.sub(r'[^\w\s\u0B80-\u0BFF]', ' ', query)
        stop_words = {
            "what", "does", "the", "bible", "say", "about", "how", "to", "in", "is",
            "are", "why", "who", "when", "where", "tell", "me", "explain", "meaning",
            "of", "for", "and", "or", "with", "a", "an", "on", "by", "வேதாகமம்", "கூறுகிறது",
            "பற்றி", "என்ன", "எப்படி", "விளக்கு", "அர்த்தம்"
        }
        tokens = [t for t in cleaned.split() if t.lower() not in stop_words and len(t) > 2]
        return tokens[:4]
