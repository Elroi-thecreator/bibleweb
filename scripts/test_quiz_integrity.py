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
    print("✓ /quiz page renders 'Questions available: 100'.")

if __name__ == "__main__":
    test_quiz_dataset()
    import asyncio
    asyncio.run(test_quiz_routes())
