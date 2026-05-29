# /foco — Enfocar agente en modo de trabajo

Cambia la inclinación del agente hacia un área específica: técnica, diseño o experiencia.

## Argumentos
`/foco tx` — modo técnico (backend)
`/foco ui` — modo diseño (frontend)
`/foco ux` — modo experiencia (trading UX)

## Qué hace
1. Lee el roadmap y el checklist del área
2. Revisa archivos clave del área
3. Identifica mejoras, code smells, pendientes
4. Reporta próximos pasos + items del roadmap

### Modo `tx` — Técnico
- Revisa: `engine/`, `analyzers/`, `data/`, `execution/`
- Enfoque: optimizaciones, deuda técnica, rendimiento, tests faltantes

### Modo `ui` — Diseño
- Revisa: `templates/`, `static/`, `dashboard.py`
- Enfoque: coherencia visual, temas, responsive, gráficos Plotly, accesibilidad

### Modo `ux` — Experiencia
- Revisa: `doc/guias/`, `alerts/`, `strategies/`
- Enfoque: métricas visibles, alertas, flujo de operación, reportes
