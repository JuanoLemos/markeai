import numpy as np

from ._base import BaseAnalyzer


class CrossAssetAnalyzer(BaseAnalyzer):
    def analyze(self, market_data: dict = None) -> dict:
        if not market_data:
            return self.empty_result()
        stocks = market_data.get("stocks", {})
        forex = market_data.get("forex", {})
        signals = []
        scores = []
        spy = stocks.get("SPY", {})
        qqq = stocks.get("QQQ", {})
        if spy and qqq:
            spy_change = spy.get("change_24h_pct", 0)
            qqq_change = qqq.get("change_24h_pct", 0)
            diff = qqq_change - spy_change
            if diff > 2:
                signals.append(f"tech_outperformance_{diff:.1f}%")
                scores.append(65)
            elif diff < -2:
                signals.append(f"tech_underperformance_{diff:.1f}%")
                scores.append(35)
        eurusd = forex.get("EURUSD=X", {}).get("change_24h_pct", 0)
        usdjpy = forex.get("USDJPY=X", {}).get("change_24h_pct", 0)
        if eurusd and usdjpy:
            if eurusd > 0.5 and usdjpy < -0.3:
                signals.append("usd_weakness")
                scores.append(60)
            elif eurusd < -0.5 and usdjpy > 0.3:
                signals.append("usd_strength")
                scores.append(40)
        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "no_cross_asset_signals",
            "details": {
                "spy_qqq_divergence": round(qqq_change - spy_change, 2) if spy and qqq else None,
            },
        }

