# MarketAI

Sistema de trading automatizado multi-capa impulsado por DeepSeek AI.

## Arquitectura

```
Datos → 7 Analizadores → Fusión → DeepSeek → Ejecución → Journal
```

3 mercados: Polymarket, Forex, Acciones. 5 capas: Recolección, Análisis (7 analizadores), Decisión (DeepSeek), Ejecución (paper/real), Auto-aprendizaje.

## Inicio rápido

```powershell
venv\Scripts\activate
python orchestrator.py --mode once          # Una iteración
python orchestrator.py --mode loop          # 24/7
.\dashboard.bat                             # Dashboard web :8050
.\loop.bat                                  # Loop en consola
```

Ver `guias/` para instalación, configuración y uso detallado.

## Tests

```powershell
python -m pytest tests/ -v
```

## Licencia

Uso personal. No apto para producción real sin validación previa.
