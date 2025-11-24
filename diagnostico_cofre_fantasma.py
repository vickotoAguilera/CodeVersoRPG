"""
Script de diagnostico para verificar de donde viene el cofre fantasma
"""

import json
import os
from pathlib import Path

print("=" * 70)
print("DIAGNOSTICO: Cofre Fantasma")
print("=" * 70)

# 1. Verificar todos los archivos de pradera
print("\n[1/3] Verificando todos los archivos de mapa_pradera...")

archivos_pradera = [
    "src/database/mapas_unificados/mapa_pradera_unificado.json",
    "src/database/mapas/mundo/mapa_pradera.json"
]

for archivo in archivos_pradera:
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cofres = data.get("cofres", [])
            print(f"\n{archivo}:")
            print(f"  - Cofres: {len(cofres)}")
            if cofres:
                for cofre in cofres:
                    print(f"    * {cofre.get('id')}: ({cofre.get('x')}, {cofre.get('y')})")
        except Exception as e:
            print(f"\n{archivo}:")
            print(f"  - ERROR: {e}")
    else:
        print(f"\n{archivo}:")
        print(f"  - NO EXISTE")

# 2. Buscar archivos .pyc (cache de Python)
print("\n[2/3] Buscando archivos de cache...")
pyc_files = list(Path("src").rglob("*.pyc"))
if pyc_files:
    print(f"  Encontrados {len(pyc_files)} archivos .pyc")
    print("  Estos pueden contener datos antiguos")
else:
    print("  No hay archivos .pyc")

# 3. Verificar si hay otros archivos JSON de pradera
print("\n[3/3] Buscando otros archivos de pradera...")
otros = list(Path("src/database").rglob("*pradera*.json"))
print(f"  Archivos encontrados: {len(otros)}")
for archivo in otros:
    if "monstruos" not in str(archivo):  # Ignorar monstruos
        print(f"    - {archivo}")
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            cofres = data.get("cofres", [])
            if cofres:
                print(f"      [!] TIENE {len(cofres)} COFRES!")
        except:
            pass

print("\n" + "=" * 70)
print("SOLUCION:")
print("=" * 70)
print("Si los archivos JSON estan vacios pero aun ves el cofre:")
print("  1. Cierra el juego completamente")
print("  2. Ejecuta: python -m compileall -f src")
print("  3. Vuelve a abrir el juego")
print("\nO simplemente reinicia el juego si ya estaba abierto.")
print("=" * 70)
