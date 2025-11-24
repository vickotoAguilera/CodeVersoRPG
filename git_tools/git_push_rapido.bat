@echo off
echo ========================================
echo   PUSH RAPIDO A GITHUB
echo ========================================
echo.

cd /d "%~dp0"

REM Organizar documentacion
python organizar_docs.py

REM Todo en uno con mensaje automatico
set mensaje=update: Cambios del %date% %time:~0,5%

git add .
git commit -m "%mensaje%"
git push

echo.
echo ========================================
echo   SUBIDO CON EXITO!
echo ========================================
echo Mensaje: %mensaje%
echo.
pause
