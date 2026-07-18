"""
engine/prompt_memory.py — Prompt memory and lessons from past trades.

Técnica 1: Inject past trade outcomes into the prompt.
Técnica 2: Track rule performance per ticker.
Técnica 3: Generate critiques after losses.

When no memory is available, returns empty strings gracefully.
"""
from datetime import datetime, timezone


class PromptMemory:
    def __init__(self, db):
        self.db = db

    def record_lesson(self, trade: dict):
        """After trade closes: save outcome as a structured lesson."""
        ticker = trade.get("ticker", "?")
        signal = trade.get("signal", "?")
        pnl_pct = trade.get("pnl_pct", 0)
        confidence = trade.get("confidence", 0)
        outcome = "win" if pnl_pct > 0 else "loss"

        # Técnica 1: lesson text
        lesson = f"{ticker} {signal}: sign was {signal}, outcome={outcome} ({pnl_pct:+.1f}%)"

        # Técnica 3: critique for losses
        critique = ""
        if outcome == "loss" and confidence > 50:
            critique = f"Confidence was {confidence}% but trade lost — possible overconfidence in this setup"

        conn = self.db._get_conn()
        conn.execute(
            """INSERT INTO prompt_memory
               (ticker, signal, confidence, outcome, pnl_pct, lesson, critique)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ticker, signal, confidence, outcome, round(pnl_pct, 2), lesson, critique),
        )
        conn.commit()
        conn.close()

    def get_lessons(self, ticker: str, limit: int = 3) -> list:
        """Last N lessons for a specific ticker — injected into the prompt."""
        conn = self.db._get_conn()
        rows = conn.execute(
            """SELECT lesson, outcome, pnl_pct, critique FROM prompt_memory
               WHERE ticker=? ORDER BY id DESC LIMIT ?""",
            (ticker, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    def get_rule_win_rate(self, ticker: str, days: int = 30) -> dict:
        """Tecnica 2: win rate per ticker over last N days."""
        conn = self.db._get_conn()
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN outcome='win' THEN 1 ELSE 0 END) as wins"
            " FROM prompt_memory WHERE ticker=? AND timestamp > datetime('now', ?)",
            (ticker, f'-{days} days'),
        ).fetchone()
        conn.close()
        total = row["total"] or 0
        wins = row["wins"] or 0
        return {"ticker": ticker, "total": total, "wins": wins,
                "win_rate": round(wins / total * 100, 1) if total else 0}
