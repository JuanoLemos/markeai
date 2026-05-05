class SentimentAnalyzer:
    def analyze(self, news_data: dict, deepseek_analyze: bool = False) -> dict:
        if not news_data or news_data.get("count", 0) == 0:
            return self._empty_result()
        bullish_pct = news_data.get("bullish_pct", 0)
        bearish_pct = news_data.get("bearish_pct", 0)
        net_sentiment = bullish_pct - bearish_pct
        if net_sentiment > 20:
            signal = "LONG"
            score = 50 + min(net_sentiment, 50)
        elif net_sentiment < -20:
            signal = "SHORT"
            score = 50 - min(abs(net_sentiment), 50)
        else:
            signal = "WAIT"
            score = 50
        reasoning_parts = []
        if bullish_pct > bearish_pct:
            reasoning_parts.append(f"bullish ({bullish_pct}% vs {bearish_pct}% bearish)")
        elif bearish_pct > bullish_pct:
            reasoning_parts.append(f"bearish ({bearish_pct}% vs {bullish_pct}% bullish)")
        else:
            reasoning_parts.append("neutral")
        reasoning_parts.append(f"{news_data.get('count', 0)} articles")
        return {
            "signal": signal,
            "score": round(float(score), 1),
            "reasoning": "; ".join(reasoning_parts),
            "details": {
                "bullish_pct": bullish_pct,
                "bearish_pct": bearish_pct,
                "neutral_pct": news_data.get("neutral_pct", 0),
                "total_articles": news_data.get("count", 0),
                "top_headlines": news_data.get("top_headlines", []),
            },
        }

    def _empty_result(self):
        return {"signal": "WAIT", "score": 50, "reasoning": "no_news_data", "details": {}}
