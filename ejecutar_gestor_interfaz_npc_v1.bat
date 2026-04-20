@echo off
cd /d "%~dp0"
set PYTHONUTF8=1

set "PYEXE="
if exist ".venv\Scripts\python.exe" (
  set "PYEXE=.venv\Scripts\python.exe"
) else (
  where py >nul 2>&1
  if not errorlevel 1 (
    set "PYEXE=py -3"
  ) else (
    set "PYEXE=python"
  )
)

echo ========================================
echo   GESTOR INTERFAZ NPC V1 (NUEVO)
echo ========================================
echo Python: %PYEXE%
echo.

%PYEXE% -c "import pygame" >nul 2>&1
if errorlevel 1 (
  echo [INFO] pygame no esta instalado. Instalando pygame-ce...
  %PYEXE% -m pip install pygame-ce
  if errorlevel 1 (
    echo [ERROR] No se pudo instalar pygame-ce.
    pause
    exit /b 1
  )
)

%PYEXE% gestor_interfaz_npc_v1.py
if errorlevel 1 (
  echo.
  echo [ERROR] El gestor NPC nuevo se cerro con errores.
)

pause
