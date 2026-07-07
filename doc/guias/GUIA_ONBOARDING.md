# GUIA_ONBOARDING — Guia de onboarding v1.0

Guia de inicio rapido para nuevos desarrolladores de MarketAI.

## Requisitos

- Python 3.10 o superior
- PowerShell 5.1 (Windows) o bash (Linux/Mac)
- Git
- Acceso a GitHub

## Primeros pasos

1. Clonar el repositorio:
   ```powershell
    git clone https://github.com/JuanoLemos/markeai.git
   cd MarketAI
   ```

2. Crear y activar entorno virtual:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```powershell
   cp .env.example .env
   # Editar .env con tus API keys (DeepSeek, opcional)
   ```

5. Verificar instalacion:
   ```powershell
   python -m pytest tests/ -v
   ```

## Donde encontrar las cosas

| Que buscas | Donde |
|------------|-------|
| Loop principal | `orchestrator.py` en la raiz |
| Dashboard Flask | `dashboard.py` y `templates/` |
| Base de datos | `data/database.py` (SQLite) |
| Motor de decision | `engine/decider.py` (DeepSeek) |
| Analizadores | `analyzers/` (9 modulos) |
| Ejecucion | `execution/` (broker, riesgo, entradas) |
| Estrategias | `strategies/` + journal |
| Documentacion | `doc/` (guias, arch, mecanicas) |

## Ejecutar el proyecto

```powershell
# Una iteracion del loop
python orchestrator.py --mode once

# Loop continuo
python orchestrator.py --mode loop

# Dashboard web
.\dashboard.bat

# System tray
.\tray_app.bat
```

## Archivos relacionados

- `AGENTS.md` — Mapeo completo de rutas y convenciones
- `doc/guias/GUIA_DE_CONTRIBUCION.md` — Como contribuir
- `doc/arch/bitacora.md` — Bitacora de sesiones
