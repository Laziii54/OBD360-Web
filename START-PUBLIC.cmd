@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Starting API...
start "OBD360 API" cmd /k call "%~dp0start-api.cmd"

echo [2/3] Starting frontend...
start "OBD360 Frontend" cmd /k call "%~dp0start-frontend.cmd"

echo [3/3] Waiting 15 seconds for the app to start...
timeout /t 15 /nobreak >nul

echo.
echo ================================================================
echo  Creating a public internet link...
echo  Copy the https://....trycloudflare.com address shown below.
echo  Keep this window open while you share the link.
echo ================================================================
echo.

"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url "http://[::1]:4200" --no-autoupdate

echo.
echo Tunnel stopped.
pause
