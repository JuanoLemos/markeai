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
    "AAPL": {"MSFT": 0.78, "GOOGL": 0.75, "AMZN": 0.72, "QQQ": 0.85, "SPY": 0.70, "XLK": 0.85, "AAPL.BA": 0.98},
    "MSFT": {"AAPL": 0.78, "GOOGL": 0.80, "AMZN": 0.70, "QQQ": 0.82, "SPY": 0.72, "XLK": 0.88, "MSFT.BA": 0.98},
    "GOOGL": {"AAPL": 0.75, "MSFT": 0.80, "AMZN": 0.65, "QQQ": 0.78, "SPY": 0.68, "XLK": 0.80, "GOOGL.BA": 0.98},
    "AMZN": {"AAPL": 0.72, "MSFT": 0.70, "GOOGL": 0.65, "QQQ": 0.75, "SPY": 0.65, "XLK": 0.78},
    "TSLA": {"QQQ": 0.60, "SPY": 0.55},
    "SPY": {"AAPL": 0.70, "MSFT": 0.72, "GOOGL": 0.68, "AMZN": 0.65, "TSLA": 0.55, "QQQ": 0.85,
            "IVV": 0.99, "EEM": 0.65, "IWM": 0.78, "XLK": 0.82, "XLF": 0.78, "GLD": 0.10, "TLT": -0.30, "VTI": 0.95,
            "VFIAX": 0.99, "FXAIX": 0.99},
    "QQQ": {"AAPL": 0.85, "MSFT": 0.82, "GOOGL": 0.78, "AMZN": 0.75, "TSLA": 0.60, "SPY": 0.85,
            "IVV": 0.82, "IWM": 0.65, "XLK": 0.92, "VTI": 0.85, "VFIAX": 0.82, "FXAIX": 0.82},
    "IVV": {"SPY": 0.99, "QQQ": 0.82, "IWM": 0.75, "VTI": 0.97, "VFIAX": 0.99, "FXAIX": 0.99},
    "IWM": {"SPY": 0.78, "QQQ": 0.65, "IVV": 0.75, "VTI": 0.82, "EEM": 0.60},
    "EEM": {"SPY": 0.65, "IWM": 0.60, "GLD": 0.45, "VTI": 0.68},
    "XLK": {"QQQ": 0.92, "SPY": 0.82, "AAPL": 0.85, "MSFT": 0.88, "GOOGL": 0.80, "AMZN": 0.78, "IVV": 0.83, "VTI": 0.82},
    "XLF": {"SPY": 0.78, "IVV": 0.79, "QQQ": 0.55},
    "GLD": {"SPY": 0.10, "IVV": 0.12, "EEM": 0.45, "TLT": 0.30, "IWM": -0.05},
    "TLT": {"SPY": -0.30, "IVV": -0.28, "GLD": 0.30, "XLF": -0.25, "IWM": -0.15},
    "VTI": {"SPY": 0.95, "IVV": 0.97, "QQQ": 0.85, "IWM": 0.82, "EEM": 0.68, "VFIAX": 0.95, "FXAIX": 0.95},
    "VFIAX": {"SPY": 0.99, "IVV": 0.99, "VTI": 0.95, "QQQ": 0.82, "FXAIX": 0.99},
    "FXAIX": {"SPY": 0.99, "IVV": 0.99, "VTI": 0.95, "QQQ": 0.82, "VFIAX": 0.99},
    "KO.BA": {"SPY": 0.40, "IWM": 0.30},
    "AAPL.BA": {"AAPL": 0.98, "QQQ": 0.70, "XLK": 0.70, "SPY": 0.50},
    "MSFT.BA": {"MSFT": 0.98, "QQQ": 0.70, "XLK": 0.70, "SPY": 0.50},
    "GOOGL.BA": {"GOOGL": 0.98, "QQQ": 0.65, "XLK": 0.65, "SPY": 0.45},
    "WMT.BA": {"SPY": 0.50, "IWM": 0.45},
    "VIST.BA": {"SPY": 0.45, "IWM": 0.40},
    "GGAL.BA": {"SPY": 0.40, "IWM": 0.35},
}


def session_hours(market: str, utc_hour: int = None, profile: str = "normal", ticker: str = "") -> bool:
    """Valida si el horario actual es apto para operar en el mercado indicado.
    
    Args:
        market: 'forex', 'stocks', 'polymarket'
        utc_hour: hora UTC (0-23). Si None, usa hora actual.
        profile: 'normal' o 'fast'. Fast tiene más horas operativas.
        ticker: ticker específico (ej: KO.BA para BYMA).
    
    Returns:
        True si se puede operar, False si está fuera de horario.
    """
    from datetime import datetime, timezone
    if utc_hour is None:
        utc_hour = datetime.now(timezone.utc).hour

    if market == "polymarket":
        return True

    if market == "forex":
        if profile == "fast":
            return 0 <= utc_hour < 22  # Tokyo + London + NY (22h/día)
        return (7 <= utc_hour < 16) or (13 <= utc_hour < 22)  # London + NY (18h/día)

    if market == "stocks":
        if profile == "fast":
            return True  # fast profile: 24/7 (bypass NYSE session para que el bot opere de noche)
        if ticker and ticker.endswith(".BA"):
            return 12 <= utc_hour < 19  # BYMA: 09:00-16:00 ART ≈ 12:00-19:00 UTC
        return 14 <= utc_hour < 21  # 09:30-16:00 ET ≈ 14:30-21:00 UTC

    return True


def correlation_check(open_positions: list, new_market: str, new_ticker: str, new_signal: str, threshold: float = 0.80) -> bool:
    """Verifica que la nueva posición no esté correlacionada con posiciones abiertas.

    Args:
        open_positions: lista de dicts con market, ticker, signal
        new_market: mercado de la nueva posición
        new_ticker: ticker de la nueva posición
        new_signal: 'LONG' o 'SHORT'
        threshold: B-09: correlation threshold (default 0.80; pass config.risk.correlation_threshold)

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
        if abs(pair_corr) >= threshold:
            return False
    return True
