@echo off
echo Verificando sintaxis de todos los archivos Python...
python -c "import py_compile, os, sys; [py_compile.compile(os.path.join(root, f), doraise=True) if f.endswith('.py') else None for root, dirs, files in os.walk('.') for f in files]"
if %errorlevel% neq 0 (
    echo.
    echo ❌ Se encontraron errores de sintaxis.
    pause
    exit /b 1
)
echo.
echo ✅ Todos los archivos tienen sintaxis correcta.
pause
