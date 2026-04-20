@echo off
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul
if errorlevel 1 set PY=python3
%PY% gestor_portales_interaccion_v2.py audit
pause
