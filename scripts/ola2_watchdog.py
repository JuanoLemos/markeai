"""
ola2_watchdog.py — Watchdog operacional del server (Mavis-allá).

Corre cada 5 min vía Task Scheduler. Chequea 7 dimensiones de salud del sistema
y escribe resultados a data/server/. NO commitea, NO reinicia, NO modifica código.
Solo informa. Las alertas CRITICAL salen por Telegram con rate limiting.

Spec: doc/server/SERVER_MANDATE.md

Exit codes:
    0  OK
    1  CRITICAL
    2  WARNING
    3  Error interno del watchdog (no pudo correr los checks)

Usage:
    python scripts/ola2_watchdog.py              # single run (modo Task Scheduler)
    python scripts/ola2_watchdog.py --once       # alias explícito de "single run"
    python scripts/ola2_watchdog.py --loop --interval 300   # loop infinito (debug)
    python scripts/ola2_watchdog.py --dry-run    # no escribe a disco, no envía Telegram
"""
import argparse
import json
import shutil
import socket
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "market.db"
ERR_LOG = ROOT / "orchestrator.err.log"
SERVER_DIR = ROOT / "data" / "server"
HEARTBEAT_FILE = SERVER_DIR / "heartbeat.json"
WATCHDOG_LOG = SERVER_DIR / "watchdog.log"
INCIDENTS_DIR = SERVER_DIR / "incidents"
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050

# Thresholds (alineados con SERVER_MANDATE.md)
LOOP_STALE_WARN_MIN = 5
LOOP_STALE_CRIT_MIN = 15
ERR_RATE_WARN_PER_MIN = 10
ERR_RATE_CRIT_PER_MIN = 30
DRAWDOWN_WARN_PCT = -3.0
DRAWDOWN_CRIT_PCT = -5.0
WR_DRIFT_WARN_PCT = 40.0
WR_DRIFT_WARN_N = 10
WR_DRIFT_CRIT_PCT = 30.0
WR_DRIFT_CRIT_N = 20
DISK_WARN_GB = 2.0
DISK_CRIT_GB = 0.5
TELEGRAM_RATE_LIMIT_MIN = 30


# ════════════════════════════════════════════
# Checks
# ════════════════════════════════════════════

def check_loop_alive() -> dict:
    """Lee último motor_heartbeat. Evalúa staleness."""
    try:
        if not DB_PATH.exists():
            return {"status": "critical", "age_min": float("inf"), "msg": "db missing"}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT timestamp, status FROM motor_heartbeat ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return {"status": "critical", "age_min": float("inf"), "msg": "no heartbeats"}
        ts_str = row[0].replace("Z", "+00:00") if ("Z" in row[0] or "+" in row[0]) else row[0] + "+00:00"
        last_ts = datetime.fromisoformat(ts_str)
        now_utc = datetime.now(timezone.utc)
        age_min = (now_utc - last_ts).total_seconds() / 60
        if age_min > LOOP_STALE_CRIT_MIN:
            return {"status": "critical", "age_min": round(age_min, 1),
                    "last_ts": last_ts.isoformat(), "last_status": row[1],
                    "msg": f"heartbeat stale {age_min:.1f}min (>{LOOP_STALE_CRIT_MIN}min)"}
        if age_min > LOOP_STALE_WARN_MIN:
            return {"status": "warning", "age_min": round(age_min, 1),
                    "last_ts": last_ts.isoformat(), "last_status": row[1],
                    "msg": f"heartbeat stale {age_min:.1f}min (>{LOOP_STALE_WARN_MIN}min)"}
        return {"status": "ok", "age_min": round(age_min, 1),
                "last_ts": last_ts.isoformat(), "last_status": row[1],
                "msg": "fresh"}
    except Exception as e:
        return {"status": "critical", "age_min": float("inf"), "msg": f"check error: {e}"}


def check_dashboard() -> dict:
    """TCP socket al puerto del dashboard."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((DASHBOARD_HOST, DASHBOARD_PORT))
        sock.close()
        if result == 0:
            return {"status": "ok", "port": DASHBOARD_PORT, "msg": "listening"}
        return {"status": "critical", "port": DASHBOARD_PORT,
                "msg": f"connect_ex={result} (puerto cerrado)"}
    except Exception as e:
        return {"status": "critical", "port": DASHBOARD_PORT, "msg": f"check error: {e}"}


def check_err_rate() -> dict:
    """Cuenta [ERROR] en orchestrator.err.log de los últimos 1 min."""
    if not ERR_LOG.exists():
        return {"status": "ok", "errors_per_min": 0, "msg": "no err.log"}
    try:
        cutoff = datetime.now() - timedelta(minutes=1)
        count = 0
        with open(ERR_LOG, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "[ERROR]" not in line:
                    continue
                try:
                    ts_str = line.split(",")[0].strip()
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if ts > cutoff:
                        count += 1
                except (ValueError, IndexError):
                    continue
        if count > ERR_RATE_CRIT_PER_MIN:
            return {"status": "critical", "errors_per_min": count,
                    "msg": f"{count} errors/min (>{ERR_RATE_CRIT_PER_MIN}/min)"}
        if count > ERR_RATE_WARN_PER_MIN:
            return {"status": "warning", "errors_per_min": count,
                    "msg": f"{count} errors/min (>{ERR_RATE_WARN_PER_MIN}/min)"}
        return {"status": "ok", "errors_per_min": count, "msg": "low"}
    except Exception as e:
        return {"status": "warning", "errors_per_min": -1, "msg": f"check error: {e}"}


def check_drawdown() -> dict:
    """Drawdown via PaperBroker state file (includes unrealized PnL from open trades)."""
    import os, json
    try:
        base = float(os.getenv("WATCHDOG_BASE_BALANCE", "1000"))
        state_path = ROOT / "data" / "cache" / "pb_fast.json"
        balance = base
        pnl_total = 0.0
        if state_path.exists():
            with open(state_path) as f:
                state = json.load(f)
            balance = state.get("balance", base)
            pnl_total = round(balance - base, 2)
        pct_total = (pnl_total / base) * 100 if base else 0.0
        pnl_today = 0.0
        if DB_PATH.exists():
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT COALESCE(SUM(pnl_usd), 0) FROM trades "
                "WHERE DATE(exit_time) = DATE('now') AND exit_reason != 'lost_recovery'"
            ).fetchone()
            conn.close()
            pnl_today = row[0] or 0.0
        if pct_total <= DRAWDOWN_CRIT_PCT:
            return {"status": "critical", "pct": round(pct_total, 2),
                    "balance": balance, "pnl_total": pnl_total, "pnl_today": pnl_today,
                    "msg": f"total drawdown {pct_total:.1f}% (<={DRAWDOWN_CRIT_PCT}%)"}
        if pct_total <= DRAWDOWN_WARN_PCT:
            return {"status": "warning", "pct": round(pct_total, 2),
                    "balance": balance, "pnl_total": pnl_total, "pnl_today": pnl_today,
                    "msg": f"total drawdown {pct_total:.1f}% (<={DRAWDOWN_WARN_PCT}%)"}
        return {"status": "ok", "pct": round(pct_total, 2),
                "balance": balance, "pnl_total": pnl_total, "pnl_today": pnl_today,
                "msg": "within limits"}
    except Exception as e:
        return {"status": "warning", "pct": 0.0, "msg": f"check error: {e}"}


def check_db_integrity() -> dict:
    """PRAGMA integrity_check sobre la DB."""
    try:
        if not DB_PATH.exists():
            return {"status": "critical", "result": "missing", "msg": "db file not found"}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        row = cur.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        result = row[0] if row else "unknown"
        if result == "ok":
            return {"status": "ok", "result": result, "msg": "integrity ok"}
        return {"status": "critical", "result": result, "msg": f"integrity: {result}"}
    except Exception as e:
        return {"status": "critical", "result": "error", "msg": f"check error: {e}"}


def check_win_rate() -> dict:
    """Win rate sobre trades cerrados válidos. Solo dispara con muestra mínima."""
    try:
        if not DB_PATH.exists():
            return {"status": "ok", "pct": 0.0, "n_trades": 0, "msg": "no db"}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        n = cur.execute(
            "SELECT COUNT(*) FROM trades "
            "WHERE status='closed' AND exit_reason != 'lost_recovery'"
        ).fetchone()[0]
        if n == 0:
            conn.close()
            return {"status": "ok", "pct": 0.0, "n_trades": 0, "msg": "no closed trades yet"}
        wins = cur.execute(
            "SELECT COUNT(*) FROM trades "
            "WHERE status='closed' AND exit_reason != 'lost_recovery' AND pnl_usd > 0"
        ).fetchone()[0]
        conn.close()
        wr = (wins / n) * 100
        if n >= WR_DRIFT_CRIT_N and wr < WR_DRIFT_CRIT_PCT:
            return {"status": "critical", "pct": round(wr, 1), "n_trades": n,
                    "wins": wins, "msg": f"win rate {wr:.1f}% <{WR_DRIFT_CRIT_PCT}% over {n} trades"}
        if n >= WR_DRIFT_WARN_N and wr < WR_DRIFT_WARN_PCT:
            return {"status": "warning", "pct": round(wr, 1), "n_trades": n,
                    "wins": wins, "msg": f"win rate {wr:.1f}% <{WR_DRIFT_WARN_PCT}% over {n} trades"}
        return {"status": "ok", "pct": round(wr, 1), "n_trades": n, "wins": wins, "msg": "ok"}
    except Exception as e:
        return {"status": "warning", "pct": 0.0, "n_trades": 0, "msg": f"check error: {e}"}


def check_disk() -> dict:
    """Espacio libre en data/ y raíz."""
    try:
        usage_data = shutil.disk_usage(SERVER_DIR if SERVER_DIR.exists() else ROOT)
        gb_free = usage_data.free / (1024 ** 3)
        if gb_free < DISK_CRIT_GB:
            return {"status": "critical", "gb_free": round(gb_free, 2),
                    "msg": f"{gb_free:.2f} GB free (<{DISK_CRIT_GB} GB)"}
        if gb_free < DISK_WARN_GB:
            return {"status": "warning", "gb_free": round(gb_free, 2),
                    "msg": f"{gb_free:.2f} GB free (<{DISK_WARN_GB} GB)"}
        return {"status": "ok", "gb_free": round(gb_free, 2), "msg": "ok"}
    except Exception as e:
        return {"status": "warning", "gb_free": 0, "msg": f"check error: {e}"}


# ════════════════════════════════════════════
# Orquestación
# ════════════════════════════════════════════

def run_all_checks() -> dict:
    """Ejecuta los 7 checks. Devuelve payload completo para heartbeat.json."""
    checks = {
        "loop_alive":    check_loop_alive(),
        "dashboard":     check_dashboard(),
        "err_rate":      check_err_rate(),
        "drawdown":      check_drawdown(),
        "db_integrity":  check_db_integrity(),
        "win_rate":      check_win_rate(),
        "disk_free":     check_disk(),
    }
    # Overall: critical gana a warning, que gana a ok
    statuses = [c["status"] for c in checks.values()]
    if "critical" in statuses:
        overall = "critical"
    elif "warning" in statuses:
        overall = "warning"
    else:
        overall = "ok"
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": overall,
        "checks": checks,
    }


def write_heartbeat(payload: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] heartbeat.json: {json.dumps(payload, indent=2)}")
        return
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def append_log(payload: dict, dry_run: bool) -> None:
    """Una línea por run en watchdog.log."""
    summary_parts = [f"{name}={chk['status']}" for name, chk in payload["checks"].items()]
    line = f"{payload['ts']}  status={payload['status']}  " + "  ".join(summary_parts) + "\n"
    if dry_run:
        print(f"[dry-run] watchdog.log: {line.rstrip()}")
        return
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def write_incident(payload: dict, dry_run: bool) -> list:
    """Por cada check en warning/critical, escribe un incident file. Devuelve lista de (tipo, level, msg)."""
    incidents_written = []
    if not INCIDENTS_DIR.exists() and not dry_run:
        INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc)
    ts_slug = ts.strftime("%Y-%m-%d-%H%M")
    for name, chk in payload["checks"].items():
        if chk["status"] not in ("warning", "critical"):
            continue
        incident = {
            "ts": payload["ts"],
            "level": chk["status"],
            "type": name,
            "message": chk.get("msg", ""),
            "evidence": {k: v for k, v in chk.items() if k not in ("status", "msg")},
            "suggested_action": SUGGESTED_ACTIONS.get(name, "Revisar manualmente."),
        }
        filename = f"{ts_slug}-{name}.json"
        path = INCIDENTS_DIR / filename
        if dry_run:
            print(f"[dry-run] incident: {path.name} -> {json.dumps(incident, ensure_ascii=False)}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(incident, f, indent=2, ensure_ascii=False)
        incidents_written.append((name, chk["status"], chk.get("msg", "")))
    return incidents_written


SUGGESTED_ACTIONS = {
    "loop_alive":   "Revisar si orchestrator está corriendo. Si no, el usuario decide reiniciar.",
    "dashboard":    "Dashboard caído. Puede ser loop vivo sin Flask, o crash del proceso web.",
    "err_rate":     "Revisar orchestrator.err.log y logs del analizador que esté fallando.",
    "drawdown":     "Evaluación manual requerida. ¿El drawdown es esperado (estrategia) o anómalo?",
    "db_integrity": "DB corrupta. NO operar hasta restaurar desde backup.",
    "win_rate":     "Win rate drift. Considerar revisar config de umbrales o session filters.",
    "disk_free":    "Liberar espacio. Logs viejos en data/cache, backups obsoletos.",
}


def maybe_alert_telegram(payload: dict, incidents: list, dry_run: bool) -> None:
    """Envía Telegram si hay CRITICAL, con rate limiting."""
    if payload["status"] != "critical":
        return
    crit = [(n, l, m) for n, l, m in incidents if l == "critical"]
    if not crit:
        return
    # Rate limit: leer último critical del log
    last_crit_ts = _last_critical_ts()
    if last_crit_ts:
        elapsed = (datetime.now(timezone.utc) - last_crit_ts).total_seconds() / 60
        if elapsed < TELEGRAM_RATE_LIMIT_MIN:
            if not dry_run:
                print(f"[watchdog] CRITICAL suprimido por rate limit ({elapsed:.1f}min < {TELEGRAM_RATE_LIMIT_MIN}min)")
            return
    # Construir mensaje
    lines = ["🚨 [CRITICAL] MarketAI server — uno o más checks en estado crítico:\n"]
    for name, level, msg in crit:
        lines.append(f"  • {name}: {msg}")
    lines.append(f"\nOverall: {payload['status'].upper()}")
    lines.append(f"Ver data/server/heartbeat.json y data/server/incidents/ para detalle.")
    lines.append("Vos decidís la acción correctiva.")
    msg = "\n".join(lines)
    if dry_run:
        print(f"[dry-run] Telegram: {msg}")
        return
    try:
        # Import lazy: notifier requiere dotenv + .env; puede no estar en el server si no se cargó.
        sys.path.insert(0, str(ROOT))
        from alerts.notifier import Notifier
        notifier = Notifier()
        sent = notifier.send_error(msg)
        if sent:
            print(f"[watchdog] Alerta CRITICAL enviada por Telegram/Discord.")
        else:
            print(f"[watchdog] Alerta CRITICAL no enviada (notifier sin canal configurado o falló).")
    except Exception as e:
        print(f"[watchdog] No se pudo enviar alerta: {e}")


def _last_critical_ts() -> Optional[datetime]:
    """Lee watchdog.log y devuelve el ts del último status=critical. None si no hay."""
    if not WATCHDOG_LOG.exists():
        return None
    try:
        last_ts = None
        with open(WATCHDOG_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if "status=critical" in line:
                    ts_str = line.split()[0]
                    try:
                        last_ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    except ValueError:
                        continue
        return last_ts
    except Exception:
        return None


# ════════════════════════════════════════════
# Main
# ════════════════════════════════════════════

def run_once(dry_run: bool = False) -> int:
    try:
        payload = run_all_checks()
    except Exception as e:
        print(f"[watchdog] ERROR ejecutando checks: {e}", file=sys.stderr)
        return 3

    write_heartbeat(payload, dry_run)
    append_log(payload, dry_run)
    incidents = write_incident(payload, dry_run)
    maybe_alert_telegram(payload, incidents, dry_run)

    # Exit code por estado
    if payload["status"] == "critical":
        return 1
    if payload["status"] == "warning":
        return 2
    return 0


def main():
    parser = argparse.ArgumentParser(description="MarketAI server watchdog")
    parser.add_argument("--once", action="store_true", help="single run (default)")
    parser.add_argument("--loop", action="store_true", help="loop infinito (debug)")
    parser.add_argument("--interval", type=int, default=300, help="segundos entre runs en --loop (default 300)")
    parser.add_argument("--dry-run", action="store_true", help="no escribe a disco ni envía Telegram")
    args = parser.parse_args()

    if args.loop:
        while True:
            code = run_once(dry_run=args.dry_run)
            print(f"[watchdog] exit_code={code} durmiendo {args.interval}s...")
            time.sleep(args.interval)
    else:
        code = run_once(dry_run=args.dry_run)
        sys.exit(code)


if __name__ == "__main__":
    main()
