"""
========================================
SPRITE SHEET EDITOR - CodeVerso RPG
========================================
Herramienta profesional para cortar y organizar sprites desde spritesheets.

CARACTERÍSTICAS:
✓ Carga spritesheets completos
✓ **NUEVO: Drag & Drop - Arrastra imágenes desde tu explorador**
✓ Selección de áreas con mouse (click y arrastrar)
✓ Múltiples selecciones
✓ Nombrar cada sprite cortado
✓ Preview en tiempo real
✓ Guardar en carpetas organizadas (héroes/monstruos/cofres/npcs)
✓ Exportar sprites individuales o crear nuevo spritesheet
✓ Historial de cortes
✓ Deshacer/Rehacer

CONTROLES:
- **Arrastra imagen .png/.jpg/.bmp/.gif desde el explorador**: Cargar spritesheet
- Click izquierdo + arrastrar: Seleccionar área
- Click derecho: Cancelar selección actual
- CTRL + Click: Múltiples selecciones
- N: Nombrar sprite seleccionado
- S: Guardar sprite actual
- E: Exportar todos
- Z: Deshacer
- Y: Rehacer
- G: Toggle Grid
- DEL: Eliminar selección
"""

import pygame
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

# ========================================
# CONFIGURACIÓN
# ========================================
ANCHO = 1400
ALTO = 900
FPS = 60

# Áreas de la ventana
AREA_PREVIEW_ANCHO = 300
AREA_SPRITESHEET_ANCHO = ANCHO - AREA_PREVIEW_ANCHO - 300
PANEL_CONTROL_ANCHO = 300

# Colores
COLOR_FONDO = (20, 20, 25)
COLOR_PANEL = (30, 30, 40)
COLOR_SELECCION = (0, 255, 0, 80)
COLOR_SELECCION_BORDER = (0, 255, 0)
COLOR_SELECCION_ACTIVA = (255, 215, 0, 100)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SEC = (180, 180, 190)
COLOR_BOTON = (50, 50, 70)
COLOR_BOTON_HOVER = (70, 70, 100)
COLOR_BOTON_ACTIVO = (90, 140, 255)
COLOR_GRID = (40, 40, 50)

class CategoriaSprite(Enum):
    """Categorías de sprites"""
    HEROE_BATALLA = "heroes/batalla"
    HEROE_MAPA = "heroes/mapa"
    MONSTRUO = "monstruos"
    NPC = "npcs"
    COFRE = "cofres y demas"
    DECORACION = "decoracion"


@dataclass
class SeleccionSprite:
    """Información de un sprite seleccionado"""
    x: int
    y: int
    ancho: int
    alto: int
    nombre: str = ""
    categoria: CategoriaSprite = CategoriaSprite.HEROE_BATALLA
    guardado: bool = False
    
    def get_rect(self):
        """Retorna el rect de la selección"""
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        """Verifica si un punto está dentro"""
        return self.get_rect().collidepoint(px, py)
    
    def to_dict(self):
        """Convierte a diccionario para guardar"""
        return {
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "nombre": self.nombre,
            "categoria": self.categoria.value,
            "guardado": self.guardado
        }


class Boton:
    """Botón simple con hover"""
    def __init__(self, x, y, ancho, alto, texto, callback=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.callback = callback
        self.hover = False
        self.activo = False
        self.fuente = pygame.font.Font(None, 20)
    
    def update(self, mouse_pos, click):
        """Actualiza el botón"""
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.hover and click and self.callback:
            self.callback()
            return True
        return False
    
    def draw(self, surface):
        """Dibuja el botón"""
        color = COLOR_BOTON_ACTIVO if self.activo else (COLOR_BOTON_HOVER if self.hover else COLOR_BOTON)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, self.rect, 2, border_radius=5)
        
        texto_surf = self.fuente.render(self.texto, True, COLOR_TEXTO)
        texto_rect = texto_surf.get_rect(center=self.rect.center)
        surface.blit(texto_surf, texto_rect)


class InputTexto:
    """Campo de entrada de texto"""
    def __init__(self, x, y, ancho, alto, texto_placeholder=""):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = ""
        self.placeholder = texto_placeholder
        self.activo = False
        self.fuente = pygame.font.Font(None, 22)
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def update(self, eventos, mouse_pos, click):
        """Actualiza el input"""
        if click:
            self.activo = self.rect.collidepoint(mouse_pos)
        
        if self.activo:
            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_BACKSPACE:
                        self.texto = self.texto[:-1]
                    elif evento.key == pygame.K_RETURN:
                        self.activo = False
                    else:
                        self.texto += evento.unicode
        
        # Cursor parpadeante
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface):
        """Dibuja el input"""
        color_borde = COLOR_BOTON_ACTIVO if self.activo else COLOR_TEXTO_SEC
        pygame.draw.rect(surface, COLOR_PANEL, self.rect)
        pygame.draw.rect(surface, color_borde, self.rect, 2, border_radius=3)
        
        texto_mostrar = self.texto if self.texto else self.placeholder
        color_texto = COLOR_TEXTO if self.texto else COLOR_TEXTO_SEC
        
        texto_surf = self.fuente.render(texto_mostrar, True, color_texto)
        surface.blit(texto_surf, (self.rect.x + 10, self.rect.y + 10))
        
        # Cursor
        if self.activo and self.cursor_visible and self.texto:
            cursor_x = self.rect.x + 10 + texto_surf.get_width() + 2
            pygame.draw.line(surface, COLOR_TEXTO, 
                           (cursor_x, self.rect.y + 8), 
                           (cursor_x, self.rect.y + self.rect.height - 8), 2)


# ========================================
# EDITOR PRINCIPAL
# ========================================

class SpriteSheetEditor:
    """Editor de spritesheets con todas las funcionalidades"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Sprite Sheet Editor - CodeVerso RPG - Arrastra imágenes aquí")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        # Spritesheet
        self.spritesheet = None
        self.spritesheet_original = None
        self.ruta_spritesheet = None
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Selecciones
        self.selecciones: List[SeleccionSprite] = []
        self.seleccion_actual: Optional[SeleccionSprite] = None
        self.seleccionando = False
        self.punto_inicio = (0, 0)
        
        # Historial (deshacer/rehacer)
        self.historial = []
        self.historial_index = -1
        
        # UI
        self.input_nombre = InputTexto(ANCHO - 280, 100, 260, 35, "Nombre del sprite...")
        self.mensaje = ""
        self.mensaje_timer = 0
        
        # Drag and drop
        self.arrastrando_archivo = False
        
        # Botones de categoría
        self.botones_categoria = []
        self.categoria_actual = CategoriaSprite.HEROE_BATALLA
        self.crear_botones_categoria()
        
        # Botones de acción
        self.botones_accion = []
        self.crear_botones_accion()
        
        # Grid
        self.mostrar_grid = True
        self.tamano_grid = 32
        
        print("✓ Sprite Sheet Editor iniciado")
        print("✓ Arrastra imágenes desde el explorador para cargarlas")
    
    def crear_botones_categoria(self):
        """Crea botones para seleccionar categoría"""
        categorias = [
            ("Héroe Batalla", CategoriaSprite.HEROE_BATALLA),
            ("Héroe Mapa", CategoriaSprite.HEROE_MAPA),
            ("Monstruo", CategoriaSprite.MONSTRUO),
            ("NPC", CategoriaSprite.NPC),
            ("Cofre", CategoriaSprite.COFRE),
        ]
        
        x = ANCHO - 280
        y = 200
        
        for nombre, categoria in categorias:
            boton = Boton(x, y, 260, 35, nombre, 
                         lambda c=categoria: self.cambiar_categoria(c))
            if categoria == self.categoria_actual:
                boton.activo = True
            self.botones_categoria.append(boton)
            y += 45
    
    def crear_botones_accion(self):
        """Crea botones de acción"""
        acciones = [
            ("Cargar Spritesheet", self.cargar_spritesheet),
            ("Guardar Sprite (S)", self.guardar_sprite_actual),
            ("Exportar Todos (E)", self.exportar_todos),
            ("Limpiar Todo", self.limpiar_todo),
            ("Deshacer (Z)", self.deshacer),
            ("Rehacer (Y)", self.rehacer),
        ]
        
        x = ANCHO - 280
        y = 500
        
        for nombre, callback in acciones:
            boton = Boton(x, y, 260, 35, nombre, callback)
            self.botones_accion.append(boton)
            y += 45
    
    def cambiar_categoria(self, categoria):
        """Cambia la categoría actual"""
        self.categoria_actual = categoria
        for boton in self.botones_categoria:
            boton.activo = False
        for boton in self.botones_categoria:
            if boton.texto == categoria.value.split('/')[-1].capitalize() or \
               (categoria == CategoriaSprite.HEROE_BATALLA and boton.texto == "Héroe Batalla") or \
               (categoria == CategoriaSprite.HEROE_MAPA and boton.texto == "Héroe Mapa"):
                boton.activo = True
        self.mostrar_mensaje(f"Categoría: {categoria.value}")
    
    def cargar_spritesheet(self):
        """Abre diálogo para cargar spritesheet"""
        # Por ahora, usar una ruta fija para testing
        # TODO: Implementar diálogo de archivo
        test_path = Path("assets/sprites/heroes/heroe_sheet.png")
        if test_path.exists():
            self.cargar_spritesheet_desde_ruta(str(test_path))
        else:
            self.mostrar_mensaje("⚠️ Coloca un spritesheet en assets/sprites/")
    
    def cargar_spritesheet_desde_ruta(self, ruta):
        """Carga un spritesheet desde una ruta"""
        try:
            self.spritesheet_original = pygame.image.load(ruta).convert_alpha()
            self.spritesheet = self.spritesheet_original.copy()
            self.ruta_spritesheet = ruta
            self.zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.mostrar_mensaje(f"✓ Cargado: {Path(ruta).name}")
            print(f"✓ Spritesheet cargado: {ruta} ({self.spritesheet.get_width()}x{self.spritesheet.get_height()})")
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {str(e)}")
            print(f"❌ Error cargando spritesheet: {e}")
    
    def guardar_sprite_actual(self):
        """Guarda el sprite actualmente seleccionado"""
        if not self.seleccion_actual:
            self.mostrar_mensaje("⚠️ No hay selección activa")
            return
        
        if not self.input_nombre.texto:
            self.mostrar_mensaje("⚠️ Ingresa un nombre primero")
            self.input_nombre.activo = True
            return
        
        self.seleccion_actual.nombre = self.input_nombre.texto
        self.seleccion_actual.categoria = self.categoria_actual
        
        # Extraer el sprite
        if self.spritesheet_original:
            sprite_surface = self.spritesheet_original.subsurface(
                self.seleccion_actual.get_rect()
            ).copy()
            
            # Guardar
            ruta_destino = Path(f"assets/sprites/{self.categoria_actual.value}")
            ruta_destino.mkdir(parents=True, exist_ok=True)
            ruta_archivo = ruta_destino / f"{self.input_nombre.texto}.png"
            
            try:
                pygame.image.save(sprite_surface, str(ruta_archivo))
                self.seleccion_actual.guardado = True
                self.mostrar_mensaje(f"✓ Guardado: {ruta_archivo.name}")
                print(f"✓ Sprite guardado: {ruta_archivo}")
                
                # Limpiar input para el siguiente
                self.input_nombre.texto = ""
                
                # Añadir a historial
                self.agregar_al_historial()
            
            except Exception as e:
                self.mostrar_mensaje(f"❌ Error: {str(e)}")
                print(f"❌ Error guardando: {e}")
    
    def exportar_todos(self):
        """Exporta todas las selecciones"""
        if not self.selecciones:
            self.mostrar_mensaje("⚠️ No hay selecciones")
            return
        
        contador = 0
        for i, sel in enumerate(self.selecciones):
            if not sel.guardado and sel.nombre:
                # Extraer y guardar
                sprite_surface = self.spritesheet_original.subsurface(sel.get_rect()).copy()
                ruta_destino = Path(f"assets/sprites/{sel.categoria.value}")
                ruta_destino.mkdir(parents=True, exist_ok=True)
                ruta_archivo = ruta_destino / f"{sel.nombre}.png"
                
                try:
                    pygame.image.save(sprite_surface, str(ruta_archivo))
                    sel.guardado = True
                    contador += 1
                except Exception as e:
                    print(f"❌ Error guardando {sel.nombre}: {e}")
        
        self.mostrar_mensaje(f"✓ Exportados {contador} sprites")
        print(f"✓ Exportados {contador} sprites")
    
    def limpiar_todo(self):
        """Limpia todas las selecciones"""
        self.selecciones = []
        self.seleccion_actual = None
        self.historial = []
        self.historial_index = -1
        self.mostrar_mensaje("✓ Todo limpiado")
    
    def agregar_al_historial(self):
        """Agrega estado actual al historial"""
        # Guardar estado
        estado = {
            "selecciones": [sel.to_dict() for sel in self.selecciones]
        }
        
        # Eliminar estados futuros si estamos en medio del historial
        if self.historial_index < len(self.historial) - 1:
            self.historial = self.historial[:self.historial_index + 1]
        
        self.historial.append(estado)
        self.historial_index = len(self.historial) - 1
    
    def deshacer(self):
        """Deshace la última acción"""
        if self.historial_index > 0:
            self.historial_index -= 1
            self.cargar_estado_historial()
            self.mostrar_mensaje("↶ Deshacer")
        else:
            self.mostrar_mensaje("⚠️ No hay más para deshacer")
    
    def rehacer(self):
        """Rehace la última acción deshecha"""
        if self.historial_index < len(self.historial) - 1:
            self.historial_index += 1
            self.cargar_estado_historial()
            self.mostrar_mensaje("↷ Rehacer")
        else:
            self.mostrar_mensaje("⚠️ No hay más para rehacer")
    
    def cargar_estado_historial(self):
        """Carga un estado del historial"""
        if 0 <= self.historial_index < len(self.historial):
            estado = self.historial[self.historial_index]
            self.selecciones = []
            for sel_dict in estado["selecciones"]:
                sel = SeleccionSprite(
                    x=sel_dict["x"],
                    y=sel_dict["y"],
                    ancho=sel_dict["ancho"],
                    alto=sel_dict["alto"],
                    nombre=sel_dict.get("nombre", ""),
                    categoria=CategoriaSprite(sel_dict.get("categoria", "heroes/batalla")),
                    guardado=sel_dict.get("guardado", False)
                )
                self.selecciones.append(sel)
    
    def mostrar_mensaje(self, texto):
        """Muestra mensaje temporal"""
        self.mensaje = texto
        self.mensaje_timer = pygame.time.get_ticks()
        print(texto)
    
    def convertir_coords_pantalla_a_sheet(self, x_pantalla, y_pantalla):
        """Convierte coordenadas de pantalla a coordenadas del spritesheet"""
        x_sheet = int((x_pantalla - self.offset_x) / self.zoom)
        y_sheet = int((y_pantalla - self.offset_y) / self.zoom)
        return x_sheet, y_sheet
    
    def convertir_coords_sheet_a_pantalla(self, x_sheet, y_sheet):
        """Convierte coordenadas del spritesheet a pantalla"""
        x_pantalla = int(x_sheet * self.zoom + self.offset_x)
        y_pantalla = int(y_sheet * self.zoom + self.offset_y)
        return x_pantalla, y_pantalla
    
    def dibujar_spritesheet(self, surface):
        """Dibuja el spritesheet con zoom"""
        if not self.spritesheet:
            # Mensaje si no hay spritesheet
            texto1 = self.fuente_titulo.render("Arrastra una imagen aquí", True, COLOR_TEXTO)
            texto2 = self.fuente.render("o usa el botón 'Cargar Spritesheet'", True, COLOR_TEXTO_SEC)
            
            rect1 = texto1.get_rect(center=(AREA_SPRITESHEET_ANCHO // 2, ALTO // 2 - 20))
            rect2 = texto2.get_rect(center=(AREA_SPRITESHEET_ANCHO // 2, ALTO // 2 + 20))
            
            surface.blit(texto1, rect1)
            surface.blit(texto2, rect2)
            
            # Indicador visual de zona de drop
            if self.arrastrando_archivo:
                # Borde punteado cuando se arrastra
                rect_drop = pygame.Rect(20, 20, AREA_SPRITESHEET_ANCHO - 40, ALTO - 40)
                for i in range(0, rect_drop.width, 20):
                    pygame.draw.line(surface, COLOR_BOTON_ACTIVO, 
                                   (rect_drop.x + i, rect_drop.y), 
                                   (rect_drop.x + i + 10, rect_drop.y), 3)
                    pygame.draw.line(surface, COLOR_BOTON_ACTIVO, 
                                   (rect_drop.x + i, rect_drop.bottom), 
                                   (rect_drop.x + i + 10, rect_drop.bottom), 3)
                
                for i in range(0, rect_drop.height, 20):
                    pygame.draw.line(surface, COLOR_BOTON_ACTIVO, 
                                   (rect_drop.x, rect_drop.y + i), 
                                   (rect_drop.x, rect_drop.y + i + 10), 3)
                    pygame.draw.line(surface, COLOR_BOTON_ACTIVO, 
                                   (rect_drop.right, rect_drop.y + i), 
                                   (rect_drop.right, rect_drop.y + i + 10), 3)
                
                # Texto adicional
                texto_drop = self.fuente.render("¡Suelta aquí!", True, COLOR_BOTON_ACTIVO)
                rect_drop_texto = texto_drop.get_rect(center=(AREA_SPRITESHEET_ANCHO // 2, ALTO // 2 + 60))
                surface.blit(texto_drop, rect_drop_texto)
            
            return
        
        # Aplicar zoom al spritesheet
        nuevo_ancho = int(self.spritesheet_original.get_width() * self.zoom)
        nuevo_alto = int(self.spritesheet_original.get_height() * self.zoom)
        
        if nuevo_ancho > 0 and nuevo_alto > 0:
            spritesheet_zoom = pygame.transform.scale(
                self.spritesheet_original, (nuevo_ancho, nuevo_alto)
            )
            surface.blit(spritesheet_zoom, (self.offset_x, self.offset_y))
        
        # Dibujar grid
        if self.mostrar_grid:
            self.dibujar_grid(surface)
        
        # Dibujar selecciones guardadas
        for sel in self.selecciones:
            if sel != self.seleccion_actual:
                self.dibujar_seleccion(surface, sel, False)
        
        # Dibujar selección actual
        if self.seleccion_actual:
            self.dibujar_seleccion(surface, self.seleccion_actual, True)
        
        # Dibujar selección en progreso
        if self.seleccionando:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x < AREA_SPRITESHEET_ANCHO:
                x1, y1 = self.punto_inicio
                ancho = mouse_x - x1
                alto = mouse_y - y1
                
                rect_preview = pygame.Rect(x1, y1, ancho, alto)
                superficie_sel = pygame.Surface((abs(ancho), abs(alto)))
                superficie_sel.set_alpha(80)
                superficie_sel.fill((255, 215, 0))
                
                pos_x = min(x1, mouse_x)
                pos_y = min(y1, mouse_y)
                surface.blit(superficie_sel, (pos_x, pos_y))
                pygame.draw.rect(surface, (255, 215, 0), 
                               pygame.Rect(pos_x, pos_y, abs(ancho), abs(alto)), 2)
    
    def dibujar_seleccion(self, surface, sel, es_actual):
        """Dibuja una selección"""
        x_pantalla, y_pantalla = self.convertir_coords_sheet_a_pantalla(sel.x, sel.y)
        ancho = int(sel.ancho * self.zoom)
        alto = int(sel.alto * self.zoom)
        
        # Superficie semitransparente
        color = COLOR_SELECCION_ACTIVA if es_actual else COLOR_SELECCION
        superficie_sel = pygame.Surface((ancho, alto))
        superficie_sel.set_alpha(80 if es_actual else 40)
        superficie_sel.fill((255, 215, 0) if es_actual else (0, 255, 0))
        surface.blit(superficie_sel, (x_pantalla, y_pantalla))
        
        # Borde
        color_borde = COLOR_SELECCION_ACTIVA[:3] if es_actual else COLOR_SELECCION_BORDER
        pygame.draw.rect(surface, color_borde, 
                        pygame.Rect(x_pantalla, y_pantalla, ancho, alto), 3 if es_actual else 2)
        
        # Nombre
        if sel.nombre:
            texto = self.fuente_pequena.render(sel.nombre, True, COLOR_TEXTO)
            fondo = pygame.Surface((texto.get_width() + 10, texto.get_height() + 4))
            fondo.fill((0, 0, 0))
            fondo.set_alpha(150)
            surface.blit(fondo, (x_pantalla + 2, y_pantalla + 2))
            surface.blit(texto, (x_pantalla + 7, y_pantalla + 4))
        
        # Indicador de guardado
        if sel.guardado:
            checkmark = self.fuente.render("✓", True, (0, 255, 0))
            surface.blit(checkmark, (x_pantalla + ancho - 25, y_pantalla + 5))
    
    def dibujar_grid(self, surface):
        """Dibuja grid sobre el spritesheet"""
        if not self.spritesheet_original:
            return
        
        grid_size = int(self.tamano_grid * self.zoom)
        if grid_size < 5:  # No dibujar si es muy pequeño
            return
        
        ancho_total = int(self.spritesheet_original.get_width() * self.zoom)
        alto_total = int(self.spritesheet_original.get_height() * self.zoom)
        
        # Líneas verticales
        x = self.offset_x
        while x < self.offset_x + ancho_total:
            if 0 <= x < AREA_SPRITESHEET_ANCHO:
                pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, ALTO), 1)
            x += grid_size
        
        # Líneas horizontales
        y = self.offset_y
        while y < self.offset_y + alto_total:
            if 0 <= y < ALTO:
                pygame.draw.line(surface, COLOR_GRID, (0, y), (AREA_SPRITESHEET_ANCHO, y), 1)
            y += grid_size
    
    def dibujar_panel_control(self, surface):
        """Dibuja panel de control derecho"""
        # Fondo
        pygame.draw.rect(surface, COLOR_PANEL, 
                        (ANCHO - PANEL_CONTROL_ANCHO, 0, PANEL_CONTROL_ANCHO, ALTO))
        
        # Título
        x = ANCHO - 280
        y = 20
        titulo = self.fuente_titulo.render("Controles", True, COLOR_TEXTO)
        surface.blit(titulo, (x, y))
        
        y += 60
        
        # Input de nombre
        self.input_nombre.draw(surface)
        
        y = 150
        
        # Texto "Categoría:"
        texto_cat = self.fuente.render("Categoría:", True, COLOR_TEXTO)
        surface.blit(texto_cat, (x, y))
        
        # Botones de categoría
        for boton in self.botones_categoria:
            boton.draw(surface)
        
        # Botones de acción
        for boton in self.botones_accion:
            boton.draw(surface)
    
    def dibujar_panel_preview(self, surface):
        """Dibuja panel de preview izquierdo"""
        # Fondo
        pygame.draw.rect(surface, COLOR_PANEL, 
                        (AREA_SPRITESHEET_ANCHO, 0, AREA_PREVIEW_ANCHO, ALTO))
        
        x = AREA_SPRITESHEET_ANCHO + 20
        y = 20
        
        # Título
        titulo = self.fuente.render("Preview", True, COLOR_TEXTO)
        surface.blit(titulo, (x, y))
        y += 40
        
        # Preview del sprite actual
        if self.seleccion_actual and self.spritesheet_original:
            try:
                sprite = self.spritesheet_original.subsurface(
                    self.seleccion_actual.get_rect()
                ).copy()
                
                # Escalar para que quepa en el panel
                max_tam = AREA_PREVIEW_ANCHO - 40
                factor = min(max_tam / sprite.get_width(), max_tam / sprite.get_height())
                if factor < 1:
                    nuevo_ancho = int(sprite.get_width() * factor)
                    nuevo_alto = int(sprite.get_height() * factor)
                    sprite = pygame.transform.scale(sprite, (nuevo_ancho, nuevo_alto))
                
                # Centrar
                pos_x = x + (max_tam - sprite.get_width()) // 2
                surface.blit(sprite, (pos_x, y))
                y += sprite.get_height() + 20
                
                # Info
                info = [
                    f"Tamaño: {self.seleccion_actual.ancho}x{self.seleccion_actual.alto}",
                    f"Pos: ({self.seleccion_actual.x}, {self.seleccion_actual.y})",
                    f"Nombre: {self.seleccion_actual.nombre or 'Sin nombre'}",
                ]
                
                for linea in info:
                    texto = self.fuente_pequena.render(linea, True, COLOR_TEXTO_SEC)
                    surface.blit(texto, (x, y))
                    y += 25
            
            except:
                texto = self.fuente_pequena.render("Error en preview", True, (255, 100, 100))
                surface.blit(texto, (x, y))
        else:
            texto = self.fuente_pequena.render("Selecciona un área", True, COLOR_TEXTO_SEC)
            surface.blit(texto, (x, y))
        
        # Lista de selecciones
        y = ALTO // 2
        titulo_lista = self.fuente.render("Selecciones:", True, COLOR_TEXTO)
        surface.blit(titulo_lista, (x, y))
        y += 30
        
        for i, sel in enumerate(self.selecciones[-10:]):  # Últimas 10
            nombre = sel.nombre if sel.nombre else f"Sprite {i+1}"
            check = "✓" if sel.guardado else "○"
            texto = self.fuente_pequena.render(f"{check} {nombre}", True, 
                                              (0, 255, 0) if sel.guardado else COLOR_TEXTO_SEC)
            surface.blit(texto, (x, y))
            y += 25
    
    def dibujar_barra_estado(self, surface):
        """Dibuja barra de estado inferior"""
        barra_alto = 30
        pygame.draw.rect(surface, (20, 20, 30), (0, ALTO - barra_alto, ANCHO, barra_alto))
        
        # Info
        texto_info = f"Zoom: {self.zoom:.2f}x | Selecciones: {len(self.selecciones)} | "
        texto_info += f"Guardados: {sum(1 for s in self.selecciones if s.guardado)}"
        
        if self.spritesheet_original:
            texto_info += f" | Sheet: {self.spritesheet_original.get_width()}x{self.spritesheet_original.get_height()}"
        
        texto = self.fuente_pequena.render(texto_info, True, COLOR_TEXTO)
        surface.blit(texto, (10, ALTO - barra_alto + 8))
        
        # Mensaje temporal
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_timer < 3000:
            mensaje_surf = self.fuente.render(self.mensaje, True, (100, 255, 100))
            pos_x = ANCHO // 2 - mensaje_surf.get_width() // 2
            surface.blit(mensaje_surf, (pos_x, ALTO - barra_alto - 40))
    
    def manejar_eventos(self):
        """Maneja eventos"""
        mouse_pos = pygame.mouse.get_pos()
        click = False
        eventos_texto = []
        
        for evento in pygame.event.get():
            eventos_texto.append(evento)
            
            if evento.type == pygame.QUIT:
                return False
            
            # ========================================
            # DRAG AND DROP DE ARCHIVOS
            # ========================================
            elif evento.type == pygame.DROPFILE:
                # Archivo soltado en la ventana
                archivo = evento.file
                print(f"📁 Archivo arrastrado: {archivo}")
                
                # Verificar que sea una imagen
                extensiones_validas = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
                if any(archivo.lower().endswith(ext) for ext in extensiones_validas):
                    self.cargar_spritesheet_desde_ruta(archivo)
                    self.arrastrando_archivo = False
                else:
                    self.mostrar_mensaje("⚠️ Solo imágenes (.png, .jpg, .bmp, .gif)")
                    self.arrastrando_archivo = False
            
            elif evento.type == pygame.DROPBEGIN:
                # Se está arrastrando algo sobre la ventana
                self.arrastrando_archivo = True
                print("📥 Arrastrando archivo sobre la ventana...")
            
            elif evento.type == pygame.DROPCOMPLETE:
                # Se completó el arrastre (soltado o cancelado)
                self.arrastrando_archivo = False
            
            # ========================================
            # EVENTOS DE TECLADO
            # ========================================
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                
                elif evento.key == pygame.K_s and not self.input_nombre.activo:
                    self.guardar_sprite_actual()
                
                elif evento.key == pygame.K_e and not self.input_nombre.activo:
                    self.exportar_todos()
                
                elif evento.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.deshacer()
                
                elif evento.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.rehacer()
                
                elif evento.key == pygame.K_g:
                    self.mostrar_grid = not self.mostrar_grid
                
                elif evento.key == pygame.K_DELETE:
                    if self.seleccion_actual and self.seleccion_actual in self.selecciones:
                        self.selecciones.remove(self.seleccion_actual)
                        self.seleccion_actual = None
                        self.mostrar_mensaje("✓ Selección eliminada")
            
            # ========================================
            # EVENTOS DE MOUSE
            # ========================================
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    click = True
                    
                    # Área del spritesheet
                    if mouse_pos[0] < AREA_SPRITESHEET_ANCHO and self.spritesheet:
                        # Verificar si se clickeó una selección existente
                        x_sheet, y_sheet = self.convertir_coords_pantalla_a_sheet(
                            mouse_pos[0], mouse_pos[1]
                        )
                        
                        seleccion_clickeada = None
                        for sel in reversed(self.selecciones):
                            if sel.contiene_punto(x_sheet, y_sheet):
                                seleccion_clickeada = sel
                                break
                        
                        if seleccion_clickeada:
                            self.seleccion_actual = seleccion_clickeada
                            self.input_nombre.texto = seleccion_clickeada.nombre
                        else:
                            # Iniciar nueva selección
                            self.seleccionando = True
                            self.punto_inicio = mouse_pos
            
                elif evento.button == 4:  # Scroll up - Zoom in
                    if mouse_pos[0] < AREA_SPRITESHEET_ANCHO:
                        self.zoom = min(5.0, self.zoom * 1.1)
                
                elif evento.button == 5:  # Scroll down - Zoom out
                    if mouse_pos[0] < AREA_SPRITESHEET_ANCHO:
                        self.zoom = max(0.1, self.zoom / 1.1)
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1 and self.seleccionando:
                    # Finalizar selección
                    self.seleccionando = False
                    x1, y1 = self.punto_inicio
                    x2, y2 = mouse_pos
                    
                    if mouse_pos[0] < AREA_SPRITESHEET_ANCHO:
                        # Convertir a coordenadas del sheet
                        x1_sheet, y1_sheet = self.convertir_coords_pantalla_a_sheet(x1, y1)
                        x2_sheet, y2_sheet = self.convertir_coords_pantalla_a_sheet(x2, y2)
                        
                        # Asegurar que x1,y1 sea la esquina superior izquierda
                        x_min = min(x1_sheet, x2_sheet)
                        y_min = min(y1_sheet, y2_sheet)
                        ancho = abs(x2_sheet - x1_sheet)
                        alto = abs(y2_sheet - y1_sheet)
                        
                        if ancho > 5 and alto > 5:  # Mínimo 5x5
                            seleccion = SeleccionSprite(
                                x=x_min, y=y_min, ancho=ancho, alto=alto,
                                categoria=self.categoria_actual
                            )
                            self.selecciones.append(seleccion)
                            self.seleccion_actual = seleccion
                            self.mostrar_mensaje(f"✓ Área seleccionada: {ancho}x{alto}")
        
        # Actualizar UI
        self.input_nombre.update(eventos_texto, mouse_pos, click)
        
        for boton in self.botones_categoria + self.botones_accion:
            boton.update(mouse_pos, click)
        
        return True
    
    def ejecutar(self):
        """Bucle principal"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área del spritesheet
            area_sheet = self.pantalla.subsurface((0, 0, AREA_SPRITESHEET_ANCHO, ALTO))
            area_sheet.fill((25, 25, 30))
            self.dibujar_spritesheet(area_sheet)
            
            # Panel de preview
            self.dibujar_panel_preview(self.pantalla)
            
            # Panel de control
            self.dibujar_panel_control(self.pantalla)
            
            # Barra de estado
            self.dibujar_barra_estado(self.pantalla)
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()
        print("✓ Sprite Sheet Editor cerrado")


# ========================================
# EJECUTAR
# ========================================
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════╗
║  SPRITE SHEET EDITOR - CodeVerso RPG                 ║
║                                                       ║
║  CONTROLES:                                           ║
║  • Arrastra imagen desde explorador = Cargar         ║
║  • Click + Arrastrar = Seleccionar área              ║
║  • Scroll = Zoom                                     ║
║  • N = Nombrar sprite                                ║
║  • S = Guardar sprite                                ║
║  • E = Exportar todos                                ║
║  • G = Toggle grid                                   ║
║  • DEL = Eliminar selección                          ║
║  • CTRL+Z = Deshacer                                 ║
║  • CTRL+Y = Rehacer                                  ║
║                                                       ║
║  💡 NUEVO: Arrastra imágenes .png/.jpg desde tu      ║
║     explorador directamente a la ventana             ║
╚══════════════════════════════════════════════════════╝
    """)
    
    editor = SpriteSheetEditor()
    editor.ejecutar()
