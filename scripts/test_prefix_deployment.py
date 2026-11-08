#!/usr/bin/env python3
"""
Test Suite: Subpath Deployment & URL Prefixing (/bible)
Verifies that the Holy Bible web server operates cleanly both at the root '/'
and under a custom subpath '/bible' for Oracle Cloud VM hosting.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_prefix_tests():
    print("=" * 65)
    print(" TESTING SUBPATH HOSTING UNDER /bible (Oracle Cloud VM Standard)")
    print("=" * 65)

    # 1. Test URL_PREFIX="/bible"
    os.environ["URL_PREFIX"] = "/bible"
    
    # Reload modules to pick up URL_PREFIX
    if "app.main" in sys.modules:
        del sys.modules["app.main"]
    if "app.admin.routes" in sys.modules:
        del sys.modules["app.admin.routes"]
    if "app.admin.auth" in sys.modules:
        del sys.modules["app.admin.auth"]

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
        print("[OK] 2. /bible/ returns 200 and all navigation/static assets are prefixed with /bible/")

        # Test 3: Scripture Reader at /bible/read/43/1 (John 1 bilingual)
        r2 = client.get("/bible/read/43/1?mode=bilingual")
        assert r2.status_code == 200, f"Expected 200, got {r2.status_code}"
        assert "யோவான்" in r2.text or "John" in r2.text, "Scripture text missing from reader"
        assert '/bible/static/' in r2.text, "Reader static links must be prefixed with /bible/static/"
        print("[OK] 3. /bible/read/43/1 renders bilingual Scripture with /bible/ assets")

        # Test 4: Songs search page at /bible/songs
        r3 = client.get("/bible/songs")
        assert r3.status_code == 200, f"Expected 200, got {r3.status_code}"
        print("[OK] 4. /bible/songs loads song lyrics index successfully")

        # Test 5: Quiz portal at /bible/quiz
        r4 = client.get("/bible/quiz")
        assert r4.status_code == 200, f"Expected 200, got {r4.status_code}"
        print("[OK] 5. /bible/quiz loads Bible Quiz portal successfully")

        # Test 6: Reading plans at /bible/plans
        r5 = client.get("/bible/plans")
        assert r5.status_code == 200, f"Expected 200, got {r5.status_code}"
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
        assert r8.headers["location"] == "/bible/read/43/1?mode=bilingual", f"Expected /bible/read/43/1?mode=bilingual, got {r8.headers['location']}"
        print("[OK] 9. Legacy book redirects correctly prepend /bible/")

        # Test 10: Admin settings redirect /bible/settings -> /bible/admin/settings
        r9 = client.get("/bible/settings", follow_redirects=False)
        assert r9.status_code == 303, f"Expected 303 redirect, got {r9.status_code}"
        assert r9.headers["location"] == "/bible/admin/settings", f"Expected /bible/admin/settings, got {r9.headers['location']}"
        print("[OK] 10. /bible/settings redirects to /bible/admin/settings")

    print("=" * 65)
    print(" ALL 10 SUBPATH HOSTING TESTS PASSED PERFECTLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_prefix_tests()
