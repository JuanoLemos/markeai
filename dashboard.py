import json
import os
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread

import yaml
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.yaml"
STATE_PATH = BASE_DIR / "data" / "cache" / "paper_broker_state.json"
LOG_PATH = BASE_DIR / "orchestrator.log"
DB_PATH = BASE_DIR / "data" / "market.db"

loop_process = None


def create_app():
    app = Flask(__name__, template_folder=BASE_DIR / "templates", static_folder=BASE_DIR / "static")

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

    # ─── API routes ──────────────────────────────────────

    @app.route("/api/status")
    def api_status():
        global loop_process
        running = loop_process is not None and loop_process.poll() is None
        return jsonify({"running": running})

    @app.route("/api/summary")
    def api_summary():
        state = _read_state()
        if not state:
            return jsonify({
                "balance": 1000, "initial_balance": 1000,
                "total_pnl": 0, "total_pnl_pct": 0, "daily_pnl": 0,
                "open_positions": 0, "exposure_usd": 0,
                "total_trades": 0, "winning_trades": 0, "win_rate": 0,
            })
        closed_trades = len([t for t in state.get("trade_log", []) if t["type"] == "close"])
        winning_trades = len([t for t in state.get("trade_log", []) if t["type"] == "close" and t.get("pnl", 0) > 0])
        total_invested = sum(p["size_usd"] for p in state.get("positions", {}).values())
        return jsonify({
            "balance": round(state.get("balance", 1000), 2),
            "initial_balance": 1000,
            "total_pnl": round(state.get("balance", 1000) - 1000, 2),
            "total_pnl_pct": round((state.get("balance", 1000) - 1000) / 10, 2),
            "daily_pnl": round(state.get("daily_pnl", 0), 2),
            "open_positions": len(state.get("positions", {})),
            "exposure_usd": round(total_invested, 2),
            "total_trades": closed_trades,
            "winning_trades": winning_trades,
            "win_rate": round(winning_trades / closed_trades * 100, 1) if closed_trades > 0 else 0,
        })

    @app.route("/api/positions")
    def api_positions():
        state = _read_state()
        return jsonify(list(state.get("positions", {}).values()) if state else [])

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
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM portfolio ORDER BY timestamp ASC LIMIT 200").fetchall()
            conn.close()
            return jsonify([dict(r) for r in rows])
        except Exception:
            return jsonify([])

    @app.route("/api/health")
    def api_health():
        return jsonify(_check_health())

    @app.route("/api/backtest/run")
    def api_backtest_run():
        market = request.args.get("market", "forex")
        proc = subprocess.run(
            [sys.executable, str(BASE_DIR / "orchestrator.py"), "--mode", "backtest", "--market", market],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=120,
        )
        return jsonify({"output": proc.stdout, "error": proc.stderr})

    @app.route("/analytics")
    def analytics_page():
        return render_template("analytics.html", page="analytics")

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

    return app


def _read_state() -> dict:
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _check_health() -> dict:
    apis = {}
    try:
        import requests
        r = requests.get("https://api.etherscan.io/v2/api", params={
            "chainid": "137", "module": "account", "action": "balance",
            "address": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
            "apikey": os.getenv("POLYSCAN_API_KEY", ""),
        }, timeout=5)
        apis["polyscan"] = r.status_code == 200 and r.json().get("status") == "1"
    except Exception:
        apis["polyscan"] = False
    try:
        r = requests.get("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY','')}"},
            json={"model": "deepseek-v4-pro", "messages": [{"role":"user","content":"ping"}], "max_tokens":5},
            timeout=5,
        )
        apis["deepseek"] = r.status_code == 200
    except Exception:
        apis["deepseek"] = False
    apis["yfinance"] = True
    try:
        import yfinance as yf
        d = yf.download("SPY", period="1d", interval="1m", progress=False)
        apis["yfinance"] = not d.empty
    except Exception:
        apis["yfinance"] = False
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
