# Automated Exit Strategies for Algorithmic Trading — Complete Reference

> Research compiled for MarketAI project.
> Sources: J. Welles Wilder Jr. (1978), Chuck LeBeau (Chandelier Exit), Cynthia Kase (Kase Dev-Stop), Martin J. Pring, John Murphy, Perry Kaufman.

---

## 1. ATR-Based Trailing Stops

### 1.1 Simple ATR Trailing Stop

**Formula:**
```
For LONG:
  Trail = HighestHighSinceEntry - (ATR × multiplier)
  Exit when price < Trail

For SHORT:
  Trail = LowestLowSinceEntry + (ATR × multiplier)
  Exit when price > Trail
```

**Python:**
```python
def atr_trailing_stop(df, entry_idx, position_type='LONG', atr_period=14, multiplier=3.0):
    atr = df['atr'].iloc[-1]
    if position_type == 'LONG':
        highest = df['high'].iloc[entry_idx:].max()
        trail = highest - (atr * multiplier)
        return trail
    else:
        lowest = df['low'].iloc[entry_idx:].min()
        trail = lowest + (atr * multiplier)
        return trail
```

**Default params:** ATR(14), multiplier=3.0

**Reference:** J. Welles Wilder Jr., *New Concepts in Technical Trading Systems* (1978)

**Pros:** Adapts to volatility, rides trends well, simple
**Cons:** Whipsaws in ranging markets, multiplier needs tuning per asset

**When to use:** Trending markets with consistent volatility

---

### 1.2 Chandelier Exit (Chuck LeBeau)

**Formula:**
```
For LONG:
  ChandelierExit = 22-PeriodHighestHigh - (ATR(22) × 3.0)

For SHORT:
  ChandelierExit = 22-PeriodLowestLow + (ATR(22) × 3.0)
```

The "chandelier" hangs from the highest high (long) or lowest low (short) over the lookback period.

**Python:**
```python
def chandelier_exit(df, position_type='LONG', lookback=22, atr_period=22, multiplier=3.0):
    atr = df['atr'].iloc[-1]
    if position_type == 'LONG':
        highest = df['high'].rolling(lookback).max().iloc[-1]
        exit_price = highest - (atr * multiplier)
    else:
        lowest = df['low'].rolling(lookback).min().iloc[-1]
        exit_price = lowest + (atr * multiplier)
    return exit_price
```

**Default params:** lookback=22, ATR(22), multiplier=3.0

**Reference:** Chuck LeBeau, *Technical Traders Guide to Computer Analysis of the Futures Markets* (1992)

**Pros:** Stays above price in strong trends, catches major moves
**Cons:** Wide stop can produce large losses, bad in chop

**When to use:** Strong trending markets, daily timeframe, swing trading

---

### 1.3 Kase Dev-Stop (Cynthia Kase)

**Formula:**
```
DevStop = EMA(price) ± (k × Dev)

Where:
  Dev = (k1 × ATR) + (k2 × StdDev(returns))
  k1, k2 = weighting factors
  k = overall multiplier (typically 1.0–2.5)
```

PEP (Peak Efficiency Point) determines the optimal multiplier value dynamically based on market efficiency.

**Python:**
```python
def kase_dev_stop(df, position_type='LONG', atr_period=14, k1=1.0, k2=0.5, k=1.6):
    atr = df['atr'].iloc[-1]
    returns = df['close'].pct_change().std() * df['close'].iloc[-1]
    dev = (k1 * atr) + (k2 * returns)
    ema = df['close'].ewm(span=atr_period).mean().iloc[-1]
    if position_type == 'LONG':
        return ema - (k * dev)
    else:
        return ema + (k * dev)
```

**Default params:** ATR(14), k1=1.0, k2=0.5, k=1.6

**Reference:** Cynthia A. Kase, *Trading with the Odds* (1996)

**Pros:** Smoother than raw ATR, adjusts to noise level
**Cons:** Complex parameterization, more computation

**When to use:** Futures, commodities, intraday where noise varies

---

## 2. Parabolic SAR as Trailing Stop

**Formula:**
```
SAR(n+1) = SAR(n) + α × (EP - SAR(n))

Where:
  α = acceleration factor (starts at 0.02, increments by 0.02 each new EP)
  EP = Extreme Point (highest high in uptrend, lowest low in downtrend)
  Max α = 0.20 (default)

Upon reversal:
  - New SAR = previous EP
  - α resets to 0.02
  - EP resets to current period's extreme
```

**Python:**
```python
def parabolic_sar(high, low, accel_init=0.02, accel_max=0.20):
    sar = low[0]
    ep = high[0]
    af = accel_init
    trend = 1  # 1 = up, -1 = down
    sar_values = [sar]

    for i in range(1, len(high)):
        if trend == 1:
            if low[i] < sar:
                trend = -1
                sar = ep
                ep = low[i]
                af = accel_init
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + accel_init, accel_max)
                sar = sar + af * (ep - sar)
                sar = min(sar, low[i-1], low[i]) if i > 0 else sar
        else:
            if high[i] > sar:
                trend = 1
                sar = ep
                ep = high[i]
                af = accel_init
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + accel_init, accel_max)
                sar = sar + af * (ep - sar)
                sar = max(sar, high[i-1], high[i]) if i > 0 else sar
        sar_values.append(sar)
    return sar_values
```

**Default params:** α=0.02, max=0.20

**Reference:** J. Welles Wilder Jr., *New Concepts in Technical Trading Systems* (1978)

**Pros:** Trails tightly in trends, auto-adjusts speed, well-known
**Cons:** Fails in sideways markets, late exits in very strong trends

**When to use:** Trending markets only, use with ADX (>25) to filter range-bound

---

## 3. Time-Based Exits

### 3.1 Exit After X Bars

**Formula:**
```
ExitCondition = bars_since_entry >= max_hold_bars
```

**Python:**
```python
def time_bar_exit(position, current_bar_index, max_bars=20):
    bars_held = current_bar_index - position['entry_bar']
    if bars_held >= max_bars:
        return True, f"max_bars_exit ({bars_held}/{max_bars})"
    return False, None
```

**Default params:** max_hold_bars = 20 (varies by timeframe)

### 3.2 Exit at Market Close

**Formula:**
```
ExitCondition = minutes_to_close <= closeout_minutes
```

**Python:**
```python
def market_close_exit(current_time, close_time="15:55", market="US"):
    from datetime import datetime, timedelta
    close = datetime.strptime(close_time, "%H:%M").time()
    now = current_time.time()
    if now >= close:
        return True, "market_close"
    return False, None
```

### 3.3 Adaptive Time Exit (profit/loss dependent)

**Formula:**
```
MaxHold(hours):
  if in_profit:    max = profit_hours
  if in_loss:      max = loss_hours
  if stagnant (<0.5% move): max = stagnant_hours
```

Already implemented in `paper_broker.py:_get_time_exit_hours()`

**Default params:** profit_hours=168 (7d), loss_hours=48 (2d), stagnant_hours=36

**Reference:** Kaufman, *Trading Systems and Methods* (2013)

**Pros:** Prevents black-swan holds, enforces discipline, easy
**Cons:** Ignores price action, can exit prematurely

**When to use:** Always as circuit breaker; combine with other stops

---

## 4. Partial Profit-Taking (Scale Out)

### 4.1 Fixed-Level Scale-Out

**Formula:**
```
Position splits into tranches:
  TP1 = entry + (risk × R1)  → close 33% of position
  TP2 = entry + (risk × R2)  → close 33% of position
  TP3 = entry + (risk × R3)  → close 34% of position (or let run)

  Typical: R=1.5, R=3.0, R=5.0  (1:1.5, 1:3, 1:5 R-multiples)
```

**Python:**
```python
class PartialTakeProfit:
    def __init__(self, levels=None):
        # levels = [(r_multiple, fraction_to_close), ...]
        self.levels = levels or [
            (1.5, 0.33),   # 1:1.5 risk:reward, close 33%
            (3.0, 0.33),   # 1:3, close another 33%
            (5.0, 0.34),   # 1:5, close final 34%
        ]

    def check(self, position, current_price, atr=None):
        entry = position['entry_price']
        risk = position['stop_distance']
        signal = position['signal']
        remaining = position.get('remaining_qty', 1.0)
        results = []

        for r_mult, fraction in self.levels:
            if fraction > remaining:
                continue
            if signal == 'LONG':
                target = entry + (risk * r_mult)
                if current_price >= target:
                    results.append({'close_fraction': fraction, 'reason': f'TP_R{r_mult}'})
            else:
                target = entry - (risk * r_mult)
                if current_price <= target:
                    results.append({'close_fraction': fraction, 'reason': f'TP_R{r_mult}'})
        return results
```

**Default params:** TP at 1.5R (33%), 3R (33%), 5R (34%)

**Reference:** Ryan Jones, *The Trading Game* (1999); Van Tharp, *Trade Your Way to Financial Freedom* (2007)

**Pros:** Locks profits, reduces emotional attachment, improves win rate
**Cons:** Capping massive runners, complex position tracking

**When to use:** High-probability setups with wide potential; trend-following

---

## 5. Moving Average as Trailing Stop

**Formula:**
```
For LONG:
  Exit when price < MA(period, type)

For SHORT:
  Exit when price > MA(period, type)

Type: SMA, EMA, HMA, WMA
Period: 20 (fast), 50 (medium), 200 (slow)
```

**Python:**
```python
def ma_trailing_stop(df, position_type='LONG', period=50, ma_type='ema'):
    if ma_type == 'ema':
        ma = df['close'].ewm(span=period).mean().iloc[-1]
    else:
        ma = df['close'].rolling(period).mean().iloc[-1]

    if position_type == 'LONG':
        return ma  # price < ma = exit
    else:
        return ma  # price > ma = exit
```

**Default params:** MA50 (trend), MA200 (macro trend), EMA20 (fast trail)

**Reference:** John Murphy, *Technical Analysis of the Financial Markets* (1999)

**Pros:** Simple, well-understood, works across timeframes
**Cons:** Lagging — exits after significant retracement; whipsaws in chop

**When to use:** Strong trend (ADX > 30), higher timeframes (4H+)

---

## 6. Break-Even Stop

**Formula:**
```
BE_trigger_price = entry ± (entry × trigger_pct)
BE_stop = entry_price

If price moves X% in your favor, move SL to entry.
```

**Python:**
```python
def breakeven_stop(position, current_price, trigger_pct=1.0):
    entry = position['entry_price']
    signal = position['signal']

    if signal == 'LONG':
        move_pct = ((current_price - entry) / entry) * 100
        if move_pct >= trigger_pct:
            return entry  # SL to breakeven
    else:
        move_pct = ((entry - current_price) / entry) * 100
        if move_pct >= trigger_pct:
            return entry  # SL to breakeven
    return None  # no change
```

**Default params:** trigger_pct = 0.5–1.0% (forex), 2.0–5.0% (stocks)

**Reference:** Standard risk management practice (no single academic source)

**Pros:** Eliminates loss on winner, reduces psychological pressure
**Cons:** Gets stopped out on retrace before the move continues; reduces R:R on winning trades

**When to use:** Always — set BE as second stop after initial SL

---

## 7. Volatility-Based Exits (ATR Contraction)

**Formula:**
```
Exit when ATR drops below threshold:
  ExitCondition = ATR_current < ATR_avg × contraction_factor

Or when volatility contracts below trailing level:
  ExitCondition = ATR_current < trailing_max_ATR × contraction_ratio
```

**Python:**
```python
def volatility_contraction_exit(df, atr_period=14, contraction_factor=0.6, atr_lookback=50):
    atr = df['atr'].iloc[-1]
    atr_max = df['atr'].rolling(atr_lookback).max().iloc[-1]
    threshold = atr_max * contraction_factor
    if atr < threshold:
        return True, f"vol_contraction ({atr:.2f} < {threshold:.2f})"
    return False, None
```

**Default params:** ATR(14), contraction_factor=0.6, atr_lookback=50

**Reference:** Linda Raschke, *Street Smarts* (1996); Larry Connors

**Pros:** Exits when trend loses momentum, adapts to market
**Cons:** In choppy markets ATR stays low, false signals

**When to use:** Momentum strategies (exit when volatility decays)

---

## 8. Structure-Based Exits (Market Structure Break)

### 8.1 Swing High/Low Breach

**Formula:**
```
For LONG:
  Exit when price breaches most recent swing low

For SHORT:
  Exit when price breaches most recent swing high

Swing Low:
  low[i] < low[i-1] AND low[i] < low[i+1]  (local minimum, 2 bars each side)
Swing High:
  high[i] > high[i-1] AND high[i] > high[i+1]  (local maximum)
```

**Python:**
```python
def find_swing_points(df, left_bars=2, right_bars=2):
    highs = df['high'].values
    lows = df['low'].values
    swing_highs = []
    swing_lows = []

    for i in range(left_bars, len(df) - right_bars):
        if all(highs[i] >= highs[i-j] for j in range(1, left_bars+1)) and \
           all(highs[i] >= highs[i+j] for j in range(1, right_bars+1)):
            swing_highs.append((df.index[i], highs[i]))
        if all(lows[i] <= lows[i-j] for j in range(1, left_bars+1)) and \
           all(lows[i] <= lows[i+j] for j in range(1, right_bars+1)):
            swing_lows.append((df.index[i], lows[i]))
    return swing_highs, swing_lows


def structure_breach_exit(df, position_type='LONG', left_bars=2, right_bars=2):
    _, swing_lows = find_swing_points(df, left_bars, right_bars)
    swing_highs, _ = find_swing_points(df, left_bars, right_bars)

    if position_type == 'LONG' and swing_lows:
        last_swing_low = swing_lows[-1][1]
        if df['close'].iloc[-1] < last_swing_low:
            return True, f"structure_breach_below_SL_{last_swing_low:.4f}"
    elif position_type == 'SHORT' and swing_highs:
        last_swing_high = swing_highs[-1][1]
        if df['close'].iloc[-1] > last_swing_high:
            return True, f"structure_breach_above_SH_{last_swing_high:.4f}"
    return False, None
```

**Default params:** left_bars=2, right_bars=2 (standard swing detection)

**Reference:** ICT (Inner Circle Trader) methodology; Elliott Wave theory by R.N. Elliott

**Pros:** Aligns with market logic, reduces noise exits
**Cons:** Subjective swing point selection; repainting; misses fast breaks

**When to use:** ICT/SMC strategies, trend-following with clear structure

---

## 9. Volatility-Based Partial TP (ATR Multiples)

**Formula:**
```
TP_distance = ATR × multiplier

LONG TP price = entry + (ATR × mult)
SHORT TP price = entry - (ATR × mult)

Multilevel partial TP:
  TP1 = 1x ATR → close 50%
  TP2 = 2x ATR → close 30%
  TP3 = 3x ATR → close 20% (let run)
```

**Python:**
```python
def atr_partial_tp(position, current_price, atr, levels=None):
    entry = position['entry_price']
    signal = position['signal']
    remaining = position.get('remaining_qty', 1.0)
    levels = levels or [
        (1.0, 0.50),   # 1x ATR, close 50%
        (2.0, 0.30),   # 2x ATR, close 30%
        (3.0, 0.20),   # 3x ATR, close 20%
    ]
    results = []
    for mult, fraction in levels:
        if fraction > remaining:
            continue
        if signal == 'LONG':
            target = entry + (atr * mult)
            if current_price >= target:
                results.append({'close_fraction': fraction, 'reason': f'ATR_TP_{mult}x'})
        else:
            target = entry - (atr * mult)
            if current_price <= target:
                results.append({'close_fraction': fraction, 'reason': f'ATR_TP_{mult}x'})
    return results
```

**Default params:** 1x ATR (50%), 2x ATR (30%), 3x ATR (20%)

**Reference:** Andreas F. Clenow, *Following the Trend* (2012); professional futures trading practice

**Pros:** Self-adjusts to volatility, scales out methodically
**Cons:** ATR expands in panic → targets too far; contracts in quiet

**When to use:** Futures, crypto, forex — any market with variable volatility

---

## 10. Trailing Stop with Volatility Cushion

**Formula:**
```
For LONG:
  trailing_stop = highest_since_entry - (current_atr × mult)
  cushion = current_atr × mult_cushion
  effective_stop = trailing_stop - cushion

For SHORT:
  trailing_stop = lowest_since_entry + (current_atr × mult)
  cushion = current_atr × mult_cushion
  effective_stop = trailing_stop + cushion
```

The cushion prevents the stop from being too tight when volatility is low, and relaxes when volatility is high.

**Python:**
```python
def volatility_cushion_stop(position, current_price, df, entry_idx,
                            atr_period=14, mult=2.0, cushion_mult=0.5):
    atr = df['atr'].iloc[-1]
    signal = position['signal']

    if signal == 'LONG':
        highest = df['high'].iloc[entry_idx:].max()
        base_trail = highest - (atr * mult)
        cushion = atr * cushion_mult
        return base_trail - cushion  # stops trailing underneath cushion
    else:
        lowest = df['low'].iloc[entry_idx:].min()
        base_trail = lowest + (atr * mult)
        cushion = atr * cushion_mult
        return base_trail + cushion
```

**Default params:** ATR(14), mult=2.0, cushion_mult=0.5

**Reference:** Nick Radge, *Adaptive Trailing Stops* whitepaper (2008); quant trader practice

**Pros:** Prevents premature stops in variable volatility; outperforms fixed ATR in backtests
**Cons:** Two parameters to tune; more distance = smaller position

**When to use:** Any trending strategy as the single primary exit

---

## Comparison Matrix

| Strategy | Trend | Range | Volatility Handling | Drawdown Control | Complexity |
|---|---|---|---|---|---|
| ATR Trailing | ★★★★★ | ★☆☆☆☆ | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Chandelier Exit | ★★★★★ | ★☆☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Kase Dev-Stop | ★★★★☆ | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Parabolic SAR | ★★★★☆ | ★☆☆☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |
| Time Exit | ★★☆☆☆ | ★★★★★ | ★☆☆☆☆ | ★★★★★ | ★☆☆☆☆ |
| Partial TP | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★★★ | ★★★★☆ |
| MA Trail | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★☆☆☆☆ |
| Break-Even | ★☆☆☆☆ | ★★★★★ | ★☆☆☆☆ | ★★★★★ | ★☆☆☆☆ |
| Vol Contraction | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Structure Breach | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ |
| ATR Partial TP | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Vol Cushion | ★★★★★ | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ |

---

## Recommended Multi-Strategy Stack (Layered Exits)

For production trading bots, combine exits in layers:

```
Layer 1 — Emergency (wide):
  Chandelier Exit (or ATR × 5)

Layer 2 — Structure (medium):
  Swing low/high breach

Layer 3 — Volatility (adaptive):
  ATR Trailing × 3

Layer 4 — Profit lock (after X% gain):
  Break-even stop

Layer 5 — Time (circuit breaker):
  Max hold time (adaptive by P/L)

Layer 6 — Partial take-profit:
  50% at 1× ATR
  30% at 2× ATR
  20% runs with trailing stop (Layer 1–4)
```

Implement in `paper_broker.py::check_stops()` — iterate through layers, lowest price wins (LONG) or highest wins (SHORT).
