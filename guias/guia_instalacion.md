# Guía de Instalación

## MarketAI - Sistema de Trading Multi-Capa

---

## Requisitos del Sistema

| Componente | Requisito Mínimo |
|------------|------------------|
| **Python** | 3.10+ (probado en 3.14.0) |
| **OS** | Windows 10/11, Linux, macOS |
| **RAM** | 4 GB (8 GB recomendado) |
| **Disco** | 500 MB libres |
| **Red** | Conexión a Internet estable |
| **DeepSeek** | API key activa (obligatoria) |

---

## Paso 1: Verificar Python

```bash
python --version
# Debe mostrar: Python 3.10.0 o superior
```

Si no está instalado: https://www.python.org/downloads/

---

## Paso 2: Crear Entorno Virtual

```bash
# Windows
cd C:\xampp\htdocs\MarketAI
python -m venv venv
venv\Scripts\activate

# Linux/macOS
cd /ruta/a/MarketAI
python3 -m venv venv
source venv/bin/activate
```

---

## Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verificar instalación
```bash
python -c "import yfinance; import pandas; import numpy; import flask; import pystray; import pyarrow; print('Dependencias OK')"
```

---

## Paso 4: Configurar Variables de Entorno

```bash
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS
```

Editar `.env` con tus keys:
```ini
DEEPSEEK_API_KEY=sk-tu-api-key-aqui     # Obligatoria
NEWSAPI_KEY=tu-key                       # Opcional (con RSS fallback)
POLYSCAN_API_KEY=tu-key                  # Opcional
```

---

## Paso 5: Verificar Instalación

```bash
# Ejecutar tests (95 tests)
python -m pytest tests/ -v

# Probar una iteración
python orchestrator.py --mode once --market stocks

# Ver log
Get-Content orchestrator.log -Tail 10
```

---

## Instalación Completa → Componentes Adicionales

### Dashboard Web
```bash
python dashboard.py
# Abrir http://localhost:8050
```

### System Tray (recomendado)
```bash
python tray_app.py
# Icono $ en bandeja del sistema
```

### .bat Lanzadores (Windows)
- `dashboard.bat` — Dashboard web
- `tray_app.bat` — System tray (loop + dashboard)
- `loop.bat` — Loop 24/7 en consola

---

## Solución de Problemas

### Error: `ModuleNotFoundError: No module named '...'`
```bash
pip install -r requirements.txt
```

### Error: `UnicodeDecodeError` en config.yaml
El archivo contiene caracteres Unicode (═). Asegurate de abrirlo con encoding UTF-8.

### Error: Polymarket retorna 0 mercados
El DNS bypass está integrado. Si sigue fallando, verificar conectividad a Internet.

### Error: Etherscan API timeout
Aumentar `timeout` si la conexión es lenta. El default es 20s.

### Error: pyarrow not found
```bash
pip install pyarrow
```
Necesario para caché parquet de yfinance.

### Advertencia: CRLF
Es normal en Windows. Git maneja la conversión automáticamente.
