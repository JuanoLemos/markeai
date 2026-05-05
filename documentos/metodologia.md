# Metodología de Proyecto — MarketAI

**Propósito:** Definir cómo se mantiene coherencia, qué se actualiza cuándo, cómo evitar desviaciones.

---

## 1. ESTRUCTURA DE ARCHIVOS — TAXONOMÍA

### Archivos de Autoridad (Fuentes de Verdad)
Definen el estado ACTUAL del proyecto. **Inmutables excepto decisiones explícitas del Usuario.**

| Archivo | Propósito | Se actualiza cuando... | Frecuencia |
|---|---|---|---|
| `documentos/roadmap.md` | Tareas, fases, backlog, priorización | Se completa tarea, se descubre bug | Fin de cada instancia |
| `documentos/checklist.md` | Checklist detallado por fase | Se completa ítem del checklist | Fin de cada instancia |
| `config.yaml` | Configuración central del sistema | Cambian parámetros de trading/riesgo | Por decisión |
| `informes/bitacora.md` | Razonamiento detrás de decisiones | Se cierra una instancia | Fin de cada instancia |

### Archivos de Implementación (Código)
Especifican **cómo** funciona el sistema.

| Archivo | Propósito | Notas |
|---|---|---|
| `orchestrator.py` | Loop principal, scheduling, errores | Entry point del sistema |
| `engine/fusion.py` | Fusión de señales con pesos | No editar sin ADR |
| `engine/decider.py` | Decisor DeepSeek | No editar sin ADR |
| `analyzers/*.py` | 7 analizadores de mercado | Cada uno con interfaz analyze() estándar |
| `data/database.py` | Schema SQLite y CRUD | Migraciones vía ALTER TABLE |
| `execution/paper_broker.py` | Simulación de broker | Activo actualmente |

### Archivos de Guía (Documentación Operativa)
Ayudan a entender "cómo usar" algo. **Actualizables frecuentemente.**

| Archivo | Propósito | Audiencia |
|---|---|---|
| `guias/guia_instalacion.md` | Cómo instalar desde cero | Nuevo usuario |
| `guias/guia_configuracion.md` | Cómo configurar .env y config.yaml | Usuario |
| `guias/guia_uso.md` | Cómo operar el sistema | Usuario |
| `guias/guia.md` | Documentación completa del sistema | Usuario avanzado |

### Archivos de Contexto (Memoria del Proyecto)
Describen "qué es esto" para onboarding y coherencia a largo plazo.

| Archivo | Propósito |
|---|---|
| `OPENCODE.md` (raíz) | Manual de operación: cómo usar OpenCode en este proyecto |
| `AGENTS.md` (raíz) | Datos prácticos del proyecto, configuración, atajos |
| `README.md` | Presentación del proyecto |

---

## 2. JERARQUÍA DE CAMBIOS

### Patrón: Decisión → Roadmap → Bitácora → Código

```
Usuario toma decisión importante
        ↓
¿Es decisión de arquitectura/diseño significativa?
        ├─ SÍ → Crear ADR (en informes/adr.md si aplica)
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

## 3. CICLO DE INSTANCIA

### Al INICIO de una instancia
- [ ] Leer `documentos/roadmap.md` (qué se espera)
- [ ] Leer `informes/bitacora.md` última entrada (contexto anterior)
- [ ] Verificar estado de tests (`python -m pytest tests/ -v`)

### DURANTE la instancia
- [ ] Código → implementar
- [ ] Bugs encontrados → registrar en checklist (estado: descubierto)
- [ ] Decisión significativa → documentar inmediatamente

### Al CERRAR instancia
**Orden de actualización:**
1. `informes/bitacora.md` ← Registrar POR QUÉ se decidió así
2. `documentos/roadmap.md` ← Marcar completados, agregar pendientes
3. `documentos/checklist.md` ← Sincronizar con roadmap
4. `config.yaml` ← Si cambió configuración
5. `guias/` ← Si cambió uso del sistema

---

## 4. REGLAS DE ORO

1. **ADR primero, código después.** Decisión importante → documentar → implementar
2. **Bitácora es el "por qué", no el "qué".** El código es el qué. Bitácora explica razonamiento.
3. **Roadmap es el plan.** Si no está ahí, no se hace (o se registra como "fuera de scope")
4. **Cierre explícito de instancia.** No hay sesiones "abiertas indefinidamente"
5. **Dependencias visibles.** Si una fase bloquea a otra, está escrito en roadmap
6. **Backup antes de editar críticos.** `config.yaml`, `.env`, `orchestrator.py`, `data/database.py`, `engine/decider.py`

---

*Documento mantenido por OpenCode. Refleja cómo el orquestador mantiene coherencia y evita desviaciones.*
