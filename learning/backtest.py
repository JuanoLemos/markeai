import numpy as np
import pandas as pd


class Backtester:
    def __init__(self):
        pass

    def run(self, market: str, ticker: str, historical_data: pd.DataFrame, strategy_params: dict = None) -> dict:
        if historical_data.empty or len(historical_data) < 50:
            return {"error": "insufficient_data", "trades": 0}
        df = historical_data.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]
        trades = []
        balance = 1000.0
        position = None
        for i in range(50, len(df)):
            window = df.iloc[:i]
            current = df.iloc[i]
            close = float(current["close"])
            if isinstance(close, pd.Series):
                close = float(close.iloc[0])
            rsi = self._calc_rsi(window["close"], 14)
            ema9 = float(window["close"].ewm(span=9).mean().iloc[-1])
            ema21 = float(window["close"].ewm(span=21).mean().iloc[-1])
            signal = "WAIT"
            if rsi is not None:
                if rsi < 30 and ema9 > ema21:
                    signal = "LONG"
                elif rsi > 70 and ema9 < ema21:
                    signal = "SHORT"
            if position is None and signal != "WAIT":
                size = balance * 0.05
                position = {
                    "entry_time": i,
                    "entry_price": close,
                    "signal": signal,
                    "size": size,
                    "stop_loss": close * (0.98 if signal == "LONG" else 1.02),
                    "take_profit": close * (1.05 if signal == "LONG" else 0.95),
                }
            elif position is not None:
                exit_reason = None
                if position["signal"] == "LONG":
                    if close <= position["stop_loss"]:
                        exit_reason = "stop_loss"
                    elif close >= position["take_profit"]:
                        exit_reason = "take_profit"
                else:
                    if close >= position["stop_loss"]:
                        exit_reason = "stop_loss"
                    elif close <= position["take_profit"]:
                        exit_reason = "take_profit"
                if exit_reason or i == len(df) - 1:
                    pnl_pct = ((close - position["entry_price"]) / position["entry_price"]) * 100
                    if position["signal"] == "SHORT":
                        pnl_pct = -pnl_pct
                    pnl_usd = position["size"] * pnl_pct / 100
                    balance += position["size"] + pnl_usd
                    trades.append({
                        "entry_time": str(df.index[position["entry_time"]]),
                        "exit_time": str(df.index[i]),
                        "signal": position["signal"],
                        "entry_price": round(position["entry_price"], 4),
                        "exit_price": round(close, 4),
                        "pnl_pct": round(pnl_pct, 2),
                        "pnl_usd": round(pnl_usd, 2),
                        "reason": exit_reason or "end_of_data",
                    })
                    position = None
        return self._calculate_metrics(trades, balance)

    def _calc_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return None
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

    def _calculate_metrics(self, trades: list, final_balance: float) -> dict:
        if not trades:
            return {"trades": 0, "win_rate": 0, "total_pnl": 0, "sharpe": 0, "max_drawdown": 0}
        wins = [t for t in trades if t["pnl_usd"] > 0]
        losses = [t for t in trades if t["pnl_usd"] <= 0]
        pnl_series = [t["pnl_usd"] for t in trades]
        total_pnl = sum(pnl_series)
        win_rate = len(wins) / len(trades) if trades else 0
        cumulative = np.cumsum(pnl_series)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = running_max - cumulative
        max_dd = max(drawdown) if len(drawdown) > 0 else 0
        sharpe = 0
        if len(pnl_series) > 1 and np.std(pnl_series) > 0:
            sharpe = (np.mean(pnl_series) / np.std(pnl_series)) * np.sqrt(252)
        profit_factor = sum(t["pnl_usd"] for t in wins) / abs(sum(t["pnl_usd"] for t in losses)) if losses and sum(t["pnl_usd"] for t in losses) != 0 else float('inf')
        return {
            "trades": len(trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate * 100, 1),
            "total_pnl_usd": round(total_pnl, 2),
            "total_pnl_pct": round((final_balance - 1000) / 1000 * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_usd": round(max_dd, 2),
            "profit_factor": round(profit_factor, 2),
            "avg_win": round(np.mean([t["pnl_usd"] for t in wins]), 2) if wins else 0,
            "avg_loss": round(np.mean([t["pnl_usd"] for t in losses]), 2) if losses else 0,
        }
