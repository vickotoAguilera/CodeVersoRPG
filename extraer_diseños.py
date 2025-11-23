"""
Script para extraer diseños de ventanas desde archivos Python
y generar JSONs para el editor UI universal.

Este script analiza los archivos de pantallas existentes y extrae:
- Posiciones de ventanas (Rect)
- Tamaños de cajas
- Contenido de texto
"""

import re
import json
from pathlib import Path

def extraer_rects_de_archivo(ruta_archivo):
    """
    Extrae todos los pygame.Rect del archivo Python.
    Retorna una lista de diccionarios con la info de cada Rect.
    """
    print(f"\n{'='*60}")
    print(f"Analizando: {ruta_archivo.name}")
    print(f"{'='*60}")
    
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar todos los pygame.Rect en el código
    # Patrón: pygame.Rect(x, y, ancho, alto)
    patron_rect = r'pygame\.Rect\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)'
    
    rects_encontrados = []
    matches = re.finditer(patron_rect, contenido)
    
    for i, match in enumerate(matches):
        x = match.group(1)
        y = match.group(2)
        ancho = match.group(3)
        alto = match.group(4)
        
        # Buscar el nombre de la variable (línea completa)
        inicio_linea = contenido.rfind('\n', 0, match.start()) + 1
        fin_linea = contenido.find('\n', match.end())
        linea_completa = contenido[inicio_linea:fin_linea].strip()
        
        # Extraer nombre de variable
        nombre_var = "desconocido"
        if '=' in linea_completa:
            nombre_var = linea_completa.split('=')[0].strip()
            # Limpiar self. si existe
            nombre_var = nombre_var.replace('self.', '')
        
        rect_info = {
            "nombre": nombre_var,
            "x": x,
            "y": y,
            "ancho": ancho,
            "alto": alto,
            "linea": linea_completa
        }
        
        rects_encontrados.append(rect_info)
        print(f"  [{i+1}] {nombre_var}")
        print(f"      Posición: ({x}, {y})")
        print(f"      Tamaño: {ancho} x {alto}")
        print(f"      Línea: {linea_completa[:80]}...")
    
    return rects_encontrados


def generar_json_pantalla_magia():
    """Genera el JSON para pantalla_magia.py"""
    
    ruta = Path("_backup_ui_original/pantalla_magia.py")
    rects = extraer_rects_de_archivo(ruta)
    
    # Crear estructura JSON
    ventana_data = {
        "ventana": {
            "nombre": "pantalla_magia",
            "x": 30,
            "y": 30,
            "ancho": 1220,  # ANCHO - 60
            "alto": 660,    # ALTO - 60
            "titulo": "Magias Disponibles",
            "color_acento": [150, 80, 200],  # Morado para magia
            "alpha": 230,
            "visible": True
        },
        "textboxes": []
    }
    
    # Mapear los rects encontrados a textboxes
    for rect in rects:
        nombre = rect["nombre"]
        
        # Calcular dimensiones (reemplazar self.ANCHO y self.ALTO)
        ancho_val = rect["ancho"]
        alto_val = rect["alto"]
        
        # Reemplazar self.ANCHO con 1280 y self.ALTO con 720
        if "self.ANCHO" in ancho_val:
            ancho_val = ancho_val.replace("self.ANCHO", "1280")
        if "self.ALTO" in alto_val:
            alto_val = alto_val.replace("self.ALTO", "720")
        
        # Evaluar expresiones simples
        try:
            ancho_calculado = eval(ancho_val) if any(op in ancho_val for op in ['+', '-', '*', '/']) else int(ancho_val)
            alto_calculado = eval(alto_val) if any(op in alto_val for op in ['+', '-', '*', '/']) else int(alto_val)
        except:
            ancho_calculado = 200
            alto_calculado = 100
        
        # Determinar tipo y contenido según el nombre
        if "desc" in nombre.lower():
            textbox = {
                "nombre": "descripcion",
                "x": int(rect["x"]),
                "y": int(rect["y"]),
                "ancho": ancho_calculado,
                "alto": alto_calculado,
                "tipo": "texto",
                "contenido": ["Descripción de la magia seleccionada"],
                "fuente_size": 26,
                "color_texto": [255, 255, 255],
                "alineacion": "left",
                "scroll": {
                    "enabled": False,
                    "items_visibles": 3,
                    "color_scrollbar": [100, 100, 255],
                    "offset_y": 0,
                    "offset_x": 0
                }
            }
            ventana_data["textboxes"].append(textbox)
        
        elif "mp" in nombre.lower() and "caja" in nombre.lower():
            textbox = {
                "nombre": "mp_heroe",
                "x": int(rect["x"]),
                "y": int(rect["y"]),
                "ancho": ancho_calculado,
                "alto": alto_calculado,
                "tipo": "texto",
                "contenido": ["MP: 50 / 100"],
                "fuente_size": 28,
                "color_texto": [255, 255, 255],
                "alineacion": "left",
                "scroll": {
                    "enabled": False,
                    "items_visibles": 1,
                    "color_scrollbar": [100, 100, 255],
                    "offset_y": 0,
                    "offset_x": 0
                }
            }
            ventana_data["textboxes"].append(textbox)
        
        elif "magia" in nombre.lower() and "caja" in nombre.lower():
            # Esta es la lista de magias
            textbox = {
                "nombre": "lista_magias",
                "x": int(rect["x"]) if rect["x"].isdigit() else 295,
                "y": int(rect["y"]) if rect["y"].isdigit() else 145,
                "ancho": 925,  # Calculado
                "alto": 545,   # Calculado
                "tipo": "lista",
                "contenido": [
                    "• Cura (10 MP)",
                    "• Piro (15 MP)",
                    "• Hielo (15 MP)",
                    "• Rayo (20 MP)",
                    "• Volver"
                ],
                "fuente_size": 30,
                "color_texto": [255, 255, 255],
                "alineacion": "left",
                "scroll": {
                    "enabled": True,
                    "items_visibles": 10,
                    "color_scrollbar": [150, 80, 200],
                    "offset_y": 0,
                    "offset_x": 0
                }
            }
            ventana_data["textboxes"].append(textbox)
    
    # Guardar JSON
    ruta_salida = Path("src/database/ui/pantalla_magia.json")
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(ventana_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] JSON generado: {ruta_salida}")
    print(f"   Ventana: {ventana_data['ventana']['nombre']}")
    print(f"   TextBoxes: {len(ventana_data['textboxes'])}")
    
    return ventana_data


def generar_json_pantalla_items():
    """Genera el JSON para pantalla_items.py"""
    
    ventana_data = {
        "ventana": {
            "nombre": "pantalla_items",
            "x": 30,
            "y": 30,
            "ancho": 1220,
            "alto": 660,
            "titulo": "Items Disponibles",
            "color_acento": [100, 200, 100],  # Verde para items
            "alpha": 230,
            "visible": True
        },
        "textboxes": [
            {
                "nombre": "descripcion",
                "x": 30,
                "y": 30,
                "ancho": 1220,
                "alto": 100,
                "tipo": "texto",
                "contenido": ["Descripcion del item seleccionado"],
                "fuente_size": 26,
                "color_texto": [255, 255, 255],
                "alineacion": "left",
                "scroll": {"enabled": False, "items_visibles": 3, "color_scrollbar": [100, 200, 100], "offset_y": 0, "offset_x": 0}
            },
            {
                "nombre": "lista_items",
                "x": 30,
                "y": 145,
                "ancho": 1220,
                "alto": 545,
                "tipo": "lista",
                "contenido": [
                    "Pocion (x5)",
                    "Eter (x3)",
                    "Antidoto (x2)",
                    "Volver"
                ],
                "fuente_size": 30,
                "color_texto": [255, 255, 255],
                "alineacion": "left",
                "scroll": {"enabled": True, "items_visibles": 10, "color_scrollbar": [100, 200, 100], "offset_y": 0, "offset_x": 0}
            }
        ]
    }
    
    ruta_salida = Path("src/database/ui/pantalla_items.json")
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(ventana_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] JSON generado: {ruta_salida}")
    return ventana_data


def main():
    """Funcion principal"""
    print("\n" + "="*60)
    print("EXTRACTOR DE DISENOS DE VENTANAS")
    print("="*60)
    
    # Generar JSONs
    generar_json_pantalla_magia()
    generar_json_pantalla_items()
    
    print("\n" + "="*60)
    print("[OK] PROCESO COMPLETADO")
    print("="*60)
    print("\nAhora puedes:")
    print("1. Abrir el editor UI universal")
    print("2. Cargar estos JSONs (proxima funcionalidad)")
    print("3. Ajustar posiciones visualmente")
    print("4. Exportar los JSONs actualizados")


if __name__ == "__main__":
    main()
