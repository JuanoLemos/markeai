import os
from datetime import datetime, timezone
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

ALPACA_PAPER_URL = "https://paper-api.alpaca.markets"
ALPACA_LIVE_URL = "https://api.alpaca.markets"
OANDA_PRACTICE_URL = "https://api-fxpractice.oanda.com"
OANDA_LIVE_URL = "https://api-fxtrade.oanda.com"


class TraditionalExecutor:
    def __init__(self):
        self.alpaca_api_key = os.getenv("ALPACA_API_KEY", "")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        self.alpaca_paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
        self.oanda_api_key = os.getenv("OANDA_API_KEY", "")
        self.oanda_account_id = os.getenv("OANDA_ACCOUNT_ID", "")
        self._is_placeholder = lambda v: v in ("", "...", "tu-key-aqui")
        self.alpaca_ready = not self._is_placeholder(self.alpaca_api_key) and not self._is_placeholder(self.alpaca_secret_key)
        self.oanda_ready = not self._is_placeholder(self.oanda_api_key) and not self._is_placeholder(self.oanda_account_id)

    # ─── Alpaca REST ───────────────────────────────────────────

    def _alpaca_url(self) -> str:
        return ALPACA_PAPER_URL if self.alpaca_paper else ALPACA_LIVE_URL

    def _alpaca_headers(self) -> dict:
        return {
            "APCA-API-KEY-ID": self.alpaca_api_key,
            "APCA-API-SECRET-KEY": self.alpaca_secret_key,
            "Content-Type": "application/json",
        }

    def _alpaca_get(self, path: str) -> dict:
        try:
            resp = requests.get(
                f"{self._alpaca_url()}{path}",
                headers=self._alpaca_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": f"alpaca_request_failed: {e}"}

    def _alpaca_post(self, path: str, data: dict) -> dict:
        try:
            resp = requests.post(
                f"{self._alpaca_url()}{path}",
                headers=self._alpaca_headers(),
                json=data,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": f"alpaca_request_failed: {e}"}

    # ─── OANDA REST ────────────────────────────────────────────

    def _oanda_url(self) -> str:
        return OANDA_PRACTICE_URL if "practice" in os.getenv("OANDA_ENV", "practice") else OANDA_LIVE_URL

    def _oanda_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.oanda_api_key}",
            "Content-Type": "application/json",
        }

    def _oanda_get(self, path: str) -> dict:
        try:
            resp = requests.get(
                f"{self._oanda_url()}{path}",
                headers=self._oanda_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": f"oanda_request_failed: {e}"}

    def _oanda_post(self, path: str, data: dict) -> dict:
        try:
            resp = requests.post(
                f"{self._oanda_url()}{path}",
                headers=self._oanda_headers(),
                json=data,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": f"oanda_request_failed: {e}"}

    # ─── Stub fallback ─────────────────────────────────────────

    def _stub_place_order(self, ticker: str, side: str, size_usd: float, order_type: str = "market") -> dict:
        return {
            "id": f"stub_{ticker}_{int(__import__('time').time())}",
            "market": "forex",
            "ticker": ticker,
            "signal": side,
            "entry_price": 0.0,
            "size_usd": size_usd,
            "quantity": 0,
            "stop_loss_pct": 5,
            "take_profit_pct": 10,
            "entry_time": datetime.now(timezone.utc).isoformat(),
            "confidence": 50,
            "strategy_used": "",
            "commission": 0.0,
            "status": "simulated",
        }

    def _stub_get_balance(self) -> dict:
        return {"cash": 0, "buying_power": 0, "equity": 0}

    def _stub_get_positions(self) -> list:
        return []

    # ─── Place Order ───────────────────────────────────────────

    def place_order(self, ticker: str, side: str, size_usd: float, order_type: str = "market") -> dict:
        side_map = {"LONG": "buy", "SHORT": "sell", "BUY": "buy", "SELL": "sell"}
        mapped_side = side_map.get(side.upper(), side.lower())

        if not self.alpaca_ready:
            return self._stub_place_order(ticker, side, size_usd, order_type)

        order_data = {
            "symbol": ticker,
            "notional": str(size_usd),
            "side": mapped_side,
            "type": order_type,
            "time_in_force": "day",
        }
        result = self._alpaca_post("/v2/orders", order_data)
        if "error" in result:
            return result

        return {
            "id": result.get("id", f"alpaca_{ticker}_{datetime.now().timestamp()}"),
            "market": "stocks",
            "ticker": ticker,
            "signal": side,
            "entry_price": float(result.get("filled_avg_price", 0) or 0),
            "size_usd": size_usd,
            "quantity": float(result.get("filled_qty", result.get("qty", 0)) or 0),
            "stop_loss_pct": 5,
            "take_profit_pct": 10,
            "entry_time": result.get("filled_at", datetime.now(timezone.utc).isoformat()),
            "confidence": 70,
            "strategy_used": f"alpaca_{side}",
            "commission": 0.0,
            "status": result.get("status", "unknown"),
        }

    # ─── Get Balance ───────────────────────────────────────────

    def get_balance(self) -> dict:
        if self.alpaca_ready:
            result = self._alpaca_get("/v2/account")
            if "error" not in result:
                return {
                    "cash": float(result.get("cash", 0)),
                    "buying_power": float(result.get("buying_power", 0)),
                    "equity": float(result.get("equity", 0)),
                }
            if self.oanda_ready:
                result = self._oanda_get(f"/v3/accounts/{self.oanda_account_id}/summary")
                if "error" not in result:
                    acct = result.get("account", {})
                    return {
                        "cash": float(acct.get("balance", 0)),
                        "buying_power": float(acct.get("marginAvailable", 0)),
                        "equity": float(acct.get("NAV", 0)),
                    }
        return self._stub_get_balance()

    # ─── Get Positions ─────────────────────────────────────────

    def get_positions(self) -> list:
        if self.alpaca_ready:
            result = self._alpaca_get("/v2/positions")
            if "error" not in result:
                return [
                    {
                        "symbol": p.get("symbol"),
                        "qty": float(p.get("qty", 0)),
                        "market_value": float(p.get("market_value", 0)),
                        "unrealized_pl": float(p.get("unrealized_pl", 0)),
                        "current_price": float(p.get("current_price", 0)),
                    }
                    for p in result
                ]
        return self._stub_get_positions()
