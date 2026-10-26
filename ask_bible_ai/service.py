"""
Ask Bible AI Core Orchestrator Service.
Coordinates Grounding Context retrieval, Bilingual System Prompt Construction,
Conversation History assembly, and Async LLM Execution (both streaming and full response).
Designed to be completely decoupled and testable independently of any web framework.
"""

import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from ask_bible_ai.config import AskBibleAIConfig, config as default_config
from ask_bible_ai.client import OpenAICompatibleClient
from ask_bible_ai.grounding import BaseGroundingProvider, NullGroundingProvider, GroundingPassage
from ask_bible_ai.prompts import (
    build_system_message,
    detect_language,
    SUGGESTED_QUESTIONS_EN,
    SUGGESTED_QUESTIONS_TA,
)


class AskBibleAIService:
    """The central orchestration engine for the Ask Bible AI plugin."""

    def __init__(
        self,
        config: Optional[AskBibleAIConfig] = None,
        client: Optional[OpenAICompatibleClient] = None,
        grounding_provider: Optional[BaseGroundingProvider] = None,
    ):
        self.config = config or default_config
        self.client = client or OpenAICompatibleClient(self.config)
        self.grounding_provider = grounding_provider or NullGroundingProvider()

    def set_grounding_provider(self, provider: BaseGroundingProvider) -> None:
        """Injects or swaps the scripture grounding provider at runtime."""
        self.grounding_provider = provider

    def get_suggested_questions(self, language: str = "auto") -> List[str]:
        """Returns starter questions tailored to the user's preferred language."""
        if language in ("ta", "tamil"):
            return SUGGESTED_QUESTIONS_TA
        elif language in ("en", "english"):
            return SUGGESTED_QUESTIONS_EN
        # Auto: return curated mix
        return [
            SUGGESTED_QUESTIONS_EN[0],
            SUGGESTED_QUESTIONS_TA[0],
            SUGGESTED_QUESTIONS_EN[1],
            SUGGESTED_QUESTIONS_TA[1],
            SUGGESTED_QUESTIONS_EN[2],
            SUGGESTED_QUESTIONS_TA[2],
        ]

    async def health(self) -> Dict[str, Any]:
        """Returns comprehensive diagnostic health of the AI service and grounding engine."""
        llm_health = await self.client.health_check()
        return {
            "status": "healthy" if llm_health.get("status") in ("healthy", "simulation") else "degraded",
            "enabled": self.config.enabled,
            "provider": self.config.provider_name,
            "base_url": self.config.base_url,
            "model": self.config.model,
            "grounding_provider": self.grounding_provider.__class__.__name__,
            "grounding_enabled": self.config.enable_grounding,
            "simulation_mode": self.config.simulation_mode,
            "upstream_llm": llm_health,
        }

    async def ask(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        preferred_language: str = "auto",
        max_passages: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Processes an inquiry, retrieves verified scripture context, and generates a grounded response.
        """
        start_time = time.time()
        detected_lang = detect_language(query) if preferred_language == "auto" else preferred_language

        # 1. Retrieve scripture grounding passages if enabled
        passages: List[GroundingPassage] = []
        if self.config.enable_grounding and self.grounding_provider:
            limit = max_passages if max_passages is not None else self.config.max_grounding_passages
            try:
                passages = await self.grounding_provider.retrieve_context(
                    query=query,
                    language=detected_lang,
                    max_passages=limit,
                )
            except Exception as e:
                # Grounding failure should not crash answering
                passages = []

        # 2. Build system message with injected grounding context
        system_content = build_system_message(
            custom_prompt=None,
            grounding_passages=passages,
            language=detected_lang,
        )

        # 3. Assemble chat message sequence
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]

        # Include prior conversation turns if provided (clamped to last 6 messages)
        if history:
            sanitized_history = []
            for h in history[-6:]:
                role = h.get("role")
                content = h.get("content")
                if role in ("user", "assistant") and content:
                    sanitized_history.append({"role": role, "content": str(content)})
            messages.extend(sanitized_history)

        messages.append({"role": "user", "content": query})

        # 4. Generate LLM response
        raw_res = await self.client.generate_chat_completion(
            messages=messages,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        took_ms = round((time.time() - start_time) * 1000, 2)
        answer = raw_res["choices"][0]["message"]["content"]
        fallback_notice = raw_res.get("_fallback_notice")

        return {
            "success": True,
            "query": query,
            "language": detected_lang,
            "answer": answer,
            "citations": [p.reference for p in passages],
            "passages_used": [
                {
                    "reference": p.reference,
                    "text_en": p.text_en,
                    "text_ta": p.text_ta,
                    "book": p.book,
                    "chapter": p.chapter,
                    "verse": p.verse,
                }
                for p in passages
            ],
            "model": raw_res.get("model", self.config.model),
            "usage": raw_res.get("usage", {}),
            "took_ms": took_ms,
            "fallback_notice": fallback_notice,
        }

    async def ask_stream(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        preferred_language: str = "auto",
        max_passages: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens asynchronously.
        """
        detected_lang = detect_language(query) if preferred_language == "auto" else preferred_language

        # Retrieve grounding passages
        passages: List[GroundingPassage] = []
        if self.config.enable_grounding and self.grounding_provider:
            limit = max_passages if max_passages is not None else self.config.max_grounding_passages
            try:
                passages = await self.grounding_provider.retrieve_context(
                    query=query,
                    language=detected_lang,
                    max_passages=limit,
                )
            except Exception:
                passages = []

        self.last_citations = [p.reference for p in passages]

        system_content = build_system_message(
            custom_prompt=None,
            grounding_passages=passages,
            language=detected_lang,
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        if history:
            for h in history[-6:]:
                role = h.get("role")
                content = h.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": str(content)})
        messages.append({"role": "user", "content": query})

        async for token in self.client.stream_chat_completion(
            messages=messages,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        ):
            yield token
