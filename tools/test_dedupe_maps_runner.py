import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('editor_portales', Path('editor_portales.py').resolve())
mod = importlib.util.module_from_spec(spec)
sys.modules['editor_portales'] = mod
spec.loader.exec_module(mod)

EditorPortales = mod.EditorPortales

maps = EditorPortales._buscar_mapas(None, Path('assets/maps/ciudades_y_pueblos'), 'ciudades_y_pueblos')
print('Total mapas detectados en categoría ciudades_y_pueblos:', len(maps))
for m in maps:
    print('-', m.nombre, '->', m.ruta, 'sub:', m.subcarpeta)
