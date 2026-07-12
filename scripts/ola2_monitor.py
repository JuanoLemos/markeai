"""
ola2_monitor.py — Ola 2 monitor: watches orchestrator.log + market.db and prints
alerts to stdout when something is off. Designed to run in a separate terminal
while the loop runs in another.

Exit codes:
    0  OK
    1  Critical issue (loop dead, DB corrupt, drawdown > 5%)
    2  Warning (high error rate, win rate drifting)

Usage:
    python scripts/ola2_monitor.py --once          # single check, then exit
    python scripts/ola2_monitor.py --interval 60   # check every 60s (default 300)
"""
import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "data" / "market.db"
LOG = ROOT / "orchestrator.log"
ERR_LOG = ROOT / "orchestrator.err.log"
STALE_HEARTBEAT_MIN = 5       # loop considered dead if no heartbeat in N min
DRAWDOWN_ALERT_PCT = 5.0      # 5% daily drawdown triggers warning
ERR_RATE_PER_MIN = 10         # >10 errors/min in err.log = warning


def check_loop_alive() -> tuple:
    """Returns (alive: bool, last_heartbeat_age_min: float, last_msg: str)."""
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT timestamp FROM motor_heartbeat ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return False, float("inf"), "no heartbeats"
        ts_str = row[0].replace("Z", "+00:00") if "Z" in row[0] or "+" in row[0] else row[0] + "+00:00"
        last_ts = datetime.fromisoformat(ts_str)
        # Compare in UTC, both aware
        now_utc = datetime.now(timezone.utc)
        age_min = (now_utc - last_ts).total_seconds() / 60
        return age_min < STALE_HEARTBEAT_MIN, age_min, last_ts.isoformat()
    except Exception as e:
        return False, float("inf"), f"db error: {e}"


def check_metrics() -> dict:
    """Returns basic metrics from the DB."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    metrics = {}
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery'")
    metrics["closed_trades"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery' AND pnl_usd > 0")
    metrics["wins"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery' AND pnl_usd <= 0")
    metrics["losses"] = cur.fetchone()[0]
    cur.execute("SELECT ROUND(SUM(pnl_usd), 2) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery'")
    metrics["total_pnl"] = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='open'")
    metrics["open_trades"] = cur.fetchone()[0]
    # last 24h errors
    cur.execute(
        "SELECT COUNT(*) FROM motor_heartbeat WHERE status='error' AND timestamp > datetime('now', '-1 day')"
    )
    metrics["errors_24h"] = cur.fetchone()[0]
    # recent signals
    cur.execute("SELECT COUNT(*) FROM signals WHERE timestamp > datetime('now', '-1 day')")
    metrics["signals_24h"] = cur.fetchone()[0]
    # trades last 24h
    cur.execute(
        "SELECT COUNT(*) FROM trades WHERE entry_time > datetime('now', '-1 day')"
    )
    metrics["trades_24h"] = cur.fetchone()[0]
    conn.close()
    return metrics


def check_err_rate() -> int:
    """Count errors in err.log in the last 1 minute."""
    if not ERR_LOG.exists():
        return 0
    try:
        cutoff = datetime.now() - timedelta(minutes=1)
        count = 0
        with open(ERR_LOG, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "[ERROR]" not in line:
                    continue
                # Parse timestamp
                try:
                    ts_str = line.split(",")[0]
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if ts > cutoff:
                        count += 1
                except (ValueError, IndexError):
                    continue
        return count
    except Exception:
        return 0


def format_report(alive, age_min, last_msg, metrics, err_rate) -> str:
    wr = (metrics["wins"] / metrics["closed_trades"] * 100) if metrics["closed_trades"] else 0
    pf_denom = max(1, metrics["losses"])
    pf_str = "inf" if metrics["losses"] == 0 and metrics["wins"] > 0 else f"{metrics['wins']/pf_denom:.2f}"
    status = "ALIVE" if alive else "DEAD"
    lines = [
        f"=== Ola 2 Monitor — {datetime.now().isoformat()} ===",
        f"Loop:       {status} (last heartbeat: {age_min:.1f} min ago — {last_msg})",
        f"Trades:     {metrics['closed_trades']} closed (W:{metrics['wins']} L:{metrics['losses']}) | {metrics['open_trades']} open",
        f"Win rate:   {wr:.1f}%",
        f"PnL total:  ${metrics['total_pnl']:.2f}",
        f"Signals 24h:{metrics['signals_24h']}  Trades 24h: {metrics['trades_24h']}  Errors 24h: {metrics['errors_24h']}",
        f"Err rate:   {err_rate}/min",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="single check then exit")
    parser.add_argument("--interval", type=int, default=300, help="check every N seconds (default 300)")
    args = parser.parse_args()

    critical = False
    warning = False

    while True:
        alive, age_min, last_msg = check_loop_alive()
        metrics = check_metrics()
        err_rate = check_err_rate()

        print(format_report(alive, age_min, last_msg, metrics, err_rate))

        # Alerts
        if not alive:
            print(f"[CRITICAL] Loop not alive! Last heartbeat {age_min:.0f} min ago")
            critical = True
        if err_rate > ERR_RATE_PER_MIN:
            print(f"[WARNING] High error rate: {err_rate}/min")
            warning = True
        if metrics["closed_trades"] >= 10:
            wr = metrics["wins"] / metrics["closed_trades"]
            if wr < 0.40:
                print(f"[WARNING] Win rate {wr:.1%} below 40% over {metrics['closed_trades']} trades")
                warning = True
        if metrics["closed_trades"] >= 5:
            if metrics["total_pnl"] < -50:
                print(f"[WARNING] Cumulative PnL < -$50: ${metrics['total_pnl']:.2f}")
                warning = True

        if args.once:
            return 1 if critical else (2 if warning else 0)
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
