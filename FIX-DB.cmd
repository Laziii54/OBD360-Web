@echo off
echo [1/5] Stopping API...
taskkill /IM Obd360.Api.exe /F >nul 2>&1
taskkill /IM dotnet.exe /F >nul 2>&1

echo [2/5] Stopping LocalDB...
sqllocaldb stop MSSQLLocalDB -k

echo [3/5] Deleting LocalDB instance...
sqllocaldb delete MSSQLLocalDB

echo [4/5] Removing old database files...
del /f /q "%USERPROFILE%\Obd360WebDb.mdf" >nul 2>&1
del /f /q "%USERPROFILE%\Obd360WebDb_log.ldf" >nul 2>&1
del /f /q "%USERPROFILE%\Obd360WebDevDb.mdf" >nul 2>&1
del /f /q "%USERPROFILE%\Obd360WebDevDb_log.ldf" >nul 2>&1

echo [5/5] Creating fresh LocalDB instance...
sqllocaldb create MSSQLLocalDB -s

echo.
echo ============================================
echo Done. Now double-click run-api-log.cmd
echo ============================================
pause
