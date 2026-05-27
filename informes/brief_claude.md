# Brief: Renovación Total del Dashboard — MarketAI

## Para Claude (Agente de Diseño)

---

## Objetivo

Rediseño completo del dashboard web de MarketAI. Debe ser moderno, visualmente limpio, fácil de usar para personas sin conocimientos de trading, y responsive (funcionar en celular y escritorio).

---

## Stack técnico

| Componente | Tecnología |
|---|---|
| Backend | **Flask** (Python) — archivo `dashboard.py` |
| Frontend | **Vanilla JS** + **CSS** (sin frameworks ni librerías externas) |
| Gráficos | **SVG inline** para gráficos simples, **Plotly** para gráficos complejos (plotly ya está instalado pero no se usa actualmente) |
| Tema | **Oscuro**, 4 colores fijos (ver abajo) |

---

## Archivos que puedes modificar (SOLO estos)

| Archivo | Scope |
|---|---|
| `templates/*.html` | **Todos** los HTML del dashboard (estructura, layout, componentes) |
| `static/style.css` | CSS completo (tema, responsive, animaciones, componentes) |
| `dashboard.py` | Endpoints Flask y lógica de UI. **No tocar** imports de `engine/`, `analyzers/`, `execution/`, etc. Solo modificar rutas y helpers |

## Archivos que NO debes tocar (vitales para el sistema)

`orchestrator.py`, `engine/`, `execution/`, `analyzers/`, `data/`, `learning/`, `alerts/`, `config.yaml`, `.env`, `requirements.txt`, `tray_app.py`

---

## Paleta de colores (4 colores fijos)

| Color | Hex | Uso | Categoría |
|---|---|---|---|
| Fondo | `#0d1117` | Background principal y sidebar | BG oscuro |
| Cards | `#161b22` | Tarjetas, paneles, inputs | Superficies |
| Verde | `#00d4aa` | LONG, positivo, botón primario | Acertivo |
| Rojo | `#ff1744` | SHORT, negativo, pérdidas | Negativo |

**Colores secundarios (derivados):**
- Texto: `#e6edf3` (texto principal)
- Texto muted: `#8b949e` (textos secundarios)  
- Bordes: `#30363d` (separadores, bordes de cards)
- Azul info: `#2979ff` (WAIT, información, links)
- Hover: `#1c2333` (hover de filas y enlaces)

---

## Endpoints disponibles (no crear nuevos, no cambiar nombres)

### Datos principales
- `GET /api/summary` → `{normal: {...balance, pnl, win_rate, trades...}, fast: {...}, active: [...]}`
- `GET /api/positions` → lista de posiciones abiertas
- `GET /api/signals` → últimas señales generadas
- `GET /api/trades` → historial de trades
- `GET /api/portfolio/history` → time-series de balance para equity curve

### Métricas
- `GET /api/metrics/extended` → Sharpe, Profit Factor, Max DD, Avg Win/Loss
- `GET /api/metrics/funnel` → embudo de decisión (señales → ejecutadas)
- `GET /api/metrics/by-market` → breakdown por mercado

### Analytics
- `GET /api/analytics/confidence-distribution` → histograma de confianza
- `GET /api/analytics/layer-activity` → actividad por capa
- `GET /api/analytics/by-hour` → win rate por hora
- `GET /api/analytics/by-ticker` → rendimiento por ticker

### Sistema
- `GET /api/status` → `{running: true/false}`
- `GET /api/health` → `{deepseek: bool, polyscan: bool, yfinance: bool}`
- `GET /api/logs` → últimas 80 líneas del log
- `GET /api/news?market=all|forex|stocks|crypto&sentiment=all|bullish|bearish` → artículos
- `GET /api/risk-snapshot` → snapshot de riesgo actual
- `GET /api/backtest/run?market=forex|stocks` → ejecuta backtest, retorna resultados
- `GET /api/loop/start` → inicia loop
- `GET /api/loop/stop` → detiene loop
- `GET /api/config` → retorna config.yaml actual
- `POST /api/config` → guarda cambios a config.yaml

---

## Páginas existentes (9 páginas)

| Ruta | Archivo template | Contenido actual |
|---|---|---|
| `/` | `overview.html` | Métricas duales (Normal/Fast), equity curve SVG, estado APIs, funnel, proyección |
| `/signals` | `signals.html` | Tabla de señales con filtros (decisión, mercado), expansión de capas |
| `/trades` | `trades.html` | Historial con filtros (status, resultado, perfil), tarjetas resumen |
| `/analytics` | `analytics.html` | 4 gráficos SVG (confianza, capas, hora, ticker) |
| `/backtest` | `backtest.html` | Botones + tabla de resultados por ticker con métricas |
| `/config` | `config.html` | Acordeones editables (mercados, riesgo, deepseek, capas) |
| `/news` | `news.html` | Artículos con filtros y barra de mood |
| `/watchlist` | `watchlist.html` | Precios en vivo de tickers configurados |
| `/logs` | `logs.html` | Tail del log con auto-refresh |

---

## Requerimientos de diseño

### Funcionales (mantener todo lo que ya funciona)

- [ ] Los filtros en Señales y Trades deben seguir funcionando igual
- [ ] Los botones de inicio/detención del loop deben estar visibles y funcionales
- [ ] Todas las cards, tablas y gráficos deben actualizarse con los mismos endpoints
- [ ] El equity curve en Overview debe seguir mostrando la línea de balance
- [ ] Los acordeones en Config deben seguir expandiendo/colapsando
- [ ] La página de Noticias debe mantener los filtros por mercado y sentimiento
- [ ] El Backtest debe seguir ejecutándose y mostrando resultados

### Visuales (nuevo diseño)

- [ ] **Tarjetas con bordes sutiles** y sombras suaves
- [ ] **Gradientes** en los gráficos (debajo de la línea de equity)
- [ ] **Animaciones suaves** en transiciones y carga de datos (CSS transitions)
- [ ] **Tipografía**: `system-ui` o `Segoe UI`, jerarquía clara (tamaños 11px → 24px)
- [ ] **Íconos**: emoji o SVG inline (sin librerías de iconos)
- [ ] **Espaciado generoso**: padding de 16-24px en cards, separación clara entre secciones
- [ ] **Responsive**: adaptable a mobile (sidebar → hamburger drawer)
- [ ] **Modo oscuro coherenter**: todos los elementos deben tener fondo y borde definidos
- [ ] **Hover state** en toda fila/clickeable (cambio sutil de fondo)

### UX

- [ ] Estados vacíos con mensaje amigable (no solo "Sin datos")
- [ ] Loading spinners mientras cargan datos
- [ ] Tooltips en métricas importantes (ej: "Sharpe: qué tan rentable es el riesgo que tomás")
- [ ] La página Overview debe ser la más impactante: el usuario debe entender en 3 segundos si está ganando o perdiendo

---

## Flujo de trabajo para Claude

1. **Leer** los archivos actuales en `templates/`, `static/`, `dashboard.py`, `informes/reglas.md`
2. **Proponer** cambios en `informes/news.txt` antes de implementar
3. **Implementar** cambios solo en los archivos de diseño
4. **Reportar** bugs encontrados en archivos vitales (sin modificarlos) como "propuesto" en `informes/news.txt`
5. **Verificar** que no haya duplicados de `const`/`let`/`function` después de editar

---

## Prohibido

- ❌ No agregar nuevas dependencias a `requirements.txt`
- ❌ No tocar `orchestrator.py`, `engine/`, `execution/`, `analyzers/`, `data/`, `learning/`, `alerts/`
- ❌ No cambiar nombres de endpoints ni sus respuestas
- ❌ No modificar `.env`, `config.yaml`, `.gitignore`
- ❌ No borrar archivos de templates sin preguntar antes

---

*Documento generado para Claude. MarketAI — 2026.*
