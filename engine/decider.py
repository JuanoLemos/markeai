import json
import os
import requests


class DeepSeekDecider:
    def __init__(self, api_key: str = None, model: str = "deepseek-v4-pro", temperature: float = 0.3, max_tokens: int = 500):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def decide(self, market: str, ticker: str, fused_signal: dict, market_data: dict, layer_details: dict) -> dict:
        prompt = self._build_prompt(market, ticker, fused_signal, market_data, layer_details)
        response = self._call_deepseek(prompt)
        decision = self._parse_response(response)
        decision["market"] = market
        decision["ticker"] = ticker
        return decision

    def _build_prompt(self, market: str, ticker: str, fused: dict, market_data: dict, layers: dict) -> str:
        layers_text = ""
        for name, data in layers.items():
            s = data.get("signal", "WAIT")
            sc = data.get("score", 50)
            r = data.get("reasoning", "")
            layers_text += f"- {name}: {s} (score: {sc}) - {r}\n"
        price = None
        if market == "polymarket":
            price = market_data.get("price")
        elif market in ("forex", "stocks"):
            ticker_data = market_data.get(ticker, {})
            price = ticker_data.get("price")
        return f"""Eres un trader cuantitativo analizando {market.upper()} - {ticker}.

DATOS DEL MERCADO:
Precio actual: {price or 'N/A'}
Datos adicionales: {json.dumps(market_data.get(ticker, market_data), default=str)[:500]}

CAPAS DE ANÁLISIS:
{layers_text}

FUSIÓN:
Señal compuesta: {fused.get("signal", "WAIT")} (score: {fused.get("score", 50)}, confianza: {fused.get("confidence", 0)})

Responde SOLO con JSON SIN markdown ni explicaciones extra:
{{
  "signal": "LONG" o "SHORT" o "WAIT",
  "confidence": 0-100,
  "entry_price": precio_numérico_si_aplica_o_null,
  "position_size_usd": número_máximo_5%_del_capital,
  "stop_loss_pct": número_entre_1_y_10,
  "take_profit_pct": número_entre_1_y_20,
  "reasoning": "razón principal en una línea"
}}"""

    def _call_deepseek(self, prompt: str) -> str:
        if not self.api_key:
            return json.dumps({"signal": "WAIT", "confidence": 0, "reasoning": "no_api_key", "entry_price": None, "position_size_usd": 0, "stop_loss_pct": 0, "take_profit_pct": 0})
        try:
            resp = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"].get("content", "")
            if not content:
                content = choice["message"].get("reasoning_content", "")
            if not content:
                return json.dumps({"signal": "WAIT", "confidence": 0, "reasoning": "empty_response", "entry_price": None, "position_size_usd": 0, "stop_loss_pct": 0, "take_profit_pct": 0})
            return content
        except Exception as e:
            return json.dumps({"signal": "WAIT", "confidence": 0, "reasoning": f"api_error: {e}", "entry_price": None, "position_size_usd": 0, "stop_loss_pct": 0, "take_profit_pct": 0})

    def _parse_response(self, response: str) -> dict:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except (json.JSONDecodeError, KeyError):
            return {"signal": "WAIT", "confidence": 0, "reasoning": "parse_error", "entry_price": None, "position_size_usd": 0, "stop_loss_pct": 0, "take_profit_pct": 0}
