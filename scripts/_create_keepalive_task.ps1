$action = New-ScheduledTaskAction -Execute "C:\xampp\htdocs\MarketAI\venv\Scripts\pythonw.exe" -Argument "C:\xampp\htdocs\MarketAI\scripts\keep_alive.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
try {
    Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force -ErrorAction Stop
    Write-Host "OK: Task creada" -ForegroundColor Green
} catch {
    Write-Host ("FAIL: {0}" -f $_.Exception.Message) -ForegroundColor Red
}
Write-Host ""
Write-Host "=== Verificacion ==="
$task = Get-ScheduledTask -TaskName "MarketAI-KeepAlive" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "Task existe: State=$($task.State)"
    $info = Get-ScheduledTaskInfo -TaskName "MarketAI-KeepAlive" -ErrorAction SilentlyContinue
    if ($info) { Write-Host ("LastRun={0} NextRun={1}" -f $info.LastRunTime, $info.NextRunTime) }
} else {
    Write-Host "Task NO creada" -ForegroundColor Red
}
