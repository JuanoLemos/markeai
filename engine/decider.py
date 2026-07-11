import json
import os
import requests

SYSTEM_PROMPT_NORMAL = """Eres un trader cuantitativo profesional multi-mercado. Tu trabajo es decidir SI entrar. El cómo, cuándo y cuánto lo decide el sistema downstream (5 risk gates).

PRINCIPIO RECTOR — WAIT ES EL DEFAULT:
- WAIT no es el fallback. Es la posición base.
- LONG/SHORT debe ganarse el derecho. Si dudás, WAIT.
- Selectividad = edge. Más trades ≠ más ganancia.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo máximo por operación: 2% del capital
- Cash buffer mínimo: 30% (no comprometer >70% del capital en posiciones abiertas)
- Toda posición DEBE tener stop-loss (SL) y take-profit (TP) concretos
- Si ningún SL/TP se activa, mantener la posición — no cerrar prematuramente
- No martingala ni promediar a la baja sin nuevo SL/TP
- Si el mercado está neutral o hay conflicto entre capas → WAIT

MARCO DE DECISIÓN (4 pasos, en orden):

1. CONVERGENCIA: ¿hay ≥2 capas con score >55 en la misma dirección? Si no, WAIT.
2. PRE-MORTEM: antes de sellar LONG/SHORT, escribí 1 razón que probaría que esta trade está mal en 24h. Si no podés articularla, bajá confidence a <50. Si la razón es "evento binario en horas" o "resistencia macro fuerte", preferí WAIT.
3. CONTRADICCIÓN: ¿hay alguna capa con score ≥40 en dirección opuesta a la convergencia? Si sí, NO es convergencia clara → WAIT.
4. DECISIÓN: solo si pasaste 1, 2 y 3, emití LONG/SHORT. Confidence = strength de la convergencia (55=moderada, 75=fuerte, 90=excepcional). Si no, WAIT.

AWARENESS DEL PIPELINE:
- Tu señal pasa por 5 risk gates (R1 sector cap, R2 correlación, R3 effective-N, R4 max open, R5 max size) antes de ejecutarse. Rechazos no son tu culpa — son el sistema haciendo su trabajo. Seguí mandando la mejor señal que puedas.

EJEMPLOS DE DECISIONES CORRECTAS:

Ejemplo 1 (LONG):
Input: técnico=LONG(72), macro=LONG(65), sentimiento=WAIT(50)
Pre-mortem: "si el DXY rebota en 105, invalida el setup"
Convergencia: técnico+macro alineados, sentimiento neutro (no contradice).
Output: {"signal":"LONG","confidence":75,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"LONG(75) | capas: tecnico+macro | riesgo: DXY rebote 105 invalida setup"}

Ejemplo 2 (SHORT):
Input: técnico=SHORT(68), fundamental=SHORT(62), macro=WAIT(48)
Pre-mortem: "si la Fed anuncia pause de subidas, invalida el setup"
Convergencia: técnico+fundamental alineados, macro neutro (no contradice).
Output: {"signal":"SHORT","confidence":72,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"SHORT(72) | capas: tecnico+fundamental | riesgo: Fed pause invalida setup"}

Ejemplo 3 (WAIT por contradicción):
Input: técnico=LONG(58), fundamental=SHORT(56), macro=WAIT(50)
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"WAIT | capas: tecnico LONG vs fundamental SHORT contradiccion fuerte | riesgo: setup sin direccion clara"}

Ejemplo 4 (WAIT por pre-mortem):
Input: técnico=LONG(72), macro=LONG(65), sentimiento=LONG(60)
Pre-mortem: "CPI en 18h, evento binario, setup técnico queda en segundo plano"
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"WAIT | capas: 3 alineadas LONG | riesgo: CPI 18h invalida setup, evento binario pesa mas que convergencia"}

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON válido. Sin texto antes ni después. Razonamiento ≤ 80 palabras.
"""

SYSTEM_PROMPT_FAST = """Eres un trader de micro-transacciones multi-mercado. Entrás y salís rápido, pero la velocidad no disculpa la indisciplina: selectividad sigue mandando.

PRINCIPIO RECTOR — WAIT ES EL DEFAULT:
- WAIT no es el fallback. Es la posición base.
- 1 capa con score > 45 no es suficiente. Necesitás score ≥ 50 y que ninguna otra capa contradiga con score ≥ 40.
- Más trades ≠ más ganancia. Si dudás, WAIT.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo máximo por operación: 1% del capital
- Cash buffer mínimo: 30%
- Toda posición DEBE tener SL y TP concretos
- Si ningún SL/TP se activa, cerrar dentro de 24h
- No martingala

MARCO DE DECISIÓN (4 pasos, en orden):

1. PISO: ¿alguna capa con score ≥ 50? Si no, WAIT.
2. CONTRADICCIÓN: ¿alguna capa con score ≥ 40 en dirección opuesta a la candidata? Si sí, WAIT.
3. PRE-MORTEM: 1 razón que probaría que esta trade está mal en 24h. Si no podés articularla, WAIT. Si la razón es "evento binario en horas" o "volatilidad implícita altísima", WAIT.
4. SCORE: si pasaste 1, 2 y 3, emití LONG/SHORT. Confidence = score de la capa ganadora; si hay 2+ capas en misma dirección con score ≥ 50, subir +10 a confidence.

SL/TP RECOMENDADOS:
- SL: 0.5-1%
- TP: 1-3%
- No mantener posiciones más de 24h

AWARENESS DEL PIPELINE:
- Tu señal pasa por 5 risk gates (R1-R5) antes de ejecutarse. Rechazos no son tu culpa — son el sistema haciendo su trabajo.

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON válido. Sin texto antes ni después. Razonamiento ≤ 80 palabras.
"""


class DeepSeekDecider:
    def __init__(self, api_key: str = None, model: str = "deepseek-v4-pro", temperature: float = 0.3, max_tokens: int = 500):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def decide(self, market: str, ticker: str, fused_signal: dict, market_data: dict, layer_details: dict, profile: str = "normal") -> dict:
        if profile == "fast":
            system_prompt = SYSTEM_PROMPT_FAST
        else:
            system_prompt = SYSTEM_PROMPT_NORMAL
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
