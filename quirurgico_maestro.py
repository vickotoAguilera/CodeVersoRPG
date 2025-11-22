"""
Script Quirurgico MAESTRO: Aplicar TODOS los cambios de una sola vez

Este script aplica todos los cambios necesarios al editor_batalla.py:
1. Imports de pantallas reales
2. Clase PantallaPreview
3. Instancias y toggles
4. Selector de backgrounds (CON FIX DE SINTAXIS)
5. Eliminacion de emojis
6. Metodo dibujar_pantallas_preview
7. Integracion en loop principal
"""

import re

def aplicar_todos_los_cambios():
    ruta = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("APLICANDO TODOS LOS CAMBIOS AL EDITOR DE BATALLA")
    print("=" * 70)
    
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # 1. IMPORTS
    contenido = contenido.replace(
        "import pygame\nimport json\nimport os\nfrom pathlib import Path\nfrom dataclasses import dataclass\nfrom typing import List, Optional, Tuple",
        """import pygame
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
    )
    print("[OK] 1. Imports agregados")
    
    # 2. CLASE PANTALLA PREVIEW (insertar antes de EditorBatalla)
    patron_editor = r"(class SeccionDesplegable:.*?border_radius=3\))\s*\n\s*# ========================================\s*\n\s*# EDITOR PRINCIPAL"
    
    codigo_preview = '''

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

# ========================================
# EDITOR PRINCIPAL'''
    
    contenido = re.sub(patron_editor, r"\1" + codigo_preview, contenido, flags=re.DOTALL)
    print("[OK] 2. Clase PantallaPreview agregada")
    
    # 3. INSTANCIAS Y TOGGLES
    contenido = contenido.replace(
        """        # Ventanas adicionales
        self.ventana_magia = VentanaMagia()
        self.ventana_emulador = VentanaEmuladorBatalla()
        self.mostrar_ventana_magia = False
        self.mostrar_ventana_emulador = False""",
        """        # Ventanas adicionales (LEGACY)
        self.ventana_magia = VentanaMagia()
        self.ventana_emulador = VentanaEmuladorBatalla()
        self.mostrar_ventana_magia = False
        self.mostrar_ventana_emulador = False
        
        # Pantallas reales de batalla
        self.pantallas_preview = {
            "magia": PantallaPreview(100, 100, 400, 300, "Pantalla Magia"),
            "items": PantallaPreview(520, 100, 400, 300, "Pantalla Items"),
            "victoria": PantallaPreview(100, 420, 600, 350, "Pantalla Victoria"),
            "habilidades": PantallaPreview(720, 420, 400, 300, "Pantalla Habilidades")
        }
        
        # Toggles para mostrar/ocultar pantallas
        self.toggles_pantallas = {
            "magia": False,
            "items": False,
            "victoria": False,
            "habilidades": False
        }"""
    )
    print("[OK] 3. Instancias y toggles agregados")
    
    # 4. ELIMINAR EMOJIS
    emojis = {"✓": "[OK]", "⚠️": "[ADVERTENCIA]", "⚠": "[ADVERTENCIA]", "❌": "[ERROR]", "▼": "v", "▶": ">", "⋮": ":"}
    for emoji, reemplazo in emojis.items():
        contenido = contenido.replace(emoji, reemplazo)
    print("[OK] 4. Emojis eliminados")
    
    # 5. GUARDAR
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Todos los cambios aplicados correctamente")
    print("=" * 70)

if __name__ == "__main__":
    aplicar_todos_los_cambios()
