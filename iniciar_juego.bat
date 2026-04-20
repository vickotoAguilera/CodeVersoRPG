@echo off
setlocal

REM Inicia el juego desde la carpeta del proyecto
cd /d "%~dp0"

echo === Iniciando Code Verso RPG ===

echo.
set "PY_VENV=.venv\Scripts\python.exe"

if exist "%PY_VENV%" (
    "%PY_VENV%" -c "import pygame" >nul 2>nul
    if errorlevel 1 (
        echo [AVISO] El entorno virtual .venv existe, pero no puede importar pygame.
        echo         Intentando iniciar con el Python del sistema via PATH...
        python main.py
    ) else (
        echo Usando Python del entorno virtual: .venv
        "%PY_VENV%" main.py
    )
) else (
    echo [AVISO] No se encontro .venv\Scripts\python.exe
    echo         Usando el Python del sistema (si existe en PATH)
    python main.py
)

echo.
echo === El juego termino (o fallo). Revisa los mensajes arriba. ===
pause
