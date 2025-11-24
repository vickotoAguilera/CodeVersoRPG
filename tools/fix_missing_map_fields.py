#!/usr/bin/env python3
"""
Fix automatico para JSON de mapas: añade `id` desde el nombre de archivo si falta,
y rellena `imagen` si se detecta una imagen correspondiente en `assets/maps`.

Soporta:
  --dry-run  : no modifica archivos, solo muestra los cambios propuestos
  --apply    : aplica los cambios (respalda los archivos con .bak)

Uso:
  python tools/fix_missing_map_fields.py --dry-run
  python tools/fix_missing_map_fields.py --apply
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'
ASSETS_MAPS = ROOT / 'assets' / 'maps'

COMMON_EXT = ['.png', '.jpg', '.jpeg']


def find_image_for_map(categoria_rel, base_name):
    # Buscar en assets/maps/<categoria_rel> recursivamente
    cat_path = ASSETS_MAPS / categoria_rel
    if cat_path.exists():
        for ext in COMMON_EXT:
            for p in cat_path.rglob(base_name + ext):
                return p
    # Buscar globalmente
    for ext in COMMON_EXT:
        for p in ASSETS_MAPS.rglob(base_name + ext):
            return p
    return None


def process_file(path: Path, apply_changes: bool):
    changed = False
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, f'ERROR parseando {path}: {e}'

    base = path.stem
    props = []

    if 'id' not in data or not data.get('id'):
        props.append(('id', base))
        data['id'] = base
        changed = True

    if 'imagen' not in data or not data.get('imagen'):
        # categoria_rel es el parent relativo a src/database/mapas
        try:
            categoria_rel = str(path.parent.relative_to(DB_MAPS))
        except Exception:
            categoria_rel = ''
        found = find_image_for_map(categoria_rel, base)
        if found:
            rel = found.relative_to(ROOT)
            props.append(('imagen', str(found.name)))
            data['imagen'] = str(found.name)
            changed = True

    if changed and apply_changes:
        # backup
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    message = None
    if changed:
        message = f'MODIFICADO: {path} -> ' + ', '.join([f"{k}='{v}'" for k, v in props])
    else:
        message = f'OK: {path} (sin cambios)'

    return changed, message


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', help='No aplicar cambios')
    p.add_argument('--apply', action='store_true', help='Aplicar cambios (se crean .bak)')
    args = p.parse_args()

    if args.apply and args.dry_run:
        print('No usar --dry-run y --apply al mismo tiempo')
        sys.exit(2)

    apply_changes = args.apply

    files = list(DB_MAPS.rglob('*.json'))
    if not files:
        print('No se encontraron archivos en', DB_MAPS)
        sys.exit(0)

    total_changed = 0
    reports = []
    for f in files:
        changed, msg = process_file(f, apply_changes)
        reports.append((f, changed, msg))
        if changed:
            total_changed += 1

    # Mostrar resultados
    for f, changed, msg in reports:
        print(msg)

    print(f'Procesados {len(files)} archivos. Cambios propuestos/aplicados: {total_changed}')
    if total_changed > 0 and not apply_changes:
        print('\nEjecútalo con --apply para aplicar los cambios y crear backups (.bak).')

    if total_changed == 0:
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
