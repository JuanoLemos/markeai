import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pystray
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
STATE_PATHS = {
    "normal": BASE_DIR / "data" / "cache" / "pb_normal.json",
    "fast": BASE_DIR / "data" / "cache" / "pb_fast.json",
}
STOP_FILE = BASE_DIR / "STOP"

loop_process = None
icon_instance = None


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


def _profile_pnl(profile: str) -> str:
    path = STATE_PATHS.get(profile)
    if not path or not path.exists():
        return "$0 (0.0%)"
    try:
        with open(path) as f:
            state = json.load(f)
        balance = float(state.get("balance", 1000))
        pnl = balance - 1000
        pnl_pct = (pnl / 1000) * 100
        sign = "+" if pnl >= 0 else ""
        return f"{sign}${pnl:.0f} ({sign}{pnl_pct:.1f}%)"
    except Exception:
        return "?"


def get_status_text():
    global loop_process
    if loop_process is None or loop_process.poll() is not None:
        return "servermktai — Detenido"
    normal_pnl = _profile_pnl("normal")
    fast_pnl = _profile_pnl("fast")
    return f"servermktai | N: {normal_pnl} | F: {fast_pnl}"


def start_loop():
    global loop_process
    if loop_process is not None and loop_process.poll() is None:
        return
    if STOP_FILE.exists():
        STOP_FILE.unlink()
    loop_process = subprocess.Popen(
        [sys.executable, str(BASE_DIR / "orchestrator.py"), "--mode", "loop"],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_loop():
    global loop_process
    if loop_process is None or loop_process.poll() is not None:
        return
    try:
        STOP_FILE.write_text("stop")
        loop_process.wait(timeout=3)
    except Exception:
        try:
            loop_process.kill()
        except Exception:
            pass
    loop_process = None


def do_exit():
    stop_loop()
    try:
        if icon_instance:
            icon_instance.stop()
    except Exception:
        pass
    os._exit(0)


def on_show():
    webbrowser_open("http://localhost:8050")


def activate_bot():
    start_loop()


def kill_services():
    try:
        subprocess.run(["powershell", "-Command", "Get-Process -Name python* | Stop-Process -Force"], capture_output=True, timeout=10)
    except Exception:
        pass


def start_dashboard():
    try:
        result = subprocess.run([
            "powershell", "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'dashboard' } | Measure-Object | Select-Object -ExpandProperty Count"
        ], capture_output=True, text=True, timeout=10)
        count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        if count > 0:
            return
    except Exception:
        pass
    try:
        subprocess.Popen(
            [sys.executable, str(BASE_DIR / "dashboard.py")],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def restart_dashboard():
    try:
        subprocess.run([
            "powershell", "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'dashboard' } | Stop-Process -Force"
        ], capture_output=True, timeout=10)
    except Exception:
        try:
            subprocess.run("wmic process where \"name='python.exe' and commandline like '%dashboard%'\" delete", shell=True, capture_output=True, timeout=10)
        except Exception:
            pass
    time.sleep(1)
    start_dashboard()


def webbrowser_open(url):
    import webbrowser
    webbrowser.open(url)


def build_menu():
    return pystray.Menu(
        pystray.MenuItem("Mostrar Dashboard", on_show, default=True),
        pystray.MenuItem("Reiniciar Dashboard", restart_dashboard),
        pystray.MenuItem("──────────────────", None, enabled=False),
        pystray.MenuItem("▶ Activar", activate_bot),
        pystray.MenuItem("──────────────────", None, enabled=False),
        pystray.MenuItem("💀 Kill Services", kill_services),
        pystray.MenuItem("──────────────────", None, enabled=False),
        pystray.MenuItem("Salir", do_exit),
    )


def main():
    global icon_instance

    icon = pystray.Icon("servermktai", create_icon(), "servermktai", menu=build_menu())
    icon_instance = icon

    def tick():
        time.sleep(1)
        while getattr(icon, '_running', True):
            try:
                icon.title = get_status_text()
                icon.menu = build_menu()
            except Exception:
                pass
            time.sleep(3)

    threading.Thread(target=tick, daemon=True).start()
    start_loop()
    start_dashboard()
    icon.run()


if __name__ == "__main__":
    main()
