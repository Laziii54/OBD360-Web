@echo off
setlocal
echo Stopping OBD360 servers on ports 4200 and 5269...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ports = 4200,5269; foreach ($p in $ports) { $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue; foreach ($x in $c) { try { Stop-Process -Id $x.OwningProcess -Force -ErrorAction Stop; Write-Host ('Stopped port ' + $p + ' (PID ' + $x.OwningProcess + ')') } catch { Write-Host ('Could not stop port ' + $p) } } }; Write-Host 'Done.'"
echo.
pause
