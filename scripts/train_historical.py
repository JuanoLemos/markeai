"""
train_historical.py — Download historical data, simulate the 9 analyzers,
train a meta-model that predicts the next-day direction from analyzer scores.

Usage:
  python scripts/train_historical.py            # full run
  python scripts/train_historical.py --years 5  # override years of history
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
import joblib

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "cache" / "train"
MODEL_DIR = ROOT / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = [
    "SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "IVV", "EEM", "IWM", "XLK", "XLF", "GLD", "TLT", "VTI",
]

# Scores produced by each analyzer on a typical day
# We simulate realistic scores based on market conditions
def simulate_day_scores(ticker: str, price_data: pd.Series) -> dict:
    """Simulate the 9 analyzers for a given day's market data."""
    close = price_data.values
    if len(close) < 50:
        return None
    # Technical (RSI, MACD, Bollinger, EMAs)
    rsi = _rsi(close, 14)
    ema9 = close[-9:].mean() if len(close) >= 9 else close.mean()
    ema21 = close[-21:].mean() if len(close) >= 21 else close.mean()
    tech_score = 50 + (50 - rsi) * 0.4 if rsi else 50
    tech_signal = "LONG" if tech_score > 55 else "SHORT" if tech_score < 45 else "WAIT"

    # Macro (uses DXY/VIX — simulated as correlated to SPY movement)
    returns = np.diff(close) / close[:-1]
    vol = float(np.std(returns)) * 100 if len(returns) > 1 else 1.0
    macro_score = 50 + (close[-1] - close[-5]) / close[-5] * 100 if len(close) >= 5 else 50
    macro_signal = "LONG" if macro_score > 55 else "SHORT" if macro_score < 45 else "WAIT"

    # Sentiment (random walk around neutral)
    sent_score = 50 + float(np.random.randn(1)[0] * 5)
    sent_signal = "LONG" if sent_score > 55 else "SHORT" if sent_score < 45 else "WAIT"

    # Fundamental (P/E inertia — stable over days)
    fund_score = 50 + float(np.random.randn(1)[0] * 3)
    fund_signal = "LONG" if fund_score > 55 else "SHORT" if fund_score < 45 else "WAIT"

    # Cross-asset (correlation to SPY)
    cross_score = 50 + (close[-1] - close[-3]) / close[-3] * 60 if len(close) >= 3 else 50
    cross_signal = "LONG" if cross_score > 55 else "SHORT" if cross_score < 45 else "WAIT"

    # ADX regime
    adx_score = 55 if vol > 0.8 else 45 if vol < 0.3 else 50
    adx_signal = "LONG" if adx_score > 55 else "SHORT" if adx_score < 45 else "WAIT"

    return {
        "technical": {"signal": tech_signal, "score": round(tech_score, 1)},
        "macro": {"signal": macro_signal, "score": round(macro_score, 1)},
        "sentiment": {"signal": sent_signal, "score": round(sent_score, 1)},
        "fundamental": {"signal": fund_signal, "score": round(fund_score, 1)},
        "cross_asset": {"signal": cross_signal, "score": round(cross_score, 1)},
        "adx_regime": {"signal": adx_signal, "score": round(adx_score, 1)},
    }


def _rsi(close, period=14):
    if len(close) < period + 1:
        return 50.0
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def build_training_data(tickers, years=2):
    """Download data and simulate analyzer scores for each ticker-day."""
    import yfinance as yf
    rows = []
    end = datetime.now()
    start = end - timedelta(days=365 * years)
    for ticker in tickers:
        print(f"  Downloading {ticker}...")
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
        except Exception as e:
            print(f"    Error: {e}")
            continue
        if df.empty:
            continue
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close = close.dropna().values
        if len(close) < 100:
            continue
        for i in range(100, len(close) - 1):
            window = pd.Series(close[:i])
            scores = simulate_day_scores(ticker, window)
            if scores is None:
                continue
            next_return = (close[i + 1] - close[i]) / close[i]
            direction = 1 if next_return > 0 else -1
            rows.append({
                "ticker": ticker,
                "tech_score": scores["technical"]["score"],
                "macro_score": scores["macro"]["score"],
                "sentiment_score": scores["sentiment"]["score"],
                "fundamental_score": scores["fundamental"]["score"],
                "cross_asset_score": scores["cross_asset"]["score"],
                "adx_score": scores["adx_regime"]["score"],
                "return_1d": round(float(next_return * 100), 4),
                "direction": direction,
            })
        print(f"    {len(close)} days -> {len([r for r in rows if r['ticker']==ticker])} training rows")
    return pd.DataFrame(rows)


def train(df: pd.DataFrame) -> RandomForestClassifier:
    """Train a RandomForest on the simulated data."""
    feature_cols = ["tech_score", "macro_score", "sentiment_score",
                    "fundamental_score", "cross_asset_score", "adx_score"]
    X = df[feature_cols].values
    y = df["direction"].values
    # Convert direction to 0/1 for classification (LONG=1 if direction=1)
    y_class = (y + 1) // 2

    tscv = TimeSeriesSplit(n_splits=3)
    models = []
    accs = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y_class[train_idx], y_class[test_idx]
        clf = RandomForestClassifier(
            n_estimators=200, max_depth=6, min_samples_leaf=50,
            random_state=42, n_jobs=-1,
        )
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        accs.append(acc)
        models.append(clf)

    print(f"\n  Walk-forward accuracy: {np.mean(accs):.3f} (last fold: {accs[-1]:.3f})")
    best = models[-1]
    # Re-train on full data
    best.fit(X, y_class)
    return best


def main():
    parser = argparse.ArgumentParser(description="Train meta-model from historical data")
    parser.add_argument("--years", type=int, default=2, help="Years of history to use")
    parser.add_argument("--tickers", nargs="+", default=TICKERS, help="Tickers to train on")
    args = parser.parse_args()

    print(f"Building training data for {len(args.tickers)} tickers over {args.years} years...")
    df = build_training_data(args.tickers, years=args.years)
    if df.empty:
        print("No training data generated.")
        sys.exit(1)

    print(f"\nTotal training rows: {len(df)}")
    print(f"Direction balance: LONG={len(df[df['direction']>0])}, SHORT={len(df[df['direction']<0])}")

    print("\nTraining RandomForest classifier...")
    model = train(df)

    model_path = MODEL_DIR / "meta_model.pkl"
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    # Feature importance
    features = ["tech_score", "macro_score", "sentiment_score",
                "fundamental_score", "cross_asset_score", "adx_score"]
    print("\nFeature importance:")
    for name, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {name}: {imp:.3f}")

    print("\nDone. Meta-model ready.")


if __name__ == "__main__":
    main()
