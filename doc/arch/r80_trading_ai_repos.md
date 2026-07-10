# R80 — Investigación repos trading AI/market en GitHub

**Fecha:** 2026-07-10
**Búsqueda:** Web search GitHub + reviews externos (2026 H1)
**Objetivo:** Identificar técnicas de la comunidad que podamos adoptar o que destaquen dónde MarketAI ya está bien.

---

## Repos top del momento (mid-2026)

| Repo | Stars | Idea central | LLM |
|------|-------|--------------|-----|
| [TauricResearch/TradingAgents](https://github.com/tauricresearch/tradingagents) | ~82k | Multi-agente con debate estructurado (7 roles: fundamental, sentiment, technical, trader, risk manager, portfolio manager, fund manager). Pipeline LangGraph. Persistent decision log. | GPT-5, Claude, DeepSeek, Qwen, GLM, Ollama |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | ~49k | 14 agentes modelados como inversores legendarios (Buffett, Munger, Burry, etc.) que debaten. LangChain. | OpenAI, Anthropic, Groq, DeepSeek |
| [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) | ~17k | Plataforma agent-native con capa social. Agentes publican señales; otros copian. | Multi-LLM |
| [benstaf/FinRL_DeepSeek](https://github.com/benstaf/FinRL_DeepSeek) | activo | LLM + reinforcement learning, FNSPID 15.7M artículos (1999-2023) | DeepSeek V3, Qwen 2.5, Llama 3.3 |
| [Mattbusel/FinRL_DeepSeek_Crypto](https://github.com/Mattbusel/FinRL_DeepSeek_Crypto) | activo | LARSA — regime-switching (bull/bear/sideways/volatile), ensemble DQN, DeepSeek sentiment | DeepSeek V3 |
| [alex-jb/orallexa-ai-trading-agent](https://github.com/alex-jb/orallexa-ai-trading-agent) | activo | 8-source signal fusion, 10 ML models, Bull/Bear/Judge debate en Claude Opus, 20-agent swarm reaction simulator, Polymarket+Kalshi votes | Claude Opus 4.7 |

**Patrones comunes que se repiten (lo que la comunidad considera "tabla"):**
1. **Multi-agente con debate** (no sólo "agentes que analizan en paralelo") — el debate entre bull/bear/riesgo/PM es lo que diferencia a los frameworks buenos de los toy.
2. **Persistent decision log** — guardar cada razonamiento paso a paso, no sólo el trade final. Auditable y repetible.
3. **Multi-LLM / fallback LLM** — un LLM primario (DeepSeek) + fallback a otros (Qwen, Claude, GPT).
4. **Regime detection** — clasificar el mercado en bull/bear/sideways/volatile y adaptar la estrategia.
5. **Conectores Polymarket/Kalshi** — unificados.
6. **RL + LLM** — finetunear decisiones con reinforcement learning sobre signals de LLM.
7. **Test con backtest date-fidelity** — backtest en fecha histórica, no sólo random walk.

---

## Comparación con MarketAI

| Capacidad | TradingAgents/ai-hedge-fund | MarketAI (post-Ola 1) | Gap |
|-----------|------------------------------|----------------------|-----|
| 9 analizadores en pipeline | Sí (5-7) | **Sí (9)** | ✅ mejor |
| Dual profile (Normal+Fast) | No típicamente | **Sí** | ✅ ventaja |
| DeepSeek como motor | Sí | **Sí (v4 pro + flash)** | ✅ paridad |
| Multi-LLM con fallback | Sí (varios) | No | ⚠️ adoptar |
| Debate multi-agente | **Sí (núcleo)** | No (1 prompt por decider) | ❌ gap grande |
| Persistent decision log | Sí (auditable) | Parcial (trade_journal.md) | ⚠️ adoptar completo |
| Regime detection | Sí (LARSA) | Parcial (ADX = trend, no regime) | ⚠️ adoptar |
| Backtest con date fidelity | Sí | Parcial (replay lineal) | ⚠️ mejorar |
| Polymarket integration | Sí | **Sí** | ✅ paridad |
| RL/finetuning | Sí (FinRL) | No | ❌ out of scope ahora |
| Risk manager dedicado | **Sí (separado)** | Sí (risk_engine.py) | ✅ paridad |
| Portfolio manager (jerarquía) | **Sí (jerarquía)** | No (perfiles paralelos) | ⚠️ opcional |

---

## Lo que vale la pena evaluar (post-Ola 1)

### Alta prioridad — alineado con la visión
1. **Persistent decision log en DB** — agregar tabla `decision_log` con todos los layers + decisión DeepSeek + reasoning completo. Reusable para auditoría, training futuro, debugging.
2. **Multi-LLM fallback en decider.py** — si DeepSeek falla o da JSON inválido, intentar con backup. Trade-off: costo vs resiliencia.
3. **Refinar ADX regime detection** — actualmente `ranging | trending | transition`. Ampliar a `bull | bear | sideways | volatile` con umbrales más ricos (price momentum + volatility + volume).

### Media prioridad
4. **Bull/Bear debate antes de DeepSeek** — pre-prompt con dos opiniones encontradas, después DeepSeek arbitra. Reduce señales débiles.
5. **Regime-based profile weights** — `weights_polymarket` etc. pueden cambiar según regime. Requiere refactor del fusion engine.

### Baja prioridad (out of scope ahora)
6. **RL sobre signals** — requiere infraestructura, meses de trabajo.
7. **Multi-market API unificada** (Kalshi + Polymarket + Limitless) — más conectores, no es core.

---

## Conclusión

MarketAI está en buen lugar arquitectónico. Las **ventajas claras** vs el estado del arte son: dual profile simultáneo, soporte CEDEARs .BA con conversión ARS, dashboard Flask con 6 temas, system tray. Las **deudas** son: debate multi-agente (no sólo análisis paralelo), persistent decision log completo, regime detection real, y multi-LLM fallback.

**Recomendación:** no pivotar el diseño. Ola 2 (paper 4 semanas) tiene prioridad. Después de Ola 2, evaluar la adopción del patrón "debate pre-decider" si las métricas no son buenas — el gap más impactante es ese.

---

## Fuentes

- https://github.com/tauricresearch/tradingagents
- https://github.com/virattt/ai-hedge-fund
- https://github.com/HKUDS/AI-Trader
- https://github.com/benstaf/FinRL_DeepSeek
- https://github.com/Mattbusel/FinRL_DeepSeek_Crypto
- https://github.com/alex-jb/orallexa-ai-trading-agent
- https://ultralab.tw/en/blog/ai-finance-github-projects-2026
- https://www.askglitch.com/blog/top-5-trending-ai-github-repos-may-2026
- https://dibi8.com/resources/ai-trading/tradingagents-llm-multi-agent-trading-framework-2026/
- https://arxiv.org/abs/2412.20138 (paper original TradingAgents, UCLA × MIT)
