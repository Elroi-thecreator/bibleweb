#!/usr/bin/env python3
"""
Holy Bible Web Server - Production Multi-Worker Launcher
Automatically detects available CPU cores and spawns optimized Uvicorn worker processes.
"""

import argparse
import multiprocessing
import os
import sys

# Ensure repository root is in sys.path and environment for worker processes
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if "PYTHONPATH" not in os.environ or PROJECT_ROOT not in os.environ["PYTHONPATH"]:
    os.environ["PYTHONPATH"] = PROJECT_ROOT + (os.pathsep + os.environ["PYTHONPATH"] if "PYTHONPATH" in os.environ else "")

def get_recommended_workers() -> int:
    """Calculates ideal worker processes: min(8, max(2, cpu_count))."""
    env_workers = os.getenv("WEB_CONCURRENCY")
    if env_workers:
        try:
            return max(1, int(env_workers))
        except ValueError:
            pass
    try:
        cpus = multiprocessing.cpu_count()
        # For I/O and template bound FastAPI apps, cpu_count workers is efficient and memory safe
        return max(2, min(8, cpus))
    except Exception:
        return 2

def main():
    parser = argparse.ArgumentParser(description="Holy Bible Multi-Worker Production Server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Bind port (default: 8000)")
    parser.add_argument(
        "--workers",
        type=int,
        default=get_recommended_workers(),
        help=f"Number of worker processes (default: {get_recommended_workers()} based on available CPUs)",
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development only)")
    parser.add_argument("--log-level", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument(
        "--loop",
        default="auto",
        help="Event loop implementation (default: auto)",
    )
    args = parser.parse_args()

    import uvicorn
    import psutil

    proc = psutil.Process()
    cpus = multiprocessing.cpu_count() if hasattr(multiprocessing, "cpu_count") else "Unknown"
    handles = proc.num_handles() if hasattr(proc, "num_handles") else 0
    threads = proc.num_threads()

    loop_desc = "SelectorEventLoop (Multi-Process Windows)" if (sys.platform == "win32" and args.workers > 1) else args.loop

    print("=" * 72)
    print(" Holy Bible Web Application - Multi-Worker Server")
    print("=" * 72)
    print(f" Host:             http://{args.host}:{args.port}")
    print(f" CPU Cores:        {cpus}")
    print(f" Active Workers:   {args.workers}")
    print(f" Event Loop:       {loop_desc}")
    print(f" Supervisor PID:   {proc.pid} (Initial Handles: {handles}, Threads: {threads})")
    print(f" Auto-Reload:      {args.reload}")
    print(f" Log Level:        {args.log_level}")
    print("=" * 72)

    # In reload mode, uvicorn requires workers=1
    workers = 1 if args.reload else args.workers

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        workers=workers,
        reload=args.reload,
        log_level=args.log_level,
        loop=args.loop,
        access_log=True,
    )

if __name__ == "__main__":
    main()
