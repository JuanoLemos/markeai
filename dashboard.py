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

    return app


def _read_state() -> dict:
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


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


if __name__ == "__main__":
    app = create_app()
    print("MarketAI Dashboard at http://localhost:8050")
    app.run(host="127.0.0.1", port=8050, debug=False)
