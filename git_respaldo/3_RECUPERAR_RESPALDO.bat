@echo off
echo ========================================
echo   PASO 3: RECUPERAR RESPALDO
echo ========================================
echo.
echo ADVERTENCIA: Esto reemplazara tu codigo actual
echo con el codigo del respaldo que elijas.
echo.

cd /d "%~dp0\.."

echo Ramas de respaldo disponibles:
echo.
git branch | findstr "respaldo-"
echo.

set /p RAMA="Ingresa el nombre de la rama a recuperar (ejemplo: respaldo-20251121-150000): "

if "%RAMA%"=="" (
    echo.
    echo ERROR: No ingresaste ningun nombre de rama.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   CONFIRMACION
echo ========================================
echo.
echo Vas a recuperar la rama: %RAMA%
echo Esto REEMPLAZARA tu codigo actual.
echo.
set /p CONFIRMAR="Estas seguro? (escribe SI para confirmar): "

if /i not "%CONFIRMAR%"=="SI" (
    echo.
    echo Operacion cancelada.
    pause
    exit /b 0
)

echo.
echo [1/3] Guardando cambios actuales (por si acaso)...
git stash

echo.
echo [2/3] Cambiando a la rama de respaldo...
git checkout %RAMA%

echo.
echo [3/3] Aplicando el respaldo a la rama main...
git checkout main
git reset --hard %RAMA%

echo.
echo ========================================
echo   RESPALDO RECUPERADO EXITOSAMENTE!
echo ========================================
echo Tu proyecto ha sido restaurado al estado: %RAMA%
echo.
pause
