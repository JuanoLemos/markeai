"""
analyzers/meta_model.py — Meta-model analyzer (10th layer).
Uses a trained RandomForest to predict next-day direction from the 9 analyzer scores.
The model is trained offline by scripts/train_historical.py and loaded at runtime.

When no model is found, returns WAIT gracefully (non-blocking failure).
"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent.parent
MODEL_PATH = ROOT / "data" / "models" / "meta_model.pkl"

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        import joblib
        if MODEL_PATH.exists():
            _model = joblib.load(MODEL_PATH)
    except Exception:
        pass
    return _model


def analyze(scores: dict) -> dict:
    """Run the meta-model on the 9 analyzer scores.
    
    Args:
        scores: dict like {"technical": {"signal":"LONG","score":72}, ...}
    
    Returns:
        dict with signal, score, reasoning (standard analyzer format).
    """
    model = _load_model()
    if model is None:
        return {"signal": "WAIT", "score": 50, "reasoning": "no_model_trained",
                "details": {"source": "meta_model", "model_path": str(MODEL_PATH)}}

    features = _extract_features(scores)
    if features is None:
        return {"signal": "WAIT", "score": 50, "reasoning": "insufficient_features",
                "details": {"source": "meta_model"}}

    proba = model.predict_proba([features])[0]
    prediction = model.predict([features])[0]
    confidence = float(max(proba) * 100)

    # Map model output (1=LONG, 0=SHORT) to signal
    signal = "LONG" if prediction == 1 else "SHORT"
    score = confidence if prediction == 1 else 100 - confidence

    if confidence < 55:
        signal = "WAIT"
        score = 50

    return {
        "signal": signal,
        "score": round(score, 1),
        "reasoning": f"meta_model: {signal} (conf={confidence:.0f}%)",
        "details": {
            "source": "meta_model",
            "confidence": round(confidence, 1),
            "proba_long": round(float(proba[1]), 3),
        },
    }


def _extract_features(scores: dict) -> list:
    """Extract numeric feature vector from the 9 analyzer scores.
    
    Expected keys: technical, fundamental, macro, sentiment, onchain,
    orderbook, cross_asset, adx_regime, ict_smc.
    Each value is a dict with at least 'score'.
    Returns None if too few scores are available.
    """
    feature_keys = [
        "technical", "macro", "sentiment", "fundamental",
        "cross_asset", "adx_regime",
    ]
    features = []
    for key in feature_keys:
        layer = scores.get(key, {})
        sc = layer.get("score", 50) if isinstance(layer, dict) else 50
        features.append(sc)
    # If we couldn't get at least 4 features, abort
    if sum(1 for f in features if f > 0) < 4:
        return None
    return features
