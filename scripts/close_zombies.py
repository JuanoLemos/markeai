"""
Cierra los 32 trades 'open' en DB que son zombies del crash del 01/06/2026.
Estos trades no estan en pb_normal.json / pb_fast.json (memoria del broker),
asi que el sistema nunca los cierra por time_exit.

Los marcamos como 'lost_recovery' para distinguirlos de cierres reales.
El PnL se setea en NULL (no se puede reconstruir sin precios historicos).
"""
import sqlite3
from datetime import datetime, timezone

DB = r"C:\xampp\htdocs\MarketAI\data\market.db"
BACKUP = r"C:\xampp\htdocs\MarketAI\data\cache\market.db.pre_recovery"

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM trades WHERE status='open'")
    n_open = cur.fetchone()[0]
    print(f"Trades OPEN antes: {n_open}")

    cur.execute("SELECT id, market, ticker, signal, entry_time FROM trades WHERE status='open' ORDER BY id")
    rows = cur.fetchall()
    print(f"\nA cerrar (muestra primeros 5):")
    for r in rows[:5]:
        print(f"  id={r[0]:>3} {r[1]:<18} {r[2]:<12} {r[3]:<6} {r[4]}")

    ts = datetime.now(timezone.utc).isoformat()
    cur.execute("""
        UPDATE trades
        SET status='closed',
            exit_time=?,
            exit_reason='lost_recovery',
            pnl_usd=NULL,
            pnl_pct=NULL
        WHERE status='open'
    """, (ts,))
    updated = cur.rowcount
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM trades WHERE status='open'")
    n_open_after = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE exit_reason='lost_recovery'")
    n_lost = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed'")
    n_closed = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trades")
    n_total = cur.fetchone()[0]

    print(f"\n--- RESULTADO ---")
    print(f"Trades actualizados: {updated}")
    print(f"OPEN restantes: {n_open_after}")
    print(f"CLOSED total: {n_closed}")
    print(f"lost_recovery total: {n_lost}")
    print(f"Trades totales: {n_total}")
    print(f"Backup en: {BACKUP}")

    conn.close()

if __name__ == "__main__":
    main()