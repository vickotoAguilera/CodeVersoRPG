"""
Script para desvincular todos los portales y eliminar todos los spawns
de los archivos JSON parciales.
"""
import json
import os
from pathlib import Path

# Directorios
PORTALES_DIR = Path("src/database/portales")
SPAWNS_DIR = Path("src/database/spawns")

def clean_portales_file(json_path):
    """Limpia un archivo de portales eliminando spawn_destino_id."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes_made = False
        
        if 'portales' in data:
            for portal in data['portales']:
                if 'spawn_destino_id' in portal and portal['spawn_destino_id']:
                    print(f"  - Desvinculando portal {portal.get('id', 'sin_id')}")
                    portal['spawn_destino_id'] = ''
                    changes_made = True
        
        if changes_made:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def clean_spawns_file(json_path):
    """Elimina todos los spawns de un archivo."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'spawns' in data and data['spawns']:
            count = len(data['spawns'])
            print(f"  - Eliminando {count} spawns")
            data['spawns'] = []
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("=== Limpiando Enlaces de Portales y Spawns ===\n")
    
    # Limpiar archivos de portales
    print("📁 Procesando archivos de portales...")
    if PORTALES_DIR.exists():
        portales_files = list(PORTALES_DIR.glob("*_portales.json"))
        print(f"Encontrados {len(portales_files)} archivos\n")
        
        portales_modified = 0
        for json_file in portales_files:
            print(f"Procesando: {json_file.name}")
            if clean_portales_file(json_file):
                portales_modified += 1
                print(f"  ✓ Modificado")
            else:
                print(f"  - Sin cambios")
        print(f"\nPortales modificados: {portales_modified}/{len(portales_files)}\n")
    else:
        print(f"❌ Directorio no encontrado: {PORTALES_DIR}\n")
    
    # Limpiar archivos de spawns
    print("📁 Procesando archivos de spawns...")
    if SPAWNS_DIR.exists():
        spawns_files = list(SPAWNS_DIR.glob("*_spawns.json"))
        print(f"Encontrados {len(spawns_files)} archivos\n")
        
        spawns_modified = 0
        for json_file in spawns_files:
            print(f"Procesando: {json_file.name}")
            if clean_spawns_file(json_file):
                spawns_modified += 1
                print(f"  ✓ Modificado")
            else:
                print(f"  - Sin cambios")
        print(f"\nSpawns modificados: {spawns_modified}/{len(spawns_files)}\n")
    else:
        print(f"❌ Directorio no encontrado: {SPAWNS_DIR}\n")
    
    print(f"\n✅ Limpieza completada")
    print(f"\n📝 Próximos pasos:")
    print(f"  1. Ejecuta: python tools/merge_map_parts.py")
    print(f"  2. Abre el editor de portales")
    print(f"  3. Ahora podrás crear nuevos spawns para tus portales")

if __name__ == "__main__":
    main()
