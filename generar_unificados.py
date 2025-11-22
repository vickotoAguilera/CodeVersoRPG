"""
Script para generar archivos unificados automaticamente
Lee todos los mapas y genera sus versiones unificadas
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Configuracion
DATABASE_PATH = "src/database"
MAPAS_PATH = os.path.join(DATABASE_PATH, "mapas")
UNIFICADOS_PATH = os.path.join(DATABASE_PATH, "mapas_unificados")

# Crear directorio si no existe
os.makedirs(UNIFICADOS_PATH, exist_ok=True)

def encontrar_mapas():
    """Encuentra todos los archivos JSON de mapas"""
    mapas = []
    for root, dirs, files in os.walk(MAPAS_PATH):
        for file in files:
            if file.endswith('.json') and not any(x in file for x in ['_muros', '_portales', '_cofres', '_spawns', 'test_']):
                ruta_completa = os.path.join(root, file)
                # Calcular categoria relativa
                ruta_rel = os.path.relpath(root, MAPAS_PATH)
                mapas.append({
                    'archivo': file,
                    'ruta': ruta_completa,
                    'categoria': ruta_rel.replace('\\', '/')
                })
    return mapas

def generar_unificado(mapa_info):
    """Genera archivo unificado para un mapa"""
    try:
        # Leer archivo parcial
        with open(mapa_info['ruta'], 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Buscar imagen correspondiente
        nombre_base = os.path.splitext(mapa_info['archivo'])[0]
        imagen = None
        for ext in ['.png', '.jpg', '.jpeg']:
            posible = os.path.join(os.path.dirname(mapa_info['ruta']).replace('database\\mapas', 'assets\\mapas'), nombre_base + ext)
            if os.path.exists(posible):
                imagen = nombre_base + ext
                break
        
        # Crear estructura unificada con metadata
        unificado = {
            "mapa_base": nombre_base,
            "categoria": mapa_info['categoria'],
            "imagen": imagen or f"{nombre_base}.png",
            "ultima_modificacion": datetime.now().isoformat(),
            "version_editor": "1.0",
            "editado_por": "Script Auto-Generador",
            "muros": datos.get("muros", []),
            "portales": datos.get("portales", []),
            "spawns": datos.get("spawns", []),
            "cofres": datos.get("cofres", []),
            "npcs": datos.get("npcs", []),
            "eventos": datos.get("eventos", [])
        }
        
        # Guardar archivo unificado
        nombre_unificado = f"{nombre_base}_unificado.json"
        ruta_unificado = os.path.join(UNIFICADOS_PATH, nombre_unificado)
        
        with open(ruta_unificado, 'w', encoding='utf-8') as f:
            json.dump(unificado, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Generado: {nombre_unificado}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {mapa_info['archivo']}: {e}")
        return False

# Main
if __name__ == "__main__":
    print("=== Generador de Archivos Unificados ===\n")
    
    mapas = encontrar_mapas()
    print(f"Encontrados {len(mapas)} mapas\n")
    
    exitosos = 0
    for mapa in mapas:
        if generar_unificado(mapa):
            exitosos += 1
    
    print(f"\n=== Resumen ===")
    print(f"Total: {len(mapas)}")
    print(f"Exitosos: {exitosos}")
    print(f"Fallidos: {len(mapas) - exitosos}")
    print(f"\nArchivos generados en: {UNIFICADOS_PATH}")
