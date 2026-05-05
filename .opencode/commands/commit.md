# /commit — Commit con formato del proyecto

Realiza un commit siguiendo el formato estándar del proyecto.

## Argumentos
`/commit Mensaje del commit` — sin comillas

## Qué hace
1. `git add -A`
2. Muestra diff resumido al usuario
3. Pregunta confirmación
4. `git commit -m "MarketAI: [mensaje]"`
5. Muestra resultado

## Archivos que modifica
- Todos los cambios sin commitear
