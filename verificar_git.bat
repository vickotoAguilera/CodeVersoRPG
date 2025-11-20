@echo off
echo ========================================
echo   CONFIGURACION DE GIT
echo ========================================
echo.

cd /d "%~dp0"

echo Tu nombre configurado en Git:
git config user.name
echo.

echo Tu email configurado en Git:
git config user.email
echo.

echo Repositorio remoto:
git remote get-url origin
echo.

echo ========================================
pause
