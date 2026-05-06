"""
backup-critical.py — Backup de archivos críticos de MarketAI

Uso:
    python scripts/backup-critical.py              # Backup de todos los críticos
    python scripts/backup-critical.py config.yaml  # Backup de archivo específico

Archivos críticos:
    - config.yaml
    - .env
    - orchestrator.py
    - data/database.py
    - engine/decider.py
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CRITICAL_FILES = [
    "config.yaml",
    ".env",
    "orchestrator.py",
    "data/database.py",
    "engine/decider.py",
]

def backup_file(rel_path, backup_dir):
    src = PROJECT_ROOT / rel_path
    if not src.exists():
        print(f"  [SKIP] {rel_path} -- no encontrado")
        return False
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dst_name = f"{Path(rel_path).name}.{timestamp}.bak"
    dst = backup_dir / dst_name
    shutil.copy2(src, dst)
    print(f"  [OK] {rel_path} -> {dst_name}")
    return True

def backup_all(specific=None):
    date_str = datetime.now().strftime("%Y-%m-%d")
    backup_dir = PROJECT_ROOT / f".bak_{date_str}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    files = [specific] if specific else CRITICAL_FILES

    print(f"MarketAI — Backup crítico")
    print(f"Destino: {backup_dir}")
    print()

    count = 0
    for f in files:
        if backup_file(f, backup_dir):
            count += 1

    print()
    print(f"Respaldados: {count} archivo(s)")
    return count > 0

if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        for f in args:
            backup_all(specific=f)
    else:
        backup_all()
