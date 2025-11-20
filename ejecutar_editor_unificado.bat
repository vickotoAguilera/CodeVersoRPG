@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   EDITOR UNIFICADO - CodeVerso RPG
echo ========================================
echo.
echo Iniciando editor unificado...
echo.

python editor_unificado.py

if errorlevel 1 (
    echo.
    echo ¡ERROR! El editor cerró con errores.
    echo Presiona cualquier tecla para ver detalles...
    pause >nul
) else (
    echo.
    echo Editor cerrado correctamente.
)

pause
