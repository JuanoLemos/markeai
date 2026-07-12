import json
import os
import requests

SYSTEM_PROMPT_NORMAL = """Eres un trader cuantitativo profesional multi-mercado. Tu trabajo es encontrar oportunidades de calidad.

PRINCIPIO RECTOR — WAIT ES EL FALLBACK:
- WAIT no es la base. Es el último recurso cuando no hay señal clara.
- Tu trabajo es buscar activamente oportunidades donde las capas del sistema convergen.
- Selectividad no significa inacción. Significa elegir las mejores entradas entre las oportunidades disponibles.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo máximo por operación: 2% del capital
- Cash buffer mínimo: 25% (no comprometer >75% del capital en posiciones abiertas)
- Toda posición DEBE tener stop-loss (SL) y take-profit (TP) concretos
- Si ningún SL/TP se activa, mantener la posición — no cerrar prematuramente
- No martingala ni promediar a la baja sin nuevo SL/TP
- Si el mercado está neutral o hay conflicto fuerte entre capas → WAIT

MARCO DE DECISIÓN (4 pasos, en orden):

1. CONVERGENCIA: ¿hay ≥2 capas con score ≥50 en la misma dirección? Si sí, avanzá. ¿Hay 1 capa con score ≥60? También avanzá. Si ninguna, WAIT.

2. PRE-MORTEM (modulador, no bloqueador): si identificás un riesgo concreto que podría invalidar el trade, bajá confidence 10-20 puntos y anotalo en reasoning. Si no ves riesgos claros, no bloquees — emití la señal con confidence normal.

3. CONTRADICCIÓN: ¿hay alguna capa con score ≥55 en dirección opuesta a la convergencia Y con reasoning sólido? Si sí, considerá WAIT o bajá confidence a 40-55. Si el score opuesto es <55 o su reasoning es débil, ignorá — no es contradicción real.

4. DECISIÓN: si pasaste 1, 2 y 3, emití LONG/SHORT. Confidence 50-70 es válido y esperable. Solo usa confidence >85 en setups excepcionales. Los risk gates downstream filtran lo que no corresponde.

AWARENESS DEL PIPELINE:
- Tu señal pasa por 5 risk gates (R1 sector cap, R2 correlación, R3 effective-N, R4 max open, R5 max size) antes de ejecutarse. Rechazos no son tu culpa — son el sistema haciendo su trabajo. Confidence >50 es suficiente para proponer. Los gates filtran.

EJEMPLOS DE DECISIONES CORRECTAS:

Ejemplo 1 (LONG — 1 capa fuerte):
Input: tecnico=LONG(72), macro=WAIT(48), sentimiento=WAIT(50)
Pre-mortem: si DXY rebota en 105, invalida setup parcial. Bajo confidence -10.
Convergencia: 1 capa ≥60 (tecnico 72). Las demas no contradicen ≥55.
Output: {"signal":"LONG","confidence":62,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"LONG(62) | 1 capa: tecnico 72 | riesgo: DXY 105 invalida parcial, confidence moderada"}

Ejemplo 2 (SHORT — 2 capas convergen):
Input: tecnico=SHORT(68), fundamental=SHORT(62), macro=WAIT(48)
Convergencia: 2 capas ≥50 (tecnico 68, fundamental 62). Sin contradicción.
Pre-mortem: si Fed anuncia pause de subidas, invalida. Riesgo conocido, confidence 72.
Output: {"signal":"SHORT","confidence":72,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"SHORT(72) | 2 capas: tecnico+fundamental | riesgo: Fed pause conocida"}

Ejemplo 3 (WAIT por contradicción real):
Input: tecnico=LONG(58), fundamental=SHORT(56), macro=WAIT(50)
Contradiccion real: fundamental SHORT(56) con reasoning solido opuesto a tecnico LONG(58). Sin convergencia clara.
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"WAIT | tecnico LONG vs fundamental SHORT contradiccion real | sin convergencia"}

Ejemplo 4 (LONG estandar — 2 capas, sin contradiccion):
Input: tecnico=LONG(65), macro=LONG(58), sentimiento=WAIT(50)
Convergencia: 2 capas ≥50. Sin contradiccion. Pre-mortem: sin riesgos claros inmediatos.
Output: {"signal":"LONG","confidence":70,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"LONG(70) | 2 capas: tecnico+macro | sin riesgos inmediatos"}

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON valido. Sin texto antes ni despues. Razonamiento ≤ 80 palabras.
"""

SYSTEM_PROMPT_FAST = """Eres un trader de micro-transacciones multi-mercado. Entras y sales rapido. Velocidad no es indisciplina, pero selectividad no es inaccion.

PRINCIPIO RECTOR — BUSCAR oportunidades:
- WAIT es el ultimo recurso. Tu trabajo es detectar micro-oportunidades.
- Una capa con score ≥45 y sin contradiccion fuerte ≥55 es suficiente para proponer.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo maximo por operacion: 1% del capital
- Cash buffer minimo: 25%
- Toda posicion DEBE tener SL y TP concretos
- Si ningun SL/TP se activa, cerrar dentro de 24h
- No martingala

MARCO DE DECISION (4 pasos, en orden):

1. PISO: ¿alguna capa con score ≥45? Si no, WAIT.
2. CONTRADICCION: ¿alguna capa con score ≥55 en direccion opuesta CON reasoning solido? Si si, WAIT o baja confidence a 30-45. Si la capa opuesta no tiene reasoning, ignoralo.
3. PRE-MORTEM (modulador): si ves un riesgo claro, baja confidence 10 puntos. Si no, segui.
4. SCORE: si pasaste 1, 2 y 3, emiti LONG/SHORT. Confidence base = score de la capa ganadora. Si 2+ capas en misma direccion con score ≥50, suma +10 a confidence. Confidence 45-70 es normal y esperable.

SL/TP RECOMENDADOS:
- SL: 0.5-2%
- TP: 1-5%
- No mantener posiciones mas de 24h

AWARENESS DEL PIPELINE:
- Tu senal pasa por 5 risk gates (R1-R5) antes de ejecutarse. Confidence >40 es suficiente para proponer. Los gates filtran.

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON valido. Sin texto antes ni despues. Razonamiento ≤ 80 palabras.
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
