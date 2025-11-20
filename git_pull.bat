@echo off
echo ========================================
echo   ACTUALIZAR DESDE GITHUB
echo ========================================
echo.

cd /d "%~dp0"

echo Descargando cambios desde GitHub...
git pull origin main

echo.
echo ========================================
echo   ACTUALIZADO!
echo ========================================
echo.
pause
