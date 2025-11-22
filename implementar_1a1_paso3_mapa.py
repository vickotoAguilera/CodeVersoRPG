"""
Script quirurgico 3/3: Modificar src/mapa.py
Pasar ancho y alto directamente al constructor de Cofre
"""

import re

def aplicar_cambios():
    print("=" * 70)
    print("SCRIPT 3/3: Modificar src/mapa.py - Sistema 1:1")
    print("=" * 70)
    
    with open('src/mapa.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # CAMBIO: Reemplazar toda la logica de calculo de escala
    print("\n[1/2] Eliminando logica de calculo de escala...")
    
    # Buscar y eliminar el bloque de calculo de escala
    patron1 = r'# Calcular escala basada en el tamaño deseado del JSON.*?escala = cofre_data\.get\("escala", 0\.5\)  # Escala por defecto 0\.5'
    
    reemplazo1 = '''# Obtener tamaño exacto del JSON
                ancho = cofre_data.get("ancho") or cofre_data.get("w", 64)
                alto = cofre_data.get("alto") or cofre_data.get("h", 64)'''
    
    contenido = re.sub(patron1, reemplazo1, contenido, flags=re.DOTALL)
    
    if contenido != contenido_original:
        print("   [OK] Logica de escala eliminada")
        contenido_original = contenido
    else:
        print("   [!] No se encontro el patron de escala (puede ya estar modificado)")
    
    # CAMBIO 2: Modificar constructor de Cofre
    print("\n[2/2] Modificando llamada al constructor de Cofre...")
    
    patron2 = r'nuevo_cofre = Cofre\(\s+sx\(x\), sy\(y\),\s+id_cofre,\s+requiere_llave=cofre_info\.get\("requiere_llave"\),\s+items_contenido=cofre_info\.get\("items_contenido", \{\}\),\s+escala=escala,\s+sprite_cerrado=cofre_info\.get\("sprite_cerrado"\),\s+sprite_abierto=cofre_info\.get\("sprite_abierto"\)\s+\)'
    
    reemplazo2 = '''nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        ancho=ancho,
                        alto=alto,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )'''
    
    contenido = re.sub(patron2, reemplazo2, contenido, flags=re.MULTILINE | re.DOTALL)
    
    if contenido != contenido_original:
        print("   [OK] Constructor de Cofre modificado")
    else:
        print("   [ERROR] No se pudo modificar el constructor")
        return False
    
    # Guardar
    with open('src/mapa.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[OK] Archivo guardado")
    print("\n" + "=" * 70)
    print("SISTEMA 1:1 IMPLEMENTADO!")
    print("  - Los cofres ahora usan el tamano exacto del editor")
    print("  - No hay escalado automatico")
    print("  - Lo que ves en el editor es lo que ves en el juego")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("[!] Revisa manualmente el archivo")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
