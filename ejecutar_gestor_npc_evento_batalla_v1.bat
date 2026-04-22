@echo off
REM Lanzador del Gestor NPC Evento Batalla - Editor Canvas Doble
REM Proposito: abrir editor visual para configurar batallas de NPC con canvas doble

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Activar venv
call .venv\Scripts\activate.bat

REM Ejecutar editor
python gestor_npc_evento_batalla_v1.py

pause
