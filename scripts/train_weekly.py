"""
train_weekly.py — Weekly auto-retraining script.
Appends latest closed trades to the training dataset and re-fits the model.

Designed to run via Task Scheduler (Windows) or cron (Linux) every Sunday.

Usage:
  python scripts/train_weekly.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.database import Database


def main():
    db = Database()
    # Count recent closed trades
    conn = db._get_conn()
    recent = conn.execute(
        "SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_time > datetime('now', '-7 days')"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM trades WHERE status='closed'").fetchone()[0]
    conn.close()
    print(f"Weekly train: {recent} closed trades in last 7d ({total} total)")
    if recent < 10:
        print(f"  Not enough new data ({recent}/10 minimum). Skipping retrain.")
        return
    # Re-train meta-model with latest data
    print("  Starting historical training with new data...")
    from scripts.train_historical import build_training_data, train, TICKERS
    df = build_training_data(TICKERS, years=2)
    if df.empty:
        print("  No training data. Skipping.")
        return
    model = train(df)
    import joblib
    model_path = ROOT / "data" / "models" / "meta_model.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"  Model re-trained and saved to {model_path}")
    print("  Done.")


if __name__ == "__main__":
    main()
