class OnChainAnalyzer:
    def analyze(self, polymarket_data: dict = None) -> dict:
        if not polymarket_data:
            return self._empty_result()
        signals = []
        scores = []
        trade_history = polymarket_data.get("trade_history", [])
        if trade_history:
            large_trades = [t for t in trade_history if float(t.get("size", 0)) > 1000]
            if large_trades:
                yes_trades = sum(1 for t in large_trades if t.get("side") == "BUY")
                no_trades = sum(1 for t in large_trades if t.get("side") == "SELL")
                if yes_trades > no_trades * 2:
                    signals.append(("whale_accumulation", 70))
                    scores.append(70)
                elif no_trades > yes_trades * 2:
                    signals.append(("whale_distribution", 30))
                    scores.append(30)
        market_details = polymarket_data.get("market_details", {})
        volume_24h = float(market_details.get("volume24hr", 0) or 0)
        if volume_24h > 0:
            liquidity_score = min(volume_24h / 100000, 1) * 20
            scores.append(50 + liquidity_score)
            signals.append(f"volume_24h_{volume_24h:.0f}")
        else:
            scores.append(50)
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "no_onchain_data",
            "details": {
                "volume_24h": volume_24h,
                "large_trades": len([t for t in trade_history if float(t.get("size", 0)) > 1000]) if trade_history else 0,
            },
        }

    def _empty_result(self):
        return {"signal": "WAIT", "score": 50, "reasoning": "no_onchain_data", "details": {}}
