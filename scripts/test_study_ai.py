"""Verification test suite for AI Scripture Study and Verse Exegesis.
Tests chapter overviews, theological exegesis, admin config toggling, and reader UI rendering.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app, HTML_PAGE_CACHE
from ask_bible_ai.config import config


def run_tests():
    client = TestClient(app)

    print(">>> 1. Ensuring Study AI is enabled in config...")
    config.study_ai_enabled = True
    HTML_PAGE_CACHE.clear()

    # 1. Test Chapter Overview Endpoint
    print(">>> 2. Testing GET /api/study/chapter-overview for John 3...")
    resp = client.get("/api/study/chapter-overview?book_id=43&chapter=3")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    overview = resp.json()
    assert overview["book_id"] == 43
    assert overview["chapter"] == 3
    assert "historical_context" in overview
    assert "en" in overview["historical_context"] and len(overview["historical_context"]["en"]) > 0
    assert "ta" in overview["historical_context"] and len(overview["historical_context"]["ta"]) > 0
    assert "outline" in overview and len(overview["outline"]) > 0
    assert "spiritual_takeaway" in overview
    print("   [PASS] Chapter overview returned valid bilingual data.")

    # 2. Test Verse Exegesis Endpoint
    print(">>> 3. Testing POST /api/study/verse-exegesis for John 3:16...")
    payload = {
        "book_id": 43,
        "book_en": "John",
        "book_ta": "யோவான்",
        "chapter": 3,
        "verse": 16,
        "verse_text_en": "For God so loved the world, that he gave his only begotten Son...",
        "verse_text_ta": "தேவன், தம்முடைய ஒரேபேறான குமாரனை விசுவாசிக்கிறவன் எவனோ அவன் கெட்டுப்போகாமல்..."
    }
    resp = client.post("/api/study/verse-exegesis", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    exegesis = resp.json()
    assert "literary_and_theological_context" in exegesis
    assert "original_language" in exegesis
    assert "cross_references" in exegesis and len(exegesis["cross_references"]) > 0
    assert "practical_application" in exegesis
    assert "guided_prayer" in exegesis
    print("   [PASS] Verse exegesis returned valid linguistic and theological payload.")

    # 3. Test Reader HTML contains Study AI elements when enabled
    print(">>> 4. Verifying reader HTML with study_ai_enabled=True...")
    HTML_PAGE_CACHE.clear()
    r = client.get("/read/43/3")
    assert r.status_code == 200
    html = r.text
    assert 'id="chapter-study-card"' in html, "Chapter study card missing from reader HTML"
    assert 'id="verse-exegesis-modal"' in html, "Verse exegesis modal missing from reader HTML"
    assert 'verse-exegesis-btn' in html, "Verse exegesis action button missing from reader HTML"
    print("   [PASS] Reader template renders study UI components.")

    # 4. Test Disabling Study AI in config
    print(">>> 5. Testing disabled behavior...")
    config.study_ai_enabled = False
    HTML_PAGE_CACHE.clear()

    resp_disabled_overview = client.get("/api/study/chapter-overview?book_id=43&chapter=3")
    assert resp_disabled_overview.status_code == 503, f"Expected 503 when disabled, got {resp_disabled_overview.status_code}"

    resp_disabled_exegesis = client.post("/api/study/verse-exegesis", json=payload)
    assert resp_disabled_exegesis.status_code == 503, f"Expected 503 when disabled, got {resp_disabled_exegesis.status_code}"

    r_disabled = client.get("/read/43/3")
    assert r_disabled.status_code == 200
    html_disabled = r_disabled.text
    assert 'id="chapter-study-card"' not in html_disabled, "Chapter study card should be hidden when disabled"
    assert 'id="verse-exegesis-modal"' not in html_disabled, "Verse exegesis modal should be hidden when disabled"
    assert 'verse-exegesis-btn' not in html_disabled, "Verse exegesis button should be hidden when disabled"
    print("   [PASS] Disabling Study AI correctly gates endpoints (503) and removes UI.")

    # Reset config
    config.study_ai_enabled = True
    HTML_PAGE_CACHE.clear()
    print(">>> All Study AI tests passed successfully!")


if __name__ == "__main__":
    run_tests()
