"""
Ask Bible AI Grounding Protocol and Providers.
Defines domain-agnostic data structures and interfaces for scripture retrieval.
Enables grounding LLM responses in real verified scripture passages to eliminate hallucinations.
Zero dependencies on application-specific databases.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GroundingPassage(BaseModel):
    """Represents a verified scripture passage retrieved from a database or search index."""
    reference: str = Field(description="Scripture citation, e.g., 'John 3:16' or 'யோவான் 3:16'")
    text_en: Optional[str] = Field(default=None, description="English scripture text")
    text_ta: Optional[str] = Field(default=None, description="Tamil scripture text")
    book: Optional[str] = Field(default=None, description="Canonical book name")
    chapter: Optional[int] = Field(default=None, description="Chapter number")
    verse: Optional[int] = Field(default=None, description="Verse number")
    relevance_score: float = Field(default=1.0, description="Normalized relevance metric")

    def format_for_prompt(self, preferred_language: str = "auto") -> str:
        """Formats the passage as clean context for the LLM system prompt."""
        parts = [f"[{self.reference}]"]
        if preferred_language in ("ta", "tamil") and self.text_ta:
            parts.append(self.text_ta)
            if self.text_en:
                parts.append(f"(English: {self.text_en})")
        elif preferred_language in ("en", "english") and self.text_en:
            parts.append(self.text_en)
            if self.text_ta:
                parts.append(f"(Tamil: {self.text_ta})")
        else:
            # Auto / Both
            if self.text_ta and self.text_en:
                parts.append(f"Tamil: {self.text_ta}\nEnglish: {self.text_en}")
            elif self.text_ta:
                parts.append(self.text_ta)
            elif self.text_en:
                parts.append(self.text_en)
        return "\n".join(parts)


class BaseGroundingProvider(ABC):
    """Abstract interface for scripture grounding engines."""

    @abstractmethod
    async def retrieve_context(
        self,
        query: str,
        language: str = "auto",
        max_passages: int = 4,
    ) -> List[GroundingPassage]:
        """
        Retrieves top relevant scripture passages for a user query.
        Implementations may use SQLite FTS5, PostgreSQL pgvector, Elasticsearch, or external APIs.
        """
        pass


class NullGroundingProvider(BaseGroundingProvider):
    """No-op grounding provider when no scripture database is configured."""

    async def retrieve_context(
        self,
        query: str,
        language: str = "auto",
        max_passages: int = 4,
    ) -> List[GroundingPassage]:
        return []


class InMemoryGroundingProvider(BaseGroundingProvider):
    """In-memory passage store for unit tests or standalone lightweight usage."""

    def __init__(self, passages: Optional[List[GroundingPassage]] = None):
        self.passages: List[GroundingPassage] = passages or []

    def add_passage(self, passage: GroundingPassage) -> None:
        self.passages.append(passage)

    async def retrieve_context(
        self,
        query: str,
        language: str = "auto",
        max_passages: int = 4,
    ) -> List[GroundingPassage]:
        query_words = set(query.lower().split())
        matched = []
        for p in self.passages:
            text = f"{p.reference} {p.text_en or ''} {p.text_ta or ''}".lower()
            overlap = sum(1 for w in query_words if w in text)
            if overlap > 0:
                p_copy = p.model_copy()
                p_copy.relevance_score = float(overlap)
                matched.append(p_copy)
        matched.sort(key=lambda x: x.relevance_score, reverse=True)
        return matched[:max_passages]
