"""
Script de diagnóstico para verificar cómo se cargan los cofres
"""

import json
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO: Carga de Cofres")
print("=" * 60)

# 1. Ver qué hay en cofres_db.json
print("\n[1/3] Verificando cofres_db.json...")
try:
    with open('src/database/cofres_db.json', 'r', encoding='utf-8') as f:
        cofres_db = json.load(f)
    
    cofres_mapa = cofres_db.get("cofres_mapa", {})
    print(f"   Cofres en DB: {list(cofres_mapa.keys())[:10]}")  # Primeros 10
    
    # Ver un ejemplo
    if cofres_mapa:
        primer_id = list(cofres_mapa.keys())[0]
        print(f"\n   Ejemplo de cofre '{primer_id}':")
        print(f"   {json.dumps(cofres_mapa[primer_id], indent=4, ensure_ascii=False)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# 2. Ver qué hay en el mapa unificado
print("\n[2/3] Verificando mapa_pradera_unificado.json...")
try:
    with open('src/database/mapas_unificados/mapa_pradera_unificado.json', 'r', encoding='utf-8') as f:
        mapa_data = json.load(f)
    
    cofres = mapa_data.get("cofres", [])
    print(f"   Cofres en mapa: {len(cofres)}")
    
    if cofres:
        print(f"\n   Primer cofre:")
        print(f"   {json.dumps(cofres[0], indent=4, ensure_ascii=False)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# 3. Simular la lógica de carga
print("\n[3/3] Simulando lógica de carga...")
try:
    if cofres:
        for cofre_data in cofres:
            # Simular línea 369 de mapa.py
            id_cofre = cofre_data.get("id_cofre") or cofre_data.get("id") or cofre_data.get("cofre_id") or cofre_data.get("tipo")
            print(f"\n   Cofre encontrado:")
            print(f"     - id_cofre extraído: '{id_cofre}'")
            print(f"     - Campos disponibles: {list(cofre_data.keys())}")
            
            # Verificar si existe en DB
            if id_cofre in cofres_mapa:
                print(f"     - ✓ Existe en cofres_db.json")
                print(f"     - Tiene sprites: cerrado={cofres_mapa[id_cofre].get('sprite_cerrado')}, abierto={cofres_mapa[id_cofre].get('sprite_abierto')}")
            else:
                print(f"     - ✗ NO existe en cofres_db.json")
                print(f"     - IDs disponibles en DB: {list(cofres_mapa.keys())[:5]}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 60)
