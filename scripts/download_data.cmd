@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0download_data.ps1" %*
exit /b %ERRORLEVEL%
