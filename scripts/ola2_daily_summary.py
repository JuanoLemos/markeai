"""
ola2_daily_summary.py — Print (and optionally send via Telegram) a daily
summary of MarketAI's performance. Designed to run via cron or Task Scheduler
at the end of each trading day.

Usage:
    python scripts/ola2_daily_summary.py            # print to stdout + log file
    python scripts/ola2_daily_summary.py --log     # also append to data/cache/daily_summary.log
"""
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB = ROOT / "data" / "market.db"
LOG = ROOT / "data" / "cache" / "daily_summary.log"


def gather() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    out = {"date": datetime.now().strftime("%Y-%m-%d")}

    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery'")
    out["closed_total"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery' AND pnl_usd > 0")
    out["wins_total"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery' AND pnl_usd <= 0")
    out["losses_total"] = cur.fetchone()[0]
    cur.execute("SELECT ROUND(SUM(pnl_usd), 2) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery'")
    out["pnl_total"] = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='open'")
    out["open_trades"] = cur.fetchone()[0]

    # Today
    cur.execute("SELECT COUNT(*) FROM trades WHERE DATE(entry_time) = DATE('now')")
    out["trades_today"] = cur.fetchone()[0]
    cur.execute(
        "SELECT ROUND(SUM(pnl_usd), 2) FROM trades "
        "WHERE DATE(exit_time) = DATE('now') AND exit_reason != 'lost_recovery'"
    )
    out["pnl_today"] = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM signals WHERE DATE(timestamp) = DATE('now')")
    out["signals_today"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM motor_heartbeat WHERE DATE(timestamp) = DATE('now') AND status='error'")
    out["errors_today"] = cur.fetchone()[0]

    conn.close()
    return out


def render(m: dict) -> str:
    wr = (m["wins_total"] / m["closed_total"] * 100) if m["closed_total"] else 0
    pf_denom = max(1, m["losses_total"])
    pf = m["wins_total"] / pf_denom if m["losses_total"] else float("inf")
    pf_str = "inf" if pf == float("inf") else f"{pf:.2f}"
    return (
        f"=== MarketAI Daily Summary — {m['date']} ===\n"
        f"Trades hoy:       {m['trades_today']}  (señales: {m['signals_today']}, errores: {m['errors_today']})\n"
        f"PnL hoy:          ${m['pnl_today']:.2f}\n"
        f"Trades cerrados:  {m['closed_total']} (W:{m['wins_total']} L:{m['losses_total']})\n"
        f"Win rate total:   {wr:.1f}%\n"
        f"Profit factor:    {pf_str}\n"
        f"PnL acumulado:    ${m['pnl_total']:.2f}\n"
        f"Posiciones open:  {m['open_trades']}\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="store_true", help="append to daily_summary.log")
    args = parser.parse_args()

    m = gather()
    out = render(m)
    print(out)
    if args.log:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(out + "\n")


if __name__ == "__main__":
    main()
