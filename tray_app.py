"""
tray_app.py — MarketAI 24/7 tray keeper (refactored 2026-07-12)

Responsabilidades:
  1. Arrancar orchestrator + dashboard al inicio (limpia huerfanos primero)
  2. Monitorear cada 10s, auto-recover con backoff fijo de 30s
  3. Health check via motor_heartbeat en la DB
  4. Log de todas las acciones a tray_app.log
  5. Menu systray: Dashboard / Update / Restart Clean / Cerrar

Reglas duras:
  - 1 orchestrator, 1 dashboard. Maximo. Sin duplicacion.
  - Restart Clean = matar todo + limpiar logs + arrancar fresh + validar
  - Update = stop + update.bat + restart fresh
  - Nunca inventar datos, solo reportar lo que el sistema dice
"""
import logging
import sqlite3
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

import pystray
from PIL import Image, ImageDraw, ImageFont

# ─── Paths ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "market.db"
STOP_FILE = BASE_DIR / "STOP"
TRAY_LOG = BASE_DIR / "tray_app.log"
ORCH_SCRIPT = BASE_DIR / "orchestrator.py"
DASH_SCRIPT = BASE_DIR / "dashboard.py"
UPDATE_BAT = BASE_DIR / "update.bat"

# ─── Tuning ─────────────────────────────────────────────────────
RECOVER_INTERVAL_S = 30      # backoff fijo
STARTUP_VALIDATE_S = 3        # segundos para validar que el proceso sigue vivo
HEALTH_CHECK_OK_MIN = 5       # heartbeat < 5min = OK, < 15 WARNING, > 15 CRITICAL
MONITOR_INTERVAL_S = 10       # cada cuanto el monitor chequea
KILL_WAIT_S = 10              # espera maxima al stop
PYTHON = sys.executable

# ─── State ──────────────────────────────────────────────────────
_proc_orch = None
_proc_dash = None
_icon = None
_last_recover_ts = 0
_monitor_lock = threading.Lock()


# ════════════════════════════════════════════════════════════════
#  Logging
# ════════════════════════════════════════════════════════════════

def _setup_logging():
    logging.basicConfig(
        filename=str(TRAY_LOG),
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    # Tambien a stderr (visible si se corre desde consola para debug)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))


def log(msg, level='info'):
    getattr(logging, level)(msg)


# ════════════════════════════════════════════════════════════════
#  Process management
# ════════════════════════════════════════════════════════════════

def _kill_pid(pid):
    """Force-kill a single PID. Best-effort, errors swallowed."""
    if pid is None:
        return
    try:
        subprocess.run(
            ["powershell", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass


def kill_orphans():
    """Kill any python.exe process whose cmdline matches orchestrator|dashboard.
    Uses PowerShell + Get-CimInstance (works on Windows even from non-admin shell)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.CommandLine -match 'orchestrator|dashboard' } | "
             "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; "
             "Write-Output $_.ProcessId }"],
            capture_output=True, text=True, timeout=15,
        )
        killed = [int(x) for x in result.stdout.strip().split() if x.isdigit()]
        if killed:
            log(f"kill_orphans: terminated {killed}")
        return killed
    except Exception as e:
        log(f"kill_orphans failed: {e}", 'error')
        return []


def kill_port_8050():
    """Kill any process listening on port 8050 before starting to avoid duplicates."""
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "netstat -ano | findstr :8050 | findstr LISTENING"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if parts:
                pid = parts[-1]
                subprocess.run(["taskkill", "/f", "/pid", pid], capture_output=True, timeout=5)
                log(f"kill_port_8050: killed PID {pid}")
    except Exception as e:
        log(f"kill_port_8050: {e}", 'error')


def _log_path(service_name):
    return BASE_DIR / f"{service_name}.stdout.log"


def _err_path(service_name):
    return BASE_DIR / f"{service_name}.stderr.log"


def start_service(script_path, name, extra_args=None):
    """Start a subprocess. Returns Popen or None on failure.
    stdout/stderr go to {name}.stdout.log / {name}.stderr.log."""
    try:
        if not script_path.exists():
            log(f"start_service({name}): script missing at {script_path}", 'error')
            return None
        if STOP_FILE.exists():
            STOP_FILE.unlink()
        args = [PYTHON, str(script_path)]
        if extra_args:
            args.extend(extra_args)
        proc = subprocess.Popen(
            args,
            cwd=str(BASE_DIR),
            stdout=open(_log_path(name), 'a'),
            stderr=open(_err_path(name), 'a'),
        )
        log(f"start_service({name}): PID={proc.pid}")
        return proc
    except Exception as e:
        log(f"start_service({name}) failed: {e}", 'error')
        return None


def validate_startup(proc, name):
    """Sleep N seconds, return True if process is still alive."""
    if proc is None:
        return False
    time.sleep(STARTUP_VALIDATE_S)
    if proc.poll() is None:
        log(f"validate_startup({name}): alive (PID {proc.pid})")
        return True
    log(f"validate_startup({name}): DIED within {STARTUP_VALIDATE_S}s", 'error')
    return False


def stop_service(proc, name):
    """Stop a single service cleanly via STOP file, with fallback to kill."""
    if proc is None or proc.poll() is not None:
        return
    log(f"stop_service({name}): sending STOP")
    if not STOP_FILE.exists():
        STOP_FILE.write_text("stop")
    try:
        proc.wait(timeout=KILL_WAIT_S)
        log(f"stop_service({name}): exited cleanly")
    except subprocess.TimeoutExpired:
        log(f"stop_service({name}): timeout, force killing", 'warning')
        proc.kill()
        try:
            proc.wait(timeout=3)
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
#  Health check
# ════════════════════════════════════════════════════════════════

def health_check():
    """Read latest motor_heartbeat. Returns (alive_bool, age_min, status_str)."""
    try:
        if not DB_PATH.exists():
            return False, None, "no_db"
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        try:
            cur = conn.cursor()
            cur.execute("SELECT timestamp FROM motor_heartbeat ORDER BY timestamp DESC LIMIT 1")
            row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return False, None, "no_heartbeat"
        ts_str = row[0].replace("Z", "+00:00") if ("Z" in row[0] or "+" in row[0]) else row[0] + "+00:00"
        last = datetime.fromisoformat(ts_str)
        age_min = (datetime.now(timezone.utc) - last).total_seconds() / 60
        if age_min < HEALTH_CHECK_OK_MIN:
            return True, age_min, "ok"
        elif age_min < 15:
            return False, age_min, "stale"
        return False, age_min, "dead"
    except Exception as e:
        log(f"health_check error: {e}", 'error')
        return False, None, "error"


# ════════════════════════════════════════════════════════════════
#  Auto-recover
# ════════════════════════════════════════════════════════════════

def auto_recover():
    """Check process state and restart if needed. Backoff fijo 30s."""
    global _proc_orch, _proc_dash, _last_recover_ts

    with _monitor_lock:
        now = time.time()
        if now - _last_recover_ts < RECOVER_INTERVAL_S:
            return  # backoff
        _last_recover_ts = now

        # Check orchestrator
        if _proc_orch is None or _proc_orch.poll() is not None:
            log("auto_recover: orchestrator dead, restarting")
            _proc_orch = start_service(ORCH_SCRIPT, "orchestrator", ["--mode", "loop"])
            if _proc_orch:
                validate_startup(_proc_orch, "orchestrator")
            return

        # Check dashboard
        if _proc_dash is None or _proc_dash.poll() is not None:
            log("auto_recover: dashboard dead, restarting")
            _proc_dash = start_service(DASH_SCRIPT, "dashboard")
            if _proc_dash:
                validate_startup(_proc_dash, "dashboard")

        # Health check: even if process alive, heartbeat may be stale
        alive, age, status = health_check()
        if not alive and status == "stale":
            log(f"auto_recover: heartbeat stale ({age:.1f}min), consider restart")
        elif status == "dead":
            log(f"auto_recover: heartbeat dead ({age:.1f}min), forcing restart")
            stop_service(_proc_orch, "orchestrator")
            _proc_orch = start_service(ORCH_SCRIPT, "orchestrator", ["--mode", "loop"])
            if _proc_orch:
                validate_startup(_proc_orch, "orchestrator")


# ════════════════════════════════════════════════════════════════
#  Log management
# ════════════════════════════════════════════════════════════════

LOG_FILES_TO_CLEAR = [
    "tray_app.log",
    "orchestrator.log",
    "orchestrator.stdout.log",
    "orchestrator.stderr.log",
    "dashboard.stdout.log",
    "dashboard.stderr.log",
    "update.log",
]


def clear_logs():
    """Truncate all log files (preserves them but empty)."""
    for name in LOG_FILES_TO_CLEAR:
        path = BASE_DIR / name
        try:
            if path.exists():
                path.write_text("")
        except Exception as e:
            log(f"clear_logs: failed to clear {name}: {e}", 'warning')


# ════════════════════════════════════════════════════════════════
#  Menu actions
# ════════════════════════════════════════════════════════════════

def on_show():
    webbrowser.open("http://localhost:8050")


def restart_all_clean():
    """Git pull + kill orphans + clear logs + start fresh."""
    global _proc_orch, _proc_dash
    log("=== UPDATE & RESTART ===")
    stop_service(_proc_orch, "orchestrator")
    stop_service(_proc_dash, "dashboard")
    time.sleep(2)
    kill_orphans()
    time.sleep(2)
    # Git pull
    try:
        r = subprocess.run(["git", "pull", "origin", "main"], cwd=str(BASE_DIR),
                           capture_output=True, text=True, timeout=60)
        log(f"git pull: {r.stdout.strip() or 'up to date'}")
    except Exception as e:
        log(f"git pull failed: {e}")
    # Clear logs
    clear_logs()
    for h in logging.getLogger().handlers[:]:
        if hasattr(h, 'baseFilename'):
            h.close()
            logging.getLogger().removeHandler(h)
    _setup_logging()
    log("=== UPDATE & RESTART: code updated, starting fresh ===")
    _proc_orch = start_service(ORCH_SCRIPT, "orchestrator", ["--mode", "loop"])
    if _proc_orch:
        validate_startup(_proc_orch, "orchestrator")
    _proc_dash = start_service(DASH_SCRIPT, "dashboard")
    if _proc_dash:
        validate_startup(_proc_dash, "dashboard")
    log("=== UPDATE & RESTART COMPLETE ===")


def do_close():
    """Stop everything and exit."""
    log("=== TRAY CLOSING ===")
    stop_service(_proc_orch, "orchestrator")
    stop_service(_proc_dash, "dashboard")
    time.sleep(1)
    kill_orphans()
    if _icon:
        try:
            _icon.stop()
        except Exception:
            pass
    sys.exit(0)


# ════════════════════════════════════════════════════════════════
#  Tray icon + menu
# ════════════════════════════════════════════════════════════════

def create_icon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("segoeui.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "$", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1]
    draw.text((x, y), "$", fill="white", font=font)
    return img


def get_tooltip():
    alive, age, status = health_check()
    if alive:
        return f"MarketAI — OK ({age:.1f}min)"
    elif status == "stale":
        return f"MarketAI — STALE ({age:.1f}min)"
    elif status == "dead":
        return f"MarketAI — DEAD ({age:.1f}min)"
    elif status == "no_heartbeat":
        return "MarketAI — sin heartbeats"
    elif status == "no_db":
        return "MarketAI — DB no existe"
    return "MarketAI — error"


def build_menu():
    return pystray.Menu(
        pystray.MenuItem("🌐 Dashboard", on_show, default=True),
        pystray.MenuItem("─────────────", None, enabled=False),
        pystray.MenuItem("🔄 Update & Restart", restart_all_clean),
        pystray.MenuItem("─────────────", None, enabled=False),
        pystray.MenuItem("❌ Cerrar", do_close),
    )


# ════════════════════════════════════════════════════════════════
#  Monitor loop
# ════════════════════════════════════════════════════════════════

def monitor_loop():
    """Background thread: auto_recover every MONITOR_INTERVAL_S."""
    log("monitor_loop started")
    while True:
        try:
            auto_recover()
            # Update icon tooltip with health
            if _icon:
                _icon.title = get_tooltip()
        except Exception as e:
            log(f"monitor_loop error: {e}", 'error')
        time.sleep(MONITOR_INTERVAL_S)


# ════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════

def main():
    global _proc_orch, _proc_dash, _icon

    _setup_logging()
    log("=" * 60)
    log("TRAY APP STARTED")

    # 1. Cleanup: matar todo lo viejo
    log("Step 1: killing orphans + port 8050")
    kill_orphans()
    kill_port_8050()
    time.sleep(3)

    # 2. Start services
    log("Step 2: starting orchestrator")
    _proc_orch = start_service(ORCH_SCRIPT, "orchestrator", ["--mode", "loop"])
    if _proc_orch and not validate_startup(_proc_orch, "orchestrator"):
        log("orchestrator failed to start, will retry in monitor loop", 'error')

    log("Step 3: starting dashboard")
    _proc_dash = start_service(DASH_SCRIPT, "dashboard")
    if _proc_dash and not validate_startup(_proc_dash, "dashboard"):
        log("dashboard failed to start, will retry in monitor loop", 'error')

    # 3. Icon
    log("Step 4: creating tray icon")
    _icon = pystray.Icon("servermktai", create_icon(), get_tooltip(), menu=build_menu())

    # 4. Monitor thread
    log("Step 5: starting monitor thread")
    threading.Thread(target=monitor_loop, daemon=True, name="tray-monitor").start()

    log("Step 6: tray icon running (UI loop)")
    _icon.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}", 'error')
        raise
