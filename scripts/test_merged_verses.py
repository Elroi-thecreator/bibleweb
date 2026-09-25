# -*- coding: utf-8 -*-
import os
import sys
import asyncio
from starlette.requests import Request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app.db import get_chapter_verses, search_verses
from app.main import reader, presenter_mode, preprocess_scripture_text

def make_request(path: str, query: str = ""):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": query.encode("utf-8"),
        "headers": [],
    }
    return Request(scope)

async def test_merged_verses():
    print("=== Test 1: Catholic Chapter Grouping (Matthew 1:1-2) ===")
    cath_matt1 = get_chapter_verses(40, 1, canon="catholic")
    v0 = cath_matt1[0]
    assert v0["verse"] == 1, f"Expected verse 1, got {v0['verse']}"
    assert v0["verse_display"] == "1-2", f"Expected verse_display '1-2', got {v0['verse_display']}"
    assert "[1]" in v0["text_en"] and "[2]" in v0["text_en"], f"English text should contain both verses: {v0['text_en']}"
    assert "தாவீதின் மகனும்" in v0["text_ta"]
    print("✓ Catholic Matthew 1:1-2 successfully grouped as '1-2' with combined English.")

    print("\n=== Test 2: Catholic Chapter Grouping (1 Corinthians 1:1-3) ===")
    cath_1co1 = get_chapter_verses(46, 1, canon="catholic")
    v_1co = cath_1co1[0]
    assert v_1co["verse_display"] == "1-3", f"Expected '1-3', got {v_1co['verse_display']}"
    assert "[1]" in v_1co["text_en"] and "[2]" in v_1co["text_en"] and "[3]" in v_1co["text_en"]
    print("✓ Catholic 1 Corinthians 1:1-3 successfully grouped as '1-3' with combined English.")

    print("\n=== Test 3: Protestant Remains Strictly Separated ===")
    prot_matt1 = get_chapter_verses(40, 1, canon="protestant")
    assert prot_matt1[0]["verse_display"] == "1"
    assert prot_matt1[1]["verse_display"] == "2"
    assert len(prot_matt1) == 25, f"Expected 25 verses in Protestant Matt 1, got {len(prot_matt1)}"
    print("✓ Protestant Matthew 1 remains 25 separate verses.")

    print("\n=== Test 4: Search Deduplication ===")
    s_results = search_verses("கொரிந்து நகரிலுள்ள", canon="catholic", limit=10)
    matching = [r for r in s_results if r["book_id"] == 46 and r["chapter"] == 1]
    assert len(matching) == 1, f"Expected 1 collapsed result for 1 Cor 1:1-3, got {len(matching)}"
    assert matching[0]["verse_display"] == "1-3"
    print(f"✓ Search collapsed 1 Cor 1:1-3 into a single hit: {matching[0]['verse_display']}.")

    print("\n=== Test 5: Audio Preprocessing Strips Bracket Numbers ===")
    audio_ta = preprocess_scripture_text("[1-2] தாவீதின் மகனும் ஆபிரகாமின் மகனுமான...")
    assert not audio_ta.startswith("[1-2]") and not audio_ta.startswith("1-2")
    assert audio_ta.startswith("தாவீதின் மகனும்")
    audio_en = preprocess_scripture_text("[1] The book of... [2] Abraham begot...")
    assert "[1]" not in audio_en and "[2]" not in audio_en
    print("✓ Audio text preprocessor cleanly strips [1-2] bracket numbers for natural speech.")

    print("\n=== Test 6: Reader HTML Template Rendering ===")
    req_r = make_request("/read/40/1", "canon=catholic&mode=bilingual")
    resp_r = await reader(req_r, book_id=40, chapter=1, mode="bilingual", canon="catholic")
    html_r = resp_r.body.decode("utf-8")
    assert "1:1-2" in html_r
    assert 'data-verse-display="1-2"' in html_r
    assert '<span id="v2" class="anchor-alias"></span>' in html_r
    print("✓ Reader HTML renders single '1:1-2' card with '#v2' anchor alias.")

    print("\n=== Test 7: Presenter HTML Template Rendering ===")
    req_p = make_request("/present/40/1", "canon=catholic")
    resp_p = await presenter_mode(req_p, book_id=40, chapter=1, canon="catholic")
    html_p = resp_p.body.decode("utf-8")
    assert "Matthew 1:1-2" in html_p
    print("✓ Presenter HTML renders slide badge 'Matthew 1:1-2'.")

    print("\n🎉 ALL 7 TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_merged_verses())
