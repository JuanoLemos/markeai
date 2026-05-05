"""
ICT Fair Value Gap — Skill standalone
Market: Forex, Stocks, Crypto
Timeframe: H1, H4, D1
"""

import io
import sys
import pandas as pd


def _silent_import():
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = io.StringIO()
    try:
        from smartmoneyconcepts import smc
        return smc
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


_smc = _silent_import()


def detect_fvg(df: pd.DataFrame) -> list:
    """Detecta Fair Value Gaps no mitigados en datos OHLCV.
    
    Args:
        df: DataFrame con columnas open, high, low, close, volume
        
    Returns:
        Lista de dicts: {direction, top, bottom, mid, index, distance_pct}
    """
    if df.empty or len(df) < 20:
        return []
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [c[0].lower() for c in df.columns]
    
    fvg_result = _smc.fvg(df)
    unfilled = fvg_result.loc[
        (fvg_result["FVG"].notna()) & (fvg_result["MitigatedIndex"].isna())
    ]
    
    results = []
    current_price = float(df["close"].iloc[-1])
    for idx in unfilled.index:
        row = unfilled.loc[idx]
        top = float(row["Top"])
        bottom = float(row["Bottom"])
        mid = (top + bottom) / 2
        dist_pct = abs(current_price - mid) / current_price * 100
        direction = "bullish" if row["FVG"] == 1 else "bearish"
        results.append({
            "direction": direction,
            "top": top,
            "bottom": bottom,
            "mid": mid,
            "index": idx,
            "distance_pct": round(dist_pct, 2),
        })
    return results
