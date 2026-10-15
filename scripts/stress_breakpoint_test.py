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

async def run_stress_step(concurrency: int, duration: float = 6.0, warmup: float = 4.0):
    connector = aiohttp.TCPConnector(
        limit=concurrency + 100,
        limit_per_host=concurrency + 100,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=20.0, connect=10.0)
    
    stop_event = asyncio.Event()
    measuring_event = asyncio.Event()
    results = {"success": 0, "errors": 0, "latencies": [], "error_types": {}}

    async def worker(worker_id: int, session: aiohttp.ClientSession):
        # Stagger initial connection during warmup to prevent instantaneous TCP SYN backlog flood
        if warmup > 0:
            stagger = (worker_id / max(1, concurrency)) * min(warmup * 0.8, 3.0)
            await asyncio.sleep(stagger)

        idx = worker_id
        while not stop_event.is_set():
            path = URLS[idx % len(URLS)]
            idx += 1
            url = f"http://127.0.0.1:8000{path}"
            t0 = time.perf_counter()
            in_measurement = measuring_event.is_set()
            try:
                async with session.get(url) as resp:
                    await resp.read()
                    t1 = time.perf_counter()
                    if in_measurement:
                        if resp.status == 200:
                            results["success"] += 1
                            results["latencies"].append(t1 - t0)
                        else:
                            results["errors"] += 1
                            code = f"HTTP_{resp.status}"
                            results["error_types"][code] = results["error_types"].get(code, 0) + 1
            except Exception as e:
                if in_measurement:
                    results["errors"] += 1
                    err_name = type(e).__name__
                    results["error_types"][err_name] = results["error_types"].get(err_name, 0) + 1
                await asyncio.sleep(0.05)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Pre-flight probe
        try:
            async with session.get("http://127.0.0.1:8000/api/health") as r:
                await r.read()
        except Exception as e:
            return {
                "concurrency": concurrency,
                "requests": 0,
                "success": 0,
                "errors": 1,
                "error_types": {type(e).__name__: 1},
                "rps": 0.0,
                "err_rate": 100.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "status": f"DEAD: {e}",
            }

        # 1. Spawn workers with gradual warmup ramp
        tasks = [asyncio.create_task(worker(i, session)) for i in range(concurrency)]
        await asyncio.sleep(warmup)

        # 2. Begin active measurement window
        t_measure_start = time.perf_counter()
        measuring_event.set()
        await asyncio.sleep(duration)
        stop_event.set()
        measuring_event.clear()
        await asyncio.gather(*tasks, return_exceptions=True)
        t_measure_end = time.perf_counter()

    elapsed = max(0.001, t_measure_end - t_measure_start)
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
    print("=" * 80)
    print(" WARMED-UP STRESS BREAKPOINT TEST (4.0s Warmup Ramp + 6.0s Measurement)")
    print("=" * 80)
    print(f"{'Concurrency':>12} | {'RPS':>9} | {'p50 (ms)':>10} | {'p95 (ms)':>10} | {'Errors':>10} | {'Status'}")
    print("-" * 80)

    test_concurrencies = [300, 500, 750, 1000, 1250, 1500, 1750, 2000]

    for c in test_concurrencies:
        print(f"[*] Testing concurrency={c} (warmup 4.0s + measure 6.0s)...", flush=True)
        res = await run_stress_step(c, duration=6.0, warmup=4.0)
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

        # 3.0s cooldown period between steps to allow TCP stack to clear sockets
        await asyncio.sleep(3.0)

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
