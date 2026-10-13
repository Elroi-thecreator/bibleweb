# -*- coding: utf-8 -*-
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app.db import group_merged_verses, get_chapter_verses
from app.main import preprocess_scripture_text

async def test_merged_verses():
    print("=== Test 1: Merged Verse Grouping Engine (`group_merged_verses`) ===")
    sample_input = [
        {"verse": 1, "text_en": "The book of the generation of Jesus Christ.", "text_ta": "[1-2] இயேசு கிறிஸ்துவின் வம்ச வரலாறு."},
        {"verse": 2, "text_en": "Abraham begot Isaac.", "text_ta": "[1-2] இயேசு கிறிஸ்துவின் வம்ச வரலாறு."},
        {"verse": 3, "text_en": "And Isaac begot Jacob.", "text_ta": "ஈசாக்கு யாக்கோபைப் பெற்றான்."},
    ]
    grouped = group_merged_verses(sample_input)
    assert len(grouped) == 2
    assert grouped[0]["verse_display"] == "1-2"
    assert "[1]" in grouped[0]["text_en"] and "[2]" in grouped[0]["text_en"]
    print("✓ `group_merged_verses` combines multi-verse ranges cleanly.")

    print("\n=== Test 2: Protestant & Catholic Chapter Retrieval (Matthew 1) ===")
    prot_matt1 = get_chapter_verses(40, 1, canon="protestant")
    cath_matt1 = get_chapter_verses(40, 1, canon="catholic")
    assert len(prot_matt1) == 25
    assert len(cath_matt1) == 25
    print("✓ Matthew 1 retrieves 25 verses in both Protestant (1871/KJV) and Catholic (IRV/DRB) modes.")

    print("\n=== Test 3: Audio Preprocessing Strips [] and {} Content ===")
    audio_ta = preprocess_scripture_text("[1-2] ஆதியிலே தேவன் வானத்தையும் பூமியையும் படைத்தார்.")
    assert not audio_ta.startswith("[1-2]")
    assert audio_ta.startswith("ஆதியிலே")

    note_test = preprocess_scripture_text("In the beginning [1 Kings 21.] was the Word {an editorial note here}.")
    assert note_test == "In the beginning was the Word."
    print("✓ Audio text preprocessor completely strips anything inside [] and {} for natural speech.")

    print("\n🎉 ALL MERGED VERSE & AUDIO PREPROCESSOR TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_merged_verses())
