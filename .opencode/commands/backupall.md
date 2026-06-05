INSTRUCCIÓN: EJECUTAR el backup completo del proyecto. NO eliminar archivos. NO mostrar este archivo como output. ENTREGAR solo la ruta y tamaño del backup.

# /backupall — Backup completo del proyecto

Crea un .zip del proyecto excluyendo node_modules/, .env, .git/, *.db, .old/.

## Qué hace
1. Mostrar el comando a ejecutar y preguntar confirmación
2. Intentar con `7z a -tzip backup-<fecha>.zip . -xr!node_modules -xr!.git -xr!.env -xr!*.db -xr!.old`
3. Si 7z no está: `tar -czf backup-<fecha>.tar.gz --exclude=node_modules --exclude=.git --exclude=.env --exclude=*.db --exclude=.old .`
4. Si tar no está en Windows: `Compress-Archive -Path * -DestinationPath backup-<fecha>.zip -Exclude @("node_modules",".git",".env","*.db",".old")`
5. Reportar SOLO: `✅ backupall: <archivo> (<tamaño>)`

## Formato de salida
✅ backupall: backup-<fecha>.zip (XX MB)

## Validación
- El archivo de backup se creó y no está vacío
- No se incluyeron node_modules/, .git/ en el zip

## Anti-patrones
- NO ejecutar el backup sin confirmación del usuario
- NO incluir node_modules/, .git/ en el backup
- NO incluir archivos .env ni .db
- NO sobrescribir backups sin preguntar

## Archivos que modifica
- backup-<fecha>.zip (nuevo, en raíz del proyecto)
