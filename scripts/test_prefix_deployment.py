#!/usr/bin/env python3
"""
Test Suite: Root & Subpath Deployment Verification
Verifies that the Holy Bible web server operates cleanly both at the root '/'
(the preferred Oracle Cloud VM standard) and optionally under a subpath like '/bible'.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_root_tests():
    print("=" * 65)
    print(" TESTING ROOT HOSTING AT '/' (Primary Oracle Cloud VM Standard)")
    print("=" * 65)

    os.environ.pop("URL_PREFIX", None)
    os.environ.pop("ROOT_PATH", None)

    for mod in list(sys.modules.keys()):
        if mod.startswith("app.") or mod == "app":
            del sys.modules[mod]

    from app.main import app as bible_app
    from fastapi.testclient import TestClient

    with TestClient(bible_app) as client:
        # 1. Root landing page
        r = client.get("/")
        assert r.status_code == 200, f"Expected 200 at /, got {r.status_code}"
        assert 'href="/plans"' in r.text
        assert 'href="/progress"' in r.text
        assert 'src="/static/' in r.text
        assert '/bible/bible' not in r.text
        print("[OK] 1. Root / serves landing page with clean root-relative links")

        # 2. Reading page
        r = client.get("/read/43/1?mode=bilingual")
        assert r.status_code == 200, f"Expected 200 at /read/43/1, got {r.status_code}"
        assert "யோவான்" in r.text or "John" in r.text
        print("[OK] 2. /read/43/1 renders bilingual Scripture")

        # 3. Plans page
        r = client.get("/plans")
        assert r.status_code == 200, f"Expected 200 at /plans, got {r.status_code}"
        print("[OK] 3. /plans loads 100-Day Reading Plans successfully")

        # 4. Progress page
        r = client.get("/progress")
        assert r.status_code == 200, f"Expected 200 at /progress, got {r.status_code}"
        print("[OK] 4. /progress loads Reading Progress dashboard")

        # 5. Songs page
        r = client.get("/songs")
        assert r.status_code == 200, f"Expected 200 at /songs, got {r.status_code}"
        print("[OK] 5. /songs loads song lyrics index successfully")

        # 6. Quiz page
        r = client.get("/quiz")
        assert r.status_code == 200, f"Expected 200 at /quiz, got {r.status_code}"
        print("[OK] 6. /quiz loads Bible Quiz portal successfully")

        # 7. Static file delivery
        r = client.get("/static/manifest.json")
        assert r.status_code == 200, f"Expected 200 at /static/manifest.json, got {r.status_code}"
        print("[OK] 7. /static/manifest.json serves static assets correctly")

        # 8. API endpoints
        r = client.get("/api/health")
        assert r.status_code == 200, f"Expected 200 at /api/health, got {r.status_code}"
        assert r.json()["status"] == "ok"
        print("[OK] 8. /api/health returns valid JSON")

        # 9. Admin settings redirect
        r = client.get("/settings", follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"] == "/admin/settings"
        print("[OK] 9. /settings redirects to /admin/settings")

    print("=" * 65)
    print(" ALL ROOT HOSTING TESTS PASSED PERFECTLY!")
    print("=" * 65)


def run_prefix_tests():
    print("=" * 65)
    print(" TESTING SUBPATH HOSTING UNDER /bible (Idempotence & Subpath)")
    print("=" * 65)

    os.environ["URL_PREFIX"] = "/bible"

    for mod in list(sys.modules.keys()):
        if mod.startswith("app.") or mod == "app":
            del sys.modules[mod]

    from app.main import app as bible_app
    from fastapi.testclient import TestClient

    with TestClient(bible_app) as client:
        # Test 1: Root redirect from /bible to /bible/
        r0 = client.get("/bible", follow_redirects=False)
        assert r0.status_code == 307, f"Expected 307 redirect, got {r0.status_code}"
        assert r0.headers["location"] == "/bible/", f"Expected location /bible/, got {r0.headers['location']}"
        print("[OK] 1. /bible redirects cleanly to /bible/ (Status 307)")

        # Test 2: Home landing page at /bible/
        r1 = client.get("/bible/")
        assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"
        assert 'href="/bible/' in r1.text or "href='/bible/" in r1.text, "Landing page links must be prefixed with /bible/"
        assert '/bible/static/' in r1.text, "Static assets must be prefixed with /bible/static/"
        assert '/bible/bible' not in r1.text, "FATAL: Duplicate /bible/bible found in HTML!"
        print("[OK] 2. /bible/ returns 200 and all navigation/static assets are prefixed with /bible/ (No duplicates!)")

        # Test 3: Scripture Reader at /bible/read/43/1 (John 1 bilingual)
        r2 = client.get("/bible/read/43/1?mode=bilingual")
        assert r2.status_code == 200, f"Expected 200, got {r2.status_code}"
        assert "யோவான்" in r2.text or "John" in r2.text, "Scripture text missing from reader"
        assert '/bible/static/' in r2.text, "Reader static links must be prefixed with /bible/static/"
        assert '/bible/bible' not in r2.text, "FATAL: Duplicate /bible/bible found in reader HTML!"
        print("[OK] 3. /bible/read/43/1 renders bilingual Scripture with /bible/ assets")

        # Test 4: Songs search page at /bible/songs
        r3 = client.get("/bible/songs")
        assert r3.status_code == 200, f"Expected 200, got {r3.status_code}"
        assert '/bible/bible' not in r3.text
        print("[OK] 4. /bible/songs loads song lyrics index successfully")

        # Test 5: Quiz portal at /bible/quiz
        r4 = client.get("/bible/quiz")
        assert r4.status_code == 200, f"Expected 200, got {r4.status_code}"
        assert '/bible/bible' not in r4.text
        print("[OK] 5. /bible/quiz loads Bible Quiz portal successfully")

        # Test 6: Reading plans at /bible/plans
        r5 = client.get("/bible/plans")
        assert r5.status_code == 200, f"Expected 200, got {r5.status_code}"
        assert '/bible/bible' not in r5.text
        print("[OK] 6. /bible/plans loads 100-Day Reading Plans successfully")

        # Test 7: Static file delivery at /bible/static/manifest.json
        r6 = client.get("/bible/static/manifest.json")
        assert r6.status_code == 200, f"Expected 200, got {r6.status_code}"
        print("[OK] 7. /bible/static/manifest.json serves static assets correctly")

        # Test 8: Health and Songs API query at /bible/api/health & /bible/api/songs
        r7 = client.get("/bible/api/health")
        assert r7.status_code == 200, f"Expected 200, got {r7.status_code}"
        assert r7.json()["status"] == "ok", "Expected status ok in health JSON"

        r7_songs = client.get("/bible/api/songs?book=jebathota&limit=5")
        assert r7_songs.status_code == 200, f"Expected 200, got {r7_songs.status_code}"
        assert "songs" in r7_songs.json(), "Expected songs list in JSON"
        print("[OK] 8. /bible/api/health and /bible/api/songs return valid JSON")

        # Test 9: Legacy book redirect /bible/book/43/chapter/1
        r8 = client.get("/bible/book/43/chapter/1", follow_redirects=False)
        assert r8.status_code in (301, 302, 307), f"Expected redirect, got {r8.status_code}"
        assert r8.headers["location"] == "/bible/read/43/1?mode=bilingual"
        print("[OK] 9. Legacy book redirects correctly prepend /bible/")

        # Test 10: Admin settings redirect /bible/settings -> /bible/admin/settings
        r9 = client.get("/bible/settings", follow_redirects=False)
        assert r9.status_code == 303, f"Expected 303 redirect, got {r9.status_code}"
        assert r9.headers["location"] == "/bible/admin/settings"
        print("[OK] 10. /bible/settings redirects to /bible/admin/settings")

    print("=" * 65)
    print(" ALL SUBPATH HOSTING TESTS PASSED PERFECTLY (0 DUPLICATE PREFIXES)!")
    print("=" * 65)


if __name__ == "__main__":
    run_root_tests()
    run_prefix_tests()
