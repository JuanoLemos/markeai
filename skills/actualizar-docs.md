# Skill: actualizar-docs — Sincronización documental completa

## Cuándo cargar
Cuando el usuario pide `/updoc` o "actualizá los docs", o después de cambios que afecten comportamiento documentado.

## Proceso: checklist por tipo de cambio

### 1. Si editaste `config.yaml`
- [ ] `guias/guia_configuracion.md` — actualizar ejemplos de YAML
- [ ] Si agregaste/quitaste un perfil: actualizar sección de perfiles
- [ ] Si cambiaste algún layer weight: actualizar tabla de capas
- [ ] Si agregaste/quitaste un mercado: actualizar sección de mercados

### 2. Si editaste `dashboard.py` (nuevos endpoints)
- [ ] `guias/guia_uso.md` — tabla de páginas/rutas del dashboard
- [ ] Si hay nuevo endpoint que afecte señal/trade: verificar que las templates lo muestren

### 3. Si editaste `execution/` (broker, risk, entry_filters)
- [ ] `guias/guia_trading.md` — referencias de trailing, partial TP, time-exit
- [ ] `guias/guia_configuracion.md` — si cambió SL/TP o filtros por perfil
- [ ] `documentos/checklist.md` — Fase 4 (Ejecución) o Fase 9 (Mejoras)

### 4. Si editaste `analyzers/`
- [ ] `guias/guia_configuracion.md` — tabla de capas (pesos, enabled)
- [ ] `documentos/roadmap.md` — Fase 2 (Analizadores)
- [ ] `documentos/checklist.md` — Fase 2

### 5. Si editaste `tray_app.py`
- [ ] `guias/guia_uso.md` — sección System Tray (menú, tooltip, auto-restart)

### 6. Si cambió el número de tests
- [ ] `README.md` — línea de tests
- [ ] `documentos/checklist.md` — Hito R.4
- [ ] `documentos/roadmap.md` — Métricas de Éxito

### 7. Si editaste `AGENTS.md` u `OPENCODE.md`
- [ ] Verificar que `README.md` aún sea coherente
- [ ] Verificar que `documentos/metodologia.md` refleje el cambio

## Archivos que modifica este skill
- `documentos/checklist.md`
- `documentos/roadmap.md`
- `guias/guia_configuracion.md`
- `guias/guia_uso.md`
- `guias/guia_trading.md`
- `AGENTS.md`
- `README.md`
