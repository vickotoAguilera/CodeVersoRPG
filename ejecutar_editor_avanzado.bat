@echo off
title Editor de Mapas Avanzado - CodeVerso RPG
color 0A

echo ╔═══════════════════════════════════════════════════════╗
echo ║  EDITOR DE MAPAS PROFESIONAL - CodeVerso RPG          ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo Iniciando editor avanzado...
echo.

python editor_mapa_avanzado.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se pudo ejecutar el editor
    echo.
    echo Verifica que Python esté instalado y las dependencias
    pause
) else (
    echo.
    echo ✓ Editor cerrado correctamente
)

pause
