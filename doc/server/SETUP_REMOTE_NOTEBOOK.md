# Setup Notebook Remota — Instrucciones Revisadas

**Autor:** Mavis-allá
**Para:** humano que va a configurar la segunda notebook
**Objetivo:** Levantar MarketAI en una notebook nueva en el mismo router, accesible vía LAN para que esta Mavis-allá (en `felrena`) se pueda conectar.

---

## 📋 Review de las instrucciones originales

| # | Issue | Severidad |
|---|---|---|
| 1 | **No hay `git clone`** — el código no aparece de la nada | 🔴 bloqueante |
| 2 | **Path `C:\markeai`** vs la original `C:\xampp\htdocs\MarketAI` — inconsistencia | 🟠 importante |
| 3 | **No menciona el tray app** — las instrucciones arrancan orchestrator + dashboard por separado, sin auto-recovery | 🟠 importante |
| 4 | **No abre el puerto 8050 en el firewall** — sin esto, la otra PC no se puede conectar | 🔴 bloqueante |
| 5 | **`notepad .env` requiere intervención manual** — bloquea el script hasta que se cierre | 🟡 menor |
| 6 | **No dice cómo obtener la IP** — `ipconfig` puede dar varias (LAN, virtual, Tailscale). Hay que filtrar bien | 🟠 importante |
| 7 | **No hay un test de "soy alcanzable desde afuera"** — el dashboard puede estar OK pero el firewall de Windows bloquear conexiones entrantes | 🟠 importante |
| 8 | **No hay un bloque de "verificar al final"** completo — solo el health endpoint | 🟡 menor |
| 9 | **No documenta qué hacer después** — una vez arriba, ¿cómo me conecto yo? | 🟠 importante |
| 10 | **No menciona que se necesita API key real de DeepSeek** — sin eso, el bot hace fallback a WAIT | 🟠 importante |

---

## ✅ Versión mejorada de las instrucciones

Pegar este bloque en la notebook remota, en PowerShell **como Administrador** (click derecho en Inicio → PowerShell (Admin)).

### Bloque 1 — Verificar Python

```powershell
python --version
```

Si dice `Python 3.12.x` o `Python 3.13.x` → seguí al Bloque 2.
Si dice error o no lo encuentra → bajá e instalá https://www.python.org/downloads/ (tildar ✅ "Add Python to PATH").

### Bloque 2 — Clonar el repo y preparar

```powershell
cd C:\
if (Test-Path C:\markeai) { Write-Host "Ya existe C:\markeai,跳过" -ForegroundColor Yellow } else {
    git clone https://github.com/JuanoLemos/markeai.git C:\markeai
}
cd C:\markeai
pip install -r requirements.txt
```

Si falla con `smartmoneyconcepts` no importa, no bloquea el resto.

### Bloque 3 — Configurar .env

```powershell
cd C:\markeai
if (Test-Path .env) {
    Write-Host ".env existe, mostrando las claves actuales (enmascaradas):" -ForegroundColor Green
    Get-Content .env | ForEach-Object {
        if ($_ -match '^(#|$)') { Write-Host $_ }
        elseif ($_ -match '(KEY|SECRET|TOKEN|PASSPHRASE|PRIVATE)') {
            $parts = $_ -split '=', 2
            $val = $parts[1]
            $masked = if ($val.Length -gt 8) { $val.Substring(0,4) + "..." + $val.Substring($val.Length-4) } else { "(vacío o muy corto)" }
            Write-Host "$($parts[0])=$masked"
        } else { Write-Host $_ }
    }
} else {
    Copy-Item .env.example .env
    Write-Host ".env creado desde .env.example. Tienes que editarlo con tus claves reales:" -ForegroundColor Yellow
    Write-Host "  - DEEPSEEK_API_KEY (obligatoria, sin esto el bot no decide)"
    Write-Host "  - NEWSAPI_KEY, CRYPTOPANIC_KEY (opcionales)"
    Write-Host "  - POLYMARKET_PRIVATE_KEY (opcional, solo para trading real)"
    Write-Host "  - TELEGRAM_BOT_TOKEN (opcional, para alertas)"
    notepad .env
}
```

### Bloque 4 — Abrir el puerto 8050 en el firewall (CRÍTICO)

Sin esto, la otra PC no se puede conectar al dashboard aunque esté corriendo.

```powershell
New-NetFirewallRule -DisplayName "MarketAI Dashboard (LAN)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8050 `
    -RemoteAddress 192.168.0.0/16 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

$rule = Get-NetFirewallRule -DisplayName "MarketAI Dashboard (LAN)" -ErrorAction SilentlyContinue
if ($rule) {
    Write-Host "Regla de firewall creada OK: Enabled=$($rule.Enabled)" -ForegroundColor Green
} else {
    Write-Host "No se pudo crear la regla. Verificá que estés en PowerShell Admin." -ForegroundColor Red
}
```

### Bloque 5 — Crear icono en escritorio + tareas programadas (auto-recovery + cron)

```powershell
cd C:\markeai

# 5a. Crear acceso directo en escritorio
$desktop = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut((Join-Path $desktop "MarketAI.lnk"))
$sc.TargetPath = "C:\markeai\tray_app.bat"
$sc.WorkingDirectory = "C:\markeai"
$sc.IconLocation = "C:\markeai\venv\Scripts\python.exe,0"
$sc.Description = "MarketAI - Trading 24/7 (system tray)"
$sc.Save()
Write-Host "Acceso directo creado en escritorio" -ForegroundColor Green

# 5b. Crear task de watchdog (cada 5 min)
$action = New-ScheduledTaskAction -Execute "C:\markeai\venv\Scripts\pythonw.exe" -Argument "C:\markeai\scripts\ola2_watchdog.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 2)
Register-ScheduledTask -TaskName "MarketAI-Watchdog" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Watchdog Task Scheduler: OK (cada 5 min)" -ForegroundColor Green

# 5c. Crear task de auto-update (cada 6h)
$action2 = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "C:\markeai\update_hidden.vbs"
$trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "MarketAI AutoUpdate" -Action $action2 -Trigger $trigger2 -Settings $settings2 -Force | Out-Null
Write-Host "AutoUpdate Task Scheduler: OK (cada 6h)" -ForegroundColor Green
```

### Bloque 6 — Arrancar el servidor (doble click en el icono de escritorio)

```
Hacé doble click en el icono "MarketAI" del escritorio.
```

El tray app se inicia minimizado en la systray. Si todo salió bien, deberías ver un icono $ en la barra de tareas (cerca del reloj).

Si preferís arrancarlo desde línea de comandos:

```powershell
cd C:\markeai
.\tray_app.bat
```

(No cierres esta ventana — el server vive acá. Para que corra "invisible" usá el acceso directo del escritorio.)

### Bloque 7 — Verificar que todo funciona

```powershell
# 7a. Dashboard accesible local
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8050" -UseBasicParsing -TimeoutSec 5
    Write-Host "Dashboard local: HTTP $($r.StatusCode), $($r.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "ERROR dashboard local: $($_.Exception.Message)" -ForegroundColor Red
}

# 7b. Health endpoint
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8050/api/health" -UseBasicParsing -TimeoutSec 5
    $h = $r.Content | ConvertFrom-Json
    Write-Host "Health: $($h | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "ERROR health: $($_.Exception.Message)" -ForegroundColor Red
}

# 7c. Watchdog corre
Get-ScheduledTask -TaskName "MarketAI-Watchdog" | ForEach-Object {
    $info = Get-ScheduledTaskInfo -TaskName $_.TaskName
    Write-Host "Watchdog: proxima=$($info.NextRunTime)" -ForegroundColor Green
}
```

### Bloque 8 — Decir la IP y conectividad

```powershell
# 8a. IPs LAN (la que importa para conectar)
$lan = Get-NetIPAddress -InterfaceAlias "Ethernet*","Wi-Fi*" -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.*" } | Select-Object -First 1
if ($lan) {
    Write-Host "IP LAN: $($lan.IPAddress)" -ForegroundColor Green
} else {
    Write-Host "No se encontro IP LAN. Listando todas:" -ForegroundColor Yellow
    ipconfig | Select-String "IPv4"
}

# 8b. Tailscale (si lo tenés instalado)
$ts = & tailscale ip -4 2>$null
if ($ts) { Write-Host "Tailscale IP: $ts" -ForegroundColor Green } else { Write-Host "Tailscale: no instalado o no corriendo" -ForegroundColor Yellow }

# 8c. Hostname
Write-Host "Hostname: $env:COMPUTERNAME" -ForegroundColor Green
```

**Mandame los 3 valores**: IP LAN, Tailscale IP (si hay), hostname.

### Bloque 9 — Test final: que esta notebook me vea

Desde ESTA notebook (`felrena`), una vez que me pasaste la IP, voy a probar:

```powershell
# desde felrena:
$r = Invoke-WebRequest -Uri "http://<IP_LAN>:8050/api/health" -UseBasicParsing -TimeoutSec 5
Write-Host "Conectado a la notebook remota: HTTP $($r.StatusCode)"
```

Si eso responde 200, la conexión funciona.

---

## 📋 Qué hago yo desde acá (Mavis-allá en felrena) una vez que tengo la IP

1. Conecto a `http://<IP>:8050` para monitorear el dashboard
2. Conecto a `http://<IP>:8050/api/positions` y `/api/health` para checks programáticos
3. Si me pedís algo, ejecuto comandos via `Invoke-WebRequest` o `Invoke-Command` (WinRM si está habilitado)
4. Reporto el estado de la notebook remota con la misma estructura que la local

## ⚠️ Limitaciones

- **No tengo acceso a la terminal de la otra PC** (a menos que WinRM/RDP estén habilitados). Solo puedo hablar HTTP.
- **Los procesos los arrancás vos** — yo no puedo hacer doble click ni abrir ventanas.
- **El firewall se abre SOLO a la red 192.168.0.0/16** — si después querés exponer a internet, hay que hacerlo a propósito.
- **Si reiniciás la notebook, los servicios NO arrancan solos** — el tray app + las tasks se reinician, pero hay que verificar.

---

## ❓ Checklist pre-flight (todo esto en la notebook REMOTA)

- [ ] Python 3.12+ instalado
- [ ] `git` instalado (viene con Git for Windows o ya en PATH)
- [ ] Repo clonado en `C:\markeai`
- [ ] `.env` con `DEEPSEEK_API_KEY` real (sino el bot hace fallback a WAIT, ver Issue 1 del incidente)
- [ ] Firewall abierto para 8050
- [ ] Acceso directo en escritorio
- [ ] Watchdog + auto-update en Task Scheduler
- [ ] Tray app arrancado, icono $ en systray
- [ ] Dashboard responde localmente (HTTP 200)
- [ ] IP LAN anotada y pasada a Mavis-allá

Si todo eso está, en 5-10 minutos la notebook remota está lista.
