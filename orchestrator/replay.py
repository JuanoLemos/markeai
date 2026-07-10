"""
orchestrator/replay.py
Replay engine — runs the full MarketAI pipeline against historical data.
Extracted from orchestrator.py to keep the main class focused.
"""
import json
from pathlib import Path


def run_replay(orch, market: str, days: int = 90, use_deepseek: bool = False):
    """
    Replay trading decisions on historical OHLCV data.
    Creates an isolated PaperBroker per ticker (state in data/cache/replay_<TICKER>.json).

    Args:
        orch: MarketAIOrchestrator instance (uses orch.yf_collector, orch.tech_analyzer,
              orch.macro_analyzer, orch.fund_analyzer, orch.fusion_engine, orch.decider,
              orch.markets_cfg, orch.config, orch.log).
        market: 'polymarket' | 'forex' | 'stocks'
        days: Lookback period in days
        use_deepseek: If True, call DeepSeek per decision (slow). Default False (use fusion only).
    """
    import numpy as np
    from execution.paper_broker import PaperBroker

    orch.log.info(f"=== Replay {market} - {days} dias ===")
    market_cfg = orch.markets_cfg.get(market, {})
    if not market_cfg:
        orch.log.error(f"Unknown market: {market}")
        return

    tickers = market_cfg.get("pairs" if market == "forex" else "tickers", [])
    base_dir = Path(__file__).parent.parent

    for ticker in tickers:
        orch.log.info(f"  Replaying {ticker}...")
        data = orch.yf_collector.get_historical(ticker, f"{days}d", "1h")
        if data.empty or len(data) < 100:
            orch.log.info(f"    SKIP - {len(data)} rows")
            continue

        pb = PaperBroker(initial_balance=1000, state_path=str(base_dir / "data" / "cache" / f"replay_{ticker}.json"))
        warmup, step = 50, max(1, len(data) // 100)
        trades = []

        for i in range(warmup, len(data), step):
            chunk = data.iloc[:i + 1]
            bar = chunk.iloc[-1]
            price = float(bar["close"])
            volume = float(bar.get("volume", 0))
            change = 0
            if i >= 24:
                change = (price / float(chunk.iloc[-24]["close"]) - 1) * 100

            price_data = {"price": price, "change_24h_pct": change, "volume_24h": volume}

            layer_results = {}
            tr = orch.tech_analyzer.analyze(chunk)
            if tr and tr.get("score", 50) != 50:
                layer_results["technical"] = tr
            mr = orch.macro_analyzer.analyze(dxy=orch.yf_collector.get_dxy(), vix=orch.yf_collector.get_vix(), market_type=market)
            if mr and mr.get("score", 50) != 50:
                layer_results["macro"] = mr
            if market == "stocks" and orch.config["layers"]["fundamental"]["enabled"]:
                fr = orch.fund_analyzer.analyze(ticker, price_data, orch.yf_collector.get_fundamentals(ticker))
                if fr and fr.get("score", 50) != 50:
                    layer_results["fundamental"] = fr

            fused = orch.fusion_engine.fuse(layer_results, market)
            if fused["signal"] != "WAIT" and fused.get("confidence", 0) >= orch.profiles_config.get("normal", {}).get("per_market", {}).get(market, {}).get("min_confidence", 40):
                decision = fused
                if use_deepseek:
                    decision = orch.decider.decide(market, ticker, fused, {}, fused.get("layer_scores", {}))
                if decision and decision.get("signal", "WAIT") != "WAIT":
                    sl_pct = decision.get("stop_loss_pct") or 5
                    tp_pct = decision.get("take_profit_pct") or 10
                    sl_cfg = orch.config["risk"]
                    sl_pct = max(sl_cfg.get("sl_min_pct", 1), min(sl_cfg.get("sl_max_pct", 8), sl_pct))
                    tp_pct = max(sl_cfg.get("tp_min_pct", 2), min(sl_cfg.get("tp_max_pct", 15), tp_pct))
                    trade = pb.open_position(
                        market=market, ticker=ticker, signal=decision["signal"],
                        entry_price=decision.get("entry_price", price) or price,
                        size_usd=decision.get("position_size_usd") or market_cfg.get("max_position_usd", 30),
                        stop_loss_pct=sl_pct,
                        take_profit_pct=tp_pct,
                        confidence=decision.get("confidence", fused.get("confidence", 50)),
                        strategy_used=f"{market}_{fused['signal']}",
                    )
                    if trade and "error" not in trade:
                        trades.append(trade)

            closed = pb.check_stops({ticker: price})
            for c in closed:
                trades.append(c)

        for pid in list(pb.positions.keys()):
            c = pb.close_position(pid, price, "replay_end")
            if c:
                trades.append(c)

        closed_trades = [t for t in trades if "pnl_usd" in t]
        wins = sum(1 for t in closed_trades if t.get("pnl_usd", 0) > 0)
        losses = len(closed_trades) - wins
        total_pnl = sum(t.get("pnl_usd", 0) for t in closed_trades)
        win_rate = wins / len(closed_trades) * 100 if closed_trades else 0

        pnl_pcts = [t.get("pnl_pct", 0) for t in closed_trades]
        sharpe = np.mean(pnl_pcts) / (np.std(pnl_pcts) + 1e-10) * np.sqrt(252) if len(pnl_pcts) > 1 else 0

        gross_wins = sum(t["pnl_usd"] for t in closed_trades if t["pnl_usd"] > 0)
        gross_losses = abs(sum(t["pnl_usd"] for t in closed_trades if t["pnl_usd"] <= 0))
        pf = gross_wins / gross_losses if gross_losses > 0 else float("inf")

        cum = np.cumsum([t["pnl_usd"] for t in closed_trades]) if closed_trades else [0]
        peak = np.maximum.accumulate(cum) if len(cum) > 0 else cum
        max_dd = float(np.max(peak - cum)) if len(peak) > 0 else 0

        avg_win = np.mean([t["pnl_usd"] for t in closed_trades if t["pnl_usd"] > 0]) if wins > 0 else 0
        avg_loss = abs(np.mean([t["pnl_usd"] for t in closed_trades if t["pnl_usd"] <= 0])) if losses > 0 else 0

        orch.log.info(f"    {ticker}: {len(closed_trades)} trades, {wins}W/{losses}L, WR {win_rate:.1f}%, PnL ${total_pnl:.2f}, Sharpe {sharpe:.2f}, MaxDD ${max_dd:.2f}")
        bt_result = {
            "trades": len(closed_trades), "wins": wins, "losses": losses,
            "win_rate": round(win_rate, 1), "total_pnl_usd": round(total_pnl, 2),
            "sharpe_ratio": round(sharpe, 2), "max_drawdown_usd": round(max_dd, 2),
            "profit_factor": round(pf, 2) if pf != float("inf") else "inf",
            "avg_win": round(avg_win, 2), "avg_loss": round(avg_loss, 2),
        }
        orch.log.info(f"BT {ticker}: {json.dumps(bt_result)}")
        if pf == float("inf"):
            orch.log.info(f"      Avg Win ${avg_win:.2f} | Avg Loss ${avg_loss:.2f} | Profit Factor: inf (no losses)")
        else:
            orch.log.info(f"      Avg Win ${avg_win:.2f} | Avg Loss ${avg_loss:.2f} | Profit Factor: {pf:.2f}")

    orch.log.info("=== Replay complete ===")
