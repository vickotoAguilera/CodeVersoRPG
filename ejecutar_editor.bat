@echo off
echo ========================================
echo   EDITOR DE MAPAS - CodeVerso RPG
echo ========================================
echo.
echo Iniciando editor de mapas...
echo.

python editor_mapa.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error al ejecutar el editor
    pause
)
