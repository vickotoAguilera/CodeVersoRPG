@echo off
echo ========================================
echo   SUBIR CAMBIOS A GITHUB
echo ========================================
echo.

cd /d "%~dp0"

REM Organizar documentacion primero
echo [1/5] Organizando documentacion...
python organizar_docs.py
echo.

REM Ver estado actual
echo [2/5] Verificando cambios...
git status
echo.

REM Agregar todos los cambios
echo [3/5] Agregando archivos...
git add .
echo.

REM Hacer commit (pide mensaje)
echo [4/5] Haciendo commit...
set /p mensaje="Escribe el mensaje del commit (ejemplo: feat: nueva funcionalidad): "
if "%mensaje%"=="" (
    echo Error: Debes escribir un mensaje de commit
    pause
    exit /b 1
)
git commit -m "%mensaje%"
echo.

REM Push a GitHub
echo [5/5] Subiendo a GitHub...
git push origin main
echo.

echo ========================================
echo   COMPLETADO EXITOSAMENTE!
echo ========================================
echo.
echo Tu codigo ha sido subido a:
echo https://github.com/vickotoAguilera/CodeVersoRPG
echo.
pause
