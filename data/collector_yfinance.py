import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import yfinance as yf
import pandas as pd

CACHE_DIR = Path(__file__).parent / "cache"


class YFinanceCollector:
    FOREX_PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "AUDUSD=X"]
    DEFAULT_STOCKS = ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)

    def get_historical(self, ticker: str, period: str = "7d", interval: str = "1h") -> pd.DataFrame:
        cache_key = f"{ticker}_{period}_{interval}"
        cache_file = CACHE_DIR / f"hist_{cache_key.replace('/', '_')}.parquet"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < 300:
                try:
                    return pd.read_parquet(cache_file)
                except Exception:
                    cache_file.unlink(missing_ok=True)
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            if not data.empty:
                data.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in data.columns]
                try:
                    data.to_parquet(cache_file)
                except Exception:
                    pass
            return data
        except Exception:
            return pd.DataFrame()

    def get_current_price(self, ticker: str) -> Optional[float]:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            return float(data["Close"].iloc[-1].iloc[0]) if isinstance(data["Close"].iloc[-1], pd.Series) else float(data["Close"].iloc[-1])
        return None

    def get_forex_pairs(self) -> dict:
        result = {}
        for pair in self.FOREX_PAIRS:
            price = self.get_current_price(pair)
            if price:
                data = self.get_historical(pair, period="5d", interval="1h")
                if not data.empty:
                    result[pair] = {
                        "price": price,
                        "high_24h": float(data["high"].iloc[-24:].max().iloc[0]) if isinstance(data["high"].iloc[-24:].max(), pd.Series) else float(data["high"].iloc[-24:].max()),
                        "low_24h": float(data["low"].iloc[-24:].min().iloc[0]) if isinstance(data["low"].iloc[-24:].min(), pd.Series) else float(data["low"].iloc[-24:].min()),
                        "change_24h_pct": self._calc_change(data),
                        "volume_24h": float(data["volume"].iloc[-24:].sum().iloc[0]) if isinstance(data["volume"].iloc[-24:].sum(), pd.Series) else float(data["volume"].iloc[-24:].sum()),
                    }
        return result

    def get_stocks(self, tickers: list = None) -> dict:
        result = {}
        tickers = tickers or self.DEFAULT_STOCKS
        for ticker in tickers:
            price = self.get_current_price(ticker)
            if price:
                data = self.get_historical(ticker, period="5d", interval="1h")
                if not data.empty:
                    result[ticker] = {
                        "price": price,
                        "high_24h": float(data["high"].iloc[-24:].max().iloc[0]) if isinstance(data["high"].iloc[-24:].max(), pd.Series) else float(data["high"].iloc[-24:].max()),
                        "low_24h": float(data["low"].iloc[-24:].min().iloc[0]) if isinstance(data["low"].iloc[-24:].min(), pd.Series) else float(data["low"].iloc[-24:].min()),
                        "change_24h_pct": self._calc_change(data),
                        "volume_24h": float(data["volume"].iloc[-24:].sum().iloc[0]) if isinstance(data["volume"].iloc[-24:].sum(), pd.Series) else float(data["volume"].iloc[-24:].sum()),
                    }
        return result

    def get_market_summary(self) -> dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "forex": self.get_forex_pairs(),
            "stocks": self.get_stocks(),
        }

    FUNDAMENTAL_CACHE_TTL = 3600

    def get_fundamentals(self, ticker: str) -> Optional[dict]:
        cache_file = CACHE_DIR / f"fund_{ticker.replace('/', '_')}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < self.FUNDAMENTAL_CACHE_TTL:
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception:
                    cache_file.unlink(missing_ok=True)
        try:
            t = yf.Ticker(ticker)
            info = t.info if t.info else {}
            fundamental_data = {
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "marketCap": info.get("marketCap"),
                "dividendYield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "averageVolume": info.get("averageVolume", info.get("averageDailyVolume10Day")),
                "fiftyDayAverage": info.get("fiftyDayAverage"),
                "twoHundredDayAverage": info.get("twoHundredDayAverage"),
                "sector": info.get("sector"),
                "profitMargins": info.get("profitMargins"),
                "priceToBook": info.get("priceToBook"),
                "revenueGrowth": info.get("revenueGrowth"),
                "earningsGrowth": info.get("earningsQuarterlyGrowth", info.get("earningsGrowth")),
                "quoteType": info.get("quoteType"),
                "totalAssets": info.get("totalAssets"),
                "ytdReturn": info.get("ytdReturn"),
                "expenseRatio": info.get("expenseRatio"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            }
            try:
                cal = t.calendar
                if cal and hasattr(cal, "get"):
                    ed = cal.get("Earnings Date", cal.get("earningsDate"))
                    if ed is not None:
                        if isinstance(ed, list) and len(ed) > 0:
                            ed = ed[0]
                        fundamental_data["earningsDate"] = str(ed)
            except Exception:
                pass
            cleaned = {k: v for k, v in fundamental_data.items() if v is not None}
            if cleaned:
                with open(cache_file, "w") as f:
                    json.dump(cleaned, f, default=str)
            return cleaned if cleaned else None
        except Exception:
            return None

    def _calc_change(self, data: pd.DataFrame) -> float:
        if len(data) < 2:
            return 0.0
        close_vals = data["close"]
        if isinstance(close_vals, pd.DataFrame):
            close_vals = close_vals.iloc[:, 0]
        first = float(close_vals.iloc[-24]) if len(close_vals) >= 24 else float(close_vals.iloc[0])
        last = float(close_vals.iloc[-1])
        if first == 0:
            return 0.0
        return round(((last - first) / first) * 100, 2)

    def get_dxy(self) -> Optional[float]:
        return self.get_current_price("DX-Y.NYB")

    def get_vix(self) -> Optional[float]:
        return self.get_current_price("^VIX")

    def get_usd_ars_rate(self) -> Optional[float]:
        """Obtiene la tasa USD/ARS desde Yahoo Finance."""
        return self.get_current_price("USDARS=X")
