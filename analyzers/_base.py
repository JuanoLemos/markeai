"""
analyzers/_base.py — Base class for all analyzers.
B-24: extracted _ensure_cols() from adx_regime/ict_smc/technical.
B-25: extracted _empty_result() from 9 analyzers into a single base class.
"""
import pandas as pd


class BaseAnalyzer:
    """Base class providing shared helpers for all analyzers.

    Subclasses inherit _empty_result() and _ensure_cols() for free.
    Override analyze() to implement the specific logic.
    """

    def empty_result(self) -> dict:
        """Standard 'no data' response shared by all analyzers."""
        return {"signal": "WAIT", "score": 50, "reasoning": "insufficient_data", "details": {}}

    def ensure_cols(self, data: pd.DataFrame, fill_volume: bool = False) -> pd.DataFrame:
        """Normalize column names to lowercase. Optionally fill missing volume column with 0.

        B-24: deduplicated across adx_regime, ict_smc, technical.
        """
        df = data.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]
        if fill_volume and "volume" not in df.columns:
            df["volume"] = 0
        return df
