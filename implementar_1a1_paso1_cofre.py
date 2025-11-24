"""
Script quirurgico 1/3: Modificar src/cofre.py
Eliminar logica de escala y usar tamano exacto del rect
"""

import re

def aplicar_cambios():
    print("=" * 70)
    print("SCRIPT 1/3: Modificar src/cofre.py - Sistema 1:1")
    print("=" * 70)
    
    with open('src/cofre.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios = 0
    
    # CAMBIO 1: Modificar __init__ para aceptar ancho y alto directamente
    print("\n[1/3] Modificando constructor para aceptar ancho/alto...")
    
    patron1 = r'def __init__\(self, x, y, id_cofre, requiere_llave=None, items_contenido=None, escala=1\.0, sprite_cerrado=None, sprite_abierto=None\):'
    
    reemplazo1 = 'def __init__(self, x, y, id_cofre, requiere_llave=None, items_contenido=None, ancho=64, alto=64, sprite_cerrado=None, sprite_abierto=None):'
    
    contenido = re.sub(patron1, reemplazo1, contenido)
    if contenido != contenido_original:
        cambios += 1
        print("   [OK] Firma del constructor modificada")
        contenido_original = contenido
    
    # CAMBIO 2: Actualizar docstring
    print("\n[2/3] Actualizando docstring...")
    
    patron2 = r'escala: Escala del sprite \(1\.0 = tamaño original\)'
    reemplazo2 = 'ancho, alto: Tamaño exacto en pixeles del cofre'
    
    contenido = re.sub(patron2, reemplazo2, contenido)
    if contenido != contenido_original:
        cambios += 1
        print("   [OK] Docstring actualizado")
        contenido_original = contenido
    
    # CAMBIO 3: Eliminar self.escala y guardar ancho/alto
    print("\n[3/3] Modificando inicializacion de atributos...")
    
    patron3 = r'self\.escala = escala\s+self\.sprite_cerrado_path = sprite_cerrado\s+self\.sprite_abierto_path = sprite_abierto'
    
    reemplazo3 = '''self.ancho_deseado = ancho
        self.alto_deseado = alto
        self.sprite_cerrado_path = sprite_cerrado
        self.sprite_abierto_path = sprite_abierto'''
    
    contenido = re.sub(patron3, reemplazo3, contenido)
    if contenido != contenido_original:
        cambios += 1
        print("   [OK] Atributos modificados")
        contenido_original = contenido
    
    # Guardar
    with open('src/cofre.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"\n[OK] Archivo guardado con {cambios} cambios")
    print("\n" + "=" * 70)
    return cambios > 0

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("[!] No se aplicaron cambios")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
