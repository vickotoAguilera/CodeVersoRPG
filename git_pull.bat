@echo off
echo ========================================
echo   ACTUALIZAR DESDE GITHUB (FORZADO)
echo ========================================
echo.
echo ADVERTENCIA: Este script reemplazara COMPLETAMENTE
echo tu proyecto local con la version del repositorio.
echo Todos los cambios locales se PERDERAN.
echo.
pause

cd /d "%~dp0"

echo.
echo [1/4] Descargando informacion del repositorio...
git fetch --all

echo.
echo [2/4] Descartando todos los cambios locales...
git reset --hard origin/main

echo.
echo [3/4] Eliminando archivos no rastreados...
git clean -fd

echo.
echo [4/4] Asegurando sincronizacion completa...
git pull origin main

echo.
echo ========================================
echo   PROYECTO ACTUALIZADO COMPLETAMENTE!
echo ========================================
echo Tu proyecto local ahora es identico al repositorio.
echo.
pause
