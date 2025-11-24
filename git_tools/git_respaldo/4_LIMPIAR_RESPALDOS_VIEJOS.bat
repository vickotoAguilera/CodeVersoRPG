@echo off
echo ========================================
echo   PASO 4: LIMPIAR RESPALDOS ANTIGUOS
echo ========================================
echo.
echo Este script te ayudara a eliminar ramas
echo de respaldo antiguas que ya no necesites.
echo.
pause

cd /d "%~dp0\.."

echo.
echo Ramas de respaldo disponibles:
echo.
git branch | findstr "respaldo-"
echo.

set /p RAMA="Ingresa el nombre de la rama a ELIMINAR (o deja vacio para cancelar): "

if "%RAMA%"=="" (
    echo.
    echo Operacion cancelada.
    pause
    exit /b 0
)

echo.
echo ADVERTENCIA: Vas a eliminar la rama: %RAMA%
echo Esta accion NO se puede deshacer.
echo.
set /p CONFIRMAR="Estas seguro? (escribe SI para confirmar): "

if /i not "%CONFIRMAR%"=="SI" (
    echo.
    echo Operacion cancelada.
    pause
    exit /b 0
)

echo.
echo Eliminando rama: %RAMA%
git branch -D %RAMA%

echo.
echo ========================================
echo   RAMA ELIMINADA
echo ========================================
echo La rama %RAMA% ha sido eliminada.
echo.
pause
