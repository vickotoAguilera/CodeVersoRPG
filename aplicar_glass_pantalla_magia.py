"""
Script para aplicar efecto glassmorphism a PantallaMagia

OBJETIVO:
Modificar SOLO el metodo draw() de PantallaMagia para usar
el nuevo sistema de glassmorphism.

SEGURIDAD:
- Solo modifica el metodo de dibujo
- No toca la logica del juego
- Facil de revertir con git restore
"""

def aplicar_glassmorphism_pantalla_magia():
    import re
    
    ruta = r"c:\Users\vicko\Documents\RPG\src\pantalla_magia.py"
    
    print("=" * 70)
    print("APLICANDO GLASSMORPHISM A PANTALLA MAGIA")
    print("=" * 70)
    
    # Leer archivo
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Agregar import al inicio
    if "from src.ui_glassmorphism import" not in contenido:
        # Buscar donde estan los imports
        patron_import = r"(import pygame.*?\n)"
        
        nuevo_import = r"\1from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento\n"
        
        contenido = re.sub(patron_import, nuevo_import, contenido, count=1)
        print("[OK] Import agregado")
    else:
        print("[INFO] Import ya existe")
    
    # PASO 2: Modificar el metodo draw()
    # Buscar el inicio del metodo draw
    patron_draw = r"(def draw\(self, pantalla\):.*?)(pygame\.draw\.rect\(pantalla,.*?self\.rect.*?\))"
    
    # Reemplazo con glassmorphism
    reemplazo_draw = r"\1# Efecto glassmorphism\n        dibujar_ventana_glass(\n            pantalla, \n            self.rect, \n            'Magias',\n            obtener_color_acento('magia'),\n            alpha=230\n        )"
    
    if re.search(patron_draw, contenido, re.DOTALL):
        contenido = re.sub(patron_draw, reemplazo_draw, contenido, flags=re.DOTALL, count=1)
        print("[OK] Metodo draw() modificado")
    else:
        print("[ADVERTENCIA] No se encontro el patron de draw()")
    
    # Guardar
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Glassmorphism aplicado a PantallaMagia")
    print("=" * 70)
    print("\nPrueba el juego para ver el resultado:")
    print("  python main.py")
    print("\nSi algo falla, revierte con:")
    print("  git restore src/pantalla_magia.py")

if __name__ == "__main__":
    aplicar_glassmorphism_pantalla_magia()
