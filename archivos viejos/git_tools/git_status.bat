@echo off
echo ========================================
echo   ESTADO DEL REPOSITORIO
echo ========================================
echo.

cd /d "%~dp0"

echo Archivos modificados:
echo ------------------------------------
git status
echo.

echo ------------------------------------
echo Ultimos 5 commits:
echo ------------------------------------
git log --oneline -5 --graph --decorate
echo.

echo ------------------------------------
echo Configuracion:
echo ------------------------------------
echo Usuario: 
git config user.name
echo Email: 
git config user.email
echo Remote: 
git remote get-url origin
echo.

pause
