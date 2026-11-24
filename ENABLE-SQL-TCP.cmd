@echo off
setlocal

net session >nul 2>&1
if errorlevel 1 (
  echo Requesting administrator rights...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

set KEY=HKLM\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL17.MSSQLSERVER\MSSQLServer\SuperSocketNetLib\Tcp

echo [1/3] Enabling TCP...
reg add "%KEY%" /v Enabled /t REG_DWORD /d 1 /f
for /L %%i in (1,1,12) do reg add "%KEY%\IP%%i" /v Enabled /t REG_DWORD /d 1 /f
reg add "%KEY%\IPAll" /v TcpPort /t REG_SZ /d 1433 /f
reg add "%KEY%\IPAll" /v TcpDynamicPorts /t REG_SZ /d "" /f

echo [2/3] Restarting SQL Server...
net stop MSSQLSERVER
net start MSSQLSERVER

echo [3/3] Checking port 1433...
timeout /t 3 /nobreak >nul
netstat -ano | findstr ":1433" | findstr "LISTENING"

echo.
echo Done.
pause
