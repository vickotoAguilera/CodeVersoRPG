@echo off
echo ========================================
echo   CONECTAR CON GITHUB
echo ========================================
echo.

cd /d "%~dp0"

echo Conectando con tu repositorio de GitHub...
git remote add origin https://github.com/vickotoAguilera/CodeVersoRPG.git

echo.
echo Verificando conexion...
git remote get-url origin

echo.
echo Descargando ultima version desde GitHub...
git pull origin main --allow-unrelated-histories

echo.
echo ========================================
echo   CONECTADO EXITOSAMENTE!
echo ========================================
echo.
pause
