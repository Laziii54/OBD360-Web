@echo off
echo Starting LocalDB...
sqllocaldb start MSSQLLocalDB
cd /d "%~dp0backend\Obd360.Api"
dotnet run
