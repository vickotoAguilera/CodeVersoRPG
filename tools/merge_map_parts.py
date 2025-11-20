#!/usr/bin/env python3
"""Merge tool para unir parciales (muros, portales, spawns, cofres)
en los JSON finales de `src/database/mapas`.

Uso:
  python tools/merge_map_parts.py [--dry-run] [--apply]

Comportamiento:
  - Recorre `src/database/mapas/**/*.json` y por cada mapa busca parciales
    en `src/database/muros`, `src/database/portales`, `src/database/spawns`, `src/database/cofres`.
  - Si existe un parcial y su lista no está vacía, reemplaza la sección
    correspondiente en el JSON final (por ejemplo, `muros`, `portales`, `zonas_batalla` o `spawns`, `cofres`).
  - Valida campos obvios (p.ej. portal con `mapa_destino` vacío) y reporta warnings.
  - Si se llama con `--apply`, sobrescribe los JSON finales; si no, sólo imprime el plan (dry-run).
"""
import os
import json
from pathlib import Path
import argparse
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'
PARTIAL_DIRS = {
    'muros': ROOT / 'src' / 'database' / 'muros',
    'portales': ROOT / 'src' / 'database' / 'portales',
    'spawns': ROOT / 'src' / 'database' / 'spawns',
    'cofres': ROOT / 'src' / 'database' / 'cofres'
}

def load_partials():
    """Carga todos los parciales y los indexa por nombre_mapa o por filename base."""
    partials = {k: {} for k in PARTIAL_DIRS}
    for key, d in PARTIAL_DIRS.items():
        if not d.exists():
            continue
        for p in d.glob('*.json'):
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"ERROR parseando parcial {p}: {e}")
                continue
            # Nombre de mapa preferido dentro del JSON
            map_name = data.get('nombre_mapa') or data.get('id') or p.stem
            partials[key][map_name] = data
            # también indexar por stem (sin sufijos)
            partials[key][p.stem] = data
    return partials

def find_final_maps():
    maps = []
    if not DB_MAPS.exists():
        return maps
    for jf in DB_MAPS.rglob('*.json'):
        maps.append(jf)
    return maps

def merge_for_map(json_path, partials, apply=False):
    rel = json_path.relative_to(ROOT)
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
    except Exception as e:
        return {'path': str(rel), 'error': f'parse_error: {e}'}

    map_id = data.get('id') or json_path.stem
    report = {'path': str(rel), 'map': map_id, 'changes': [], 'warnings': []}

    # For each type, check partial
    # MUROS
    muros_partial = partials.get('muros', {}).get(map_id) or partials.get('muros', {}).get(f'{map_id}_muros')
    if muros_partial and muros_partial.get('muros'):
        report['changes'].append('muros')
        if apply:
            data['muros'] = muros_partial.get('muros', [])

    # PORTALES
    portales_partial = partials.get('portales', {}).get(map_id) or partials.get('portales', {}).get(f'{map_id}_portales')
    if portales_partial and portales_partial.get('portales'):
        report['changes'].append('portales')
        if apply:
            data['portales'] = portales_partial.get('portales', [])
    # validate portales
    portales_to_check = data.get('portales', [])
    for p in portales_to_check:
        destino = p.get('mapa_destino') if isinstance(p, dict) else None
        if destino is None or (isinstance(destino, str) and destino.strip() == ''):
            report['warnings'].append(f"portal sin mapa_destino: {p}")

    # SPAWNS (zonas_batalla or spawns)
    spawns_partial = partials.get('spawns', {}).get(map_id) or partials.get('spawns', {}).get(f'{map_id}_spawns')
    if spawns_partial:
        # decide target key: if final map uses 'zonas_batalla' prefer that, else 'spawns'
        target_key = 'zonas_batalla' if 'zonas_batalla' in data or 'zonas_batalla' in spawns_partial else 'spawns'
        if spawns_partial.get('spawns') or spawns_partial.get('zonas_batalla'):
            report['changes'].append(target_key)
            if apply:
                # Prefer 'zonas_batalla' from partial if present
                if 'zonas_batalla' in spawns_partial:
                    data['zonas_batalla'] = spawns_partial.get('zonas_batalla')
                elif 'spawns' in spawns_partial:
                    data['zonas_batalla'] = spawns_partial.get('spawns')

    # COFRES
    cofres_partial = partials.get('cofres', {}).get(map_id) or partials.get('cofres', {}).get(f'{map_id}_cofres')
    if cofres_partial and cofres_partial.get('cofres'):
        report['changes'].append('cofres')
        if apply:
            data['cofres'] = cofres_partial.get('cofres', [])

    # If apply, write back
    if apply and report['changes']:
        try:
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            report['applied'] = True
        except Exception as e:
            report['error'] = f'write_error: {e}'

    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Aplicar cambios (por defecto dry-run)')
    parser.add_argument('--map', help='Procesar sólo este map id (opcional)')
    args = parser.parse_args()

    partials = load_partials()
    maps = find_final_maps()
    reports = []
    for m in maps:
        map_id = None
        try:
            d = json.loads(m.read_text(encoding='utf-8'))
            map_id = d.get('id') or m.stem
        except Exception:
            map_id = m.stem
        if args.map and args.map != map_id:
            continue
        r = merge_for_map(m, partials, apply=args.apply)
        reports.append(r)

    # Summarize
    changed = [r for r in reports if r.get('changes')]
    warnings = [r for r in reports if r.get('warnings')]
    errors = [r for r in reports if r.get('error')]

    print('=== Merge Map Parts Report ===')
    print(f'Total maps scanned: {len(reports)}')
    print(f'Maps with changes: {len(changed)}')
    for r in changed:
        print('-', r['map'], 'changes:', r['changes'], 'applied' if r.get('applied') else '(dry)')

    print(f'Warnings: {len(warnings)}')
    for r in warnings:
        print('-', r['map'], '->', r['warnings'])

    if errors:
        print(f'Errors: {len(errors)}')
        for r in errors:
            print('-', r['path'], r.get('error'))

    if args.apply:
        # Update maps index
        gen = ROOT / 'tools' / 'generate_maps_index.py'
        if gen.exists():
            print('\nActualizando maps_index.json...')
            # Usar subprocess.run con lista de argumentos para evitar problemas
            # con rutas que contienen espacios (p.ej. "C:\Program Files\...")
            try:
                subprocess.run([sys.executable, str(gen)], check=False)
            except Exception:
                # Fallback por compatibilidad: intentar vía os.system si falla
                os.system(f'"{sys.executable}" "{str(gen)}"')

if __name__ == '__main__':
    main()
