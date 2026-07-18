"""
analyzers/meta_model.py — Meta-model analyzer (10th layer).
Uses a trained RandomForest to predict next-day direction from the 9 analyzer scores.
The model is trained offline by scripts/train_versioned.py and loaded at runtime.

Support ghost mode: if version='ghost', loads the previous model for shadow trading.
When no model is found, returns WAIT gracefully (non-blocking failure).
"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent.parent
MODEL_DIR = ROOT / "data" / "models"

_live_model = None
_ghost_model = None


def _load_model(version: str = "live"):
    global _live_model, _ghost_model
    if version == "live":
        if _live_model is not None:
            return _live_model
        path = MODEL_DIR / "meta_model.pkl"
    else:
        if _ghost_model is not None:
            return _ghost_model
        path = MODEL_DIR / "meta_model_ghost.pkl"
    try:
        import joblib
        if path.exists():
            model = joblib.load(path)
            if version == "live":
                _live_model = model
            else:
                _ghost_model = model
            return model
    except Exception:
        pass
    return None


def analyze(scores: dict, version: str = "live") -> dict:
    """Run the meta-model on the 9 analyzer scores.
    
    Args:
        scores: dict like {"technical": {"signal":"LONG","score":72}, ...}
        version: "live" or "ghost"
    
    Returns:
        dict with signal, score, reasoning (standard analyzer format).
    """
    model = _load_model(version)
    if model is None:
        return {"signal": "WAIT", "score": 50, "reasoning": f"no_model_{version}",
                "details": {"source": f"meta_model_{version}", "version": version}}

    features = _extract_features(scores)
    if features is None:
        return {"signal": "WAIT", "score": 50, "reasoning": "insufficient_features",
                "details": {"source": f"meta_model_{version}", "version": version}}

    proba = model.predict_proba([features])[0]
    prediction = model.predict([features])[0]
    confidence = float(max(proba) * 100)

    signal = "LONG" if prediction == 1 else "SHORT"
    score = confidence if prediction == 1 else 100 - confidence

    if confidence < 55:
        signal = "WAIT"
        score = 50

    return {
        "signal": signal,
        "score": round(score, 1),
        "reasoning": f"meta_model_{version}: {signal} (conf={confidence:.0f}%)",
        "details": {
            "source": f"meta_model_{version}",
            "version": version,
            "confidence": round(confidence, 1),
            "proba_long": round(float(proba[1]), 3),
        },
    }
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
