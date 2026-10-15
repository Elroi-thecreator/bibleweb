#!/usr/bin/env python3
"""
Holy Bible Web Application - High-Performance Asynchronous Load Testing Suite
Measures throughput (RPS), latency percentiles (p50, p90, p95, p99), error rates,
and saturation limits for the FastAPI/SQLite Bible Web Server.
"""

import argparse
import asyncio
import json
import math
import os
import random
import sys
import time
from typing import Dict, List, Optional, Tuple
import aiohttp

# Ensure Windows terminal prints UTF-8 Tamil characters properly
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Standardized benchmark endpoints
ENDPOINTS = {
    "health": [
        ("/api/health", "GET", "Health API (Zero DB)"),
    ],
    "reader": [
        ("/read/43/1?mode=bilingual&canon=protestant", "GET", "Reader: John 1 Bilingual"),
        ("/read/1/1?mode=bilingual&canon=protestant", "GET", "Reader: Genesis 1 Bilingual"),
        ("/read/19/23?mode=bilingual&canon=protestant", "GET", "Reader: Psalm 23 Bilingual"),
        ("/read/43/1?mode=bilingual&canon=catholic", "GET", "Reader: Catholic John 1"),
        ("/read/67/1?mode=bilingual&canon=catholic", "GET", "Reader: Deuterocanon Tobit 1"),
    ],
    "search": [
        ("/search?q=love&canon=protestant", "GET", "Search: English 'love'"),
        ("/search?q=தேவன்&canon=protestant", "GET", "Search: Tamil 'Devan'"),
        ("/search?q=இயேசு&canon=catholic", "GET", "Search: Catholic 'Yesu'"),
    ],
    "songs": [
        ("/songs", "GET", "Songs Directory Page"),
        ("/api/songs?q=இயேசு&limit=20", "GET", "Songs API Search"),
        ("/songs/2", "GET", "Song Detail Page (ID 2)"),
    ],
    "quiz": [
        ("/api/quiz/questions?limit=10", "GET", "Quiz API (10 Questions)"),
        ("/quiz", "GET", "Quiz Landing Page"),
    ],
    "landing": [
        ("/", "GET", "Landing Page (Protestant)"),
        ("/?canon=catholic", "GET", "Landing Page (Catholic)"),
        ("/plans", "GET", "Reading Plans Index"),
    ],
}

# Weighted distribution for realistic user simulation
MIXED_WEIGHTS = [
    ("reader", 0.45),
    ("landing", 0.20),
    ("search", 0.15),
    ("songs", 0.10),
    ("quiz", 0.05),
    ("health", 0.05),
]


class LoadTestResult:
    def __init__(self, name: str, concurrency: int, duration_target: float):
        self.name = name
        self.concurrency = concurrency
        self.duration_target = duration_target
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.latencies: List[float] = []
        self.status_codes: Dict[int, int] = {}
        self.errors: int = 0
        self.bytes_received: int = 0
        self.endpoint_stats: Dict[str, Dict] = {}

    @property
    def total_requests(self) -> int:
        return len(self.latencies) + self.errors

    @property
    def actual_duration(self) -> float:
        return max(0.001, self.end_time - self.start_time)

    @property
    def rps(self) -> float:
        return len(self.latencies) / self.actual_duration

    @property
    def error_rate(self) -> float:
        tot = self.total_requests
        return (self.errors / tot * 100.0) if tot > 0 else 0.0

    @property
    def throughput_mb_s(self) -> float:
        return (self.bytes_received / (1024 * 1024)) / self.actual_duration

    def calculate_percentiles(self) -> Dict[str, float]:
        if not self.latencies:
            return {k: 0.0 for k in ["min", "p50", "p90", "p95", "p99", "max", "avg"]}
        s = sorted(self.latencies)
        n = len(s)
        return {
            "min": s[0] * 1000.0,
            "p50": s[int(n * 0.50)] * 1000.0,
            "p90": s[min(n - 1, int(n * 0.90))] * 1000.0,
            "p95": s[min(n - 1, int(n * 0.95))] * 1000.0,
            "p99": s[min(n - 1, int(n * 0.99))] * 1000.0,
            "max": s[-1] * 1000.0,
            "avg": (sum(s) / n) * 1000.0,
        }

    def summary_dict(self) -> Dict:
        pct = self.calculate_percentiles()
        return {
            "name": self.name,
            "concurrency": self.concurrency,
            "duration_sec": round(self.actual_duration, 2),
            "total_requests": self.total_requests,
            "successful_requests": len(self.latencies),
            "errors": self.errors,
            "error_rate_pct": round(self.error_rate, 2),
            "rps": round(self.rps, 1),
            "throughput_mb_s": round(self.throughput_mb_s, 2),
            "latencies_ms": {k: round(v, 2) for k, v in pct.items()},
            "status_codes": self.status_codes,
            "endpoints": self.endpoint_stats,
        }


async def worker(
    session: aiohttp.ClientSession,
    base_url: str,
    endpoint_picker,
    result: LoadTestResult,
    stop_event: asyncio.Event,
):
    while not stop_event.is_set():
        path, method, desc = endpoint_picker()
        url = f"{base_url.rstrip('/')}{path}"
        t0 = time.perf_counter()
        try:
            async with session.request(method, url) as response:
                body = await response.read()
                t1 = time.perf_counter()
                latency = t1 - t0
                result.latencies.append(latency)
                result.bytes_received += len(body)
                code = response.status
                result.status_codes[code] = result.status_codes.get(code, 0) + 1

                # Track per-endpoint
                if desc not in result.endpoint_stats:
                    result.endpoint_stats[desc] = {"count": 0, "latencies": [], "errors": 0}
                result.endpoint_stats[desc]["count"] += 1
                result.endpoint_stats[desc]["latencies"].append(latency)
        except Exception:
            result.errors += 1
            if desc not in result.endpoint_stats:
                result.endpoint_stats[desc] = {"count": 0, "latencies": [], "errors": 0}
            result.endpoint_stats[desc]["errors"] += 1


def make_endpoint_picker(scenario: str):
    if scenario == "mixed":
        categories = [item[0] for item in MIXED_WEIGHTS]
        weights = [item[1] for item in MIXED_WEIGHTS]

        def pick():
            chosen_cat = random.choices(categories, weights=weights, k=1)[0]
            return random.choice(ENDPOINTS[chosen_cat])

        return pick
    elif scenario in ENDPOINTS:
        pool = ENDPOINTS[scenario]

        def pick():
            return random.choice(pool)

        return pick
    else:
        # Default to all endpoints equally
        pool = []
        for cat in ENDPOINTS.values():
            pool.extend(cat)

        def pick():
            return random.choice(pool)

        return pick


async def run_scenario(
    base_url: str,
    scenario_name: str,
    concurrency: int,
    duration: float,
) -> LoadTestResult:
    result = LoadTestResult(scenario_name, concurrency, duration)
    endpoint_picker = make_endpoint_picker(scenario_name)

    stop_event = asyncio.Event()
    connector = aiohttp.TCPConnector(
        limit=concurrency + 50,
        limit_per_host=concurrency + 50,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=10.0, connect=3.0)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Warmup probe
        try:
            async with session.get(f"{base_url.rstrip('/')}/api/health") as resp:
                await resp.read()
        except Exception as e:
            print(f"[!] Warmup connection failed to {base_url}/api/health: {e}")
            result.errors += 1
            return result

        result.start_time = time.perf_counter()
        workers = [
            asyncio.create_task(worker(session, base_url, endpoint_picker, result, stop_event))
            for _ in range(concurrency)
        ]

        await asyncio.sleep(duration)
        stop_event.set()
        await asyncio.gather(*workers, return_exceptions=True)
        result.end_time = time.perf_counter()

    return result


def print_result_table(res: LoadTestResult):
    p = res.calculate_percentiles()
    print("\n" + "=" * 78)
    print(f" LOAD TEST RESULT: {res.name.upper()} (Concurrency: {res.concurrency}, Duration: {res.actual_duration:.1f}s)")
    print("=" * 78)
    print(f" Requests Completed:   {res.total_requests:,}")
    print(f" Throughput (RPS):     {res.rps:,.1f} req/s")
    print(f" Network Transfer:     {res.throughput_mb_s:.2f} MB/s")
    print(f" Error Rate:           {res.error_rate:.2f}% ({res.errors} errors)")
    print(f" Status Codes:         {dict(sorted(res.status_codes.items()))}")
    print("-" * 78)
    print(" LATENCY DISTRIBUTION (Milliseconds):")
    print(f"   Min:   {p['min']:7.2f} ms |   p50 (Median): {p['p50']:7.2f} ms")
    print(f"   Avg:   {p['avg']:7.2f} ms |   p90:          {p['p90']:7.2f} ms")
    print(f"   p95:   {p['p95']:7.2f} ms |   p99:          {p['p99']:7.2f} ms")
    print(f"   Max:   {p['max']:7.2f} ms")
    print("-" * 78)

    if res.endpoint_stats and len(res.endpoint_stats) > 1:
        print(" BREAKDOWN BY ENDPOINT:")
        print(f"   {'Endpoint Description':<35} | {'Reqs':>6} | {'Avg (ms)':>9} | {'p95 (ms)':>9} | {'Errs':>5}")
        print("   " + "-" * 72)
        for desc, st in sorted(res.endpoint_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            lats = st["latencies"]
            avg_l = (sum(lats) / len(lats) * 1000.0) if lats else 0.0
            slats = sorted(lats)
            p95_l = (slats[min(len(slats) - 1, int(len(slats) * 0.95))] * 1000.0) if slats else 0.0
            print(f"   {desc:<35} | {st['count']:>6} | {avg_l:>9.2f} | {p95_l:>9.2f} | {st['errors']:>5}")
        print("-" * 78)


async def main_async():
    parser = argparse.ArgumentParser(description="Holy Bible Web Server Load Testing Tool")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL to test")
    parser.add_argument("--duration", type=float, default=10.0, help="Test duration in seconds per stage")
    parser.add_argument("--concurrency", type=int, default=50, help="Concurrent workers")
    parser.add_argument(
        "--scenario",
        default="mixed",
        choices=["mixed", "health", "reader", "search", "songs", "quiz", "landing", "all", "ramp"],
        help="Test scenario to execute",
    )
    parser.add_argument("--output-json", default=None, help="Save summary report to JSON file")
    args = parser.parse_args()

    print(f"Target Host:     {args.url}")
    print(f"Scenario:        {args.scenario}")

    if args.scenario == "ramp":
        # Concurrency ramping to find saturation potential curve
        concurrencies = [5, 15, 30, 60, 120, 250]
        ramp_results = []
        print("\n[+] Initiating Concurrency Ramping Test to discover saturation limit...")
        print(f"{'Concurrency':>12} | {'RPS':>10} | {'Avg Latency':>13} | {'p95 Latency':>13} | {'Error Rate':>11}")
        print("-" * 70)

        for c in concurrencies:
            res = await run_scenario(args.url, "mixed", c, args.duration)
            p = res.calculate_percentiles()
            ramp_results.append(res.summary_dict())
            print(
                f"{c:>12} | {res.rps:>10.1f} | {p['avg']:>10.2f} ms | {p['p95']:>10.2f} ms | {res.error_rate:>10.2f}%"
            )
            await asyncio.sleep(1.0)

        print("-" * 70)
        # Find peak RPS
        peak = max(ramp_results, key=lambda x: x["rps"])
        print(f"\n[*] Peak Throughput Achieved: {peak['rps']:.1f} RPS at Concurrency = {peak['concurrency']}")

        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump({"ramp_test": ramp_results}, f, indent=2)
            print(f"Saved ramp report to {args.output_json}")

    elif args.scenario == "all":
        # Run isolated benchmarks across all major scenarios
        scenarios = ["health", "reader", "search", "songs", "quiz", "landing", "mixed"]
        all_res = []
        for sc in scenarios:
            print(f"\n[*] Benchmarking scenario: {sc} (concurrency={args.concurrency}, duration={args.duration}s)...")
            res = await run_scenario(args.url, sc, args.concurrency, args.duration)
            print_result_table(res)
            all_res.append(res.summary_dict())
            await asyncio.sleep(1.0)

        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump({"benchmarks": all_res}, f, indent=2)
            print(f"\nSaved benchmark results to {args.output_json}")
    else:
        print(f"\n[*] Benchmarking scenario: {args.scenario} (concurrency={args.concurrency}, duration={args.duration}s)...")
        res = await run_scenario(args.url, args.scenario, args.concurrency, args.duration)
        print_result_table(res)

        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(res.summary_dict(), f, indent=2)
            print(f"Saved report to {args.output_json}")


if __name__ == "__main__":
    asyncio.run(main_async())
