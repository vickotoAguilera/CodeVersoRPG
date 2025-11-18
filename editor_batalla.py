"""
========================================
EDITOR DE BATALLA - CodeVerso RPG
========================================
Editor especializado para configurar escenas de batalla:
✓ Fondo de batalla (pelea_pradera.png)
✓ Secciones desplegables (Héroes/Monstruos)
✓ Drag & Drop de sprites
✓ Escalado con mouse
✓ Detección automática de nuevos sprites
✓ Guardado/Carga de configuración
"""

import pygame
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ========================================
# CONFIGURACIÓN
# ========================================
ANCHO = 1600
ALTO = 900
FPS = 60
PANEL_ANCHO = 300
AREA_BATALLA_ANCHO = ANCHO - PANEL_ANCHO

# Colores
COLOR_FONDO = (15, 15, 20)
COLOR_PANEL = (25, 25, 35)
COLOR_BOTON = (50, 50, 70)
COLOR_BOTON_HOVER = (70, 70, 100)
COLOR_BOTON_ACTIVO = (90, 140, 255)
COLOR_SELECCION = (255, 215, 0)
COLOR_HOVER = (100, 200, 255)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SEC = (180, 180, 180)
COLOR_TEXTO_SEL = (255, 255, 0)
COLOR_HANDLE = (255, 100, 100)

# Colores por defecto de textos flotantes
COLOR_DANIO_NORMAL = (255, 255, 255)
COLOR_DANIO_CRITICO = (255, 50, 50)
COLOR_CURACION = (50, 255, 50)
COLOR_MISS = (150, 150, 150)

# ========================================
# CLASES AUXILIARES
# ========================================

@dataclass
class SpriteInfo:
    """Información de un sprite disponible"""
    nombre: str
    ruta: str
    tipo: str  # "heroe" o "monstruo"
    ancho_default: int = 96
    alto_default: int = 96

@dataclass
class SpriteColocado:
    """Sprite colocado en el área de batalla"""
    sprite_ref: str  # Referencia al sprite original
    tipo: str
    x: float
    y: float
    ancho: int
    alto: int
    slot_numero: int = 0  # Número de slot asignado (1-4 para héroes, 1-6 para monstruos)
    imagen: pygame.Surface = None
    
    def __post_init__(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        self.offset_y = 0
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=10):
        """Retorna qué handle (esquina) está en el punto"""
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
            "sprite_ref": self.sprite_ref,
            "tipo": self.tipo,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "slot_numero": self.slot_numero
        }

@dataclass
class TextoFlotanteDemo:
    """Texto flotante de demostración"""
    texto: str
    x: float
    y: float
    color: Tuple[int, int, int]
    tamano: int = 24
    tipo: str = "normal"  # normal, critico, curacion, miss
    
    def __post_init__(self):
        self.rect = pygame.Rect(int(self.x) - 30, int(self.y) - 15, 60, 30)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x) - 30, int(self.y) - 15, 60, 30)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=8):
        """Retorna qué handle está en el punto"""
        handles = {
            'nw': (self.rect.x, self.rect.y),
            'ne': (self.rect.x + self.rect.width, self.rect.y),
            'sw': (self.rect.x, self.rect.y + self.rect.height),
            'se': (self.rect.x + self.rect.width, self.rect.y + self.rect.height)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam and abs(py - hy) <= tam:
                return nombre
        return None
    
    def to_dict(self):
        return {
            "texto": self.texto,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "tamano": self.tamano,
            "tipo": self.tipo
        }

class VentanaBatalla:
    """Ventana de comandos inferior redimensionable"""
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        self.comandos = ["Ataque", "Magia", "Habilidades", "Items", "Huir"]
        self.seleccionado = 0
    
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
    
    def get_tamano_texto_escalado(self):
        """Calcula el tamaño del texto basado en el tamaño de la ventana"""
        factor = min(self.ancho / 600, self.alto / 120)  # Tamaño base
        return max(12, int(32 * factor))
    
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto
        }

class VentanaMagia:
    """Ventana de magias/habilidades redimensionable"""
    def __init__(self):
        self.x = 100
        self.y = 100
        self.ancho = 400
        self.alto = 300
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        self.visible = False
        
        # Magias de ejemplo
        self.magias = [
            {"nombre": "Fuego", "mp": 10},
            {"nombre": "Rayo", "mp": 15},
            {"nombre": "Curar", "mp": 8},
            {"nombre": "Hielo", "mp": 12},
            {"nombre": "Veneno", "mp": 6}
        ]
        self.seleccionado = 0
    
    def get_tamano_texto_escalado(self):
        """Calcula el tamaño del texto basado en el tamaño de la ventana"""
        factor = min(self.ancho / 400, self.alto / 300)
        return max(10, int(20 * factor))
    
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

class VentanaEmuladorBatalla:
    """Ventana que emula la vista completa de batalla"""
    def __init__(self):
        self.x = 700
        self.y = 100
        self.ancho = 500
        self.alto = 400
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        self.visible = False
    
    def get_tamano_texto_escalado(self, base=20):
        """Calcula el tamaño del texto basado en el tamaño de la ventana"""
        factor = min(self.ancho / 500, self.alto / 400)  # Tamaño base
        return max(10, int(base * factor))
    
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

class SeccionDesplegable:
    """Sección expandible/colapsable"""
    def __init__(self, x, y, ancho, titulo, color_titulo=(60, 100, 150)):
        self.rect_titulo = pygame.Rect(x, y, ancho, 40)
        self.titulo = titulo
        self.expandida = False
        self.color_titulo = color_titulo
        self.items: List[SpriteInfo] = []
        self.scroll_y = 0  # Mantenemos por compatibilidad pero no se usa
        self.fuente = pygame.font.Font(None, 22)
        self.fuente_item = pygame.font.Font(None, 18)
    
    def toggle(self):
        """Expande o colapsa la sección"""
        self.expandida = not self.expandida
    
    def get_alto_total(self):
        """Retorna el alto total incluyendo items si está expandida"""
        if not self.expandida:
            return self.rect_titulo.height
        return self.rect_titulo.height + len(self.items) * 35 + 10
    
    def click_en_titulo(self, mouse_pos):
        """Verifica si se hizo click en el título"""
        return self.rect_titulo.collidepoint(mouse_pos)
    
    def get_item_en_posicion(self, mouse_pos, scroll_offset=0, items_visibles=999):
        """Retorna el item clickeado (si hay) - con soporte para scroll"""
        if not self.expandida:
            return None
        
        x, y = mouse_pos
        if not (self.rect_titulo.x <= x <= self.rect_titulo.x + self.rect_titulo.width):
            return None
        
        y_item_inicio = self.rect_titulo.y + self.rect_titulo.height + 5
        
        # Calcular items visibles basado en scroll
        items_fin = min(scroll_offset + items_visibles, len(self.items))
        items_visibles_lista = self.items[scroll_offset:items_fin]
        
        for idx_visual, item in enumerate(items_visibles_lista):
            rect_item = pygame.Rect(
                self.rect_titulo.x + 10,
                y_item_inicio + idx_visual * 35,
                self.rect_titulo.width - 20,
                30
            )
            if rect_item.collidepoint(mouse_pos):
                return item
        return None
    
    def dibujar(self, surface, scroll_offset=0, items_visibles_max=999):
        """Dibuja la sección con soporte para scroll"""
        # Título
        color = COLOR_BOTON_ACTIVO if self.expandida else self.color_titulo
        pygame.draw.rect(surface, color, self.rect_titulo, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, self.rect_titulo, 2, border_radius=5)
        
        # Flecha indicadora
        flecha = "▼" if self.expandida else "▶"
        texto_flecha = self.fuente.render(flecha, True, COLOR_TEXTO)
        surface.blit(texto_flecha, (self.rect_titulo.x + 10, self.rect_titulo.y + 10))
        
        # Título
        texto = self.fuente.render(self.titulo, True, COLOR_TEXTO)
        surface.blit(texto, (self.rect_titulo.x + 40, self.rect_titulo.y + 10))
        
        # Contador de items
        contador = self.fuente_item.render(f"({len(self.items)})", True, COLOR_TEXTO_SEC)
        surface.blit(contador, (self.rect_titulo.x + self.rect_titulo.width - 50, self.rect_titulo.y + 12))
        
        # Items (si está expandida) - con scroll
        if self.expandida and len(self.items) > 0:
            y_item = self.rect_titulo.y + self.rect_titulo.height + 5
            
            # Calcular items visibles basado en scroll
            items_fin = min(scroll_offset + items_visibles_max, len(self.items))
            items_visibles = self.items[scroll_offset:items_fin]
            
            for idx_visual, item in enumerate(items_visibles):
                y_pos = y_item + idx_visual * 35
                
                rect_item = pygame.Rect(
                    self.rect_titulo.x + 10,
                    y_pos,
                    self.rect_titulo.width - 20,
                    30
                )
                
                # Hover
                mouse_pos = pygame.mouse.get_pos()
                color = COLOR_BOTON_HOVER if rect_item.collidepoint(mouse_pos) else COLOR_BOTON
                pygame.draw.rect(surface, color, rect_item, border_radius=3)
                
                # Nombre del sprite
                nombre_corto = item.nombre[:28] if len(item.nombre) > 28 else item.nombre
                texto_item = self.fuente_item.render(nombre_corto, True, COLOR_TEXTO)
                surface.blit(texto_item, (rect_item.x + 5, rect_item.y + 8))
                
                # Icono de arrastre
                icono = self.fuente_item.render("⋮⋮", True, COLOR_TEXTO_SEC)
                surface.blit(icono, (rect_item.x + rect_item.width - 25, rect_item.y + 8))
            
            # Dibujar scrollbar si es necesario
            if len(self.items) > items_visibles_max:
                scrollbar_x = self.rect_titulo.x + self.rect_titulo.width - 8
                scrollbar_y = y_item
                scrollbar_ancho = 6
                scrollbar_altura = items_visibles_max * 35
                
                # Barra de fondo
                pygame.draw.rect(surface, (50, 50, 100),
                               (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura),
                               border_radius=3)
                
                # Calcular tamaño y posición del thumb
                thumb_altura = max(15, int((items_visibles_max / len(self.items)) * scrollbar_altura))
                thumb_pos_max = scrollbar_altura - thumb_altura
                scroll_ratio = scroll_offset / (len(self.items) - items_visibles_max)
                thumb_y = scrollbar_y + int(scroll_ratio * thumb_pos_max)
                
                # Dibujar thumb
                pygame.draw.rect(surface, (100, 100, 255),
                               (scrollbar_x, thumb_y, scrollbar_ancho, thumb_altura),
                               border_radius=3)

# ========================================
# EDITOR PRINCIPAL
# ========================================

class EditorBatalla:
    """Editor especializado para configurar batallas"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Batalla - CodeVerso RPG")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        # Sistema de slots numerados
        self.cantidad_heroes_seleccionada = 1  # Cantidad de héroes permitida (1-4)
        self.cantidad_monstruos_seleccionada = 1  # Cantidad de monstruos permitida (1-6)
        self.max_heroes = 4
        self.max_monstruos = 6
        
        # Ventana de batalla inferior
        ventana_alto = 120
        ventana_padding = 20
        self.ventana_batalla = VentanaBatalla(
            PANEL_ANCHO + ventana_padding,
            ALTO - ventana_alto - ventana_padding,
            AREA_BATALLA_ANCHO - (ventana_padding * 2),
            ventana_alto
        )
        
        # Ventanas adicionales
        self.ventana_magia = VentanaMagia()
        self.ventana_emulador = VentanaEmuladorBatalla()
        self.mostrar_ventana_magia = False
        self.mostrar_ventana_emulador = False
        
        # Textos flotantes de demostración
        self.textos_flotantes_demo: List[TextoFlotanteDemo] = []
        self.mostrar_textos_flotantes = False
        self.texto_seleccionado: Optional[TextoFlotanteDemo] = None
        
        # Paleta de colores
        self.mostrar_paleta = False
        self.tipo_color_editando = None  # "normal", "critico", "curacion", "miss"
        self.colores_config = {
            "normal": list(COLOR_DANIO_NORMAL),
            "critico": list(COLOR_DANIO_CRITICO),
            "curacion": list(COLOR_CURACION),
            "miss": list(COLOR_MISS)
        }
        
        # Fondo de batalla
        self.fondo_batalla = None
        self.cargar_fondo()
        
        # Sprites colocados en el área de batalla
        self.sprites_colocados: List[SpriteColocado] = []
        self.sprite_seleccionado: Optional[SpriteColocado] = None
        self.sprite_hover: Optional[SpriteColocado] = None
        
        # Sistema de drag & drop
        self.sprite_siendo_arrastrado: Optional[SpriteInfo] = None
        self.texto_siendo_arrastrado: Optional[str] = None  # tipo de texto: "normal", "critico", etc
        self.arrastrando_desde_panel = False
        self.offset_drag_x = 0
        self.offset_drag_y = 0
        
        # Cache de imágenes
        self.imagenes_cache = {}
        
        # Secciones desplegables
        self.seccion_heroes = SeccionDesplegable(10, 60, PANEL_ANCHO - 20, "Héroes", (50, 150, 50))
        self.seccion_monstruos = SeccionDesplegable(10, 110, PANEL_ANCHO - 20, "Monstruos", (200, 50, 50))
        
        # Sistema de scroll para secciones
        self.scroll_heroes = 0  # Offset de scroll para héroes
        self.scroll_monstruos = 0  # Offset de scroll para monstruos
        self.items_visibles_max = 8  # Máximo de items visibles a la vez
        self.tiempo_ultimo_scroll = pygame.time.get_ticks()
        self.cooldown_scroll = 150  # ms entre cada scroll
        
        # Cargar sprites
        self.cargar_sprites()
        
        # Botones derecha (inicializados luego en dibujar)
        self.rect_guardar_derecha = None
        self.rect_cargar_derecha = None
        
        # Mensajes
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        print("✓ Editor de Batalla iniciado")
    
    def cargar_fondo(self):
        """Carga el fondo de batalla"""
        try:
            ruta = Path("assets/backgrounds/pelea_pradera.png")
            if ruta.exists():
                self.fondo_batalla = pygame.image.load(str(ruta)).convert()
                # Escalar al área de batalla
                self.fondo_batalla = pygame.transform.scale(self.fondo_batalla, (AREA_BATALLA_ANCHO, ALTO))
                print(f"✓ Fondo cargado: {ruta.name}")
            else:
                print(f"⚠️ No se encontró: {ruta}")
        except Exception as e:
            print(f"❌ Error cargando fondo: {e}")
    
    def cargar_sprites(self):
        """Escanea y carga todos los sprites disponibles"""
        # Limpiar listas
        self.seccion_heroes.items = []
        self.seccion_monstruos.items = []
        
        # Cargar héroes
        path_heroes = Path("assets/sprites/heroes/batalla")
        if path_heroes.exists():
            for archivo in sorted(path_heroes.glob("*.png")):
                sprite = SpriteInfo(
                    nombre=archivo.stem,
                    ruta=str(archivo).replace('\\', '/'),
                    tipo="heroe",
                    ancho_default=96,
                    alto_default=96
                )
                self.seccion_heroes.items.append(sprite)
                
                # Precargar imagen
                try:
                    img = pygame.image.load(sprite.ruta).convert_alpha()
                    self.imagenes_cache[sprite.ruta] = img
                except Exception as e:
                    print(f"⚠️ Error cargando {archivo.name}: {e}")
        
        # Cargar monstruos (buscar recursivamente)
        path_monstruos = Path("assets/sprites/monstruos")
        if path_monstruos.exists():
            for archivo in sorted(path_monstruos.rglob("*.png")):
                sprite = SpriteInfo(
                    nombre=archivo.stem,
                    ruta=str(archivo).replace('\\', '/'),
                    tipo="monstruo",
                    ancho_default=128,
                    alto_default=128
                )
                self.seccion_monstruos.items.append(sprite)
                
                # Precargar imagen
                try:
                    img = pygame.image.load(sprite.ruta).convert_alpha()
                    self.imagenes_cache[sprite.ruta] = img
                except Exception as e:
                    print(f"⚠️ Error cargando {archivo.name}: {e}")
        
        print(f"✓ Sprites cargados: {len(self.seccion_heroes.items)} héroes, {len(self.seccion_monstruos.items)} monstruos")
    
    def crear_textos_flotantes_demo(self):
        """Crea textos flotantes de demostración"""
        centro_x = PANEL_ANCHO + (AREA_BATALLA_ANCHO // 2)
        centro_y = ALTO // 2
        
        self.textos_flotantes_demo = [
            TextoFlotanteDemo("100", centro_x - 200, centro_y - 100, tuple(self.colores_config["normal"]), 24, "normal"),
            TextoFlotanteDemo("CRITICO!", centro_x + 150, centro_y - 100, tuple(self.colores_config["critico"]), 32, "critico"),
            TextoFlotanteDemo("+50", centro_x - 200, centro_y + 80, tuple(self.colores_config["curacion"]), 24, "curacion"),
            TextoFlotanteDemo("MISS", centro_x + 150, centro_y + 80, tuple(self.colores_config["miss"]), 24, "miss")
        ]
    
    def actualizar_colores_textos(self):
        """Actualiza los colores de los textos flotantes según la configuración"""
        for texto in self.textos_flotantes_demo:
            texto.color = tuple(self.colores_config[texto.tipo])
    
    def mostrar_mensaje(self, texto):
        """Muestra un mensaje temporal"""
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
        print(texto)
    
    def crear_texto_flotante_en_posicion(self, tipo_texto: str, x: int, y: int):
        """Crea un texto flotante en una posición específica"""
        textos_ejemplo = {
            "normal": ("100", 24),
            "critico": ("CRITICO!", 32),
            "curacion": ("+50", 24),
            "miss": ("MISS", 24)
        }
        
        if tipo_texto not in textos_ejemplo:
            return
        
        texto, tamano = textos_ejemplo[tipo_texto]
        color = tuple(self.colores_config[tipo_texto])
        
        nuevo_texto = TextoFlotanteDemo(
            texto=texto,
            x=x,
            y=y,
            color=color,
            tamano=tamano,
            tipo=tipo_texto
        )
        
        self.textos_flotantes_demo.append(nuevo_texto)
        self.texto_seleccionado = nuevo_texto
        self.mostrar_mensaje(f"✓ Texto {tipo_texto} añadido")
    
    def crear_sprite_en_posicion(self, sprite_info: SpriteInfo, x: int, y: int):
        """Crea un sprite en una posición específica"""
        # Verificar límites según cantidad seleccionada
        heroes_actuales = len([s for s in self.sprites_colocados if s.tipo == 'heroe'])
        monstruos_actuales = len([s for s in self.sprites_colocados if s.tipo == 'monstruo'])
        
        if sprite_info.tipo == 'heroe' and heroes_actuales >= self.cantidad_heroes_seleccionada:
            self.mostrar_mensaje(f"⚠️ Solo se permiten {self.cantidad_heroes_seleccionada} héroe(s)")
            return
        
        if sprite_info.tipo == 'monstruo' and monstruos_actuales >= self.cantidad_monstruos_seleccionada:
            self.mostrar_mensaje(f"⚠️ Solo se permiten {self.cantidad_monstruos_seleccionada} monstruo(s)")
            return
        
        # Asignar número de slot automáticamente
        if sprite_info.tipo == 'heroe':
            slot_numero = heroes_actuales + 1
        else:
            slot_numero = monstruos_actuales + 1
        
        # Centrar en el cursor
        x_centrado = x - (sprite_info.ancho_default // 2)
        y_centrado = y - (sprite_info.alto_default // 2)
        
        # Cargar imagen
        imagen = None
        if sprite_info.ruta in self.imagenes_cache:
            imagen = self.imagenes_cache[sprite_info.ruta]
        
        sprite_colocado = SpriteColocado(
            sprite_ref=sprite_info.nombre,
            tipo=sprite_info.tipo,
            x=x_centrado,
            y=y_centrado,
            ancho=sprite_info.ancho_default,
            alto=sprite_info.alto_default,
            slot_numero=slot_numero,
            imagen=imagen
        )
        
        self.sprites_colocados.append(sprite_colocado)
        self.sprite_seleccionado = sprite_colocado
        self.mostrar_mensaje(f"✓ {sprite_info.nombre} añadido [Slot {slot_numero}]")
    
    def eliminar_sprite(self, sprite: SpriteColocado):
        """Elimina un sprite del área de batalla y reorganiza los slots"""
        if sprite in self.sprites_colocados:
            self.sprites_colocados.remove(sprite)
            
            # Reorganizar números de slot para el mismo tipo
            sprites_mismo_tipo = sorted(
                [s for s in self.sprites_colocados if s.tipo == sprite.tipo],
                key=lambda s: s.slot_numero
            )
            for idx, s in enumerate(sprites_mismo_tipo, 1):
                s.slot_numero = idx
            
            self.sprite_seleccionado = None
            self.mostrar_mensaje(f"✓ Eliminado: {sprite.sprite_ref}")
    
    def duplicar_sprite(self, sprite: SpriteColocado):
        """Duplica un sprite"""
        if not sprite:
            return
        
        # Verificar límites según cantidad seleccionada
        heroes_actuales = len([s for s in self.sprites_colocados if s.tipo == 'heroe'])
        monstruos_actuales = len([s for s in self.sprites_colocados if s.tipo == 'monstruo'])
        
        if sprite.tipo == 'heroe' and heroes_actuales >= self.cantidad_heroes_seleccionada:
            self.mostrar_mensaje(f"⚠️ Solo se permiten {self.cantidad_heroes_seleccionada} héroe(s)")
            return
        
        if sprite.tipo == 'monstruo' and monstruos_actuales >= self.cantidad_monstruos_seleccionada:
            self.mostrar_mensaje(f"⚠️ Solo se permiten {self.cantidad_monstruos_seleccionada} monstruo(s)")
            return
        
        # Asignar nuevo número de slot
        if sprite.tipo == 'heroe':
            nuevo_slot = heroes_actuales + 1
        else:
            nuevo_slot = monstruos_actuales + 1
        
        nuevo = SpriteColocado(
            sprite_ref=sprite.sprite_ref,
            tipo=sprite.tipo,
            x=sprite.x + 20,
            y=sprite.y + 20,
            ancho=sprite.ancho,
            alto=sprite.alto,
            slot_numero=nuevo_slot,
            imagen=sprite.imagen
        )
        
        self.sprites_colocados.append(nuevo)
        self.sprite_seleccionado = nuevo
        self.mostrar_mensaje(f"✓ Duplicado [Slot {nuevo_slot}]")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        config = {
            "fondo": "pelea_pradera.png",
            "sprites": [s.to_dict() for s in self.sprites_colocados],
            "ventana_batalla": self.ventana_batalla.to_dict(),
            "textos_flotantes": [t.to_dict() for t in self.textos_flotantes_demo],
            "colores": self.colores_config
        }
        
        try:
            ruta = Path("src/database/batalla_config.json")
            ruta.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje(f"✓ Guardado: {len(self.sprites_colocados)} sprites")
            return True
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {e}")
            return False
    
    def cargar_configuracion(self):
        """Carga una configuración guardada"""
        try:
            ruta = Path("src/database/batalla_config.json")
            if not ruta.exists():
                self.mostrar_mensaje("⚠️ No hay configuración guardada")
                return False
            
            with open(ruta, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Limpiar sprites actuales
            self.sprites_colocados = []
            
            # Recrear sprites
            for sprite_data in config.get("sprites", []):
                # Buscar la imagen en el cache
                imagen = None
                for ruta_img, img in self.imagenes_cache.items():
                    if sprite_data["sprite_ref"] in ruta_img:
                        imagen = img
                        break
                
                sprite = SpriteColocado(
                    sprite_ref=sprite_data["sprite_ref"],
                    tipo=sprite_data["tipo"],
                    x=sprite_data["x"],
                    y=sprite_data["y"],
                    ancho=sprite_data["ancho"],
                    alto=sprite_data["alto"],
                    imagen=imagen
                )
                self.sprites_colocados.append(sprite)
            
            # Cargar ventana de batalla
            if "ventana_batalla" in config:
                v = config["ventana_batalla"]
                self.ventana_batalla.x = v["x"]
                self.ventana_batalla.y = v["y"]
                self.ventana_batalla.ancho = v["ancho"]
                self.ventana_batalla.alto = v["alto"]
                self.ventana_batalla.actualizar_rect()
            
            # Cargar textos flotantes
            if "textos_flotantes" in config:
                self.textos_flotantes_demo = []
                for t_data in config["textos_flotantes"]:
                    texto = TextoFlotanteDemo(
                        texto=t_data["texto"],
                        x=t_data["x"],
                        y=t_data["y"],
                        color=tuple(t_data["color"]),
                        tamano=t_data["tamano"],
                        tipo=t_data["tipo"]
                    )
                    self.textos_flotantes_demo.append(texto)
            
            # Cargar colores
            if "colores" in config:
                self.colores_config = config["colores"]
                self.actualizar_colores_textos()
            
            self.mostrar_mensaje(f"✓ Cargado: {len(self.sprites_colocados)} sprites")
            return True
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {e}")
            return False
    
    def get_sprite_en_posicion(self, x, y):
        """Obtiene el sprite en una posición (de atrás hacia adelante)"""
        for sprite in reversed(self.sprites_colocados):
            if sprite.contiene_punto(x, y):
                return sprite
        return None
    
    def dibujar_handles(self, surface, sprite: SpriteColocado):
        """Dibuja los handles de escalado"""
        tam = 8
        handles = [
            (sprite.x, sprite.y),  # NW
            (sprite.x + sprite.ancho, sprite.y),  # NE
            (sprite.x, sprite.y + sprite.alto),  # SW
            (sprite.x + sprite.ancho, sprite.y + sprite.alto),  # SE
        ]
        
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), tam)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam, 2)
    
    def dibujar_sprite_fantasma(self, surface, mouse_pos):
        """Dibuja sprite semitransparente durante drag"""
        if not self.sprite_siendo_arrastrado:
            return
        
        sprite = self.sprite_siendo_arrastrado
        x = mouse_pos[0] - (sprite.ancho_default // 2)
        y = mouse_pos[1] - (sprite.alto_default // 2)
        
        if sprite.ruta in self.imagenes_cache:
            img = self.imagenes_cache[sprite.ruta]
            img_escalada = pygame.transform.scale(img, (sprite.ancho_default, sprite.alto_default))
            img_fantasma = img_escalada.copy()
            img_fantasma.set_alpha(150)
            surface.blit(img_fantasma, (x, y))
        else:
            # Rectángulo placeholder
            color = (50, 255, 50) if sprite.tipo == "heroe" else (255, 50, 150)
            rect = pygame.Surface((sprite.ancho_default, sprite.alto_default))
            rect.set_alpha(150)
            rect.fill(color)
            surface.blit(rect, (x, y))
        
        # Borde
        pygame.draw.rect(surface, COLOR_TEXTO, (x, y, sprite.ancho_default, sprite.alto_default), 2)
        
        # Nombre
        texto = self.fuente_pequena.render(sprite.nombre[:20], True, COLOR_TEXTO)
        fondo = pygame.Surface((texto.get_width() + 10, texto.get_height() + 4))
        fondo.set_alpha(200)
        fondo.fill((0, 0, 0))
        surface.blit(fondo, (x + 2, y - 20))
        surface.blit(texto, (x + 5, y - 18))
    
    def dibujar_texto_fantasma(self, surface, mouse_pos):
        """Dibuja texto flotante semitransparente durante drag"""
        if not self.texto_siendo_arrastrado:
            return
        
        textos_ejemplo = {
            "normal": ("100", 24),
            "critico": ("CRITICO!", 32),
            "curacion": ("+50", 24),
            "miss": ("MISS", 24)
        }
        
        if self.texto_siendo_arrastrado not in textos_ejemplo:
            return
        
        texto_str, tamano = textos_ejemplo[self.texto_siendo_arrastrado]
        color = self.colores_config[self.texto_siendo_arrastrado]
        
        fuente_texto = pygame.font.Font(None, tamano)
        texto_surf = fuente_texto.render(texto_str, True, tuple(color))
        texto_surf.set_alpha(180)
        
        x = mouse_pos[0] - texto_surf.get_width() // 2
        y = mouse_pos[1] - texto_surf.get_height() // 2
        
        # Fondo semitransparente
        fondo = pygame.Surface((texto_surf.get_width() + 10, texto_surf.get_height() + 10))
        fondo.set_alpha(100)
        fondo.fill((50, 50, 50))
        surface.blit(fondo, (x - 5, y - 5))
        
        # Texto
        surface.blit(texto_surf, (x, y))
        
        # Borde
        pygame.draw.rect(surface, COLOR_TEXTO, (x - 5, y - 5, texto_surf.get_width() + 10, texto_surf.get_height() + 10), 2)
    
    def dibujar_area_batalla(self, surface):
        """Dibuja el área de batalla"""
        # Fondo
        if self.fondo_batalla:
            surface.blit(self.fondo_batalla, (0, 0))
        else:
            surface.fill((30, 20, 40))
        
        # Sprites colocados
        for sprite in self.sprites_colocados:
            if sprite.imagen:
                img_escalada = pygame.transform.scale(sprite.imagen, (sprite.ancho, sprite.alto))
                surface.blit(img_escalada, (int(sprite.x), int(sprite.y)))
            else:
                # Placeholder
                color = (50, 200, 50) if sprite.tipo == "heroe" else (200, 50, 200)
                pygame.draw.rect(surface, color, sprite.rect)
            
            # Borde
            if sprite == self.sprite_seleccionado:
                pygame.draw.rect(surface, COLOR_SELECCION, sprite.rect, 3)
                self.dibujar_handles(surface, sprite)
            elif sprite == self.sprite_hover:
                pygame.draw.rect(surface, COLOR_HOVER, sprite.rect, 2)
            else:
                pygame.draw.rect(surface, (255, 255, 255), sprite.rect, 1)
            
            # Número de slot en la esquina superior izquierda
            slot_text = f"#{sprite.slot_numero}"
            color_slot = (255, 255, 100) if sprite.tipo == "heroe" else (255, 100, 255)
            texto_slot = self.fuente.render(slot_text, True, color_slot)
            
            # Fondo circular para el número
            circulo_radio = 18
            circulo_centro = (int(sprite.x) + circulo_radio, int(sprite.y) + circulo_radio)
            pygame.draw.circle(surface, (0, 0, 0), circulo_centro, circulo_radio)
            pygame.draw.circle(surface, color_slot, circulo_centro, circulo_radio, 3)
            
            texto_rect = texto_slot.get_rect(center=circulo_centro)
            surface.blit(texto_slot, texto_rect)
            
            # Nombre
            texto = self.fuente_pequena.render(sprite.sprite_ref[:15], True, COLOR_TEXTO)
            fondo = pygame.Surface((texto.get_width() + 6, texto.get_height() + 2))
            fondo.set_alpha(180)
            fondo.fill((0, 0, 0))
            surface.blit(fondo, (sprite.x + 2, sprite.y + 2))
            surface.blit(texto, (sprite.x + 5, sprite.y + 3))
        
        # Ventana de batalla
        self.dibujar_ventana_batalla(surface)
        
        # Ventana de magia
        self.dibujar_ventana_magia(surface)
        
        # Ventana emulador
        self.dibujar_ventana_emulador(surface)
        
        # Textos flotantes de demostración
        if self.mostrar_textos_flotantes:
            self.dibujar_textos_flotantes(surface)
    
    def dibujar_ventana_batalla(self, surface):
        """Dibuja la ventana de comandos inferior"""
        v = self.ventana_batalla
        
        # Fondo de la ventana
        pygame.draw.rect(surface, (0, 0, 139), v.rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_TEXTO, v.rect, 3, border_radius=12)
        
        # Siempre mostrar handles para que sea claro que es redimensionable
        tam = 8
        handles = [
            (v.x, v.y),
            (v.x + v.ancho, v.y),
            (v.x, v.y + v.alto),
            (v.x + v.ancho, v.y + v.alto)
        ]
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), tam)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam, 2)
        
        # Comandos con texto escalado automáticamente
        tamano_texto_escalado = v.get_tamano_texto_escalado()
        fuente_escalada = pygame.font.Font(None, tamano_texto_escalado)
        
        espacio_entre_comandos = v.ancho // len(v.comandos)
        for i, comando in enumerate(v.comandos):
            x_texto = v.x + 40 + (i * espacio_entre_comandos)
            y_texto = v.y + v.alto // 2 - tamano_texto_escalado // 2
            
            color = COLOR_TEXTO_SEL if i == v.seleccionado else COLOR_TEXTO
            texto = fuente_escalada.render(comando, True, color)
            surface.blit(texto, (x_texto, y_texto))
    
    def dibujar_ventana_magia(self, surface):
        """Dibuja la ventana de magias/habilidades"""
        if not self.mostrar_ventana_magia:
            return
        
        v = self.ventana_magia
        
        # Fondo semitransparente
        fondo = pygame.Surface((v.ancho, v.alto))
        fondo.set_alpha(230)
        fondo.fill((25, 25, 50))
        surface.blit(fondo, (int(v.x), int(v.y)))
        
        # Borde
        pygame.draw.rect(surface, COLOR_TEXTO, v.rect, 3, border_radius=8)
        
        # Handles para redimensionar
        tam = 8
        handles = [
            (v.x, v.y),
            (v.x + v.ancho, v.y),
            (v.x, v.y + v.alto),
            (v.x + v.ancho, v.y + v.alto)
        ]
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), tam)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam, 2)
        
        # Título con texto escalado
        tamano_titulo = int(v.get_tamano_texto_escalado() * 1.3)
        fuente_titulo = pygame.font.Font(None, tamano_titulo)
        texto_titulo = fuente_titulo.render("MAGIAS", True, COLOR_TEXTO)
        surface.blit(texto_titulo, (int(v.x + 10), int(v.y + 10)))
        
        # Lista de magias con texto escalado
        tamano_texto = v.get_tamano_texto_escalado()
        fuente_magias = pygame.font.Font(None, tamano_texto)
        
        y_inicio = v.y + 40 + (tamano_titulo - 20)
        espacio_vertical = max(25, int(v.alto - 60) / len(v.magias))
        
        for i, magia in enumerate(v.magias):
            y_pos = y_inicio + i * espacio_vertical
            
            # Highlight de selección
            if i == v.seleccionado:
                rect_sel = pygame.Rect(int(v.x + 5), int(y_pos - 5), v.ancho - 10, espacio_vertical)
                pygame.draw.rect(surface, (50, 50, 100), rect_sel, border_radius=5)
            
            # Nombre y MP
            texto_magia = fuente_magias.render(f"{magia['nombre']} - MP: {magia['mp']}", True, COLOR_TEXTO)
            surface.blit(texto_magia, (int(v.x + 15), int(y_pos)))
    
    def dibujar_ventana_emulador(self, surface):
        """Dibuja la ventana de emulación completa de batalla"""
        if not self.mostrar_ventana_emulador:
            return
        
        v = self.ventana_emulador
        
        # Fondo semitransparente
        fondo = pygame.Surface((v.ancho, v.alto))
        fondo.set_alpha(200)
        fondo.fill((15, 15, 30))
        surface.blit(fondo, (int(v.x), int(v.y)))
        
        # Borde
        pygame.draw.rect(surface, COLOR_TEXTO, v.rect, 3, border_radius=8)
        
        # Handles para redimensionar
        tam = 8
        handles = [
            (v.x, v.y),
            (v.x + v.ancho, v.y),
            (v.x, v.y + v.alto),
            (v.x + v.ancho, v.y + v.alto)
        ]
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), tam)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam, 2)
        
        # Título con texto escalado
        tamano_titulo = v.get_tamano_texto_escalado(28)
        fuente_titulo = pygame.font.Font(None, tamano_titulo)
        texto_titulo = fuente_titulo.render("VISTA DE BATALLA", True, COLOR_TEXTO)
        surface.blit(texto_titulo, (int(v.x + 10), int(v.y + 5)))
        
        # Dividir en 3 secciones
        margen = 10
        
        # 1. Menú de acción (izquierda, 25%)
        ancho_menu = int(v.ancho * 0.25)
        rect_menu = pygame.Rect(int(v.x + margen), int(v.y + 35), ancho_menu - margen, v.alto - 45)
        pygame.draw.rect(surface, (30, 30, 60), rect_menu, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO_SEC, rect_menu, 2, border_radius=5)
        
        # Texto del menú escalado
        tamano_menu = v.get_tamano_texto_escalado(16)
        fuente_menu = pygame.font.Font(None, tamano_menu)
        texto_menu = fuente_menu.render("Menú", True, COLOR_TEXTO_SEC)
        surface.blit(texto_menu, (rect_menu.x + 5, rect_menu.y + 5))
        
        # 2. Zona de héroes (arriba, 20%)
        x_heroes = v.x + ancho_menu + margen
        ancho_centro = v.ancho - ancho_menu - (margen * 2)
        alto_heroes = int(v.alto * 0.20)
        
        rect_heroes = pygame.Rect(int(x_heroes), int(v.y + 35), ancho_centro, alto_heroes)
        pygame.draw.rect(surface, (50, 100, 50), rect_heroes, border_radius=5)
        pygame.draw.rect(surface, (100, 200, 100), rect_heroes, 2, border_radius=5)
        
        # Dibujar héroes colocados
        heroes_en_batalla = [s for s in self.sprites_colocados if s.tipo == "heroe" and s.slot_numero <= self.cantidad_heroes_seleccionada]
        if heroes_en_batalla:
            for heroe in heroes_en_batalla:
                # Escalar miniatura proporcionalmente
                factor_x = ancho_centro / AREA_BATALLA_ANCHO
                factor_y = alto_heroes / (ALTO * 0.20)
                
                x_mini = rect_heroes.x + int((heroe.x - PANEL_ANCHO) * factor_x)
                y_mini = rect_heroes.y + int(heroe.y * factor_y)
                ancho_mini = max(20, int(heroe.ancho * factor_x))
                alto_mini = max(20, int(heroe.alto * factor_y))
                
                pygame.draw.rect(surface, (100, 255, 100), (x_mini, y_mini, ancho_mini, alto_mini), border_radius=2)
                
                # Número de slot escalado
                tamano_num_slot = v.get_tamano_texto_escalado(12)
                fuente_num = pygame.font.Font(None, tamano_num_slot)
                texto_num = fuente_num.render(str(heroe.slot_numero), True, (0, 0, 0))
                surface.blit(texto_num, (x_mini + 3, y_mini + 2))
        
        # 3. Zona de monstruos (centro, 50%)
        y_monstruos = v.y + 35 + alto_heroes + margen
        alto_monstruos = v.alto - alto_heroes - 50 - margen
        
        rect_monstruos = pygame.Rect(int(x_heroes), int(y_monstruos), ancho_centro, alto_monstruos)
        pygame.draw.rect(surface, (100, 50, 50), rect_monstruos, border_radius=5)
        pygame.draw.rect(surface, (200, 100, 100), rect_monstruos, 2, border_radius=5)
        
        # Dibujar monstruos colocados
        monstruos_en_batalla = [s for s in self.sprites_colocados if s.tipo == "monstruo" and s.slot_numero <= self.cantidad_monstruos_seleccionada]
        if monstruos_en_batalla:
            for monstruo in monstruos_en_batalla:
                # Escalar miniatura proporcionalmente
                factor_x = ancho_centro / AREA_BATALLA_ANCHO
                factor_y = alto_monstruos / (ALTO * 0.50)
                
                x_mini = rect_monstruos.x + int((monstruo.x - PANEL_ANCHO) * factor_x)
                y_mini = rect_monstruos.y + int((monstruo.y - alto_heroes - 35) * factor_y)
                ancho_mini = max(20, int(monstruo.ancho * factor_x))
                alto_mini = max(20, int(monstruo.alto * factor_y))
                
                pygame.draw.rect(surface, (255, 100, 100), (x_mini, y_mini, ancho_mini, alto_mini), border_radius=2)
                
                # Número de slot escalado
                tamano_num_slot = v.get_tamano_texto_escalado(12)
                fuente_num = pygame.font.Font(None, tamano_num_slot)
                texto_num = fuente_num.render(str(monstruo.slot_numero), True, (0, 0, 0))
                surface.blit(texto_num, (x_mini + 3, y_mini + 2))
    
    def dibujar_textos_flotantes(self, surface):
        """Dibuja los textos flotantes de demostración"""
        for texto in self.textos_flotantes_demo:
            fuente_texto = pygame.font.Font(None, texto.tamano)
            texto_surf = fuente_texto.render(texto.texto, True, texto.color)
            
            # Centrar el texto
            x_centrado = int(texto.x - texto_surf.get_width() // 2)
            y_centrado = int(texto.y - texto_surf.get_height() // 2)
            surface.blit(texto_surf, (x_centrado, y_centrado))
            
            # Borde de selección
            if texto == self.texto_seleccionado:
                pygame.draw.rect(surface, COLOR_SELECCION, texto.rect, 2)
                # Handles
                tam = 6
                handles = [
                    (texto.rect.x, texto.rect.y),
                    (texto.rect.x + texto.rect.width, texto.rect.y),
                    (texto.rect.x, texto.rect.y + texto.rect.height),
                    (texto.rect.x + texto.rect.width, texto.rect.y + texto.rect.height)
                ]
                for hx, hy in handles:
                    pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), tam)
                    pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam, 1)
    
    def dibujar_paleta_colores(self, surface):
        """Dibuja la paleta de colores"""
        if not self.mostrar_paleta or not self.tipo_color_editando:
            return
        
        paleta_x = PANEL_ANCHO + 50
        paleta_y = 50
        paleta_ancho = 300
        paleta_alto = 200
        
        # Fondo de la paleta
        pygame.draw.rect(surface, (40, 40, 50), (paleta_x, paleta_y, paleta_ancho, paleta_alto), border_radius=10)
        pygame.draw.rect(surface, COLOR_TEXTO, (paleta_x, paleta_y, paleta_ancho, paleta_alto), 3, border_radius=10)
        
        # Título
        titulo = f"Color: {self.tipo_color_editando.upper()}"
        texto_titulo = self.fuente.render(titulo, True, COLOR_TEXTO)
        surface.blit(texto_titulo, (paleta_x + 10, paleta_y + 10))
        
        # Sliders RGB
        color_actual = self.colores_config[self.tipo_color_editando]
        componentes = ["R", "G", "B"]
        
        for i, (comp, valor) in enumerate(zip(componentes, color_actual)):
            y_slider = paleta_y + 50 + (i * 40)
            
            # Etiqueta
            texto_comp = self.fuente.render(f"{comp}: {valor}", True, COLOR_TEXTO)
            surface.blit(texto_comp, (paleta_x + 10, y_slider))
            
            # Slider
            slider_x = paleta_x + 60
            slider_ancho = 200
            pygame.draw.rect(surface, (80, 80, 80), (slider_x, y_slider + 5, slider_ancho, 10), border_radius=5)
            
            # Indicador
            pos_indicador = slider_x + int((valor / 255) * slider_ancho)
            pygame.draw.circle(surface, COLOR_BOTON_ACTIVO, (pos_indicador, y_slider + 10), 8)
            pygame.draw.circle(surface, COLOR_TEXTO, (pos_indicador, y_slider + 10), 8, 2)
        
        # Preview del color
        preview_x = paleta_x + 10
        preview_y = paleta_y + paleta_alto - 40
        pygame.draw.rect(surface, tuple(color_actual), (preview_x, preview_y, 280, 30), border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, (preview_x, preview_y, 280, 30), 2, border_radius=5)
        
        # Botones para cambiar de tipo de texto
        tipos = ["normal", "critico", "curacion", "miss"]
        for idx, tipo in enumerate(tipos):
            btn_x = paleta_x + 10 + (idx * 70)
            btn_y = paleta_y + paleta_alto - 70
            btn_ancho = 65
            btn_alto = 25
            
            # Color del botón
            if tipo == self.tipo_color_editando:
                btn_color = COLOR_BOTON_ACTIVO
            else:
                btn_color = tuple(self.colores_config[tipo])
            
            pygame.draw.rect(surface, btn_color, (btn_x, btn_y, btn_ancho, btn_alto), border_radius=3)
            pygame.draw.rect(surface, COLOR_TEXTO, (btn_x, btn_y, btn_ancho, btn_alto), 2, border_radius=3)
            
            # Texto del botón
            texto_btn = self.fuente_pequena.render(tipo[:3].upper(), True, (0, 0, 0) if sum(self.colores_config[tipo]) > 400 else COLOR_TEXTO)
            surface.blit(texto_btn, (btn_x + 15, btn_y + 5))
    
    def dibujar_panel_lateral(self, surface):
        """Dibuja el panel lateral con secciones"""
        # Fondo
        pygame.draw.rect(surface, COLOR_PANEL, (0, 0, PANEL_ANCHO, ALTO))
        
        # Título
        texto = self.fuente_titulo.render("Sprites", True, COLOR_TEXTO)
        surface.blit(texto, (10, 10))
        
        # Selectores numéricos de cantidad
        mouse_pos = pygame.mouse.get_pos()
        y_selectores = 45
        
        # Selector de héroes (1-4)
        texto_heroes = self.fuente_pequena.render("Heroes:", True, (100, 255, 100))
        surface.blit(texto_heroes, (10, y_selectores))
        
        for num in range(1, 5):
            btn_x = 10 + (num - 1) * 70
            btn_y = y_selectores + 20
            btn_ancho = 60
            btn_alto = 30
            
            btn_rect = pygame.Rect(btn_x, btn_y, btn_ancho, btn_alto)
            
            # Color del botón
            if num == self.cantidad_heroes_seleccionada:
                btn_color = (50, 200, 50)
            elif btn_rect.collidepoint(mouse_pos):
                btn_color = (80, 230, 80)
            else:
                btn_color = (30, 100, 30)
            
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_TEXTO, btn_rect, 2, border_radius=5)
            
            # Número
            texto_num = self.fuente.render(str(num), True, COLOR_TEXTO)
            texto_rect = texto_num.get_rect(center=btn_rect.center)
            surface.blit(texto_num, texto_rect)
        
        # Selector de monstruos (1-6)
        y_monstruos = y_selectores + 60
        texto_monstruos = self.fuente_pequena.render("Monstruos:", True, (255, 100, 255))
        surface.blit(texto_monstruos, (10, y_monstruos))
        
        for num in range(1, 7):
            col = (num - 1) % 3
            fila = (num - 1) // 3
            btn_x = 10 + col * 95
            btn_y = y_monstruos + 20 + (fila * 35)
            btn_ancho = 85
            btn_alto = 30
            
            btn_rect = pygame.Rect(btn_x, btn_y, btn_ancho, btn_alto)
            
            # Color del botón
            if num == self.cantidad_monstruos_seleccionada:
                btn_color = (200, 50, 200)
            elif btn_rect.collidepoint(mouse_pos):
                btn_color = (230, 80, 230)
            else:
                btn_color = (100, 30, 100)
            
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_TEXTO, btn_rect, 2, border_radius=5)
            
            # Número
            texto_num = self.fuente.render(str(num), True, COLOR_TEXTO)
            texto_rect = texto_num.get_rect(center=btn_rect.center)
            surface.blit(texto_num, texto_rect)
        
        # Contadores de sprites actuales
        heroes_actuales = len([s for s in self.sprites_colocados if s.tipo == 'heroe'])
        monstruos_actuales = len([s for s in self.sprites_colocados if s.tipo == 'monstruo'])
        
        y_contadores = y_monstruos + 90
        texto_count_h = self.fuente_pequena.render(f"Colocados: {heroes_actuales}/{self.cantidad_heroes_seleccionada}", True, (150, 255, 150))
        texto_count_m = self.fuente_pequena.render(f"Colocados: {monstruos_actuales}/{self.cantidad_monstruos_seleccionada}", True, (255, 150, 255))
        surface.blit(texto_count_h, (10, y_contadores))
        surface.blit(texto_count_m, (160, y_contadores))
        
        # Botón recargar
        rect_recargar = pygame.Rect(PANEL_ANCHO - 120, 15, 110, 30)
        color = COLOR_BOTON_HOVER if rect_recargar.collidepoint(mouse_pos) else (50, 150, 50)
        pygame.draw.rect(surface, color, rect_recargar, border_radius=5)
        texto_rec = self.fuente_pequena.render("↻ Recargar", True, COLOR_TEXTO)
        surface.blit(texto_rec, (rect_recargar.x + 15, rect_recargar.y + 8))
        
        # Ajustar posiciones de secciones según expansión  
        y_secciones_inicio = y_contadores + 30
        self.seccion_heroes.rect_titulo.y = y_secciones_inicio
        self.seccion_heroes.dibujar(surface, self.scroll_heroes, self.items_visibles_max)
        
        self.seccion_monstruos.rect_titulo.y = y_secciones_inicio + self.seccion_heroes.get_alto_total() + 10
        self.seccion_monstruos.dibujar(surface, self.scroll_monstruos, self.items_visibles_max)
        
        # Botones de acción en la parte inferior
        y_botones = ALTO - 230
        
        # Botón Textos Flotantes
        rect_textos = pygame.Rect(10, y_botones, PANEL_ANCHO - 20, 30)
        color_t = (150, 100, 255) if self.mostrar_textos_flotantes else (80, 50, 120)
        if rect_textos.collidepoint(mouse_pos):
            color_t = (180, 130, 255)
        pygame.draw.rect(surface, color_t, rect_textos, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, rect_textos, 2, border_radius=5)
        texto_t = self.fuente_pequena.render("Textos Flotantes", True, COLOR_TEXTO)
        surface.blit(texto_t, (rect_textos.x + 50, rect_textos.y + 8))
        
        # Botón Ventana de Magia
        y_botones += 35
        rect_magia = pygame.Rect(10, y_botones, PANEL_ANCHO - 20, 30)
        color_m = (100, 150, 255) if self.mostrar_ventana_magia else (50, 80, 120)
        if rect_magia.collidepoint(mouse_pos):
            color_m = (130, 180, 255)
        pygame.draw.rect(surface, color_m, rect_magia, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, rect_magia, 2, border_radius=5)
        texto_m = self.fuente_pequena.render("Ventana Magia", True, COLOR_TEXTO)
        surface.blit(texto_m, (rect_magia.x + 60, rect_magia.y + 8))
        
        # Botón Ventana Emulador
        y_botones += 35
        rect_emulador = pygame.Rect(10, y_botones, PANEL_ANCHO - 20, 30)
        color_e = (255, 150, 100) if self.mostrar_ventana_emulador else (120, 80, 50)
        if rect_emulador.collidepoint(mouse_pos):
            color_e = (255, 180, 130)
        pygame.draw.rect(surface, color_e, rect_emulador, border_radius=5)
        pygame.draw.rect(surface, COLOR_TEXTO, rect_emulador, 2, border_radius=5)
        texto_e = self.fuente_pequena.render("Ventana Emulador", True, COLOR_TEXTO)
        surface.blit(texto_e, (rect_emulador.x + 50, rect_emulador.y + 8))
        
        # Ajustar posición de instrucción
        y_botones += 35
        
        # Instrucción de arrastre si los textos están activos
        if self.mostrar_textos_flotantes:
            instruccion = self.fuente_pequena.render("Arrastra colores ->", True, (150, 255, 150))
            surface.blit(instruccion, (10, y_botones + 5))
            
            # Botón para abrir paleta de colores
            rect_paleta = pygame.Rect(160, y_botones + 3, 130, 20)
            color_paleta = (255, 150, 50) if rect_paleta.collidepoint(mouse_pos) else (200, 100, 30)
            pygame.draw.rect(surface, color_paleta, rect_paleta, border_radius=3)
            texto_paleta = self.fuente_pequena.render("[Editar Colores]", True, COLOR_TEXTO)
            surface.blit(texto_paleta, (rect_paleta.x + 5, rect_paleta.y + 3))
        
        # Botones de paleta de colores (2x2 grid)
        tipos_colores = ["normal", "critico", "curacion", "miss"]
        y_inicio_botones = y_botones + 25 if self.mostrar_textos_flotantes else y_botones + 10
        for i, tipo in enumerate(tipos_colores):
            col = i % 2
            fila = i // 2
            rect_color = pygame.Rect(10 + col * 145, y_inicio_botones + fila * 40, 135, 35)
            color_btn = tuple(self.colores_config[tipo]) if self.tipo_color_editando != tipo else COLOR_BOTON_ACTIVO
            if rect_color.collidepoint(mouse_pos):
                # Aclarar color
                color_btn = tuple(min(c + 50, 255) for c in self.colores_config[tipo])
            pygame.draw.rect(surface, color_btn, rect_color, border_radius=5)
            pygame.draw.rect(surface, COLOR_TEXTO, rect_color, 2, border_radius=5)
            
            # Texto del botón con indicador
            if self.mostrar_textos_flotantes:
                texto_col = self.fuente_pequena.render(f"[{tipo[:3].upper()}]", True, (0, 0, 0) if sum(self.colores_config[tipo]) > 400 else COLOR_TEXTO)
            else:
                texto_col = self.fuente_pequena.render(tipo.capitalize(), True, (0, 0, 0) if sum(self.colores_config[tipo]) > 400 else COLOR_TEXTO)
            surface.blit(texto_col, (rect_color.x + 35, rect_color.y + 10))
        
        # Nota: Botones Guardar/Cargar ahora están en la derecha (ver dibujar_botones_derecha)
        
        # Info del sprite/texto seleccionado
        y_info = y_inicio_botones + 85
        if self.sprite_seleccionado:
            s = self.sprite_seleccionado
            info = [
                f"Sprite:",
                f"{s.sprite_ref[:20]}",
                f"Pos: ({int(s.x)}, {int(s.y)})",
                f"Tam: {s.ancho}x{s.alto}"
            ]
            for i, linea in enumerate(info):
                texto = self.fuente_pequena.render(linea, True, COLOR_TEXTO if i == 0 else COLOR_TEXTO_SEC)
                surface.blit(texto, (10, y_info + i * 18))
        elif self.texto_seleccionado:
            t = self.texto_seleccionado
            info = [
                f"Texto:",
                f"{t.texto}",
                f"Tipo: {t.tipo}",
                f"Tam: {t.tamano}px"
            ]
            for i, linea in enumerate(info):
                texto = self.fuente_pequena.render(linea, True, COLOR_TEXTO if i == 0 else COLOR_TEXTO_SEC)
                surface.blit(texto, (10, y_info + i * 18))
    
    def dibujar_botones_derecha(self, surface):
        """Dibuja los botones Guardar/Cargar en la parte derecha de la pantalla"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Posición en la derecha
        btn_ancho = 140
        btn_alto = 50
        margen = 20
        x_botones = ANCHO - btn_ancho - margen
        y_inicio = 50
        espacio = 20
        
        # Botón Guardar
        rect_guardar = pygame.Rect(x_botones, y_inicio, btn_ancho, btn_alto)
        color_g = (50, 200, 50) if rect_guardar.collidepoint(mouse_pos) else (30, 150, 30)
        pygame.draw.rect(surface, color_g, rect_guardar, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXTO, rect_guardar, 3, border_radius=8)
        texto_g = self.fuente.render("Guardar", True, COLOR_TEXTO)
        texto_rect_g = texto_g.get_rect(center=rect_guardar.center)
        surface.blit(texto_g, texto_rect_g)
        
        # Botón Cargar
        rect_cargar = pygame.Rect(x_botones, y_inicio + btn_alto + espacio, btn_ancho, btn_alto)
        color_c = (50, 150, 200) if rect_cargar.collidepoint(mouse_pos) else (30, 100, 150)
        pygame.draw.rect(surface, color_c, rect_cargar, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXTO, rect_cargar, 3, border_radius=8)
        texto_c = self.fuente.render("Cargar", True, COLOR_TEXTO)
        texto_rect_c = texto_c.get_rect(center=rect_cargar.center)
        surface.blit(texto_c, texto_rect_c)
        
        # Guardar las posiciones para eventos
        self.rect_guardar_derecha = rect_guardar
        self.rect_cargar_derecha = rect_cargar
    
    def dibujar_barra_estado(self, surface):
        """Dibuja barra de estado"""
        alto_barra = 30
        pygame.draw.rect(surface, (45, 45, 65), (0, ALTO - alto_barra, ANCHO, alto_barra))
        
        # Info
        texto = f"Sprites: {len(self.sprites_colocados)} | Héroes: {len([s for s in self.sprites_colocados if s.tipo == 'heroe'])} | Monstruos: {len([s for s in self.sprites_colocados if s.tipo == 'monstruo'])}"
        texto_surf = self.fuente_pequena.render(texto, True, COLOR_TEXTO)
        surface.blit(texto_surf, (10, ALTO - alto_barra + 8))
        
        # Controles
        controles = "T: Textos | G: Guardar | L: Cargar | D: Duplicar | DEL: Eliminar | ESC: Salir"
        texto_ctrl = self.fuente_pequena.render(controles, True, COLOR_TEXTO_SEC)
        surface.blit(texto_ctrl, (PANEL_ANCHO + 20, ALTO - alto_barra + 8))
        
        # Mensaje temporal
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_tiempo < 3000:
            mensaje_surf = self.fuente.render(self.mensaje, True, (100, 255, 100))
            surface.blit(mensaje_surf, (ANCHO // 2 - mensaje_surf.get_width() // 2, ALTO - alto_barra - 40))
    
    def manejar_eventos(self):
        """Maneja eventos"""
        mouse_pos = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # Cerrar paleta si está abierta
                    if self.mostrar_paleta:
                        self.mostrar_paleta = False
                        self.tipo_color_editando = None
                    else:
                        return False
                elif evento.key == pygame.K_g:
                    self.guardar_configuracion()
                elif evento.key == pygame.K_l:
                    self.cargar_configuracion()
                elif evento.key == pygame.K_d and self.sprite_seleccionado:
                    self.duplicar_sprite(self.sprite_seleccionado)
                elif evento.key == pygame.K_DELETE:
                    if self.sprite_seleccionado:
                        self.eliminar_sprite(self.sprite_seleccionado)
                    elif self.texto_seleccionado and self.mostrar_textos_flotantes:
                        self.textos_flotantes_demo.remove(self.texto_seleccionado)
                        self.texto_seleccionado = None
                        self.mostrar_mensaje("✓ Texto eliminado")
                elif evento.key == pygame.K_r:
                    self.cargar_sprites()
                    self.mostrar_mensaje("✓ Sprites recargados")
                elif evento.key == pygame.K_t:
                    self.mostrar_textos_flotantes = not self.mostrar_textos_flotantes
                    if self.mostrar_textos_flotantes and not self.textos_flotantes_demo:
                        self.crear_textos_flotantes_demo()
                    else:
                        # Al desactivar textos, cerrar también la paleta de colores
                        if not self.mostrar_textos_flotantes:
                            self.mostrar_paleta = False
                            self.tipo_color_editando = None
                    self.mostrar_mensaje(f"Textos: {'ON' if self.mostrar_textos_flotantes else 'OFF'}")
                
                # Manejo de scroll con flechas
                elif evento.key in (pygame.K_UP, pygame.K_DOWN):
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - self.tiempo_ultimo_scroll > self.cooldown_scroll:
                        # Determinar qué sección está expandida para aplicar scroll
                        if self.seccion_heroes.expandida:
                            total_heroes = len(self.seccion_heroes.items)
                            if total_heroes > self.items_visibles_max:
                                if evento.key == pygame.K_DOWN:
                                    # Scroll hacia abajo
                                    max_scroll = total_heroes - self.items_visibles_max
                                    self.scroll_heroes = min(self.scroll_heroes + 1, max_scroll)
                                elif evento.key == pygame.K_UP:
                                    # Scroll hacia arriba
                                    self.scroll_heroes = max(self.scroll_heroes - 1, 0)
                                self.tiempo_ultimo_scroll = tiempo_actual
                                
                        elif self.seccion_monstruos.expandida:
                            total_monstruos = len(self.seccion_monstruos.items)
                            if total_monstruos > self.items_visibles_max:
                                if evento.key == pygame.K_DOWN:
                                    # Scroll hacia abajo
                                    max_scroll = total_monstruos - self.items_visibles_max
                                    self.scroll_monstruos = min(self.scroll_monstruos + 1, max_scroll)
                                elif evento.key == pygame.K_UP:
                                    # Scroll hacia arriba
                                    self.scroll_monstruos = max(self.scroll_monstruos - 1, 0)
                                self.tiempo_ultimo_scroll = tiempo_actual
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    # Click en panel lateral
                    if mouse_pos[0] < PANEL_ANCHO:
                        # Botón recargar
                        rect_recargar = pygame.Rect(PANEL_ANCHO - 120, 15, 110, 30)
                        if rect_recargar.collidepoint(mouse_pos):
                            self.cargar_sprites()
                            self.mostrar_mensaje("✓ Sprites recargados")
                            continue
                        
                        # Selectores de cantidad de héroes (1-4)
                        y_selectores = 45
                        for num in range(1, 5):
                            btn_x = 10 + (num - 1) * 70
                            btn_y = y_selectores + 20
                            btn_rect = pygame.Rect(btn_x, btn_y, 60, 30)
                            if btn_rect.collidepoint(mouse_pos):
                                self.cantidad_heroes_seleccionada = num
                                # Limpiar sprites de héroes que excedan la nueva cantidad
                                heroes = [s for s in self.sprites_colocados if s.tipo == 'heroe']
                                if len(heroes) > num:
                                    for sprite in heroes[num:]:
                                        self.sprites_colocados.remove(sprite)
                                self.mostrar_mensaje(f"✓ Configurado: {num} héroe(s)")
                                continue
                        
                        # Selectores de cantidad de monstruos (1-6)
                        y_monstruos = y_selectores + 60
                        for num in range(1, 7):
                            col = (num - 1) % 3
                            fila = (num - 1) // 3
                            btn_x = 10 + col * 95
                            btn_y = y_monstruos + 20 + (fila * 35)
                            btn_rect = pygame.Rect(btn_x, btn_y, 85, 30)
                            if btn_rect.collidepoint(mouse_pos):
                                self.cantidad_monstruos_seleccionada = num
                                # Limpiar sprites de monstruos que excedan la nueva cantidad
                                monstruos = [s for s in self.sprites_colocados if s.tipo == 'monstruo']
                                if len(monstruos) > num:
                                    for sprite in monstruos[num:]:
                                        self.sprites_colocados.remove(sprite)
                                self.mostrar_mensaje(f"✓ Configurado: {num} monstruo(s)")
                                continue
                        
                        # Click en título de sección
                        if self.seccion_heroes.click_en_titulo(mouse_pos):
                            self.seccion_heroes.toggle()
                            # Resetear scroll al alternar sección
                            self.scroll_heroes = 0
                        elif self.seccion_monstruos.click_en_titulo(mouse_pos):
                            self.seccion_monstruos.toggle()
                            # Resetear scroll al alternar sección
                            self.scroll_monstruos = 0
                        
                        # Click en item de sección (iniciar drag)
                        else:
                            item = self.seccion_heroes.get_item_en_posicion(mouse_pos, self.scroll_heroes, self.items_visibles_max)
                            if not item:
                                item = self.seccion_monstruos.get_item_en_posicion(mouse_pos, self.scroll_monstruos, self.items_visibles_max)
                            
                            if item:
                                self.sprite_siendo_arrastrado = item
                                self.arrastrando_desde_panel = True
                                self.offset_drag_x = mouse_pos[0]
                                self.offset_drag_y = mouse_pos[1]
                        
                        # Botón textos flotantes
                        y_botones_extra = ALTO - 230
                        rect_textos = pygame.Rect(10, y_botones_extra, PANEL_ANCHO - 20, 30)
                        if rect_textos.collidepoint(mouse_pos):
                            self.mostrar_textos_flotantes = not self.mostrar_textos_flotantes
                            if self.mostrar_textos_flotantes and not self.textos_flotantes_demo:
                                self.crear_textos_flotantes_demo()
                            else:
                                # Al desactivar textos, cerrar también la paleta de colores
                                if not self.mostrar_textos_flotantes:
                                    self.mostrar_paleta = False
                                    self.tipo_color_editando = None
                            self.mostrar_mensaje(f"Textos: {'ON' if self.mostrar_textos_flotantes else 'OFF'}")
                            continue
                        
                        # Botón ventana de magia
                        rect_magia = pygame.Rect(10, y_botones_extra + 35, PANEL_ANCHO - 20, 30)
                        if rect_magia.collidepoint(mouse_pos):
                            self.mostrar_ventana_magia = not self.mostrar_ventana_magia
                            self.mostrar_mensaje(f"Ventana Magia: {'ON' if self.mostrar_ventana_magia else 'OFF'}")
                            continue
                        
                        # Botón ventana emulador
                        rect_emulador = pygame.Rect(10, y_botones_extra + 70, PANEL_ANCHO - 20, 30)
                        if rect_emulador.collidepoint(mouse_pos):
                            self.mostrar_ventana_emulador = not self.mostrar_ventana_emulador
                            self.mostrar_mensaje(f"Ventana Emulador: {'ON' if self.mostrar_ventana_emulador else 'OFF'}")
                            continue
                        
                        # Botón para abrir paleta de colores (solo si textos están activados)
                        if self.mostrar_textos_flotantes:
                            rect_paleta = pygame.Rect(160, y_botones_extra + 3, 130, 20)
                            if rect_paleta.collidepoint(mouse_pos):
                                if not self.mostrar_paleta:
                                    self.mostrar_paleta = True
                                    self.tipo_color_editando = "normal"
                                    self.mostrar_mensaje("✓ Paleta de colores abierta")
                                else:
                                    self.mostrar_paleta = False
                                    self.tipo_color_editando = None
                                    self.mostrar_mensaje("✓ Paleta de colores cerrada")
                                continue
                        
                        # Botones de paleta de colores (arrastrar para crear textos)
                        tipos_colores = ["normal", "critico", "curacion", "miss"]
                        y_inicio_botones = y_botones_extra + 130 if self.mostrar_textos_flotantes else y_botones_extra + 105
                        for i, tipo in enumerate(tipos_colores):
                            col = i % 2
                            fila = i // 2
                            rect_color = pygame.Rect(10 + col * 145, y_inicio_botones + fila * 40, 135, 35)
                            if rect_color.collidepoint(mouse_pos):
                                # Si los textos están activados, iniciar arrastre
                                if self.mostrar_textos_flotantes:
                                    self.texto_siendo_arrastrado = tipo
                                    self.arrastrando_desde_panel = True
                                    self.offset_drag_x = mouse_pos[0]
                                    self.offset_drag_y = mouse_pos[1]
                                else:
                                    # Si no, abrir paleta de colores
                                    self.tipo_color_editando = tipo
                                    self.mostrar_paleta = True
                                    self.mostrar_mensaje(f"Editando color: {tipo}")
                                continue
                        
                        # Botones guardar/cargar (ahora en la derecha)
                        if hasattr(self, 'rect_guardar_derecha') and self.rect_guardar_derecha and self.rect_guardar_derecha.collidepoint(mouse_pos):
                            self.guardar_configuracion()
                        elif hasattr(self, 'rect_cargar_derecha') and self.rect_cargar_derecha and self.rect_cargar_derecha.collidepoint(mouse_pos):
                            self.cargar_configuracion()
                    
                    # Click en paleta de colores (sliders y selector de tipo)
                    if self.mostrar_paleta and self.tipo_color_editando:
                        paleta_x = PANEL_ANCHO + 50
                        paleta_y = 50
                        paleta_ancho = 300
                        paleta_alto = 200
                        
                        # Click en botones de tipo de texto en la paleta
                        tipos = ["normal", "critico", "curacion", "miss"]
                        for idx, tipo in enumerate(tipos):
                            btn_x = paleta_x + 10 + (idx * 70)
                            btn_y = paleta_y + paleta_alto - 70
                            btn_rect = pygame.Rect(btn_x, btn_y, 65, 25)
                            if btn_rect.collidepoint(mouse_pos):
                                self.tipo_color_editando = tipo
                                self.mostrar_mensaje(f"Editando: {tipo}")
                                continue
                        
                        # Click en sliders
                        for i in range(3):  # R, G, B
                            y_slider = paleta_y + 50 + (i * 40)
                            slider_x = paleta_x + 60
                            slider_ancho = 200
                            
                            if slider_x <= mouse_pos[0] <= slider_x + slider_ancho and y_slider <= mouse_pos[1] <= y_slider + 20:
                                # Calcular nuevo valor
                                valor = int(((mouse_pos[0] - slider_x) / slider_ancho) * 255)
                                valor = max(0, min(255, valor))
                                self.colores_config[self.tipo_color_editando][i] = valor
                                self.actualizar_colores_textos()
                                continue
                                valor = int(((mouse_pos[0] - slider_x) / slider_ancho) * 255)
                                valor = max(0, min(255, valor))
                                self.colores_config[self.tipo_color_editando][i] = valor
                                self.actualizar_colores_textos()
                                continue
                    
                    # Click en área de batalla (siempre procesar, independiente de la paleta)
                    if mouse_pos[0] >= PANEL_ANCHO:
                        x_batalla = mouse_pos[0] - PANEL_ANCHO
                        y_batalla = mouse_pos[1]
                        
                        # Variable para saber si se clickeó alguna ventana
                        ventana_clickeada = False
                        
                        # Verificar click en ventana de magia
                        if self.mostrar_ventana_magia and not ventana_clickeada:
                            vm = self.ventana_magia
                            if vm.contiene_punto(x_batalla, y_batalla):
                                self.sprite_seleccionado = None
                                self.texto_seleccionado = None
                                ventana_clickeada = True
                                
                                # Verificar handle
                                handle = vm.get_handle_en_punto(x_batalla, y_batalla, 10)
                                if handle:
                                    vm.escalando = True
                                    vm.handle_activo = handle
                                else:
                                    vm.arrastrando = True
                                    vm.offset_x = vm.x - x_batalla
                                    vm.offset_y = vm.y - y_batalla
                        
                        # Verificar click en ventana emulador
                        if self.mostrar_ventana_emulador and not ventana_clickeada:
                            ve = self.ventana_emulador
                            if ve.contiene_punto(x_batalla, y_batalla):
                                self.sprite_seleccionado = None
                                self.texto_seleccionado = None
                                ventana_clickeada = True
                                
                                # Verificar handle
                                handle = ve.get_handle_en_punto(x_batalla, y_batalla, 10)
                                if handle:
                                    ve.escalando = True
                                    ve.handle_activo = handle
                                else:
                                    ve.arrastrando = True
                                    ve.offset_x = ve.x - x_batalla
                                    ve.offset_y = ve.y - y_batalla
                        
                        # Solo procesar otros elementos si no se clickeó una ventana
                        if not ventana_clickeada:
                            # Verificar click en texto flotante
                            texto_clickeado = None
                            if self.mostrar_textos_flotantes:
                                for texto in reversed(self.textos_flotantes_demo):
                                    if texto.contiene_punto(x_batalla, y_batalla):
                                        texto_clickeado = texto
                                        break
                        
                            if texto_clickeado:
                                self.texto_seleccionado = texto_clickeado
                                self.sprite_seleccionado = None
                                
                                # Verificar handle
                                handle = texto_clickeado.get_handle_en_punto(x_batalla, y_batalla, 8)
                                if handle:
                                    texto_clickeado.escalando = True
                                    texto_clickeado.handle_activo = handle
                                else:
                                    texto_clickeado.arrastrando = True
                                    texto_clickeado.offset_x = texto_clickeado.x - x_batalla
                                    texto_clickeado.offset_y = texto_clickeado.y - y_batalla
                            else:
                                # Verificar click en ventana de batalla
                                v = self.ventana_batalla
                                if v.contiene_punto(x_batalla, y_batalla):
                                    self.sprite_seleccionado = None
                                    self.texto_seleccionado = None
                                    
                                    # Verificar handle
                                    handle = v.get_handle_en_punto(x_batalla, y_batalla, 10)
                                    if handle:
                                        v.escalando = True
                                        v.handle_activo = handle
                                    else:
                                        v.arrastrando = True
                                        v.offset_x = v.x - x_batalla
                                        v.offset_y = v.y - y_batalla
                                else:
                                    # Click en sprite
                                    sprite = self.get_sprite_en_posicion(x_batalla, y_batalla)
                                    
                                    if sprite:
                                        self.sprite_seleccionado = sprite
                                        self.texto_seleccionado = None
                                        
                                        # Verificar si clickeó un handle
                                        handle = sprite.get_handle_en_punto(x_batalla, y_batalla, 10)
                                        
                                        if handle:
                                            sprite.escalando = True
                                            sprite.handle_activo = handle
                                        else:
                                            sprite.arrastrando = True
                                            sprite.offset_x = sprite.x - x_batalla
                                            sprite.offset_y = sprite.y - y_batalla
                                    else:
                                        self.sprite_seleccionado = None
                                        self.texto_seleccionado = None
                
                elif evento.button == 3:  # Click derecho - eliminar
                    if mouse_pos[0] >= PANEL_ANCHO:
                        x_batalla = mouse_pos[0] - PANEL_ANCHO
                        y_batalla = mouse_pos[1]
                        sprite = self.get_sprite_en_posicion(x_batalla, y_batalla)
                        if sprite:
                            self.eliminar_sprite(sprite)
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    # Soltar sprite arrastrado desde panel
                    if self.arrastrando_desde_panel and self.sprite_siendo_arrastrado:
                        if mouse_pos[0] >= PANEL_ANCHO:
                            x_drop = mouse_pos[0] - PANEL_ANCHO
                            y_drop = mouse_pos[1]
                            self.crear_sprite_en_posicion(self.sprite_siendo_arrastrado, x_drop, y_drop)
                        
                        self.sprite_siendo_arrastrado = None
                        self.arrastrando_desde_panel = False
                    
                    # Soltar texto arrastrado desde panel
                    if self.arrastrando_desde_panel and self.texto_siendo_arrastrado:
                        if mouse_pos[0] >= PANEL_ANCHO:
                            x_drop = mouse_pos[0] - PANEL_ANCHO
                            y_drop = mouse_pos[1]
                            self.crear_texto_flotante_en_posicion(self.texto_siendo_arrastrado, x_drop, y_drop)
                        
                        self.texto_siendo_arrastrado = None
                        self.arrastrando_desde_panel = False
                    
                    # Soltar sprites colocados
                    for sprite in self.sprites_colocados:
                        sprite.arrastrando = False
                        sprite.escalando = False
                        sprite.handle_activo = None
                    
                    # Soltar textos flotantes
                    for texto in self.textos_flotantes_demo:
                        texto.arrastrando = False
                        texto.escalando = False
                        texto.handle_activo = None
                    
                    # Soltar ventana de batalla
                    self.ventana_batalla.arrastrando = False
                    self.ventana_batalla.escalando = False
                    self.ventana_batalla.handle_activo = None
                    
                    # Soltar ventana de magia
                    self.ventana_magia.arrastrando = False
                    self.ventana_magia.escalando = False
                    self.ventana_magia.handle_activo = None
                    
                    # Soltar ventana emulador
                    self.ventana_emulador.arrastrando = False
                    self.ventana_emulador.escalando = False
                    self.ventana_emulador.handle_activo = None
            
            elif evento.type == pygame.MOUSEMOTION:
                if mouse_pos[0] >= PANEL_ANCHO:
                    x_batalla = mouse_pos[0] - PANEL_ANCHO
                    y_batalla = mouse_pos[1]
                    
                    # Arrastrar/escalar ventana de batalla
                    v = self.ventana_batalla
                    if v.arrastrando:
                        v.x = x_batalla + v.offset_x
                        v.y = y_batalla + v.offset_y
                        v.actualizar_rect()
                    elif v.escalando and v.handle_activo:
                        if 'e' in v.handle_activo:
                            nuevo_ancho = max(200, x_batalla - v.x)
                            v.ancho = nuevo_ancho
                        elif 'w' in v.handle_activo:
                            nuevo_ancho = max(200, v.x + v.ancho - x_batalla)
                            if nuevo_ancho >= 200:
                                v.x = x_batalla
                                v.ancho = nuevo_ancho
                        
                        if 's' in v.handle_activo:
                            nuevo_alto = max(60, y_batalla - v.y)
                            v.alto = nuevo_alto
                        elif 'n' in v.handle_activo:
                            nuevo_alto = max(60, v.y + v.alto - y_batalla)
                            if nuevo_alto >= 60:
                                v.y = y_batalla
                                v.alto = nuevo_alto
                        
                        v.actualizar_rect()
                    
                    # Arrastrar/escalar ventana de magia
                    vm = self.ventana_magia
                    if vm.arrastrando:
                        vm.x = x_batalla + vm.offset_x
                        vm.y = y_batalla + vm.offset_y
                        vm.actualizar_rect()
                    elif vm.escalando and vm.handle_activo:
                        if 'e' in vm.handle_activo:
                            nuevo_ancho = max(200, x_batalla - vm.x)
                            vm.ancho = nuevo_ancho
                        elif 'w' in vm.handle_activo:
                            nuevo_ancho = max(200, vm.x + vm.ancho - x_batalla)
                            if nuevo_ancho >= 200:
                                vm.x = x_batalla
                                vm.ancho = nuevo_ancho
                        
                        if 's' in vm.handle_activo:
                            nuevo_alto = max(100, y_batalla - vm.y)
                            vm.alto = nuevo_alto
                        elif 'n' in vm.handle_activo:
                            nuevo_alto = max(100, vm.y + vm.alto - y_batalla)
                            if nuevo_alto >= 100:
                                vm.y = y_batalla
                                vm.alto = nuevo_alto
                        
                        vm.actualizar_rect()
                    
                    # Arrastrar/escalar ventana emulador
                    ve = self.ventana_emulador
                    if ve.arrastrando:
                        ve.x = x_batalla + ve.offset_x
                        ve.y = y_batalla + ve.offset_y
                        ve.actualizar_rect()
                    elif ve.escalando and ve.handle_activo:
                        if 'e' in ve.handle_activo:
                            nuevo_ancho = max(300, x_batalla - ve.x)
                            ve.ancho = nuevo_ancho
                        elif 'w' in ve.handle_activo:
                            nuevo_ancho = max(300, ve.x + ve.ancho - x_batalla)
                            if nuevo_ancho >= 300:
                                ve.x = x_batalla
                                ve.ancho = nuevo_ancho
                        
                        if 's' in ve.handle_activo:
                            nuevo_alto = max(200, y_batalla - ve.y)
                            ve.alto = nuevo_alto
                        elif 'n' in ve.handle_activo:
                            nuevo_alto = max(200, ve.y + ve.alto - y_batalla)
                            if nuevo_alto >= 200:
                                ve.y = y_batalla
                                ve.alto = nuevo_alto
                        
                        ve.actualizar_rect()
                    
                    # Arrastrar/escalar textos flotantes
                    for texto in self.textos_flotantes_demo:
                        if texto.arrastrando:
                            texto.x = x_batalla + texto.offset_x
                            texto.y = y_batalla + texto.offset_y
                            texto.actualizar_rect()
                        elif texto.escalando and texto.handle_activo:
                            # Escalar tamaño de fuente según distancia del handle
                            if 'e' in texto.handle_activo or 'se' in texto.handle_activo:
                                # Handle derecho o esquina inferior derecha
                                dist_x = x_batalla - texto.x
                                nuevo_tamano = max(10, min(100, int(dist_x / 3)))
                                texto.tamano = nuevo_tamano
                            elif 's' in texto.handle_activo:
                                # Handle inferior
                                dist_y = y_batalla - texto.y
                                nuevo_tamano = max(10, min(100, int(dist_y / 2)))
                                texto.tamano = nuevo_tamano
                    
                    # Arrastrar sprites
                    for sprite in self.sprites_colocados:
                        if sprite.arrastrando:
                            sprite.x = x_batalla + sprite.offset_x
                            sprite.y = y_batalla + sprite.offset_y
                            sprite.actualizar_rect()
                        
                        elif sprite.escalando and sprite.handle_activo:
                            # Escalado proporcional
                            if 'e' in sprite.handle_activo:  # Este (derecha)
                                nuevo_ancho = max(20, x_batalla - sprite.x)
                                sprite.ancho = nuevo_ancho
                            elif 'w' in sprite.handle_activo:  # Oeste (izquierda)
                                nuevo_ancho = max(20, sprite.x + sprite.ancho - x_batalla)
                                if nuevo_ancho >= 20:
                                    sprite.x = x_batalla
                                    sprite.ancho = nuevo_ancho
                            
                            if 's' in sprite.handle_activo:  # Sur (abajo)
                                nuevo_alto = max(20, y_batalla - sprite.y)
                                sprite.alto = nuevo_alto
                            elif 'n' in sprite.handle_activo:  # Norte (arriba)
                                nuevo_alto = max(20, sprite.y + sprite.alto - y_batalla)
                                if nuevo_alto >= 20:
                                    sprite.y = y_batalla
                                    sprite.alto = nuevo_alto
                            
                            sprite.actualizar_rect()
                    
                    # Actualizar hover
                    if not any(s.arrastrando or s.escalando for s in self.sprites_colocados) and not v.arrastrando and not v.escalando:
                        self.sprite_hover = self.get_sprite_en_posicion(x_batalla, y_batalla)
        
        return True
    
    def ejecutar(self):
        """Bucle principal"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área de batalla
            area_batalla = self.pantalla.subsurface((PANEL_ANCHO, 0, AREA_BATALLA_ANCHO, ALTO))
            self.dibujar_area_batalla(area_batalla)
            
            # Sprite fantasma durante drag
            if self.arrastrando_desde_panel and self.sprite_siendo_arrastrado:
                self.dibujar_sprite_fantasma(self.pantalla, pygame.mouse.get_pos())
            
            # Texto fantasma durante drag
            if self.arrastrando_desde_panel and self.texto_siendo_arrastrado:
                self.dibujar_texto_fantasma(self.pantalla, pygame.mouse.get_pos())
            
            # Panel lateral
            self.dibujar_panel_lateral(self.pantalla)
            
            # Botones en la derecha
            self.dibujar_botones_derecha(self.pantalla)
            
            # Paleta de colores
            if self.mostrar_paleta:
                self.dibujar_paleta_colores(self.pantalla)
            
            # Barra de estado
            self.dibujar_barra_estado(self.pantalla)
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()
        print("✓ Editor cerrado")

# ========================================
# EJECUTAR
# ========================================
if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════╗
║       EDITOR DE BATALLA - CodeVerso RPG               ║
║                                                        ║
║  Características:                                      ║
║  ✓ Secciones desplegables (Héroes/Monstruos)         ║
║  ✓ Drag & Drop desde panel a batalla                 ║
║  ✓ Escalado con esquinas                             ║
║  ✓ Ventana de comandos redimensionable               ║
║  ✓ Textos flotantes configurables                    ║
║  ✓ Paleta de colores para textos                     ║
║  ✓ Guardado/Carga de configuración                   ║
║                                                        ║
║  Controles:                                            ║
║  - Arrastra sprites desde panel a batalla             ║
║  - Arrastra esquinas para escalar                     ║
║  - T: Toggle textos flotantes                         ║
║  - Click en botones de color para editar              ║
║  - G: Guardar | L: Cargar | D: Duplicar              ║
║  - DEL: Eliminar | ESC: Salir/Cerrar paleta          ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    editor = EditorBatalla()
    editor.ejecutar()
