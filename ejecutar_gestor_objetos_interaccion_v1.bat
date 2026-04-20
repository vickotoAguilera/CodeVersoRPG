@echo off
cd /d "%~dp0"
set PYTHONUTF8=1

set "PYEXE="
if exist ".venv\Scripts\python.exe" (
	set "PYEXE=.venv\Scripts\python.exe"
) else (
	where py >nul 2>&1
	if not errorlevel 1 (
		set "PYEXE=py -3"
	) else (
		set "PYEXE=python"
	)
)

%PYEXE% -c "import pygame" >nul 2>&1
if errorlevel 1 (
	echo [INFO] pygame no esta instalado. Instalando pygame-ce...
	%PYEXE% -m pip install pygame-ce
	if errorlevel 1 (
		echo [ERROR] No se pudo instalar pygame-ce.
		pause
		exit /b 1
	)
)

if "%~1"=="" (
	%PYEXE% gestor_objetos_interaccion_v1.py editor
) else (
	%PYEXE% gestor_objetos_interaccion_v1.py %*
)
pause
