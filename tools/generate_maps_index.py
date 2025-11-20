#!/usr/bin/env python3
"""
Genera `src/database/maps_index.json` a partir de los JSONs en
`src/database/mapas` y las imágenes en `assets/maps`.

Salida:
- `src/database/maps_index.json` con entradas:
  { "id": ..., "nombre": ..., "categoria": ..., "imagen": ..., "ruta_json": ... }

Uso: ejecutar desde la raíz del proyecto.
"""
import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'
ASSETS_MAPS = ROOT / 'assets' / 'maps'
OUT_FILE = ROOT / 'src' / 'database' / 'maps_index.json'


def find_image_for_map(categoria, imagen_nombre):
    # intenta resolver ruta completa probando en assets/<categoria> y subcarpetas
    base = ASSETS_MAPS / categoria
    if not base.exists():
        return None
    # Si imagen_nombre ya incluye subcarpeta, probar directo
    candidate = base / imagen_nombre
    if candidate.exists():
        return str(candidate.relative_to(ROOT))
    # Buscar recursivamente por nombre de archivo
    for p in base.rglob('*'):
        if p.is_file() and p.name == imagen_nombre:
            return str(p.relative_to(ROOT))
    return None


def scan_maps():
    entries = []
    if not DB_MAPS.exists():
        print('No existe', DB_MAPS)
        return entries

    for categoria_dir in DB_MAPS.iterdir():
        if not categoria_dir.is_dir():
            continue
        categoria = categoria_dir.name
        for json_file in categoria_dir.glob('*.json'):
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f'ERROR parseando {json_file}:', e)
                continue
            map_id = data.get('id') or json_file.stem
            nombre = data.get('nombre') or map_id
            imagen = data.get('imagen') or ''
            imagen_ruta = None
            if imagen:
                imagen_ruta = find_image_for_map(categoria, imagen)

            entries.append({
                'id': map_id,
                'nombre': nombre,
                'categoria': categoria,
                'imagen': imagen if imagen else None,
                'imagen_ruta': imagen_ruta,
                'ruta_json': str(json_file.relative_to(ROOT))
            })

    return entries


def main():
    entries = scan_maps()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Escrito', OUT_FILE, 'con', len(entries), 'entradas')


if __name__ == '__main__':
    main()
