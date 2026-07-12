# Brief para @trade: Revisión del AI prompt de MarketAI

**De:** Mavis (Mavis-acá)
**Para:** @trade
**Fecha:** 2026-07-11
**Tema:** Mejorar el prompt del DeepSeek en `engine/decider.py` incorporando mejores prácticas de los 4 repos públicos.

---

## Contexto

MarketAI es un bot de trading paper-mode que corre en Windows. El loop principal:
1. Recolecta datos (forex, stocks, polymarket) — capas: técnico, fundamental, macro, sentiment, etc.
2. Fusiona capas en una señal compuesta con score/confidence.
3. Llama a DeepSeek (`engine/decider.py`) con un system prompt + user prompt que arma la decisión final.
4. Pasa por 5 risk gates (R1-R5) recién implementados.
5. Ejecuta via paper broker (slippage, trailing, partial TP).

Hay 2 perfiles: **NORMAL** (conservador, $1000 seed) y **FAST** (micro-transacciones, $1000 seed).

## Estado del roadmap

- **R80** "Informe repos trading" (duplicado en roadmap, una ✅ y una ⏳ — sugiere que nunca se cerró bien)
- **R85** 🔴 "Risk code-enforced estilo swarm-trader" — relacionado
- **R86** 🔴 "Time-exit estilo Freqtrade" — relacionado
- **R87** 🔴 "Single Portfolio Manager bottleneck estilo swarm-trader" — relacionado
- **R88** 🔴 "Walk-forward ML4T pattern" — relacionado

---

## Texto actual del prompt (esto es lo que tiene que mejorar)

### `SYSTEM_PROMPT_NORMAL` (engine/decider.py línea 5-31)

```
Eres un trader cuantitativo profesional multi-mercado.

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
```

### `SYSTEM_PROMPT_FAST` (engine/decider.py línea 33-53)

```
Eres un trader de micro-transacciones multi-mercado. Entras y sales rapido, operas con senales tempranas.

REGLAS DE RIESGO (obligatorias):
- Riesgo maximo por operacion: 1% del capital
- Cash buffer minimo: 30%
- Toda posicion DEBE tener SL y TP concretos
- Si ningun SL/TP se activa, cerrar dentro de 24h
- No martingala

MARCO DE DECISION:
1. Analiza cada capa disponible
2. ≥1 capa con score >45 → LONG/SHORT (no esperes convergencia de 2 capas)
3. Si capas se contradicen (una LONG, otra SHORT) → elegir la de mayor score
4. Solo WAIT si TODAS las capas son WAIT
5. Preferir senales con score cerca de 55+ (mas confianza)

SL/TP RECOMENDADOS:
- SL: 0.5-1%
- TP: 1-3%
- No mantener posiciones mas de 24h
```

---

## Constraints duros (no negociar)

1. **JSON output obligatorio** con estos campos exactos (lo parsea `_parse_response` en línea 153-161):
   - `signal`: "LONG" | "SHORT" | "WAIT"
   - `confidence`: 0-100
   - `entry_price`: null o número
   - `position_size_usd`: número 10-200
   - `stop_loss_pct`: 0-10
   - `take_profit_pct`: 0-20
   - `reasoning`: string de 1 línea
2. **NO cambiar** los risk parameters (2%/1%, 30% cash buffer, SL/TP min/max) — están en producción.
3. **NO romper** el fallback WAIT — `_parse_response` ya devuelve WAIT en caso de error, eso se mantiene.
4. **Idiomas**: español OK (consistente con la UI y el usuario), pero los campos JSON en inglés.
5. **Latencia objetivo**: el usuario ya testeó que el LLM directo es 5-10s, demasiado lento para uso en mesa real. Si podés agregar instrucción de "respuesta concisa, sin razonamiento largo", hacelo. Pero no cambies max_tokens (eso es config).
6. **Compatibilidad**: DeepSeek v4-flash, temperature 0.3, max_tokens 500.
7. **Modelo compatible**: el prompt se manda a DeepSeek. Evitar instrucciones que asuman features de GPT-4 (ej. function calling nativo).

## Scope guardrail

- **Máximo 5-6 cambios** en el prompt, no 20. El usuario quiere saber QUÉ movió la aguja.
- Si un patrón del repo requiere un cambio grande de infra (ej. multi-agente debate), mencionalo como **futuro item**, no lo incluyas en v2.
- Priorizá los cambios que tocan: anti-overtrading, self-criticism, ejemplos, latencia.

## Lo que NO quiero

- No toques código todavía. Solo texto de prompt + plan de A/B.
- No propongas cambios que rompan la compatibilidad con el JSON parser.
- No uses los nombres de archivos reales (no "v2") — el versionado lo manejamos en git.
- No inventes referencias a los repos públicos si no estás seguro — citá el archivo/función concreto si podés.

## Formato de salida

Escribí tu respuesta en **3 archivos markdown** en tu workspace:
- `ai-prompt-review/01-inventario.md` (tabla comparativa)
- `ai-prompt-review/02-draft-v2.md` (texto de los 2 prompts nuevos + diff conceptual)
- `ai-prompt-review/03-plan-ab-test.md` (plan de medición)

Después mandame un report-back corto con los paths y un TL;DR de 3-4 líneas.

Si tenés alguna duda sobre el proyecto antes de empezar, preguntame antes de escribir. Si no, dale para adelante.

---
*Fin del brief. Esperando tu entrega.*
