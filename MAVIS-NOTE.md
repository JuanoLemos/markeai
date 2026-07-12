# Mavis — Chequeo de server (2026-07-12)

Hacé `git pull` en la notebook, ejecutá estos comandos en PowerShell y copiá TODO el resultado en un reply (commit, archivo, o lo que prefieras).

---

## 1. IP actual

```powershell
ipconfig | Select-String "192.168"
```

## 2. ¿Server vivo?

```powershell
curl -s http://localhost:8050/api/health
```

## 3. Procesos activos

```powershell
Get-Process python -ErrorAction SilentlyContinue | Select Id, ProcessName, StartTime
```

## 4. Posiciones abiertas

```powershell
curl -s http://localhost:8050/api/positions
```

## 5. Estado del watchdog / debug

```powershell
curl -s http://localhost:8050/api/debug
```
