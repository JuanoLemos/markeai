INSTRUCCIÓN: EJECUTAR verificación legal del proyecto. NO modificar archivos sin confirmación del usuario. NO mostrar este archivo como output.

# /legal — Verificación y aplicación de buenas prácticas legales

Verifica la presencia de documentos legales esenciales y ofrece aplicar templates.
NO constituye asesoría legal — es una herramienta de organización documental.

## Argumentos

`/legal [--apply]`

- Sin argumentos: verificar solo (modo auditoría)
- `--apply`: ofrecer copiar templates faltantes desde doc-base

## Qué hace

1. VERIFICAR presencia de estos documentos legales en la raíz del proyecto:

   | Documento | Path esperado | Impacto si falta |
   |---|---|---|
   | `LICENSE` | `./LICENSE` | Sin licencia explícita — el proyecto no tiene términos de uso claros |
   | `NOTICE` | `./NOTICE` | Sin atribución de terceros (riesgo en dependencias copyleft) |
   | `SECURITY.md` | `./SECURITY.md` | Sin canal de reporte de vulnerabilidades |
   | `LICENSING.md` | `./LICENSING.md` | Sin historial de cambios de licencia (opcional, solo si hubo cambios) |

2. VERIFICAR `package.json` campo `"license"`:

   - Si existe `package.json` y no tiene `"license"`: sugerir agregarlo
   - Si tiene `"license"`: validar que el valor sea un identificador SPDX válido

3. VERIFICAR headers SPDX en archivos fuente (muestreo de 5 archivos):

   - Buscar `SPDX-License-Identifier` en `src/` o directorio de código
   - Si menos del 50% de los archivos muestreados tienen header: sugerir agregarlos

4. Si `--apply`:
   - Preguntar por cada documento faltante si copiar el template de doc-base
   - Para NOTICE y SECURITY.md: copiar desde `~/.config/opencode/templates/doc-base/` con `<NOMBRE_DEL_PROYECTO>` reemplazado
   - Para `package.json` sin `"license"`: preguntar valor a agregar

## Formato de salida

```
📋 /legal — Verificación de cumplimiento legal
══════════════════════════════════════════

📄 Documentos legales:
  ✅ LICENSE  — presente
  ❌ NOTICE   — ausente
  ❌ SECURITY.md — ausente

📦 package.json:
  ❌ Falta campo "license"

🔤 Headers SPDX:
  ⚠️ 0/5 archivos muestreados tienen header

══════════════════════════════════════════
  Resumen: 1/4 documentos legales presentes
  📝 Ejecutar /legal --apply para aplicar templates
```

## Validación

- La verificación es siempre solo lectura
- Solo `--apply` modifica archivos
- NO sugerir cambios de licencia — solo verificar presencia de documentos
- Si `LICENSE` no existe, preguntar antes de copiar template GPL-3.0
- NO reemplazar `LICENSE` si ya existe

## Anti-patrones

- NO opinar sobre qué licencia elegir — el usuario decide
- NO modificar headers SPDX existentes
- NO eliminar documentos legales existentes
- NO copiar templates sin preguntar
- NO dar asesoría legal explícita
