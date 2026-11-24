@echo off
cd /d "%~dp0backend\Obd360.Api"

echo Starting LocalDB...
sqllocaldb start MSSQLLocalDB

echo.
echo Starting API. Log file: api.log
echo Keep this window open. Stop with Ctrl+C
echo.
dotnet run > "%~dp0api.log" 2>&1

echo.
echo API stopped. api.log updated.
pause
