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
STATE_PATH = BASE_DIR / "data" / "cache" / "paper_broker_state.json"
STOP_FILE = BASE_DIR / "STOP"

loop_process = None
paused = False
status = "detenido"
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


def get_status_text():
    global loop_process, paused, status
    if loop_process is None or loop_process.poll() is not None:
        return "BotEscucha — Detenido"
    if paused:
        return "BotEscucha — En pausa"
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)
        balance = state.get("balance", 0)
        pnl = state.get("balance", 1000) - 1000
        return f"BotEscucha — Corriendo | Balance: ${balance:.0f} | PnL: ${pnl:+.0f}"
    except Exception:
        return "BotEscucha — Corriendo"


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
    STOP_FILE.write_text("stop")
    if loop_process and loop_process.poll() is None:
        loop_process.wait(timeout=10)
    loop_process = None


def do_pause():
    global paused, status
    paused = True
    status = "pausado"
    stop_loop()


def do_resume():
    global paused, status
    paused = False
    status = "corriendo"
    start_loop()


def do_exit():
    stop_loop()
    if icon_instance:
        icon_instance.stop()
    os._exit(0)


def on_show():
    webbrowser_open("http://localhost:8050")


def restart_dashboard():
    try:
        subprocess.run([
            "powershell", "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'dashboard' } | Stop-Process -Force"
        ], capture_output=True, timeout=10)
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


def webbrowser_open(url):
    import webbrowser
    webbrowser.open(url)


def build_menu():
    global paused, loop_process
    running = loop_process is not None and loop_process.poll() is None
    return pystray.Menu(
        pystray.MenuItem("Mostrar Dashboard", on_show, default=True),
        pystray.MenuItem("Reiniciar Dashboard", restart_dashboard),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("▶ Reanudar" if paused else "⏸ Pausar",
                         do_resume if paused else do_pause,
                         enabled=paused or running),
        pystray.MenuItem("■ Detener", stop_loop, enabled=running and not paused),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir", do_exit),
    )


def main():
    global icon_instance

    icon = pystray.Icon("marketai", create_icon(), "BotEscucha — Detenido")
    icon_instance = icon

    def tick():
        time.sleep(1)
        while getattr(icon, '_running', True):
            try:
                icon.title = get_status_text()
                icon.menu = build_menu()
                icon.update_menu()
            except Exception:
                pass
            time.sleep(3)

    threading.Thread(target=tick, daemon=True).start()
    start_loop()
    icon.run()


if __name__ == "__main__":
    main()
