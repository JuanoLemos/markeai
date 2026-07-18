# Mavis — Server caido. Instrucciones de reinicio.

El servidor esta caido. El tray crasheo y no se levanto solo porque no estas usando el watchdog.

## 1. Matar todo (PowerShell como Administrador)

```powershell
taskkill /f /im python.exe
```

## 2. Arrancar con watchdog (auto-restart si crashea)

```powershell
cd C:\xampp\htdocs\MarketAI
tray_watchdog.bat
```

Deja esa ventana abierta. Si el tray crashea, el .bat lo relanza en 10 segundos.

**IMPORTANTE:** NO uses `python tray_app.py` directo. Usa siempre `tray_watchdog.bat`. Eso mantiene el servidor vivo aunque python crashee.
