@echo off
chcp 65001 >nul
cd /d "%~dp0"
set R=%~dp0

rem 1) Browser: the app + Swagger
start "" http://localhost:4200
start "" http://localhost:5269/swagger

rem 2) Docs: README, ER diagram, C4 diagram, report, presentation
start "" "%R%README.md"
start "" "%R%docs\report\assets\er-diagram.png"
start "" "%R%docs\c4\OBD360 C4.pdf"
start "" "%R%docs\report\OBD360-Web-Documentation.pdf"
start "" "%R%docs\პრეზენტაცია\პრეზენტაცია.pptx"

rem 3) SSMS with the DB schema script
set "SSMS=C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\ssms.exe"
if exist "%SSMS%" start "" "%SSMS%" "%R%database\schema.sql"

rem 4) VS Code: models, DbContext, migration, controllers, auth, tests, Angular signals
where code >nul 2>&1
if %errorlevel%==0 (
  call code -n "%R%" ^
    "%R%backend\Obd360.Core\Entities\Vehicle.cs" ^
    "%R%backend\Obd360.Core\Entities\ScanSession.cs" ^
    "%R%backend\Obd360.Infrastructure\Data\ApplicationDbContext.cs" ^
    "%R%backend\Obd360.Infrastructure\Migrations\20261028152609_InitialCreate.cs" ^
    "%R%backend\Obd360.Api\Controllers\VehiclesController.cs" ^
    "%R%backend\Obd360.Api\Controllers\AuthController.cs" ^
    "%R%backend\Obd360.Api\Program.cs" ^
    "%R%backend\Obd360.Tests\Controllers\VehiclesAndRemindersTests.cs" ^
    "%R%frontend\src\app\core\services\auth.ts" ^
    "%R%frontend\src\app\features\garage\garage.ts"
)
exit
