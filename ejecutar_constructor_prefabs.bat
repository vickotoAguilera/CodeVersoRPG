@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
cls
echo ========================================
echo   CONSTRUCTOR DE PREFABS - CodeVerso RPG
echo ========================================
echo.
echo Este editor permite:
echo  - Cargar piezas o tiles desde assets
echo  - Armar prefabs grandes como casas o castillos
echo  - Rotar y espejar piezas
echo  - Guardar PNG + JSON

echo ========================================
echo.

python constructor_prefabs.py

if errorlevel 1 (
    echo.
    echo [ERROR] El constructor cerro con errores.
    echo Presiona cualquier tecla para salir...
    pause >nul
) else (
    echo.
    echo [OK] Constructor cerrado correctamente
)

pause
