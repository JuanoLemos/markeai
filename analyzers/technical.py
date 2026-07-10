import pandas as pd
import numpy as np

from ._base import BaseAnalyzer


class TechnicalAnalyzer(BaseAnalyzer):
    def analyze(self, data: pd.DataFrame) -> dict:
        if data.empty or len(data) < 26:
            return self.empty_result()
        df = self.ensure_cols(data)
        rsi = self._calc_rsi(df["close"], 14)
        macd_line, macd_signal, macd_hist = self._calc_macd(df["close"])
        bb_upper, bb_middle, bb_lower, bb_pct = self._calc_bollinger(df["close"])
        ema_9, ema_21, ema_50 = self._calc_emas(df["close"])
        support, resistance = self._calc_support_resistance(df)
        atr = self._calc_atr(df, 14)
        volume_trend = self._calc_volume_trend(df)
        signals = []
        scores = []
        if rsi is not None:
            if rsi < 30:
                signals.append(("oversold", 70))
                scores.append(70)
            elif rsi > 70:
                signals.append(("overbought", 30))
                scores.append(30)
            else:
                signals.append(("neutral_rsi", 50))
                scores.append(50)
        if ema_9 is not None and ema_21 is not None and ema_50 is not None:
            if ema_9 > ema_21 > ema_50:
                signals.append(("ema_bullish", 70))
                scores.append(70)
            elif ema_9 < ema_21 < ema_50:
                signals.append(("ema_bearish", 30))
                scores.append(30)
            else:
                signals.append(("ema_mixed", 50))
                scores.append(50)
        if macd_hist is not None and len(macd_hist) >= 2:
            if macd_hist.iloc[-1] > macd_hist.iloc[-2] and macd_hist.iloc[-1] > 0:
                signals.append(("macd_bullish", 70))
                scores.append(70)
            elif macd_hist.iloc[-1] < macd_hist.iloc[-2] and macd_hist.iloc[-1] < 0:
                signals.append(("macd_bearish", 30))
                scores.append(30)
            else:
                signals.append(("macd_neutral", 50))
                scores.append(50)
        if bb_pct is not None:
            bb_val = float(bb_pct.iloc[-1]) if hasattr(bb_pct, 'iloc') else float(bb_pct)
            if bb_val < 0:
                signals.append(("bb_oversold", 70))
                scores.append(70)
            elif bb_val > 1:
                signals.append(("bb_overbought", 30))
                scores.append(30)
            else:
                signals.append(("bb_neutral", 50))
                scores.append(50)
        if support is not None and resistance is not None:
            last_price = float(df["close"].iloc[-1])
            dist_to_support = ((last_price - support) / last_price) * 100
            dist_to_resistance = ((resistance - last_price) / last_price) * 100
            if dist_to_support < 1.0:
                signals.append(("near_support", 65))
                scores.append(65)
            elif dist_to_resistance < 1.0:
                signals.append(("near_resistance", 35))
                scores.append(35)
        avg_score = np.mean(scores) if scores else 50
        signal = "LONG" if avg_score >= 60 else "SHORT" if avg_score <= 40 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(f"{s[0]}" for s in signals),
            "details": {
                "rsi": round(float(rsi), 1) if rsi is not None else None,
                "macd_line": round(float(macd_line.iloc[-1]), 6) if macd_line is not None else None,
                "macd_signal": round(float(macd_signal.iloc[-1]), 6) if macd_signal is not None else None,
                "bb_pct": round(float(bb_pct.iloc[-1]), 3) if bb_pct is not None else None,
                "ema_9": round(float(ema_9), 2) if ema_9 is not None else None,
                "ema_21": round(float(ema_21), 2) if ema_21 is not None else None,
                "ema_50": round(float(ema_50), 2) if ema_50 is not None else None,
                "atr": round(float(atr), 4) if atr is not None else None,
                "support": round(float(support), 2) if support is not None else None,
                "resistance": round(float(resistance), 2) if resistance is not None else None,
                "volume_trend": volume_trend,
            },
        }

    def _calc_rsi(self, prices: pd.Series, period: int = 14) -> float:
        if len(prices) < period + 1:
            return None
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

    def _calc_macd(self, prices: pd.Series, fast=12, slow=26, signal=9):
        if len(prices) < slow + signal:
            return None, None, None
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram

    def _calc_bollinger(self, prices: pd.Series, period=20, std=2):
        if len(prices) < period:
            return None, None, None, None
        sma = prices.rolling(period).mean()
        rolling_std = prices.rolling(period).std()
        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)
        bb_pct = (prices - lower) / (upper - lower)
        return upper, sma, lower, bb_pct

    def _calc_emas(self, prices: pd.Series):
        if len(prices) < 50:
            return None, None, None
        return (
            float(prices.ewm(span=9).mean().iloc[-1]),
            float(prices.ewm(span=21).mean().iloc[-1]),
            float(prices.ewm(span=50).mean().iloc[-1]),
        )

    def _calc_support_resistance(self, df: pd.DataFrame, window: int = 20):
        if len(df) < window:
            return None, None
        recent = df.tail(window)
        support = float(recent["low"].min())
        resistance = float(recent["high"].max())
        return support, resistance

    def _calc_atr(self, df: pd.DataFrame, period: int = 14):
        if len(df) < period:
            return None
        high, low, close = df["high"], df["low"], df["close"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None

    def _calc_volume_trend(self, df: pd.DataFrame, window: int = 20):
        if len(df) < window:
            return "neutral"
        recent_vol = df["volume"].iloc[-5:].mean()
        hist_vol = df["volume"].iloc[-window:-5].mean()
        if hist_vol == 0:
            return "neutral"
        ratio = recent_vol / hist_vol
        if ratio > 1.5:
            return "rising"
        if ratio < 0.5:
            return "falling"
        return "neutral"
