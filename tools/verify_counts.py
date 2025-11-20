import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('editor_unificado_mod', str(Path('editor_unificado.py').resolve()))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EditorUnificado = mod.EditorUnificado

ed = EditorUnificado()

# Mostrar qué mapa auto-carga el editor (el de mayor cantidad de elementos)
print('Mapas disponibles:', len(ed.mapas_disponibles))
for m in ed.mapas_disponibles:
    # Mostrar ruta y conteos desde el JSON
    try:
        import json
        data = json.load(open(m.ruta_json, encoding='utf-8'))
        print(m.ruta_json, '-> muros', len(data.get('muros', [])), 'portales', len(data.get('portales', [])), 'zonas', len(data.get('zonas_batalla', [])))
    except Exception as e:
        print('ERR', m.ruta_json, e)

# Cargar el mapa que el editor hubiera elegido: el de mayor count
mejor = None
maxc = 0
for m in ed.mapas_disponibles:
    try:
        import json
        data = json.load(open(m.ruta_json, encoding='utf-8'))
        c = len(data.get('muros', [])) + len(data.get('portales', [])) + len(data.get('zonas_batalla', []))
        if c > maxc:
            maxc = c; mejor = m
    except:
        continue

print('\nMejor mapa elegido:', mejor.ruta_json if mejor else None, 'con', maxc, 'elementos')
ed.cargar_mapa(mejor)

print('\nElementos internos:')
from collections import Counter
cnt = Counter([e.tipo for e in ed.elementos])
print(cnt)

print('\nConteos usados en panel:')
singular_map = {'muros': 'muro','portales': 'portal','spawns': 'spawn','cofres': 'cofre','npcs': 'npc','eventos': 'evento'}
for capa in ed.capas_visibles:
    tipo = singular_map.get(capa, capa[:-1])
    print(capa, len([e for e in ed.elementos if e.tipo == tipo]))
