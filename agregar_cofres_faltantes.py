"""
Script quirurgico para agregar cofres faltantes a cofres_db.json
"""

import json
from pathlib import Path

def agregar_cofres_faltantes():
    print("=" * 70)
    print("SCRIPT QUIRURGICO: Agregar Cofres Faltantes a DB")
    print("=" * 70)
    
    # 1. Cargar cofres_db.json
    print("\n[1/3] Cargando cofres_db.json...")
    with open('src/database/cofres_db.json', 'r', encoding='utf-8') as f:
        cofres_db = json.load(f)
    
    cofres_mapa = cofres_db.get("cofres_mapa", {})
    print(f"   [OK] Cofres actuales en DB: {len(cofres_mapa)}")
    
    # 2. Escanear todos los mapas buscando cofres
    print("\n[2/3] Escaneando mapas...")
    cofres_encontrados = set()
    
    # Escanear mapas unificados
    dir_unificados = Path("src/database/mapas_unificados")
    if dir_unificados.exists():
        for archivo in dir_unificados.glob("*.json"):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for cofre in data.get("cofres", []):
                    id_cofre = cofre.get("id") or cofre.get("id_cofre")
                    if id_cofre:
                        cofres_encontrados.add(id_cofre)
            except:
                pass
    
    # Escanear mapas parciales
    dir_mapas = Path("src/database/mapas")
    if dir_mapas.exists():
        for categoria_dir in dir_mapas.iterdir():
            if categoria_dir.is_dir():
                for archivo in categoria_dir.glob("*.json"):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        for cofre in data.get("cofres", []):
                            id_cofre = cofre.get("id") or cofre.get("id_cofre")
                            if id_cofre:
                                cofres_encontrados.add(id_cofre)
                    except:
                        pass
    
    print(f"   [OK] Cofres encontrados en mapas: {len(cofres_encontrados)}")
    print(f"   IDs: {sorted(cofres_encontrados)}")
    
    # 3. Agregar cofres faltantes
    print("\n[3/3] Agregando cofres faltantes...")
    cofres_faltantes = cofres_encontrados - set(cofres_mapa.keys())
    
    if not cofres_faltantes:
        print("   [OK] No hay cofres faltantes")
        return
    
    print(f"   Cofres a agregar: {sorted(cofres_faltantes)}")
    
    for id_cofre in sorted(cofres_faltantes):
        # Crear entrada basica para el cofre
        cofres_mapa[id_cofre] = {
            "nombre": f"Cofre_{id_cofre}",
            "tipo": "madera",
            "requiere_llave": None,
            "oro": 50,
            "items_contenido": {
                "POCION_BASICA": 3,
                "ETER_BASICO": 1
            },
            "equipo_contenido": {},
            "especiales_contenido": {},
            "puede_reabrir": True,
            "ultima_apertura": 0,
            "descripcion": f"Cofre generado automaticamente para {id_cofre}",
            "sprite_cerrado": "cofre_madera_1.png",
            "sprite_abierto": "cofre_madera_3.png"
        }
        print(f"   [OK] Agregado: {id_cofre}")
    
    # Guardar
    cofres_db["cofres_mapa"] = cofres_mapa
    with open('src/database/cofres_db.json', 'w', encoding='utf-8') as f:
        json.dump(cofres_db, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Archivo guardado con {len(cofres_faltantes)} cofres nuevos")
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print(f"  - Cofres agregados: {len(cofres_faltantes)}")
    print(f"  - Total en DB ahora: {len(cofres_mapa)}")
    print("\nAhora los cofres deberian aparecer en el juego!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        agregar_cofres_faltantes()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
