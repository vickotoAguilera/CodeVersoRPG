"""
========================================
SPRITE SHEET EDITOR - CodeVerso RPG
========================================
Herramienta profesional para cortar y organizar sprites desde spritesheets.

CARACTERÍSTICAS:
✓ Carga spritesheets completos
✓ **NUEVO: Drag & Drop - Arrastra imágenes desde tu explorador**
✓ **NUEVO: Quitar Fondo - Elimina fondos automáticamente**
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
- Click derecho + arrastrar: Mover cámara (pan)
- **Click derecho en cuadrado**: Eliminar selección
- **Arrastrar bordes/esquinas**: Redimensionar selección
- Click en checkbox: Marcar/desmarcar sprite para exportar
- Rueda del mouse (en canvas): Zoom in/out
- **Rueda del mouse (en lista)**: Scroll de la lista
- **Botón "Quitar Fondo"**: Elimina el fondo del sprite seleccionado
- S: Guardar sprite actual
- E: Exportar todos los sprites marcados
- P: Toggle preview de animación
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
ANCHO = 800
ALTO = 600
FPS = 60

# Áreas de la ventana
AREA_PREVIEW_ANCHO = 200
AREA_SPRITESHEET_ANCHO = ANCHO - AREA_PREVIEW_ANCHO - 200
PANEL_CONTROL_ANCHO = 200

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
    seleccionado: bool = True  # Checkbox para exportar
    
    def get_rect(self):
        """Retorna el rect de la selección"""
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
    
    def get_rect_valido(self, spritesheet):
        """Retorna el rect validado para no salir de los límites del spritesheet"""
        if not spritesheet:
            return self.get_rect()
        
        max_x = spritesheet.get_width()
        max_y = spritesheet.get_height()
        
        # Ajustar coordenadas para que estén dentro del spritesheet
        x = max(0, min(self.x, max_x - 1))
        y = max(0, min(self.y, max_y - 1))
        ancho = max(1, min(self.ancho, max_x - x))
        alto = max(1, min(self.alto, max_y - y))
        
        return pygame.Rect(x, y, ancho, alto)
    
    def contiene_punto(self, px, py):
        """Verifica si un punto está dentro"""
        return self.get_rect().collidepoint(px, py)
    
    def get_borde_cercano(self, px, py, offset_x, offset_y, zoom, tolerancia=15):
        """Detecta si el punto está cerca de un borde/esquina para redimensionar"""
        rect = self.get_rect()
        
        # Convertir a coordenadas de pantalla con zoom y offset
        x1 = rect.x * zoom + offset_x
        y1 = rect.y * zoom + offset_y
        x2 = (rect.x + rect.width) * zoom + offset_x
        y2 = (rect.y + rect.height) * zoom + offset_y
        
        cerca_izq = abs(px - x1) < tolerancia
        cerca_der = abs(px - x2) < tolerancia
        cerca_arr = abs(py - y1) < tolerancia
        cerca_aba = abs(py - y2) < tolerancia
        
        dentro_x = x1 - tolerancia < px < x2 + tolerancia
        dentro_y = y1 - tolerancia < py < y2 + tolerancia
        
        # Esquinas (prioridad)
        if cerca_izq and cerca_arr and dentro_x and dentro_y:
            return 'tl'  # top-left
        if cerca_der and cerca_arr and dentro_x and dentro_y:
            return 'tr'  # top-right
        if cerca_izq and cerca_aba and dentro_x and dentro_y:
            return 'bl'  # bottom-left
        if cerca_der and cerca_aba and dentro_x and dentro_y:
            return 'br'  # bottom-right
        
        # Bordes
        if cerca_arr and dentro_x:
            return 'top'
        if cerca_aba and dentro_x:
            return 'bottom'
        if cerca_izq and dentro_y:
            return 'left'
        if cerca_der and dentro_y:
            return 'right'
        
        return None
    
    def to_dict(self):
        """Convierte a diccionario para guardar"""
        return {
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "nombre": self.nombre,
            "categoria": self.categoria.value,
            "guardado": self.guardado,
            "seleccionado": self.seleccionado
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
        
        # Control de ventana
        self.fullscreen = False
        self.ventana_ancho = ANCHO
        self.ventana_alto = ALTO
        
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
        
        # Pan de cámara
        self.panning = False
        self.pan_inicio = (0, 0)
        
        # Selecciones
        self.selecciones: List[SeleccionSprite] = []
        self.seleccion_actual: Optional[SeleccionSprite] = None
        self.seleccionando = False
        self.punto_inicio = (0, 0)
        
        # Redimensionamiento de selecciones
        self.redimensionando = False
        self.borde_seleccionado = None  # 'top', 'bottom', 'left', 'right', 'tl', 'tr', 'bl', 'br'
        self.punto_resize_inicio = (0, 0)
        
        # Scroll en lista de sprites
        self.scroll_lista_offset = 0
        self.scroll_lista_max = 0
        
        # Historial (deshacer/rehacer)
        self.historial = []
        self.historial_index = -1
        
        # UI
        self.input_nombre = InputTexto(self.ventana_ancho - (PANEL_CONTROL_ANCHO - 20), 80, PANEL_CONTROL_ANCHO - 40, 30, "Nombre del sprite...")
        self.mensaje = ""
        self.mensaje_timer = 0
        
        # Drag and drop
        self.arrastrando_archivo = False
        
        # Preview de animación
        self.ventana_preview_activa = False
        self.preview_frame_actual = 0
        self.preview_timer = 0
        self.preview_velocidad = 10  # frames entre cambios
        
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
        
        # Checkboxes
        self.checkbox_rects = []
        
        # Quitar fondo
        self.tolerancia_fondo = 30  # Tolerancia para detectar colores similares
        
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
        
        x = self.ventana_ancho - (PANEL_CONTROL_ANCHO - 20)
        y = 180
        
        for nombre, categoria in categorias:
            boton = Boton(x, y, PANEL_CONTROL_ANCHO - 40, 30, nombre, 
                         lambda c=categoria: self.cambiar_categoria(c))
            if categoria == self.categoria_actual:
                boton.activo = True
            self.botones_categoria.append(boton)
            y += 38
    
    def actualizar_input_posicion(self):
        """Actualiza la posición del input cuando cambia el tamaño de ventana"""
        self.input_nombre.rect.x = self.ventana_ancho - (PANEL_CONTROL_ANCHO - 20)
        self.input_nombre.rect.y = 80
        self.input_nombre.rect.width = PANEL_CONTROL_ANCHO - 40
    
    def crear_botones_accion(self):
        """Crea botones de acción"""
        acciones = [
            ("Cargar", self.cargar_spritesheet),
            ("Preview", self.toggle_preview),
            ("Quitar Fondo", self.quitar_fondo_sprite),
            ("Guardar (S)", self.guardar_sprite_actual),
            ("Exportar (E)", self.exportar_todos),
            ("Limpiar", self.limpiar_todo),
            ("Deshacer (Z)", self.deshacer),
            ("Rehacer (Y)", self.rehacer),
            ("Fullscreen (F)", self.toggle_fullscreen),
        ]
        
        x = self.ventana_ancho - (PANEL_CONTROL_ANCHO - 20)
        y = 450
        
        for nombre, callback in acciones:
            boton = Boton(x, y, PANEL_CONTROL_ANCHO - 40, 30, nombre, callback)
            self.botones_accion.append(boton)
            y += 38
    
    def toggle_fullscreen(self):
        """Alterna entre modo ventana y pantalla completa"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.RESIZABLE)
            self.ventana_ancho = self.pantalla.get_width()
            self.ventana_alto = self.pantalla.get_height()
            self.mostrar_mensaje("✓ Pantalla completa (F para salir)")
        else:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
            self.ventana_ancho = ANCHO
            self.ventana_alto = ALTO
            self.mostrar_mensaje("✓ Modo ventana")
        
        # Recrear botones para nueva posición
        self.botones_categoria = []
        self.botones_accion = []
        self.crear_botones_categoria()
        self.crear_botones_accion()
        self.actualizar_input_posicion()
    
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
                self.seleccion_actual.get_rect_valido(self.spritesheet_original)
            ).copy()
            
            # Guardar
            ruta_destino = Path(f"assets/sprites/{self.categoria_actual.value}")
            ruta_destino.mkdir(parents=True, exist_ok=True)
            ruta_archivo = ruta_destino / f"{self.input_nombre.texto}.png"
            
            # Verificar si existe y preguntar
            if ruta_archivo.exists():
                print(f"⚠️ El archivo {ruta_archivo.name} ya existe")
                self.mostrar_mensaje(f"⚠️ Archivo existe, se reemplazará")
            
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
    
    def quitar_fondo_sprite(self):
        """Quita el fondo del sprite seleccionado haciéndolo transparente"""
        if not self.seleccion_actual:
            self.mostrar_mensaje("⚠️ No hay selección activa")
            return
        
        if not self.spritesheet_original:
            self.mostrar_mensaje("⚠️ No hay spritesheet cargado")
            return
        
        try:
            # Extraer el sprite
            sprite_rect = self.seleccion_actual.get_rect_valido(self.spritesheet_original)
            sprite_surface = self.spritesheet_original.subsurface(sprite_rect).copy()
            
            # Obtener el color de fondo (esquina superior izquierda)
            color_fondo = sprite_surface.get_at((0, 0))[:3]  # Solo RGB, sin alpha
            
            # Crear una nueva superficie con transparencia
            nueva_surface = pygame.Surface(sprite_surface.get_size(), pygame.SRCALPHA)
            nueva_surface.fill((0, 0, 0, 0))  # Totalmente transparente
            
            # Copiar píxeles que no sean del color de fondo
            ancho, alto = sprite_surface.get_size()
            pixeles_cambiados = 0
            
            for x in range(ancho):
                for y in range(alto):
                    color_pixel = sprite_surface.get_at((x, y))
                    
                    # Calcular diferencia de color con tolerancia
                    diff = abs(color_pixel[0] - color_fondo[0]) + \
                           abs(color_pixel[1] - color_fondo[1]) + \
                           abs(color_pixel[2] - color_fondo[2])
                    
                    if diff > self.tolerancia_fondo:
                        # No es color de fondo, copiar con alpha 255 (opaco)
                        nueva_surface.set_at((x, y), (color_pixel[0], color_pixel[1], color_pixel[2], 255))
                    else:
                        # Es color de fondo, dejar transparente (alpha 0)
                        pixeles_cambiados += 1
            
            # CLAVE: Recrear el spritesheet completo con soporte alpha
            nuevo_spritesheet = pygame.Surface(self.spritesheet_original.get_size(), pygame.SRCALPHA, 32)
            nuevo_spritesheet = nuevo_spritesheet.convert_alpha()
            
            # Copiar todo el spritesheet original
            nuevo_spritesheet.blit(self.spritesheet_original, (0, 0))
            
            # Reemplazar el área del sprite con la versión sin fondo
            # Limpiar área primero rellenando con transparencia
            nuevo_spritesheet.fill((0, 0, 0, 0), sprite_rect)
            # Pegar sprite sin fondo (sin special_flags para evitar problemas)
            nuevo_spritesheet.blit(nueva_surface, sprite_rect.topleft)
            
            # Actualizar el spritesheet
            self.spritesheet_original = nuevo_spritesheet
            
            porcentaje = (pixeles_cambiados / (ancho * alto)) * 100
            self.mostrar_mensaje(f"✓ Fondo eliminado ({porcentaje:.1f}% transparente)")
            print(f"✓ Fondo eliminado: {pixeles_cambiados} píxeles ({porcentaje:.1f}%)")
            print(f"  Color detectado: RGB{color_fondo}")
            print(f"  Sprite actualizado en spritesheet")
            
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {str(e)}")
            print(f"❌ Error quitando fondo: {e}")
            import traceback
            traceback.print_exc()

    
    def exportar_todos(self):
        """Exporta todas las selecciones marcadas con checkbox"""
        if not self.selecciones:
            self.mostrar_mensaje("⚠️ No hay selecciones")
            return
        
        # Filtrar solo los seleccionados con checkbox
        selecciones_a_exportar = [s for s in self.selecciones if s.seleccionado and not s.guardado]
        
        if not selecciones_a_exportar:
            self.mostrar_mensaje("⚠️ No hay sprites marcados para exportar")
            return
        
        # Verificar que todos tengan nombre
        sin_nombre = [s for s in selecciones_a_exportar if not s.nombre]
        if sin_nombre:
            self.mostrar_mensaje(f"⚠️ {len(sin_nombre)} sprites sin nombre")
            return
        
        contador = 0
        errores = 0
        
        # Exportar cada sprite con su nombre tal cual
        for sel in selecciones_a_exportar:
            try:
                sprite_surface = self.spritesheet_original.subsurface(sel.get_rect_valido(self.spritesheet_original)).copy()
                ruta_destino = Path(f"assets/sprites/{sel.categoria.value}")
                ruta_destino.mkdir(parents=True, exist_ok=True)
                ruta_archivo = ruta_destino / f"{sel.nombre}.png"
                
                pygame.image.save(sprite_surface, str(ruta_archivo))
                sel.guardado = True
                contador += 1
                print(f"✓ Guardado: {sel.nombre}.png en {sel.categoria.value}")
            except Exception as e:
                errores += 1
                print(f"❌ Error guardando {sel.nombre}: {e}")
        
        if errores > 0:
            self.mostrar_mensaje(f"✓ Exportados {contador} sprites ({errores} errores)")
        else:
            self.mostrar_mensaje(f"✓ Exportados {contador} sprites")
        print(f"✓ Total exportados: {contador} sprites")
        if errores > 0:
            print(f"⚠️ Errores: {errores}")
    
    def toggle_preview(self):
        """Activa/desactiva ventana de preview"""
        # Solo si hay selecciones marcadas
        selecciones_preview = [s for s in self.selecciones if s.seleccionado]
        if not selecciones_preview:
            self.mostrar_mensaje("⚠️ Marca sprites con checkbox para preview")
            return
        
        self.ventana_preview_activa = not self.ventana_preview_activa
        self.preview_frame_actual = 0
        self.preview_timer = 0
        
        if self.ventana_preview_activa:
            self.mostrar_mensaje("✓ Preview activado")
        else:
            self.mostrar_mensaje("✓ Preview desactivado")
    
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
                sel.seleccionado = sel_dict.get("seleccionado", True)
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
        area_sheet_ancho = self.ventana_ancho - AREA_PREVIEW_ANCHO - PANEL_CONTROL_ANCHO
        
        if not self.spritesheet:
            # Mensaje si no hay spritesheet
            texto1 = self.fuente.render("Arrastra una imagen aquí", True, COLOR_TEXTO)
            texto2 = self.fuente_pequena.render("o usa el botón 'Cargar'", True, COLOR_TEXTO_SEC)
            
            rect1 = texto1.get_rect(center=(area_sheet_ancho // 2, self.ventana_alto // 2 - 20))
            rect2 = texto2.get_rect(center=(area_sheet_ancho // 2, self.ventana_alto // 2 + 20))
            
            surface.blit(texto1, rect1)
            surface.blit(texto2, rect2)
            
            # Indicador visual de zona de drop
            if self.arrastrando_archivo:
                # Borde punteado cuando se arrastra
                rect_drop = pygame.Rect(20, 20, area_sheet_ancho - 40, self.ventana_alto - 40)
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
                rect_drop_texto = texto_drop.get_rect(center=(area_sheet_ancho // 2, self.ventana_alto // 2 + 60))
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
            area_sheet_ancho = self.ventana_ancho - AREA_PREVIEW_ANCHO - PANEL_CONTROL_ANCHO
            if mouse_x < area_sheet_ancho:
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
        panel_x = self.ventana_ancho - PANEL_CONTROL_ANCHO
        pygame.draw.rect(surface, COLOR_PANEL, 
                        (panel_x, 0, PANEL_CONTROL_ANCHO, self.ventana_alto))
        
        # Título
        x = panel_x + 20
        y = 20
        titulo = self.fuente.render("Controles", True, COLOR_TEXTO)
        surface.blit(titulo, (x, y))
        
        y += 50
        
        # Input de nombre
        self.input_nombre.draw(surface)
        
        y = 130
        
        # Texto "Categoría:"
        texto_cat = self.fuente_pequena.render("Categoría:", True, COLOR_TEXTO)
        surface.blit(texto_cat, (x, y))
        
        # Botones de categoría
        for boton in self.botones_categoria:
            boton.draw(surface)
        
        # Botones de acción
        for boton in self.botones_accion:
            boton.draw(surface)
    
    def dibujar_panel_preview(self, surface):
        """Dibuja panel de preview izquierdo"""
        # Calcular área del spritesheet según tamaño de ventana
        area_sheet_ancho = self.ventana_ancho - AREA_PREVIEW_ANCHO - PANEL_CONTROL_ANCHO
        
        # Fondo
        pygame.draw.rect(surface, COLOR_PANEL, 
                        (area_sheet_ancho, 0, AREA_PREVIEW_ANCHO, self.ventana_alto))
        
        x = area_sheet_ancho + 10
        y = 20
        
        # Título
        titulo = self.fuente.render("Preview", True, COLOR_TEXTO)
        surface.blit(titulo, (x, y))
        y += 30
        
        # Info primero (antes del preview)
        if self.seleccion_actual and self.spritesheet_original:
            info = [
                f"Tamaño: {self.seleccion_actual.ancho}x{self.seleccion_actual.alto}",
                f"Pos: ({self.seleccion_actual.x}, {self.seleccion_actual.y})",
            ]
            
            for linea in info:
                texto = self.fuente_pequena.render(linea, True, COLOR_TEXTO_SEC)
                surface.blit(texto, (x, y))
                y += 18
            
            y += 5  # Espacio antes del preview
            
            # Preview del sprite actual DEBAJO de la info
            try:
                sprite = self.spritesheet_original.subsurface(
                    self.seleccion_actual.get_rect_valido(self.spritesheet_original)
                ).copy()
                
                # Calcular espacio disponible para el preview
                espacio_disponible = (self.ventana_alto // 2) - y - 30
                max_tam = min(AREA_PREVIEW_ANCHO - 20, espacio_disponible)
                
                # Escalar para que quepa en el panel
                factor = min(max_tam / sprite.get_width(), max_tam / sprite.get_height(), 3.0)
                if factor < 1 or factor > 1:
                    nuevo_ancho = int(sprite.get_width() * factor)
                    nuevo_alto = int(sprite.get_height() * factor)
                    if nuevo_ancho > 0 and nuevo_alto > 0:
                        sprite = pygame.transform.scale(sprite, (nuevo_ancho, nuevo_alto))
                
                # Fondo de cuadrícula para transparencias
                for i in range(0, sprite.get_width(), 8):
                    for j in range(0, sprite.get_height(), 8):
                        color = (40, 40, 50) if (i // 8 + j // 8) % 2 == 0 else (50, 50, 60)
                        pygame.draw.rect(surface, color, (x + i, y + j, 8, 8))
                
                # Dibujar sprite
                surface.blit(sprite, (x, y))
                y += sprite.get_height() + 10
            
            except Exception as e:
                texto = self.fuente_pequena.render("Error en preview", True, (255, 100, 100))
                surface.blit(texto, (x, y))
                y += 20
        else:
            texto = self.fuente_pequena.render("Selecciona un área", True, COLOR_TEXTO_SEC)
            surface.blit(texto, (x, y))
            y += 20
        
        # Lista de selecciones con checkboxes y SCROLL
        # Ajustar posición si hay preview de animación activo
        if self.ventana_preview_activa:
            y_lista_inicio = y + 10  # Justo después del preview del sprite actual
            lista_alto = (self.ventana_alto - y_lista_inicio - 250)  # Dejar espacio para animación abajo
        else:
            y_lista_inicio = self.ventana_alto // 2
            lista_alto = self.ventana_alto - y_lista_inicio - 50  # Sin preview de animación
        
        titulo_lista = self.fuente_pequena.render(f"Sprites: {len(self.selecciones)}", True, COLOR_TEXTO)
        surface.blit(titulo_lista, (x, y_lista_inicio))
        y_lista_inicio += 25
        
        # Área de la lista (con scroll)
        lista_ancho = AREA_PREVIEW_ANCHO - 20
        
        # Crear superficie para la lista con clip
        clip_rect = pygame.Rect(x, y_lista_inicio, lista_ancho, lista_alto)
        
        # Guardar posiciones de checkboxes para detección de clicks
        self.checkbox_rects = []
        
        y = y_lista_inicio - self.scroll_lista_offset
        altura_total = 0
        
        for i, sel in enumerate(self.selecciones):
            # Solo dibujar si está visible
            if y + 25 >= y_lista_inicio and y < y_lista_inicio + lista_alto:
                nombre = sel.nombre if sel.nombre else f"Sprite {i+1}"
                
                # Dibujar checkbox
                checkbox_rect = pygame.Rect(x, y, 18, 18)
                self.checkbox_rects.append((checkbox_rect, sel))
                
                # Fondo del checkbox
                pygame.draw.rect(surface, (60, 60, 80), checkbox_rect, border_radius=3)
                pygame.draw.rect(surface, COLOR_TEXTO, checkbox_rect, 2, border_radius=3)
                
                # Marca si está seleccionado
                if sel.seleccionado:
                    pygame.draw.line(surface, (100, 255, 100), 
                                   (x + 3, y + 9), (x + 7, y + 14), 3)
                    pygame.draw.line(surface, (100, 255, 100), 
                                   (x + 7, y + 14), (x + 15, y + 4), 3)
                
                # Indicador de guardado
                guardado_icon = "✓" if sel.guardado else "○"
                color_texto = (0, 255, 0) if sel.guardado else COLOR_TEXTO_SEC
                
                # Resaltar si es el sprite actual
                if sel == self.seleccion_actual:
                    pygame.draw.rect(surface, (70, 70, 100), (x - 5, y - 2, lista_ancho, 22), border_radius=3)
                
                texto = self.fuente_pequena.render(f"{guardado_icon} {nombre}", True, color_texto)
                surface.blit(texto, (x + 25, y))
            
            y += 25
            altura_total += 25
        
        # Actualizar scroll máximo
        self.scroll_lista_max = max(0, altura_total - lista_alto)
        
        # Dibujar scrollbar si es necesario
        if self.scroll_lista_max > 0:
            scrollbar_x = x + lista_ancho + 5
            scrollbar_alto = lista_alto
            scrollbar_ancho = 8
            
            # Barra de fondo
            pygame.draw.rect(surface, (50, 50, 70), 
                           (scrollbar_x, y_lista_inicio, scrollbar_ancho, scrollbar_alto), border_radius=4)
            
            # Thumb de scroll
            thumb_alto = max(20, scrollbar_alto * (lista_alto / altura_total))
            thumb_y = y_lista_inicio + (self.scroll_lista_offset / self.scroll_lista_max) * (scrollbar_alto - thumb_alto) if self.scroll_lista_max > 0 else y_lista_inicio
            pygame.draw.rect(surface, (100, 100, 200), 
                           (scrollbar_x, thumb_y, scrollbar_ancho, thumb_alto), border_radius=4)
        
        y = y_lista_inicio + lista_alto
        
        # Si el preview está activo, mostrarlo más abajo (después de la lista)
        if self.ventana_preview_activa:
            self.dibujar_preview_animacion(surface, area_sheet_ancho, y + 10)
    
    def dibujar_barra_estado(self, surface):
        """Dibuja barra de estado inferior"""
        barra_alto = 25
        pygame.draw.rect(surface, (20, 20, 30), (0, self.ventana_alto - barra_alto, self.ventana_ancho, barra_alto))
        
        # Info
        texto_info = f"Zoom: {self.zoom:.1f}x | Sprites: {len(self.selecciones)} | "
        texto_info += f"Marcados: {sum(1 for s in self.selecciones if s.seleccionado)}"
        
        if self.spritesheet_original:
            texto_info += f" | Sheet: {self.spritesheet_original.get_width()}x{self.spritesheet_original.get_height()}"
        
        texto = self.fuente_pequena.render(texto_info, True, COLOR_TEXTO)
        surface.blit(texto, (10, self.ventana_alto - barra_alto + 5))
        
        # Mensaje temporal
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_timer < 3000:
            mensaje_surf = self.fuente.render(self.mensaje, True, (100, 255, 100))
            pos_x = self.ventana_ancho // 2 - mensaje_surf.get_width() // 2
            surface.blit(mensaje_surf, (pos_x, self.ventana_alto - barra_alto - 30))
    
    def dibujar_preview_animacion(self, surface, x_base, y_inicio):
        """Dibuja la ventana de preview de animación"""
        # Obtener sprites seleccionados con checkbox
        sprites_animacion = [s for s in self.selecciones if s.seleccionado]
        
        if not sprites_animacion or not self.spritesheet_original:
            return
        
        # Calcular posición y tamaño
        x_panel = x_base + 10
        ancho_preview = AREA_PREVIEW_ANCHO - 20
        alto_preview = min(220, self.ventana_alto - y_inicio - 30)  # Ajustar al espacio disponible
        
        # Fondo del preview
        rect_preview = pygame.Rect(x_panel, y_inicio, ancho_preview, alto_preview)
        pygame.draw.rect(surface, (40, 40, 60), rect_preview, border_radius=5)
        pygame.draw.rect(surface, COLOR_BOTON_ACTIVO, rect_preview, 2, border_radius=5)
        
        # Título
        titulo = self.fuente.render("Animación", True, COLOR_TEXTO)
        surface.blit(titulo, (x_panel + 10, y_inicio + 10))
        
        # Actualizar frame de animación
        self.preview_timer += 1
        if self.preview_timer >= self.preview_velocidad:
            self.preview_timer = 0
            self.preview_frame_actual = (self.preview_frame_actual + 1) % len(sprites_animacion)
        
        # Dibujar sprite actual de la animación
        sprite_actual = sprites_animacion[self.preview_frame_actual]
        try:
            sprite_surface = self.spritesheet_original.subsurface(sprite_actual.get_rect_valido(self.spritesheet_original)).copy()
            
            # Escalar para que quepa - usar más espacio vertical
            max_ancho = ancho_preview - 20
            max_alto = alto_preview - 70
            escala = min(max_ancho / sprite_surface.get_width(),
                        max_alto / sprite_surface.get_height(), 4.0)
            
            nuevo_ancho = int(sprite_surface.get_width() * escala)
            nuevo_alto = int(sprite_surface.get_height() * escala)
            
            if nuevo_ancho > 0 and nuevo_alto > 0:
                sprite_escalado = pygame.transform.scale(sprite_surface, (nuevo_ancho, nuevo_alto))
                
                # Centrar en el área de preview
                x_sprite = x_panel + (ancho_preview - nuevo_ancho) // 2
                y_sprite = y_inicio + 40 + (alto_preview - 70 - nuevo_alto) // 2
                
                # Fondo de cuadrícula para ver transparencias
                for i in range(0, nuevo_ancho, 10):
                    for j in range(0, nuevo_alto, 10):
                        color = (50, 50, 60) if (i // 10 + j // 10) % 2 == 0 else (60, 60, 70)
                        pygame.draw.rect(surface, color, (x_sprite + i, y_sprite + j, 10, 10))
                
                surface.blit(sprite_escalado, (x_sprite, y_sprite))
        
        except Exception as e:
            texto_error = self.fuente_pequena.render(f"Error: {str(e)}", True, (255, 100, 100))
            surface.blit(texto_error, (x_panel + 10, y_inicio + 50))
        
        # Info de frame actual - en la parte inferior
        info = f"Frame {self.preview_frame_actual + 1}/{len(sprites_animacion)}"
        texto_info = self.fuente_pequena.render(info, True, COLOR_TEXTO_SEC)
        surface.blit(texto_info, (x_panel + 10, y_inicio + alto_preview - 20))
    
    def manejar_eventos(self):
        """Maneja eventos"""
        mouse_pos = pygame.mouse.get_pos()
        click = False
        eventos_texto = []
        area_sheet_ancho = self.ventana_ancho - AREA_PREVIEW_ANCHO - PANEL_CONTROL_ANCHO
        
        for evento in pygame.event.get():
            eventos_texto.append(evento)
            
            if evento.type == pygame.QUIT:
                return False
            
            # Redimensionamiento de ventana
            elif evento.type == pygame.VIDEORESIZE:
                self.ventana_ancho = evento.w
                self.ventana_alto = evento.h
                self.pantalla = pygame.display.set_mode((self.ventana_ancho, self.ventana_alto), pygame.RESIZABLE)
                # Recrear botones para nuevas posiciones
                self.botones_categoria = []
                self.botones_accion = []
                self.crear_botones_categoria()
                self.crear_botones_accion()
                self.actualizar_input_posicion()
            
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
                
                elif evento.key == pygame.K_f:
                    self.toggle_fullscreen()
                
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
                    
                    # Verificar click en checkboxes del panel preview
                    checkbox_clickeado = False
                    for checkbox_rect, sel in self.checkbox_rects:
                        if checkbox_rect.collidepoint(mouse_pos):
                            sel.seleccionado = not sel.seleccionado
                            self.seleccion_actual = sel  # Seleccionar este sprite
                            self.input_nombre.texto = sel.nombre
                            self.mostrar_mensaje(f"✓ {'Marcado' if sel.seleccionado else 'Desmarcado'}: {sel.nombre or 'Sprite'}")
                            checkbox_clickeado = True
                            break
                    
                    # Si no se clickeó un checkbox, continuar con lógica normal
                    if not checkbox_clickeado:
                        # Área del spritesheet
                        if mouse_pos[0] < area_sheet_ancho and self.spritesheet:
                            # Verificar si se clickeó una selección existente o su borde
                            x_sheet, y_sheet = self.convertir_coords_pantalla_a_sheet(
                                mouse_pos[0], mouse_pos[1]
                            )
                            
                            # Primero verificar bordes para redimensionamiento
                            borde_encontrado = False
                            for sel in reversed(self.selecciones):
                                borde = sel.get_borde_cercano(mouse_pos[0], mouse_pos[1], self.offset_x, self.offset_y, self.zoom)
                                if borde:
                                    self.redimensionando = True
                                    self.seleccion_actual = sel
                                    self.borde_seleccionado = borde
                                    self.punto_resize_inicio = (x_sheet, y_sheet)
                                    self.input_nombre.texto = sel.nombre
                                    borde_encontrado = True
                                    break
                            
                            if not borde_encontrado:
                                # Verificar click dentro de una selección
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
                
                elif evento.button == 3:  # Click derecho
                    # Verificar si está sobre una selección en el canvas para eliminarla
                    if mouse_pos[0] < area_sheet_ancho and self.spritesheet:
                        x_sheet, y_sheet = self.convertir_coords_pantalla_a_sheet(
                            mouse_pos[0], mouse_pos[1]
                        )
                        
                        seleccion_a_eliminar = None
                        for sel in reversed(self.selecciones):
                            if sel.contiene_punto(x_sheet, y_sheet):
                                seleccion_a_eliminar = sel
                                break
                        
                        if seleccion_a_eliminar:
                            # Eliminar la selección
                            self.selecciones.remove(seleccion_a_eliminar)
                            if self.seleccion_actual == seleccion_a_eliminar:
                                self.seleccion_actual = None
                                self.input_nombre.texto = ""
                            self.mostrar_mensaje("✓ Selección eliminada")
                        else:
                            # Si no hay selección, iniciar pan
                            self.panning = True
                            self.pan_inicio = mouse_pos
                    else:
                        # Pan en otras áreas
                        if self.spritesheet:
                            self.panning = True
                            self.pan_inicio = mouse_pos
                
                elif evento.button == 4:  # Scroll up
                    # Scroll en lista del panel preview si el mouse está ahí
                    if mouse_pos[0] >= area_sheet_ancho:
                        self.scroll_lista_offset = max(0, self.scroll_lista_offset - 25)
                    # Zoom en spritesheet si está ahí
                    elif mouse_pos[0] < area_sheet_ancho:
                        old_zoom = self.zoom
                        self.zoom = min(5.0, self.zoom * 1.1)
                        # Ajustar offset para zoom hacia el cursor
                        zoom_factor = self.zoom / old_zoom
                        self.offset_x = mouse_pos[0] - (mouse_pos[0] - self.offset_x) * zoom_factor
                        self.offset_y = mouse_pos[1] - (mouse_pos[1] - self.offset_y) * zoom_factor
                
                elif evento.button == 5:  # Scroll down
                    # Scroll en lista del panel preview si el mouse está ahí
                    if mouse_pos[0] >= area_sheet_ancho:
                        self.scroll_lista_offset = min(self.scroll_lista_max, self.scroll_lista_offset + 25)
                    # Zoom out en spritesheet si está ahí
                    elif mouse_pos[0] < area_sheet_ancho:
                        old_zoom = self.zoom
                        self.zoom = max(0.1, self.zoom / 1.1)
                        # Ajustar offset para zoom hacia el cursor
                        zoom_factor = self.zoom / old_zoom
                        self.offset_x = mouse_pos[0] - (mouse_pos[0] - self.offset_x) * zoom_factor
                        self.offset_y = mouse_pos[1] - (mouse_pos[1] - self.offset_y) * zoom_factor
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    if self.seleccionando:
                        # Finalizar selección
                        self.seleccionando = False
                        x1, y1 = self.punto_inicio
                        x2, y2 = mouse_pos
                        
                        if mouse_pos[0] < area_sheet_ancho:
                            # Convertir a coordenadas del sheet
                            x1_sheet, y1_sheet = self.convertir_coords_pantalla_a_sheet(x1, y1)
                            x2_sheet, y2_sheet = self.convertir_coords_pantalla_a_sheet(x2, y2)
                            
                            # Asegurar que x1,y1 sea la esquina superior izquierda
                            x_min = min(x1_sheet, x2_sheet)
                            y_min = min(y1_sheet, y2_sheet)
                            ancho = abs(x2_sheet - x1_sheet)
                            alto = abs(y2_sheet - y1_sheet)
                            
                            if ancho > 5 and alto > 5:  # Mínimo 5x5
                                # Validar que la selección esté dentro del spritesheet
                                max_x = self.spritesheet_original.get_width()
                                max_y = self.spritesheet_original.get_height()
                                
                                # Ajustar si se sale de los límites
                                if x_min < 0:
                                    x_min = 0
                                if y_min < 0:
                                    y_min = 0
                                if x_min + ancho > max_x:
                                    ancho = max_x - x_min
                                if y_min + alto > max_y:
                                    alto = max_y - y_min
                                
                                # Solo crear si sigue siendo válida
                                if ancho > 5 and alto > 5 and x_min >= 0 and y_min >= 0:
                                    seleccion = SeleccionSprite(
                                        x=x_min, y=y_min, ancho=ancho, alto=alto,
                                        categoria=self.categoria_actual
                                    )
                                    self.selecciones.append(seleccion)
                                    self.seleccion_actual = seleccion
                                    self.mostrar_mensaje(f"✓ Área seleccionada: {ancho}x{alto}")
                                else:
                                    self.mostrar_mensaje("⚠️ Selección fuera de límites")
                    
                    elif self.redimensionando:
                        # Finalizar redimensionamiento
                        self.redimensionando = False
                        self.borde_seleccionado = None
                        self.mostrar_mensaje(f"✓ Redimensionado a {self.seleccion_actual.ancho}x{self.seleccion_actual.alto}")
                
                elif evento.button == 3:  # Soltar botón derecho - Finalizar pan
                    self.panning = False
            
            elif evento.type == pygame.MOUSEMOTION:
                # Redimensionamiento si está activo
                if self.redimensionando and self.seleccion_actual and self.spritesheet_original:
                    x_sheet, y_sheet = self.convertir_coords_pantalla_a_sheet(mouse_pos[0], mouse_pos[1])
                    sel = self.seleccion_actual
                    borde = self.borde_seleccionado
                    
                    # Límites del spritesheet
                    max_x = self.spritesheet_original.get_width()
                    max_y = self.spritesheet_original.get_height()
                    
                    # Guardar posiciones originales
                    x_orig = sel.x
                    y_orig = sel.y
                    ancho_orig = sel.ancho
                    alto_orig = sel.alto
                    
                    # Aplicar cambios según el borde
                    if 'top' in borde or borde == 'tl' or borde == 'tr':
                        diff_y = y_sheet - y_orig
                        sel.y = max(0, y_sheet)
                        sel.alto = alto_orig - diff_y
                    
                    if 'bottom' in borde or borde == 'bl' or borde == 'br':
                        sel.alto = min(y_sheet - y_orig, max_y - y_orig)
                    
                    if 'left' in borde or borde == 'tl' or borde == 'bl':
                        diff_x = x_sheet - x_orig
                        sel.x = max(0, x_sheet)
                        sel.ancho = ancho_orig - diff_x
                    
                    if 'right' in borde or borde == 'tr' or borde == 'br':
                        sel.ancho = min(x_sheet - x_orig, max_x - x_orig)
                    
                    # Validar tamaños mínimos
                    if sel.ancho < 5:
                        sel.ancho = 5
                        if 'left' in borde or borde == 'tl' or borde == 'bl':
                            sel.x = x_orig + ancho_orig - 5
                    
                    if sel.alto < 5:
                        sel.alto = 5
                        if 'top' in borde or borde == 'tl' or borde == 'tr':
                            sel.y = y_orig + alto_orig - 5
                    
                    # Validar límites máximos
                    if sel.x + sel.ancho > max_x:
                        sel.ancho = max_x - sel.x
                    if sel.y + sel.alto > max_y:
                        sel.alto = max_y - sel.y
                
                # Pan de cámara si está activo
                elif self.panning:
                    dx = mouse_pos[0] - self.pan_inicio[0]
                    dy = mouse_pos[1] - self.pan_inicio[1]
                    self.offset_x += dx
                    self.offset_y += dy
                    self.pan_inicio = mouse_pos
        
        # Actualizar UI
        self.input_nombre.update(eventos_texto, mouse_pos, click)
        
        for boton in self.botones_categoria + self.botones_accion:
            boton.update(mouse_pos, click)
        
        # Actualizar cursor según contexto
        if mouse_pos[0] < area_sheet_ancho and self.spritesheet and not self.panning and not self.seleccionando:
            cursor_cambiado = False
            for sel in reversed(self.selecciones):
                borde = sel.get_borde_cercano(mouse_pos[0], mouse_pos[1], self.offset_x, self.offset_y, self.zoom)
                if borde:
                    # Cambiar cursor según el borde
                    if borde in ['tl', 'br']:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
                    elif borde in ['tr', 'bl']:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
                    elif borde in ['top', 'bottom']:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
                    elif borde in ['left', 'right']:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                    cursor_cambiado = True
                    break
            
            if not cursor_cambiado:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        return True
    
    def ejecutar(self):
        """Bucle principal"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Actualizar tamaños si la ventana cambió
            nuevo_ancho = self.pantalla.get_width()
            nuevo_alto = self.pantalla.get_height()
            if nuevo_ancho != self.ventana_ancho or nuevo_alto != self.ventana_alto:
                self.ventana_ancho = nuevo_ancho
                self.ventana_alto = nuevo_alto
                # Recrear botones
                self.botones_categoria = []
                self.botones_accion = []
                self.crear_botones_categoria()
                self.crear_botones_accion()
                self.actualizar_input_posicion()
            
            area_sheet_ancho = self.ventana_ancho - AREA_PREVIEW_ANCHO - PANEL_CONTROL_ANCHO
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área del spritesheet
            area_sheet = self.pantalla.subsurface((0, 0, area_sheet_ancho, self.ventana_alto))
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
║  • Arrastra imagen = Cargar                          ║
║  • Click + Arrastrar = Seleccionar área              ║
║  • Arrastrar bordes = Redimensionar                  ║
║  • Click derecho = Eliminar selección / Pan          ║
║  • Scroll (canvas) = Zoom                            ║
║  • Scroll (lista) = Desplazar                        ║
║  • Botón "Quitar Fondo" = Eliminar fondo sprite      ║
║  • S = Guardar sprite                                ║
║  • E = Exportar todos                                ║
║  • F = Pantalla completa                             ║
║  • G = Toggle grid                                   ║
║  • DEL = Eliminar selección                          ║
║  • CTRL+Z = Deshacer                                 ║
║  • CTRL+Y = Rehacer                                  ║
║  • ESC = Salir                                       ║
╚══════════════════════════════════════════════════════╝
    """)
    
    editor = SpriteSheetEditor()
    editor.ejecutar()
