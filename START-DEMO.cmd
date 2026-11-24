@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Starting LocalDB...
sqllocaldb start MSSQLLocalDB

echo [2/3] Starting API...
start "OBD360 API" cmd /k call "%~dp0start-api.cmd"

echo [3/3] Starting Frontend...
start "OBD360 Frontend" cmd /k call "%~dp0start-frontend.cmd"

echo.
echo Waiting 15 seconds...
timeout /t 15 /nobreak >nul

start "" http://localhost:4200
start "" http://localhost:5269/swagger

echo.
echo Done. Browser should be open now.
pause
