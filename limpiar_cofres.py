"""
Script para limpiar TODOS los cofres de los mapas
Esto dejará los mapas sin cofres para empezar desde cero
"""

import json
import os
from pathlib import Path

def limpiar_cofres():
    print("=" * 60)
    print("LIMPIEZA DE COFRES - Eliminando todos los cofres")
    print("=" * 60)
    
    archivos_modificados = 0
    cofres_eliminados = 0
    
    # 1. Limpiar mapas unificados
    print("\n[1/2] Limpiando mapas unificados...")
    dir_unificados = Path("src/database/mapas_unificados")
    if dir_unificados.exists():
        for archivo in dir_unificados.glob("*.json"):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "cofres" in data:
                    num_cofres = len(data["cofres"])
                    if num_cofres > 0:
                        data["cofres"] = []
                        
                        with open(archivo, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        print(f"   [OK] {archivo.name}: {num_cofres} cofres eliminados")
                        archivos_modificados += 1
                        cofres_eliminados += num_cofres
            except Exception as e:
                print(f"   [ERROR] {archivo.name}: {e}")
    
    # 2. Limpiar mapas parciales
    print("\n[2/2] Limpiando mapas parciales...")
    dir_mapas = Path("src/database/mapas")
    if dir_mapas.exists():
        for categoria_dir in dir_mapas.iterdir():
            if categoria_dir.is_dir():
                for archivo in categoria_dir.glob("*.json"):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if "cofres" in data:
                            num_cofres = len(data["cofres"])
                            if num_cofres > 0:
                                data["cofres"] = []
                                
                                with open(archivo, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2, ensure_ascii=False)
                                
                                print(f"   [OK] {categoria_dir.name}/{archivo.name}: {num_cofres} cofres eliminados")
                                archivos_modificados += 1
                                cofres_eliminados += num_cofres
                    except Exception as e:
                        print(f"   [ERROR] {categoria_dir.name}/{archivo.name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESUMEN:")
    print(f"  - Archivos modificados: {archivos_modificados}")
    print(f"  - Cofres eliminados: {cofres_eliminados}")
    print("\nAhora los mapas están limpios. Puedes agregar cofres nuevos")
    print("desde el editor y probar que se carguen correctamente.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        limpiar_cofres()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
