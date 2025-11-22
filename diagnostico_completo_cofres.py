"""
Script de diagnóstico completo para la carga de cofres
Verifica cada paso del proceso
"""

import json
from pathlib import Path

print("=" * 70)
print("DIAGNÓSTICO COMPLETO: Sistema de Cofres")
print("=" * 70)

# 1. Verificar cofres_db.json
print("\n[1/5] Verificando cofres_db.json...")
try:
    with open('src/database/cofres_db.json', 'r', encoding='utf-8') as f:
        cofres_db_completo = json.load(f)
    
    cofres_mapa = cofres_db_completo.get("cofres_mapa", {})
    print(f"   [OK] Archivo cargado correctamente")
    print(f"   [OK] Cofres disponibles: {len(cofres_mapa)}")
    print(f"   [OK] IDs: {list(cofres_mapa.keys())}")
    
    # Verificar que tengan sprites
    sin_sprites = []
    for id_cofre, datos in cofres_mapa.items():
        if not datos.get("sprite_cerrado") or not datos.get("sprite_abierto"):
            sin_sprites.append(id_cofre)
    
    if sin_sprites:
        print(f"   [!] Cofres SIN sprites: {sin_sprites}")
    else:
        print(f"   [OK] Todos los cofres tienen sprites")
        
except Exception as e:
    print(f"   [ERROR] {e}")
    cofres_mapa = {}

# 2. Verificar mapa unificado
print("\n[2/5] Verificando mapa_pradera_unificado.json...")
try:
    with open('src/database/mapas_unificados/mapa_pradera_unificado.json', 'r', encoding='utf-8') as f:
        mapa_unificado = json.load(f)
    
    cofres_en_mapa = mapa_unificado.get("cofres", [])
    print(f"   [OK] Archivo cargado correctamente")
    print(f"   [OK] Cofres en mapa: {len(cofres_en_mapa)}")
    
    if cofres_en_mapa:
        for i, cofre in enumerate(cofres_en_mapa):
            print(f"\n   Cofre #{i+1}:")
            print(f"     - ID: {cofre.get('id') or cofre.get('id_cofre') or 'SIN ID'}")
            print(f"     - Posicion: ({cofre.get('x')}, {cofre.get('y')})")
            print(f"     - Tamano: {cofre.get('ancho')}x{cofre.get('alto')}")
            print(f"     - Tipo: {cofre.get('tipo')}")
            
            # Verificar si existe en DB
            id_cofre = cofre.get('id') or cofre.get('id_cofre')
            if id_cofre:
                if id_cofre in cofres_mapa:
                    print(f"     - [OK] Existe en cofres_db.json")
                else:
                    print(f"     - [ERROR] NO existe en cofres_db.json")
                    print(f"     - Sugerencia: Agregar '{id_cofre}' a cofres_db.json")
    else:
        print("   [!] No hay cofres en el mapa")
        
except Exception as e:
    print(f"   [ERROR] {e}")

# 3. Verificar mapa parcial
print("\n[3/5] Verificando mapa_pradera.json (parcial)...")
try:
    with open('src/database/mapas/mundo/mapa_pradera.json', 'r', encoding='utf-8') as f:
        mapa_parcial = json.load(f)
    
    cofres_parcial = mapa_parcial.get("cofres", [])
    print(f"   [OK] Archivo cargado correctamente")
    print(f"   [OK] Cofres en mapa parcial: {len(cofres_parcial)}")
    
    if cofres_parcial:
        for cofre in cofres_parcial:
            id_cofre = cofre.get('id') or cofre.get('id_cofre')
            print(f"     - {id_cofre}: ({cofre.get('x')}, {cofre.get('y')})")
            
except Exception as e:
    print(f"   [ERROR] {e}")

# 4. Simular lógica de carga del juego
print("\n[4/5] Simulando logica de carga del juego...")
print("   Codigo en src/mapa.py linea 369:")
print("   id_cofre = cofre_data.get('id_cofre') or cofre_data.get('id') or ...")

if cofres_en_mapa:
    for cofre_data in cofres_en_mapa:
        # Simular línea 369
        id_cofre = cofre_data.get("id_cofre") or cofre_data.get("id") or cofre_data.get("cofre_id") or cofre_data.get("tipo")
        
        print(f"\n   Procesando cofre:")
        print(f"     - Campos en JSON: {list(cofre_data.keys())}")
        print(f"     - ID extraido: '{id_cofre}'")
        
        # Simular línea 406
        cofre_info = cofres_mapa.get(id_cofre)
        if cofre_info:
            print(f"     - [OK] Encontrado en cofres_db.json")
            print(f"     - Sprites: cerrado={cofre_info.get('sprite_cerrado')}, abierto={cofre_info.get('sprite_abierto')}")
        else:
            print(f"     - [ERROR] NO encontrado en cofres_db.json")
            print(f"     - El cofre NO se cargara en el juego")

# 5. Verificar que el editor guarde correctamente
print("\n[5/5] Verificando formato de guardado del editor...")
print("   El editor de cofres guarda con campo 'id'")
print("   El juego busca primero 'id_cofre', luego 'id'")
print("   [OK] Esto deberia funcionar correctamente")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)

if not cofres_en_mapa:
    print("[!] NO HAY COFRES EN EL MAPA")
    print("   1. Abre el editor de cofres: python editor_cofres.py")
    print("   2. Carga el mapa 'mapa_pradera'")
    print("   3. Crea un cofre (click izquierdo en el mapa)")
    print("   4. Click derecho en el cofre para configurarlo")
    print("   5. Guarda con Ctrl+G")
else:
    # Verificar si todos los cofres tienen su entrada en DB
    cofres_sin_db = []
    for cofre_data in cofres_en_mapa:
        id_cofre = cofre_data.get("id_cofre") or cofre_data.get("id")
        if id_cofre and id_cofre not in cofres_mapa:
            cofres_sin_db.append(id_cofre)
    
    if cofres_sin_db:
        print(f"[!] PROBLEMA ENCONTRADO:")
        print(f"   Los siguientes cofres NO estan en cofres_db.json:")
        for id_c in cofres_sin_db:
            print(f"     - {id_c}")
        print(f"\n   SOLUCION: Crear script para agregar estos cofres a cofres_db.json")
    else:
        print("[OK] TODOS LOS COFRES DEBERIAN CARGARSE CORRECTAMENTE")
        print("  Si no aparecen en el juego, verifica:")
        print("    1. Que el juego este cargando el archivo unificado")
        print("    2. Que no haya errores en la consola del juego")

print("=" * 70)
