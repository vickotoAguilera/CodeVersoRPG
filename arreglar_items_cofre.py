"""
Script quirurgico para arreglar la carga de items de cofres

PROBLEMA:
- Los cofres tienen items en 3 categorias: items_contenido, equipo_contenido, especiales_contenido
- Solo se esta pasando items_contenido al constructor de Cofre
- Los items de equipo y especiales no se estan dando al jugador

SOLUCION:
- Combinar los 3 diccionarios en uno solo antes de crear el Cofre
"""

def arreglar_items_cofre():
    ruta_mapa = r"c:\Users\vicko\Documents\RPG\src\mapa.py"
    
    print("=" * 70)
    print("ARREGLANDO CARGA DE ITEMS DE COFRES EN MAPA.PY")
    print("=" * 70)
    
    # Leer el archivo
    with open(ruta_mapa, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y reemplazar el codigo de creacion del cofre
    viejo_codigo = """                # Buscar datos del cofre en la base de datos
                cofre_info = self.cofres_db.get(id_cofre)
                if cofre_info:
                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        ancho=ancho_deseado if ancho_deseado else 64,
                        alto=alto_deseado if alto_deseado else 64,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )"""
    
    nuevo_codigo = """                # Buscar datos del cofre en la base de datos
                cofre_info = self.cofres_db.get(id_cofre)
                if cofre_info:
                    # Combinar todos los items (consumibles, equipo y especiales)
                    todos_items = {}
                    todos_items.update(cofre_info.get("items_contenido", {}))
                    todos_items.update(cofre_info.get("equipo_contenido", {}))
                    todos_items.update(cofre_info.get("especiales_contenido", {}))
                    
                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=todos_items,
                        ancho=ancho_deseado if ancho_deseado else 64,
                        alto=alto_deseado if alto_deseado else 64,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )"""
    
    if viejo_codigo in contenido:
        contenido = contenido.replace(viejo_codigo, nuevo_codigo)
        print("[OK] Codigo de carga de items actualizado")
        print("     - Ahora se combinan items_contenido + equipo_contenido + especiales_contenido")
    else:
        print("[ADVERTENCIA] No se encontro el codigo a reemplazar")
        return
    
    # Guardar el archivo
    with open(ruta_mapa, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Archivo guardado exitosamente")
    print("=" * 70)
    print("\nAhora los cofres daran TODOS los items configurados:")
    print("  - Items consumibles (pociones, eteres, etc.)")
    print("  - Equipo (armas, armaduras, accesorios)")
    print("  - Items especiales (cristales, expansores, etc.)")

if __name__ == "__main__":
    arreglar_items_cofre()
    print("\nListo! Prueba abrir un cofre en el juego")
