@echo off
echo ========================================
echo   PUSH COMPLETO A GITHUB
echo ========================================
echo.

cd /d "%~dp0"

REM Organizar documentacion
python organizar_docs.py

REM Mensaje automatico
set mensaje=update: Cambios del %date% %time:~0,5%

echo [1/4] Agregando archivos...
git add .

echo [2/4] Creando commit...
git commit -m "%mensaje%"

echo [3/4] Subiendo rama actual...
git push

echo [4/4] Actualizando rama main...
REM Guardar rama actual
for /f "tokens=*" %%i in ('git branch --show-current') do set rama_actual=%%i

REM Cambiar a main, hacer merge y subir
git checkout main
git merge %rama_actual% -m "Merge: %mensaje%"
git push origin main

REM Volver a la rama original
git checkout %rama_actual%

echo.
echo ========================================
echo   SUBIDO CON EXITO!
echo ========================================
echo Rama actual: %rama_actual%
echo Rama main: ACTUALIZADA
echo Mensaje: %mensaje%
echo.
pause
