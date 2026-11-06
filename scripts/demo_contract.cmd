@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0demo_contract.ps1"
exit /b %ERRORLEVEL%
