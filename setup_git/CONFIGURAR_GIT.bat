@echo off
chcp 65001 >nul
echo ========================================
echo   CONFIGURACION AUTOMATICA DE GIT
echo   CodeVersoRPG
echo ========================================
echo.

REM Ir al directorio del proyecto (un nivel arriba del script)
cd /d "%~dp0.."

echo [PASO 1/6] Verificando si Git esta instalado...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Git no esta instalado en este PC
    echo.
    echo Por favor instala Git desde: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo ✓ Git encontrado
echo.

echo [PASO 2/6] Verificando si ya existe un repositorio Git...
if exist ".git" (
    echo ✓ Repositorio Git ya existe
    echo.
    goto :configure_remote
) else (
    echo ⚠ No hay repositorio Git, inicializando...
    git init
    if errorlevel 1 (
        echo ❌ Error al inicializar Git
        pause
        exit /b 1
    )
    echo ✓ Repositorio Git inicializado
    echo.
)

:configure_remote
echo [PASO 3/6] Configurando usuario de Git...
echo.

REM Configurar con tus datos automaticamente
set git_user=vickotoAguilera
set git_email=victoraguileramunoz@gmail.com

git config user.name "%git_user%"
git config user.email "%git_email%"
echo ✓ Usuario configurado: %git_user% (%git_email%)
echo.

echo [PASO 4/6] Configurando repositorio remoto...
REM Verificar si ya existe el remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Agregando remote de GitHub...
    git remote add origin https://github.com/vickotoAguilera/CodeVersoRPG.git
    echo ✓ Remote agregado
) else (
    echo ✓ Remote ya existe
)
echo.

echo [PASO 5/6] Configurando rama principal...
git branch -M main
echo ✓ Rama 'main' configurada
echo.

echo.
echo Descargando desde GitHub...
git pull origin main --allow-unrelated-histories
if errorlevel 1 (
    echo.
    echo ⚠ Hubo un problema al sincronizar
    echo   Esto es normal si hay conflictos
    echo   Revisa los archivos y resuelve los conflictos manualmente
    echo.
) else (
    echo ✓ Sincronizado exitosamente
    echo.
)

:end
echo ========================================
echo   CONFIGURACION COMPLETADA
echo ========================================
echo.
echo Tu repositorio esta listo para usar!
echo.
echo Comandos utiles:
echo   - git status          Ver cambios
echo   - git add .           Agregar archivos
echo   - git commit -m "..."  Hacer commit
echo   - git push origin main Subir a GitHub
echo.
echo O usa los scripts .bat del proyecto:
echo   - git_status.bat
echo   - git_push.bat
echo   - git_pull.bat
echo.
pause
