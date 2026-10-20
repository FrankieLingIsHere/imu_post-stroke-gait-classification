@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\mobile\mobile-lab.ps1" -Action Start %*
