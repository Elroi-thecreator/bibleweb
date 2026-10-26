"""
Ask Bible AI — Reusable, Decoupled Biblical AI Plugin for Python and FastAPI.
Provides OpenAI-compatible LLM orchestration with verified scripture grounding,
bilingual English/Tamil support, and Server-Sent Events (SSE) streaming.
"""

from ask_bible_ai.config import AskBibleAIConfig, config
from ask_bible_ai.client import OpenAICompatibleClient
from ask_bible_ai.grounding import (
    BaseGroundingProvider,
    GroundingPassage,
    InMemoryGroundingProvider,
    NullGroundingProvider,
)
from ask_bible_ai.service import AskBibleAIService
from ask_bible_ai.history import ChatHistoryStore, history_store
from ask_bible_ai.routes import router as ask_ai_router

__all__ = [
    "AskBibleAIConfig",
    "config",
    "OpenAICompatibleClient",
    "BaseGroundingProvider",
    "GroundingPassage",
    "InMemoryGroundingProvider",
    "NullGroundingProvider",
    "AskBibleAIService",
    "ChatHistoryStore",
    "history_store",
    "ask_ai_router",
]
