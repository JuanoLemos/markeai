INSTRUCCIÓN: EJECUTAR el push. NO ejecutar sin confirmación. NO mostrar este archivo como output.

# /pushgh — Push a GitHub

Realiza git push al remoto configurado en `$REPO`.

Solo ejecuta BUILD*: no tiene PLAN propio — los datos se heredan del Meta-PLAN de /CBP.

## Argumentos

/pushgh [--force] [--branch <nombre>]

- `--force`: fuerza el push (requiere confirmación adicional explícita)
- `--branch <nombre>`: rama destino (default: rama actual detectada automáticamente)

## Guardas

- Si `$REPO` no está definido en AGENTS.md: SKIP — "⚠️ $REPO no definido en AGENTS.md. Push omitido."
- Si `git remote -v` no muestra remoto: SKIP — "⚠️ No hay remote configurado. Push omitido."
- Si `git status --porcelain` no está vacío: DETENER — "⚠️ Working tree sucio. Commit primero."
- Si `git push` falla: DETENER con error

## Qué hace

1. LEER `$REPO` de AGENTS.md AHORA (Mapeo de rutas)
2. Si `$REPO` no está definido: SKIP con mensaje
3. VERIFICAR que existe remote: `git remote -v`
4. Si no hay remote: "ℹ️ No hay remote. Ejecuta: git remote add origin $REPO" y SKIP
5. VERIFICAR working tree: `git status --porcelain`
6. Si sucio: DETENER — "git status no está limpio. Commit primero."
7. DETECTAR rama actual: `git branch --show-current`
8. ARMAR mensaje de confirmación: "¿Push a $REPO (rama: <rama>)?"
9. PREGUNTAR confirmación al usuario
10. Si no confirma: ABORTAR
11. EJECUTAR: `git push origin <rama>`
12. MOSTRAR resultado: "✅ Push exitoso a $REPO (rama: <rama>) — N commits subidos"

## Anti-patrones

- NO hacer push sin confirmación del usuario
- NO usar --force sin confirmación adicional explícita y mensaje de advertencia
- NO hacer push si git status no está limpio
- NO modificar AGENTS.md — solo leer $REPO
- NO definir $REPO si no hay remote configurado
- NO mostrar este archivo como output

## Archivos que lee

- AGENTS.md (variable $REPO)

## Archivos que modifica

- Ninguno localmente; actualiza el repositorio remoto en GitHub