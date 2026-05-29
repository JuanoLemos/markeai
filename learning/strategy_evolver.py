from datetime import datetime, timezone
from pathlib import Path


class StrategyEvolver:
    def __init__(self, strategy_path: str = None):
        if strategy_path is None:
            strategy_path = str(Path(__file__).parent.parent / "strategies" / "master_strategy.md")
        self.strategy_path = strategy_path
        Path(strategy_path).parent.mkdir(exist_ok=True)

    def evolve(self, trade_history: list, performance: dict) -> str:
        if len(trade_history) < 5:
            return "not_enough_trades"
        wins = [t for t in trade_history if t.get("pnl_usd", 0) > 0]
        losses = [t for t in trade_history if t.get("pnl_usd", 0) <= 0]
        suggestions = []
        if wins and losses:
            win_avg_return = sum(t.get("pnl_pct", 0) for t in wins) / len(wins)
            loss_avg_return = sum(t.get("pnl_pct", 0) for t in losses) / len(losses)
            if abs(win_avg_return) < abs(loss_avg_return) * 1.5:
                suggestions.append("- ⚠️ Las pérdidas promedio son mayores que las ganancias. Considera reducir posición o ajustar stop-loss.")
        strategies_used = {}
        for t in trade_history:
            strat = t.get("strategy_used", "unknown")
            if strat not in strategies_used:
                strategies_used[strat] = {"wins": 0, "losses": 0, "total_pnl": 0}
            if t.get("pnl_usd", 0) > 0:
                strategies_used[strat]["wins"] += 1
            else:
                strategies_used[strat]["losses"] += 1
            strategies_used[strat]["total_pnl"] += t.get("pnl_usd", 0)
        best_strat = None
        best_win_rate = 0
        for strat, stats in strategies_used.items():
            total = stats["wins"] + stats["losses"]
            if total >= 3:
                wr = stats["wins"] / total
                if wr > best_win_rate:
                    best_win_rate = wr
                    best_strat = strat
        if best_strat and best_win_rate > 0.6:
            suggestions.append(f"- ✅ La estrategia '{best_strat}' tiene {best_win_rate*100:.0f}% win rate. Considera darle más peso.")
        self._update_strategy_md(suggestions, performance, strategies_used)
        self._write_skills(strategies_used)
        return "; ".join(suggestions) if suggestions else "no_suggestions"

    def _update_strategy_md(self, suggestions: list, performance: dict, strategies: dict):
        content = "# MarketAI - Master Strategy (Auto-Evolving)\n\n"
        content += f"## Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        content += "---\n\n"
        content += "## Performance General\n\n"
        content += f"- Balance: ${performance.get('balance', 0):.2f}\n"
        content += f"- PnL Total: ${performance.get('total_pnl', 0):.2f} ({performance.get('total_pnl_pct', 0):.1f}%)\n"
        content += f"- Win Rate: {performance.get('win_rate', 0):.1f}%\n"
        content += f"- Trades Totales: {performance.get('total_trades', 0)}\n\n"
        content += "---\n\n"
        content += "## Sugerencias de Mejora\n\n"
        for s in suggestions:
            content += f"{s}\n"
        if not suggestions:
            content += "- Sin sugerencias por ahora (necesitas más trades)\n"
        content += "\n---\n\n"
        content += "## Performance por Estrategia\n\n"
        content += "| Estrategia | Wins | Losses | Win Rate | PnL |\n"
        content += "|---|---|---|---|---|\n"
        for strat, stats in sorted(strategies.items(), key=lambda x: x[1]["total_pnl"], reverse=True):
            total = stats["wins"] + stats["losses"]
            wr = f"{stats['wins']/total*100:.0f}%" if total > 0 else "-"
            content += f"| {strat} | {stats['wins']} | {stats['losses']} | {wr} | ${stats['total_pnl']:.2f} |\n"
        content += "\n---\n\n"
        content += "## Reglas Activas\n\n"
        content += "### Polymarket\n"
        content += "- Entrar cuando order book imbalance > 2:1\n"
        content += "- Salir cuando imbalance < 1.2:1 o evento resuelto\n"
        content += "- Máximo 2 posiciones concurrentes\n\n"
        content += "### Forex\n"
        content += "- Operar en dirección del DXY (DXY ↑ = USD long)\n"
        content += "- Evitar operar 30 min antes/después de noticias macro\n"
        content += "- Timeframes: 1h para entrada, 4h para tendencia\n\n"
        content += "### Acciones\n"
        content += "- Solo LONG en tendencia alcista (EMA50 > EMA200)\n"
        content += "- Post-earnings: esperar 2 velas horarias antes de entrar\n"
        content += "- Salir si VIX > 30 (volatilidad extrema)\n"
        with open(self.strategy_path, "w") as f:
            f.write(content)

    def _write_skills(self, strategies: dict):
        skills_dir = Path(__file__).parent.parent / "skills"
        skills_dir.mkdir(exist_ok=True)
        for strat, stats in strategies.items():
            total = stats["wins"] + stats["losses"]
            if total < 3:
                continue
            wr = f"{stats['wins']/total*100:.0f}%"
            skill = f"# Estrategia: {strat}\n\n"
            skill += f"- Trades: {total}\n"
            skill += f"- Wins: {stats['wins']}\n"
            skill += f"- Losses: {stats['losses']}\n"
            skill += f"- Win Rate: {wr}\n"
            skill += f"- PnL: ${stats['total_pnl']:.2f}\n"
            safe_name = strat.replace("/", "_").replace(" ", "_")
            (skills_dir / f"{safe_name}.md").write_text(skill)
        overview = "# Skills Auto-Generados\n\n"
        overview += "Estrategias con 3+ trades ejecutados.\n\n"
        overview += f"Actualizado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        for strat, stats in sorted(strategies.items(), key=lambda x: x[1]["total_pnl"], reverse=True):
            total = stats["wins"] + stats["losses"]
            if total < 3:
                continue
            overview += f"- [{strat}]({strat.replace('/', '_').replace(' ', '_')}.md): {stats['wins']}/{total} wins, ${stats['total_pnl']:.2f}\n"
        (skills_dir / "README.md").write_text(overview)
