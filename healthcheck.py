import sys
import os
import socket

def check_dashboard():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8050"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()
    if result == 0:
        sys.exit(0)
    sys.exit(1)

def check_orchestrator():
    db_path = os.path.join(os.path.dirname(__file__), "data", "market.db")
    if os.path.exists(db_path):
        sys.exit(0)
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.exists(config_path):
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "--dashboard":
        check_dashboard()
    elif arg == "--orchestrator":
        check_orchestrator()
    else:
        check_orchestrator()
