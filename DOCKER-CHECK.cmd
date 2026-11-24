@echo off
cd /d "%~dp0"
echo === docker version === > docker.log
docker version >> docker.log 2>&1
echo === docker ps === >> docker.log
docker ps >> docker.log 2>&1
echo done >> docker.log
