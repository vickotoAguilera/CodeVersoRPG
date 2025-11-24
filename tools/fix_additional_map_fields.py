#!/usr/bin/env python3
"""
Rellena campos faltantes comunes en mapas:
- `portales[].categoria_destino` -> por defecto la categoría del mapa si falta
- `portales[].caja.w` / `portales[].caja.h` o `w`/`h` directos -> añadir valores por defecto
- `muros` y `zonas_batalla`: asegurar `w`/`h` si faltan

Soporta --dry-run y --apply (crea backups .bak)
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'


def ensure_box(d: dict, defaults=(16,16)):
    # Asegura que exista w/h en dict o en subdict 'caja'
    changed = False
    if 'caja' in d and isinstance(d['caja'], dict):
        c = d['caja']
        if 'w' not in c:
            c['w'] = defaults[0]
            changed = True
        if 'h' not in c:
            c['h'] = defaults[1]
            changed = True
    else:
        # check direct w/h
        if 'x' in d and 'y' in d:
            if 'w' not in d:
                d['w'] = defaults[0]; changed = True
            if 'h' not in d:
                d['h'] = defaults[1]; changed = True
    return changed


def process_map_file(path: Path, apply: bool):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, f'ERROR parsing {path}: {e}'

    changed = False
    # infer map category relative path
    try:
        categoria_rel = str(path.parent.relative_to(DB_MAPS))
    except Exception:
        categoria_rel = ''

    # Portales
    portales = data.get('portales', [])
    for p in portales:
        # categoria_destino default
        if 'categoria_destino' not in p or not p.get('categoria_destino'):
            p['categoria_destino'] = categoria_rel
            changed = True
        # ensure box dims
        if ensure_box(p):
            changed = True

    # Muros
    muros = data.get('muros', [])
    for m in muros:
        if ensure_box(m, defaults=(32,32)):
            changed = True

    # Zonas de batalla
    zonas = data.get('zonas_batalla', [])
    for z in zonas:
        if ensure_box(z, defaults=(64,64)):
            changed = True

    if changed and apply:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    msg = 'MOD' if changed else 'OK'
    return changed, f"{msg}: {path}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    if args.apply and args.dry_run:
        print('No usar --dry-run y --apply simultáneamente')
        sys.exit(2)

    files = list(DB_MAPS.rglob('*.json'))
    total = 0
    changes = []
    for f in files:
        ch, msg = process_map_file(f, args.apply)
        print(msg)
        if ch:
            total += 1
            changes.append(str(f))

    print(f'Procesados {len(files)} archivos. Cambios: {total}')
    if total and not args.apply:
        print('Ejecuta con --apply para escribir cambios y crear backups (.bak)')

if __name__ == '__main__':
    main()
