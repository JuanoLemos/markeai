import json
import os
import requests

SYSTEM_PROMPT = """Eres un trader cuantitativo profesional multi-mercado.

REGLAS DE RIESGO (obligatorias):
- Riesgo máximo por operación: 2% del capital
- Cash buffer mínimo: 30% (no comprometer >70% del capital en posiciones abiertas)
- Toda posición DEBE tener stop-loss (SL) y take-profit (TP) concretos
- Si ningún SL/TP se activa, mantener la posición — no cerrar prematuramente
- No martingala ni promediar a la baja sin nuevo SL/TP
- Si el mercado está neutral o hay conflicto entre capas → WAIT

MARCO DE DECISIÓN:
1. Analiza cada capa de análisis (técnico, fundamental, sentimiento, macro, etc.)
2. Identifica si las capas convergen en la misma dirección o se contradicen
3. Si hay convergencia clara (≥2 capas en misma dirección con score >55): LONG/SHORT
4. Si hay conflicto (50% LONG, 50% SHORT): WAIT
5. Si todas las capas son neutrales: WAIT

EJEMPLOS DE DECISIONES CORRECTAS:

Ejemplo 1 (LONG):
Input: técnico=LONG(72), macro=LONG(65), sentimiento=WAIT(50)
Output: {"signal":"LONG","confidence":75,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"Capas tecnica y macro convergen alcistas. RSI en 42 rebotando desde oversold, DXY debil favoreciendo activos de riesgo."}

Ejemplo 2 (WAIT):
Input: técnico=WAIT(52), fundamental=SHORT(48), macro=WAIT(50)
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"Capas contradictorias: tecnico neutral, fundamental ligeramente bajista. Sin convergencia clara."}
"""


class DeepSeekDecider:
    def __init__(self, api_key: str = None, model: str = "deepseek-v4-pro", temperature: float = 0.3, max_tokens: int = 500):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def decide(self, market: str, ticker: str, fused_signal: dict, market_data: dict, layer_details: dict) -> dict:
        system_prompt = SYSTEM_PROMPT
        user_prompt = self._build_prompt(market, ticker, fused_signal, market_data, layer_details)
        response = self._call_deepseek(system_prompt, user_prompt)
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
        active_positions = market_data.get("open_positions", [])
        positions_text = ""
        if active_positions:
            for p in active_positions:
                positions_text += f"  {p.get('ticker','?')} | {p.get('signal','?')} | entry:{p.get('entry_price','?')} | SL:{p.get('stop_loss_pct','?')}% | TP:{p.get('take_profit_pct','?')}%\n"
        else:
            positions_text = "  Sin posiciones abiertas"
        return f"""## Mercado: {market.upper()} - {ticker}

### Datos del mercado
Precio actual: {price or 'N/A'}

### Capas de análisis
{layers_text}
### Fusión
Señal compuesta: {fused.get('signal', 'WAIT')} (score: {fused.get('score', 50)}, confianza: {fused.get('confidence', 0)})

### Posiciones abiertas
{positions_text}

### Instrucción
Analiza los datos y responde SOLO con JSON sin markdown ni explicaciones extra:
{{
  "signal": "LONG" o "SHORT" o "WAIT",
  "confidence": 0-100,
  "entry_price": null (dejar que el sistema decida) o numero,
  "position_size_usd": numero_entre_10_y_200,
  "stop_loss_pct": numero_entre_1_y_10 (0 si WAIT),
  "take_profit_pct": numero_entre_1_y_20 (0 si WAIT),
  "reasoning": "razon en una linea"
}}"""

    def _call_deepseek(self, system_prompt: str, user_prompt: str) -> str:
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
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
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
