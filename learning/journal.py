from pathlib import Path


class TradeJournal:
    def __init__(self, journal_path: str = None):
        if journal_path is None:
            journal_path = str(Path(__file__).parent.parent / "strategies" / "trade_journal.md")
        self.journal_path = journal_path
        Path(journal_path).parent.mkdir(exist_ok=True)
        if not Path(journal_path).exists():
            with open(journal_path, "w") as f:
                f.write("# MarketAI - Trade Journal\n\n")
                f.write("## Diario automático de operaciones\n\n")
                f.write("| # | Fecha | Mercado | Ticker | Señal | Entrada | Salida | PnL% | Razón |\n")
                f.write("|---|---|---|---|---|---|---|---|---|\n")

    def record_trade(self, trade_result: dict):
        if not trade_result:
            return
        with open(self.journal_path, "a") as f:
            entry_time = trade_result.get("entry_time", "")[:19]
            exit_time = trade_result.get("exit_time", "")[:19]
            pnl_pct = trade_result.get("pnl_pct", 0)
            emoji = "[WIN]" if pnl_pct > 0 else "[LOSS]" if pnl_pct < 0 else "[FLAT]"
            f.write(
                f"| {emoji} | {exit_time} | {trade_result.get('market', '?')} "
                f"| {trade_result.get('ticker', '?')} | {trade_result.get('signal', '?')} "
                f"| {trade_result.get('entry_price', '?')} | {trade_result.get('exit_price', '?')} "
                f"| {pnl_pct}% | {trade_result.get('reason', '?')} |\n"
            )

    def generate_summary(self) -> str:
        return self._read_journal()

    def _read_journal(self) -> str:
        try:
            with open(self.journal_path) as f:
                return f.read()
        except FileNotFoundError:
            return ""
