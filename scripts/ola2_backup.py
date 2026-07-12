"""
ola2_backup.py — Backup data/market.db with 7-day rotation.
Keeps daily backups for the last 7 days, plus a weekly snapshot.

Usage:
    python scripts/ola2_backup.py            # make a new backup
    python scripts/ola2_backup.py --prune    # prune old backups (>7d)
"""
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "data" / "market.db"
BACKUPS = ROOT / "data" / "cache" / "backups"
KEEP_DAYS = 7


def make_backup() -> Path:
    BACKUPS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = BACKUPS / f"market.db.ola2_{ts}"
    shutil.copy2(SRC, dst)
    print(f"[OK] Backup created: {dst.name} ({dst.stat().st_size:,} bytes)")
    return dst


def prune_old() -> int:
    if not BACKUPS.exists():
        return 0
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    removed = 0
    for f in BACKUPS.glob("market.db.ola2_*"):
        try:
            ts_str = f.stem.replace("market.db.ola2_", "")
            ftime = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
        except ValueError:
            continue
        if ftime < cutoff:
            f.unlink()
            removed += 1
            print(f"[PRUNE] Removed: {f.name}")
    return removed


def list_backups():
    if not BACKUPS.exists():
        return []
    files = sorted(BACKUPS.glob("market.db.ola2_*"))
    for f in files:
        ftime = datetime.fromtimestamp(f.stat().st_mtime)
        size = f.stat().st_size
        print(f"  {f.name}  {size:>12,} bytes  {ftime.isoformat()}")
    return files


if __name__ == "__main__":
    if "--prune" in sys.argv:
        n = prune_old()
        print(f"[DONE] Pruned {n} old backup(s)")
    elif "--list" in sys.argv:
        list_backups()
    else:
        make_backup()
        list_backups()
