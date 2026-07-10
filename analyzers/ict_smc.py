import numpy as np
import pandas as pd

from ._base import BaseAnalyzer
from ._utils import silent_import


_smc = silent_import()


class ICTAnalyzer(BaseAnalyzer):
    def analyze(self, data: pd.DataFrame) -> dict:
        if data.empty or len(data) < 50:
            return self.empty_result()
        df = self.ensure_cols(data, fill_volume=True)
        signals = []
        scores = []

        shl = _smc.swing_highs_lows(df)
        fvg_result = _smc.fvg(df)
        ob_result = _smc.ob(df, shl)
        liq_result = _smc.liquidity(df, shl)
        bos_result = _smc.bos_choch(df, shl)

        current_idx = len(df) - 1
        lookback = range(max(0, current_idx - 10), current_idx + 1)

        unfilled_fvg = fvg_result.loc[
            (fvg_result["FVG"].notna()) & (fvg_result["MitigatedIndex"].isna())
        ]
        recent_fvg = unfilled_fvg[unfilled_fvg.index.isin(lookback)]
        for idx in recent_fvg.index:
            fvg_row = recent_fvg.loc[idx]
            fvg_top, fvg_bottom = float(fvg_row["Top"]), float(fvg_row["Bottom"])
            current_price = float(df["close"].iloc[-1])
            fvg_mid = (fvg_top + fvg_bottom) / 2
            dist_pct = abs(current_price - fvg_mid) / current_price * 100

            if fvg_row["FVG"] == 1:
                signals.append(f"bullish_fvg_{idx}")
                scores.append(65 if dist_pct < 1 else 55)
            elif fvg_row["FVG"] == -1:
                signals.append(f"bearish_fvg_{idx}")
                scores.append(35 if dist_pct < 1 else 45)

        if shl is not None and not shl.empty:
            sw_type = None
            sw_price = None
            for i in range(len(shl) - 1, -1, -1):
                row = shl.iloc[i]
                if pd.notna(row.get("HighLow")):
                    sw_type = "SwingHigh" if float(row["HighLow"]) > 0 else "SwingLow"
                    sw_price = float(row.get("Level", 0))
                    break
            if sw_type == "SwingLow":
                signals.append(f"swing_low_{sw_price:.2f}")
                scores.append(55)
            elif sw_type == "SwingHigh":
                signals.append(f"swing_high_{sw_price:.2f}")
                scores.append(45)

        recent_ob = ob_result.loc[ob_result.index.isin(lookback) & ob_result["OB"].notna()]
        for idx in recent_ob.index:
            ob_type = float(recent_ob.loc[idx, "OB"])
            if ob_type == 1:
                signals.append(f"bullish_ob_{idx}")
                scores.append(60)
            elif ob_type == -1:
                signals.append(f"bearish_ob_{idx}")
                scores.append(40)

        recent_liq = liq_result.loc[liq_result.index.isin(lookback) & liq_result["Liquidity"].notna()]
        for idx in recent_liq.index:
            liq_dir = float(recent_liq.loc[idx, "Liquidity"])
            if liq_dir > 0:
                signals.append(f"liquidity_sweep_bullish_{idx}")
                scores.append(65)
            elif liq_dir < 0:
                signals.append(f"liquidity_sweep_bearish_{idx}")
                scores.append(35)

        recent_bos = bos_result.loc[bos_result.index.isin(lookback) & bos_result["BOS"].notna()]
        for idx in recent_bos.index:
            bos_type = float(recent_bos.loc[idx, "BOS"])
            if bos_type == 1:
                signals.append(f"bos_bullish_{idx}")
                scores.append(55)
            elif bos_type == -1:
                signals.append(f"bos_bearish_{idx}")
                scores.append(45)

        if not scores:
            return self.empty_result()

        avg_score = sum(scores) / len(scores)
        signal = "LONG" if avg_score >= 55 else "SHORT" if avg_score <= 45 else "WAIT"
        return {
            "signal": signal,
            "score": round(float(avg_score), 1),
            "reasoning": "; ".join(signals) if signals else "no_ict_patterns",
            "details": {
                "fvg_count": int(recent_fvg.shape[0]) if not recent_fvg.empty else 0,
                "ob_count": int(recent_ob.shape[0]) if not recent_ob.empty else 0,
                "liquidity_sweeps": int(recent_liq.shape[0]) if not recent_liq.empty else 0,
                "bos_count": int(recent_bos.shape[0]) if not recent_bos.shape[0] else 0,
            },
        }

