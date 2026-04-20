@echo off
title ✨ Sprite Editor con Auto-Splitter Magico - CodeVerso RPG
color 0B
echo.
echo ===================================================
echo   SPRITE SHEET EDITOR - CON AUTO-SPLITTER MAGICO
echo ===================================================
echo.
echo  NUEVO: Presiona [A] para detectar sprites SOLO!
echo.
echo Iniciando...
echo.
cd /d "%~dp0"
python sprite_sheet_editor.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el editor
    echo Verifica que Python y pygame esten instalados
    echo.
    pause
)
