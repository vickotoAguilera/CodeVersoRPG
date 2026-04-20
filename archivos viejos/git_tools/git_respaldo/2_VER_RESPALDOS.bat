@echo off
echo ========================================
echo   PASO 2: VER RESPALDOS DISPONIBLES
echo ========================================
echo.

cd /d "%~dp0\.."

echo Ramas de respaldo disponibles:
echo.
git branch | findstr "respaldo-"

echo.
echo ========================================
echo Tambien puedes ver TODOS los commits:
echo ========================================
echo.
git log --oneline -20

echo.
echo ========================================
echo   INFORMACION
echo ========================================
echo.
echo - Las ramas que empiezan con 'respaldo-' son tus puntos de restauracion
echo - Los commits muestran el historial completo de cambios
echo - Anota el nombre de la rama o ID del commit que quieres recuperar
echo.
echo Siguiente paso: Usa 3_RECUPERAR_RESPALDO.bat
echo.
pause
