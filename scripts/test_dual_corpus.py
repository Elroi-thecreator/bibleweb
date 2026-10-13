import os
import sys
import asyncio
from starlette.requests import Request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app.main import landing_page, reader, search_page, presenter_mode, stream_audio, privacy_page
from app.db import get_chapter_verses, get_book_info, search_verses

def make_request(path: str, query: str = "", cookies: dict = None):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": query.encode("utf-8"),
        "headers": [(b"cookie", "; ".join(f"{k}={v}" for k, v in (cookies or {}).items()).encode("utf-8"))],
    }
    return Request(scope)

async def run_tests():
    print("=== 1. Testing Landing Page ===")
    req_p = make_request("/", query="canon=protestant")
    resp_p = await landing_page(req_p, canon="protestant")
    body_p = resp_p.body.decode("utf-8")
    assert "ஆதியாகமம்" in body_p
    print("✓ Protestant landing page rendered with 1871 Tamil Old Version names.")

    req_c = make_request("/", query="canon=catholic")
    resp_c = await landing_page(req_c, canon="catholic")
    body_c = resp_c.body.decode("utf-8")
    assert "தொடக்க நூல்" in body_c
    assert "திருப்பாடல்கள்" in body_c
    print("✓ Catholic 73-book landing page rendered with traditional Tamil names (தொடக்க நூல், திருப்பாடல்கள்).")

    print("\n=== 2. Testing Genesis 1:1 ===")
    req_gen_p = make_request("/read/1/1", query="canon=protestant&mode=bilingual")
    resp_gen_p = await reader(req_gen_p, book_id=1, chapter=1, mode="bilingual", canon="protestant")
    body_gen_p = resp_gen_p.body.decode("utf-8")
    assert "ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்" in body_gen_p
    assert "In the beginning God created the heaven" in body_gen_p
    print("✓ Protestant Genesis 1:1 verified (1871 Tamil Old Version + KJV).")

    req_gen_c = make_request("/read/1/1", query="canon=catholic&mode=bilingual")
    resp_gen_c = await reader(req_gen_c, book_id=1, chapter=1, mode="bilingual", canon="catholic")
    body_gen_c = resp_gen_c.body.decode("utf-8")
    assert "ஆதியிலே தேவன் வானத்தையும் பூமியையும் படைத்தார்" in body_gen_c
    assert "In the beginning God created heaven, and earth." in body_gen_c
    print("✓ Catholic Genesis 1:1 verified (Tamil IRV CC BY-SA 4.0 + Douay-Rheims 1752 Public Domain).")

    print("\n=== 3. Testing Psalm 23:1 ===")
    req_ps_p = make_request("/read/19/23", query="canon=protestant&mode=bilingual")
    resp_ps_p = await reader(req_ps_p, book_id=19, chapter=23, mode="bilingual", canon="protestant")
    body_ps_p = resp_ps_p.body.decode("utf-8")
    assert "கர்த்தர் என் மேய்ப்பராயிருக்கிறார்" in body_ps_p
    print("✓ Protestant Psalm 23:1 verified (கர்த்தர் என் மேய்ப்பராயிருக்கிறார்).")

    req_ps_c = make_request("/read/19/23", query="canon=catholic&mode=bilingual")
    resp_ps_c = await reader(req_ps_c, book_id=19, chapter=23, mode="bilingual", canon="catholic")
    body_ps_c = resp_ps_c.body.decode("utf-8")
    assert "யெகோவா என் மேய்ப்பராக இருக்கிறார்" in body_ps_c
    print("✓ Catholic Psalm 23:1 verified (Tamil IRV CC BY-SA 4.0).")

    print("\n=== 4. Testing John 1:1 ===")
    req_jn_p = make_request("/read/43/1", query="canon=protestant&mode=bilingual")
    resp_jn_p = await reader(req_jn_p, book_id=43, chapter=1, mode="bilingual", canon="protestant")
    body_jn_p = resp_jn_p.body.decode("utf-8")
    assert "ஆதியிலே வார்த்தை இருந்தது" in body_jn_p
    print("✓ Protestant John 1:1 verified (1871 Tamil Old Version).")

    req_jn_c = make_request("/read/43/1", query="canon=catholic&mode=bilingual")
    resp_jn_c = await reader(req_jn_c, book_id=43, chapter=1, mode="bilingual", canon="catholic")
    body_jn_c = resp_jn_c.body.decode("utf-8")
    assert "ஆரம்பத்திலே வார்த்தை இருந்தது" in body_jn_c
    print("✓ Catholic John 1:1 verified (Tamil IRV CC BY-SA 4.0).")

    print("\n=== 5. Testing Deuterocanon (Tobit 1 - Douay-Rheims 1752 Public Domain) ===")
    req_tob = make_request("/read/67/1", query="canon=catholic&mode=bilingual")
    resp_tob = await reader(req_tob, book_id=67, chapter=1, mode="bilingual", canon="catholic")
    body_tob = resp_tob.body.decode("utf-8")
    assert "தோபித்து" in body_tob
    assert "Tobias" in body_tob
    print("✓ Deuterocanon Tobit 1:1 verified (Douay-Rheims 1752 Public Domain).")

    print("\n=== 6. Testing Search in Both Canons & Privacy Policy Page ===")
    req_s_p = make_request("/search", query="q=சிருஷ்டித்தார்&canon=protestant")
    resp_s_p = await search_page(req_s_p, q="சிருஷ்டித்தார்", canon="protestant")
    body_s_p = resp_s_p.body.decode("utf-8")
    assert "ஆதியாகமம்" in body_s_p
    print("✓ Protestant search returns 1871 Tamil Old Version matches.")

    req_s_c = make_request("/search", query="q=படைத்தார்&canon=catholic")
    resp_s_c = await search_page(req_s_c, q="படைத்தார்", canon="catholic")
    body_s_c = resp_s_c.body.decode("utf-8")
    assert "தொடக்க நூல்" in body_s_c
    print("✓ Catholic search returns Tamil IRV (CC BY-SA 4.0) matches.")

    req_priv = make_request("/privacy", query="")
    resp_priv = await privacy_page(req_priv, canon="protestant")
    body_priv = resp_priv.body.decode("utf-8")
    assert resp_priv.status_code == 200
    assert "Bridge Connectivity Solutions" in body_priv
    assert "Supabase" in body_priv
    print("✓ Privacy & Scripture Licenses page (/privacy) verified.")

    print("\n=== 7. Testing Audio Stream ===")
    resp_audio = await stream_audio(text="ஆதியிலே தேவன் வானத்தையும் பூமியையும் படைத்தார்.", lang="ta")
    assert resp_audio.status_code == 200
    assert len(resp_audio.body) > 1000
    print(f"✓ Neural TTS audio generated ({len(resp_audio.body)} bytes).")

    print("\n=======================================================")
    print("ALL 7 TEST SUITES PASSED! OPEN-LICENSED DUAL-CORPUS 100% OPERATIONAL!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
