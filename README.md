# MarketAI

Sistema de trading automatizado multi-capa impulsado por DeepSeek AI.

## Arquitectura

```
Datos → 9 Analizadores → Fusión → DeepSeek → Ejecución → Journal
```

3 mercados: Polymarket, Forex, Acciones. Perfiles duales: Normal + Fast.

## Inicio rápido

```powershell
venv\Scripts\activate
python orchestrator.py --mode once          # Una iteración
python orchestrator.py --mode loop          # 24/7
.\dashboard.bat                             # Dashboard web :8050
.\tray_app.bat                              # System tray (recomendado)
```

Ver `doc/guias/` para instalación, configuración y uso detallado.

## Tests

```powershell
python -m pytest tests/ -v                 # 95 tests
```

## Licencia

Uso personal. No apto para producción real sin validación previa.
