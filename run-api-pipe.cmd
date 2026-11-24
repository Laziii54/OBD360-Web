@echo off
setlocal

net session >nul 2>&1
if errorlevel 1 (
  echo Requesting administrator rights...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

cd /d "%~dp0backend\Obd360.Api"

echo Starting LocalDB...
sqllocaldb start MSSQLLocalDB

set "PIPE="
for /f "tokens=4" %%a in ('sqllocaldb info MSSQLLocalDB ^| findstr /i "Instance pipe name"') do set "PIPE=%%a"

if "%PIPE%"=="" (
  echo ERROR: could not read LocalDB pipe name.
  pause
  exit /b 1
)

echo Using pipe: %PIPE%
set "ConnectionStrings__DefaultConnection=Server=%PIPE%;Database=Obd360WebDb;Trusted_Connection=True;MultipleActiveResultSets=true;TrustServerCertificate=True"

echo.
echo Starting API as Administrator...
echo Log file: api.log
echo Keep this window open. Stop with Ctrl+C
echo.
dotnet run > "%~dp0api.log" 2>&1

echo.
echo API stopped. api.log updated.
pause
