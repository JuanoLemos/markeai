#!/usr/bin/env python3
"""MarketAI — CLI entry point. Main orchestration logic lives in orchestrator/ package."""
import argparse

from orchestrator import MarketAIOrchestrator, load_config


def main():
    parser = argparse.ArgumentParser(description="MarketAI - Trading Multi-Capa")
    parser.add_argument("--mode", choices=["once", "loop", "backtest", "report", "cron", "replay"], default="once")
    parser.add_argument("--paper", action="store_true", default=True)
    parser.add_argument("--market", type=str, default=None)
    parser.add_argument("--task", type=str, default="daily")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--deepseek", action="store_true", default=False)
    args = parser.parse_args()
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


if __name__ == "__main__":
    main()
