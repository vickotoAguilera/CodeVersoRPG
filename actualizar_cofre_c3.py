"""
Script quirurgico para actualizar el cofre C3 con los items correctos
"""
import json

def actualizar_cofre_c3():
    ruta = r"c:\Users\vicko\Documents\RPG\src\database\cofres_db.json"
    
    print("=" * 70)
    print("ACTUALIZANDO COFRE C3 EN COFRES_DB.JSON")
    print("=" * 70)
    
    # Leer el archivo JSON
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    # Actualizar el cofre C3
    if "C3" in datos["cofres_mapa"]:
        datos["cofres_mapa"]["C3"] = {
            "nombre": "Cofre_Madera_C3",
            "tipo": "madera",
            "sprite_cerrado": "cofre_madera_1.png",
            "sprite_abierto": "cofre_madera_3.png",
            "requiere_llave": None,
            "oro": 0,
            "items_contenido": {
                "ETER_INTERMEDIO": 1,
                "POCION_INTERMEDIA": 1,
                "ETER_BASICO": 1
            },
            "equipo_contenido": {
                "MANDOBLE_HIERRO": 1,
                "TUNICA_TELA": 1,
                "ESPADA_COBRE": 1,
                "ESCUDO_MADERA": 1
            },
            "especiales_contenido": {},
            "puede_reabrir": True,
            "ultima_apertura": 0,
            "descripcion": "Cofre de madera en la pradera"
        }
        print("[OK] Cofre C3 actualizado con:")
        print("  Items Consumibles:")
        print("    - Eter Intermedio x1")
        print("    - Pocion Intermedia x1")
        print("    - Eter Basico x1")
        print("  Equipo:")
        print("    - Mandoble de Hierro x1")
        print("    - Tunica de Tela x1")
        print("    - Espada de Cobre x1")
        print("    - Escudo de Madera x1")
    else:
        print("[ERROR] No se encontro el cofre C3")
        return
    
    # Guardar el archivo
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print("\n[EXITO] Archivo guardado exitosamente")
    print("=" * 70)

if __name__ == "__main__":
    actualizar_cofre_c3()
    print("\nAhora prueba abrir el cofre C3 en el juego!")
