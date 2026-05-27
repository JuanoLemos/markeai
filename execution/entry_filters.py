"""
Entry Filters — Validación de horarios, correlación y condiciones previas a la apertura de una posición.
"""


SESSIONS_FOREX = {
    "london": {"start": 7, "end": 16},
    "new_york": {"start": 13, "end": 22},
    "overlap": {"start": 13, "end": 16},
    "sydney": {"start": 22, "end": 7},
    "tokyo": {"start": 0, "end": 9},
}

FOREX_CORRELATION = {
    "EURUSD=X": {"GBPUSD=X": 0.85, "USDCHF=X": -0.90, "EURCHF=X": 0.80},
    "GBPUSD=X": {"EURUSD=X": 0.85, "USDCHF=X": -0.80, "EURGBP=X": -0.70},
    "USDJPY=X": {"USDCAD=X": 0.60, "AUDUSD=X": -0.50},
    "USDCAD=X": {"USDJPY=X": 0.60, "AUDUSD=X": -0.70},
    "AUDUSD=X": {"USDCAD=X": -0.70, "NZDUSD=X": 0.80},
    "EURCHF=X": {"EURUSD=X": 0.80, "USDCHF=X": -0.85},
}

STOCK_CORRELATION = {
    "AAPL": {"MSFT": 0.78, "GOOGL": 0.75, "AMZN": 0.72, "QQQ": 0.85, "SPY": 0.70},
    "MSFT": {"AAPL": 0.78, "GOOGL": 0.80, "AMZN": 0.70, "QQQ": 0.82, "SPY": 0.72},
    "GOOGL": {"AAPL": 0.75, "MSFT": 0.80, "AMZN": 0.65, "QQQ": 0.78, "SPY": 0.68},
    "AMZN": {"AAPL": 0.72, "MSFT": 0.70, "GOOGL": 0.65, "QQQ": 0.75, "SPY": 0.65},
    "TSLA": {"QQQ": 0.60, "SPY": 0.55},
}


def session_hours(market: str, utc_hour: int = None) -> bool:
    """Valida si el horario actual es apto para operar en el mercado indicado.
    
    Args:
        market: 'forex', 'stocks', 'polymarket'
        utc_hour: hora UTC (0-23). Si None, usa hora actual.
    
    Returns:
        True si se puede operar, False si está fuera de horario.
    """
    from datetime import datetime, timezone
    if utc_hour is None:
        utc_hour = datetime.now(timezone.utc).hour

    if market == "polymarket":
        return True

    if market == "forex":
        return (7 <= utc_hour < 16) or (13 <= utc_hour < 22)

    if market == "stocks":
        return 14 <= utc_hour < 21  # 09:30-16:00 ET ≈ 14:30-21:00 UTC

    return True


def correlation_check(open_positions: list, new_market: str, new_ticker: str, new_signal: str) -> bool:
    """Verifica que la nueva posición no esté correlacionada con posiciones abiertas.
    
    Args:
        open_positions: lista de dicts con market, ticker, signal
        new_market: mercado de la nueva posición
        new_ticker: ticker de la nueva posición
        new_signal: 'LONG' o 'SHORT'
    
    Returns:
        True si la nueva posición es aceptable (pasa el filtro)
        False si está bloqueada por correlación
    """
    corr_map = FOREX_CORRELATION if new_market == "forex" else STOCK_CORRELATION if new_market == "stocks" else {}

    for pos in open_positions:
        if pos["market"] != new_market:
            continue
        if pos["signal"] != new_signal:
            continue
        if pos["ticker"] == new_ticker:
            continue
        pair_corr = corr_map.get(pos["ticker"], {}).get(new_ticker, 0)
        if abs(pair_corr) >= 0.80:
            return False
    return True
