"""
Ask Bible AI Prompt Engineering & Bilingual Orchestration.
Defines system instructions, theological guardrails, and context assembly.
Supports automatic Tamil / English language intelligence.
"""

import re
from typing import List, Optional
from ask_bible_ai.grounding import GroundingPassage


def detect_language(text: str) -> str:
    """Detects whether text contains Tamil characters (Unicode block U+0B80 - U+0BFF)."""
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "ta"
    return "en"


DEFAULT_SYSTEM_PROMPT = """You are "Ask Bible AI", a compassionate, scholarly, and spiritually uplifting biblical assistant.
Your mission is to help believers, seekers, and students of the Bible understand Holy Scripture deeply.

CORE GUIDELINES:
1. SCRIPTURE FIDELITY: Ground every answer in the Holy Bible. Quote chapter and verse citations accurately (e.g., John 3:16, Matthew 5:3-10, சங்கீதம் 23:1).
2. NEVER HALLUCINATE: Never invent, alter, or misattribute scripture verses. If you are uncertain of a specific citation, state that clearly.
3. GROUNDING CONTEXT: When verified scripture passages are provided in the [SCRIPTURE CONTEXT] section, prioritize them directly in your response.
4. CANONICAL RESPECT: Acknowledge both Protestant (66 books) and Catholic (73 books including Deuterocanonical books like Tobit, Judith, Wisdom, Sirach, Baruch, 1-2 Maccabees) canons when historical or textual differences arise.
5. BILINGUAL CAPABILITY:
   - If the user asks in Tamil (தமிழ்), reply primarily in natural, reverent, grammatically sound Tamil, including Tamil scripture verses and English reference brackets.
   - If the user asks in English, reply in clear, inspiring English.
   - If the user asks a mixed or transliterated query (Tanglish), provide an accessible bilingual response.
6. STRUCTURE & TONE:
   - Maintain a respectful, encouraging, and pastoral tone.
   - Format responses cleanly with Markdown: bold key verses, bullet points for principles, and short digestible paragraphs.
   - Conclude with a brief, uplifting takeaway, reflection, or prayer point.
"""


def build_system_message(
    custom_prompt: Optional[str] = None,
    grounding_passages: Optional[List[GroundingPassage]] = None,
    language: str = "auto",
) -> str:
    """Assembles the complete system prompt including verified grounding passages."""
    base = custom_prompt.strip() if custom_prompt else DEFAULT_SYSTEM_PROMPT.strip()

    if not grounding_passages:
        return base

    context_lines = [base, "\n---", "### [VERIFIED SCRIPTURE CONTEXT FROM DATABASE] ###"]
    context_lines.append("Use the following verified verses from the Bible database to ground your explanation:")

    for idx, p in enumerate(grounding_passages, start=1):
        context_lines.append(f"\n{idx}. {p.format_for_prompt(language)}")

    context_lines.append("---")
    return "\n".join(context_lines)


SUGGESTED_QUESTIONS_EN = [
    "What does the Bible teach about dealing with anxiety and fear?",
    "Explain the parable of the Prodigal Son in Luke 15.",
    "What are the fruits of the Spirit described in Galatians 5?",
    "Why is Psalm 23 called the Shepherd Psalm? What is its deeper meaning?",
    "How does the Old Testament foreshadow Jesus Christ?",
    "What does scripture say about forgiveness when it feels impossible?",
]

SUGGESTED_QUESTIONS_TA = [
    "பயம் மற்றும் கவலையை வெல்ல வேதாகமம் என்ன போதிக்கிறது?",
    "சங்கீதம் 23-ன் ஆவிக்குரிய அர்த்தம் என்ன?",
    "கலாத்தியர் 5-ல் உள்ள ஆவியின் கனிகள் யாவை?",
    "லூக்கா 15-ல் உள்ள காணாமல்போன மகன் உவமையின் விளக்கம் என்ன?",
    "மன்னிப்பைப் பற்றி வேதாகமம் என்ன கூறுகிறது?",
    "பழைய ஏற்பாடு இயேசு கிறிஸ்துவை எவ்வாறு முன்னறிவிக்கிறது?",
]
