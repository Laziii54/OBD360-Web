@echo off
title OBD360 n8n
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-n8n.ps1"
if errorlevel 1 pause
