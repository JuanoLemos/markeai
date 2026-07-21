#!/usr/bin/env python3
"""MarketAI — CLI entry point. Main orchestration logic lives in orchestrator/ package."""
import argparse
import os
import sys
import signal
from pathlib import Path

from orchestrator import MarketAIOrchestrator, load_config

LOCK_FILE = Path(__file__).parent / ".orchestrator.lock"


def _lock_acquire():
    """Prevent duplicate orchestrator instances via lockfile with PID check."""
    if LOCK_FILE.exists():
        try:
            stale_pid = int(LOCK_FILE.read_text().strip())
            try:
                os.kill(stale_pid, 0)
            except OSError:
                pass
            else:
                import subprocess
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     f"Get-CimInstance Win32_Process -Filter \"ProcessId={stale_pid}\" | "
                     "Where-Object { $_.CommandLine -match 'orchestrator' } | "
                     "Select-Object -ExpandProperty ProcessId"],
                    capture_output=True, text=True, timeout=5,
                )
                if r.stdout.strip():
                    print(f"[orchestrator] Another instance is already running (PID {stale_pid}). Exiting.")
                    sys.exit(0)
        except (ValueError, FileNotFoundError):
            pass
        LOCK_FILE.unlink(missing_ok=True)
    LOCK_FILE.write_text(str(os.getpid()))


def _lock_release():
    LOCK_FILE.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="MarketAI - Trading Multi-Capa")
    parser.add_argument("--mode", choices=["once", "loop", "backtest", "report", "cron", "replay"], default="once")
    parser.add_argument("--paper", action="store_true", default=True)
    parser.add_argument("--market", type=str, default=None)
    parser.add_argument("--task", type=str, default="daily")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--deepseek", action="store_true", default=False)
    args = parser.parse_args()

    if args.mode == "loop":
        _lock_acquire()

    try:
        config = load_config()
        if args.market:
            for m in ["polymarket", "forex", "stocks"]:
                if m != args.market:
                    config["markets"][m]["enabled"] = False
        orch = MarketAIOrchestrator(config, mode="paper" if args.paper else "real")
        if args.mode == "once":
            orch.run_once()
        elif args.mode == "loop":
            orch.run_loop()
        elif args.mode == "backtest":
            orch.run_backtest()
        elif args.mode == "report":
            orch.run_report()
        elif args.mode == "cron":
            orch.run_cron(task=args.task)
        elif args.mode == "replay":
            orch.run_replay(market=args.market or "stocks", days=args.days, use_deepseek=args.deepseek)
    finally:
        if args.mode == "loop":
            _lock_release()


if __name__ == "__main__":
    main()
