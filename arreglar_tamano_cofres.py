"""
Script quirúrgico para arreglar el tamaño de los cofres
El problema es que no se están pasando los sprites al constructor del Cofre
"""

import re

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Arreglar Tamaño de Cofres")
    print("=" * 60)
    
    # Leer el archivo
    with open('src/mapa.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # CAMBIO: Pasar los sprites al constructor del Cofre
    print("\n[1/1] Agregando sprites al constructor de Cofre...")
    
    patron_cofre = r'nuevo_cofre = Cofre\(\s+sx\(x\), sy\(y\),\s+id_cofre,\s+requiere_llave=cofre_info\.get\("requiere_llave"\),\s+items_contenido=cofre_info\.get\("items_contenido", \{\}\),\s+escala=escala\s+\)'
    
    reemplazo_cofre = '''nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        escala=escala,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )'''
    
    contenido = re.sub(patron_cofre, reemplazo_cofre, contenido, flags=re.MULTILINE)
    
    if contenido != contenido_original:
        print("   [OK] Constructor modificado")
    else:
        print("   [ERROR] No se pudo modificar constructor")
        return False
    
    # Guardar el archivo
    with open('src/mapa.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    print("\n[OK] Archivo guardado exitosamente")
    
    print("\n" + "=" * 60)
    print("RESUMEN: Constructor de Cofre actualizado")
    print("Los sprites ahora se pasan correctamente")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("\n[ADVERTENCIA] Algunos cambios no se aplicaron correctamente")
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
