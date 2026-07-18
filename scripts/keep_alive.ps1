# keep_alive.ps1 — External watchdog for MarketAI server
# Designed to run via Windows Task Scheduler every 5 minutes.
# Checks if the dashboard responds. If not, kills zombies and restarts.

$BASE = "C:\xampp\htdocs\MarketAI"
$URL = "http://localhost:8050/api/ping"
$LOG = "$BASE\data\server\keep_alive.log"
$BAT = "$BASE\tray_watchdog.bat"

# Ensure log directory exists
$null = New-Item -ItemType Directory -Path "$BASE\data\server" -Force -ErrorAction SilentlyContinue

try {
    $response = Invoke-WebRequest -Uri $URL -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        # Server alive — nothing to do
        exit 0
    }
}
catch {
    # Server not responding — needs restart
}

# Log the restart attempt
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$ts] Server not responding. Killing python processes..." | Out-File -FilePath $LOG -Append

# Kill all python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Kill any process on port 8050
$netstat = netstat -ano | Select-String ":8050" | Select-String "LISTENING"
if ($netstat) {
    foreach ($line in $netstat) {
        $pid = $line.ToString().Split()[-1].Trim()
        if ($pid -match "^\d+$") {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

# Start tray_watchdog.bat
"[$ts] Starting tray_watchdog.bat..." | Out-File -FilePath $LOG -Append
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $BAT -WindowStyle Hidden

"[$ts] Done. Will check again in 5 min." | Out-File -FilePath $LOG -Append
exit 1
