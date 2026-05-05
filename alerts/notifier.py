import os
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Notifier:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
        self._is_placeholder = lambda v: not v or v in ("...", "tu-key-aqui") or v.endswith("/...")
        self.telegram_enabled = all([self.telegram_token, self.telegram_chat_id]) and not any(self._is_placeholder(v) for v in [self.telegram_token, self.telegram_chat_id])
        self.discord_enabled = bool(self.discord_webhook) and not self._is_placeholder(self.discord_webhook)

    def send_trade_entry(self, trade: dict) -> bool:
        msg = (
            f"🟢 ENTRADA - {trade.get('market', '?').upper()}\n"
            f"Ticker: {trade.get('ticker', '?')}\n"
            f"Señal: {trade.get('signal', '?')}\n"
            f"Precio: ${trade.get('entry_price', '?')}\n"
            f"Tamaño: ${trade.get('size_usd', 0):.2f}\n"
            f"Confianza: {trade.get('confidence', '?')}/100\n"
            f"SL: {trade.get('stop_loss_pct', '?')}% | TP: {trade.get('take_profit_pct', '?')}%"
        )
        return self._send(msg)

    def send_trade_exit(self, result: dict) -> bool:
        pnl = result.get("pnl_pct", 0)
        emoji = "✅" if pnl > 0 else "❌"
        msg = (
            f"{emoji} SALIDA - {result.get('market', '?').upper()}\n"
            f"Ticker: {result.get('ticker', '?')}\n"
            f"Señal: {result.get('signal', '?')}\n"
            f"Entrada: ${result.get('entry_price', '?')} → Salida: ${result.get('exit_price', '?')}\n"
            f"PnL: ${result.get('pnl_usd', 0):.2f} ({pnl}%)\n"
            f"Razón: {result.get('reason', '?')}"
        )
        return self._send(msg)

    def send_error(self, error_msg: str) -> bool:
        msg = f"⚠️ ERROR\n{error_msg}"
        return self._send(msg)

    def send_daily_summary(self, summary: dict) -> bool:
        msg = (
            f"📊 RESUMEN DIARIO\n"
            f"Balance: ${summary.get('balance', 0):.2f}\n"
            f"PnL Hoy: ${summary.get('daily_pnl', 0):.2f}\n"
            f"PnL Total: ${summary.get('total_pnl', 0):.2f} ({summary.get('total_pnl_pct', 0)}%)\n"
            f"Win Rate: {summary.get('win_rate', 0)}%\n"
            f"Trades: {summary.get('total_trades', 0)}"
        )
        return self._send(msg)

    def _send(self, message: str) -> bool:
        sent = False
        if self.telegram_enabled:
            sent = self._send_telegram(message) or sent
        if self.discord_enabled:
            sent = self._send_discord(message) or sent
        return sent

    def _send_telegram(self, message: str) -> bool:
        if not self.telegram_enabled:
            return False
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            resp = requests.post(url, json={
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
            }, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def _send_discord(self, message: str) -> bool:
        if not self.discord_enabled:
            return False
        try:
            import requests
            resp = requests.post(
                self.discord_webhook,
                json={"content": message},
                timeout=10,
            )
            return resp.status_code in (200, 204)
        except Exception:
            return False
