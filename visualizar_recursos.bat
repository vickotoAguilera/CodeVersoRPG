@echo off
title Lanzador del Visualizador Maestro de Sprites
cd /d "%~dp0"
echo ============================================================
echo      INICIALIZANDO VISUALIZADOR MAESTRO DE SPRITES
echo ============================================================
echo.
echo Verificando dependencias...
python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Pygame no esta instalado. Instalandolo ahora...
    python -m pip install pygame
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar Pygame.
        pause
        exit /b 1
    )
)

echo Escaneando recursos en carpeta actual...
echo.
echo Iniciando aplicacion...
python visualizador_recursos.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La aplicacion se cerro inesperadamente.
    pause
)
