# Guía de Trading — Conocimiento y Mejores Prácticas para MarketAI

## Referencia completa de fórmulas, estrategias, gestión de riesgo y filtros para trading automatizado.

---

## Índice

1. [Position Sizing (Tamaño de Posición)](#1-position-sizing)
2. [Exit Strategies (Estrategias de Salida)](#2-exit-strategies)
3. [Entry Filters & Market Regime](#3-entry-filters--market-regime)
4. [Risk Management Metrics](#4-risk-management-metrics)
5. [Complete Python RiskManager Class](#5-complete-python-riskmanager-class)
6. [Combined Filter Pipeline](#6-combined-filter-pipeline)
7. [Referencias y Fuentes](#7-referencias-y-fuentes)

---

## 1. Position Sizing

### Kelly Criterion (Kelly 1956)

**Fórmula para resultados binarios:**

```
f* = (bp - q) / b

  f* = fracción óptima del capital
  p  = probabilidad de ganar (win rate)
  q  = 1 - p (probabilidad de perder)
  b  = ratio win/loss (avg_win / avg_loss)
```

**Python:**

```python
def kelly_fraction(win_rate, avg_win, avg_loss):
    b = avg_win / avg_loss if avg_loss > 0 else 1
    q = 1 - win_rate
    kelly = (b * win_rate - q) / b if b > 0 else 0
    return max(0, kelly)
```

**Fórmula para retornos normales (simplificada):**

```
f* = mu / sigma^2

  mu    = media de retornos
  sigma = desviación estándar de retornos
```

### Fractional Kelly — La regla profesional

| Fracción | Crecimiento | Riesgo de ruina | Cuándo usarlo |
|---|---|---|---|
| 100% (full Kelly) | Máximo | 100% | Nunca en trading real |
| 50% (half Kelly) | Alto | 13.5% | Sistemas muy robustos |
| **25% (quarter Kelly)** | Moderado | 0.5% | **Recomendado para MarketAI** |
| 10% | Bajo | ~0% | Conservador, drawdown mínimo |

**Regla general:** Usar `kelly * 0.25`. Si el sistema tiene Sharpe < 1, reducir aún más.

### Optimal f (Ralph Vince 1990)

Optimización numérica sobre R-múltiplos (ganancia/pérdida como múltiplo del riesgo):

```python
from scipy.optimize import minimize_scalar

def optimal_f(trades_pnl, risk_per_trade=100):
    r_multiples = trades_pnl / risk_per_trade
    neg_r = -r_multiples

    def twr(f):
        # Terminal Wealth Relative
        return -np.prod(1 + f * r_multiples)  # negative for minimization
    
    result = minimize_scalar(twr, bounds=(0.01, 0.5), method='bounded')
    return result.x
```

**Diferencia con Kelly:** Optimal f maximiza la TWR (Terminal Wealth Relative) sobre datos históricos reales, no asume distribución normal.

### Fixed Fractional

```
position_size = (equity * risk_pct) / (entry_price - stop_price)
```

```python
def fixed_fractional_size(balance, risk_pct, entry, stop):
    risk_per_unit = abs(entry - stop) / entry
    raw_size = balance * risk_pct / risk_per_unit
    max_size = balance * 0.05  # 5% del balance máximo
    return min(raw_size, max_size)
```

**Parámetros recomendados:** risk_pct = 0.5% a 2% (1% es estándar profesional).

### Fixed Ratio (Ryan Jones)

```
delta = optimal_growth_target  # ej: $500
level_threshold = 1 + (profit / delta)
size = max(1, floor(level_threshold))
```

Progresión aritmética: cada vez que la cuenta gana X$, se aumenta 1 unidad.

### Risk of Ruin

**Fórmula simple (trades independientes):**

```
R = ((1 - win_rate) / (1 + win_rate)) ^ (account / risk_per_trade)
```

```python
def risk_of_ruin(balance, risk_per_trade, win_rate):
    if win_rate <= 0.5:
        return 1.0  # 100% de ruina si WR <= 50%
    ratio = (1 - win_rate) / (1 + win_rate)
    return ratio ** (balance / risk_per_trade)
```

**Fórmula con Kelly:** Si usás full Kelly y tenés 50% WR, la ruina es 100%. Si usás quarter Kelly, la ruina es ~0.5%.

### Drawdown-Based Sizing

```python
def drawdown_based_size(balance, peak_balance, base_risk, max_dd=0.15):
    current_dd = (peak_balance - balance) / peak_balance
    if current_dd > max_dd:
        return 0  # shutdown
    # Escala lineal: 0% en max_dd → 100% en 0% dd
    risk_factor = 1 - (current_dd / max_dd)
    return balance * base_risk * risk_factor
```

### Referencias Position Sizing

| Fuente | Autor | Año |
|---|---|---|
| *The Kelly Criterion in Blackjack, Sports Betting and the Stock Market* | E.O. Thorp | 2008 |
| *The Mathematics of Money Management* | R. Vince | 1992 |
| *Portfolio Management Formulas* | R. Vince | 1990 |
| *Definitive Guide to Position Sizing* | Van Tharp | 2008 |
| *The Trading Game* | R. Jones | 1999 |

---

## 2. Exit Strategies

### Trailing Stop por ATR

```
trailing_stop = max(entry_price:current_high) - ATR * multiplier
```

```python
def atr_trailing_stop(high, atr_values, multiplier=3.0):
    running_high = np.maximum.accumulate(high)  # desde entry
    return running_high - atr_values * multiplier
```

**Parámetros:** multiplier = 2.0-3.0 (más bajo = más tight, más stops falsos).

### Chandelier Exit (LeBeau 1992)

```
chandelier_long = highest_high(period) - ATR * multiplier
chandelier_short = lowest_low(period) + ATR * multiplier
```

Usa rolling highest/lowest en vez de "desde entry" como trailing stop. **Más robusto en mercados laterales.**

### Parabolic SAR (Wilder 1978)

```
SAR = prior_SAR + AF * (EP - prior_SAR)
EP = highest high (long) or lowest low (short) since entry
AF = 0.02 initial, incrementa 0.02 cada nuevo extremo, max 0.20
```

**Recomendado para:** Tendencias fuertes (ADX > 25). **No usar en** mercados laterales.

### Partial Take-Profit (Escalonado)

```
Escenario: TP1 a 1.5% (50% del tamaño), TP2 a 3% (50% restante)

Ejemplo: Si posición abre 100 unidades:
  - TP1 alcanzado: cerrar 50 unidades, deja SL en break-even
  - TP2 alcanzado: cerrar 50 restantes
```

**Regla:** La primera salida debe cubrir comisiones y dejar SL en break-even.

### Break-Even Stop

Cuando el precio se mueve X% a favor, mover SL al precio de entrada:

```
if abs(current_price - entry_price) / entry_price >= break_even_trigger:
    stop_loss_price = entry_price
```

**Trigger recomendado:** 1-2× ATR a favor, o cuando el precio supera entry + ATR.

### Time-Based Exit

```
max_age: depender del mercado:
  Forex: 96h (4 días) → 168h (7 días) si está en profit
  Stocks: 72h (3 días) → 120h (5 días) si está en profit
  Polymarket: 336h (14 días) → 504h (21 días) si está en profit
```

Precio estancado (<0.5% de movimiento) → cerrar en la mitad del tiempo.

### Estrategia de Salida Recomendada para MarketAI

```
1. ATR Trailing Stop (multiplicador = 2.5)
2. Partial TP: 50% en 2× ATR, 50% en 4× ATR (para Normal)
3. Break-even cuando precio se mueve 1× ATR a favor
4. Time exit condicional (por mercado + profit/loss/stagnant)
```

### Referencias Exit Strategies

| Fuente | Autor | Año |
|---|---|---|
| *New Concepts in Technical Trading Systems* | J.W. Wilder | 1978 |
| *Technical Analysis of Stock Trends* | Edwards & Magee | 1948 |
| *The Ultimate Trading Guide* | J. Hill et al. | 2000 |
| *Chandelier Exit* | C. LeBeau | 1992 |
| *Trading Systems and Methods* | P. Kaufman | 2013 |
| *Following the Trend* | A. Clenow | 2012 |

---

## 3. Entry Filters & Market Regime

### ADX — Market Regime Detection (Wilder 1978)

```
ADX > 25 = Trending (seguir tendencia)
ADX < 20 = Ranging (mean reversion)
ADX 20-25 = Transition (esperar)
```

```python
def market_regime(df, period=14):
    high, low, close = df['high'], df['low'], df['close']
    up = high - high.shift(1)
    down = low.shift(1) - low
    pos_dm = np.where((up > down) & (up > 0), up, 0)
    neg_dm = np.where((down > up) & (down > 0), down, 0)
    
    tr = np.maximum(high - low, 
                    np.maximum(abs(high - close.shift(1)),
                               abs(low - close.shift(1))))
    atr = tr.rolling(period).mean()
    pos_di = 100 * pd.Series(pos_dm).rolling(period).mean() / atr
    neg_di = 100 * pd.Series(neg_dm).rolling(period).mean() / atr
    dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di + 1e-10)
    adx = dx.rolling(period).mean()
    
    regime = 'trending' if adx.iloc[-1] > 25 else 'ranging' if adx.iloc[-1] < 20 else 'transition'
    return regime, adx.iloc[-1], pos_di.iloc[-1], neg_di.iloc[-1]
```

### Choppiness Index (Alternativa a ADX para mercados laterales)

```
CHOP = 100 * LOG10(SUM(ATR, n) / (max_high(n) - min_low(n))) / LOG10(n)
CHOP > 61.8 = ranging, CHOP < 38.2 = trending
```

### Volatility Filter (ATR)

No operar cuando la volatilidad es muy baja (el precio no se mueve):

```python
def volatility_filter(df, min_atr_pct=0.3):
    atr = atr_calc(df)
    atr_pct = atr.iloc[-1] / df['close'].iloc[-1] * 100
    return atr_pct >= min_atr_pct  # False si muy baja volatilidad
```

**ATR% mínimo:** 0.3% forex, 1% stocks, 2% crypto.

### Session Filter (Forex)

| Sesión | UTC | Liquidez | Operar |
|---|---|---|---|
| Sydney | 22:00-07:00 | Baja | ❌ |
| Tokyo | 00:00-09:00 | Media | ⚠️ |
| London | 07:00-16:00 | Alta | ✅ |
| New York | 13:00-22:00 | Alta | ✅ |
| **Overlap** | **13:00-16:00** | **Máxima** | **✅ Mejor momento** |

### Market Structure Filter (Swing Points)

```
Uptrend = higher highs + higher lows → solo LONGs
Downtrend = lower highs + lower lows → solo SHORTs
Ranging = sin estructura clara → LONG o SHORT
```

### Correlation Filter

```
|r| > 0.85 → BLOCK (no abrir ambas posiciones)
|r| > 0.70 → REDUCE (mitad del tamaño)
```

**Ejemplo:** EUR/USD y GBP/USD tienen ~0.85 de correlación. Abrir ambas en la misma dirección duplica el riesgo sin duplicar la diversificación.

### RSI Divergence Filter (Wilder 1978)

```
RSI > 70 + precio subiendo = sobrecomprado → no LONG
RSI < 30 + precio bajando = sobrevendido → no SHORT
Bearish divergence: precio nuevo high, RSI más bajo → posible reversión bajista
Bullish divergence: precio nuevo low, RSI más alto → posible reversión alcista
```

### Filtro por Día de Semana

| Día | Acciones | Forex |
|---|---|---|
| Monday | Sesgo bajista (Monday Effect) | Reducir tamaño x0.7 |
| Tuesday | Neutral | Normal |
| Wednesday | Fuerte | Normal |
| Thursday | Débil pre-FOMC | Reducir tamaño x0.8 |
| Friday | Cerrar antes de cierre | Reducir x0.6, cerrar antes de 20:00 UTC |
| Saturday/Sunday | Cerrado | Cerrado |

### Volume Confirmation

```
Volumen actual > MA(20) de volumen → confirmación
OBV (On-Balance Volume) en tendencia alcista → confirmación LONG
```

### Pipeline de Filtros (Orden de Ejecución)

```
1. Session filter (más barato, más rápido)
2. Day of week (casi gratis)
3. Volatility filter (asegurar que hay movimiento)
4. Market structure (solo trades en dirección de tendencia)
5. Correlation (evitar riesgo duplicado)
6. RSI extreme (no comprar sobrecomprado)
7. ADX regime (ajustar estrategia según mercado)
```

### Referencias Entry Filters

| Fuente | Autor | Año |
|---|---|---|
| *New Concepts in Technical Trading Systems* | J.W. Wilder | 1978 |
| *Technical Analysis of the Financial Markets* | J. Murphy | 1999 |
| *The Art and Science of Technical Analysis* | A. Grimes | 2012 |
| *Trading for a Living* | A. Elder | 1993 |
| *Bollinger on Bollinger Bands* | J. Bollinger | 2002 |
| *Multiple Timeframe Trading* | W. Adams | 2004 |

---

## 4. Risk Management Metrics

### Value at Risk (VaR)

**Paramétrico:** `VaR = -(mu + sigma * z_alpha)`

```python
def parametric_var(returns, confidence=0.95):
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    z = stats.norm.ppf(1 - confidence)
    return -(mu + z * sigma)
```

**Histórico:** `VaR = -percentile(returns, (1 - confidence) * 100)`

| confianza | z-score |
|---|---|
| 95% | 1.645 |
| 99% | 2.326 |
| 99.5% | 2.576 |

### Expected Shortfall (CVaR)

Promedio de pérdidas más allá de VaR:

```python
def cvar(returns, confidence=0.95):
    var = historical_var(returns, confidence)
    tail = returns[returns <= -var]
    return -np.mean(tail) if len(tail) > 0 else var
```

### Sharpe Ratio (Sharpe 1994)

```
Sharpe = (mean_return - risk_free_rate) / std_return
Annualizado: Sharpe_daily * sqrt(252)
```

| Valor | Evaluación |
|---|---|
| < 0.5 | Pobre |
| 0.5 - 1.0 | Aceptable |
| 1.0 - 2.0 | Bueno |
| 2.0 - 3.0 | Excelente |
| > 3.0 | Sospechoso (probable overfitting) |

### Sortino Ratio

Igual que Sharpe pero usando solo desviación a la baja (downside deviation). Penaliza solo la volatilidad negativa.

### Calmar Ratio

```
Calmar = CAGR / Max Drawdown

CAGR = (Vf/Vi)^(1/Y) - 1

| Valor | Evaluación |
|---|---|
| < 1 | Malo |
| 1 - 3 | Bueno |
| 3 - 5 | Excelente |
```

### Profit Factor

```
PF = Gross Profit / Gross Loss

| PF | Evaluación |
|---|---|
| < 1.0 | Perdiendo plata |
| 1.0 - 1.5 | Marginal |
| 1.5 - 2.0 | Bueno |
| > 2.0 | Muy bueno |
```

### Maximum Drawdown

```
MDD = min((equity - peak) / peak)
Recovery = períodos desde trough hasta nuevo ATH
```

### Consecutive Loss Probability

```
Expected_max_losses ≈ log(1/(1-WR))(n_trades) + correction
```

**Ejemplo:** 40% WR, 1000 trades → ~10-12 pérdidas consecutivas esperadas.

### Monte Carlo Simulation

```python
def monte_carlo(trades_pnl, n_sim=10000):
    n = len(trades_pnl)
    final = np.zeros(n_sim)
    for i in range(n_sim):
        shuffled = np.random.choice(trades_pnl, n, replace=True)
        final[i] = np.sum(shuffled)
    return {
        'mean': np.mean(final),
        'p5': np.percentile(final, 5),
        'p95': np.percentile(final, 95),
        'prob_profit': np.mean(final > 0)
    }
```

Si el percentil 5 es negativo → >5% de probabilidad de perder plata.

### Tabla de Interpretación para Decisiones Automatizadas

| Métrica | Uso en el Bot |
|---|---|
| VaR/CVaR | Límite de posición: `max_size = risk_budget / VaR` |
| Sharpe | Ranking de estrategias, asignación dinámica |
| Sortino | Evitar estrategias con cola derecha (muchos wins chicos, pérdidas grandes) |
| Calmar | Rechazar si CAGR/MDD < 1 después de 6 meses |
| MDD | Circuit breaker al 80% del MDD histórico |
| Monte Carlo p5 | No operar si >5% de perder plata en 1 año |
| Kelly | Usar 0.25× Kelly como máximo |
| Consecutive Loss | Asegurar margen para 2× pérdidas consecutivas esperadas |

### Referencias Risk Management

| Fuente | Autor | Año |
|---|---|---|
| *Value at Risk* | P. Jorion | 2006 |
| *Conditional Value-at-Risk* | Rockafellar & Uryasev | 2000 |
| *The Sharpe Ratio* | W. Sharpe | 1994 |
| *Downside Risk* | Sortino & van der Meer | 1991 |
| *Maximum Drawdown* | Magdon-Ismail & Atiya | 2004 |
| *Advances in Financial Machine Learning* | M. Lopez de Prado | 2018 |

---

## 5. Complete Python RiskManager Class

```python
"""
RiskManager — Computa todas las métricas de una lista de trades P&L.
Uso: rm = RiskManager(lista_pnl, equity_curve); report = rm.full_report()
"""

import numpy as np
import warnings
from scipy import stats
from typing import List, Optional, Dict

class RiskManager:
    def __init__(self, trades_pnl: List[float], equity_curve: Optional[List[float]] = None,
                 initial_capital: float = 100000.0, periods_per_year: int = 252, confidence: float = 0.95):
        self.trades_pnl = np.array(trades_pnl, dtype=float)
        self.initial_capital = initial_capital
        self.periods_per_year = periods_per_year
        self.confidence = confidence
        
        if equity_curve is not None:
            self.equity_curve = np.array(equity_curve, dtype=float)
        else:
            self.equity_curve = initial_capital + np.concatenate([[0], np.cumsum(self.trades_pnl)])
        
        self.returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        self.n_trades = len(self.trades_pnl)
        self.wins = self.trades_pnl[self.trades_pnl > 0]
        self.losses = self.trades_pnl[self.trades_pnl < 0]
        self.win_rate = len(self.wins) / self.n_trades if self.n_trades > 0 else 0.0

    def sharpe_ratio(self) -> float:
        excess = self.returns - 0 / self.periods_per_year
        if np.std(excess, ddof=1) == 0: return 0.0
        return np.mean(excess) / np.std(excess, ddof=1) * np.sqrt(self.periods_per_year)

    def sortino_ratio(self) -> float:
        excess = self.returns - 0 / self.periods_per_year
        downside = excess.copy(); downside[downside > 0] = 0
        dd = np.sqrt(np.mean(downside**2)) * np.sqrt(self.periods_per_year)
        return np.mean(excess) * self.periods_per_year / dd if dd > 0 else 0.0

    def calmar_ratio(self) -> float:
        total_return = self.equity_curve[-1] / self.equity_curve[0]
        years = self.n_trades / self.periods_per_year if self.n_trades > 0 else 1
        cagr = total_return ** (1 / years) - 1 if years > 0 else 0
        mdd = abs(self.max_drawdown())
        return cagr / mdd if mdd > 0 else (np.inf if cagr > 0 else 0.0)

    def profit_factor(self) -> float:
        gw = np.sum(self.wins); gl = abs(np.sum(self.losses))
        return gw / gl if gl > 0 else (np.inf if gw > 0 else 0.0)

    def kelly_fraction(self) -> float:
        aw = np.mean(self.wins) if len(self.wins) > 0 else 0
        al = abs(np.mean(self.losses)) if len(self.losses) > 0 else 1
        odds = aw / al if al > 0 else 1
        return self.win_rate - (1 - self.win_rate) / odds

    def max_drawdown(self) -> float:
        rm = np.maximum.accumulate(self.equity_curve)
        return np.min((self.equity_curve - rm) / rm)

    def max_consecutive_losses(self) -> int:
        streak = max_streak = 0
        for p in self.trades_pnl:
            if p < 0: streak += 1; max_streak = max(max_streak, streak)
            else: streak = 0
        return max_streak

    def historical_var(self) -> float:
        if len(self.returns) == 0: return 0.0
        return -np.percentile(self.returns, (1 - self.confidence) * 100)

    def cvar(self) -> float:
        var = self.historical_var()
        tail = self.returns[self.returns <= -var]
        return -np.mean(tail) if len(tail) > 0 else var

    def full_report(self) -> Dict:
        return {
            'summary': {
                'trades': self.n_trades, 'wins': len(self.wins), 'losses': len(self.losses),
                'win_rate': self.win_rate, 'total_pnl': np.sum(self.trades_pnl),
                'avg_trade': np.mean(self.trades_pnl),
            },
            'ratios': {
                'sharpe': self.sharpe_ratio(), 'sortino': self.sortino_ratio(),
                'calmar': self.calmar_ratio(), 'profit_factor': self.profit_factor(),
                'kelly': self.kelly_fraction(), 'kelly_quarter': self.kelly_fraction() * 0.25,
            },
            'risk': {
                'mdd_pct': self.max_drawdown() * 100,
                'max_consecutive_losses': self.max_consecutive_losses(),
                'var_95': self.historical_var(), 'cvar_95': self.cvar(),
            }
        }
```

---

## 6. Combined Filter Pipeline

Orden de ejecución recomendado para minimizar cálculos innecesarios:

```python
class TradingFilters:
    def evaluate(self, signal, market_data, dt):
        for name, func in self.filters:
            passed, msg = func(signal, market_data, dt)
            if not passed:
                return False, f"BLOCKED by {name}: {msg}"
        return True, "PASS"

# Orden: (más baratos/veloces primero)
filters = [
    ('day_of_week', check_dow),         # O(1)
    ('session', check_session),          # O(1)
    ('volatility', check_atr),           # O(n)
    ('market_structure', check_structure),# O(n)
    ('correlation', check_corr),         # O(n * k)
    ('rsi_extreme', check_rsi),          # O(n)
    ('adx_regime', check_adx),           # O(n)
]
```

---

## 7. Referencias y Fuentes

### Libros Clásicos

| Título | Autor | Año | Tema |
|---|---|---|---|
| *New Concepts in Technical Trading Systems* | J.W. Wilder | 1978 | RSI, ATR, ADX, Parabolic SAR |
| *Technical Analysis of Stock Trends* | Edwards & Magee | 1948 | Análisis técnico clásico |
| *Technical Analysis of the Financial Markets* | J. Murphy | 1999 | Análisis técnico completo |
| *Trading for a Living* | A. Elder | 1993 | Psicología + trading |
| *Bollinger on Bollinger Bands* | J. Bollinger | 2002 | Bandas de Bollinger |
| *The Art and Science of Technical Analysis* | A. Grimes | 2012 | Estructura de mercado |
| *Trading Systems and Methods* | P. Kaufman | 2013 | Sistemas de trading |
| *Following the Trend* | A. Clenow | 2012 | Trend following |
| *The New Market Wizards* | J. Schwager | 1992 | Entrevistas a traders |

### Gestión de Riesgo y Position Sizing

| Título | Autor | Año |
|---|---|---|
| *The Mathematics of Money Management* | R. Vince | 1992 |
| *Value at Risk* | P. Jorion | 2006 |
| *Advances in Financial Machine Learning* | M. Lopez de Prado | 2018 |
| *The Black Swan* | N.N. Taleb | 2007 |
| *Conditional Value-at-Risk Optimization* | Rockafellar & Uryasev | 2000 |
| *The Sharpe Ratio* | W. Sharpe | 1994 |

### Artículos Académicos

| Título | Autor | Año | Journal |
|---|---|---|---|
| A New Interpretation of Information Rate | J.L. Kelly | 1956 | Bell System Tech. Journal |
| Maximum Drawdown | Magdon-Ismail & Atiya | 2004 | Risk Magazine |
| Empirical Properties of Asset Returns | R. Cont | 2001 | Quantitative Finance |
| The Longest Run of Heads | M. Schilling | 1990 | College Mathematics Journal |
| Day-of-the-Week Effect | K. French | 1980 | Journal of Financial Economics |
| Turn-of-the-Month Effect | Lakonishok & Smidt | 1988 | J. of Financial Economics |

---

*Documento compilado para MarketAI. Contiene fórmulas, código y referencias verificadas para implementar mejoras en el bot de trading automatizado.*
