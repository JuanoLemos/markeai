import json
import logging
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE = Path(r"C:\xampp\htdocs\MarketAI")
URL = "http://localhost:8050/api/ping"
LOG = BASE / "data" / "server" / "keep_alive.log"
WATCHDOG = BASE / "tray_watchdog.bat"
LOG.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG, level=logging.INFO, format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def is_alive() -> bool:
    try:
        req = Request(URL, method="GET")
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except (URLError, OSError):
        return False

def kill_processes(names: list[str]):
    for name in names:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode != 0:
                continue
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    pid = int(parts[1])
                    os.kill(pid, signal.SIGTERM)
                    logging.info(f"Killed {name} PID {pid}")
                except (ValueError, OSError):
                    continue
        except subprocess.TimeoutExpired:
            logging.warning(f"Timeout listing {name}")
    time.sleep(3)

def free_port(port: int):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        if result != 0:
            return
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    try:
                        pid = int(parts[-1])
                        os.kill(pid, signal.SIGTERM)
                        logging.info(f"Killed process on port {port} PID {pid}")
                    except (ValueError, OSError):
                        continue
        time.sleep(2)
    except Exception as e:
        logging.warning(f"free_port error: {e}")

def main():
    logging.info("KeepAlive check starting...")
    if is_alive():
        logging.info("Server alive - exiting")
        sys.exit(0)

    logging.warning("Server not responding - initiating recovery")
    kill_processes(["python.exe", "python3.exe"])
    free_port(8050)

    logging.info(f"Starting {WATCHDOG}")
    subprocess.Popen(
        ["cmd.exe", "/c", str(WATCHDOG)],
        shell=False, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    logging.info("Done. Next check in 5 min.")
    sys.exit(1)

if __name__ == "__main__":
    main()
