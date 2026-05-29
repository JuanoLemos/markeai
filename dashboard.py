import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread

import yaml
from flask import Flask, jsonify, render_template, request
from data.database import Database

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.yaml"
STATE_PATH = BASE_DIR / "data" / "cache" / "paper_broker_state.json"
LOG_PATH = BASE_DIR / "orchestrator.log"
DB_PATH = BASE_DIR / "data" / "market.db"

loop_process = None


def create_app():
    app = Flask(__name__, template_folder=BASE_DIR / "templates", static_folder=BASE_DIR / "static")

    def _version():
        try:
            with open(CONFIG_PATH) as f:
                c = yaml.safe_load(f)
            return c.get("version", "1.0.0")
        except Exception:
            return "1.0.0"

    @app.context_processor
    def inject_globals():
        return dict(app_version=_version())

    # ─── HTML routes ─────────────────────────────────────

    @app.route("/")
    def overview():
        return render_template("overview.html", page="overview")

    @app.route("/signals")
    def signals():
        return render_template("signals.html", page="signals")

    @app.route("/trades")
    def trades():
        return render_template("trades.html", page="trades")

    @app.route("/config")
    def config_page():
        return render_template("config.html", page="config")

    @app.route("/logs")
    def logs():
        return render_template("logs.html", page="logs")

    @app.route("/backtest")
    def backtest_page():
        return render_template("backtest.html", page="backtest")

    @app.route("/ticker/<symbol>")
    def ticker_page(symbol):
        return render_template("ticker.html", page="ticker", symbol=symbol)

    @app.route("/news")
    def news_page():
        return render_template("news.html", page="news")

    @app.route("/sandbox")
    def sandbox_page():
        return render_template("sandbox.html", page="sandbox")

    # ─── API routes ──────────────────────────────────────

    @app.route("/api/status")
    def api_status():
        try:
            running = LOG_PATH.exists() and time.time() - LOG_PATH.stat().st_mtime < 60
        except Exception:
            running = False
        return jsonify({"running": running})

    @app.route("/api/motors")
    def api_motors():
        try:
            db = Database()
            motors = db.get_heartbeats(minutes=120)
            db._get_conn().close()
            labels = {"loop":"Loop","data":"Datos","fusion":"Fusion","deepseek":"DeepSeek","execution":"Ejecucion"}
            for m in motors:
                m["label"] = labels.get(m["motor"], m["motor"])
            running = LOG_PATH.exists() and time.time() - LOG_PATH.stat().st_mtime < 60
            motors.append({
                "motor": "bot",
                "label": "Bot",
                "last_status": "ok" if running else "error",
                "last_message": "Loop activo" if running else "Detenido o sin heartbeat >60s",
                "last_run": "ahora" if running else "hace >1min",
            })
            return jsonify(motors)
        except Exception as e:
            return jsonify([])

    @app.route("/api/debug")
    def api_debug():
        try:
            info = {}
            info["api_version"] = _version()
            info["motors_db"] = Database().get_heartbeats(minutes=120)
            info["motors_count"] = len(info["motors_db"])
            info["signals_count"] = 0
            info["portfolio_rows"] = 0
            info["trades_open"] = 0
            info["profiles"] = {}
            for n in ("normal", "fast"):
                p = _profile_from_file(n)
                info["profiles"][n] = {
                    "balance": p.get("balance"),
                    "positions_count": len(p.get("positions", {})),
                    "trade_log_count": len(p.get("trade_log", [])),
                }
            try:
                import sqlite3
                conn = sqlite3.connect(str(DB_PATH))
                info["signals_count"] = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
                info["portfolio_rows"] = conn.execute("SELECT COUNT(*) FROM portfolio").fetchone()[0]
                info["trades_open"] = conn.execute("SELECT COUNT(*) FROM trades WHERE status='open'").fetchone()[0]
                conn.close()
            except Exception:
                pass
            return jsonify(info)
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/debug/inject-signal", methods=["POST"])
    def api_debug_inject():
        try:
            body = request.get_json(force=True)
            market = body.get("market", "forex")
            ticker = body.get("ticker", "EURUSD=X")
            decision = body.get("decision", "LONG")
            confidence = int(body.get("confidence", 65))
            profile = body.get("profile", "normal")
            trigger_broker = body.get("trigger_broker", False)
            price = float(body.get("price", 1.05))

            db = Database()
            fused = body.get("layer_scores", {"technical": {"signal":"LONG","score":65},"fusion":{"signal":"LONG","score":70}})
            db.insert_signal({
                "market": market, "ticker": ticker,
                "decision": decision, "confidence": confidence,
                "layer_scores": fused, "reasoning": "[DEBUG] Senal inyectada manualmente",
            })

            if trigger_broker:
                state_path = BASE_DIR / "data" / "cache" / f"pb_{profile}.json"
                try:
                    with open(state_path) as f:
                        state = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    state = {"balance": 1000, "positions": {}, "trade_log": [], "daily_pnl": 0}
                pid = f"{market}_{ticker}_{int(time.time())}"
                entry_price = price
                sl_pct = body.get("sl_pct", 2.0)
                tp_pct = body.get("tp_pct", 5.0)
                size = body.get("size_usd", 50)
                state["positions"][pid] = {
                    "market": market, "ticker": ticker, "signal": decision,
                    "entry_price": entry_price, "size_usd": size,
                    "stop_loss_pct": sl_pct, "take_profit_pct": tp_pct,
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                }
                with open(state_path, "w") as f:
                    json.dump(state, f, indent=2)
                db.record_heartbeat("execution", "ok", f"[DEBUG] {profile} {market} {ticker} {decision} ${size}")
                return jsonify({"ok": True, "position_id": pid, "profile": profile})

            return jsonify({"ok": True, "signal": f"{decision} {ticker} @ {confidence}"})
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/debug/reset-broker", methods=["POST"])
    def api_debug_reset():
        try:
            body = request.get_json(force=True) or {}
            profile = body.get("profile", "all")
            targets = ["normal", "fast"] if profile == "all" else [profile]
            for name in targets:
                path = BASE_DIR / "data" / "cache" / f"pb_{name}.json"
                with open(path, "w") as f:
                    json.dump({"balance": 1000, "positions": {}, "trade_log": [], "daily_pnl": 0}, f, indent=2)
            return jsonify({"ok": True, "reset": targets})
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/debug/motors-clear", methods=["POST"])
    def api_debug_motors_clear():
        try:
            db = Database()
            db.prune_signals(0)
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)})

    @app.route("/api/summary")
    def api_summary():
        return jsonify(_read_all_profiles())

    @app.route("/api/daily-brief")
    def api_daily_brief():
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            state = _read_state()

            # signals, trades, positions hoy
            import datetime
            today = datetime.date.today().isoformat()
            cur.execute("SELECT COUNT(*) as cnt, SUM(CASE WHEN decision='LONG' THEN 1 ELSE 0 END) as longs, SUM(CASE WHEN decision='SHORT' THEN 1 ELSE 0 END) as shorts FROM signals WHERE date(timestamp) = ?", (today,))
            sig = dict(cur.fetchone() or {"cnt": 0, "longs": 0, "shorts": 0})

            cur.execute("SELECT SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as wins, COUNT(*) as total, SUM(pnl_usd) as pnl FROM trades WHERE date(closed_at) = ? AND closed_at IS NOT NULL", (today,))
            trd = dict(cur.fetchone() or {"wins": 0, "total": 0, "pnl": 0})
            conn.close()

            # generar resumen narrativo
            opened = len(state.get("positions", {})) if state else 0
            signals_cnt = sig.get("cnt") or 0
            trades_closed = trd.get("total") or 0
            pnl_today = round(trd.get("pnl") or 0, 2)

            brief = ""
            if signals_cnt == 0:
                brief = "El bot no detectó señales hoy. Mercado en espera."
            else:
                brief = f"Hoy: {signals_cnt} señal(es) ({sig.get('longs') or 0}L/{sig.get('shorts') or 0}S). "
                if trades_closed > 0:
                    brief += f"Cerré {trades_closed} trade(s): {'+' if pnl_today >= 0 else ''}{pnl_today}$. "
                if opened > 0:
                    brief += f"{opened} posición(es) abierta(s) aún."
                else:
                    brief += "Sin posiciones abiertas."
            brief += " Estado: todo OK ✓"

            return jsonify({"brief": brief, "signals": signals_cnt, "trades_closed": trades_closed, "pnl_today": pnl_today, "open_positions": opened})
        except Exception as e:
            return jsonify({"brief": f"Error cargando brief (sin datos aún)", "error": str(e)})

    @app.route("/api/positions")
    def api_positions():
        import sqlite3
        state = _read_state()
        positions = list(state.get("positions", {}).values()) if state else []
        if not positions:
            return jsonify([])
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            tickers = [p.get("ticker") for p in positions if p.get("ticker")]
            placeholders = ",".join("?" * len(tickers))
            rows = conn.execute(
                f"SELECT ticker, price FROM market_data WHERE ticker IN ({placeholders}) GROUP BY ticker HAVING MAX(timestamp)",
                tickers
            ).fetchall()
            conn.close()
            price_map = {r["ticker"]: r["price"] for r in rows}
        except Exception:
            price_map = {}
        for p in positions:
            ticker = p.get("ticker")
            entry = p.get("entry_price") or 0
            current = price_map.get(ticker)
            p["current_price"] = current
            if current and entry:
                raw_delta = (current - entry) / entry * 100
                p["delta_pct"] = round(raw_delta if p.get("signal") == "LONG" else -raw_delta, 2)
            else:
                p["delta_pct"] = None
        return jsonify(positions)

    @app.route("/api/positions/<pos_id>/close", methods=["POST"])
    def api_close_position(pos_id):
        state = _read_state()
        positions = state.get("positions", {})
        if pos_id not in positions:
            matched = next((k for k, v in positions.items() if str(v.get("ticker")) == pos_id), None)
            if not matched:
                return jsonify({"ok": False, "error": "not found"}), 404
            pos_id = matched
        del state["positions"][pos_id]
        try:
            with open(STATE_PATH, "w") as f:
                json.dump(state, f, indent=2)
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/signals")
    def api_signals():
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM signals ORDER BY id DESC LIMIT 50").fetchall()
            conn.close()
            return jsonify([dict(r) for r in rows])
        except Exception:
            return jsonify([])

    @app.route("/api/trades")
    def api_trades():
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 50").fetchall()
            conn.close()
            return jsonify([dict(r) for r in rows])
        except Exception:
            return jsonify([])

    @app.route("/api/config", methods=["GET", "POST"])
    def api_config():
        if request.method == "GET":
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return jsonify(yaml.safe_load(f))
        try:
            updates = request.get_json()
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            _deep_merge(cfg, updates)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)})

    @app.route("/api/logs")
    def api_logs():
        try:
            with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            return jsonify({"lines": "".join(lines[-80:])})
        except FileNotFoundError:
            return jsonify({"lines": "(log file not created yet)"})

    @app.route("/api/loop/start")
    def api_loop_start():
        global loop_process
        if loop_process is not None and loop_process.poll() is None:
            return jsonify({"ok": False, "error": "Loop already running"})
        loop_process = subprocess.Popen(
            [sys.executable, str(BASE_DIR / "orchestrator.py"), "--mode", "loop"],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"ok": True})

    @app.route("/api/loop/stop")
    def api_loop_stop():
        global loop_process
        stop_file = BASE_DIR / "STOP"
        stop_file.write_text("stop")
        if loop_process and loop_process.poll() is None:
            loop_process.wait(timeout=10)
        loop_process = None
        if stop_file.exists():
            stop_file.unlink()
        return jsonify({"ok": True})

    @app.route("/api/portfolio/history")
    def api_portfolio_history():
        try:
            import sqlite3, datetime
            period = request.args.get("period", "all")
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            if period == "1d":
                cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
            elif period == "7d":
                cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat()
            elif period == "30d":
                cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
            else:
                cutoff = None
            if cutoff:
                rows = conn.execute("SELECT * FROM portfolio WHERE timestamp >= ? ORDER BY timestamp ASC LIMIT 500", (cutoff,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM portfolio ORDER BY timestamp ASC LIMIT 500").fetchall()
            # trades cerrados con timestamp para overlay
            trade_rows = conn.execute(
                "SELECT ticker, signal, pnl_usd, closed_at FROM trades WHERE closed_at IS NOT NULL ORDER BY closed_at ASC"
            ).fetchall()
            conn.close()
            return jsonify({
                "history": [dict(r) for r in rows],
                "trades": [dict(r) for r in trade_rows]
            })
        except Exception:
            return jsonify({"history": [], "trades": []})

    @app.route("/api/health")
    def api_health():
        return jsonify(_check_health())

    @app.route("/api/backtest/run")
    def api_backtest_run():
        market = request.args.get("market", "forex")
        proc = subprocess.run(
            [sys.executable, str(BASE_DIR / "orchestrator.py"), "--mode", "backtest", "--market", market],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=900,
        )
        results = []
        for line in proc.stdout.splitlines():
            if "BT " not in line:
                continue
            txt = line.split("BT ", 1)[-1]
            parts = txt.split(": ", 1)
            if len(parts) < 2:
                continue
            try:
                data = json.loads(parts[1])
                data["ticker"] = parts[0]
                results.append(data)
            except (json.JSONDecodeError, KeyError):
                pass
        total_trades = sum(r.get("trades", 0) for r in results)
        total_pnl = sum(r.get("total_pnl_usd", 0) for r in results)
        wr_vals = [r.get("win_rate", 0) for r in results if r.get("win_rate") is not None]
        avg_win_rate = round(sum(wr_vals) / len(wr_vals), 1) if wr_vals else 0
        return jsonify({
            "results": results,
            "aggregate": {
                "total_trades": total_trades,
                "avg_win_rate": avg_win_rate,
                "total_pnl_usd": round(total_pnl, 2),
            },
            "error": proc.stderr.strip() if proc.stderr and proc.stderr.strip() else None,
        })

    @app.route("/analytics")
    def analytics_page():
        return render_template("analytics.html", page="analytics")

    @app.route("/watchlist")
    def watchlist_page():
        return render_template("watchlist.html", page="watchlist")

    @app.route("/api/watchlist")
    def api_watchlist():
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT ticker, market,
                  COUNT(*) AS total_signals,
                  SUM(CASE WHEN decision='LONG' THEN 1 ELSE 0 END) AS longs,
                  SUM(CASE WHEN decision='SHORT' THEN 1 ELSE 0 END) AS shorts,
                  AVG(confidence) AS avg_conf,
                  MAX(timestamp) AS last_signal
                FROM signals GROUP BY ticker, market ORDER BY total_signals DESC
            """)
            signals_by_ticker = {r["ticker"]: dict(r) for r in cur.fetchall()}
            cur.execute("""
                SELECT ticker,
                  COUNT(*) AS trades,
                  SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) AS wins,
                  SUM(CASE WHEN pnl_usd IS NOT NULL AND pnl_usd <= 0 THEN 1 ELSE 0 END) AS losses,
                  SUM(COALESCE(pnl_usd, 0)) AS total_pnl,
                  SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_count
                FROM trades GROUP BY ticker
            """)
            trades_by_ticker = {r["ticker"]: dict(r) for r in cur.fetchall()}
            conn.close()
            tickers = sorted(set(list(signals_by_ticker.keys()) + list(trades_by_ticker.keys())))
            result = []
            for t in tickers:
                s = signals_by_ticker.get(t, {})
                tr = trades_by_ticker.get(t, {})
                wins = tr.get("wins", 0) or 0
                closed = (tr.get("wins", 0) or 0) + (tr.get("losses", 0) or 0)
                result.append({
                    "ticker": t,
                    "market": s.get("market", "—"),
                    "total_signals": s.get("total_signals", 0),
                    "longs": s.get("longs", 0),
                    "shorts": s.get("shorts", 0),
                    "avg_conf": round(s.get("avg_conf") or 0, 1),
                    "last_signal": s.get("last_signal", ""),
                    "trades": tr.get("trades", 0),
                    "open_count": tr.get("open_count", 0),
                    "win_rate": round(wins / closed * 100, 1) if closed > 0 else None,
                    "total_pnl": round(tr.get("total_pnl") or 0, 2),
                })
            return jsonify(result)
        except Exception as e:
            return jsonify([])

    @app.route("/api/metrics/extended")
    def api_metrics_extended():
        return jsonify(_compute_extended_metrics())

    @app.route("/api/metrics/by-market")
    def api_metrics_by_market():
        return jsonify(_metrics_by_market())

    @app.route("/api/metrics/funnel")
    def api_metrics_funnel():
        return jsonify(_decision_funnel())

    @app.route("/api/analytics/confidence-distribution")
    def api_confidence_distribution():
        return jsonify(_confidence_distribution())

    @app.route("/api/analytics/layer-activity")
    def api_layer_activity():
        return jsonify(_layer_activity())

    @app.route("/api/analytics/by-hour")
    def api_by_hour():
        return jsonify(_winrate_by_hour())

    @app.route("/api/analytics/by-ticker")
    def api_by_ticker():
        return jsonify(_performance_by_ticker())

    @app.route("/api/signals/<int:signal_id>")
    def api_signal_detail(signal_id):
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM signals WHERE id=?", (signal_id,)).fetchone()
            conn.close()
            if not row:
                return jsonify({})
            d = dict(row)
            try:
                d["layer_scores"] = json.loads(d.get("layer_scores", "{}"))
            except Exception:
                d["layer_scores"] = {}
            return jsonify(d)
        except Exception:
            return jsonify({})

    @app.route("/api/benchmark")
    def api_benchmark():
        try:
            import sqlite3, datetime, math
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT timestamp, balance_usd FROM portfolio ORDER BY timestamp ASC LIMIT 500").fetchall()
            conn.close()
            if not rows:
                return jsonify({"series": [], "summary": {}})
            initial = 1000.0
            spy_daily = (1.10 ** (1/252)) - 1
            btc_daily = (1.60 ** (1/365)) - 1
            bank_daily = (1.04 ** (1/365)) - 1
            series = []
            for i, r in enumerate(rows):
                ts = r["timestamp"]
                bot = r["balance_usd"]
                spy = round(initial * ((1 + spy_daily) ** i), 2)
                btc = round(initial * ((1 + btc_daily) ** i), 2)
                bank = round(initial * ((1 + bank_daily) ** i), 2)
                series.append({"ts": ts, "bot": bot, "spy": spy, "btc": btc, "bank": bank})
            last = series[-1]
            def pct(v): return round((v - initial) / initial * 100, 2)
            return jsonify({
                "series": series,
                "summary": {
                    "bot": {"balance": last["bot"], "pct": pct(last["bot"])},
                    "spy": {"balance": last["spy"], "pct": pct(last["spy"]), "note": "SPY ~10%/yr"},
                    "btc": {"balance": last["btc"], "pct": pct(last["btc"]), "note": "BTC ~60%/yr"},
                    "bank": {"balance": last["bank"], "pct": pct(last["bank"]), "note": "Banco ~4%/yr"},
                },
            })
        except Exception as e:
            return jsonify({"error": str(e), "series": [], "summary": {}})

    @app.route("/api/ticker/<symbol>")
    def api_ticker(symbol):
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            sigs = conn.execute(
                "SELECT id, timestamp, market, decision, confidence, layer_scores, reasoning FROM signals WHERE ticker=? ORDER BY timestamp DESC LIMIT 50",
                (symbol,)
            ).fetchall()
            trades_rows = conn.execute(
                "SELECT * FROM trades WHERE ticker=? ORDER BY entry_time DESC LIMIT 50",
                (symbol,)
            ).fetchall()
            price_rows = conn.execute(
                "SELECT timestamp, price, volume, change_24h_pct FROM market_data WHERE ticker=? ORDER BY timestamp ASC LIMIT 200",
                (symbol,)
            ).fetchall()
            conn.close()
            signals_out = []
            for s in sigs:
                d = dict(s)
                try:
                    d["layer_scores"] = json.loads(d.get("layer_scores") or "{}")
                except Exception:
                    d["layer_scores"] = {}
                signals_out.append(d)
            return jsonify({
                "symbol": symbol,
                "signals": signals_out,
                "trades": [dict(r) for r in trades_rows],
                "price_history": [dict(r) for r in price_rows],
            })
        except Exception as e:
            return jsonify({"error": str(e), "signals": [], "trades": [], "price_history": []})

    @app.route("/api/news")
    def api_news():
        try:
            market = request.args.get("market", "all")
            sentiment_filter = request.args.get("sentiment", "all")
            cache_map = {
                "forex": BASE_DIR / "data" / "cache" / "news_forex_24h.json",
                "stocks": BASE_DIR / "data" / "cache" / "news_stocks_24h.json",
                "crypto": BASE_DIR / "data" / "cache" / "news_crypto_24h.json",
            }
            if market == "all":
                articles = []
                seen = set()
                for mkt in ["crypto", "stocks", "forex"]:
                    try:
                        with open(cache_map[mkt]) as f:
                            batch = json.load(f)
                        for a in batch:
                            key = a.get("url", "") or a.get("title", "")
                            if key and key not in seen:
                                seen.add(key)
                                articles.append(a)
                    except (FileNotFoundError, json.JSONDecodeError):
                        continue
            else:
                cache_file = cache_map.get(market)
                if cache_file:
                    try:
                        with open(cache_file) as f:
                            articles = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        articles = []
                else:
                    articles = []
            # normalize sentiment labels
            sentiment_map = {"positive": "bullish", "negative": "bearish", "bullish": "bullish", "bearish": "bearish"}
            for a in articles:
                a["sentiment"] = sentiment_map.get(a.get("sentiment", ""), "neutral")
            if sentiment_filter != "all":
                articles = [a for a in articles if a.get("sentiment") == sentiment_filter]
            articles.sort(key=lambda a: a.get("published_at", ""), reverse=True)
            bullish = sum(1 for a in articles if a.get("sentiment") == "bullish")
            bearish = sum(1 for a in articles if a.get("sentiment") == "bearish")
            neutral = len(articles) - bullish - bearish
            return jsonify({
                "articles": articles[:60],
                "total": len(articles),
                "bullish": bullish,
                "bearish": bearish,
                "neutral": neutral,
            })
        except Exception as e:
            return jsonify({"error": str(e), "articles": [], "total": 0, "bullish": 0, "bearish": 0, "neutral": 0})

    @app.route("/api/risk-snapshot")
    def api_risk_snapshot():
        items = []
        total_exposure = 0.0
        total_max_loss = 0.0
        total_balance = 0.0
        for name in ("normal", "fast"):
            state = _profile_from_file(name)
            pos = state.get("positions", {})
            bal = state.get("balance", 0) or 0
            total_balance += bal
            for pid, p in pos.items():
                size = p.get("size_usd") or 0
                sl_pct = p.get("stop_loss_pct") or 0
                max_loss = round(size * sl_pct / 100, 2)
                total_exposure += size
                total_max_loss += max_loss
                items.append({
                    "ticker": pid,
                    "market": p.get("market", ""),
                    "signal": p.get("signal", ""),
                    "profile": name,
                    "size_usd": round(size, 2),
                    "stop_loss_pct": sl_pct,
                    "max_loss_usd": max_loss,
                })
        balance = total_balance if total_balance > 0 else 1000
        worst_balance = round(balance - total_max_loss, 2)
        pct_at_risk = round(total_max_loss / balance * 100, 2) if balance > 0 else 0
        return jsonify({
            "balance": round(balance, 2),
            "positions": items,
            "total_exposure_usd": round(total_exposure, 2),
            "total_max_loss_usd": round(total_max_loss, 2),
            "worst_balance": worst_balance,
            "pct_at_risk": pct_at_risk,
        })

    @app.route("/api/projection")
    def api_projection():
        try:
            import sqlite3, datetime, math
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # PnL por día de los últimos 30 días
            cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
            cur.execute("""
                SELECT date(closed_at) as day, SUM(pnl_usd) as daily_pnl, COUNT(*) as cnt
                FROM trades WHERE closed_at >= ? AND closed_at IS NOT NULL
                GROUP BY day ORDER BY day ASC
            """, (cutoff,))
            rows = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT SUM(CASE WHEN pnl_usd>0 THEN 1 ELSE 0 END)*100.0/COUNT(*) as wr, AVG(CASE WHEN pnl_usd>0 THEN pnl_usd END) as avg_win, AVG(CASE WHEN pnl_usd<0 THEN pnl_usd END) as avg_loss FROM trades WHERE closed_at IS NOT NULL")
            stats = dict(cur.fetchone() or {})
            conn.close()

            state = _read_state()
            balance = state.get("balance", 1000)
            initial = 1000.0

            avg_daily = sum(r["daily_pnl"] for r in rows) / len(rows) if rows else 0
            wr = round(stats.get("wr") or 0, 1)
            avg_win = round(stats.get("avg_win") or 0, 2)
            avg_loss = round(stats.get("avg_loss") or 0, 2)

            days_to_double = None
            if avg_daily > 0:
                days_to_double = math.ceil(balance / avg_daily)

            streak = 0
            best_streak = 0
            cur_streak = 0
            state_trades = sorted(state.get("trade_log", []), key=lambda x: x.get("timestamp",""))
            for t in state_trades:
                if t.get("type") == "close":
                    if (t.get("pnl") or 0) > 0:
                        cur_streak += 1
                        best_streak = max(best_streak, cur_streak)
                    else:
                        cur_streak = 0

            # badge por racha
            badge = None
            if best_streak >= 10:
                badge = {"icon": "🏆", "label": f"¡{best_streak} wins seguidos!", "level": "gold"}
            elif best_streak >= 5:
                badge = {"icon": "🥈", "label": f"{best_streak} wins en racha", "level": "silver"}
            elif best_streak >= 3:
                badge = {"icon": "🥉", "label": f"{best_streak} wins seguidos", "level": "bronze"}

            return jsonify({
                "balance": round(balance, 2),
                "initial": initial,
                "avg_daily_pnl": round(avg_daily, 2),
                "days_to_double": days_to_double,
                "win_rate": wr,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "best_streak": best_streak,
                "badge": badge,
                "daily_history": rows[-14:],
            })
        except Exception as e:
            return jsonify({"error": str(e), "avg_daily_pnl": 0, "days_to_double": None, "badge": None})

    return app


def _read_state() -> dict:
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _profile_from_file(name: str) -> dict:
    path = BASE_DIR / "data" / "cache" / f"pb_{name}.json"
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _summarize_state(state: dict) -> dict:
    if not state:
        return {"balance": 1000, "initial_balance": 1000, "total_pnl": 0, "total_pnl_pct": 0, "daily_pnl": 0, "open_positions": 0, "exposure_usd": 0, "total_trades": 0, "winning_trades": 0, "win_rate": 0}
    closed = len([t for t in state.get("trade_log", []) if t["type"] == "close"])
    wins = len([t for t in state.get("trade_log", []) if t["type"] == "close" and t.get("pnl", 0) > 0])
    bal = state.get("balance", 1000)
    inv = sum(p["size_usd"] for p in state.get("positions", {}).values())
    return {
        "balance": round(bal, 2), "initial_balance": 1000,
        "total_pnl": round(bal - 1000, 2), "total_pnl_pct": round((bal - 1000) / 1000 * 100, 2),
        "daily_pnl": round(state.get("daily_pnl", 0), 2),
        "open_positions": len(state.get("positions", {})), "exposure_usd": round(inv, 2),
        "total_trades": closed, "winning_trades": wins,
        "win_rate": round(wins / closed * 100, 1) if closed > 0 else 0,
    }


def _read_all_profiles() -> dict:
    result = {}
    for name in ("normal", "fast"):
        result[name] = _summarize_state(_profile_from_file(name))
    result["active"] = [n for n, s in result.items() if s["total_trades"] > 0 or s["open_positions"] > 0]
    return result


_health_cache = {"data": {}, "ts": 0}

def _check_health() -> dict:
    now = time.time()
    if now - _health_cache["ts"] < 60:
        return _health_cache["data"]
    apis = {}
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    apis["deepseek"] = bool(deepseek_key)
    try:
        import requests
        if deepseek_key:
            try:
                cfg = yaml.safe_load(open(CONFIG_PATH, encoding="utf-8"))
                model = cfg.get("deepseek", {}).get("model", "deepseek-v4-flash")
            except Exception:
                model = "deepseek-v4-flash"
            try:
                r = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {deepseek_key}"},
                    json={"model": model, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                    timeout=4,
                )
                apis["deepseek"] = r.status_code == 200
            except Exception:
                apis["deepseek"] = False
        try:
            r = requests.get("https://api.etherscan.io/v2/api", params={
                "chainid": "137", "module": "account", "action": "balance",
                "address": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
                "apikey": os.getenv("POLYSCAN_API_KEY", ""),
            }, timeout=4)
            apis["polyscan"] = r.status_code == 200 and r.json().get("status") == "1"
        except Exception:
            apis["polyscan"] = False
    except ImportError:
        apis["polyscan"] = False
    try:
        import yfinance as yf
        d = yf.download("SPY", period="1d", interval="1m", progress=False)
        apis["yfinance"] = not d.empty
    except Exception:
        apis["yfinance"] = False
    _health_cache["data"] = apis
    _health_cache["ts"] = now
    return apis


def _deep_merge(base: dict, updates: dict):
    for k, v in updates.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            if v in ("true", "false"):
                base[k] = v == "true"
            else:
                try:
                    num = int(v)
                    base[k] = num
                except (ValueError, TypeError):
                    try:
                        num = float(v)
                        base[k] = num
                    except (ValueError, TypeError):
                        base[k] = v


def _query_all(sql: str, params: tuple = ()) -> list:
    try:
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def _compute_extended_metrics() -> dict:
    rows = _query_all("SELECT pnl_usd FROM trades WHERE status='closed' AND pnl_usd IS NOT NULL ORDER BY entry_time")
    pnls = [r["pnl_usd"] for r in rows]
    if not pnls:
        return {"sharpe": 0, "profit_factor": 0, "max_drawdown": 0, "avg_win": 0, "avg_loss": 0, "trades": 0}
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    n = len(pnls)
    mean = sum(pnls) / n
    var = sum((p - mean) ** 2 for p in pnls) / n if n > 1 else 0
    std = var ** 0.5
    sharpe = (mean / std * (252 ** 0.5)) if std > 0 else 0
    pf = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else (float("inf") if wins else 0)
    cum, peak, max_dd = 0.0, 0.0, 0.0
    for p in pnls:
        cum += p
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
    return {
        "sharpe": round(sharpe, 2),
        "profit_factor": round(pf, 2) if pf != float("inf") else 999.99,
        "max_drawdown": round(max_dd, 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0,
        "trades": n,
    }


def _metrics_by_market() -> list:
    rows = _query_all("""
        SELECT market,
               COUNT(*) as trades,
               COALESCE(SUM(pnl_usd), 0) as pnl,
               COALESCE(AVG(CASE WHEN pnl_usd > 0 THEN 1.0 ELSE 0 END), 0) as wr,
               SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) as open_count
        FROM trades
        GROUP BY market
    """)
    for r in rows:
        r["pnl"] = round(r["pnl"], 2)
        r["wr"] = round(r["wr"] * 100, 1)
    return rows


def _decision_funnel() -> dict:
    sigs = _query_all("""
        SELECT
          COUNT(*) as total,
          SUM(CASE WHEN decision != 'WAIT' THEN 1 ELSE 0 END) as actionable
        FROM signals
        WHERE timestamp > datetime('now', '-7 days')
    """)
    trades = _query_all("""
        SELECT COUNT(*) as opened
        FROM trades
        WHERE entry_time > datetime('now', '-7 days')
    """)
    by_market = _query_all("""
        SELECT market,
               COUNT(*) as total,
               SUM(CASE WHEN decision != 'WAIT' THEN 1 ELSE 0 END) as actionable
        FROM signals
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY market
    """)
    return {
        "total_signals": sigs[0]["total"] if sigs else 0,
        "actionable": sigs[0]["actionable"] if sigs else 0,
        "executed": trades[0]["opened"] if trades else 0,
        "by_market": by_market,
    }


def _confidence_distribution() -> dict:
    rows = _query_all("SELECT confidence, decision FROM signals WHERE timestamp > datetime('now', '-30 days')")
    bins = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    by_decision = {"LONG": 0, "SHORT": 0, "WAIT": 0}
    for r in rows:
        c = r["confidence"] or 0
        if c < 20: bins["0-20"] += 1
        elif c < 40: bins["20-40"] += 1
        elif c < 60: bins["40-60"] += 1
        elif c < 80: bins["60-80"] += 1
        else: bins["80-100"] += 1
        d = r["decision"] or "WAIT"
        if d in by_decision:
            by_decision[d] += 1
    return {"bins": bins, "by_decision": by_decision, "total": len(rows)}


def _layer_activity() -> dict:
    rows = _query_all("SELECT layer_scores FROM signals WHERE timestamp > datetime('now', '-30 days')")
    activity = {}
    direction = {}
    for r in rows:
        try:
            layers = json.loads(r["layer_scores"] or "{}")
        except Exception:
            continue
        for name, info in layers.items():
            activity[name] = activity.get(name, 0) + 1
            if name not in direction:
                direction[name] = {"LONG": 0, "SHORT": 0, "WAIT": 0}
            sig = info.get("signal", "WAIT") if isinstance(info, dict) else "WAIT"
            if sig in direction[name]:
                direction[name][sig] += 1
    items = sorted(
        [{"layer": k, "count": v, "direction": direction.get(k, {})} for k, v in activity.items()],
        key=lambda x: x["count"], reverse=True,
    )
    return {"layers": items, "total_signals": len(rows)}


def _winrate_by_hour() -> list:
    rows = _query_all("""
        SELECT strftime('%H', entry_time) as hour,
               COUNT(*) as trades,
               COALESCE(AVG(CASE WHEN pnl_usd > 0 THEN 1.0 ELSE 0 END), 0) as wr,
               COALESCE(SUM(pnl_usd), 0) as pnl
        FROM trades
        WHERE status='closed' AND pnl_usd IS NOT NULL
        GROUP BY hour
        ORDER BY hour
    """)
    out = []
    for h in range(24):
        hh = f"{h:02d}"
        match = next((r for r in rows if r["hour"] == hh), None)
        if match:
            out.append({"hour": hh, "trades": match["trades"], "wr": round(match["wr"] * 100, 1), "pnl": round(match["pnl"], 2)})
        else:
            out.append({"hour": hh, "trades": 0, "wr": 0, "pnl": 0})
    return out


def _performance_by_ticker() -> list:
    rows = _query_all("""
        SELECT ticker, market,
               COUNT(*) as trades,
               SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) as wins,
               COALESCE(SUM(pnl_usd), 0) as pnl,
               COALESCE(AVG(CASE WHEN pnl_usd > 0 THEN 1.0 ELSE 0 END), 0) as wr
        FROM trades
        WHERE status='closed' AND pnl_usd IS NOT NULL
        GROUP BY ticker, market
        ORDER BY pnl DESC
    """)
    for r in rows:
        r["pnl"] = round(r["pnl"], 2)
        r["wr"] = round(r["wr"] * 100, 1)
    return rows


if __name__ == "__main__":
    app = create_app()
    print("MarketAI Dashboard at http://localhost:8050")
    app.run(host="127.0.0.1", port=8050, debug=False)
