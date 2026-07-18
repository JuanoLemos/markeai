"""
orchestrator/core.py
Main MarketAIOrchestrator class. Lifecycle, init, and high-level run methods.
Pipeline iteration logic lives in orchestrator/pipeline.py; replay in orchestrator/replay.py.
"""
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

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
from analyzers.adx_regime import ADXRegimeAnalyzer
from engine.fusion import FusionEngine
from engine.decider import DeepSeekDecider
from engine.prompt_memory import PromptMemory
from execution.paper_broker import PaperBroker
from execution.executor_polymarket import PolymarketExecutor
from execution.executor_traditional import TraditionalExecutor
from learning.journal import TradeJournal
from learning.strategy_evolver import StrategyEvolver
from alerts.notifier import Notifier
from execution.risk_engine import RiskEngine
from execution.risk_gates import RiskGateManager

# Local pipeline/replay modules
from . import pipeline as _pipeline
from . import replay as _replay


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_sectors_file(path: str) -> dict:
    """Load config/sectors.yaml and return a flat {symbol -> sector_name} map."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(__file__).parent.parent / path
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    out = {}
    for sector, symbols in data.items():
        if not isinstance(symbols, list):
            continue
        for s in symbols:
            if isinstance(s, str):
                out[s] = sector
    return out


def _build_sector_caps(sector_cfg: dict) -> dict:
    """Return {sector_name -> cap_pct} from config risk_gates.sector_cap."""
    if not sector_cfg or not sector_cfg.get("enabled", False):
        return {}
    return dict(sector_cfg.get("sector_overrides", {}) or {})


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
        err_file = self.orchestrator_cfg.get("err_file", "orchestrator.err.log")
        # B-Day4: separate ERROR+ handler to err_file for easier debugging
        err_handler = logging.FileHandler(err_file)
        err_handler.setLevel(logging.ERROR)
        err_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file), err_handler, logging.StreamHandler()],
        )
        self.log = logging.getLogger(__name__)

    def init_components(self):
        self.db = Database()
        self.prompt_memory = PromptMemory(self.db)
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
            # B-08: pull SL/TP defaults from this profile's config
            pb = PaperBroker(
                initial_balance=1000,
                state_path=str(Path(__file__).parent.parent / "data" / "cache" / f"pb_{prof_name}.json"),
                default_sl_pct=prof_cfg.get("sl_default", 5.0),
                default_tp_pct=prof_cfg.get("tp_default", 10.0),
            )
            pb.set_time_exit_config(self.config.get("risk", {}).get("time_exit", {}))
            pb.max_total_exposure_pct = self.config["risk"].get("max_total_exposure_pct", 0.40)
            setattr(self, f"pb_{prof_name}", pb)
            self.paper_brokers[prof_name] = pb
        self.paper_broker = self.paper_brokers["normal"]
        # Issue 7: auto-detox corrupted balance at boot
        for name, pb in self.paper_brokers.items():
            if pb.balance > pb.initial_balance * 3:
                self.log.warning(f"{name} balance ${pb.balance:.0f} > 3x initial — auto-resetting")
                pb.reset_balance()
        self.pm_executor = PolymarketExecutor()
        self.trad_executor = TraditionalExecutor()
        self.journal = TradeJournal()
        self.evolver = StrategyEvolver()

        self.notifier = Notifier()
        self.risk_engine = RiskEngine(initial_balance=1000)
        self.ict_analyzer = ICTAnalyzer()
        self.adx_analyzer = ADXRegimeAnalyzer()
        self._news_cache = {}

        # Issue 2: pre-trade risk gates (5 hard rules, cascade)
        # Sector map loaded from config/sectors.yaml; sector caps from risk_gates.sector_cap.
        # Correlation matrix is empty at boot — populated lazily by
        # compute_correlation_matrix() once per cycle (T-1 data, no look-ahead).
        rg_cfg = self.config.get("risk_gates", {})
        self._sector_map = _load_sectors_file(rg_cfg.get("sectors_file", "config/sectors.yaml"))
        self._sector_caps = _build_sector_caps(rg_cfg.get("sector_cap", {}))
        self._correlation_matrix = {}
        self.risk_gate_manager = RiskGateManager(
            config=rg_cfg,
            sector_map=self._sector_map,
            sector_caps=self._sector_caps,
            correlation_matrix=self._correlation_matrix,
            log=self.log,
        )

        # B-N2: reconcile DB with broker JSON state at boot
        self._reconcile_db_with_brokers()

    def compute_correlation_matrix(self) -> dict:
        """
        Compute the (sym_a, sym_b) -> correlation matrix for the universe
        using T-1 daily returns (no look-ahead). Persists in-memory; the
        caller decides when to refresh (typically once per cycle, before
        the cascade is invoked).

        Returns: dict {(sym_a, sym_b): float in [-1, 1]}, symmetric.
        """
        rg_cfg = self.config.get("risk_gates", {})
        lookback = int(rg_cfg.get("correlation", {}).get("matrix_lookback_days", 60))
        universe = set()
        for m, cfg in self.markets_cfg.items():
            if m == "polymarket":
                continue
            for t in cfg.get("tickers", []) + cfg.get("pairs", []):
                universe.add(t)
        if not universe:
            self._correlation_matrix = {}
            self.risk_gate_manager.set_correlation_matrix({})
            return {}
        # Pull daily closes
        try:
            closes = {}
            for sym in universe:
                df = self.yf_collector.get_historical(sym, f"{lookback}d", "1d")
                if df is None or df.empty or "close" not in df.columns:
                    continue
                closes[sym] = df["close"].pct_change().dropna()
        except Exception as e:
            self.log.warning(f"compute_correlation_matrix: yfinance pull failed: {e}")
            return self._correlation_matrix or {}
        # Build matrix
        symbols = list(closes.keys())
        matrix = {}
        for i, a in enumerate(symbols):
            for b in symbols[i + 1:]:
                s1, s2 = closes[a], closes[b]
                joined = s1.align(s2, join="inner")
                if len(joined) < 20:  # need at least 20 aligned obs
                    continue
                corr = float(joined.corr())
                matrix[(a, b)] = corr
                matrix[(b, a)] = corr
        self._correlation_matrix = matrix
        self.risk_gate_manager.set_correlation_matrix(matrix)
        return matrix

    def _reconcile_db_with_brokers(self):
        """
        Crash recovery: if DB has trades with status='open' that are not in
        any broker's JSON state (i.e. lost during a previous crash), mark them
        as 'lost_recovery' so they don't pollute metrics.
        """
        try:
            open_trades = self.db.get_open_trades()
            if not open_trades:
                return
            known_position_ids = set()
            for pb in self.paper_brokers.values():
                known_position_ids.update(pb.positions.keys())
            lost = [t for t in open_trades if t.get("position_id") not in known_position_ids]
            if not lost:
                return
            ts = datetime.now(timezone.utc).isoformat()
            for t in lost:
                self.db.mark_lost_recovery(t["id"], ts)
            self.log.warning(f"B-N2: Reconciled {len(lost)} stale open trades as 'lost_recovery'")
        except Exception as e:
            self.log.error(f"Reconcile error (non-fatal): {e}")

    def _get_news(self, market_type: str) -> dict:
        if "_all" not in self._news_cache:
            self._news_cache["_all"] = self.news_collector.get_sentiment_summary("all", 24)
        return self._news_cache["_all"]

    def _hb(self, motor: str, status: str = "ok", message: str = ""):
        try:
            self.db.record_heartbeat(motor, status, message)
        except Exception:
            pass

    def run_iteration(self):
        _pipeline.run_iteration(self)

    def _process_market(self, market: str, market_cfg: dict):
        _pipeline._process_market(self, market, market_cfg)

    def _snapshot_portfolio(self):
        _pipeline._snapshot_portfolio(self)

    def _analyze_polymarket(self, market_cfg: dict) -> tuple:
        return _pipeline._analyze_polymarket(self, market_cfg)

    def _analyze_forex(self, market_cfg: dict) -> tuple:
        return _pipeline._analyze_forex(self, market_cfg)

    def _analyze_stocks(self, market_cfg: dict) -> tuple:
        return _pipeline._analyze_stocks(self, market_cfg)

    def _get_tickers(self, market: str, market_cfg: dict) -> list:
        return _pipeline._get_tickers(market, market_cfg)

    def check_stops_and_evolve(self):
        _pipeline.check_stops_and_evolve(self)

    def run_loop(self):
        self.log.info("MarketAI starting in loop mode")
        intervals = {}
        for m, c in self.markets_cfg.items():
            if c.get("enabled"):
                intervals[m] = c.get("check_interval_min", 60)
        last_run = {}
        while True:
            stop_file = Path(__file__).parent.parent / "STOP"
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
        self.log.info("Running backtest via replay (full MarketAI pipeline)")
        for market, cfg in self.markets_cfg.items():
            if not cfg.get("enabled") or market == "polymarket":
                continue
            _replay.run_replay(self, market=market, days=90, use_deepseek=False)
            self.log.info(f"Backtest complete for {market}")

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
        _replay.run_replay(self, market, days, use_deepseek)
