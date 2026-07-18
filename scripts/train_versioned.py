"""
train_versioned.py — Versioned meta-model training with ghost system.

Each run:
  1. Downloads fresh historical data
  2. Trains a new RandomForest model
  3. Saves as data/models/meta_model_v{N}.pkl (incrementing version)
  4. The previous model becomes the "ghost" (meta_model_ghost.pkl)
  5. Cleans old models (keeps last 3 versions)

Usage:
  python scripts/train_versioned.py

Designed to run weekly via cron/Task Scheduler.
"""
import sys
from pathlib import Path
import re

ROOT = Path(__file__).parent.parent
MODEL_DIR = ROOT / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from scripts.train_historical import build_training_data, train, TICKERS
import joblib


def _next_version() -> int:
    """Find the next available version number."""
    existing = list(MODEL_DIR.glob("meta_model_v*.pkl"))
    if not existing:
        return 1
    versions = []
    for p in existing:
        m = re.search(r"meta_model_v(\d+)\.pkl", p.name)
        if m:
            versions.append(int(m.group(1)))
    return max(versions) + 1 if versions else 1


def main():
    # Phase 1: train new model
    version = _next_version()
    print(f"Versioned train: starting v{version}")

    df = build_training_data(TICKERS, years=2)
    if df.empty:
        print("  No training data. Aborting.")
        sys.exit(1)

    print(f"  Rows: {len(df)}, LONG={len(df[df['direction']>0])}, SHORT={len(df[df['direction']<0])}")
    model = train(df)

    # Phase 2: promote previous live model to ghost
    live_path = MODEL_DIR / "meta_model.pkl"
    ghost_path = MODEL_DIR / "meta_model_ghost.pkl"
    if live_path.exists():
        joblib.dump(joblib.load(live_path), ghost_path)
        print(f"  Ghost saved: {ghost_path}")

    # Phase 3: save new model as live and versioned
    versioned_path = MODEL_DIR / f"meta_model_v{version}.pkl"
    joblib.dump(model, versioned_path)
    joblib.dump(model, live_path)
    print(f"  Live model: {live_path}")
    print(f"  Versioned:  {versioned_path}")

    # Phase 4: cleanup old models (keep last 3)
    kept = 0
    for p in sorted(MODEL_DIR.glob("meta_model_v*.pkl"), key=lambda x: -int(re.search(r'v(\d+)', x.name).group(1))):
        if kept < 3:
            kept += 1
        else:
            p.unlink()
            print(f"  Cleaned: {p.name}")

    # Phase 5: log version as signal info
    print(f"  Version #: {version}")
    print(f"  Ghost #:   v{version - 1 if version > 1 else '-'}")
    print(f"  Done.")


if __name__ == "__main__":
    main()
