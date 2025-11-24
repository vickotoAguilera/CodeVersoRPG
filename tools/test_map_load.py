#!/usr/bin/env python3
"""
Intenta instanciar `src.mapa.Mapa` para cada entrada del índice `src/database/maps_index.json`.
Usa un backend de display 'dummy' si es posible para evitar abrir ventanas.
"""
import os
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'src' / 'database' / 'maps_index.json'

if not INDEX.exists():
    print('maps_index.json no existe. Ejecuta tools/generate_maps_index.py primero.')
    sys.exit(1)

# Asegurar que el root del proyecto esté en sys.path para importar `src`
import sys
sys.path.insert(0, str(ROOT))

# Intentar configurar display dummy (Unix/SDL). En Windows puede o no funcionar.
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
import pygame
pygame.init()
try:
    pygame.display.set_mode((1,1))
except Exception:
    pass

from src.mapa import Mapa

with open(INDEX, 'r', encoding='utf-8') as f:
    entradas = json.load(f)

import subprocess

errores = []
helper = ROOT / 'tools' / '_load_map_subprocess.py'
for e in entradas:
    idmap = e.get('id') or e.get('ruta_json') or '<sin-id>'
    img = e.get('imagen') or e.get('imagen_ruta')
    cat = e.get('categoria')
    nombre_arch = img if img else (os.path.splitext(os.path.basename(e.get('ruta_json','')))[0] + '.png')
    print('-> Probando:', idmap, 'categoria=', cat, 'imagen=', nombre_arch)
    try:
        res = subprocess.run([sys.executable, str(helper), nombre_arch, cat], capture_output=True, text=True, timeout=20)
        out = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode == 0 and 'OK' in out:
            print('   OK')
        else:
            print('   FALLÓ (código', res.returncode, ')')
            if out: print('   STDOUT:', out)
            if err: print('   STDERR:', err)
            errores.append((idmap, res.returncode, out + '\n' + err))
    except Exception as ex:
        print('   EXCEPCIÓN EJECUTANDO SUBPROCESO:', ex)
        errores.append((idmap, str(ex)))

print('\nResumen:')
if errores:
    print('Mapas con errores:')
    for it in errores:
        print(' -', it[0], it[1])
    sys.exit(2)
else:
    print('Todos los mapas cargaron correctamente (o no arrojaron excepciones fatales).')
    sys.exit(0)
