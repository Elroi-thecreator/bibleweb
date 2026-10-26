"""
Unit and Integration Tests for Ask Bible AI Plugin.
Can be executed with `pytest` inside any project that includes `ask_bible_ai`.
"""

import asyncio
import os
import pytest
from ask_bible_ai.config import AskBibleAIConfig
from ask_bible_ai.prompts import detect_language, build_system_message
from ask_bible_ai.grounding import GroundingPassage, InMemoryGroundingProvider, NullGroundingProvider
from ask_bible_ai.client import OpenAICompatibleClient
from ask_bible_ai.service import AskBibleAIService


@pytest.mark.asyncio
async def test_config():
    cfg = AskBibleAIConfig(api_key="sk-test-secret-12345", simulation_mode=True)
    d = cfg.to_dict()
    assert d["simulation_mode"] is True
    assert "..." in d["api_key"]


@pytest.mark.asyncio
async def test_language_detection():
    assert detect_language("What does the Bible teach about peace?") == "en"
    assert detect_language("சமாதானத்தைப் பற்றி வேதாகமம் என்ன கூறுகிறது?") == "ta"


@pytest.mark.asyncio
async def test_in_memory_grounding():
    provider = InMemoryGroundingProvider([
        GroundingPassage(reference="John 1:1", text_en="In the beginning was the Word"),
        GroundingPassage(reference="Psalm 23:1", text_en="The Lord is my shepherd"),
    ])
    results = await provider.retrieve_context("shepherd")
    assert len(results) == 1
    assert results[0].reference == "Psalm 23:1"


@pytest.mark.asyncio
async def test_service_simulation_mode():
    cfg = AskBibleAIConfig(simulation_mode=True)
    client = OpenAICompatibleClient(cfg)
    provider = InMemoryGroundingProvider([
        GroundingPassage(reference="John 3:16", text_en="For God so loved the world", text_ta="தேவன் உலகத்தில் அன்புகூர்ந்தார்"),
    ])
    service = AskBibleAIService(config=cfg, client=client, grounding_provider=provider)

    res = await service.ask("What is love?")
    assert res["success"] is True
    assert len(res["answer"]) > 50
    assert "John 3:16" in res["citations"]
