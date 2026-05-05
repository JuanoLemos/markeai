import json
import os
import socket as _socket
import time
import hashlib
import hmac
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests

CACHE_DIR = Path(__file__).parent / "cache"
_DOH_CACHE = {}

_ORIGINAL_GETADDRINFO = _socket.getaddrinfo


def _doh_resolve(hostname: str) -> list:
    now = time.time()
    cached = _DOH_CACHE.get(hostname)
    if cached and (now - cached[1]) < 300:
        return cached[0]
    try:
        resp = requests.get(
            "https://dns.google/resolve",
            params={"name": hostname, "type": "A"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        ips = [a["data"] for a in data.get("Answer", []) if a.get("type") == 1]
        if ips:
            _DOH_CACHE[hostname] = (ips, now)
        return ips
    except requests.RequestException:
        return []


@contextmanager
def _doh_patch():
    def patched_gai(host, port, family=0, typ=0, proto=0, flags=0):
        if isinstance(host, str) and host.endswith("polymarket.com") and not host.endswith("dns.google"):
            ips = _doh_resolve(host)
            if ips:
                results = []
                for ip in ips:
                    results.append((_socket.AF_INET, typ or _socket.SOCK_STREAM, proto or _socket.IPPROTO_TCP, "", (ip, port)))
                return results
        return _ORIGINAL_GETADDRINFO(host, port, family, typ, proto, flags)

    _socket.getaddrinfo = patched_gai
    try:
        yield
    finally:
        _socket.getaddrinfo = _ORIGINAL_GETADDRINFO


class PolymarketCollector:
    BASE_URL = "https://clob.polymarket.com"

    def __init__(self, api_key: str = "", api_secret: str = "", api_passphrase: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        CACHE_DIR.mkdir(exist_ok=True)

    def _get_headers(self, method: str, path: str, body: str = "") -> dict:
        if not self.api_key:
            return {}
        timestamp = str(int(time.time() * 1000))
        msg = timestamp + method + path + body
        signature = hmac.new(
            self.api_secret.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()
        return {
            "POLY_API_KEY": self.api_key,
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": timestamp,
            "POLY_PASSPHRASE": self.api_passphrase,
        }

    def _request(self, path: str, params: dict = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        headers = self._get_headers("GET", path)
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            pass
        with _doh_patch():
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                return {"error": str(e)}

    def get_active_markets(self, limit: int = 50) -> list:
        cache_file = CACHE_DIR / "active_markets.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < 300:
                with open(cache_file) as f:
                    return json.load(f)
        data = self._request("/markets", {"limit": limit})
        all_markets = []
        if isinstance(data, list):
            all_markets = data
        elif isinstance(data, dict) and "data" in data:
            all_markets = data["data"]
        # Filter for currently tradeable: accepting orders
        filtered = [m for m in all_markets if m.get("accepting_orders") == True]
        with open(cache_file, "w") as f:
            json.dump(filtered, f)
        return filtered

    def _find_market(self, slug: str) -> Optional[dict]:
        markets = self.get_active_markets()
        for m in markets:
            m_slug = m.get("market_slug", "") or m.get("slug", "") or m.get("ticker", "")
            if slug in m_slug or m_slug in slug:
                return m
        return None

    def get_order_book(self, market_slug: str) -> dict:
        cache_file = CACHE_DIR / f"orderbook_{market_slug}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < 30:
                with open(cache_file) as f:
                    return json.load(f)
        m = self._find_market(market_slug)
        if not m:
            return {"error": "Market not found"}
        if m.get("enable_order_book") is False:
            return {"error": "no_order_book"}
        token_id = self._slug_to_token_id(market_slug)
        if not token_id:
            return {"error": "No token_id"}
        data = self._request(f"/orderbook/{token_id}")
        if isinstance(data, dict) and "error" not in data:
            with open(cache_file, "w") as f:
                json.dump(data, f)
        return data if isinstance(data, dict) else {}

    def get_market_price(self, market_slug: str) -> Optional[float]:
        m = self._find_market(market_slug)
        if m:
            tokens = m.get("tokens", [])
            if tokens:
                prices = [t.get("price") for t in tokens if t.get("price") is not None]
                if prices:
                    return float(sum(prices) / len(prices))
        book = self.get_order_book(market_slug)
        if not book or "error" in book:
            return None
        bids = book.get("bids", [])
        if bids:
            return float(bids[0].get("price", 0))
        return None

    def get_bid_ask_imbalance(self, market_slug: str) -> Optional[float]:
        book = self.get_order_book(market_slug)
        if "error" in book or not book:
            return None
        bids = sum(float(b.get("size", 0)) for b in book.get("bids", []))
        asks = sum(float(a.get("size", 0)) for a in book.get("asks", []))
        if asks == 0:
            return None
        return round(bids / asks, 2)

    def get_depth(self, market_slug: str, levels: int = 5) -> dict:
        book = self.get_order_book(market_slug)
        if "error" in book or not book:
            return {}
        return {
            "bids": sorted(book.get("bids", []), key=lambda x: float(x.get("price", 0)), reverse=True)[:levels],
            "asks": sorted(book.get("asks", []), key=lambda x: float(x.get("price", 0)))[:levels],
        }

    def _slug_to_token_id(self, slug: str) -> Optional[str]:
        m = self._find_market(slug)
        if m:
            tokens = m.get("tokens", [])
            if tokens:
                return tokens[0].get("token_id")
            return m.get("condition_id")
        return None

    def get_trade_history(self, market_slug: str) -> list:
        data = self._request("/trades", {"market": market_slug})
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return []

    def get_market_details(self, slug: str) -> dict:
        m = self._find_market(slug)
        return m if m else {}

    POLYSCAN_API_URL = "https://api.etherscan.io/v2/api"
    USDC_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CLOB_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
    ONCHAIN_CACHE_TTL = 300

    def get_onchain_data(self) -> dict:
        cache_file = CACHE_DIR / "onchain_data.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < self.ONCHAIN_CACHE_TTL:
                try:
                    with open(cache_file) as f:
                        return json.load(f)
                except Exception:
                    cache_file.unlink(missing_ok=True)
        api_key = os.getenv("POLYSCAN_API_KEY", "")
        if not api_key or api_key in ("", "...", "tu-key-aqui"):
            return {}
        try:
            resp = requests.get(self.POLYSCAN_API_URL, params={
                "chainid": "137",
                "module": "account",
                "action": "tokentx",
                "contractaddress": self.USDC_POLYGON,
                "address": self.CLOB_EXCHANGE,
                "sort": "desc",
                "offset": 100,
                "apikey": api_key,
            }, timeout=20)
            data = resp.json()
        except requests.RequestException:
            return {}
        if data.get("status") != "1":
            return {}
        transfers = data.get("result", [])
        if not transfers:
            return {}
        now = int(time.time())
        cutoff = now - 172800
        inflow_count = inflow_usd = outflow_count = outflow_usd = 0
        addresses = set()
        for tx in transfers:
            ts = int(tx.get("timeStamp", 0))
            if ts < cutoff:
                continue
            value = float(tx.get("value", 0)) / 10 ** int(tx.get("tokenDecimal", 6))
            addr_from = tx.get("from", "").lower()
            addr_to = tx.get("to", "").lower()
            exchange = self.CLOB_EXCHANGE.lower()
            if addr_to == exchange:
                inflow_count += 1
                inflow_usd += value
            elif addr_from == exchange:
                outflow_count += 1
                outflow_usd += value
            addresses.add(addr_from)
            addresses.add(addr_to)
        addresses.discard(self.CLOB_EXCHANGE.lower())
        result = {
            "inflow_count": inflow_count,
            "inflow_usd": round(inflow_usd, 2),
            "outflow_count": outflow_count,
            "outflow_usd": round(outflow_usd, 2),
            "net_usd": round(inflow_usd - outflow_usd, 2),
            "unique_addresses": len(addresses),
            "whale_transfers": inflow_count + outflow_count,
        }
        with open(cache_file, "w") as f:
            json.dump(result, f)
        return result
