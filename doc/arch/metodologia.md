# Metodología de Proyecto — MarketAI

**Propósito:** Definir cómo se mantiene coherencia, qué se actualiza cuándo, cómo evitar desviaciones.

---

## 1. ESTRUCTURA DE ARCHIVOS — TAXONOMÍA (Diligencia v1.0)

El proyecto sigue la convención **Diligencia v1.0** (ver `DILIGENCIA.md`) que define una estructura estándar para proyectos OpenCode.

### Archivos de Autoridad (Fuentes de Verdad)
Definen el estado ACTUAL del proyecto. **Inmutables excepto decisiones explícitas del Usuario.**

| Archivo | Propósito | Se actualiza cuando... | Frecuencia |
|---|---|---|---|
| `$RM` (raíz) | Tareas, fases, backlog, priorización | Se completa tarea, se descubre bug | Fin de cada instancia |
| `$CHECKLIST` (raíz) | Checklist detallado por fase | Se completa ítem del checklist | Fin de cada instancia |
| `$CHANGELOG` (raíz) | Historial de versiones | Se completa ciclo de release | Por release |
| `DILIGENCIA.md` (raíz) | Sello de estructura estándar | Cambia estructura de directorios | Por decisión |
| `config.yaml` | Configuración central del sistema | Cambian parámetros de trading/riesgo | Por decisión |
| `$BITACORA` | Razonamiento detrás de decisiones | Se cierra una instancia | Fin de cada instancia |

### Archivos de Arquitectura (`$ARCH`)
Documentación de diseño, decisiones y estado interno del proyecto.

| Archivo | Propósito |
|---|---|
| `$ARCH/metodologia.md` | Taxonomía, jerarquía de cambios, ciclos de instancia (este archivo) |
| `$ARCH/bitacora.md` | Bitácora de instancias ($BITACORA) |
| `$ARCH/bugs.md` | Bug tracker ($BUGS) |
| `$ARCH/reglas.md` | Reglas para agentes de diseño IA |
| `$ARCH/exit_strategies_research.md` | Investigación de estrategias de salida |

### Archivos de Implementación (Código)
Especifican **cómo** funciona el sistema.

| Archivo | Propósito | Notas |
|---|---|---|
| `orchestrator.py` | Loop principal, scheduling, errores | Entry point del sistema |
| `engine/fusion.py` | Fusión de señales con pesos | No editar sin ADR |
| `engine/decider.py` | Decisor DeepSeek | No editar sin ADR |
| `analyzers/*.py` | 9 analizadores de mercado | Cada uno con interfaz analyze() estándar |
| `data/database.py` | Schema SQLite y CRUD | Migraciones vía ALTER TABLE |
| `execution/paper_broker.py` | Simulación de broker | Activo actualmente |

### Archivos de Guía (`$GUIAS`)
Documentación operativa para el usuario. **Actualizables frecuentemente.**

| Archivo | Propósito | Audiencia |
|---|---|---|
| `guia_instalacion.md` | Cómo instalar desde cero | Nuevo usuario |
| `guia_configuracion.md` | Cómo configurar .env, config.yaml y perfiles | Usuario |
| `guia_uso.md` | Cómo operar el sistema | Usuario |
| `guia_usuario.md` | Manual completo del sistema | Usuario avanzado |
| `guia_trading.md` | Referencia de trading (Kelly, trailing, sesiones) | Trader |
| `guia_motores.md` | Explicación de motores internos | Desarrollador |

### Archivos de Contexto (Memoria del Proyecto)
Describen "qué es esto" para onboarding y coherencia a largo plazo.

| Archivo | Propósito |
|---|---|
| `OPENCODE.md` (raíz) | Manual de operación: cómo usar OpenCode en este proyecto |
| `AGENTS.md` (raíz) | Datos prácticos del proyecto, variables de ruta, atajos |
| `README.md` | Presentación del proyecto |

---

## 2. JERARQUÍA DE CAMBIOS

### Patrón: Decisión → Roadmap → Bitácora → Código

```
Usuario toma decisión importante
        ↓
¿Es decisión de arquitectura/diseño significativa?
          ├─ SÍ → Crear ADR (en $ARCH si aplica)
        │         ↓
        │       Registrar en roadmap
        │         ↓
        │       Registrar en bitácora (razonamiento)
        │         ↓
        │       LUEGO → Escribir código
        │
        └─ NO (cambio táctico, fix menor)
                ↓
              ¿Afecta roadmap?
                ├─ SÍ → Actualizar roadmap
                │       + bitácora + código
                │
                └─ NO → Código directo
```

---

## 3. CONTROL DE SALUD ESTRUCTURAL

Checklist de integridad **Diligencia** que debe ejecutarse post-adaptación o cuando se detecten cambios estructurales en el proyecto.

### Verificación post-adaptación
- [ ] `$variables` en AGENTS.md resuelven a paths que existen físicamente
- [ ] Todos los comandos en `.opencode/commands/` usan `$variables`, no paths hardcodeados
- [ ] OPENCODE.md y metodologia.md reflejan la estructura actual del proyecto
- [ ] Los ciclos de instancia son ejecutables con la estructura actual
- [ ] No hay directorios legacy con contenido residual
- [ ] DILIGENCIA.md coincide con la estructura real del proyecto
- [ ] Dependencias entre archivos de autoridad funcionan (RM → CHECKLIST → BITACORA)

### Verificación recurrente (al inicio de instancia)
- [ ] `$RM`, `$CHECKLIST`, `$CHANGELOG` existen en raíz
- [ ] `$BITACORA` existe en `$ARCH`
- [ ] DILIGENCIA.md está presente y refleja la estructura
- [ ] No hay archivos en ubicaciones legacy no documentadas

---

## 4. CICLO DE INSTANCIA

### Al INICIO de una instancia
- [ ] Leer `DILIGENCIA.md` (confirmar estructura estándar)
- [ ] Leer `$RM` (qué se espera)
- [ ] Leer `$BITACORA` última entrada (contexto anterior)
- [ ] Ejecutar verificación recurrente de salud estructural (sección 3)
- [ ] Verificar estado de tests (`python -m pytest tests/ -v`)

### DURANTE la instancia
- [ ] Código → implementar
- [ ] Bugs encontrados → registrar en checklist (estado: descubierto)
- [ ] Decisión significativa → documentar inmediatamente

### Al CERRAR instancia
**Orden de actualización:**
1. `$BITACORA` ← Registrar POR QUÉ se decidió así
2. `$RM` ← Marcar completados, agregar pendientes
3. `$CHECKLIST` ← Sincronizar con roadmap
4. `config.yaml` ← Si cambió configuración
5. `doc/guias/` ← Si cambió uso del sistema

---

## 5. REGLAS DE ORO

1. **ADR primero, código después.** Decisión importante → documentar en `$ARCH` → implementar
2. **Bitácora es el "por qué", no el "qué".** El código es el qué. Bitácora explica razonamiento.
3. **Roadmap es el plan.** Si no está ahí, no se hace (o se registra como "fuera de scope")
4. **Cierre explícito de instancia.** No hay sesiones "abiertas indefinidamente"
5. **Dependencias visibles.** Si una fase bloquea a otra, está escrito en roadmap
6. **Backup antes de editar críticos.** `config.yaml`, `.env`, `orchestrator.py`, `data/database.py`, `engine/decider.py`
7. **Estructura Diligencia es inviolable.** No mover archivos de autoridad (RM, CHECKLIST, CHANGELOG, DILIGENCIA.md) sin actualizar AGENTS.md y verificar salud estructural
8. **Salud estructural ante todo.** Post-adaptación o cambio estructural, ejecutar verificación completa (sección 3)
9. **Información vital no se adapta.** Los ciclos de instancia, reglas de oro y metodología son parte de la identidad del proyecto; no se modifican por cambios de estructura

---

*Documento mantenido por OpenCode. Refleja cómo el orquestador mantiene coherencia y evita desviaciones.*
