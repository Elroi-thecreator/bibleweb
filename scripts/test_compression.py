#!/usr/bin/env python3
"""
Test HTTP Gzip & Brotli Compression on the Bible Web FastAPI Server.
Verifies wire payload sizes, Content-Encoding headers, and data integrity.
Uses http.client to inspect raw wire bytes without automatic client decoding.
"""

import http.client
import gzip
import subprocess
import sys
import time
import urllib.parse
import brotli

def fetch_raw_response(host: str, port: int, path: str, accept_encoding: str):
    conn = http.client.HTTPConnection(host, port, timeout=5)
    headers = {}
    if accept_encoding:
        headers["Accept-Encoding"] = accept_encoding
    conn.request("GET", path, headers=headers)
    resp = conn.getresponse()
    wire_bytes = resp.read()
    content_encoding = resp.getheader("Content-Encoding")
    conn.close()
    return wire_bytes, content_encoding

def test_compression():
    port = 8765
    server_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"
    ]
    proc = subprocess.Popen(server_cmd)

    try:
        # Wait for startup
        started = False
        for _ in range(30):
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                conn.request("GET", "/api/health")
                r = conn.getresponse()
                if r.status == 200:
                    r.read()
                    conn.close()
                    started = True
                    break
            except Exception:
                time.sleep(0.2)

        if not started:
            raise RuntimeError("Uvicorn test server failed to start")

        target_path = "/read/43/1?mode=bilingual"

        print("=" * 72)
        print(" HTTP COMPRESSION BENCHMARK: /read/43/1 (John 1 Bilingual)")
        print("=" * 72)

        # 1. Uncompressed (Raw)
        raw_bytes, raw_enc = fetch_raw_response("127.0.0.1", port, target_path, "identity")
        raw_size = len(raw_bytes)
        print(f" 1. Uncompressed (Raw Wire):")
        print(f"    Payload Size:     {raw_size:>8,} bytes ({raw_size / 1024:.1f} KB)")
        print(f"    Content-Encoding: {raw_enc or 'None (Identity)'}")

        # 2. Gzip
        gzip_bytes, gzip_enc = fetch_raw_response("127.0.0.1", port, target_path, "gzip")
        gzip_size = len(gzip_bytes)
        decompressed_gzip = gzip.decompress(gzip_bytes)
        gzip_pct = ((raw_size - gzip_size) / raw_size) * 100.0
        print(f"\n 2. Gzip Compression (gzip):")
        print(f"    Wire Size:        {gzip_size:>8,} bytes ({gzip_size / 1024:.1f} KB)")
        print(f"    Bandwidth Saved:  {gzip_pct:>7.1f}% reduction")
        print(f"    Content-Encoding: {gzip_enc}")
        print(f"    Integrity Match:  {decompressed_gzip == raw_bytes}")

        # 3. Brotli (br)
        br_bytes, br_enc = fetch_raw_response("127.0.0.1", port, target_path, "br, gzip, deflate")
        br_size = len(br_bytes)
        decompressed_br = brotli.decompress(br_bytes)
        br_pct = ((raw_size - br_size) / raw_size) * 100.0
        print(f"\n 3. Brotli Compression (br):")
        print(f"    Wire Size:        {br_size:>8,} bytes ({br_size / 1024:.1f} KB)")
        print(f"    Bandwidth Saved:  {br_pct:>7.1f}% reduction")
        print(f"    Content-Encoding: {br_enc}")
        print(f"    Integrity Match:  {decompressed_br == raw_bytes}")

        print("=" * 72)
        assert gzip_enc == "gzip", f"Expected gzip, got {gzip_enc}"
        assert br_enc == "br", f"Expected br, got {br_enc}"
        assert decompressed_gzip == raw_bytes, "Gzip decompression mismatch"
        assert decompressed_br == raw_bytes, "Brotli decompression mismatch"
        print(" [SUCCESS] Both Gzip and Brotli compressions verified with 100% integrity!")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_compression()
