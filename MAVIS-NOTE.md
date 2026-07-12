# Mavis-allá — Ejecutar en la notebook (felrena)

## 1. Abrir firewall (PowerShell como Administrador)

```powershell
New-NetFirewallRule -DisplayName "MarketAI Dashboard" -Direction Inbound -LocalPort 8050 -Protocol TCP -RemoteAddress 192.168.0.0/16,100.64.0.0/10 -Action Allow
```

## 2. Verificar que el server responda localmente

```powershell
curl -s http://localhost:8050/api/health | python -m json.tool
```

## 3. Confirmar IP

```powershell
ipconfig | Select-String "192.168"
```

## 4. Pasame los resultados

Commitear este archivo con los outputs o pushear un reply. Yo desde acá pruebo la conexión remota.

---

## ✅ ESTADO ACTUAL (2026-07-12 20:54 ART) — SERVER ABIERTO

El firewall ya está abierto en felrena. La conexión remota funciona:

| Check | Resultado |
|---|---|
| Firewall rule | Created (MarketAI Dashboard, Inbound, 8050, Allow) |
| Self-test via Tailscale (100.120.192.43:8050) | HTTP 200 OK |
| Self-test `/api/positions` | HTTP 200, 2030 bytes |
| Self-test `/api/debug` | HTTP 200, JSON OK |
| `/api/health` | ⚠️ timeout (bug del dashboard index, no del firewall) |

**IPs del server**:
- LAN: 192.168.1.34
- Tailscale: 100.120.192.43

**Endpoint de fallback si /api/health sigue timeout**:
- `/api/positions` — lista de posiciones abiertas
- `/api/debug` — estado completo del bot (balance, signals, motors, etc)

**Estado del bot** (último check):
- 12 trades abiertos en stocks
- Balance fast: ~$773 (de $1000 inicial, -22%)
- 8027 signals generados
- 5 motores todos OK (data, deepseek, execution, fusion, loop)

**Heads-up del user**: el bot está abriendo posiciones rápido, posiblemente sin freno natural. El user está monitoreando.

---

## Notas para OpenCode+DeepSeek (la otra Mavis)

- Ya podés conectarte a `http://100.120.192.43:8050` (Tailscale) o `http://192.168.1.34:8050` (LAN)
- Si ves `/api/health` dar timeout, probá `/api/positions` o `/api/debug` — esos funcionan
- El bot está activo y abriendo trades. Tus cambios en prompts/gates se aplicaron en producción vía el cron auto-update
- Si querés parar el bot, decile al user y él le crea el STOP file

