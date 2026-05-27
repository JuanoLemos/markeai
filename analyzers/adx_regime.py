import sys
import io
import numpy as np
import pandas as pd


def _silent_import():
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = io.StringIO()
    try:
        from smartmoneyconcepts import smc
        return smc
    finally:
        sys.stdout, sys.stderr = old_out, old_err


_smc = _silent_import()


class ADXRegimeAnalyzer:
    def analyze(self, data: pd.DataFrame) -> dict:
        if data.empty or len(data) < 30:
            return self._empty_result()
        df = self._ensure_cols(data)
        adx, pos_di, neg_di = self._calc_adx(df)
        if adx is None:
            return self._empty_result()

        signals = []
        scores = []
        details = {"adx": round(float(adx), 1), "pos_di": round(float(pos_di), 1), "neg_di": round(float(neg_di), 1)}

        if adx > 25:
            details["regime"] = "trending"
            if pos_di > neg_di:
                signals.append(f"adx_{adx:.0f}_trending_up")
                scores.append(65)
            else:
                signals.append(f"adx_{adx:.0f}_trending_down")
                scores.append(35)
        elif adx < 20:
            details["regime"] = "ranging"
            signals.append(f"adx_{adx:.0f}_ranging")
            scores.append(50)
        else:
            details["regime"] = "transition"
            signals.append(f"adx_{adx:.0f}_transition")
            scores.append(50)

        avg_score = sum(scores) / len(scores) if scores else 50
        signal = "LONG" if avg_score >= 55 else "SHORT" if avg_score <= 45 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals),
            "details": details,
        }

    def _calc_adx(self, df: pd.DataFrame, period: int = 14):
        high, low, close = df["high"].values, df["low"].values, df["close"].values
        if len(high) < period + 5:
            return None, None, None
        up = np.diff(high, prepend=high[0])
        down = np.diff(low, prepend=low[0])
        pos_dm = np.where((up > down) & (up > 0), up, 0)
        neg_dm = np.where((down > up) & (down > 0), down, 0)
        tr = np.maximum(high - low,
                        np.maximum(abs(high - np.roll(close, 1)),
                                   abs(low - np.roll(close, 1))))
        atr = self._smooth(tr, period)
        pdi = 100 * self._smooth(pos_dm, period) / np.maximum(atr, 1e-10)
        ndi = 100 * self._smooth(neg_dm, period) / np.maximum(atr, 1e-10)
        dx = 100 * abs(pdi - ndi) / np.maximum(pdi + ndi, 1e-10)
        adx = self._smooth(dx, period)
        return float(adx[-1]), float(pdi[-1]), float(ndi[-1])

    def _smooth(self, values, period):
        result = np.zeros_like(values)
        result[period] = np.mean(values[1:period + 1])
        for i in range(period + 1, len(values)):
            result[i] = (result[i - 1] * (period - 1) + values[i]) / period
        return result

    def _ensure_cols(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]
        return df

    def _empty_result(self):
        return {"signal": "WAIT", "score": 50, "reasoning": "insufficient_data", "details": {}}
