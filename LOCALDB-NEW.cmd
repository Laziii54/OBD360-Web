@echo off
cd /d "%~dp0"
echo === sqllocaldb info === > localdb.log
sqllocaldb info >> localdb.log 2>&1
echo === create Obd360 === >> localdb.log
sqllocaldb create Obd360 -s >> localdb.log 2>&1
sqllocaldb start Obd360 >> localdb.log 2>&1
sqllocaldb info Obd360 >> localdb.log 2>&1
echo done >> localdb.log
