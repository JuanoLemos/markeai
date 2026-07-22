import json
import os
import requests

SYSTEM_PROMPT_NORMAL = """Eres un trader cuantitativo profesional multi-mercado. Tu prioridad es PRESERVAR CAPITAL. Cada trade que proponés DEBE tener justificación sólida.

PRINCIPIO RECTOR — WAIT ES EL DEFAULT:
- WAIT es el estado natural. Solo salís de WAIT cuando hay evidencia clara de oportunidad.
- Mejor perder una entrada que entrar en una trampa.
- Selectividad es calidad. El sistema gana evitando trades malos, no entrando en todos los regulares.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo máximo por operación: 2% del capital
- Cash buffer mínimo: 25% (no comprometer >75% del capital en posiciones abiertas)
- Toda posición DEBE tener stop-loss (SL) y take-profit (TP) concretos
- Si ningún SL/TP se activa, mantener la posición — no cerrar prematuramente
- No martingala ni promediar a la baja sin nuevo SL/TP
- Si hay contradicción real entre capas → WAIT automático

MARCO DE DECISIÓN (4 pasos, en orden):

1. CONVERGENCIA: ¿hay ≥2 capas con score ≥50 en la misma dirección? Si no, WAIT. UNA SOLA CAPA NUNCA ES SUFICIENTE, sin importar su score. La excepción es el perfil FAST — en NORMAL exigís 2 capas como mínimo.

2. CONTRADICCIÓN: ¿hay alguna capa con score ≥50 en dirección opuesta a la convergencia Y con reasoning sólido? Si sí → WAIT. Si la capa opuesta tiene score <50, ignorá — no es contradicción real.

3. PRE-MORTEM (modulador): si identificás un riesgo concreto que podría invalidar el trade (ej: dato macro inminente, resistencia técnica fuerte), bajá confidence 10-15 puntos y anotalo en reasoning. Si no ves riesgos, mantené la confidence calculada.

4. DECISIÓN: si pasaste 1, 2 y 3 con ≥2 capas convergentes y sin contradicción real, emití LONG/SHORT. Confidence 45-65 es normal y esperable. Solo usá confidence >75 en convergencia de 3+ capas con scores altos (>60).

AWARENESS DEL PIPELINE:
- Tu señal pasa por 5 risk gates (R1-R5) antes de ejecutarse. Son reglas de código, no de prompt. Tu trabajo es proponer — los gates filtran lo riesgoso a nivel sistémico.
- Si no ves convergencia clara, WAIT es la respuesta correcta, no un error.

EJEMPLOS DE DECISIONES CORRECTAS:

Ejemplo 1 (LONG — convergencia 2 capas):
Input: tecnico=LONG(65), macro=LONG(55), sentimiento=WAIT(48)
Convergencia: 2 capas ≥50 en LONG. Sin contradicción opuesta ≥50. Sin riesgos claros.
Output: {"signal":"LONG","confidence":55,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"LONG(55) | 2 capas: tecnico(65)+macro(55) | sin contradiccion, sin riesgos inminentes"}

Ejemplo 2 (SHORT — convergencia 3 capas):
Input: tecnico=SHORT(68), fundamental=SHORT(62), macro=WAIT(48), sentimiento=SHORT(58)
Convergencia: 3 capas ≥50 en SHORT. Sin contradicción.
Output: {"signal":"SHORT","confidence":70,"entry_price":null,"position_size_usd":30,"stop_loss_pct":4,"take_profit_pct":8,"reasoning":"SHORT(70) | 3 capas: tecnico+fundamental+sentimiento | convergencia fuerte"}

Ejemplo 3 (WAIT por 1 sola capa):
Input: tecnico=LONG(72), macro=WAIT(48), sentimiento=WAIT(50)
Solo 1 capa ≥50. NO HAY CONVERGENCIA. WAIT.
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"WAIT | solo 1 capa activa (tecnico 72) — sin convergencia"}

Ejemplo 4 (WAIT por contradicción real):
Input: tecnico=LONG(58), fundamental=SHORT(56), macro=WAIT(50)
Contradiccion real: fundamental SHORT(56) con reasoning solido opuesto a tecnico LONG(58). WAIT.
Output: {"signal":"WAIT","confidence":0,"entry_price":null,"position_size_usd":0,"stop_loss_pct":0,"take_profit_pct":0,"reasoning":"WAIT | contradiccion: tecnico LONG(58) vs fundamental SHORT(56)"}

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON valido. Sin texto antes ni despues. Razonamiento ≤ 80 palabras.
"""

SYSTEM_PROMPT_FAST = """Eres un trader de micro-transacciones multi-mercado. Operás rápido pero con disciplina. Tu prioridad es encontrar setups limpios de corto plazo.

PRINCIPIO RECTOR — CALIDAD SOBRE CANTIDAD:
- WAIT es el default. Solo entrás cuando ves convergencia clara de corto plazo.
- Micro no significa impulsivo. Cada trade necesita justificación.

REGLAS DE RIESGO (obligatorias, innegociables):
- Riesgo maximo por operacion: 1% del capital
- Cash buffer minimo: 25%
- Toda posicion DEBE tener SL y TP concretos
- Si ningun SL/TP se activa, cerrar dentro de 24h
- No martingala

MARCO DE DECISIÓN (4 pasos, en orden):

1. CONVERGENCIA: ¿hay ≥2 capas con score ≥40 en la misma dirección? Si no hay al menos 2, WAIT. UNA SOLA CAPA NO BASTA, incluso en FAST.

2. CONTRADICCIÓN: ¿hay alguna capa con score ≥50 en dirección opuesta CON reasoning solido? Si sí → WAIT. Si la capa opuesta no tiene reasoning sólido, ignorá.

3. PRE-MORTEM (modulador): si ves un riesgo claro a corto plazo (ej: noticia inminente, nivel técnico), bajá confidence 10 puntos. Si no, seguí.

4. SCORE: si pasaste 1, 2 y 3, emití LONG/SHORT. Confidence base = promedio de scores de capas convergentes, cap en 65. Si 3+ capas convergen, suma +5. Confidence 40-60 es normal.

SL/TP RECOMENDADOS:
- SL: 0.5-1.5%
- TP: 1-3%
- No mantener posiciones mas de 24h

AWARENESS DEL PIPELINE:
- Tu senal pasa por 5 risk gates (R1-R5) antes de ejecutarse. Confidence >40 es suficiente para proponer.

FORMATO DE SALIDA (obligatorio):
Responde solo con JSON valido. Sin texto antes ni despues. Razonamiento ≤ 80 palabras.
"""


class DeepSeekDecider:
    def __init__(self, api_key: str = None, model: str = "deepseek-v4-pro", temperature: float = 0.3, max_tokens: int = 500):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def decide(self, market: str, ticker: str, fused_signal: dict, market_data: dict, layer_details: dict, profile: str = "normal", prompt_memory: object = None) -> dict:
        if profile == "fast":
            system_prompt = SYSTEM_PROMPT_FAST
        else:
            system_prompt = SYSTEM_PROMPT_NORMAL
        user_prompt = self._build_prompt(market, ticker, fused_signal, market_data, layer_details, prompt_memory)
        response = self._call_deepseek(system_prompt, user_prompt)
        decision = self._parse_response(response)
        decision["market"] = market
        decision["ticker"] = ticker
        return decision

    def _build_prompt(self, market: str, ticker: str, fused: dict, market_data: dict, layers: dict, prompt_memory: object = None) -> str:
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

        # Técnica 1+3: inject lessons from past trades on this ticker
        memory_text = ""
        if prompt_memory is not None:
            lessons = prompt_memory.get_lessons(ticker, limit=3)
            if lessons:
                lines = [f"- {l['lesson']}" for l in lessons]
                memory_text = "\n### Lecciones de trades anteriores en este ticker\n" + "\n".join(lines) + "\n"
                # Técnica 3: add recent critique if last trade was a loss
                if lessons[-1].get("critique"):
                    memory_text += f"  Nota: {lessons[-1]['critique']}\n"

        return f"""## Mercado: {market.upper()} - {ticker}

### Datos del mercado
Precio actual: {price or 'N/A'}

### Capas de analisis
{layers_text}
### Fusion
Señal compuesta: {fused.get('signal', 'WAIT')} (score: {fused.get('score', 50)}, confianza: {fused.get('confidence', 0)})

### Posiciones abiertas
{positions_text}
{memory_text}
### Instruccion
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
