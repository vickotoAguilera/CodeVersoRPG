@echo off
title Sprite Sheet Editor - CodeVerso RPG
color 0A
echo.
echo ================================================
echo   SPRITE SHEET EDITOR - CodeVerso RPG
echo ================================================
echo.
echo Iniciando editor de sprites...
echo.

python sprite_sheet_editor.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el editor
    echo Verifica que Python este instalado correctamente
    pause
) else (
    echo.
    echo Editor cerrado correctamente
)

pause
