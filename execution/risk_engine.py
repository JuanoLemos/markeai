import numpy as np


class RiskEngine:
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.peak_balance = initial_balance
        self.daily_pnl = 0.0
        self.trade_history = []
        self.max_position_pct = 0.05
        self.max_daily_loss_pct = 0.10
        self.max_drawdown_pct = 0.15

    def update_balance(self, current_balance: float):
        self.balance = current_balance
        self.peak_balance = max(self.peak_balance, current_balance)

    def record_trade(self, trade: dict):
        if "pnl_usd" in trade:
            self.trade_history.append(trade)
            self.daily_pnl += trade.get("pnl_usd", 0)

    def reset_daily(self):
        self.daily_pnl = 0.0

    def kelly_fraction(self, win_rate: float = None, avg_win: float = None, avg_loss: float = None) -> float:
        if win_rate is None or avg_win is None or avg_loss is None:
            stats = self._compute_stats()
            win_rate = stats["win_rate"] / 100
            avg_win = stats["avg_win"]
            avg_loss = stats["avg_loss"]
        if win_rate <= 0 or win_rate >= 1 or avg_loss <= 0:
            return self.max_position_pct * 0.5
        b = avg_win / avg_loss if avg_loss > 0 else 1
        q = 1 - win_rate
        kelly = (b * win_rate - q) / b if b > 0 else 0
        return max(0, kelly * 0.25)

    def _compute_stats(self) -> dict:
        closed = [t for t in self.trade_history if t.get("pnl_usd") is not None]
        if len(closed) < 5:
            return {"win_rate": 0, "avg_win": 0, "avg_loss": 0, "trades": len(closed)}
        wins = [t["pnl_usd"] for t in closed if t["pnl_usd"] > 0]
        losses = [t["pnl_usd"] for t in closed if t["pnl_usd"] <= 0]
        return {
            "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
            "avg_win": round(np.mean(wins), 2) if wins else 0,
            "avg_loss": round(abs(np.mean(losses)), 2) if losses else 0,
            "trades": len(closed),
        }

    def atr_stop(self, df, multiplier: float = 2.0) -> float:
        if df.empty or len(df) < 15:
            return 0.0
        high, low, close = df["high"], df["low"], df["close"]
        tr = np.maximum(high - low, np.maximum(
            abs(high - close.shift(1)),
            abs(low - close.shift(1)),
        ))
        atr = tr.rolling(14).mean().iloc[-1]
        return float(atr * multiplier) if not np.isnan(atr) else 0.0

    def position_size(self, entry_price: float, stop_price: float = None, kelly_f: float = None) -> float:
        if kelly_f is None:
            kelly_f = self.kelly_fraction()
        if stop_price and entry_price > 0 and abs(entry_price - stop_price) > 0:
            risk_per_unit = abs(entry_price - stop_price) / entry_price
            raw_size = self.balance * kelly_f / risk_per_unit
        else:
            raw_size = self.balance * kelly_f
        max_size = self.balance * self.max_position_pct
        return round(min(raw_size, max_size), 2)

    def check_daily_loss(self) -> bool:
        if self.initial_balance <= 0:
            return True
        loss_pct = abs(self.daily_pnl) / self.initial_balance
        return loss_pct <= self.max_daily_loss_pct

    def check_drawdown(self) -> bool:
        if self.peak_balance <= 0:
            return True
        dd_pct = (self.peak_balance - self.balance) / self.peak_balance
        return dd_pct <= self.max_drawdown_pct

    def circuit_breakers(self) -> tuple:
        can_trade = True
        reasons = []
        if not self.check_daily_loss():
            can_trade = False
            reasons.append("daily_loss_limit")
        if not self.check_drawdown():
            can_trade = False
            reasons.append("max_drawdown_exceeded")
        return can_trade, "; ".join(reasons) if reasons else "ok"
