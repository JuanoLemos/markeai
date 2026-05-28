import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import requests

CACHE_DIR = Path(__file__).parent / "cache"

BULLISH_WORDS = [
    "surge", "rally", "gain", "jump", "rise", "soar", "bull", "bullish",
    "upgrade", "beat", "record high", "outperform", "growth", "optimism",
    "recovery", "breakthrough", "momentum", "boost", "climb", "advance",
    "positive", "strong", "profit", "green", "higher", "rebound",
    "outlook raised", "raised target", "upside", "buy", "overweight",
]
BEARISH_WORDS = [
    "plunge", "crash", "tumble", "drop", "fall", "sink", "bear", "bearish",
    "downgrade", "miss", "record low", "underperform", "decline", "fear",
    "recession", "risk", "sell-off", "selloff", "weak", "loss", "worry",
    "negative", "red", "lower", "warning", "crisis", "tariff", "sanction",
    "slide", "slump", "tank", "cut", "headwind", "downside", "sell",
    "overvalued", "bubble", "layoff", "default",
]


def _classify_text(text: str) -> str:
    if not text:
        return "neutral"
    lower = text.lower()
    bull_count = sum(1 for w in BULLISH_WORDS if w in lower)
    bear_count = sum(1 for w in BEARISH_WORDS if w in lower)
    if bull_count > bear_count:
        return "bullish"
    if bear_count > bull_count:
        return "bearish"
    return "neutral"


class NewsCollector:
    NEWSAPI_URL = "https://newsapi.org/v2/everything"
    CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"

    FOREX_KEYWORDS = ["forex", "currency", "central bank", "fed", "ecb", "interest rate", "inflation", "cpi"]
    STOCKS_KEYWORDS = ["stock market", "earnings", "sec", "ipo", "nasdaq", "nyse", "sp500"]
    CRYPTO_KEYWORDS = ["bitcoin", "ethereum", "crypto", "defi", "blockchain", "polymarket", "prediction market"]

    def __init__(self, newsapi_key: str = "", cryptopanic_key: str = ""):
        self.newsapi_key = newsapi_key
        self.cryptopanic_key = cryptopanic_key
        CACHE_DIR.mkdir(exist_ok=True)

    def get_news(self, market_type: str = "all", hours_back: int = 24) -> list:
        cache_key = f"news_{market_type}_{hours_back}h"
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < 600:
                with open(cache_file) as f:
                    return json.load(f)
        articles = []
        if self.newsapi_key:
            articles.extend(self._fetch_newsapi(market_type, hours_back))
        if self.cryptopanic_key and market_type in ("crypto", "all"):
            articles.extend(self._fetch_cryptopanic(hours_back))
        if len(articles) < 5:
            rss_articles = self._fetch_rss(market_type)
            seen = {a.get("url", a.get("title")) for a in articles}
            for a in rss_articles:
                key = a.get("url", a.get("title"))
                if key and key not in seen:
                    seen.add(key)
                    articles.append(a)
        with open(cache_file, "w") as f:
            json.dump(articles, f)
        return articles

    def _fetch_newsapi(self, market_type: str, hours_back: int) -> list:
        keywords = self.CRYPTO_KEYWORDS
        if market_type == "forex":
            keywords = self.FOREX_KEYWORDS
        elif market_type == "stocks":
            keywords = self.STOCKS_KEYWORDS
        elif market_type == "all":
            keywords = self.FOREX_KEYWORDS + self.STOCKS_KEYWORDS + self.CRYPTO_KEYWORDS
        from_date = (datetime.now() - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S")
        params = {
            "q": " OR ".join(keywords),
            "from": from_date,
            "language": "en",
            "sortBy": "popularity",
            "pageSize": 50,
            "apiKey": self.newsapi_key,
        }
        try:
            resp = requests.get(self.NEWSAPI_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "source": a.get("source", {}).get("name", "NewsAPI"),
                    "title": a["title"],
                    "description": a.get("description", ""),
                    "url": a["url"],
                    "published_at": a["publishedAt"],
                    "sentiment": _classify_text(
                        (a.get("title") or "") + " " + (a.get("description") or "")
                    ),
                }
                for a in data.get("articles", [])
                if a.get("title")
            ]
        except requests.RequestException:
            return []

    def _fetch_cryptopanic(self, hours_back: int) -> list:
        params = {
            "auth_token": self.cryptopanic_key,
            "kind": "news",
            "public": "true",
        }
        if hours_back <= 24:
            params["filter"] = "hot"
        try:
            resp = requests.get(self.CRYPTOPANIC_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "source": "CryptoPanic",
                    "title": p.get("title", ""),
                    "description": p.get("metadata", {}).get("description", ""),
                    "url": p.get("url", ""),
                    "published_at": p.get("published_at", ""),
                    "sentiment": p.get("votes", {}).get("sentiment", "neutral"),
                }
                for p in data.get("results", [])
                if p.get("title")
            ]
        except requests.RequestException:
            return []

    RSS_FEEDS = {
        "forex": "https://finance.yahoo.com/news/rssindex",
        "stocks": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "crypto": "https://news.google.com/rss/search?q=cryptocurrency+bitcoin+market&hl=en-US&gl=US&ceid=US:en",
        "all": "https://news.google.com/rss/search?q=stock+market+forex+crypto+finance&hl=en-US&gl=US&ceid=US:en",
    }

    def _fetch_rss(self, market_type: str) -> list:
        url = self.RSS_FEEDS.get(market_type, self.RSS_FEEDS["all"])
        try:
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item") or soup.find_all("entry")
            articles = []
            for item in items[:20]:
                title = item.find("title")
                desc = item.find("description") or item.find("summary")
                link = item.find("link")
                pub_date = item.find("pubDate") or item.find("published")
                if not title:
                    continue
                href = link.text if link and not link.get("href") else (link.get("href") if link else "")
                articles.append({
                    "source": "RSS",
                    "title": title.text.strip(),
                    "description": desc.text.strip()[:200] if desc else "",
                    "url": href,
                    "published_at": pub_date.text.strip() if pub_date else datetime.now().isoformat(),
                    "sentiment": _classify_text(title.text),
                })
            return articles
        except Exception:
            return []

    def get_sentiment_summary(self, market_type: str = "all", hours_back: int = 24) -> dict:
        articles = self.get_news(market_type, hours_back)
        if not articles:
            return {"count": 0, "bullish": 0, "bearish": 0, "neutral": 0, "summary": ""}
        sentiment_map = {"positive": "bullish", "negative": "bearish", "bullish": "bullish", "bearish": "bearish", "lol": "neutral", "important": "bullish"}
        sentiments = []
        for a in articles:
            s = sentiment_map.get(a.get("sentiment", ""), "neutral")
            sentiments.append(s)
        bullish = sentiments.count("bullish")
        bearish = sentiments.count("bearish")
        neutral = sentiments.count("neutral")
        total = len(sentiments) or 1
        return {
            "count": len(articles),
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "bullish_pct": round(bullish / total * 100, 1),
            "bearish_pct": round(bearish / total * 100, 1),
            "top_headlines": [a["title"] for a in articles[:5]],
        }
