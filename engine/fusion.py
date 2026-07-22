class FusionEngine:
    def __init__(self, config: dict):
        self.config = config
        self.weights = self._build_weights()

    def _build_weights(self) -> dict:
        layers = self.config.get("layers", {})
        return {
            market: {
                layer: layers[layer].get(f"weight_{market}", 0.0)
                for layer in layers
                if layers[layer].get("enabled", True)
            }
            for market in ["polymarket", "forex", "stocks"]
        }

    def fuse(self, layer_results: dict, market: str) -> dict:
        weights = self.weights.get(market, {})
        if not weights:
            return {"signal": "WAIT", "score": 50, "confidence": 0, "layer_scores": {}, "reasoning": "no_weights"}
        valid_scores = []
        signals = []
        layer_scores = {}
        for layer_name, result in layer_results.items():
            if not result or result.get("score", 50) == 50:
                continue
            weight = weights.get(layer_name, 0)
            if weight > 0 and result.get("score") is not None:
                score = result["score"]
                raw_signal = result.get("signal", "WAIT")
                effective_signal = raw_signal if raw_signal != "WAIT" else ("LONG" if score > 50 else "SHORT")
                valid_scores.append((score, weight, effective_signal))
                layer_scores[layer_name] = {
                    "score": score,
                    "signal": effective_signal,
                    "weight": weight,
                    "reasoning": result.get("reasoning", ""),
                }
                if effective_signal != "WAIT":
                    signals.append(effective_signal)
        if not valid_scores:
            return {"signal": "WAIT", "score": 50, "confidence": 0, "layer_scores": layer_scores, "reasoning": "no_strong_signals"}
        weighted_score = sum(s * w for s, w, _ in valid_scores) / sum(w for _, w, _ in valid_scores)
        signal = "LONG" if weighted_score >= 55 else "SHORT" if weighted_score <= 45 else "WAIT"
        long_votes = signals.count("LONG")
        short_votes = signals.count("SHORT")
        total_signals = len(signals)
        total_layers = len(layer_scores)
        if total_signals > 0:
            raw_confidence = int((abs(long_votes - short_votes) / total_signals) * 100)
            confidence = int(raw_confidence * min(1.0, total_signals / 3))
        elif weighted_score != 50:
            deviation = abs(weighted_score - 50)
            raw_confidence = int(deviation * total_layers * 2)
            confidence = int(raw_confidence * min(1.0, total_layers / 3))
        else:
            confidence = 0
        confidence = max(0, min(100, confidence))
        return {
            "signal": signal,
            "score": round(float(weighted_score), 1),
            "confidence": confidence,
            "layer_scores": layer_scores,
            "reasoning": f"{long_votes}L/{short_votes}S from {len(layer_scores)} layers",
        }
