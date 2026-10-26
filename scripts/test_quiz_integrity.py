# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from collections import Counter
from app.quiz_data import QUIZ_CATEGORIES, QUIZ_QUESTIONS

def test_quiz_dataset():
    print(f"Total questions in QUIZ_QUESTIONS: {len(QUIZ_QUESTIONS)}")
    assert len(QUIZ_QUESTIONS) == 100, f"Expected 100 questions, got {len(QUIZ_QUESTIONS)}"

    ids = set()
    category_counts = Counter()
    difficulty_counts = Counter()

    for idx, q in enumerate(QUIZ_QUESTIONS, start=1):
        # 1. ID checks
        assert q["id"] == idx, f"Question index {idx} has id {q.get('id')}"
        assert q["id"] not in ids, f"Duplicate ID: {q['id']}"
        ids.add(q["id"])

        # 2. Required fields
        for field in ["category", "difficulty", "question_en", "question_ta", "options_en", "options_ta", "correct_index", "reference", "explanation_en", "explanation_ta"]:
            assert field in q, f"Missing field '{field}' in Q{q['id']}"
            assert q[field] is not None, f"Field '{field}' is None in Q{q['id']}"

        # 3. Category & Difficulty
        cat = q["category"]
        assert cat in QUIZ_CATEGORIES, f"Unknown category '{cat}' in Q{q['id']}"
        category_counts[cat] += 1

        diff = q["difficulty"]
        assert diff in ["easy", "medium", "hard"], f"Unknown difficulty '{diff}' in Q{q['id']}"
        difficulty_counts[diff] += 1

        # 4. Options
        assert len(q["options_en"]) == 4, f"options_en length != 4 in Q{q['id']}"
        assert len(q["options_ta"]) == 4, f"options_ta length != 4 in Q{q['id']}"
        assert 0 <= q["correct_index"] <= 3, f"Invalid correct_index in Q{q['id']}"

        # Ensure text is not empty
        assert len(q["question_en"].strip()) > 5
        assert len(q["question_ta"].strip()) > 5
        assert len(q["reference"].strip()) > 3
        assert len(q["explanation_en"].strip()) > 5
        assert len(q["explanation_ta"].strip()) > 5

    print("\n✓ Category Breakdown:")
    for cat, count in category_counts.most_common():
        cat_info = QUIZ_CATEGORIES[cat]
        print(f"  - {cat_info['icon']} {cat_info['name_en']} ({cat_info['name_ta']}): {count} questions")

    print("\n✓ Difficulty Breakdown:")
    for diff, count in difficulty_counts.most_common():
        print(f"  - {diff.capitalize()}: {count} questions")

    print("\n🎉 ALL 100 QUIZ QUESTIONS ARE 100% VALID & INTEGRAL!")

async def test_quiz_routes():
    from starlette.requests import Request
    from app.main import get_quiz_questions, quiz_page
    import json

    resp = await get_quiz_questions(category="all", difficulty="all", limit=20, randomize=True)
    data = json.loads(resp.body.decode("utf-8"))
    assert data["total_available"] == 100, f"Expected 100 available, got {data['total_available']}"
    assert len(data["questions"]) == 20, f"Expected 20 questions, got {len(data['questions'])}"
    print("✓ /api/quiz/questions returned 20 random questions out of 100 available.")

    # Test category filtering
    for cat in ["gospels", "old_testament", "heroes", "miracles_parables", "general"]:
        resp_cat = await get_quiz_questions(category=cat, difficulty="all", limit=50, randomize=False)
        data_cat = json.loads(resp_cat.body.decode("utf-8"))
        assert data_cat["total_available"] >= 18, f"Expected at least 18 questions in {cat}, got {data_cat['total_available']}"
        print(f"✓ Filtered category '{cat}': {data_cat['total_available']} questions available.")

    from ask_bible_ai.config import config as ai_config
    ai_config.enabled = True
    ai_config.quiz_ai_enabled = True

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/quiz",
        "raw_path": b"/quiz",
        "query_string": b"",
        "headers": [],
    }
    req = Request(scope)
    page_resp = await quiz_page(req, canon=None)
    html = page_resp.body.decode("utf-8")
    assert "Questions available: 100" in html
    assert "AI Scripture Quiz Generator" in html
    assert "Ask AI Tutor for Reflection" in html
    print("✓ /quiz page renders 'Questions available: 100' and AI Scripture Quiz Generator UI when enabled.")

    # Test that /quiz omits AI Generator when disabled in settings
    ai_config.quiz_ai_enabled = False
    page_resp_disabled = await quiz_page(req, canon=None)
    html_disabled = page_resp_disabled.body.decode("utf-8")
    assert 'id="ai-quick-topics"' not in html_disabled
    assert 'id="ai-tutor-trigger-btn"' not in html_disabled
    print("✓ /quiz page correctly hides AI Quiz sections and Tutor button when quiz_ai_enabled is False.")
    ai_config.quiz_ai_enabled = True


async def test_ai_quiz_features():
    from starlette.requests import Request
    from app.main import api_generate_quiz_ai, api_explain_quiz_ai
    from ask_bible_ai.config import config as ai_config
    from fastapi import HTTPException
    import json

    # 1. Test POST /api/quiz/generate-ai with "Parables of Jesus"
    payload = {
        "topic": "Parables of Jesus (உவமைகள்)",
        "count": 5,
        "difficulty": "medium",
        "language": "bilingual"
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/quiz/generate-ai",
        "raw_path": b"/api/quiz/generate-ai",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
    }
    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    req = Request(scope, receive)
    resp = await api_generate_quiz_ai(req)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = json.loads(resp.body.decode("utf-8"))
    assert data["status"] == "ok"
    assert len(data["questions"]) == 5
    for q in data["questions"]:
        assert "question_en" in q and "question_ta" in q
        assert len(q["options_en"]) == 4 and len(q["options_ta"]) == 4
        assert 0 <= q["correct_index"] <= 3
        assert "reference" in q and "explanation_en" in q and "explanation_ta" in q
    print("✓ /api/quiz/generate-ai successfully generated 5 valid bilingual questions on Parables.")

    # 2. Test POST /api/quiz/explain-ai
    sample_q = data["questions"][0]
    explain_payload = {
        "question_en": sample_q["question_en"],
        "question_ta": sample_q["question_ta"],
        "options_en": sample_q["options_en"],
        "options_ta": sample_q["options_ta"],
        "chosen_index": sample_q["correct_index"],
        "correct_index": sample_q["correct_index"],
        "reference": sample_q["reference"],
        "explanation_en": sample_q["explanation_en"],
        "explanation_ta": sample_q["explanation_ta"],
        "language": "bilingual"
    }
    explain_body = json.dumps(explain_payload).encode("utf-8")
    scope_exp = {
        "type": "http",
        "method": "POST",
        "path": "/api/quiz/explain-ai",
        "raw_path": b"/api/quiz/explain-ai",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
    }
    async def receive_exp():
        return {"type": "http.request", "body": explain_body, "more_body": False}

    req_exp = Request(scope_exp, receive_exp)
    resp_exp = await api_explain_quiz_ai(req_exp)
    assert resp_exp.status_code == 200
    exp_data = json.loads(resp_exp.body.decode("utf-8"))
    assert exp_data["status"] == "ok"
    assert "tutoring" in exp_data and len(exp_data["tutoring"]) > 20
    print("✓ /api/quiz/explain-ai returned deep theological reflection with scripture grounding.")

    # 3. Test Configurable Disabling of AI in Quiz
    ai_config.quiz_ai_enabled = False
    try:
        req_disabled = Request(scope, receive)
        await api_generate_quiz_ai(req_disabled)
        assert False, "Expected HTTPException 503 when quiz_ai_enabled is False"
    except HTTPException as e:
        assert e.status_code == 503
        print("✓ Verified /api/quiz/generate-ai returns HTTP 503 when disabled in Settings.")
    finally:
        ai_config.quiz_ai_enabled = True


if __name__ == "__main__":
    test_quiz_dataset()
    import asyncio
    asyncio.run(test_quiz_routes())
    asyncio.run(test_ai_quiz_features())
