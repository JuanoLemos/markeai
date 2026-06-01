INSTRUCCIÓN: EJECUTAR toggle de notificación remota. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /notify — Toggle de notificación remota

Activa/desactiva la notificación remota del proyecto. Cuando está activa, los planes y resultados de BUILD pueden enviarse a un canal remoto (Telegram, webhook, etc.).

## Argumentos
| Comando | Efecto |
|---|---|
| `/notify on` | Activa notificación remota. Crea archivo de estado. |
| `/notify off` | Desactiva notificación remota. Borra archivo de estado. |
| `/notify` | Muestra estado actual (activo/inactivo). |
| `/notify test` | Envía mensaje de prueba (si hay notificador configurado). |

## Qué hace
1. `/notify` (sin args): leer archivo de estado notify-active.json (o $NOTIFY_STATE si está definido)
   - Si existe con `active: true`: "✅ Notify ACTIVO desde [fecha]"
   - Si no: "❌ Notify INACTIVO"
2. `/notify on`:
   - Crear notify-active.json con `{ "active": true, "started_at": "<ISO>" }`
   - "✅ Notify activado. Modo remoto habilitado."
3. `/notify off`:
   - Borrar notify-active.json
   - "❌ Notify desactivado."
4. `/notify test`:
   - Buscar script notificador o webhook configurado en el proyecto
   - Si encuentra: ejecutar test de conectividad
   - Si no: "⚠️ No hay notificador configurado. Definir $NOTIFY_SCRIPT en AGENTS.md."

## Formato de salida
✅ Notify ACTIVO desde <fecha>
❌ Notify INACTIVO — usar /notify on
⚠️ No hay notificador configurado

## Validación
- notify-active.json contiene JSON válido con campo `active`
- /notify off siempre borra el archivo de estado
- /notify test verifica conectividad real

## Anti-patrones
- NO enviar notificaciones sin que notify esté activo
- NO crear notify-active.json si no se puede enviar (verificar configuración primero)
- NO hardcodear ruta del notificador — usar $NOTIFY_SCRIPT o buscar en scripts/
- NO confundir estado del proyecto con estado del agente — notify es independiente

## Archivos que modifica
- notify-active.json (en raíz del proyecto)
