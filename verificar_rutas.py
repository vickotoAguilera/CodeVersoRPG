import os
import json
from pathlib import Path

def scan_and_report():
    print("=== VERIFICACIÓN DE RUTAS Y CONTENIDO DE MAPAS ===\n")
    
    base_db = Path('src/database/mapas')
    base_assets = Path('assets/maps')
    
    print(f"Buscando en: {base_db.absolute()}")
    
    mapas_encontrados = []
    
    # 1. Escanear src/database/mapas
    if base_db.exists():
        for json_file in base_db.rglob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                keys = list(data.keys())
                num_muros = len(data.get('muros', []))
                num_portales = len(data.get('portales', []))
                num_spawns = len(data.get('zonas_batalla', [])) + len(data.get('spawns', []))
                
                info = {
                    'path': str(json_file),
                    'name': json_file.stem,
                    'keys': keys,
                    'counts': f"Muros: {num_muros}, Portales: {num_portales}, Spawns: {num_spawns}"
                }
                mapas_encontrados.append(info)
                
                if json_file.stem == 'mapa_herrero':
                    print(f"\n[!!!] ENCONTRADO mapa_herrero.json en: {json_file}")
                    print(f"      Contenido: {info['counts']}")
                    print(f"      Claves: {keys}")
                    if 'portales' in data:
                        print(f"      Portales data: {data['portales']}")
            except Exception as e:
                print(f"Error leyendo {json_file}: {e}")

    # 2. Buscar duplicados o rutas alternativas
    print("\n--- Buscando posibles duplicados en otras carpetas ---")
    otras_rutas = ['datos/mapas', 'data/maps', 'maps', 'mapas']
    for r in otras_rutas:
        p = Path(r)
        if p.exists() and p != base_db:
            print(f"Explorando ruta alternativa: {p}")
            for json_file in p.rglob('*.json'):
                if json_file.stem == 'mapa_herrero':
                     print(f"[!!!] DUPLICADO DETECTADO en: {json_file}")

    print("\n=== FIN DEL REPORTE ===")

if __name__ == "__main__":
    scan_and_report()
