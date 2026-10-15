#!/usr/bin/env python3
"""
Holy Bible Web Application - System Failure & Breakpoint Stress Test
Probes increasing concurrency levels [500, 750, 1000, 1500, 2000, 2500, 3000]
to discover the exact failure modes:
1. Latency degradation breakpoint
2. Client timeout cascade breakpoint
3. Socket / TCP backlog drop failure
4. Total system collapse threshold
"""

import asyncio
import json
import os
import sys
import time
import aiohttp

# Ensure Windows terminal prints UTF-8 characters properly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Test endpoints
URLS = [
    "/read/43/1?mode=bilingual&canon=protestant",
    "/search?q=love&canon=protestant",
    "/songs",
    "/api/health",
    "/",
]

async def run_stress_step(concurrency: int, duration: float = 5.0):
    connector = aiohttp.TCPConnector(
        limit=concurrency + 50,
        limit_per_host=concurrency + 50,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=15.0, connect=8.0)
    
    stop_event = asyncio.Event()
    results = {"success": 0, "errors": 0, "latencies": [], "error_types": {}}

    async def worker(session):
        idx = 0
        while not stop_event.is_set():
            path = URLS[idx % len(URLS)]
            idx += 1
            url = f"http://127.0.0.1:8000{path}"
            t0 = time.perf_counter()
            try:
                async with session.get(url) as resp:
                    await resp.read()
                    t1 = time.perf_counter()
                    if resp.status == 200:
                        results["success"] += 1
                        results["latencies"].append(t1 - t0)
                    else:
                        results["errors"] += 1
                        code = f"HTTP_{resp.status}"
                        results["error_types"][code] = results["error_types"].get(code, 0) + 1
            except Exception as e:
                results["errors"] += 1
                err_name = type(e).__name__
                results["error_types"][err_name] = results["error_types"].get(err_name, 0) + 1

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Probe
        try:
            async with session.get("http://127.0.0.1:8000/api/health") as r:
                await r.read()
        except Exception as e:
            return {"concurrency": concurrency, "rps": 0, "error_rate": 100.0, "p50": 0, "p95": 0, "status": f"DEAD: {e}"}

        t_start = time.perf_counter()
        tasks = [asyncio.create_task(worker(session)) for _ in range(concurrency)]
        await asyncio.sleep(duration)
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        t_end = time.perf_counter()

    elapsed = max(0.001, t_end - t_start)
    tot = results["success"] + results["errors"]
    err_rate = (results["errors"] / tot * 100.0) if tot > 0 else 100.0
    rps = results["success"] / elapsed

    s_lat = sorted(results["latencies"])
    n = len(s_lat)
    p50 = (s_lat[int(n * 0.5)] * 1000.0) if n > 0 else 0.0
    p95 = (s_lat[min(n - 1, int(n * 0.95))] * 1000.0) if n > 0 else 0.0

    return {
        "concurrency": concurrency,
        "requests": tot,
        "success": results["success"],
        "errors": results["errors"],
        "error_types": results["error_types"],
        "rps": round(rps, 1),
        "err_rate": round(err_rate, 2),
        "p50_ms": round(p50, 1),
        "p95_ms": round(p95, 1),
    }


async def main():
    print("=" * 75)
    print(" STRESS BREAKPOINT TEST: DISCOVERING TOTAL FAILURE THRESHOLD")
    print("=" * 75)
    print(f"{'Concurrency':>12} | {'RPS':>9} | {'p50 (ms)':>10} | {'p95 (ms)':>10} | {'Errors':>10} | {'Status'}")
    print("-" * 75)

    test_concurrencies = [500, 750, 1000, 1500, 2000, 2500, 3000]

    for c in test_concurrencies:
        res = await run_stress_step(c, duration=5.0)
        status_desc = "HEALTHY"
        if res["err_rate"] > 50.0:
            status_desc = "TOTAL FAILURE"
        elif res["err_rate"] > 10.0:
            status_desc = "SEVERE DEGRADATION"
        elif res["err_rate"] > 1.0 or res["p95_ms"] > 5000:
            status_desc = "SATURATED / SLOW"

        print(
            f"{res['concurrency']:>12} | {res['rps']:>9.1f} | {res['p50_ms']:>10.1f} | {res['p95_ms']:>10.1f} | {res['err_rate']:>9.2f}% | {status_desc}"
        )
        if res.get("error_types"):
            print(f"             └── Errors: {res['error_types']}")

        if res["err_rate"] >= 80.0:
            print("\n[!] Total System Failure Threshold reached.")
            break
        await asyncio.sleep(1.5)

    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(main())
