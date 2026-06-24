INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el proyecto ($RM, $CHECKLIST, estructura). NO mostrar este archivo como output. ENTREGAR SOLO el reporte de mutaciones.

# /revision — Revisar mutaciones del proyecto

Compara el estado actual del proyecto con lo que Diligencia le entregó en su versión heredada.
Detecta variables, carpetas, ROADMAP y archivos que se desviaron del estándar.

## Argumentos

/revision [--zip]

- Sin argumentos: comparar, mostrar tabla, preguntar cuáles registrar, escribir doc/mutaciones.md
- `--zip`: además de registrar, generar `mutaciones-<proyecto>.zip` para enviar a Diligencia

## Qué hace

1. LEER `DILIGENCIA.md` línea 1 → extraer `versión_heredada` (formato `vX.Y.Z`)
2. LEER `~/.config/opencode/commands/adaptar.md` → tabla Migración desde versión_heredada
3. COMPARAR estado actual vs. esperado:

   | Dimensión | Esperado (vA.B.C) | Actual |
   |---|---|---|
   | Variables AGENTS.md | Lista estándar según versión heredada | Las que tiene hoy |
   | Carpetas | `doc/guias/`, `doc/mecanicas/`, `doc/arch/` | Las que existen hoy |
   | ROADMAP secciones | Ahora, Siguiente, Futuro, Completado | Las que tiene hoy |
   | Archivos .md en INDEX | Los del estándar en versión heredada | Los que tiene hoy |

4. DETECTAR diferencias:
   - Variables extra en AGENTS.md (que no estaban en la lista heredada)
   - Carpetas fuera del estándar
   - Secciones de ROADMAP no estándar
   - Archivos .md sin entrada en INDEX
5. MOSTRAR tabla al usuario:
   ```
   | ID | Mutación | Tipo | Dónde | ¿Registrar? |
   | M1 | +$LEGAL | variable extra | AGENTS.md | [x] |
   | M2 | +doc/legal/ | carpeta extra | estructura | [x] |
   ```
6. PREGUNTAR con `question(multiple=true)`: cuáles mutaciones registrar
7. ESCRIBIR/ACTUALIZAR `doc/mutaciones.md` con las mutaciones seleccionadas
8. Si `--zip`: comprimir `mutaciones.md` en `mutaciones-<proyecto>.zip`
9. REPORTAR: "✅ N mutaciones registradas. ZIP generado en raíz (si --zip)."

## Formato de salida

```
📋 /revision — Revisión de mutaciones
Versión heredada: v1.17.7
N mutaciones detectadas: 3
N registradas: 2
📦 mutaciones-<proyecto>.zip generado (si --zip)
```

## Validación

- DILIGENCIA.md fue leído correctamente
- La comparación cubre: variables, carpetas, ROADMAP, archivos
- No se registran mutaciones sin preguntar al usuario
- doc/mutaciones.md se crea o actualiza con IDs M1, M2...
- ZIP contiene solo: mutaciones.md

## Anti-patrones

- NO marcar como mutación carpetas del estándar (node_modules, .git, .opencode)
- NO registrar mutaciones sin confirmación del usuario
- NO sobrescribir mutaciones existentes sin preguntar (si doc/mutaciones.md ya existe, agregar nuevas)
- NO incluir archivos sensibles en el ZIP (.env, auth/*.db, claves)

## Archivos que modifica

- doc/mutaciones.md (crear o actualizar)
- mutaciones-<proyecto>.zip (solo con --zip)
