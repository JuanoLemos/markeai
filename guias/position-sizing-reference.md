# Position Sizing Formulas for Automated Trading Systems

> Referencia técnica completa. Fuentes principales: Ralph Vince (1990, 1995, 2007), Ryan Jones (1999), Ed Thorp (1962), John L. Kelly Jr. (1956), Nauzer Balsara (1992), Robert Pardo (2008).

---

## Tabla de contenidos

1. [Kelly Criterion](#1-kelly-criterion)
2. [Optimal f (Ralph Vince)](#2-optimal-f-ralph-vince)
3. [Fixed Fractional Position Sizing](#3-fixed-fractional-position-sizing)
4. [Fixed Ratio Position Sizing (Ryan Jones)](#4-fixed-ratio-position-sizing-ryan-jones)
5. [Risk of Ruin](#5-risk-of-ruin)
6. [Half-Kelly / Quarter-Kelly](#6-half-kelly--quarter-kelly)
7. [Maximum Drawdown-Based Sizing](#7-maximum-drawdown-based-sizing)
8. [Compound vs Linear Growth Tradeoffs](#8-compound-vs-linear-growth-tradeoffs)

---

## 1. Kelly Criterion

### 1.1 Full Kelly

**Mathematical formula**

Kelly criterion maximizes the expected logarithm of wealth. For a binary outcome (win/loss):

```
f* = (bp - q) / b
```

Where:
- `f*` = fraction of capital to bet
- `b` = net odds received on the bet (profit per unit wagered, i.e., win_amount / risk_amount)
- `p` = probability of winning
- `q` = probability of losing = 1 - p

For trading with continuous outcomes (R-multiple distribution):

```
f* = (W - L) / W
```

Where `W` = average winner (as % of risk), `L` = average loser (as % of risk).

Or using the mean and variance of returns:

```
f* = μ / σ²
```

Where `μ` = mean excess return, `σ²` = variance of returns.

**Python pseudocode**

```python
def kelly_full(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Full Kelly fraction.

    Parameters
    ----------
    win_rate : float
        Probability of winning (0.0 to 1.0)
    avg_win  : float
        Average winning trade as decimal (e.g., 0.10 for 10%)
    avg_loss : float
        Average losing trade as positive decimal (e.g., 0.05 for 5% loss)

    Returns
    -------
    float
        Fraction of capital to risk per trade. 0.0 = no bet, negative = don't bet.
    """
    if win_rate <= 0.0 or win_rate >= 1.0:
        return 0.0
    # b = avg_win / avg_loss (odds received per unit risked)
    b = avg_win / avg_loss
    p = win_rate
    q = 1.0 - p
    f = (b * p - q) / b
    return max(0.0, f)  # never bet negative


def kelly_full_gaussian(mean_return: float, var_return: float) -> float:
    """
    Full Kelly for normally distributed returns.
    f* = μ / σ²
    """
    if var_return <= 0.0:
        return 0.0
    return mean_return / var_return
```

**Recommended default parameters**

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `win_rate` | rolling 50–100 trades | Enough for statistical relevance |
| `avg_win` / `avg_loss` | rolling 50–100 trades | Same window as win rate |
| Min trades before use | 30 | Minimum for statistical validity |
| Update frequency | After each trade | Or batch every N trades |
| Clip f* to | [0.0, 0.25] | Safety: never bet >25% per trade |

**Source / reference**

| Author | Work | Year |
|--------|------|------|
| John L. Kelly Jr. | "A New Interpretation of Information Rate" (Bell System Technical Journal) | 1956 |
| Edward O. Thorp | "Beat the Dealer" (blackjack) + "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market" | 1962, 2008 |
| William Poundstone | "Fortune's Formula" (historical overview) | 2005 |

**Pros**

- Mathematically optimal for maximizing long-run growth
- Maximizes geometric mean of returns
- Prevents over-betting (any fraction > f* reduces growth)
- Never risks ruin if exact probabilities known

**Cons / risks**

- Extreme volatility in practice (drawdowns of 50–80% common)
- Sensitive to estimation errors — overestimating p or underestimating q leads to overbetting
- Assumes known probabilities (which don't exist in markets)
- Assumes independence of outcomes (serial correlation breaks Kelly)
- Full Kelly is unplayable for most humans/strategies due to drawdown

---

### 1.2 Fractional Kelly (25%, 50%)

**Mathematical formula**

```
f_fractional = f_kelly × fraction
```

Where `fraction` is typically 0.25 (Quarter-Kelly), 0.50 (Half-Kelly), or 0.10 to 0.30 (common range).

**Python pseudocode**

```python
def kelly_fractional(win_rate: float, avg_win: float, avg_loss: float,
                     fraction: float = 0.25) -> float:
    """
    Fractional Kelly.

    Parameters
    ----------
    fraction : float
        Fraction of full Kelly to use (0.0 to 1.0).
        0.25 = Quarter-Kelly (conservative)
        0.50 = Half-Kelly (moderate)

    Returns
    -------
    float
        Fraction of capital to risk per trade.
    """
    f_full = kelly_full(win_rate, avg_win, avg_loss)
    return f_full * fraction
```

**When to use each fraction**

| Fraction | Use case | Drawdown expectation |
|----------|----------|---------------------|
| 100% (full) | Only if you can tolerate 60–80% drawdown and have perfect probability estimates | ~50–80% |
| 50% (half) | Professional edge, strong confidence in system, can tolerate 25–40% drawdown | ~25–40% |
| 25% (quarter) | Typical automated strategy, moderate confidence | ~10–20% |
| 10% (tenth) | Conservative, new strategy, small account, low Sharpe | ~5–10% |

**Source**

| Author | Work | Year |
|--------|------|------|
| Ralph Vince | "The Mathematics of Money Management" | 1992 |
| Nauzer Balsara | "Money Management Strategies for Futures Traders" | 1992 |
| Ed Thorp | Various papers on fractional Kelly | 1997+ |

---

## 2. Optimal f (Ralph Vince)

### 2.1 Formula

Optimal f is a numerical optimization that finds the fraction *f* that maximizes the Terminal Wealth Relative (TWR) after a sequence of trades.

Unlike Kelly (which assumes binary outcomes), Optimal f works with the actual distribution of historical trade outcomes (R-multiples).

**Mathematical definition**

Given a sequence of trade outcomes (R-multiples) `R_i` (where R = profit/risk, e.g., +2.0 means 2× risk gained, -1.0 means full risk lost):

```
TWR(f) = ∏_{i=1}^{N} [ 1 + f × (-R_i) ]
```

The Geometric Mean:

```
G(f) = TWR(f)^{1/N}
```

Optimal f maximizes `G(f)`.

Where:
- `f` = fraction of capital risked per trade (the variable being optimized)
- `R_i` = return on each trade in R-units (positive for winners, negative for losers)
- The worst-case loss is implicitly handled (if `f` is too large, a losing trade can wipe the account)

The optimization is bounded by the worst drawdown:

```
f < 1 / (max_drawdown_in_R_units)
```

**Key difference from Kelly**

| Aspect | Kelly Criterion | Optimal f |
|--------|----------------|-----------|
| Assumes | Binary outcomes (win/loss) | Any distribution (actual R-multiples) |
| Parametric | Needs p, b as point estimates | Non-parametric, works with empirical distribution |
| Robustness | Fragile to estimation error | More robust to outliers if historical sample is representative |
| Optimization | Closed-form formula | Numerical (iterative) |
| Published | 1956 | 1990 |

### 2.2 Python implementation

```python
import numpy as np
from scipy.optimize import minimize_scalar


def optimal_f(r_multiples: np.ndarray) -> dict:
    """
    Find the Optimal f (Ralph Vince) for a sequence of trade R-multiples.

    Parameters
    ----------
    r_multiples : np.ndarray
        Array of trade outcomes in R-units.
        +2.0 = gained 2× risk amount.
        -1.0 = lost full risk amount.
        -2.0 = lost 2× risk amount (possible with slippage).

    Returns
    -------
    dict with keys:
        f_opt       : optimal fraction
        twr         : Terminal Wealth Relative at f_opt
        geometric_mean : Geometric mean at f_opt
        max_dd      : Max drawdown at f_opt (as fraction of equity)
    """
    r = np.asarray(r_multiples, dtype=float)
    if len(r) == 0:
        return {'f_opt': 0.0, 'twr': 1.0, 'geometric_mean': 1.0, 'max_dd': 0.0}

    # Upper bound: f must be less than 1 / abs(largest loss)
    worst_loss = np.min(r)  # most negative
    if worst_loss >= 0:
        # No losing trades — cannot optimize (no risk)
        return {'f_opt': 0.0, 'twr': 1.0, 'geometric_mean': 1.0, 'max_dd': 0.0}

    upper_bound = 1.0 / abs(worst_loss)
    # Safety: never let optimal f exceed 0.5
    upper_bound = min(upper_bound, 0.5)

    def negative_geometric_mean(f):
        # TWR(f) = prod(1 + f * (-r_i))
        # Note: r_i is already negative for losers, so -r_i makes it positive
        # Actually: for each trade, equity multiplier = 1 + f * (-return)
        # where return is in R-units.
        # For a -1R loss: 1 + f * (-(-1)) = 1 - f  (correct)
        # For a +2R win: 1 + f * (-(2)) = 1 - 2f  (wrong! should be 1 + 2f)
        # CORRECTION: equity multiplier = 1 + f * r_i
        # For a -1R loss: 1 + f * (-1) = 1 - f  (correct)
        # For a +2R win: 1 + f * (2) = 1 + 2f  (correct)
        multipliers = 1.0 + f * r
        if np.any(multipliers <= 0):
            return 0.0  # account wiped
        twr = np.prod(multipliers)
        gmean = twr ** (1.0 / len(r))
        return -gmean  # negative for minimization

    result = minimize_scalar(
        negative_geometric_mean,
        bounds=(0.0, upper_bound),
        method='bounded'
    )

    f_opt = result.x
    multipliers = 1.0 + f_opt * r
    twr = np.prod(multipliers)
    gmean = twr ** (1.0 / len(r))

    # Calculate max drawdown at f_opt
    equity_curve = np.cumprod(multipliers)
    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = (peaks - equity_curve) / peaks
    max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0.0

    return {
        'f_opt': float(f_opt),
        'twr': float(twr),
        'geometric_mean': float(gmean),
        'max_dd': float(max_dd)
    }


def optimal_f_with_constraint(r_multiples: np.ndarray,
                              max_allowed_dd: float = 0.25) -> dict:
    """
    Optimal f constrained to keep estimated drawdown below max_allowed_dd.
    """
    result = optimal_f(r_multiples)
    if result['max_dd'] <= max_allowed_dd:
        return result

    # Binary search for f that respects drawdown constraint
    r = np.asarray(r_multiples, dtype=float)
    lo, hi = 0.0, result['f_opt']
    for _ in range(50):
        mid = (lo + hi) / 2.0
        multipliers = 1.0 + mid * r
        equity_curve = np.cumprod(multipliers)
        peaks = np.maximum.accumulate(equity_curve)
        dd = np.max((peaks - equity_curve) / peaks) if len(equity_curve) > 0 else 0.0
        if dd <= max_allowed_dd:
            lo = mid
        else:
            hi = mid

    final_f = (lo + hi) / 2.0
    multipliers = 1.0 + final_f * r
    twr = np.prod(multipliers)
    gmean = twr ** (1.0 / len(r))
    equity_curve = np.cumprod(multipliers)
    peaks = np.maximum.accumulate(equity_curve)
    max_dd = np.max((peaks - equity_curve) / peaks) if len(equity_curve) > 0 else 0.0

    return {
        'f_opt': float(final_f),
        'twr': float(twr),
        'geometric_mean': float(gmean),
        'max_dd': float(max_dd),
        'note': 'Constrained by max_dd'
    }
```

**Recommended default parameters**

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| Min trades | 30 | Small samples produce unreliable f |
| Upper bound | 0.25 (Quarter) | Safety cap — never bet more than 25% |
| Max drawdown constraint | 20–30% | Typical professional risk tolerance |
| Optimization method | Bounded scalar | Simple, avoids gradient issues |
| Num iterations | 50 | Sufficient for binary search in constraint mode |

**Source / reference**

| Author | Work | Year |
|--------|------|------|
| Ralph Vince | "Portfolio Management Formulas" | 1990 |
| Ralph Vince | "The Mathematics of Money Management" | 1992 |
| Ralph Vince | "The Handbook of Portfolio Mathematics" | 2007 |

**Pros**

- Works with any distribution of returns (not just binary)
- Directly optimizes geometric growth
- Accounts for the full shape of the P&L distribution
- More realistic than Kelly for trading with variable win sizes

**Cons / risks**

- Overfits to historical data — optimal f from 100 trades rarely matches the unseen future
- Highly sensitive to the largest loss in the sample
- Can suggest extremely aggressive sizing if history has no large loss (black swan risk)
- Needs numerical optimization (no closed form)
- Drawdown can be catastrophic if future losses exceed historical ones

---

## 3. Fixed Fractional Position Sizing

### 3.1 Formula

Risk a fixed percentage of current account equity per trade.

**Position size formula:**

```
PositionSize = (AccountEquity × RiskPercent) / (EntryPrice - StopLossPrice)

Or in R-units:

PositionSize = (AccountEquity × RiskPercent) / RiskPerUnit
```

Where:
- `RiskPercent` = fraction of equity to risk (e.g., 0.01 for 1%)
- `RiskPerUnit` = dollar risk per share/contract (entry - stop)

**Python pseudocode**

```python
def fixed_fractional_size(
    account_equity: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    position_value_per_unit: float = 1.0,
) -> int:
    """
    Calculate position size using Fixed Fractional method.

    Parameters
    ----------
    account_equity : float
        Current account value in dollars
    risk_percent  : float
        Fraction of equity to risk per trade (0.01 = 1%)
    entry_price   : float
        Entry price per unit
    stop_loss     : float
        Stop loss price per unit
    position_value_per_unit : float
        Notional value per unit (for FX: units, for stocks: shares, for futures: 1 contract)

    Returns
    -------
    int
        Number of units/shares/contracts to trade
    """
    if account_equity <= 0:
        return 0
    if entry_price <= 0 or stop_loss < 0:
        return 0

    dollar_risk = account_equity * risk_percent
    risk_per_unit = abs(entry_price - stop_loss) * position_value_per_unit

    if risk_per_unit <= 0:
        return 0

    return int(dollar_risk / risk_per_unit)


def fixed_fractional_size_from_r(
    account_equity: float,
    risk_percent: float,
    risk_per_unit: float,
) -> int:
    """
    Simplified version when risk-per-unit is already known.
    """
    if account_equity <= 0 or risk_per_unit <= 0:
        return 0
    dollar_risk = account_equity * risk_percent
    return int(dollar_risk / risk_per_unit)
```

**Recommended default parameters**

| Parameter | Suggested | Context |
|-----------|-----------|---------|
| `risk_percent` | 0.5% – 2% | Account size < $50K: 1–2%; > $500K: 0.5–1% |
| Conservative | 0.5% (0.005) | Protracted losing streaks |
| Moderate | 1.0% (0.01) | Typical automated system |
| Aggressive | 2.0% (0.02) | High Sharpe (>1.5), short streaks |
| Very aggressive | 3%+ | Not recommended for automated systems |

**Source**

| Author | Work | Year |
|--------|------|------|
| Ralph Vince | "Portfolio Management Formulas" | 1990 |
| Robert Pardo | "The Evaluation and Optimization of Trading Strategies" | 2008 |
| Van Tharp | "Trade Your Way to Financial Freedom" | 2007 |
| Ryan Jones | "The Trading Game" | 1999 |

**Pros**

- Simple, intuitive, easy to implement
- Scales with equity (more capital = larger position)
- Naturally reduces size during drawdowns
- Risk per trade is constant as % of account
- Works with any market, timeframe, or strategy

**Cons / risks**

- Too conservative vs Kelly for high-win-rate systems
- Too aggressive vs Kelly for low-win-rate systems
- Doesn't account for win rate or edge at all
- Doesn't adapt to changing market conditions
- Can produce large intra-trade swings if stops are wide
- Position size oscillates with every equity change (can be noisy)

---

## 4. Fixed Ratio Position Sizing (Ryan Jones)

### 4.1 Formula

Fixed Ratio increases position size by one unit after the account grows by a fixed profit amount (the *delta*). Unlike fixed fractional, it grows arithmetically (by units) rather than geometrically (by percentage).

```
CurrentLevel = Floor( (AccountEquity - StartingEquity) / Delta ) + 1

NewSize = min(CurrentLevel, MaxSize)
```

Where:
- `Delta` = profit required to increase by one unit
- `StartingEquity` = equity when trading began at size 1

**To calculate Delta:**

```
Delta = 0.5 × (StdDev_of_Trade_P&L) × Risk_Factor

Or heuristically:

Delta = 0.25 × (Max_Losing_Streak × Avg_Loss)
```

### 4.2 Python pseudocode

```python
def fixed_ratio_size(
    account_equity: float,
    starting_equity: float,
    delta: float,
    max_size: int = 100,
) -> int:
    """
    Fixed Ratio position sizing (Ryan Jones).

    Parameters
    ----------
    account_equity  : float
        Current account equity.
    starting_equity : float
        Account equity when at size 1.
    delta           : float
        Profit required to increase position by 1 unit.
    max_size        : int
        Maximum allowed position size.

    Returns
    -------
    int
        Number of contracts/shares/units.
    """
    if account_equity <= starting_equity or delta <= 0:
        return 1

    # Number of levels above starting equity
    levels = (account_equity - starting_equity) / delta
    size = int(levels) + 1  # +1 because we start at size 1
    return min(size, max_size)


def estimate_fixed_ratio_delta(
    avg_trade_pnl: float,
    std_trade_pnl: float,
    max_consecutive_losses: int,
) -> float:
    """
    Heuristic to estimate a reasonable delta.

    Common approach: delta = 0.5 * std_pnl (conservative)
                           = 0.25 * max_consecutive_losses * avg_loss
    """
    return 0.5 * std_trade_pnl


class FixedRatioManager:
    """
    Manages Fixed Ratio position size progression.
    Tracks a reference equity level for when size last changed.
    """

    def __init__(self, delta: float, initial_size: int = 1, max_size: int = 100):
        self.delta = delta
        self.current_size = initial_size
        self.max_size = max_size
        self.next_level_equity = initial_size * initial_size * delta  # Ryan Jones formula
        # Actually the simplified level tracking:
        self.base_equity = None

    def update(self, current_equity: float) -> int:
        if self.base_equity is None:
            self.base_equity = current_equity
            return self.current_size

        # Ryan Jones original formulation
        # Size increases by 1 when account grows by: current_size * delta
        # So at size 1, need delta; at size 2, need 2*delta more; etc.
        equity_growth = current_equity - self.base_equity
        required_growth = self.current_size * self.delta

        if equity_growth >= required_growth and self.current_size < self.max_size:
            self.current_size += 1
            self.base_equity = current_equity
        elif equity_growth < 0 and self.current_size > 1:
            # Check if we should decrease
            required_growth_for_current = (self.current_size - 1) * self.delta
            if equity_growth < -required_growth_for_current:
                self.current_size -= 1
                self.base_equity = current_equity

        return self.current_size
```

**Recommended default parameters**

| Parameter | Suggested | Comment |
|-----------|-----------|---------|
| Delta | 0.5 × StdDev(trade P&L) | Conservative growth |
| Delta (conservative) | 1.0 × StdDev(trade P&L) | Very slow growth |
| Max size | 10–20 | Unless large account |
| Min trades before use | 30 | For stable std estimate |
| Re-estimate delta | Every 50 trades | Or quarterly |

**Source**

| Author | Work | Year |
|--------|------|------|
| Ryan Jones | "The Trading Game: Playing by the Numbers to Make Millions" | 1999 |

**Pros**

- Geometric profits (compounding) with arithmetic risk growth
- Less aggressive than fixed fractional in early stages
- More aggressive than fixed fractional in later stages (good)
- Smooth equity curve progression
- Naturally adjusts to volatility (via delta)
- Avoids the "ratchet down" effect of fixed fractional during drawdowns

**Cons / risks**

- Can increase size too rapidly during a hot streak (bad if streak ends)
- Delta selection is critical and not obvious
- Can decrease size too slowly during drawdowns
- Less common = fewer resources/examples
- Complex to manage with multiple instruments
- Ryan Jones formulation is proprietary and can be confusing

---

## 5. Risk of Ruin

### 5.1 Formulas

**Simplified (fixed bet size, fixed probability):**

```
R = (q / p)^(Capital / BetSize)

Where:
  p = probability of winning
  q = 1 - p (probability of losing)
  Capital = current account size
  BetSize = amount risked per trade
```

**Assuming p ≠ q (edge exists):**

```
R = ((1 - edge) / (1 + edge))^(Capital / BetSize)

Where edge = (p - q) = 2p - 1
```

**With variable bet size (fixed fraction):**

```
R = ( (1 - f) / (1 + f) )^(Capital_Units)

Where:
  f = fraction of capital risked per trade
  Capital_Units = initial capital in "risk units"
```

**Continuous risk of ruin (Wiener process approximation):**

```
R = exp(-2 × μ × S / σ²)

Where:
  μ = expected return per trade
  σ = standard deviation of returns
  S = capital (in same units as μ and σ)
```

### 5.2 Python pseudocode

```python
def risk_of_ruin_simple(
    win_rate: float,
    risk_per_trade_pct: float,
    capital_fraction: float = 1.0,
    bet_as_fraction_of_capital: bool = True,
) -> float:
    """
    Simplified risk of ruin probability.

    Parameters
    ----------
    win_rate              : float
        Probability of a winning trade (0 to 1)
    risk_per_trade_pct    : float
        Percentage of capital risked per trade (0.02 = 2%)
    capital_fraction      : float
        Fraction of initial capital remaining = ruin threshold.
        Usually 0.0 (zero), or 0.5 (half lost) as practical ruin.

    Returns
    -------
    float
        Probability of ruin (0.0 = certain survival, 1.0 = certain ruin).
    """
    if win_rate <= 0.0 or win_rate >= 1.0:
        return 1.0

    p = win_rate
    q = 1.0 - p

    if p <= q:
        return 1.0  # No edge → certain ruin with enough trades

    if bet_as_fraction_of_capital:
        # Each trade risks fraction f of current capital
        f = risk_per_trade_pct
        capital_units = abs(np.log(capital_fraction) / np.log(1 - f))

        # R = ((1-f)/(1+f))^(capital_units)
        # But this is a simplification — true formula depends on win/lose sequence
        if f <= 0:
            return 0.0

        return ((1.0 - f) / (1.0 + f)) ** capital_units
    else:
        # Fixed bet size (not recommended for trading)
        bet_as_fraction = risk_per_trade_pct
        capital_in_bets = capital_fraction / bet_as_fraction
        if capital_in_bets <= 0:
            return 0.0
        return (q / p) ** capital_in_bets


def risk_of_ruin_continuous(
    mean_return: float,
    std_return: float,
    capital: float,
    ruin_threshold: float = 0.0,
) -> float:
    """
    Risk of ruin using continuous (Wiener) approximation.

    R = exp(-2 * μ * S / σ²)

    Parameters
    ----------
    mean_return    : float
        Expected return per trade (dollar or %)
    std_return     : float
        Standard deviation of returns per trade (same units)
    capital        : float
        Current capital (same units)
    ruin_threshold : float
        Capital level considered ruin (e.g., 0.0, or 0.5 * capital)

    Returns
    -------
    float
        Probability of hitting ruin threshold eventually.
    """
    if mean_return <= 0.0 or std_return <= 0.0:
        return 1.0

    S = capital - ruin_threshold  # distance to ruin
    if S <= 0:
        return 1.0

    exponent = -2.0 * mean_return * S / (std_return ** 2)
    return np.exp(exponent)


def probability_of_drawdown(
    win_rate: float,
    risk_per_trade: float,
    target_drawdown: float = 0.20,
) -> float:
    """
    Probability of experiencing a drawdown of at least target_drawdown.

    Approximation using streak probability.
    """
    if win_rate <= 0.0:
        return 1.0

    p_loss = 1.0 - win_rate
    # Consecutive losses needed to hit target_drawdown
    # With fixed fraction: (1 - f)^n <= (1 - target_dd)
    # n >= log(1 - target_dd) / log(1 - f)
    if risk_per_trade <= 0:
        return 0.0

    n = np.log(1.0 - target_drawdown) / np.log(1.0 - risk_per_trade)
    if n < 1:
        return 1.0

    # Probability of n consecutive losses
    return p_loss ** n


# Practical risk manager
class RiskOfRuinManager:
    """
    Tracks risk of ruin in real-time and adjusts position size.
    """

    def __init__(self,
                 initial_capital: float,
                 ruin_threshold: float = 0.0,
                 max_risk_of_ruin: float = 0.01,
                 lookback_trades: int = 100):
        self.initial_capital = initial_capital
        self.ruin_threshold = ruin_threshold
        self.max_risk_of_ruin = max_risk_of_ruin
        self.lookback_trades = lookback_trades
        self.trades = []

    def add_trade(self, pnl: float, risk_amount: float):
        self.trades.append({
            'pnl': pnl,
            'risk': risk_amount,
            'r_multiple': pnl / risk_amount if risk_amount > 0 else 0.0
        })
        if len(self.trades) > self.lookback_trades * 2:
            self.trades = self.trades[-self.lookback_trades:]

    def current_risk_of_ruin(self, current_capital: float) -> float:
        recent = self.trades[-self.lookback_trades:] if len(self.trades) > self.lookback_trades else self.trades
        if len(recent) < 10:
            return 0.0

        r_multiples = [t['r_multiple'] for t in recent]
        mean_r = np.mean(r_multiples)
        std_r = np.std(r_multiples)

        if std_r == 0 or mean_r <= 0:
            return 1.0

        # Convert to continuous risk of ruin
        capital_risk_unit = current_capital - self.ruin_threshold
        return risk_of_ruin_continuous(mean_r, std_r, capital_risk_unit)

    def max_safe_fraction(self, current_capital: float) -> float:
        """
        Find the maximum risk fraction that keeps risk of ruin below threshold.
        """
        target_ror = self.max_risk_of_ruin
        lo, hi = 0.0, 0.05  # search up to 5% per trade

        for _ in range(30):
            mid = (lo + hi) / 2.0
            # Approximate: risk of ruin rises with f
            ror = self.current_risk_of_ruin(current_capital * (1 - mid * 10) if True else current_capital)
            # Simplified: use the fixed-fraction formula
            recent = self.trades[-self.lookback_trades:] if len(self.trades) > self.lookback_trades else self.trades
            wins = sum(1 for t in recent if t['pnl'] > 0)
            if len(recent) > 0:
                win_rate = wins / len(recent)
                ror_est = risk_of_ruin_simple(win_rate, mid)
                if ror_est <= target_ror:
                    lo = mid
                else:
                    hi = mid

        return lo
```

**Recommended default parameters**

| Parameter | Suggested | Context |
|-----------|-----------|---------|
| Maximum acceptable ruin risk | 1% (0.01) | Professional |
| Practical ruin threshold | Account < 50% of peak | Drawdown-based survival |
| Lookback trades | 100–200 | Balance recency vs stability |
| Min trades for estimate | 20 | Below this, assume no edge |

**Source**

| Author | Work | Year |
|--------|------|------|
| Ralph Vince | "Portfolio Management Formulas" Ch. 6 | 1990 |
| Ralph Vince | "The Mathematics of Money Management" | 1992 |
| Nauzer Balsara | "Money Management Strategies for Futures Traders" | 1992 |
| William Feller | "An Introduction to Probability Theory" (gambler's ruin) | 1968 |
| J.L. Kelly Jr. | Original paper (ruin probability in Appendix) | 1956 |

**Pros**

- Quantifies the single most important risk: total loss
- Allows setting position size based on acceptable ruin probability
- Simple formulas work as close approximations
- Provides objective stop condition for a strategy

**Cons / risks**

- All formulas assume independence of trades (not true in markets)
- Estimating p and q from historical data is unreliable
- Cannot account for regime changes (volatility spikes)
- Past risk of ruin ≠ future risk of ruin
- Very sensitive to small changes in win rate estimate
- "Practical ruin" (50% drawdown) is more useful than "absolute ruin" (0%)

---

## 6. Half-Kelly / Quarter-Kelly

### 6.1 Why reduced Kelly

The theoretical justification:

1. **Estimation error**: If you overestimate edge by 2×, full Kelly leads to 2× overbetting, growth rate becomes *negative* (sub-optimal). Half-Kelly stays profitable.

2. **Drawdown tolerance**: Full Kelly can produce 60–80% drawdowns. Half-Kelly reduces max drawdown by ~50%. Quarter-Kelly reduces it by ~75%.

3. **The "Kurtosis problem"**: Kelly assumes known distribution. Markets have fat tails. A −10σ event (rare but real) wipes out a full Kelly bettor but only hurts a Quarter-Kelly bettor.

4. **Growth-optimality tradeoff**: Half-Kelly reduces growth rate by 25% but cuts volatility by 50% (measured by Sharpe ratio improvement).

**Growth reduction table:**

| Fraction | Drawdown vs Full Kelly | Growth vs Full Kelly | Approx max DD |
|----------|----------------------|---------------------|---------------|
| 100% (Full) | 100% | 100% | 60–80% |
| 50% (Half) | ~40–50% | ~75% | 25–35% |
| 25% (Quarter) | ~15–25% | ~50% | 10–20% |
| 10% (Tenth) | ~5–10% | ~25% | 3–8% |

### 6.2 Python implementation

```python
def kelly_family(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
) -> dict:
    """
    Calculate Full, Half, Quarter, and Tenth Kelly.

    Returns dict with fractions and recommended use cases.
    """
    f_full = kelly_full(win_rate, avg_win, avg_loss)

    return {
        'full_kelly': {
            'f': f_full,
            'max_dd_estimate': f_full * 3,  # heuristic
            'recommendation': 'Only for known-probability repetitive bets (not trading)'
        },
        'half_kelly': {
            'f': f_full * 0.50,
            'max_dd_estimate': f_full * 1.5,
            'recommendation': 'Strong edge, moderate confidence, high risk tolerance'
        },
        'quarter_kelly': {
            'f': f_full * 0.25,
            'max_dd_estimate': f_full * 0.75,
            'recommendation': 'Typical automated strategy with reasonable edge'
        },
        'tenth_kelly': {
            'f': f_full * 0.10,
            'max_dd_estimate': f_full * 0.30,
            'recommendation': 'New strategy, low Sharpe, small account, conservative'
        }
    }


def optimal_kelly_fraction(sharpe_ratio: float) -> float:
    """
    Rule of thumb: optimal fraction of Kelly ≈ Sharpe ratio.
    For Sharpe 0.5 → 50% Kelly. Sharpe 0.25 → 25% Kelly.
    """
    return max(0.0, min(1.0, sharpe_ratio))


def adaptive_kelly(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    current_drawdown: float,
    confidence_factor: float = 1.0,
) -> float:
    """
    Adaptive Kelly that reduces fraction during drawdown.

    Parameters
    ----------
    current_drawdown : float
        Current drawdown from peak (0.15 = 15% down)
    confidence_factor : float
        How confident we are in edge estimate (0.0 to 1.0)
    """
    f_full = kelly_full(win_rate, avg_win, avg_loss)

    # Base fraction: quarter Kelly
    base_fraction = 0.25

    # Reduce further during drawdown
    drawdown_penalty = max(0.0, 1.0 - current_drawdown * 3)

    # Reduce if confidence is low
    confidence_mult = confidence_factor

    f_final = f_full * base_fraction * drawdown_penalty * confidence_mult
    return f_final
```

**Source**

| Author | Work | Year |
|--------|------|------|
| Edward O. Thorp | "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market" | 2008 |
| Paul Samuelson | Criticism of Kelly (MIT) — showed it's not optimal for all utility functions | 1970s |
| M. Stutzer | "A Portfolio Performance Index" (Kelly vs fractional Kelly) | 2000 |
| Victor Haghani | "Why Many Investors Fail: The Kelly Criterion" | 2015 |

**Pros**

- Significantly reduces drawdown and volatility
- Maintains most of the compound growth
- Robust to estimation errors (the real-world killer)
- Matches most traders' risk tolerance
- Easy to implement (multiply full Kelly by constant)

**Cons / risks**

- Not theoretically optimal (no single "right" fraction)
- Choice of fraction is subjective
- Still needs good edge estimates
- Fractional Kelly still overweights if edge is overestimated
- Some argue: if you can't use full Kelly, you shouldn't bet at all (academic view)

---

## 7. Maximum Drawdown-Based Sizing

### 7.1 Formula

Adjust position size dynamically based on current drawdown from peak equity. The goal: reduce risk when underwater to protect the account, and increase risk when near highs when you can "afford" it.

**Basic drawdown-based adjustment:**

```
RiskPercent = BaseRisk × DD_Multiplier

DD_Multiplier = 1.0 - (CurrentDD / MaxTolerableDD)

Or:

DD_Multiplier = min(1.0, (MaxTolerableDD - CurrentDD) / MaxTolerableDD)
```

**Variant — "Safe f" (drawdown-adjusted Optimal f):**

```
Safe_f = Optimal_f × (1 - CurrentDD / MaxAcceptableDD)

Where:
  CurrentDD = current drawdown (0.15 = 15% below peak)
  MaxAcceptableDD = the most drawdown you'll tolerate (e.g., 0.30)
```

**Stop-and-reverse (shut down at threshold):**

```
if CurrentDD >= MaxTolerableDD:
    PositionSize = 0   # STOP TRADING
```

### 7.2 Python pseudocode

```python
class DrawdownBasedSizer:
    """
    Position sizer that adjusts risk based on current drawdown.
    """

    def __init__(self,
                 base_risk_pct: float = 0.01,
                 max_tolerable_dd: float = 0.25,
                 recovery_mode: str = 'linear',
                 dd_peak_window: int = 50):
        """
        Parameters
        ----------
        base_risk_pct    : float
            Base risk fraction (0.01 = 1%)
        max_tolerable_dd : float
            Risk goes to zero at this drawdown
        recovery_mode    : str
            'linear' — smooth reduction
            'step'   — discrete tiers
            'shutdown' — stop trading at threshold
        dd_peak_window   : int
            Only consider peak within this many periods
        """
        self.base_risk_pct = base_risk_pct
        self.max_tolerable_dd = max_tolerable_dd
        self.recovery_mode = recovery_mode
        self.dd_peak_window = dd_peak_window
        self.peak_equity = None
        self.equity_history = []

    def update_equity(self, current_equity: float):
        self.equity_history.append(current_equity)
        if len(self.equity_history) > self.dd_peak_window * 2:
            self.equity_history = self.equity_history[-self.dd_peak_window:]

        # Running peak (using window to allow new peaks to form)
        window = self.equity_history[-self.dd_peak_window:]
        self.peak_equity = max(window) if window else current_equity

    def current_drawdown(self) -> float:
        if self.peak_equity is None or self.peak_equity <= 0:
            return 0.0
        current_eq = self.equity_history[-1] if self.equity_history else 0
        return max(0.0, (self.peak_equity - current_eq) / self.peak_equity)

    def get_risk_multiplier(self) -> float:
        dd = self.current_drawdown()

        if self.max_tolerable_dd <= 0:
            return 0.0

        if dd >= self.max_tolerable_dd:
            return 0.0  # Shut down

        if self.recovery_mode == 'linear':
            # f = base * (1 - dd / max_dd)
            mult = 1.0 - (dd / self.max_tolerable_dd)
            return max(0.0, mult)

        elif self.recovery_mode == 'step':
            # Discrete tiers
            ratio = dd / self.max_tolerable_dd
            if ratio <= 0.25:
                return 1.0
            elif ratio <= 0.50:
                return 0.75
            elif ratio <= 0.75:
                return 0.50
            else:
                return 0.25

        elif self.recovery_mode == 'shutdown':
            return 1.0 if dd < self.max_tolerable_dd else 0.0

        return 1.0

    def get_position_size(self,
                          account_equity: float,
                          entry_price: float,
                          stop_loss: float,
                          value_per_unit: float = 1.0) -> int:
        mult = self.get_risk_multiplier()
        adjusted_risk = self.base_risk_pct * mult

        risk_per_unit = abs(entry_price - stop_loss) * value_per_unit
        if risk_per_unit <= 0:
            return 0

        dollar_risk = account_equity * adjusted_risk
        return int(dollar_risk / risk_per_unit)


class SafetyFirstSizer:
    """
    Combines multiple sizing methods with drawdown protection.
    """

    def __init__(self,
                 base_fraction_fn,  # callable returning base risk fraction
                 max_dd: float = 0.20,
                 risk_of_ruin_limit: float = 0.01):
        self.base_fn = base_fraction_fn
        self.max_dd = max_dd
        self.ror_limit = risk_of_ruin_limit
        self.peak_equity = None

    def __call__(self, account_equity: float, trade_stats: dict) -> float:
        # 1. Get base fraction from primary method
        f_base = self.base_fn(trade_stats)

        # 2. Apply drawdown penalty
        if self.peak_equity is None:
            self.peak_equity = account_equity
        self.peak_equity = max(self.peak_equity, account_equity)

        dd = max(0.0, (self.peak_equity - account_equity) / self.peak_equity)
        dd_penalty = 1.0 - (dd / self.max_dd) if dd < self.max_dd else 0.0
        dd_penalty = max(0.0, dd_penalty)

        # 3. Apply penalty
        f_adjusted = f_base * dd_penalty

        # 4. Cap at safety limits
        return min(f_adjusted, 0.02)  # never exceed 2% per trade
```

**Recommended default parameters**

| Parameter | Suggested | Context |
|-----------|-----------|---------|
| `max_tolerable_dd` | 20–30% | Professional |
| `base_risk_pct` | 1% | Before any adjustment |
| Recovery mode | `linear` | Smooth, no cliff effects |
| Peak window | 50–100 periods | Recent enough to be relevant |
| DD multiplier floor | 0.25 | Never go to zero (unless shutdown) |

**Source**

| Author | Work | Year |
|--------|------|------|
| Robert Pardo | "The Evaluation and Optimization of Trading Strategies" | 2008 |
| Van K. Tharp | "Trade Your Way to Financial Freedom" | 2007 |
| Ralph Vince | "The Mathematics of Money Management" (drawdown constraints) | 1992 |
| Howard Marks | "The Most Important Thing" (risk management philosophy) | 2011 |

**Pros**

- Directly addresses the #1 concern: large drawdowns
- Automatically reduces risk when it matters most (after losses)
- Prevents the "death spiral" of fixed sizing during drawdowns
- Intuitive and easy to explain
- Combines well with any other sizing method

**Cons / risks**

- Defers recovery (smaller size during drawdown = slower to recover)
- May reduce size too aggressively if max_dd is tight
- The "peak" is a trailing lookback — not a fixed reference
- Hysteresis: once in drawdown, stays small for a while
- Creates a "ceiling" constraint that prevents equity from making new highs quickly

---

## 8. Compound Growth vs Linear Growth Tradeoffs

### 8.1 Key formulas

**Linear (fixed position size):**

```
FinalEquity_linear = StartingCapital + (N × AvgTrade)

Or as a growth rate:

R_linear = (FinalEquity / StartingCapital - 1) / N
```

**Compound (reinvesting profits):**

```
FinalEquity_compound = StartingCapital × (1 + R_avg)^N
```

Where:
- `R_avg` = average return per period as a decimal
- `N` = number of periods

**Crossover point:**

For a system with positive expectancy, compound always beats linear given enough time.

**Compound vs linear ratio:**

```
Ratio(N) = (1 + R_avg)^N / (1 + N × R_avg)
```

For small `R_avg`, linear ≈ compound for many periods. For large `R_avg`, compound dominates quickly.

### 8.2 Python pseudocode

```python
import numpy as np
from typing import List

def simulate_growth(
    trades_r: List[float],
    initial_capital: float = 100000.0,
    risk_fraction: float = 0.01,
    sizing_method: str = 'compound',
) -> np.ndarray:
    """
    Compare compound vs linear equity curves from trade R-multiples.

    Parameters
    ----------
    trades_r       : list of R-multiples (+2.0 = 2R winner, -1.0 = 1R loser)
    initial_capital: Starting equity
    risk_fraction  : Fraction risked per trade (for compound sizing)
    sizing_method  : 'compound' or 'linear'

    Returns
    -------
    np.ndarray of equity values
    """
    equity = float(initial_capital)
    curve = [equity]
    fixed_risk_amount = equity * risk_fraction  # for linear sizing

    for r in trades_r:
        if sizing_method == 'compound':
            # Risk fraction of current equity
            risk_amount = equity * risk_fraction
        elif sizing_method == 'linear':
            # Risk fixed dollar amount
            risk_amount = fixed_risk_amount
        else:
            raise ValueError(f"Unknown method: {sizing_method}")

        pnl = risk_amount * r
        equity += pnl
        # Never go negative
        equity = max(equity, 0.0)
        curve.append(equity)

    return np.array(curve)


def compare_compound_vs_linear(
    trades_r: List[float],
    initial_capital: float = 100000.0,
    risk_fraction: float = 0.01,
) -> dict:
    """
    Compare compound vs linear growth for a sequence of trades.
    """
    comp = simulate_growth(trades_r, initial_capital, risk_fraction, 'compound')
    lin = simulate_growth(trades_r, initial_capital, risk_fraction, 'linear')

    n = len(trades_r)
    comp_final = comp[-1]
    lin_final = lin[-1]

    comp_cagr = (comp_final / initial_capital) ** (1.0 / max(n, 1)) - 1.0
    lin_ror = (lin_final / initial_capital - 1.0) / max(n, 1)

    comp_dd = _max_drawdown(comp)
    lin_dd = _max_drawdown(lin)

    return {
        'compound_final': comp_final,
        'linear_final': lin_final,
        'compound_cagr_per_trade': comp_cagr,
        'linear_return_per_trade': lin_ror,
        'compound_max_dd': comp_dd,
        'linear_max_dd': lin_dd,
        'compound_advantage': comp_final / lin_final if lin_final > 0 else float('inf'),
        'trades': n,
        'win_rate': sum(1 for r in trades_r if r > 0) / max(len(trades_r), 1),
        'avg_r': np.mean(trades_r) if trades_r else 0.0,
    }


def _max_drawdown(equity_curve: np.ndarray) -> float:
    if len(equity_curve) < 2:
        return 0.0
    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = (peaks - equity_curve) / peaks
    return float(np.max(drawdowns))


def breakeven_compare(
    avg_r: float,
    win_rate: float,
    risk_per_trade: float,
    max_trades: int = 1000,
) -> dict:
    """
    Show how many trades until compound dominates linear by a given factor.
    """
    trade_sequence = []
    for i in range(max_trades):
        r = avg_r if np.random.random() < win_rate else -1.0
        trade_sequence.append(r)

    result = compare_compound_vs_linear(trade_sequence, 100000.0, risk_per_trade)

    # Find crossover point
    comp = simulate_growth(trade_sequence, 100000.0, risk_per_trade, 'compound')
    lin = simulate_growth(trade_sequence, 100000.0, risk_per_trade, 'linear')

    crossover_trade = None
    for i in range(len(comp)):
        if comp[i] > lin[i]:
            crossover_trade = i
            break

    result['crossover_trade'] = crossover_trade
    return result
```

### 8.3 Key tradeoffs

| Aspect | Compound (reinvest) | Linear (fixed lot) |
|--------|--------------------|--------------------|
| Long-term final equity | Much higher | Lower |
| Drawdown magnitude | Larger (bigger positions near peak) | Smaller (constant risk) |
| Recovery after drawdown | Slower (smaller equity → smaller size) | Faster (constant $ risk) |
| Sequence of returns risk | YES — large loss early is devastating | No — same risk regardless of order |
| Account growth for small accounts | Good — grows when it can | Slower — never accelerates |
| Drawdown during losing streak | Decreases (position shrinks with equity) | Stays constant (bad — can lose more) |
| Psychological | Harder — more volatile equity swings | Easier — smoother equity curve |
| Mathematical growth rate | Geometric (exponential) | Arithmetic (linear) |
| Terminal value formula | `C × (1 + r)^N` | `C + N × r × C` |
| Optimal for | Long time horizons, stable edge | Short horizons, risk-averse |

### 8.4 When to use each

**Use compound growth when:**
- Time horizon is long (years)
- Edge is stable and well-estimated
- You can tolerate 20–40% drawdowns
- Account is small relative to opportunity
- Strategy has positive Sharpe > 0.5

**Use linear growth (or partial compounding) when:**
- Strategy is new with unknown reliability
- Account is large and preservation matters more than growth
- You withdraw profits regularly (treating it as income)
- The strategy has a "capacity limit" (cannot scale beyond certain size)
- You want to smooth the equity curve

**Blended approach:**

```python
def blended_sizer(
    account_equity: float,
    original_capital: float,
    risk_pct_compound: float = 0.01,
    risk_pct_linear: float = 0.005,
    blend: float = 0.5,
) -> float:
    """
    Blend compound and linear sizing.

    blend = 0.0 → pure linear (fixed fraction of original capital)
    blend = 1.0 → pure compound (fraction of current equity)
    """
    compound_risk = account_equity * risk_pct_compound
    linear_risk = original_capital * risk_pct_linear
    return compound_risk * blend + linear_risk * (1.0 - blend)
```

### 8.5 The "Equity Curve" trap

Compounding amplifies both gains AND losses. A 50% drawdown requires a 100% gain to recover — so drawdown avoidance is actually THE most important factor for long-term compound growth.

```
RecoveryGain = Drawdown / (1 - Drawdown)
```

| Drawdown | Gain needed to recover |
|----------|----------------------|
| 10%      | 11% |
| 20%      | 25% |
| 30%      | 43% |
| 40%      | 67% |
| 50%      | 100% |
| 60%      | 150% |
| 70%      | 233% |
| 80%      | 400% |
| 90%      | 900% |

This asymmetry is the single most important argument for conservative position sizing. Avoiding large drawdowns is more important than maximizing short-term growth.

**Source**

| Author | Work | Year |
|--------|------|------|
| Ralph Vince | All three books | 1990–2007 |
| Van Tharp | "Trade Your Way to Financial Freedom" | 2007 |
| Robert Pardo | "The Evaluation and Optimization…" Ch. 7–9 | 2008 |
| William Bernstein | "The Four Pillars of Investing" | 2002 |
| AQR Capital | Papers on geometric vs arithmetic return | Various |

---

## Summary: Choosing a Sizing Method

| Method | Best for | Avoid when |
|--------|----------|------------|
| Full Kelly | Theoretical benchmark only | Real trading (too aggressive) |
| Half/Quarter Kelly | High-confidence strategies, >1 Sharpe | Low edge, new systems |
| Optimal f | Research / backtesting comparison | Deployed auto trading (overfits) |
| Fixed Fractional (1% rule) | Most practical for auto trading | High-frequency (noise) |
| Fixed Ratio (Ryan Jones) | Growing accounts, scaling up | Small accounts, large volatility |
| Drawdown-based | All strategies — add as overlay | When already using very tight risk |
| Risk-of-ruin-constrained | As upper bound / sanity check | As primary sizer (wastes capital) |

**Recommended default for automated trading (practical):**

```
1. Base: Fixed Fractional at 0.5–1.0% per trade
2. Drawdown adjustment: Reduce linearly from 100% to 25% over 0% → 25% drawdown
3. Cap: Never exceed Quarter Kelly
4. Shutdown: Stop trading if drawdown exceeds 30%
5. Re-enter: Resume at 50% of base size, only after 10% above trough
```

---

## Complete Python reference implementation

```python
# position_sizing.py — Complete reference for automated trading systems

import numpy as np
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class PositionSizingResult:
    fraction: float      # fraction of capital to risk
    size_units: int      # number of units to trade
    risk_amount: float   # dollar amount at risk
    method: str          # which method was used


class PositionSizer:
    """
    Unified position sizer with multiple methods.
    """

    def __init__(self,
                 method: str = 'fixed_fractional',
                 base_risk: float = 0.01,
                 max_risk: float = 0.02,
                 max_drawdown: float = 0.25,
                 kelly_fraction: float = 0.25):
        self.method = method
        self.base_risk = base_risk
        self.max_risk = max_risk
        self.max_drawdown = max_drawdown
        self.kelly_fraction = kelly_fraction
        self.peak_equity = None
        self.trade_history = []

    def __call__(self,
                 account_equity: float,
                 entry_price: float,
                 stop_loss: float,
                 value_per_unit: float = 1.0,
                 trade_stats: Optional[dict] = None) -> PositionSizingResult:

        # 1. Determine base risk fraction
        if self.method == 'fixed_fractional':
            f = self.base_risk

        elif self.method == 'kelly' and trade_stats:
            f = kelly_fractional(
                trade_stats.get('win_rate', 0.0),
                trade_stats.get('avg_win', 0.0),
                trade_stats.get('avg_loss', 0.0),
                self.kelly_fraction
            )
            f = max(f, self.base_risk * 0.5)  # floor

        elif self.method in ('optimal_f', 'vince') and trade_stats:
            result = optimal_f(np.array(trade_stats.get('r_multiples', [])))
            f = result['f_opt'] * 0.25  # Quarter optimal f
            f = min(f, self.max_risk)

        else:
            f = self.base_risk

        # 2. Apply drawdown reduction
        if self.peak_equity is None:
            self.peak_equity = account_equity
        self.peak_equity = max(self.peak_equity, account_equity)

        dd = max(0.0, (self.peak_equity - account_equity) / self.peak_equity)
        if dd >= self.max_drawdown:
            return PositionSizingResult(0.0, 0, 0.0, 'shutdown')

        dd_mult = 1.0 - (dd / self.max_drawdown)
        f *= max(0.25, dd_mult)

        # 3. Cap
        f = min(f, self.max_risk)

        # 4. Calculate position size
        risk_per_unit = abs(entry_price - stop_loss) * value_per_unit
        if risk_per_unit > 0:
            risk_amount = account_equity * f
            units = int(risk_amount / risk_per_unit)
        else:
            units = 0
            risk_amount = 0.0

        return PositionSizingResult(
            fraction=f,
            size_units=units,
            risk_amount=risk_amount,
            method=self.method
        )

    def record_trade(self, r_multiple: float):
        self.trade_history.append(r_multiple)
```

---

## Compiled source references

| # | Author | Title | Year | Key contribution |
|---|--------|-------|------|-----------------|
| 1 | John L. Kelly Jr. | A New Interpretation of Information Rate | 1956 | Kelly Criterion |
| 2 | Edward O. Thorp | Beat the Dealer | 1962 | Applied Kelly to blackjack |
| 3 | Edward O. Thorp | The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market | 2008 | Fractional Kelly |
| 4 | Ralph Vince | Portfolio Management Formulas | 1990 | Optimal f |
| 5 | Ralph Vince | The Mathematics of Money Management | 1992 | Drawdown constraints |
| 6 | Ralph Vince | The Handbook of Portfolio Mathematics | 2007 | Geometric mean strategies |
| 7 | Ryan Jones | The Trading Game | 1999 | Fixed Ratio sizing |
| 8 | Nauzer Balsara | Money Management Strategies for Futures Traders | 1992 | Practical risk of ruin |
| 9 | Van K. Tharp | Trade Your Way to Financial Freedom | 2007 | Position sizing strategies |
| 10 | Robert Pardo | The Evaluation and Optimization of Trading Strategies | 2008 | Testing with position sizing |
| 11 | William Feller | An Introduction to Probability Theory and Its Applications | 1968 | Gambler's ruin (risk of ruin) |
| 12 | Paul Samuelson | Why We Should Not Make Mean Log of Wealth Big Though Years to Act Are Long | 1971 | Critique of Kelly |
| 13 | A. W. Lo & M. T. MacKinlay | A Non-Random Walk Down Wall Street | 1999 | Non-independence of returns |
| 14 | Howard Marks | The Most Important Thing | 2011 | Risk management philosophy |
| 15 | Victor Haghani | Why Many Investors Fail: The Kelly Criterion | 2015 | Practical Kelly usage |

---

*Documento generado para referencia técnica. No constituye asesoría financiera. Probar cualquier método en backtesting y forward testing antes del uso real.*
