#!/usr/bin/env python3
"""
Utility para exportar un mapa desde un build temporal del editor hacia las carpetas del juego.

Uso (ejemplo):
  python tools/export_map.py --src-json out/editor_map.json --image out/mapa_prueba.png --categoria mundo

El script:
- valida el JSON mínimo
- copia la imagen a `assets/maps/<categoria>/` (creando carpeta si es necesario)
- escribe el JSON en `src/database/mapas/<categoria>/<id>.json`
- actualiza `src/database/maps_index.json` ejecutando `tools/generate_maps_index.py`
- valida el mapa con `tools/validate_map.py`
"""
import argparse
import json
import os
import shutil
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'
ASSETS_MAPS = ROOT / 'assets' / 'maps'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--src-json', required=True, help='JSON de origen (exportado por editor)')
    p.add_argument('--image', required=False, help='Ruta a la imagen del mapa (opcional)')
    p.add_argument('--categoria', required=True, help='Categoria destino (ej. mundo)')
    args = p.parse_args()

    src_json = Path(args.src_json)
    if not src_json.exists():
        print('ERROR: no existe', src_json); return

    data = json.loads(src_json.read_text(encoding='utf-8'))
    map_id = data.get('id')
    if not map_id:
        print('ERROR: el JSON de origen debe incluir "id"'); return

    categoria = args.categoria
    target_dir = DB_MAPS / categoria
    target_dir.mkdir(parents=True, exist_ok=True)

    # Imagen
    if args.image:
        src_img = Path(args.image)
        if not src_img.exists():
            print('ERROR: imagen no encontrada', src_img); return
        assets_cat = ASSETS_MAPS / categoria
        assets_cat.mkdir(parents=True, exist_ok=True)
        target_img = assets_cat / src_img.name
        shutil.copy2(src_img, target_img)
        # guardar referencia relativa
        data['imagen'] = src_img.name

    # Escribir JSON destino
    out_json = target_dir / (map_id + '.json')
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Escrito mapa en', out_json)

    # Regenerar índice
    gen = ROOT / 'tools' / 'generate_maps_index.py'
    if gen.exists():
        subprocess.run([os.sys.executable, str(gen)], check=False)

    # Validar mapa
    val = ROOT / 'tools' / 'validate_map.py'
    if val.exists():
        subprocess.run([os.sys.executable, str(val)], check=False)

    print('Export completado.')


if __name__ == '__main__':
    main()
