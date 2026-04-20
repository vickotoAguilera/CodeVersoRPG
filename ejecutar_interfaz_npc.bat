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
echo   INTERFAZ NPC (GESTOR NUEVO)
echo ========================================
echo Python: %PYEXE%
echo.

%PYEXE% -c "import pygame" >nul 2>&1
if errorlevel 1 (
  echo [INFO] pygame no esta instalado. Instalando pygame-ce...
  %PYEXE% -m pip install pygame-ce
  if errorlevel 1 (
    echo [ERROR] No se pudo instalar pygame-ce.
    echo Activa tu entorno virtual y ejecuta: pip install pygame-ce
    pause
    exit /b 1
  )
)

%PYEXE% gestor_interfaz_npc_v1.py
if errorlevel 1 (
  echo.
  echo [ERROR] La interfaz NPC nueva se cerro con errores.
)

pause
