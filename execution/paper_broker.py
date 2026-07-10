import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import numpy as np


class PaperBroker:
    def __init__(self, initial_balance: float = 1000.0, slippage_pct: float = 0.001, commission_pct: float = 0.001, state_path: str = None,
                 default_sl_pct: float = 5.0, default_tp_pct: float = 10.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct
        self.max_total_exposure_pct = 0.40
        self.time_exit_config = None
        # B-08: configurable defaults from config.yaml profiles
        self.default_sl_pct = default_sl_pct
        self.default_tp_pct = default_tp_pct
        self.positions = {}
        self.trade_log = []
        self.daily_pnl = 0.0
        if state_path:
            self._state_file = Path(state_path)
            self._load_state()
        else:
            self._state_file = Path(__file__).parent.parent / "data" / "cache" / "paper_broker_state.json"
            self._load_state()

    def _state_path(self) -> Path:
        return self._state_file

    def _load_state(self):
        path = self._state_path()
        if path.exists():
            try:
                with open(path) as f:
                    state = json.load(f)
                self.balance = state.get("balance", self.initial_balance)
                self.positions = state.get("positions", {})
                self.trade_log = state.get("trade_log", [])
                self.daily_pnl = state.get("daily_pnl", 0.0)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_state(self):
        path = self._state_path()
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump({
                "balance": self.balance,
                "positions": self.positions,
                "trade_log": self.trade_log[-100:],
                "daily_pnl": self.daily_pnl,
            }, f, indent=2)

    def get_balance(self) -> float:
        return self.balance

    def get_positions(self) -> list:
        return list(self.positions.values())

    def can_open_position(self, max_position_pct: float = 0.05, max_daily_loss_pct: float = 0.10) -> tuple:
        if self.balance <= 0:
            return False, "sin_balance"
        if self.daily_pnl / self.initial_balance <= -max_daily_loss_pct:
            return False, "limite_perdida_diaria"
        return True, "ok"

    def open_position(self, market: str, ticker: str, signal: str, entry_price: float, size_usd: float,
                      stop_loss_pct: float = None, take_profit_pct: float = None, confidence: int = 50,
                      strategy_used: str = "") -> Optional[dict]:
        # B-08: use configurable defaults if not provided
        if stop_loss_pct is None:
            stop_loss_pct = self.default_sl_pct
        if take_profit_pct is None:
            take_profit_pct = self.default_tp_pct
        can_open, reason = self.can_open_position()
        if not can_open:
            return {"error": reason}
        if size_usd > self.balance:
            size_usd = self.balance * 0.95
        if size_usd > self.balance * 0.05:
            size_usd = self.balance * 0.05
        total_exposure = sum(p["size_usd"] for p in self.positions.values())
        if total_exposure + size_usd > self.initial_balance * self.max_total_exposure_pct:
            return {"error": "max_total_exposure"}
        slippage = entry_price * self.slippage_pct * (1 if signal == "LONG" else -1)
        exec_price = entry_price + slippage
        commission = size_usd * self.commission_pct
        cost = size_usd + commission
        if cost > self.balance:
            return {"error": "insufficient_balance"}
        self.balance -= cost
        position_id = f"{market}_{ticker}_{int(time.time())}"
        position = {
            "id": position_id,
            "market": market,
            "ticker": ticker,
            "signal": signal,
            "entry_price": round(exec_price, 6),
            "size_usd": round(size_usd, 2),
            "quantity": round(size_usd / exec_price, 6) if exec_price > 0 else 0,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "confidence": confidence,
            "strategy_used": strategy_used,
            "commission": round(commission, 4),
        }
        self.positions[position_id] = position
        self.trade_log.append({
            "type": "open",
            "position_id": position_id,
            "market": market,
            "ticker": ticker,
            "signal": signal,
            "price": round(exec_price, 6),
            "size": round(size_usd, 2),
            "time": position["entry_time"],
        })
        self._save_state()
        return position

    def close_position(self, position_id: str, current_price: float, reason: str = "manual") -> Optional[dict]:
        position = self.positions.pop(position_id, None)
        if not position:
            return None
        slippage = current_price * self.slippage_pct * (-1 if position["signal"] == "LONG" else 1)
        exit_price = current_price + slippage
        if position["signal"] == "LONG":
            pnl = (exit_price - position["entry_price"]) * position["quantity"]
        else:
            pnl = (position["entry_price"] - exit_price) * position["quantity"]
        commission = abs(pnl) * self.commission_pct
        pnl_net = pnl - commission
        self.balance += position["size_usd"] + pnl_net
        self.daily_pnl += pnl_net
        result = {
            "position_id": position_id,
            "market": position["market"],
            "ticker": position["ticker"],
            "signal": position["signal"],
            "entry_price": position["entry_price"],
            "exit_price": round(exit_price, 6),
            "pnl_usd": round(pnl_net, 2),
            "pnl_pct": round((pnl_net / position["size_usd"]) * 100, 2) if position["size_usd"] > 0 else 0,
            "reason": reason,
            "exit_time": datetime.now(timezone.utc).isoformat(),
            "_db_id": position.get("_db_id"),
        }
        self.trade_log.append({
            "type": "close",
            "position_id": position_id,
            "pnl": round(pnl_net, 2),
            "reason": reason,
            "time": result["exit_time"],
        })
        self._save_state()
        return result

    def set_time_exit_config(self, config: dict):
        self.time_exit_config = config or {}

    def _get_time_exit_hours(self, pos: dict, current_prices: dict) -> float:
        cfg = self.time_exit_config or {}
        market = pos.get("market", "default")
        mcfg = cfg.get(market, cfg.get("default", {"base_hours": 72, "profit_hours": 120, "loss_hours": 48, "stagnant_hours": 36}))
        entry = pos["entry_price"]
        ticker = pos["ticker"]
        price = current_prices.get(ticker)
        if price and entry > 0:
            movement_pct = abs(price - entry) / entry * 100
            if movement_pct < 0.5:
                return mcfg.get("stagnant_hours", mcfg["base_hours"])
            is_profit = (price > entry and pos["signal"] == "LONG") or (price < entry and pos["signal"] == "SHORT")
            if is_profit:
                return mcfg.get("profit_hours", mcfg["base_hours"])
            return mcfg.get("loss_hours", mcfg["base_hours"])
        return mcfg.get("base_hours", 72)

    def check_stops(self, current_prices: dict) -> list:
        closed = []
        for pid, pos in list(self.positions.items()):
            ticker = pos["ticker"]
            price = current_prices.get(ticker)
            if not price:
                continue
            if pos["signal"] == "LONG":
                stop_price = pos["entry_price"] * (1 - pos["stop_loss_pct"] / 100)
                tp_price = pos["entry_price"] * (1 + pos["take_profit_pct"] / 100)
                tp1_price = pos["entry_price"] * (1 + pos["take_profit_pct"] * 0.5 / 100)
                if price <= stop_price:
                    result = self.close_position(pid, price, "stop_loss")
                    if result:
                        closed.append(result)
                elif not pos.get("_tp1_hit") and pos["take_profit_pct"] >= 2 and price >= tp1_price:
                    partial = pos["size_usd"] * 0.5
                    pnl = (price - pos["entry_price"]) * (pos["quantity"] * 0.5)
                    self.balance += partial + pnl
                    pos["size_usd"] = round(pos["size_usd"] - partial, 2)
                    pos["quantity"] = round(pos["quantity"] / 2, 6)
                    pos["stop_loss_pct"] = 0.1
                    pos["_tp1_hit"] = True
                    self.trade_log.append({"type":"close","position_id":pid,"pnl":round(pnl,2),"reason":"partial_tp1","time":datetime.now(timezone.utc).isoformat()})
                    self._save_state()
                elif price >= tp_price:
                    result = self.close_position(pid, price, "take_profit")
                    if result:
                        closed.append(result)
            else:
                stop_price = pos["entry_price"] * (1 + pos["stop_loss_pct"] / 100)
                tp_price = pos["entry_price"] * (1 - pos["take_profit_pct"] / 100)
                tp1_price = pos["entry_price"] * (1 - pos["take_profit_pct"] * 0.5 / 100)
                if price >= stop_price:
                    result = self.close_position(pid, price, "stop_loss")
                    if result:
                        closed.append(result)
                elif not pos.get("_tp1_hit") and pos["take_profit_pct"] >= 2 and price <= tp1_price:
                    partial = pos["size_usd"] * 0.5
                    pnl = (pos["entry_price"] - price) * (pos["quantity"] * 0.5)
                    self.balance += partial + pnl
                    pos["size_usd"] = round(pos["size_usd"] - partial, 2)
                    pos["quantity"] = round(pos["quantity"] / 2, 6)
                    pos["stop_loss_pct"] = 0.1
                    pos["_tp1_hit"] = True
                    self.trade_log.append({"type":"close","position_id":pid,"pnl":round(pnl,2),"reason":"partial_tp1","time":datetime.now(timezone.utc).isoformat()})
                    self._save_state()
                elif price <= tp_price:
                    result = self.close_position(pid, price, "take_profit")
                    if result:
                        closed.append(result)
        for pid, pos in list(self.positions.items()):
            ticker = pos["ticker"]
            price = current_prices.get(ticker)
            if not price:
                continue
            atr_est = abs(pos["entry_price"] - pos["entry_price"] * (1 - pos["stop_loss_pct"] / 100))
            if atr_est <= 0:
                atr_est = pos["entry_price"] * 0.005
            if pos["signal"] == "LONG":
                target = price - atr_est * 2.5
                if target > pos["entry_price"] * (1 - pos["stop_loss_pct"] / 100):
                    pos["stop_loss_pct"] = max(0.1, (1 - target / pos["entry_price"]) * 100)
                if not pos.get("_be_applied") and (price - pos["entry_price"]) / pos["entry_price"] >= atr_est * 1.5 / pos["entry_price"]:
                    pos["stop_loss_pct"] = 0.1
                    pos["_be_applied"] = True
            else:
                target = price + atr_est * 2.5
                if target < pos["entry_price"] * (1 + pos["stop_loss_pct"] / 100):
                    pos["stop_loss_pct"] = max(0.1, (target / pos["entry_price"] - 1) * 100)
                if not pos.get("_be_applied") and (pos["entry_price"] - price) / pos["entry_price"] >= atr_est * 1.5 / pos["entry_price"]:
                    pos["stop_loss_pct"] = 0.1
                    pos["_be_applied"] = True
        for pid, pos in list(self.positions.items()):
            entry_dt = datetime.fromisoformat(pos["entry_time"])
            age_hours = (datetime.now(timezone.utc) - entry_dt).total_seconds() / 3600
            max_hours = self._get_time_exit_hours(pos, current_prices)
            if age_hours > max_hours:
                ticker = pos["ticker"]
                price = current_prices.get(ticker)
                if not price:
                    price = pos["entry_price"]
                result = self.close_position(pid, price, "time_exit")
                if result:
                    closed.append(result)
        return closed

    def get_summary(self) -> dict:
        total_invested = sum(p["size_usd"] for p in self.positions.values())
        total_trades = len([t for t in self.trade_log if t["type"] == "close"])
        winning_trades = len([t for t in self.trade_log if t["type"] == "close" and t.get("pnl", 0) > 0])
        return {
            "balance": round(self.balance, 2),
            "initial_balance": self.initial_balance,
            "total_pnl": round(self.balance - self.initial_balance, 2),
            "total_pnl_pct": round((self.balance - self.initial_balance) / self.initial_balance * 100, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "open_positions": len(self.positions),
            "exposure_usd": round(total_invested, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": round(winning_trades / total_trades * 100, 1) if total_trades > 0 else 0,
        }
