@echo off
echo ========================================
echo   PUSH TOTAL - SUBE TODO A GITHUB
echo ========================================
echo.

cd /d "%~dp0"

REM Organizar documentacion
echo [1/6] Organizando documentacion...
python organizar_docs.py

REM Mensaje automatico
set mensaje=update: Cambios del %date% %time:~0,5%

echo [2/6] Agregando todos los archivos...
git add .

echo [3/6] Creando commit...
git commit -m "%mensaje%"
if errorlevel 1 (
    echo No hay cambios para commitear
)

echo [4/6] Asegurando que estamos en main...
git checkout main

echo [5/6] Haciendo merge de todas las ramas...
REM Hacer merge de fix/auto-map-fixes si existe
git merge fix/auto-map-fixes -m "Merge: %mensaje%" 2>nul
if errorlevel 1 (
    echo Rama fix/auto-map-fixes ya esta mergeada o no existe
)

echo [6/6] Subiendo TODO a GitHub...
git push origin main

echo.
echo ========================================
echo   TODO SUBIDO CON EXITO!
echo ========================================
echo Rama: main
echo Mensaje: %mensaje%
echo.
echo Todos tus cambios estan en GitHub!
echo.
pause
