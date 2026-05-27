#!/usr/bin/env python3
import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

load_dotenv()

from data.collector_polymarket import PolymarketCollector
from data.collector_yfinance import YFinanceCollector
from data.collector_news import NewsCollector
from data.database import Database
from analyzers.technical import TechnicalAnalyzer
from analyzers.onchain import OnChainAnalyzer
from analyzers.sentiment import SentimentAnalyzer
from analyzers.orderbook import OrderBookAnalyzer
from analyzers.fundamental import FundamentalAnalyzer
from analyzers.macro import MacroAnalyzer
from analyzers.cross_asset import CrossAssetAnalyzer
from analyzers.ict_smc import ICTAnalyzer
from engine.fusion import FusionEngine
from engine.decider import DeepSeekDecider
from execution.paper_broker import PaperBroker
from execution.executor_polymarket import PolymarketExecutor
from execution.executor_traditional import TraditionalExecutor
from learning.journal import TradeJournal
from learning.strategy_evolver import StrategyEvolver
from learning.backtest import Backtester
from alerts.notifier import Notifier
from execution.risk_engine import RiskEngine

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


class MarketAIOrchestrator:
    def __init__(self, config: dict, mode: str = "paper"):
        self.config = config
        self.mode = mode
        self.markets_cfg = config.get("markets", {})
        self.risk_cfg = config.get("risk", {})
        self.orchestrator_cfg = config.get("orchestrator", {})
        self.setup_logging()
        self.init_components()

    def setup_logging(self):
        log_level = getattr(logging, self.orchestrator_cfg.get("log_level", "INFO"))
        log_file = self.orchestrator_cfg.get("log_file", "orchestrator.log")
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.log = logging.getLogger(__name__)

    def init_components(self):
        self.db = Database()
        self.news_collector = NewsCollector(
            newsapi_key=os.getenv("NEWSAPI_KEY", ""),
            cryptopanic_key=os.getenv("CRYPTOPANIC_KEY", ""),
        )
        self.yf_collector = YFinanceCollector()
        self.pm_collector = PolymarketCollector()
        self.tech_analyzer = TechnicalAnalyzer()
        self.onchain_analyzer = OnChainAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ob_analyzer = OrderBookAnalyzer()
        self.fund_analyzer = FundamentalAnalyzer()
        self.macro_analyzer = MacroAnalyzer()
        self.cross_analyzer = CrossAssetAnalyzer()
        self.fusion_engine = FusionEngine(self.config)
        self.decider = DeepSeekDecider(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=self.config.get("deepseek", {}).get("model", "deepseek-v4-pro"),
            temperature=self.config.get("deepseek", {}).get("temperature", 0.3),
            max_tokens=self.config.get("deepseek", {}).get("max_tokens", 500),
        )
        self.paper_brokers = {}
        self.profiles_config = self.config.get("profiles", {"normal": {"label":"Normal","sl_min_pct":1,"sl_max_pct":5,"tp_min_pct":2,"tp_max_pct":10}})
        for prof_name, prof_cfg in self.profiles_config.items():
            pb = PaperBroker(
                initial_balance=1000,
                state_path=str(Path(__file__).parent / "data" / "cache" / f"pb_{prof_name}.json"),
            )
            pb.set_time_exit_config(self.config.get("risk", {}).get("time_exit", {}))
            pb.max_total_exposure_pct = self.config["risk"].get("max_total_exposure_pct", 0.40)
            setattr(self, f"pb_{prof_name}", pb)
            self.paper_brokers[prof_name] = pb
        self.paper_broker = self.paper_brokers["normal"]
        self.pm_executor = PolymarketExecutor()
        self.trad_executor = TraditionalExecutor()
        self.journal = TradeJournal()
        self.evolver = StrategyEvolver()
        self.backtester = Backtester()
        self.notifier = Notifier()
        self.risk_engine = RiskEngine(initial_balance=1000)
        self.ict_analyzer = ICTAnalyzer()

    def run_iteration(self):
        self.log.info("=== Starting iteration ===")
        try:
            for market, market_cfg in self.markets_cfg.items():
                if not market_cfg.get("enabled", False):
                    continue
                self.log.info(f"Processing market: {market}")
                self._process_market(market, market_cfg)
        except Exception as e:
            self.log.error(f"Iteration error: {e}")
            self.notifier.send_error(f"Iteration failed: {e}")
        self.log.info("=== Iteration complete ===")
        self._snapshot_portfolio()

    def _snapshot_portfolio(self):
        try:
            for name, pb in self.paper_brokers.items():
                s = pb.get_summary()
                self.risk_engine.update_balance(s["balance"])
                self.db.insert_portfolio_snapshot(
                    balance=s["balance"], open_positions=s["open_positions"],
                    daily_pnl=s["daily_pnl"], total_pnl=s["total_pnl"],
                )
        except Exception:
            pass

    def _process_market(self, market: str, market_cfg: dict):
        layer_results = {}
        market_data = {}
        if market == "polymarket":
            layer_results, market_data = self._analyze_polymarket(market_cfg)
        elif market == "forex":
            layer_results, market_data = self._analyze_forex(market_cfg)
        elif market == "stocks":
            layer_results, market_data = self._analyze_stocks(market_cfg)
        if not layer_results:
            self.log.info(f"No layer results for {market}, skipping")
            return
        target_tickers = self._get_tickers(market, market_cfg)
        if market == "polymarket" and market_data.get("slug"):
            target_tickers = [market_data["slug"]]
        for ticker in target_tickers:
            self.log.info(f"  Analyzing {ticker}...")
            fused = self.fusion_engine.fuse(layer_results, market)
            self.db.insert_signal({
                "market": market,
                "ticker": ticker,
                "decision": fused["signal"],
                "confidence": fused.get("confidence", 0),
                "layer_scores": fused.get("layer_scores", {}),
                "reasoning": fused.get("reasoning", ""),
            })
            self.log.info(f"  Fused: {fused['signal']} (score:{fused['score']} conf:{fused['confidence']})")
            if fused["signal"] != "WAIT" and fused.get("confidence", 0) >= market_cfg.get("min_confidence", 50):
                decision = self.decider.decide(market, ticker, fused, market_data, fused.get("layer_scores", {}))
                self.log.info(f"  DeepSeek: {decision.get('signal')} (conf:{decision.get('confidence')})")
                if decision["signal"] != "WAIT":
                    self.risk_engine.update_balance(self.paper_broker.balance)
                    can_trade, reason = self.risk_engine.circuit_breakers()
                    if not can_trade:
                        self.log.warning(f"  Risk block: {reason}")
                        return
                    trade = None
                    exec_mode = market_cfg.get("mode", "paper")
                    if exec_mode == "real":
                        if market == "polymarket":
                            trade = self.pm_executor.place_order(
                                market_slug=ticker,
                                side=decision["signal"],
                                size=decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50),
                                price=decision.get("entry_price", 0) or market_data.get("price", 0),
                            )
                        else:
                            trade = self.trad_executor.place_order(
                                ticker=ticker,
                                side=decision["signal"],
                                size_usd=decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50),
                            )
                    else:
                        entry_price = decision.get("entry_price") or market_data.get(ticker, {}).get("price", 0) or market_data.get("price", 0)
                        base_stop = decision.get("stop_loss_pct") or 5
                        base_tp = decision.get("take_profit_pct") or 10
                        stop_price = entry_price * (1 - base_stop / 100)
                        risk_size = self.risk_engine.position_size(entry_price, stop_price)
                        size_usd = min(decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50), risk_size)
                        for prof_name, prof_cfg in self.profiles_config.items():
                            pb = self.paper_brokers[prof_name]
                            sp = max(prof_cfg.get("sl_min_pct", 0.5), min(prof_cfg.get("sl_max_pct", 5), base_stop))
                            tp = max(prof_cfg.get("tp_min_pct", 1), min(prof_cfg.get("tp_max_pct", 10), base_tp))
                            trade = pb.open_position(
                                market=market, ticker=ticker, signal=decision["signal"],
                                entry_price=entry_price, size_usd=size_usd,
                                stop_loss_pct=sp, take_profit_pct=tp,
                                confidence=decision.get("confidence", fused.get("confidence", 0)),
                                strategy_used=f"{prof_name}_{market}_{fused['signal']}",
                            )
                            if trade and "error" not in trade:
                                self.risk_engine.record_trade(trade)
                                self.journal.record_trade(trade)
                                self.db.insert_trade({
                                    "market": f"{prof_name}_{market}", "ticker": ticker,
                                    "signal": decision["signal"], "entry_price": trade.get("entry_price", 0),
                                    "position_size_usd": trade.get("size_usd", trade.get("size", 0)),
                                    "stop_loss": sp, "take_profit": tp,
                                    "confidence": decision.get("confidence", 0),
                                    "strategy_used": f"{prof_name}_{market}_{fused['signal']}",
                                })

    def _analyze_polymarket(self, market_cfg: dict) -> tuple:
        layer_results = {}
        market_data = {}
        try:
            markets = self.pm_collector.get_active_markets(limit=10)
            if not markets:
                return {}, {}
            for m in markets[:3]:
                slug = m.get("market_slug", "") or m.get("slug", "") or m.get("ticker", "")
                if not slug:
                    continue
                market_data["slug"] = slug
                market_data["price"] = self.pm_collector.get_market_price(slug)
                market_data["title"] = m.get("question", slug)
                try:
                    order_book = self.pm_collector.get_order_book(slug)
                    if self.config["layers"]["orderbook"]["enabled"]:
                        ob_result = self.ob_analyzer.analyze(order_book)
                        if ob_result:
                            layer_results["orderbook"] = ob_result
                except Exception as e:
                    self.log.error(f"Polymarket orderbook[{slug}] error: {e}")
                try:
                    if self.config["layers"]["onchain"]["enabled"]:
                        onchain_result = self.onchain_analyzer.analyze({
                            "trade_history": self.pm_collector.get_trade_history(slug),
                            "market_details": m,
                            "onchain_data": self.pm_collector.get_onchain_data(),
                        })
                        if onchain_result:
                            layer_results["onchain"] = onchain_result
                except Exception as e:
                    self.log.error(f"Polymarket onchain[{slug}] error: {e}")
                break
            try:
                news = self.news_collector.get_sentiment_summary("crypto", 24)
                if self.config["layers"]["sentiment"]["enabled"]:
                    sr = self.sentiment_analyzer.analyze(news)
                    if sr:
                        layer_results["sentiment"] = sr
            except Exception as e:
                self.log.error(f"Polymarket sentiment error: {e}")
        except Exception as e:
            self.log.error(f"Polymarket error: {e}")
        return layer_results, market_data

    def _analyze_forex(self, market_cfg: dict) -> tuple:
        layer_results = {}
        market_data = {}
        try:
            pairs = market_cfg.get("pairs", ["EURUSD=X"])
            summary = self.yf_collector.get_market_summary()
            market_data = summary.get("forex", {})
            dxy = self.yf_collector.get_dxy()
            vix = self.yf_collector.get_vix()
            news = self.news_collector.get_sentiment_summary("forex", 24)
            for pair in pairs:
                data = self.yf_collector.get_historical(pair, "14d", "1h")
                try:
                    if self.config["layers"]["technical"]["enabled"]:
                        tr = self.tech_analyzer.analyze(data)
                        if tr:
                            layer_results["technical"] = tr
                except Exception as e:
                    self.log.error(f"Forex technical error: {e}")
                try:
                    if self.config["layers"]["ict_smc"]["enabled"]:
                        ict_r = self.ict_analyzer.analyze(data)
                        if ict_r and ict_r.get("score", 50) != 50:
                            layer_results["ict_smc"] = ict_r
                except Exception as e:
                    self.log.error(f"Forex ict_smc error: {e}")
                break
            try:
                if self.config["layers"]["sentiment"]["enabled"]:
                    sr = self.sentiment_analyzer.analyze(news)
                    if sr:
                        layer_results["sentiment"] = sr
            except Exception as e:
                self.log.error(f"Forex sentiment error: {e}")
            try:
                if self.config["layers"]["macro"]["enabled"]:
                    mr = self.macro_analyzer.analyze(dxy=dxy, vix=vix, market_type="forex")
                    if mr:
                        layer_results["macro"] = mr
            except Exception as e:
                self.log.error(f"Forex macro error: {e}")
            try:
                if self.config["layers"]["cross_asset"]["enabled"]:
                    cr = self.cross_analyzer.analyze(summary)
                    if cr:
                        layer_results["cross_asset"] = cr
            except Exception as e:
                self.log.error(f"Forex cross_asset error: {e}")
        except Exception as e:
            self.log.error(f"Forex error: {e}")
        return layer_results, market_data

    def _analyze_stocks(self, market_cfg: dict) -> tuple:
        layer_results = {}
        market_data = {}
        try:
            tickers = market_cfg.get("tickers", ["SPY", "QQQ"])
            summary = self.yf_collector.get_market_summary()
            market_data = summary.get("stocks", {})
            vix = self.yf_collector.get_vix()
            news = self.news_collector.get_sentiment_summary("stocks", 24)

            primary = tickers[0] if tickers else "SPY"
            data = self.yf_collector.get_historical(primary, "14d", "1h")
            try:
                if self.config["layers"]["technical"]["enabled"]:
                    tr = self.tech_analyzer.analyze(data)
                    if tr:
                        layer_results["technical"] = tr
            except Exception as e:
                self.log.error(f"Stocks technical[{primary}] error: {e}")

            try:
                if self.config["layers"]["ict_smc"]["enabled"]:
                    ict_r = self.ict_analyzer.analyze(data)
                    if ict_r and ict_r.get("score", 50) != 50:
                        layer_results["ict_smc"] = ict_r
            except Exception as e:
                self.log.error(f"Stocks ict_smc error: {e}")

            try:
                if self.config["layers"]["fundamental"]["enabled"]:
                    for ticker in tickers:
                        raw = self.yf_collector.get_fundamentals(ticker)
                        if raw:
                            fd = market_data.get(ticker, {})
                            fr = self.fund_analyzer.analyze(ticker, fd, raw)
                            if fr and fr["score"] != 50:
                                layer_results["fundamental"] = fr
                                break
            except Exception as e:
                self.log.error(f"Stocks fundamental error: {e}")

            try:
                if self.config["layers"]["sentiment"]["enabled"]:
                    sr = self.sentiment_analyzer.analyze(news)
                    if sr:
                        layer_results["sentiment"] = sr
            except Exception as e:
                self.log.error(f"Stocks sentiment error: {e}")
            try:
                if self.config["layers"]["macro"]["enabled"]:
                    mr = self.macro_analyzer.analyze(vix=vix, market_type="stocks")
                    if mr:
                        layer_results["macro"] = mr
            except Exception as e:
                self.log.error(f"Stocks macro error: {e}")
            try:
                if self.config["layers"]["cross_asset"]["enabled"]:
                    cr = self.cross_analyzer.analyze(summary)
                    if cr:
                        layer_results["cross_asset"] = cr
            except Exception as e:
                self.log.error(f"Stocks cross_asset error: {e}")
        except Exception as e:
            self.log.error(f"Stocks error: {e}")
        return layer_results, market_data

    def _get_tickers(self, market: str, market_cfg: dict) -> list:
        if market == "polymarket":
            return [market_cfg.get("slug", "default")]
        if market == "forex":
            return market_cfg.get("pairs", ["EURUSD=X"])
        if market == "stocks":
            return market_cfg.get("tickers", ["SPY"])
        return ["default"]

    def check_stops_and_evolve(self):
        current_prices = {}
        positions = self.paper_broker.get_positions()
        if positions:
            tickers = set(p["ticker"] for p in positions)
            for tk in tickers:
                try:
                    price = self.yf_collector.get_current_price(tk)
                    if price:
                        current_prices[tk] = price
                except Exception:
                    pass
        for name, pb in self.paper_brokers.items():
            closed = pb.check_stops(current_prices)
            for c in closed:
                self.risk_engine.record_trade(c)
                self.journal.record_trade(c)
                self.notifier.send_trade_exit(c)
                self.db.close_trade(0, c["exit_price"], c["reason"], c["pnl_usd"], c["pnl_pct"])
            if len(pb.trade_log) > 0 and len(pb.trade_log) % 10 == 0:
                self.evolver.evolve(pb.trade_log, pb.get_summary())

    def run_loop(self):
        self.log.info("MarketAI starting in loop mode")
        intervals = {}
        for m, c in self.markets_cfg.items():
            if c.get("enabled"):
                intervals[m] = c.get("check_interval_min", 60)
        last_run = {}
        while True:
            stop_file = Path(__file__).parent / "STOP"
            if stop_file.exists():
                self.log.info("STOP file detected, shutting down")
                stop_file.unlink(missing_ok=True)
                break
            now = time.time()
            for market, interval in intervals.items():
                if market not in last_run or (now - last_run[market]) >= interval * 60:
                    self.log.info(f"Scheduled: {market}")
                    self.run_iteration()
                    last_run[market] = now
            self.check_stops_and_evolve()
            time.sleep(30)

    def run_once(self):
        self.log.info("MarketAI single iteration")
        self.run_iteration()
        self.check_stops_and_evolve()

    def run_backtest(self):
        self.log.info("Running backtest")
        for market, cfg in self.markets_cfg.items():
            if not cfg.get("enabled"):
                continue
            if market == "forex":
                for pair in cfg.get("pairs", []):
                    data = self.yf_collector.get_historical(pair, "3mo", "1h")
                    r = self.backtester.run(market, pair, data)
                    self.log.info(f"BT {pair}: {json.dumps(r, default=str)}")
            elif market == "stocks":
                for tk in cfg.get("tickers", []):
                    data = self.yf_collector.get_historical(tk, "3mo", "1h")
                    r = self.backtester.run(market, tk, data)
                    self.log.info(f"BT {tk}: {json.dumps(r, default=str)}")

    def run_report(self):
        s = self.paper_broker.get_summary()
        print(json.dumps(s, indent=2))
        return s

    def run_cron(self, task: str = "daily"):
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.log.info(f"Cron [{task}] - {now}")
        if task == "daily":
            self.run_once()
            s = self.paper_broker.get_summary()
            self.notifier.send_daily_summary(s)
        elif task == "weekly":
            self.run_backtest()
        elif task == "hourly":
            self._snapshot_portfolio()
            status = "OK"
            err = 0
            try:
                with open(self.orchestrator_cfg.get("log_file", "orchestrator.log")) as f:
                    for line in f:
                        if "[ERROR]" in line:
                            err += 1
                if err > 5:
                    status = f"WARN({err} errors)"
            except Exception:
                pass
            self.log.info(f"Cron health: {status}")

    def run_replay(self, market: str, days: int = 90, use_deepseek: bool = False):
        self.log.info(f"=== Replay {market} - {days} dias ===")
        market_cfg = self.markets_cfg.get(market, {})
        if not market_cfg:
            self.log.error(f"Unknown market: {market}")
            return

        import numpy as np
        from execution.paper_broker import PaperBroker

        tickers = market_cfg.get("pairs" if market == "forex" else "tickers", [])
        base_dir = Path(__file__).parent

        for ticker in tickers:
            self.log.info(f"  Replaying {ticker}...")
            data = self.yf_collector.get_historical(ticker, f"{days}d", "1h")
            if data.empty or len(data) < 100:
                self.log.info(f"    SKIP - {len(data)} rows")
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
                tr = self.tech_analyzer.analyze(chunk)
                if tr and tr.get("score", 50) != 50:
                    layer_results["technical"] = tr
                mr = self.macro_analyzer.analyze(dxy=self.yf_collector.get_dxy(), vix=self.yf_collector.get_vix(), market_type=market)
                if mr and mr.get("score", 50) != 50:
                    layer_results["macro"] = mr
                if market == "stocks" and self.config["layers"]["fundamental"]["enabled"]:
                    fr = self.fund_analyzer.analyze(ticker, price_data, self.yf_collector.get_fundamentals(ticker))
                    if fr and fr.get("score", 50) != 50:
                        layer_results["fundamental"] = fr

                fused = self.fusion_engine.fuse(layer_results, market)
                if fused["signal"] != "WAIT" and fused.get("confidence", 0) >= market_cfg.get("min_confidence", 40):
                    decision = fused
                    if use_deepseek:
                        decision = self.decider.decide(market, ticker, fused, {}, fused.get("layer_scores", {}))
                    if decision and decision.get("signal", "WAIT") != "WAIT":
                        sl_pct = decision.get("stop_loss_pct") or 5
                        tp_pct = decision.get("take_profit_pct") or 10
                        sl_cfg = self.config["risk"]
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

            self.log.info(f"    {ticker}: {len(closed_trades)} trades, {wins}W/{losses}L, WR {win_rate:.1f}%, PnL ${total_pnl:.2f}, Sharpe {sharpe:.2f}, MaxDD ${max_dd:.2f}")
            if pf == float("inf"):
                self.log.info(f"      Avg Win ${avg_win:.2f} | Avg Loss ${avg_loss:.2f} | Profit Factor: inf (no losses)")
            else:
                self.log.info(f"      Avg Win ${avg_win:.2f} | Avg Loss ${avg_loss:.2f} | Profit Factor: {pf:.2f}")

        self.log.info("=== Replay complete ===")


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
