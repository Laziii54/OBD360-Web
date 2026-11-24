@echo off
cd /d "%~dp0"
echo === docker version === > docker.log
docker version >> docker.log 2>&1
echo === compose up sqlserver === >> docker.log
docker compose up -d sqlserver >> docker.log 2>&1
echo === waiting 40s === >> docker.log
timeout /t 40 /nobreak >nul
docker compose ps >> docker.log 2>&1
echo done >> docker.log
echo.
echo See docker.log in the OBD2 WEB folder. Press any key to close.
pause >nul
