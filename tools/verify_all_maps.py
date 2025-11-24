import os, json

ROOT = os.path.abspath(os.getcwd())
DATABASE_MAPS = os.path.join(ROOT, 'src', 'database', 'mapas')
ASSETS_MAPS = os.path.join(ROOT, 'assets', 'maps')
MAPS_INDEX = os.path.join(ROOT, 'src', 'database', 'maps_index.json')

problems = []

def find_image_in_assets(imagen_name, categoria):
    # imagen_name may be 'mapa.png' or a subpath. We'll search inside assets/maps/<categoria>
    cat_dir = os.path.join(ASSETS_MAPS, categoria)
    if not os.path.isdir(cat_dir):
        return False, []
    found_paths = []
    base = os.path.basename(imagen_name)
    if not base:
        return False, []
    for root, dirs, files in os.walk(cat_dir):
        for f in files:
            if f.lower() == base.lower():
                found_paths.append(os.path.relpath(os.path.join(root, f), ROOT))
    return (len(found_paths) > 0), found_paths

# 1) Check maps_index.json entries
if os.path.exists(MAPS_INDEX):
    try:
        with open(MAPS_INDEX, 'r', encoding='utf-8') as f:
            idx = json.load(f)
        for e in idx:
            imagen = e.get('imagen') or e.get('imagen_ruta')
            ruta_json = e.get('ruta_json')
            categoria = e.get('categoria') or ''
            if not imagen:
                problems.append(('maps_index', e.get('id', '<no-id>'), 'imagen vacía', ruta_json))
            else:
                ok, paths = find_image_in_assets(imagen, categoria)
                if not ok:
                    problems.append(('maps_index', e.get('id', '<no-id>'), f'imagen no encontrada: {imagen}', categoria))
    except Exception as ex:
        problems.append(('maps_index', None, f'error leyendo indice: {ex}', None))
else:
    problems.append(('maps_index', None, 'maps_index.json no encontrado', None))

# 2) Walk all map JSONs
for root, dirs, files in os.walk(DATABASE_MAPS):
    for f in files:
        if not f.lower().endswith('.json'):
            continue
        ruta = os.path.join(root, f)
        rel_ruta = os.path.relpath(ruta, ROOT)
        try:
            with open(ruta, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
        except Exception as ex:
            problems.append(('json_parse', rel_ruta, f'error parseando JSON: {ex}', None))
            continue
        # determine category relative to mapas root
        cat = os.path.relpath(root, DATABASE_MAPS).replace('\\', '/').lstrip('./')
        # image field
        imagen = data.get('imagen')
        if imagen is None:
            # try infer from filename
            imagen = os.path.splitext(f)[0] + '.png'
            problems.append(('imagen_missing_field', rel_ruta, 'campo "imagen" ausente; usando '+imagen, None))
        if imagen == '' or imagen == '.png':
            problems.append(('imagen_vacia', rel_ruta, f'imagen inválida: "{imagen}"', None))
        else:
            ok, paths = find_image_in_assets(imagen, cat)
            if not ok:
                # also try searching across all assets if category is nested
                ok_all = False
                found_all = []
                for aroot, adirs, afiles in os.walk(ASSETS_MAPS):
                    for af in afiles:
                        if af.lower() == os.path.basename(imagen).lower():
                            ok_all = True
                            found_all.append(os.path.relpath(os.path.join(aroot, af), ROOT))
                if not ok_all:
                    problems.append(('imagen_no_en_assets', rel_ruta, f'imagen referenciada no encontrada: {imagen}', cat))
                else:
                    problems.append(('imagen_en_otro_lugar', rel_ruta, f'imagen encontrada en otras rutas: {found_all}', cat))
        # check portals
        for portal in data.get('portales', []):
            mapa_dest = portal.get('mapa_destino')
            if mapa_dest is None or (isinstance(mapa_dest, str) and mapa_dest.strip() == ''):
                problems.append(('portal_destino_vacio', rel_ruta, f'portal sin mapa_destino: {portal}', None))
        # check id fields in spawns
        for s in data.get('spawns', []):
            # check if spawn has invalid/missing coords
            if isinstance(s, dict):
                x = s.get('x')
                y = s.get('y')
                if x is None or y is None:
                    problems.append(('spawn_sin_pos', rel_ruta, f'spawn sin x/y: {s}', None))

# 3) Summarize
print('=== Informe de verificación de mapas ===')
if not problems:
    print('No se detectaron problemas en los JSON de mapas ni en el índice.')
else:
    print(f'Se detectaron {len(problems)} posibles problemas:')
    for p in problems:
        print('-', p)

# Exit code 0
