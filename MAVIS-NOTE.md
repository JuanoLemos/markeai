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
