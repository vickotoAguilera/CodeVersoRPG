@echo off
echo ========================================
echo   PASO 1: CREAR RESPALDO
echo ========================================
echo.
echo Este script creara una rama de respaldo
echo con la fecha y hora actual.
echo.
pause

cd /d "%~dp0\.."

REM Obtener fecha y hora para el nombre de la rama
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set FECHA=%datetime:~0,8%
set HORA=%datetime:~8,6%
set RAMA_RESPALDO=respaldo-%FECHA%-%HORA%

echo.
echo Creando rama de respaldo: %RAMA_RESPALDO%
git branch %RAMA_RESPALDO%

echo.
echo ========================================
echo   RESPALDO CREADO EXITOSAMENTE!
echo ========================================
echo Rama creada: %RAMA_RESPALDO%
echo.
echo Ahora puedes trabajar tranquilo en la rama 'main'.
echo Si algo sale mal, usa el script 2_VER_RESPALDOS.bat
echo.
pause
