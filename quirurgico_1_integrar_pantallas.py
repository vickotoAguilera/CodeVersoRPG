"""
Script Quirúrgico 1: Integrar Pantallas Reales de Batalla al Editor

OBJETIVO:
Reemplazar las ventanas mockup del editor_batalla.py con las clases reales
de las pantallas de batalla del juego (PantallaMagia, PantallaItems, PantallaVictoria)

CAMBIOS:
1. Agregar imports de las pantallas reales
2. Crear versiones "preview" de las pantallas que no requieran lógica de batalla
3. Agregar toggles para mostrar/ocultar cada pantalla
4. Mantener la funcionalidad de mover y redimensionar

ARCHIVOS A MODIFICAR:
- editor_batalla.py
"""

import os
import re

def integrar_pantallas_reales():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("INTEGRANDO PANTALLAS REALES DE BATALLA AL EDITOR")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Agregar imports de las pantallas reales
    imports_viejos = """import pygame
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple"""
    
    imports_nuevos = """import pygame
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Importar pantallas reales de batalla
from src.pantalla_magia import PantallaMagia
from src.pantalla_items import PantallaItems
from src.pantalla_victoria import PantallaVictoria
from src.pantalla_lista_habilidades import PantallaListaHabilidades"""
    
    if imports_viejos in contenido:
        contenido = contenido.replace(imports_viejos, imports_nuevos)
        print("[OK] Paso 1: Imports agregados")
    else:
        print("[ADVERTENCIA] No se encontraron los imports originales")
    
    # PASO 2: Agregar clase wrapper para pantallas en modo preview
    codigo_wrapper = '''

# ========================================
# WRAPPERS PARA PANTALLAS REALES
# ========================================

class PantallaPreview:
    """Wrapper base para pantallas de batalla en modo preview"""
    def __init__(self, x, y, ancho, alto, titulo="Pantalla"):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.visible = False
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=10):
        """Retorna qué handle está en el punto"""
        handles = {
            'nw': (self.x, self.y),
            'ne': (self.x + self.ancho, self.y),
            'sw': (self.x, self.y + self.alto),
            'se': (self.x + self.ancho, self.y + self.alto)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam and abs(py - hy) <= tam:
                return nombre
        return None
    
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "visible": self.visible
        }

'''
    
    # Buscar donde insertar (después de SeccionDesplegable)
    patron_insercion = r"(class SeccionDesplegable:.*?border_radius=3\))\s*\n\s*# ========================================\s*\n\s*# EDITOR PRINCIPAL"
    
    if re.search(patron_insercion, contenido, re.DOTALL):
        contenido = re.sub(
            patron_insercion,
            r"\1" + codigo_wrapper + "\n# ========================================\n# EDITOR PRINCIPAL",
            contenido,
            flags=re.DOTALL
        )
        print("[OK] Paso 2: Clase wrapper agregada")
    else:
        print("[ADVERTENCIA] No se encontró el punto de inserción para wrapper")
    
    # Guardar archivo
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Paso 1 completado: Estructura base agregada")
    print("=" * 70)

if __name__ == "__main__":
    integrar_pantallas_reales()
    print("\nSiguiente paso: Agregar instancias de pantallas en __init__")
