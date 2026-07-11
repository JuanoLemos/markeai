"""
orchestrator/pipeline.py
Iteration pipeline — run_iteration, _process_market, _analyze_*, _get_tickers,
_snapshot_portfolio, check_stops_and_evolve. Extracted from orchestrator.py to
keep the main class lean. All functions take the orchestrator instance as first arg.
"""
import uuid
from datetime import datetime, timezone
from execution.entry_filters import session_hours, correlation_check


def run_iteration(orch):
    """One full iteration: process all enabled markets, snapshot portfolio."""
    orch._news_cache = {}
    # B-Day4: request_id for tracing this iteration across logs
    orch.request_id = f"iter-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    orch.log.info(f"=== Starting iteration [req_id={orch.request_id}] ===")
    orch._hb("loop", "ok", f"Iteracion {orch.request_id}")
    try:
        for market, market_cfg in orch.markets_cfg.items():
            if not market_cfg.get("enabled", False):
                continue
            orch.log.info(f"Processing market: {market}")
            _process_market(orch, market, market_cfg)
        orch._hb("loop", "ok", "Iteracion completa")
    except Exception as e:
        orch.log.error(f"Iteration error: {e}")
        orch._hb("loop", "error", str(e))
        orch.notifier.send_error(f"Iteration failed: {e}")
    orch.log.info("=== Iteration complete ===")
    _snapshot_portfolio(orch)


def _snapshot_portfolio(orch):
    try:
        for name, pb in orch.paper_brokers.items():
            s = pb.get_summary()
            orch.risk_engine.update_balance(s["balance"])

            # Issue 7 fix: compute total_pnl from DB as source of truth, not
            # from PaperBroker.get_summary() which reflects in-memory self.balance
            # (corruptible via duplicate orchestrators or state-file race).
            def _price(ticker):
                try:
                    return orch.yf_collector.get_current_price(ticker)
                except Exception:
                    return None
            pnl_data = orch.db.compute_total_pnl_from_db(get_current_price=_price)

            # Kill-switch: if computed total_pnl exceeds 2x initial balance,
            # it's clearly fictional (e.g. Issue 7 observed +$10,736 on $1000
            # account). Log CRITICAL + Telegram. Do NOT abort — the snapshot
            # still records the corrected value so the dashboard reflects reality.
            initial_balance = (orch.config.get("paper") or {}).get("initial_balance", 1000)
            if abs(pnl_data["total_pnl"]) > initial_balance * 2:
                msg = (
                    f"FICTIONAL PnL DETECTED: total_pnl=${pnl_data['total_pnl']:.2f} "
                    f"exceeds 2x initial_balance=${initial_balance}. "
                    f"realized=${pnl_data['realized_pnl']:.2f}, "
                    f"unrealized=${pnl_data['unrealized_pnl']:.2f}, "
                    f"n_open={pnl_data['n_open']}, n_closed={pnl_data['n_closed']}"
                )
                orch.log.critical(msg)
                if getattr(orch, "notifier", None):
                    try:
                        orch.notifier.send_error(f"🚨 [KILL-SWITCH] {msg}")
                    except Exception:
                        pass

            orch.db.insert_portfolio_snapshot(
                balance=s["balance"], open_positions=s["open_positions"],
                daily_pnl=s["daily_pnl"], total_pnl=pnl_data["total_pnl"],
            )
    except Exception as e:
        try:
            orch.log.error(f"_snapshot_portfolio failed: {e}")
        except Exception:
            pass


def _process_market(orch, market: str, market_cfg: dict):
    layer_results = {}
    market_data = {}
    if market == "polymarket":
        layer_results, market_data = _analyze_polymarket(orch, market_cfg)
    elif market == "forex":
        layer_results, market_data = _analyze_forex(orch, market_cfg)
    elif market == "stocks":
        layer_results, market_data = _analyze_stocks(orch, market_cfg)
    if not layer_results:
        orch.log.info(f"No layer results for {market}, skipping")
        orch._hb("data", "error", f"{market}: sin resultados")
        return
    orch._hb("data", "ok", f"{market}: {len(layer_results)} capas")
    target_tickers = _get_tickers(market, market_cfg)
    if market == "polymarket" and market_data.get("slug"):
        target_tickers = [market_data["slug"]]
    # B-13 fix: fuse once per market, not per ticker
    fused = orch.fusion_engine.fuse(layer_results, market)
    for ticker in target_tickers:
        orch.log.info(f"  Analyzing {ticker}...")
        orch._hb("fusion", "ok", f"{market} {ticker}: {fused['signal']} score={fused['score']}")
        layers_with_score = {**fused.get("layer_scores", {}), "_fused_score": fused.get("score", 50)}
        orch.db.insert_signal({
            "market": market,
            "ticker": ticker,
            "decision": fused["signal"],
            "confidence": fused.get("confidence", 0),
            "layer_scores": layers_with_score,
            "reasoning": fused.get("reasoning", ""),
        })
        orch.log.info(f"  Fused: {fused['signal']} (score:{fused['score']} conf:{fused['confidence']})")
        if fused["signal"] != "WAIT":
            conj_scores = [l.get("score", 50) for _, l in fused.get("layer_scores", {}).items()]
            active_layer_count = sum(1 for s in conj_scores if s < 45 or s > 55)
            kelly = orch.risk_engine.kelly_fraction()
            adx_regime = layer_results.get("adx_regime", {}).get("details", {}).get("regime", "")
            exec_mode = market_cfg.get("mode", "paper")
            for prof_name, prof_cfg in orch.profiles_config.items():
                mc = prof_cfg.get("per_market", {}).get(market, {}).get("min_confidence", 40)
                if fused.get("confidence", 0) < mc:
                    orch.log.info(f"  {prof_name} low conf ({fused.get('confidence')}/{mc})")
                    continue
                if prof_cfg.get("min_confluence", 1) > 1 and active_layer_count < prof_cfg["min_confluence"]:
                    orch.log.info(f"  {prof_name} blocked: only {active_layer_count}/{prof_cfg['min_confluence']} layers")
                    continue
                if prof_cfg.get("adx_alignment") == "required" and adx_regime == "ranging":
                    orch.log.info(f"  {prof_name} blocked: ADX ranging")
                    continue
                pb = orch.paper_brokers[prof_name]
                decision = orch.decider.decide(market, ticker, fused, {**market_data, "open_positions": pb.get_positions()}, fused.get("layer_scores", {}), profile=prof_name)
                orch._hb("deepseek", "ok", f"{prof_name} {market} {ticker}: {decision.get('signal')} conf={decision.get('confidence')}")
                orch.log.info(f"  {prof_name} DeepSeek: {decision.get('signal')} (conf:{decision.get('confidence')})")
                if decision["signal"] == "WAIT":
                    continue
                orch.risk_engine.update_balance(orch.paper_broker.balance)
                can_trade, reason = orch.risk_engine.circuit_breakers()
                if not can_trade:
                    orch.log.warning(f"  Risk block ({prof_name}): {reason}")
                    continue
                hour = datetime.now(timezone.utc).hour
                if not session_hours(market, hour, profile=prof_name, ticker=ticker):
                    orch.log.info(f"  {prof_name} session blocked at hour {hour}")
                    continue
                if prof_cfg.get("correlation_filter") and pb and pb.get_positions():
                    if not correlation_check(pb.get_positions(), market, ticker, decision.get("signal", "LONG"),
                                            threshold=orch.config.get("risk", {}).get("correlation_threshold", 0.80)):
                        orch.log.info(f"  {prof_name} correlation blocked")
                        continue
                if kelly <= 0 and orch.risk_engine.trade_history:
                    orch.log.info(f"  {prof_name} blocked: Kelly={kelly:.2f}")
                    continue
                trade = None
                sp, tp = 5.0, 10.0  # fallback SL/TP if not set later
                if exec_mode == "real":
                    if market == "polymarket":
                        trade = orch.pm_executor.place_order(
                            market_slug=ticker,
                            side=decision["signal"],
                            size=decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50),
                            price=decision.get("entry_price", 0) or market_data.get("price", 0),
                        )
                    else:
                        trade = orch.trad_executor.place_order(
                            ticker=ticker,
                            side=decision["signal"],
                            size_usd=decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50),
                        )
                else:
                    entry_price = decision.get("entry_price") or market_data.get(ticker, {}).get("price", 0) or market_data.get("price", 0)
                    base_stop = decision.get("stop_loss_pct") or 5
                    base_tp = decision.get("take_profit_pct") or 10
                    stop_price = entry_price * (1 - base_stop / 100)
                    risk_size = orch.risk_engine.position_size(entry_price, stop_price)
                    size_usd = min(decision.get("position_size_usd") or market_cfg.get("max_position_usd", 50), risk_size)
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
                    orch._hb("execution", "ok", f"{prof_name} {market} {ticker} {decision['signal']} ${trade.get('size_usd',0):.0f}")
                    orch.risk_engine.record_trade(trade)
                    orch.journal.record_trade(trade)
                    orch.notifier.send_trade_entry(trade)
                    db_trade_id = orch.db.insert_trade({
                        "market": f"{prof_name}_{market}", "ticker": ticker,
                        "signal": decision["signal"], "entry_price": trade.get("entry_price", 0),
                        "position_size_usd": trade.get("size_usd", trade.get("size", 0)),
                        "stop_loss": sp, "take_profit": tp,
                        "confidence": decision.get("confidence", 0),
                        "strategy_used": f"{prof_name}_{market}_{fused['signal']}",
                        "position_id": trade.get("id"),
                    })
                    if trade and "id" in trade and db_trade_id and trade["id"] in pb.positions:
                        pb.positions[trade["id"]]["_db_id"] = db_trade_id


def _analyze_polymarket(orch, market_cfg: dict) -> tuple:
    layer_results = {}
    market_data = {}
    try:
        markets = orch.pm_collector.get_active_markets(limit=10)
        if not markets:
            return {}, {}
        for m in markets[:3]:
            slug = m.get("market_slug", "") or m.get("slug", "") or m.get("ticker", "")
            if not slug:
                continue
            market_data["slug"] = slug
            market_data["price"] = orch.pm_collector.get_market_price(slug)
            market_data["title"] = m.get("question", slug)
            try:
                order_book = orch.pm_collector.get_order_book(slug)
                if orch.config["layers"]["orderbook"]["enabled"]:
                    ob_result = orch.ob_analyzer.analyze(order_book)
                    if ob_result:
                        layer_results["orderbook"] = ob_result
            except Exception as e:
                orch.log.error(f"Polymarket orderbook[{slug}] error: {e}")
            try:
                if orch.config["layers"]["onchain"]["enabled"]:
                    onchain_result = orch.onchain_analyzer.analyze({
                        "trade_history": orch.pm_collector.get_trade_history(slug),
                        "market_details": m,
                        "onchain_data": orch.pm_collector.get_onchain_data(),
                    })
                    if onchain_result:
                        layer_results["onchain"] = onchain_result
            except Exception as e:
                orch.log.error(f"Polymarket onchain[{slug}] error: {e}")
            break
        try:
            news = orch._get_news("crypto")
            if orch.config["layers"]["sentiment"]["enabled"]:
                sr = orch.sentiment_analyzer.analyze(news)
                if sr:
                    layer_results["sentiment"] = sr
        except Exception as e:
            orch.log.error(f"Polymarket sentiment error: {e}")
    except Exception as e:
        orch.log.error(f"Polymarket error: {e}")
    return layer_results, market_data


def _analyze_forex(orch, market_cfg: dict) -> tuple:
    layer_results = {}
    market_data = {}
    try:
        pairs = market_cfg.get("pairs", ["EURUSD=X"])
        summary = orch.yf_collector.get_market_summary()
        market_data = summary.get("forex", {})
        dxy = orch.yf_collector.get_dxy()
        vix = orch.yf_collector.get_vix()
        news = orch._get_news("forex")
        for pair in pairs:
            data = orch.yf_collector.get_historical(pair, "14d", "1h")
            try:
                if orch.config["layers"]["technical"]["enabled"]:
                    tr = orch.tech_analyzer.analyze(data)
                    if tr:
                        layer_results["technical"] = tr
            except Exception as e:
                orch.log.error(f"Forex technical error: {e}")
            try:
                if orch.config["layers"]["ict_smc"]["enabled"]:
                    ict_r = orch.ict_analyzer.analyze(data)
                    if ict_r and ict_r.get("score", 50) != 50:
                        layer_results["ict_smc"] = ict_r
            except Exception as e:
                orch.log.error(f"Forex ict_smc error: {e}")
            try:
                if orch.config["layers"]["adx_regime"]["enabled"]:
                    adx_r = orch.adx_analyzer.analyze(data)
                    if adx_r and adx_r.get("score", 50) != 50:
                        layer_results["adx_regime"] = adx_r
            except Exception as e:
                orch.log.error(f"Forex adx error: {e}")
            break
        try:
            if orch.config["layers"]["sentiment"]["enabled"]:
                sr = orch.sentiment_analyzer.analyze(news)
                if sr:
                    layer_results["sentiment"] = sr
        except Exception as e:
            orch.log.error(f"Forex sentiment error: {e}")
        try:
            if orch.config["layers"]["macro"]["enabled"]:
                mr = orch.macro_analyzer.analyze(dxy=dxy, vix=vix, market_type="forex")
                if mr:
                    layer_results["macro"] = mr
        except Exception as e:
            orch.log.error(f"Forex macro error: {e}")
        try:
            if orch.config["layers"]["cross_asset"]["enabled"]:
                cr = orch.cross_analyzer.analyze(summary)
                if cr:
                    layer_results["cross_asset"] = cr
        except Exception as e:
            orch.log.error(f"Forex cross_asset error: {e}")
    except Exception as e:
        orch.log.error(f"Forex error: {e}")
    return layer_results, market_data


def _analyze_stocks(orch, market_cfg: dict) -> tuple:
    layer_results = {}
    market_data = {}
    try:
        tickers = market_cfg.get("tickers", ["SPY", "QQQ"])
        summary = orch.yf_collector.get_market_summary()
        market_data = summary.get("stocks", {})
        all_data = orch.yf_collector.get_stocks(tickers)
        market_data.update(all_data)
        usd_ars_rate = None
        for tk in list(market_data.keys()):
            if tk.endswith(".BA"):
                if usd_ars_rate is None:
                    usd_ars_rate = orch.yf_collector.get_usd_ars_rate()
                if usd_ars_rate and usd_ars_rate > 0:
                    for field in ["price", "high_24h", "low_24h"]:
                        if field in market_data[tk]:
                            market_data[tk][field] = round(market_data[tk][field] / usd_ars_rate, 2)
                    market_data[tk]["_currency"] = "ARS"
        vix = orch.yf_collector.get_vix()
        news = orch._get_news("stocks")

        primary = tickers[0] if tickers else "SPY"
        data = orch.yf_collector.get_historical(primary, "14d", "1h")
        try:
            if orch.config["layers"]["technical"]["enabled"]:
                tr = orch.tech_analyzer.analyze(data)
                if tr:
                    layer_results["technical"] = tr
        except Exception as e:
            orch.log.error(f"Stocks technical[{primary}] error: {e}")

        try:
            if orch.config["layers"]["ict_smc"]["enabled"]:
                ict_r = orch.ict_analyzer.analyze(data)
                if ict_r and ict_r.get("score", 50) != 50:
                    layer_results["ict_smc"] = ict_r
        except Exception as e:
            orch.log.error(f"Stocks ict_smc error: {e}")

        try:
            if orch.config["layers"]["adx_regime"]["enabled"]:
                adx_r = orch.adx_analyzer.analyze(data)
                if adx_r and adx_r.get("score", 50) != 50:
                    layer_results["adx_regime"] = adx_r
        except Exception as e:
            orch.log.error(f"Stocks adx error: {e}")

        try:
            if orch.config["layers"]["fundamental"]["enabled"]:
                for ticker in tickers:
                    raw = orch.yf_collector.get_fundamentals(ticker)
                    if raw:
                        fd = market_data.get(ticker, {})
                        fr = orch.fund_analyzer.analyze(ticker, fd, raw)
                        if fr and fr["score"] != 50:
                            layer_results["fundamental"] = fr
                            break
        except Exception as e:
            orch.log.error(f"Stocks fundamental error: {e}")

        try:
            if orch.config["layers"]["sentiment"]["enabled"]:
                sr = orch.sentiment_analyzer.analyze(news)
                if sr:
                    layer_results["sentiment"] = sr
        except Exception as e:
            orch.log.error(f"Stocks sentiment error: {e}")
        try:
            if orch.config["layers"]["macro"]["enabled"]:
                mr = orch.macro_analyzer.analyze(vix=vix, market_type="stocks")
                if mr:
                    layer_results["macro"] = mr
        except Exception as e:
            orch.log.error(f"Stocks macro error: {e}")
        try:
            if orch.config["layers"]["cross_asset"]["enabled"]:
                cr = orch.cross_analyzer.analyze(summary)
                if cr:
                    layer_results["cross_asset"] = cr
        except Exception as e:
            orch.log.error(f"Stocks cross_asset error: {e}")
    except Exception as e:
        orch.log.error(f"Stocks error: {e}")
    return layer_results, market_data


def _get_tickers(market: str, market_cfg: dict) -> list:
    if market == "polymarket":
        return [market_cfg.get("slug", "default")]
    if market == "forex":
        return market_cfg.get("pairs", ["EURUSD=X"])
    if market == "stocks":
        return market_cfg.get("tickers", ["SPY"])
    return ["default"]


def check_stops_and_evolve(orch):
    """Check stops, time_exit, partial TP for all brokers' open positions."""
    # B-N3 fix: collect prices for ALL brokers' positions (not just paper_broker alias)
    current_prices = {}
    all_positions = []
    for pb in orch.paper_brokers.values():
        all_positions.extend(pb.get_positions())
    if all_positions:
        tickers = set(p["ticker"] for p in all_positions)
        for tk in tickers:
            try:
                price = orch.yf_collector.get_current_price(tk)
                if price:
                    if tk.endswith(".BA"):
                        ars_rate = orch.yf_collector.get_usd_ars_rate()
                        if ars_rate and ars_rate > 0:
                            price = round(price / ars_rate, 2)
                    current_prices[tk] = price
            except Exception:
                pass
    for name, pb in orch.paper_brokers.items():
        closed = pb.check_stops(current_prices)
        for c in closed:
            orch.risk_engine.record_trade(c)
            orch.journal.record_trade(c)
            orch.notifier.send_trade_exit(c)
            db_id = c.get("_db_id", 0)
            if db_id:
                orch.db.close_trade(db_id, c["exit_price"], c["reason"], c["pnl_usd"], c["pnl_pct"])
            else:
                orch.log.warning(f"B-01: No DB trade_id for closed position {c.get('position_id', '?')}")
        if len(pb.trade_log) > 0 and len(pb.trade_log) % 10 == 0:
            orch.evolver.evolve(pb.trade_log, pb.get_summary())
