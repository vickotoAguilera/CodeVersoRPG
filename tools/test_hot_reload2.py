import importlib.util
from pathlib import Path
import os
import time

path = Path('editor_unificado.py').resolve()
spec = importlib.util.spec_from_file_location('editor_unificado_mod', str(path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

EditorUnificado = module.EditorUnificado

print('Instanciando EditorUnificado (esto abrirá una ventana Pygame momentáneamente)')
editor = EditorUnificado()

# Cargar mapa_herrero
mapa = None
for m in editor.mapas_disponibles:
    if m.nombre == 'mapa_herrero':
        mapa = m
        break

if not mapa:
    print('mapa_herrero no encontrado')
    raise SystemExit(1)

editor.cargar_mapa(mapa)
print('Antes:', editor.archivos_modificados)

# Tocar el JSON para forzar cambio
ruta = str(mapa.ruta_json)
print('Tocando:', ruta)
os.utime(ruta, None)

# Forzar chequeo
editor.ultimo_check = 0
editor._check_hot_reload()

print('Después, elementos=', len(editor.elementos))

# Limpiar
try:
    editor.guardar_cambios()
except Exception:
    pass
import pygame
pygame.quit()
