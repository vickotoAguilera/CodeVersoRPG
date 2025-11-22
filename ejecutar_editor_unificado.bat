@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   EDITOR UNIFICADO - CodeVerso RPG
echo ========================================
echo.
echo Este editor permite:
echo  - Ver TODOS los elementos del mapa en capas
echo  - MOVER y ESCALAR elementos existentes
echo  - Generar archivo unificado para el juego
echo.
echo IMPORTANTE: 
echo  - NO se pueden crear nuevos elementos aqui
echo  - Use los editores especializados para crear
echo  - Este es el "producto final" que lee el juego
echo.
echo ========================================
echo.

python editor_unificado.py

if errorlevel 1 (
    echo.
    echo [ERROR] El editor cerro con errores.
    echo Presiona cualquier tecla para salir...
    pause >nul
) else (
    echo.
    echo [OK] Archivo unificado generado correctamente
    echo Los cambios se reflejaran al reiniciar el juego
)

pause
