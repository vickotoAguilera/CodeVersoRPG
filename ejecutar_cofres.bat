@echo off
echo ========================================
echo   Editor de Cofres - CodeVerso RPG
echo ========================================
echo.
echo Iniciando editor...
echo.

"C:\Program Files\Python312\python.exe" editor_cofres.py

if errorlevel 1 (
    echo.
    echo ERROR: El editor se cerro con errores
    pause
) else (
    echo.
    echo Editor cerrado correctamente
)
