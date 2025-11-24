from pathlib import Path
import json

mapas = list(Path('src/database/mapas').rglob('*.json'))
print(f"Total de mapas: {len(mapas)}\n")

for m in mapas:
    try:
        data = json.load(open(m, encoding='utf-8'))
        num_muros = len(data.get('muros', []))
        if num_muros > 0:
            print(f"✓ {m.name}: {num_muros} muros")
            print(f"  Ruta: {m}")
    except Exception as e:
        print(f"✗ Error en {m.name}: {e}")

print("\n--- Mapas sin muros ---")
for m in mapas:
    try:
        data = json.load(open(m, encoding='utf-8'))
        num_muros = len(data.get('muros', []))
        if num_muros == 0:
            print(f"  {m.name}: 0 muros")
    except:
        pass
