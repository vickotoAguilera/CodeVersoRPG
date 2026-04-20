@echo off
chcp 65001 >nul
echo ========================================
echo   CONFIGURACION RAPIDA DE GIT
echo   (Version simplificada)
echo ========================================
echo.

cd /d "%~dp0.."

REM Verificar Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git no instalado. Descarga desde: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Inicializar si no existe
if not exist ".git" (
    echo Inicializando Git...
    git init
    git branch -M main
)

REM Configurar remote si no existe
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin https://github.com/vickotoAguilera/CodeVersoRPG.git
)

REM Configurar usuario (usa valores por defecto si ya existen)
for /f "delims=" %%i in ('git config user.name') do set current_user=%%i
if "%current_user%"=="" (
    git config user.name "vickotoAguilera"
    git config user.email "victoraguileramunoz@gmail.com"
    echo ✓ Usuario configurado: vickotoAguilera
) else (
    echo ✓ Usuario ya configurado: %current_user%
)

echo.
echo ✅ CONFIGURACION COMPLETADA
echo.
echo Para sincronizar con GitHub ejecuta:
echo    git pull origin main --allow-unrelated-histories
echo    git push origin main
echo.
pause
