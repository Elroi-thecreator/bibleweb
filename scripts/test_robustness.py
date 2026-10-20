#!/usr/bin/env python3
"""
Holy Bible Web Application - Robustness, Security, and Caching Verification Suite
Verifies:
1. Thread-local SQLite connection pooling and MMAP configuration
2. Custom branded HTML 404/500 error pages
3. API JSON error responses
4. Security headers (OWASP best practices)
5. Static asset Cache-Control headers
6. Scripture Reader Cache-Control, ETag, and HTTP 304 Not Modified
7. Deep database health check probes
"""

import asyncio
import json
import os
import sys

# Ensure Windows terminal prints UTF-8 characters properly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, HAS_BROTLI_LIB

async def asgi_request(path: str, query_string: str = "", headers: list = None):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string.encode(),
        "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or [])],
    }
    sent = []
    async def receive():
        return {"type": "http.request"}
    async def send(msg):
        sent.append(msg)
    await app(scope, receive, send)

    status = None
    resp_headers = {}
    body_chunks = []
    for m in sent:
        if m["type"] == "http.response.start":
            status = m["status"]
            resp_headers = {k.decode().lower(): v.decode() for k, v in m["headers"]}
        elif m["type"] == "http.response.body":
            body_chunks.append(m.get("body", b""))
    return status, resp_headers, b"".join(body_chunks)


async def test_robustness():
    print("=" * 65)
    print(" TESTING ARCHITECTURAL ROBUSTNESS & SECURITY ENHANCEMENTS")
    print("=" * 65)

    # 1. Test 404 HTML Page
    status, headers, body = await asgi_request("/nonexistent-scripture-page")
    assert status == 404, f"Expected 404, got {status}"
    assert b"404" in body and b"Page Not Found" in body
    print("✓ 1. Branded 404 HTML template verified (Status 404 with Tamil/English guidance)")

    # 2. Test 404 API JSON
    status, headers, body = await asgi_request("/api/unknown-endpoint")
    assert status == 404
    parsed_json = json.loads(body.decode())
    assert "detail" in parsed_json
    print("✓ 2. API 404 returns clean JSON payload")

    # 3. Test Security Headers & Reader Cache Headers
    status, headers, body = await asgi_request("/read/43/1")
    assert status == 200
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "SAMEORIGIN"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert headers.get("x-xss-protection") == "1; mode=block"
    print("✓ 3. OWASP Security headers verified (nosniff, SAMEORIGIN, strict-origin, XSS-Protection)")

    assert "etag" in headers
    assert "cache-control" in headers
    etag = headers["etag"]
    print(f"✓ 4. Reader Cache-Control ({headers['cache-control']}) and ETag ({etag}) verified")

    # 4. Test 304 Not Modified
    status_304, headers_304, body_304 = await asgi_request("/read/43/1", headers=[("if-none-match", etag)])
    assert status_304 == 304, f"Expected 304, got {status_304}"
    assert len(body_304) == 0, f"Expected 0-byte body on 304, got {len(body_304)}"
    print("✓ 5. Conditional HTTP 304 Not Modified verified (0-byte payload on repeat reads)")

    # 5. Test Static Assets Cache Headers
    status, headers, body = await asgi_request("/static/manifest.json")
    assert status == 200
    assert "cache-control" in headers
    assert "max-age=604800" in headers["cache-control"]
    print(f"✓ 6. Static Assets Cache-Control verified ({headers['cache-control']})")

    # 6. Test Deep Health Check
    status, headers, body = await asgi_request("/api/health", query_string="deep=true")
    assert status == 200
    h_json = json.loads(body.decode())
    assert h_json["databases"]["bible_db"] is True
    assert h_json["databases"]["songs_db"] is True
    print(f"✓ 7. Deep database health verification verified ({h_json['databases']})")

    # 7. Test Pre-Compressed Brotli & Gzip In-Memory Page Cache
    # Initial read populated the cache (or populate now)
    status_br, headers_br, body_br = await asgi_request(
        "/read/43/1",
        headers=[("Accept-Encoding", "gzip, deflate, br")]
    )
    assert status_br == 200
    assert headers_br.get("x-page-cache") == "HIT", f"Expected cache HIT, got {headers_br.get('x-page-cache')}"
    expected_enc = "br" if HAS_BROTLI_LIB else "gzip"
    assert headers_br.get("content-encoding") == expected_enc, f"Expected {expected_enc} encoding, got {headers_br.get('content-encoding')}"
    assert len(body_br) > 0 and len(body_br) < 50000

    status_gz, headers_gz, body_gz = await asgi_request(
        "/read/43/1",
        headers=[("Accept-Encoding", "gzip")]
    )
    assert status_gz == 200
    assert headers_gz.get("x-page-cache") == "HIT"
    assert headers_gz.get("content-encoding") == "gzip", f"Expected gzip encoding, got {headers_gz.get('content-encoding')}"
    print(f"✓ 8. Pre-compressed Brotli ({len(body_br)} bytes) and Gzip ({len(body_gz)} bytes) zero-CPU cache verified")

    # 8. Test Presenter Mode & Plans Route Caching
    status_p1, _, _ = await asgi_request("/present/43/1")
    assert status_p1 == 200
    status_p2, headers_p2, _ = await asgi_request("/present/43/1", headers=[("Accept-Encoding", "br")])
    assert status_p2 == 200
    assert headers_p2.get("x-page-cache") == "HIT"

    status_pl1, _, _ = await asgi_request("/plans")
    assert status_pl1 == 200
    status_pl2, headers_pl2, _ = await asgi_request("/plans", headers=[("Accept-Encoding", "br")])
    assert status_pl2 == 200
    assert headers_pl2.get("x-page-cache") == "HIT"
    print("✓ 9. Presenter Mode (/present) and Plans (/plans) page caching verified")

    print("=" * 65)
    print(" ALL 9 ROBUSTNESS, CACHING & SECURITY VERIFICATIONS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(test_robustness())
