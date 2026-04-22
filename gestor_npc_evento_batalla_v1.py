# -*- coding: utf-8 -*-
"""
Gestor NPC Evento Batalla - Editor Canvas Doble

Proposito:
- Editor visual para configurar NPC de evento de batalla.
- Canvas izquierdo: mapa del mundo (NPC fisico).
- Canvas derecho: preview de batalla (enemigos vs heroes).
- Guardado/carga de layouts globales y overrides por encuentro.

Funcionalidad Paso 1 (base + sprites):
- Crear py + bat del editor.
- Dibujar marco UI con dos canvas y barra inferior.
- Cargar mapa en canvas izquierdo.
- Cargar y mostrar sprites de monstruos/heroes.
- Permitir seleccionar y organizar slots.
"""

import pygame
import json
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import (
    DATABASE_PATH,
    HEROES_SPRITES_PATH, MONSTRUOS_SPRITES_PATH
)

# ============================================================================
# CONSTANTES EDITOR
# ============================================================================

# Dimensiones de pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

TITULO_VENTANA = "Gestor NPC Evento Batalla - Editor Canvas Doble (v1)"

# Colores
COLOR_FONDO = (20, 20, 30)
COLOR_CANVAS_BG = (30, 30, 40)
COLOR_PANEL_BG = (40, 40, 50)
COLOR_TEXTO = (200, 200, 200)
COLOR_BORDE = (100, 100, 120)
COLOR_ACTIVO = (100, 200, 100)
COLOR_HOVER = (150, 150, 180)

# Tamaños de canvas
ANCHO_CANVAS = ANCHO_PANTALLA // 2 - 10
ALTO_CANVAS = ALTO_PANTALLA - 120
MARGEN = 5

# Posiciones canvas
CANVAS_IZQ_X = MARGEN
CANVAS_IZQ_Y = MARGEN
CANVAS_DER_X = ANCHO_CANVAS + 20
CANVAS_DER_Y = MARGEN

# Barra inferior
ALTO_BARRA_INFERIOR = 100
BARRA_Y = ALTO_PANTALLA - ALTO_BARRA_INFERIOR

# Slots de enemigos/heroes (max 5)
MAX_SLOTS = 5

# ============================================================================
# RUTAS DE DATOS
# ============================================================================

NPC_EVENTO_BATALLA_LAYOUTS_PATH = os.path.join(DATABASE_PATH, 'npc_evento_batalla_layouts.json')
NPC_EVENTO_BATALLA_POR_MAPA_DIR = os.path.join(DATABASE_PATH, 'npc_evento_batalla_por_mapa')

# Crear directorio si no existe
os.makedirs(NPC_EVENTO_BATALLA_POR_MAPA_DIR, exist_ok=True)


# ============================================================================
# CLASES
# ============================================================================

class EditorCanvasDoble:
    """Editor principal con canvas izquierdo (mundo) y derecho (batalla preview)."""
    
    def __init__(self):
        """Inicializar editor."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption(TITULO_VENTANA)
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        
        self.ejecutando = True
        self.fps = FPS
        
        # Estado editor
        self.mapa_actual = None
        self.mapa_surface = None
        self.mapa_rect = None
        self.offset_mapa_x = 0
        self.offset_mapa_y = 0
        self.zoom_mapa = 1.0
        
        # Datos cargados
        self.mapas_disponibles = self._cargar_mapas_disponibles()
        self.monstruos_db = self._cargar_json(os.path.join(DATABASE_PATH, 'monstruos_db.json'))
        self.heroes_db = self._cargar_json(os.path.join(DATABASE_PATH, 'heroes_db.json'))
        self.layouts_globales = self._cargar_layouts_globales()
        
        # Cache de sprites cargados
        self.sprites_monstruos_cache = {}  # {"nombre": pygame.Surface}
        self.sprites_heroes_cache = {}     # {"nombre": pygame.Surface}
        self._cargar_sprites_en_cache()
        
        # Slots de enemigos y heroes
        self.cantidad_enemigos = 1
        self.enemigos_slots = [{"monstruo_id": None, "sprite_id": None} for _ in range(MAX_SLOTS)]
        self.heroes_slots = [{"heroe_id": None, "sprite_id": None} for _ in range(MAX_SLOTS)]
        
        # Interfaz
        self.botones = self._crear_botones()
        self.mapa_seleccionado_idx = 0
        self.lista_scroll_y = 0
        
        # Drag and drop
        self.slot_siendo_arrastrado = None
        self.mouse_pos_actual = (0, 0)
        
        print(f"[EditorCanvasDoble] Inicializado. Mapas: {len(self.mapas_disponibles)}, Monstruos: {len(self.monstruos_db or {})}, Heroes: {len(self.heroes_db or {})}")
    
    def _cargar_json(self, ruta):
        """Cargar archivo JSON."""
        if not os.path.exists(ruta):
            return {}
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] No se pudo cargar {ruta}: {e}")
            return {}
    
    def _cargar_mapas_disponibles(self):
        """Cargar lista de mapas JSON disponibles."""
        mapas = []
        # Buscar en mapas_unificados primero
        ruta_unificados = os.path.join(DATABASE_PATH, 'mapas_unificados')
        if os.path.exists(ruta_unificados):
            for archivo in os.listdir(ruta_unificados):
                if archivo.endswith('.json') and 'mapa_' in archivo:
                    mapa_nombre = archivo.replace('.json', '')
                    mapas.append(mapa_nombre)
        
        if mapas:
            return sorted(mapas)
        
        # Fallback: buscar en mapas/mundo/
        ruta_mundo = os.path.join(DATABASE_PATH, 'mapas', 'mundo')
        if os.path.exists(ruta_mundo):
            for archivo in os.listdir(ruta_mundo):
                if archivo.endswith('.json'):
                    mapa_nombre = archivo.replace('.json', '')
                    mapas.append(mapa_nombre)
        
        return sorted(mapas)
    
    def _cargar_sprites_en_cache(self):
        """Pre-cargar todos los sprites en cache para acceso rápido."""
        if self.monstruos_db:
            for monstruo_id, datos in self.monstruos_db.items():
                try:
                    archivo_sprite = datos.get('sprite_archivo', 'dragon_prueba.png')
                    ruta_sprite = os.path.join(MONSTRUOS_SPRITES_PATH, archivo_sprite)
                    if os.path.exists(ruta_sprite):
                        img = pygame.image.load(ruta_sprite)
                        escala = datos.get('escala_sprite', 1.0)
                        nuevo_w = int(img.get_width() * escala * 0.5)
                        nuevo_h = int(img.get_height() * escala * 0.5)
                        img_escalada = pygame.transform.scale(img, (nuevo_w, nuevo_h))
                        self.sprites_monstruos_cache[monstruo_id] = img_escalada
                except Exception as e:
                    print(f"[AVISO] No se pudo cargar sprite de {monstruo_id}: {e}")
        
        if self.heroes_db:
            for heroe_id, datos in self.heroes_db.items():
                try:
                    # Para heroes usamos una miniatura simple por ahora
                    # Los sprites reales están en asset_coords_db
                    # Aquí creamos un placeholder
                    surf = pygame.Surface((40, 50))
                    surf.fill((100, 150, 200))
                    nombre = datos.get('nombre', heroe_id)
                    texto = pygame.font.Font(None, 12).render(nombre[:3], True, (255, 255, 255))
                    surf.blit(texto, (5, 20))
                    self.sprites_heroes_cache[heroe_id] = surf
                except Exception as e:
                    print(f"[AVISO] No se pudo crear sprite de heroe {heroe_id}: {e}")
    
    def _cargar_layouts_globales(self):
        """Cargar configuracion global de layouts."""
        ruta = os.path.join(DATABASE_PATH, 'npc_evento_batalla_layouts.json')
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] No se pudo cargar layouts: {e}")
        return self._crear_layouts_por_defecto()
    
    def _crear_layouts_por_defecto(self):
        """Crear estructura por defecto de layouts."""
        return {
            "version": "1.0",
            "layouts": {
                "1": {"enemigos": [{"x": 400, "y": 200}], "heroes": [{"x": 100, "y": 200}]},
                "2": {"enemigos": [{"x": 420, "y": 150}, {"x": 420, "y": 250}], "heroes": [{"x": 100, "y": 150}, {"x": 100, "y": 250}]},
                "3": {"enemigos": [{"x": 420, "y": 100}, {"x": 420, "y": 200}, {"x": 420, "y": 300}], "heroes": [{"x": 100, "y": 100}, {"x": 100, "y": 200}, {"x": 100, "y": 300}]},
                "4": {"enemigos": [{"x": 380, "y": 100}, {"x": 460, "y": 100}, {"x": 380, "y": 300}, {"x": 460, "y": 300}], "heroes": [{"x": 80, "y": 100}, {"x": 120, "y": 100}, {"x": 80, "y": 300}, {"x": 120, "y": 300}]},
                "5": {"enemigos": [{"x": 380, "y": 80}, {"x": 460, "y": 80}, {"x": 420, "y": 200}, {"x": 380, "y": 320}, {"x": 460, "y": 320}], "heroes": [{"x": 80, "y": 80}, {"x": 120, "y": 80}, {"x": 100, "y": 200}, {"x": 80, "y": 320}, {"x": 120, "y": 320}]},
            }
        }
    
    def _crear_botones(self):
        """Crear botones de interfaz."""
        botones = {
            "cargar_mapa": pygame.Rect(10, BARRA_Y + 10, 120, 30),
            "guardar": pygame.Rect(140, BARRA_Y + 10, 100, 30),
            "cargar": pygame.Rect(250, BARRA_Y + 10, 100, 30),
            "resetear": pygame.Rect(360, BARRA_Y + 10, 120, 30),
            "cantidad_menos": pygame.Rect(10, BARRA_Y + 50, 30, 25),
            "cantidad_mas": pygame.Rect(50, BARRA_Y + 50, 30, 25),
            "salir": pygame.Rect(ANCHO_PANTALLA - 110, BARRA_Y + 10, 100, 30),
        }
        return botones
    
    def _cargar_mapa(self, nombre_mapa):
        """Cargar archivo JSON de mapa y preparar surface."""
        # Intentar cargar desde mapas_unificados primero
        ruta_mapa = os.path.join(DATABASE_PATH, 'mapas_unificados', f"{nombre_mapa}.json")
        if not os.path.exists(ruta_mapa):
            # Fallback a mapas/mundo/
            ruta_mapa = os.path.join(DATABASE_PATH, 'mapas', 'mundo', f"{nombre_mapa}.json")
        
        if not os.path.exists(ruta_mapa):
            print(f"[ERROR] Mapa no encontrado: {ruta_mapa}")
            return False
        
        try:
            with open(ruta_mapa, 'r', encoding='utf-8') as f:
                datos_mapa = json.load(f)
            
            self.mapa_actual = datos_mapa
            ancho = datos_mapa.get('ancho', 320)
            alto = datos_mapa.get('alto', 180)
            
            # Crear surface del mapa con fondo simple por ahora
            self.mapa_surface = pygame.Surface((ancho, alto))
            self.mapa_surface.fill(COLOR_CANVAS_BG)
            
            # TODO: Dibujar tilemap real desde capas
            
            print(f"[EditorCanvasDoble] Mapa cargado: {nombre_mapa} ({ancho}x{alto})")
            self.mapa_rect = self.mapa_surface.get_rect()
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo cargar mapa: {e}")
            return False
    
    def _guardar_config_actual(self):
        """Guardar configuracion actual a JSON por mapa."""
        if not self.mapa_actual:
            print("[AVISO] No hay mapa cargado, no se puede guardar.")
            return
        
        mapa_nombre = self.mapa_actual.get('nombre', 'mapa_sin_nombre')
        ruta_destino = os.path.join(NPC_EVENTO_BATALLA_POR_MAPA_DIR, f"{mapa_nombre}.json")
        
        config = {
            "version": "1.0",
            "mapa": mapa_nombre,
            "cantidad_enemigos": self.cantidad_enemigos,
            "enemigos_slots": self.enemigos_slots[:self.cantidad_enemigos],
            "heroes_slots": self.heroes_slots[:self.cantidad_enemigos],
        }
        
        try:
            with open(ruta_destino, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"[EditorCanvasDoble] Guardado: {ruta_destino}")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar: {e}")
    
    def procesar_eventos(self):
        """Procesar eventos del teclado y mouse."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ejecutando = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.ejecutando = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._procesar_click(event.pos, event.button)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos_actual = event.pos
    
    def _procesar_click(self, pos, boton):
        """Procesar click del mouse."""
        # Botones principales
        for boton_id, rect in self.botones.items():
            if rect.collidepoint(pos):
                self._ejecutar_accion_boton(boton_id)
                return
    
    def _ejecutar_accion_boton(self, boton_id):
        """Ejecutar accion segun boton clickeado."""
        if boton_id == "cargar_mapa":
            if self.mapas_disponibles:
                self._cargar_mapa(self.mapas_disponibles[self.mapa_seleccionado_idx])
        
        elif boton_id == "guardar":
            self._guardar_config_actual()
        
        elif boton_id == "cantidad_menos":
            if self.cantidad_enemigos > 1:
                self.cantidad_enemigos -= 1
        
        elif boton_id == "cantidad_mas":
            if self.cantidad_enemigos < MAX_SLOTS:
                self.cantidad_enemigos += 1
        
        elif boton_id == "salir":
            self.ejecutando = False
    
    def actualizar(self):
        """Actualizar logica del editor."""
        pass
    
    def dibujar(self):
        """Dibujar todo el editor."""
        self.pantalla.fill(COLOR_FONDO)
        
        # Dibujar canvas izquierdo (mundo)
        self._dibujar_canvas_izquierdo()
        
        # Dibujar canvas derecho (batalla)
        self._dibujar_canvas_derecho()
        
        # Dibujar barra inferior
        self._dibujar_barra_inferior()
        
        pygame.display.flip()
    
    def _dibujar_canvas_izquierdo(self):
        """Dibujar canvas del mapa del mundo."""
        rect_canvas = pygame.Rect(CANVAS_IZQ_X, CANVAS_IZQ_Y, ANCHO_CANVAS, ALTO_CANVAS)
        pygame.draw.rect(self.pantalla, COLOR_CANVAS_BG, rect_canvas)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, rect_canvas, 2)
        
        # Dibujar titulo
        titulo = self.fuente_pequena.render("Canvas Mundo (Izq)", True, COLOR_TEXTO)
        self.pantalla.blit(titulo, (CANVAS_IZQ_X + 5, CANVAS_IZQ_Y + 5))
        
        # Dibujar mapa si esta cargado
        if self.mapa_surface:
            self.pantalla.blit(self.mapa_surface, (CANVAS_IZQ_X + 10, CANVAS_IZQ_Y + 30))
        
        # Texto auxiliar
        if not self.mapa_actual:
            texto_carga = self.fuente_pequena.render("Presiona 'Cargar Mapa' para comenzar", True, COLOR_TEXTO)
            self.pantalla.blit(texto_carga, (CANVAS_IZQ_X + 10, CANVAS_IZQ_Y + 100))
    
    def _dibujar_canvas_derecho(self):
        """Dibujar canvas de preview de batalla."""
        rect_canvas = pygame.Rect(CANVAS_DER_X, CANVAS_DER_Y, ANCHO_CANVAS, ALTO_CANVAS)
        pygame.draw.rect(self.pantalla, COLOR_CANVAS_BG, rect_canvas)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, rect_canvas, 2)
        
        # Dibujar titulo
        titulo = self.fuente_pequena.render(f"Canvas Batalla - {self.cantidad_enemigos} Enemigos (Der)", True, COLOR_TEXTO)
        self.pantalla.blit(titulo, (CANVAS_DER_X + 5, CANVAS_DER_Y + 5))
        
        # Dibujar slots de enemigos y heroes
        self._dibujar_slots_batalla(rect_canvas)
    
    def _dibujar_slots_batalla(self, rect_canvas):
        """Dibujar slots de batalla con sprites."""
        x_enemigos = CANVAS_DER_X + 20
        x_heroes = CANVAS_DER_X + ANCHO_CANVAS - 100
        y_base = CANVAS_DER_Y + 35
        y_spacing = 65
        
        # Label enemigos
        label_enemigos = self.fuente_pequena.render("Enemigos:", True, COLOR_TEXTO)
        self.pantalla.blit(label_enemigos, (x_enemigos, y_base - 25))
        
        # Dibujar slots de enemigos
        for i in range(self.cantidad_enemigos):
            slot_rect = pygame.Rect(x_enemigos, y_base + i * y_spacing, 70, 55)
            pygame.draw.rect(self.pantalla, COLOR_PANEL_BG, slot_rect)
            pygame.draw.rect(self.pantalla, COLOR_BORDE, slot_rect, 2)
            
            # Dibujar sprite o placeholder
            slot_data = self.enemigos_slots[i]
            if slot_data.get('monstruo_id'):
                if slot_data['monstruo_id'] in self.sprites_monstruos_cache:
                    sprite = self.sprites_monstruos_cache[slot_data['monstruo_id']]
                    self.pantalla.blit(sprite, (x_enemigos + 5, y_base + 5 + i * y_spacing))
                texto = self.fuente_pequena.render(f"E{i+1}: {slot_data['monstruo_id'][:8]}", True, COLOR_TEXTO)
            else:
                texto = self.fuente_pequena.render(f"E{i+1}: vacio", True, COLOR_TEXTO)
            
            self.pantalla.blit(texto, (x_enemigos + 5, y_base + 40 + i * y_spacing))
        
        # Label heroes
        label_heroes = self.fuente_pequena.render("Heroes:", True, COLOR_TEXTO)
        self.pantalla.blit(label_heroes, (x_heroes, y_base - 25))
        
        # Dibujar slots de heroes
        for i in range(self.cantidad_enemigos):
            slot_rect = pygame.Rect(x_heroes, y_base + i * y_spacing, 70, 55)
            pygame.draw.rect(self.pantalla, COLOR_PANEL_BG, slot_rect)
            pygame.draw.rect(self.pantalla, COLOR_BORDE, slot_rect, 2)
            
            # Dibujar sprite o placeholder
            slot_data = self.heroes_slots[i]
            if slot_data.get('heroe_id'):
                if slot_data['heroe_id'] in self.sprites_heroes_cache:
                    sprite = self.sprites_heroes_cache[slot_data['heroe_id']]
                    self.pantalla.blit(sprite, (x_heroes + 5, y_base + 5 + i * y_spacing))
                texto = self.fuente_pequena.render(f"H{i+1}: {slot_data['heroe_id'][:8]}", True, COLOR_TEXTO)
            else:
                texto = self.fuente_pequena.render(f"H{i+1}: vacio", True, COLOR_TEXTO)
            
            self.pantalla.blit(texto, (x_heroes + 5, y_base + 40 + i * y_spacing))
    
    def _dibujar_barra_inferior(self):
        """Dibujar barra de botones inferior."""
        rect_barra = pygame.Rect(0, BARRA_Y, ANCHO_PANTALLA, ALTO_BARRA_INFERIOR)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_BG, rect_barra)
        pygame.draw.line(self.pantalla, COLOR_BORDE, (0, BARRA_Y), (ANCHO_PANTALLA, BARRA_Y), 2)
        
        # Dibujar botones
        self._dibujar_boton(self.botones["cargar_mapa"], "Cargar Mapa")
        self._dibujar_boton(self.botones["guardar"], "Guardar")
        self._dibujar_boton(self.botones["cargar"], "Cargar")
        self._dibujar_boton(self.botones["resetear"], "Resetear")
        self._dibujar_boton(self.botones["salir"], "Salir")
        
        # Mostrar cantidad de enemigos
        texto_cantidad = self.fuente_pequena.render(f"Cant: {self.cantidad_enemigos}", True, COLOR_TEXTO)
        self.pantalla.blit(texto_cantidad, (ANCHO_PANTALLA // 2 - 30, BARRA_Y + 15))
        
        self._dibujar_boton(self.botones["cantidad_menos"], "-")
        self._dibujar_boton(self.botones["cantidad_mas"], "+")
    
    def _dibujar_boton(self, rect, texto):
        """Dibujar un boton."""
        pygame.draw.rect(self.pantalla, COLOR_ACTIVO, rect)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, rect, 2)
        
        label = self.fuente_pequena.render(texto, True, COLOR_FONDO)
        label_rect = label.get_rect(center=rect.center)
        self.pantalla.blit(label, label_rect)
    
    def ejecutar(self):
        """Bucle principal del editor."""
        while self.ejecutando:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(self.fps)
        
        pygame.quit()
        print("[EditorCanvasDoble] Editor cerrado.")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        editor = EditorCanvasDoble()
        editor.ejecutar()
    except Exception as e:
        print(f"[ERROR FATAL] {e}")
        import traceback
        traceback.print_exc()
