# GUIA_DEPLOY — Despliegue 24/7 con Docker v1.0

Guía para ejecutar MarketAI 24/7 en una notebook (Windows) o VPS (Linux) usando Docker.

---

## Requisitos

| Componente | Notebook (Windows) | VPS (Linux) |
|---|---|---|
| Docker | Docker Desktop | Docker Engine + docker compose plugin |
| Git | git for Windows | git |
| Memoria | Mín 4GB libre | Mín 2GB |
| Disco | 5GB libre | 2GB libre |

## Setup inicial (1 vez)

### 1. Clonar el repositorio

```powershell
cd C:\
git clone https://github.com/JuanoLemos/markeai.git
cd MarketAI
```

### 2. Configurar API keys

Copiar `.env` con las claves reales desde tu máquina de desarrollo. El archivo `.env` no está en git (está en `.gitignore`).

```powershell
# Crear .env desde la plantilla
copy .env.example .env
# Editar con tus claves: DeepSeek, Alpaca, Telegram, etc.
notepad .env
```

### 3. Iniciar servicios

```powershell
docker compose up -d --build
```

### 4. Verificar

```powershell
docker compose ps
```

Deberías ver 2 servicios con estado `Up`:
- `marketai-orch` — Orchestrator (loop 24/7)
- `marketai-dash` — Dashboard web

### 5. Abrir dashboard

`http://localhost:8050`

## Actualizar el sistema

Cada vez que haya cambios en GitHub:

```powershell
deploy.bat
```

Esto hace:
1. `git pull origin master`
2. `docker compose down`
3. `docker compose up -d --build`

## Comandos útiles

```powershell
# Ver logs del orquestador
docker compose logs -f orchestrator

# Ver logs del dashboard
docker compose logs -f dashboard

# Reiniciar el orquestador (sin rebuild)
docker compose restart orchestrator

# Detener todo
docker compose down

# Reconstruir sin cache
docker compose build --no-cache
docker compose up -d
```

## Docker Desktop — Auto-start en Windows

1. Abrir Docker Desktop → Settings → General
2. Activar "Start Docker Desktop when you sign in to your computer"
3. Windows minimiza Docker Desktop al tray automáticamente

## Migración a VPS (futuro)

El mismo `docker-compose.yml` funciona sin cambios. Para producción agregar:

1. `nginx` como reverse proxy delante del dashboard (puerto 80/443)
2. `certbot` para HTTPS con Let's Encrypt
3. `UFW` para firewall
4. Backup automático del volumen `marketai_data`

## Arquitectura

```
                    docker-compose.yml
┌────────────────────────────────────────────┐
│  marketai-orch       marketai-dash          │
│  :8050                                       │
│  loop 24/7           Flask dashboard        │
│  healthcheck          healthcheck            │
│  restart: unless-stop  restart: unless-stop  │
│       ▲                     ▲               │
│       └───── marketai_data ──┘               │
│             (DB, cache compartido)           │
└────────────────────────────────────────────┘
```

## Archivos relacionados

- `Dockerfile` — Imagen base Python 3.12
- `docker-compose.yml` — Definición de servicios
- `docker-compose.yml` — Servicios y volúmenes
- `healthcheck.py` — Healthchecks
- `deploy.bat` / `deploy.sh` — Scripts de deploy
- `.dockerignore` — Exclusiones del contexto de build
