"""
========================================
EDITOR DE MAPAS PROFESIONAL - CodeVerso RPG
========================================
Editor completo con todas las funcionalidades solicitadas:
✓ Selector de mapas con preview
✓ Biblioteca de sprites (Héroes, Monstruos, NPCs, Cofres)
✓ Redimensionamiento arrastrando esquinas
✓ Sistema de capas y z-index
✓ Historial de uso de sprites
✓ Información de dónde se usa cada sprite
✓ Exportación JSON automática
✓ Grid con coordenadas
✓ Zoom y pan con cámara
"""

import pygame
import json
import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

# ========================================
# CONFIGURACIÓN
# ========================================
ANCHO = 1600
ALTO = 900
FPS = 60
PANEL_IZQUIERDO = 300
PANEL_DERECHO = 300
AREA_MAPA_ANCHO = ANCHO - PANEL_IZQUIERDO - PANEL_DERECHO

# Colores
COLOR_FONDO = (15, 15, 20)
COLOR_GRID = (35, 35, 45)
COLOR_SELECCION = (255, 215, 0)
COLOR_HOVER = (100, 200, 255)
COLOR_RESIZE_HANDLE = (255, 100, 100)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SEC = (180, 180, 180)
COLOR_PANEL = (25, 25, 35)
COLOR_PANEL_TITULO = (45, 45, 65)
COLOR_BOTON = (50, 50, 70)
COLOR_BOTON_HOVER = (70, 70, 100)
COLOR_BOTON_ACTIVO = (90, 140, 255)
COLOR_SCROLL = (60, 60, 80)

# ========================================
# CLASES AUXILIARES
# ========================================

class TipoSprite(Enum):
    """Tipos de sprites disponibles"""
    COFRE = "cofre"
    NPC = "npc"
    HEROE_MAPA = "heroe_mapa"
    HEROE_BATALLA = "heroe_batalla"
    MONSTRUO = "monstruo"
    DECORACION = "decoracion"
    ZONA_BATALLA = "zona_batalla"
    PORTAL = "portal"
    MURO = "muro"


class ModoEditor(Enum):
    """Modos de edición"""
    NORMAL = "normal"
    DIBUJAR_MUROS = "dibujar_muros"
    CREAR_PORTAL = "crear_portal"
    VISTA_BATALLA = "vista_batalla"


@dataclass
class SpriteInfo:
    """Información de un sprite en la biblioteca"""
    tipo: str
    id: str
    ruta_imagen: str
    ancho_default: int
    alto_default: int
    usos: List[str]  # Lista de mapas/contextos donde se usa
    descripcion: str = ""


@dataclass
class ObjetoMapa:
    """Objeto colocado en el mapa"""
    tipo: str
    id: str
    x: float
    y: float
    ancho: int
    alto: int
    z_index: int = 0
    sprite_ref: str = ""  # Referencia al sprite original
    datos_extra: dict = None
    
    def __post_init__(self):
        if self.datos_extra is None:
            self.datos_extra = {}
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.arrastrando = False
        self.redimensionando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar_rect(self):
        """Actualiza el rect con las coordenadas y tamaño actuales"""
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        """Verifica si un punto está dentro del objeto"""
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam_handle=10):
        """Retorna qué handle (esquina) está en el punto dado"""
        handles = {
            'nw': (self.x, self.y),
            'ne': (self.x + self.ancho, self.y),
            'sw': (self.x, self.y + self.alto),
            'se': (self.x + self.ancho, self.y + self.alto)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam_handle and abs(py - hy) <= tam_handle:
                return nombre
        return None
    
    def to_dict(self):
        """Convierte a diccionario para guardar"""
        return {
            "tipo": self.tipo,
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "z_index": self.z_index,
            "sprite_ref": self.sprite_ref,
            "datos_extra": self.datos_extra
        }


@dataclass
class Portal:
    """Portal de conexión entre mapas"""
    id: str
    mapa_origen: str
    x_origen: float
    y_origen: float
    mapa_destino: str
    x_destino: float
    y_destino: float
    ancho: int = 64
    alto: int = 64
    nombre: str = ""
    
    def to_dict(self):
        return {
            "id": self.id,
            "mapa_origen": self.mapa_origen,
            "x_origen": self.x_origen,
            "y_origen": self.y_origen,
            "mapa_destino": self.mapa_destino,
            "x_destino": self.x_destino,
            "y_destino": self.y_destino,
            "ancho": self.ancho,
            "alto": self.alto,
            "nombre": self.nombre
        }


@dataclass
class MuroDibujable:
    """Muro dibujado a mano (polígono de colisión)"""
    id: str
    puntos: List[Tuple[float, float]]  # Lista de puntos (x, y)
    color: Tuple[int, int, int] = (255, 0, 0)
    grosor: int = 5
    cerrado: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "puntos": self.puntos,
            "color": self.color,
            "grosor": self.grosor,
            "cerrado": self.cerrado
        }


class Boton:
    """Botón clickeable simple"""
    def __init__(self, x, y, ancho, alto, texto, callback=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.callback = callback
        self.hover = False
        self.activo = False
        self.fuente = pygame.font.Font(None, 20)
    
    def update(self, mouse_pos, click):
        """Actualiza estado del botón"""
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


class PanelScroll:
    """Panel con scroll vertical"""
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.scroll_y = 0
        self.contenido_alto = 0
        self.arrastrando_scroll = False
    
    def actualizar_scroll(self, mouse_y, delta_y):
        """Actualiza el scroll"""
        if delta_y != 0:
            self.scroll_y -= delta_y * 20
            self.scroll_y = max(0, min(self.scroll_y, max(0, self.contenido_alto - self.rect.height)))
    
    def get_rect_visible(self):
        """Retorna el rect visible considerando el scroll"""
        return pygame.Rect(self.rect.x, self.rect.y - self.scroll_y, self.rect.width, self.contenido_alto)


# ========================================
# EDITOR PRINCIPAL
# ========================================

class EditorMapaAvanzado:
    """Editor profesional de mapas con todas las funcionalidades"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Mapas Profesional - CodeVerso RPG")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        # Estado del editor
        self.mapa_actual = None
        self.carpeta_actual = "mundo"
        self.imagen_mapa = None
        self.imagen_mapa_escalada = None  # Para mostrar en el editor
        
        # Dimensiones REALES del juego (como aparecerá en el juego)
        self.ANCHO_JUEGO = 1280
        self.ALTO_JUEGO = 720
        self.ancho_mapa = 1280
        self.alto_mapa = 720
        
        # Cámara
        self.camara_x = 0
        self.camara_y = 0
        self.zoom = 1.0
        self.arrastrando_camara = False
        self.mouse_anterior = (0, 0)
        
        # Objetos del mapa
        self.objetos: List[ObjetoMapa] = []
        self.objeto_seleccionado: Optional[ObjetoMapa] = None
        self.objeto_hover: Optional[ObjetoMapa] = None
        
        # Portales
        self.portales: List[Portal] = []
        self.portal_temp = None  # Portal temporal mientras se crea
        self.creando_portal_origen = False
        self.creando_portal_destino = False
        
        # Muros dibujables
        self.muros: List[MuroDibujable] = []
        self.muro_actual: Optional[MuroDibujable] = None
        self.dibujando_muro = False
        self.grosor_muro = 5
        
        # Modo de edición
        self.modo_editor = ModoEditor.NORMAL
        
        # Configuración batalla
        self.num_heroes = 1
        self.num_monstruos = 1
        self.fondo_batalla_actual = None
        
        # ¡NUEVO! Sistema de Drag & Drop
        self.sprite_siendo_arrastrado = None  # SpriteInfo del sprite siendo arrastrado
        self.tipo_sprite_arrastrado = None  # "heroe" o "monstruo"
        self.offset_drag_x = 0
        self.offset_drag_y = 0
        self.arrastrando_desde_panel = False

        # --- NUEVO: Modos de dibujo y herramientas ---
        self.modo_dibujo = 'rectangulo'  # rectangulo | pincel | borrador
        self.pincel_tamano = 60
        self.pincel_min = 10
        self.pincel_max = 200
        self.dibujando_rectangulo = False
        self.rect_inicio = None
        self.mouse_izquierdo_presionado = False
        # Movimiento de muros dibujables (polígonos)
        self.muro_seleccionado = None
        self.muro_arrastrando = False
        self.muro_offset = (0, 0)
        
        # Biblioteca de sprites
        self.biblioteca_sprites: Dict[str, List[SpriteInfo]] = {}
        self.cargar_biblioteca_sprites()
        
        # Mapas disponibles
        self.mapas_disponibles = []
        self.cargar_lista_mapas()
        
        # UI
        self.modo_actual = "mapas"  # mapas, heroes, monstruos, npcs, cofres
        self.mostrar_grid = True
        self.cambios_sin_guardar = False
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        # Paneles scroll
        self.panel_izquierdo_scroll = PanelScroll(10, 60, PANEL_IZQUIERDO - 20, ALTO - 70)
        self.panel_derecho_scroll = PanelScroll(ANCHO - PANEL_DERECHO + 10, 60, PANEL_DERECHO - 20, ALTO - 70)
        
        # Botones de modo
        self.botones_modo = []
        self.crear_botones_modo()
        
        print("✓ Editor Avanzado Iniciado")
    
    def crear_botones_modo(self):
        """Crea botones para cambiar entre modos"""
        modos = ["Mapas", "Cofres", "NPCs", "Héroes", "Monstruos", "Portales", "Muros", "Batalla"]
        x_boton = 10
        y_boton = 10
        ancho_boton = (PANEL_IZQUIERDO - 30) // 3
        
        for i, modo in enumerate(modos):
            if i > 0 and i % 3 == 0:
                x_boton = 10
                y_boton += 45
            
            boton = Boton(
                x_boton, y_boton, ancho_boton, 35,
                modo,
                lambda m=modo.lower(): self.cambiar_modo(m)
            )
            self.botones_modo.append(boton)
            x_boton += ancho_boton + 5
    
    def cambiar_modo(self, modo):
        """Cambia el modo de visualización"""
        self.modo_actual = modo
        
        # Si estamos cambiando a modo muros o portales, actualizar modo_editor
        if modo == "muros":
            self.modo_editor = ModoEditor.DIBUJAR_MUROS
            self.dibujando_muro = False
            self.muro_actual = None
            print("🌀 Modo Muros: Dibuja con clicks en el mapa")
        elif modo == "portales":
            self.modo_editor = ModoEditor.CREAR_PORTAL
            self.portal_temp = None
            self.creando_portal_origen = False
            self.creando_portal_destino = False
            print("🌀 Modo Portales: Click para crear origen del portal")
        elif modo == "batalla":
            self.modo_editor = ModoEditor.VISTA_BATALLA
            # Cargar fondos de batalla si no están cargados
            if not hasattr(self, 'fondos_batalla'):
                self.cargar_fondos_batalla()
            print("🌀 Modo Batalla: Vista de configuración de batalla")
        else:
            self.modo_editor = ModoEditor.NORMAL
        
        print(f"Modo cambiado a: {modo}")
        for boton in self.botones_modo:
            boton.activo = (boton.texto.lower() == modo)
    
    def cargar_biblioteca_sprites(self):
        """Carga información de todos los sprites disponibles (recursivo)"""
        base_path = Path("assets/sprites")
        
        # Cargar cofres (buscar en "cofres y demas")
        self.biblioteca_sprites["cofres"] = []
        cofres_path = base_path / "cofres y demas"
        if cofres_path.exists():
            for archivo in cofres_path.rglob("*.png"):  # rglob = recursivo
                sprite = SpriteInfo(
                    tipo="cofre",
                    id=archivo.stem,
                    ruta_imagen=str(archivo).replace('\\', '/'),
                    ancho_default=64,
                    alto_default=64,
                    usos=[],
                    descripcion=f"Cofre: {archivo.stem}"
                )
                self.biblioteca_sprites["cofres"].append(sprite)
                print(f"  ✓ Cofre cargado: {archivo.stem} desde {archivo.parent.name}")
        
        # Cargar NPCs (preparado para cuando los tengamos)
        self.biblioteca_sprites["npcs"] = []
        npcs_path = base_path / "npcs"
        if npcs_path.exists():
            for archivo in npcs_path.rglob("*.png"):
                sprite = SpriteInfo(
                    tipo="npc",
                    id=archivo.stem,
                    ruta_imagen=str(archivo).replace('\\', '/'),
                    ancho_default=48,
                    alto_default=64,
                    usos=[],
                    descripcion=f"NPC: {archivo.stem}"
                )
                self.biblioteca_sprites["npcs"].append(sprite)
                print(f"  ✓ NPC cargado: {archivo.stem}")
        
        # Cargar Héroes (buscar en heroes/ recursivamente)
        self.biblioteca_sprites["héroes"] = []
        heroes_path = base_path / "heroes"
        if heroes_path.exists():
            for archivo in heroes_path.rglob("*.png"):  # Buscar recursivamente
                # Determinar si es de batalla o de mapa según carpeta
                tipo = "heroe_batalla" if "batalla" in str(archivo.parent).lower() else "heroe_mapa"
                sprite = SpriteInfo(
                    tipo=tipo,
                    id=archivo.stem,
                    ruta_imagen=str(archivo).replace('\\', '/'),
                    ancho_default=96,
                    alto_default=96,
                    usos=[],
                    descripcion=f"Héroe: {archivo.stem} ({archivo.parent.name})"
                )
                self.biblioteca_sprites["héroes"].append(sprite)
                print(f"  ✓ Héroe cargado: {archivo.stem} desde {archivo.parent.name}")
        
        # Cargar Monstruos (buscar en assets/sprites/monstruos/ recursivamente)
        self.biblioteca_sprites["monstruos"] = []
        monstruos_path = base_path / "monstruos"  # Ruta correcta
        if monstruos_path.exists():
            for archivo in monstruos_path.rglob("*.png"):  # Buscar recursivamente
                sprite = SpriteInfo(
                    tipo="monstruo",
                    id=archivo.stem,
                    ruta_imagen=str(archivo).replace('\\', '/'),
                    ancho_default=128,
                    alto_default=128,
                    usos=[],
                    descripcion=f"Monstruo: {archivo.stem}"
                )
                self.biblioteca_sprites["monstruos"].append(sprite)
                print(f"  ✓ Monstruo cargado: {archivo.stem}")
        else:
            print(f"  ⚠️ Carpeta de monstruos no encontrada: {monstruos_path}")

        
        # Cache de imágenes cargadas
        self.imagenes_sprites = {}
        for categoria, sprites in self.biblioteca_sprites.items():
            for sprite in sprites:
                try:
                    img = pygame.image.load(sprite.ruta_imagen).convert_alpha()
                    self.imagenes_sprites[sprite.ruta_imagen] = img
                except Exception as e:
                    print(f"  ⚠️ Error cargando {sprite.ruta_imagen}: {e}")
        
        print(f"✓ Biblioteca cargada: {sum(len(v) for v in self.biblioteca_sprites.values())} sprites")
    
    def cargar_lista_mapas(self):
        """Carga lista de mapas disponibles (recursivo)"""
        self.mapas_disponibles = []
        maps_path = Path("assets/maps")
        if maps_path.exists():
            # Buscar recursivamente en todas las subcarpetas
            for archivo in maps_path.rglob("*.jpg"):
                self.mapas_disponibles.append({
                    "nombre": archivo.stem,
                    "carpeta": archivo.parent.name,
                    "ruta": str(archivo).replace('\\', '/')
                })
                print(f"  ✓ Mapa JPG: {archivo.stem} ({archivo.parent.name})")
            
            # También buscar PNG
            for archivo in maps_path.rglob("*.png"):
                self.mapas_disponibles.append({
                    "nombre": archivo.stem,
                    "carpeta": archivo.parent.name,
                    "ruta": str(archivo).replace('\\', '/')
                })
                print(f"  ✓ Mapa PNG: {archivo.stem} ({archivo.parent.name})")
        print(f"✓ Mapas encontrados: {len(self.mapas_disponibles)}")
    
    def cargar_fondos_batalla(self):
        """Carga fondos de batalla desde assets/backgrounds/"""
        self.fondos_batalla = []
        backgrounds_path = Path("assets/backgrounds")
        
        if backgrounds_path.exists():
            for archivo in backgrounds_path.glob("*.png"):
                self.fondos_batalla.append({
                    "nombre": archivo.stem,
                    "ruta": str(archivo).replace('\\', '/')
                })
                print(f"  ✓ Fondo batalla: {archivo.stem}")
            
            # Cargar JPG también
            for archivo in backgrounds_path.glob("*.jpg"):
                self.fondos_batalla.append({
                    "nombre": archivo.stem,
                    "ruta": str(archivo).replace('\\', '/')
                })
                print(f"  ✓ Fondo batalla JPG: {archivo.stem}")
        
        print(f"✓ Fondos de batalla encontrados: {len(self.fondos_batalla)}")
        
        # Precargar cloud_batalla.png
        cloud_path = Path("assets/sprites/heroes/batalla/cloud_batalla.png")
        if cloud_path.exists():
            try:
                self.cloud_batalla_img = pygame.image.load(str(cloud_path)).convert_alpha()
                print("✓ cloud_batalla.png cargado")
            except Exception as e:
                self.cloud_batalla_img = None
                print(f"⚠️ Error cargando cloud_batalla.png: {e}")
        else:
            self.cloud_batalla_img = None
            print("⚠️ No se encontró cloud_batalla.png")
    
    def crear_thumbnail(self, ruta_imagen, ancho=70, alto=40):
        """Crea un thumbnail de una imagen"""
        try:
            img = pygame.image.load(ruta_imagen).convert()
            return pygame.transform.scale(img, (ancho, alto))
        except Exception as e:
            # Crear placeholder si no se puede cargar
            placeholder = pygame.Surface((ancho, alto))
            placeholder.fill((80, 80, 80))
            return placeholder
    
    def cargar_mapa(self, nombre_mapa, carpeta):
        """Carga un mapa para editar"""
        self.mapa_actual = nombre_mapa
        self.carpeta_actual = carpeta
        
        # Buscar la ruta correcta del mapa
        mapa_info = next((m for m in self.mapas_disponibles if m["nombre"] == nombre_mapa and m["carpeta"] == carpeta), None)
        
        if mapa_info:
            ruta_imagen = Path(mapa_info["ruta"])
            if ruta_imagen.exists():
                # Cargar imagen original
                img_original = pygame.image.load(str(ruta_imagen)).convert()
                
                # Usar dimensiones originales del mapa
                self.ancho_mapa = img_original.get_width()
                self.alto_mapa = img_original.get_height()
                
                # No escalar, usar imagen original
                self.imagen_mapa = img_original
                
                print(f"✓ Mapa cargado: {nombre_mapa}")
                print(f"  Dimensiones: {self.ancho_mapa}x{self.alto_mapa}")
            else:
                self.imagen_mapa = None
                print(f"⚠️ No se encontró imagen: {ruta_imagen}")
        else:
            # Intentar buscar manualmente
            for ext in ['.jpg', '.png', '.jpeg']:
                ruta_imagen = Path(f"assets/maps/{carpeta}/{nombre_mapa}{ext}")
                if ruta_imagen.exists():
                    img_original = pygame.image.load(str(ruta_imagen)).convert()
                    
                    # Usar dimensiones originales
                    self.ancho_mapa = img_original.get_width()
                    self.alto_mapa = img_original.get_height()
                    
                    # No escalar, usar imagen original
                    self.imagen_mapa = img_original
                    
                    print(f"✓ Mapa cargado: {nombre_mapa}")
                    print(f"  Dimensiones: {self.ancho_mapa}x{self.alto_mapa}")
                    break
            else:
                self.imagen_mapa = None
                print(f"⚠️ No se encontró imagen del mapa: {nombre_mapa}")
        
        # Cargar objetos del JSON
        self.cargar_objetos_mapa()
        
        # Resetear cámara
        self.camara_x = 0
        self.camara_y = 0
        self.zoom = 1.0
        
        self.mostrar_mensaje(f"Mapa cargado: {nombre_mapa}")
    
    def cargar_objetos_mapa(self):
        """Carga objetos existentes del JSON del mapa"""
        self.objetos = []
        
        ruta_json = Path(f"src/database/mapas/{self.carpeta_actual}/{self.mapa_actual}.json")
        if not ruta_json.exists():
            print(f"⚠️ No existe JSON para este mapa: {ruta_json}")
            return
        
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar cofres
            for cofre in data.get("cofres", []):
                obj = ObjetoMapa(
                    tipo="cofre",
                    id=cofre.get("id", "cofre_1"),
                    x=cofre.get("x", 0),
                    y=cofre.get("y", 0),
                    ancho=cofre.get("ancho", 64),
                    alto=cofre.get("alto", 64),
                    z_index=cofre.get("z_index", 0),
                    sprite_ref=cofre.get("sprite_ref", ""),
                    datos_extra=cofre
                )
                self.objetos.append(obj)
            
            # Cargar NPCs
            for npc in data.get("npcs", []):
                obj = ObjetoMapa(
                    tipo="npc",
                    id=npc.get("id", "npc_1"),
                    x=npc.get("x", 0),
                    y=npc.get("y", 0),
                    ancho=npc.get("ancho", 48),
                    alto=npc.get("alto", 64),
                    z_index=npc.get("z_index", 1),
                    sprite_ref=npc.get("sprite_ref", ""),
                    datos_extra=npc
                )
                self.objetos.append(obj)
            
            print(f"✓ Cargados {len(self.objetos)} objetos del mapa")
        
        except Exception as e:
            print(f"❌ Error cargando objetos: {e}")
    
    def guardar_mapa(self):
        """Guarda el mapa actual"""
        if not self.mapa_actual:
            self.mostrar_mensaje("⚠️ No hay mapa cargado")
            return False
        
        # Organizar por tipo
        cofres = []
        npcs = []
        zonas_batalla = []
        
        for obj in self.objetos:
            datos = obj.to_dict()
            if obj.tipo == "cofre":
                cofres.append(datos)
            elif obj.tipo == "npc":
                npcs.append(datos)
            elif obj.tipo == "zona_batalla":
                zonas_batalla.append(datos)
        
        # Crear estructura JSON
        data = {
            "nombre": self.mapa_actual,
            "carpeta": self.carpeta_actual,
            "cofres": cofres,
            "npcs": npcs,
            "zonas_batalla": zonas_batalla
        }
        
        # Guardar
        try:
            ruta_json = Path(f"src/database/mapas/{self.carpeta_actual}/{self.mapa_actual}.json")
            ruta_json.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.cambios_sin_guardar = False
            self.mostrar_mensaje(f"✓ Guardado: {len(self.objetos)} objetos")
            print(f"✓ Mapa guardado: {ruta_json}")
            return True
        
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {str(e)}")
            print(f"❌ Error guardando: {e}")
            return False
    
    def mostrar_mensaje(self, texto):
        """Muestra un mensaje temporal"""
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
        print(texto)
    
    def crear_objeto(self, tipo, sprite_ref=""):
        """Crea un nuevo objeto en el mapa"""
        # Generar ID único
        num = len([o for o in self.objetos if o.tipo == tipo]) + 1
        nuevo_id = f"{tipo}_{num}"
        
        # Posición en centro de la vista
        x = self.camara_x + AREA_MAPA_ANCHO // 2
        y = self.camara_y + ALTO // 2
        
        obj = ObjetoMapa(
            tipo=tipo,
            id=nuevo_id,
            x=x,
            y=y,
            ancho=64,
            alto=64,
            z_index=len(self.objetos),
            sprite_ref=sprite_ref
        )
        
        self.objetos.append(obj)
        self.objeto_seleccionado = obj
        self.cambios_sin_guardar = True
        self.mostrar_mensaje(f"✓ Creado: {nuevo_id}")
    
    def explorar_y_añadir_sprite(self, categoria):
        """Abre diálogo para seleccionar y añadir un nuevo sprite"""
        import shutil
        
        # ¡NUEVO! Normalizar categoría para evitar confusiones
        categoria_normalizada = categoria.lower().strip()
        print(f"🔍 DEBUG explorar_y_añadir_sprite:")
        print(f"   Categoría recibida: '{categoria}'")
        print(f"   Categoría normalizada: '{categoria_normalizada}'")
        
        # Crear ventana tkinter oculta para el diálogo
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Abrir diálogo de selección de archivo
        archivo = filedialog.askopenfilename(
            title=f"Seleccionar sprite de {categoria}",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos", "*.*")]
        )
        
        root.destroy()
        
        if not archivo:
            print("   ✗ Diálogo cancelado")
            return  # Cancelado
        
        archivo_path = Path(archivo)
        print(f"   Archivo seleccionado: {archivo_path.name}")
        
        # Determinar carpeta destino según categoría
        carpetas_destino = {
            "cofres": Path("assets/sprites/cofres y demas"),
            "npcs": Path("assets/sprites/npcs"),
            "heroes": Path("assets/sprites/heroes/batalla"),
            "monstruos": Path("assets/sprites/monstruos")
        }
        
        carpeta_destino = carpetas_destino.get(categoria_normalizada)
        if not carpeta_destino:
            self.mostrar_mensaje(f"❌ Categoría no válida: {categoria}")
            print(f"   ❌ Categorías disponibles: {list(carpetas_destino.keys())}")
            return
        
        print(f"   Carpeta destino: {carpeta_destino}")
        
        # Crear carpeta si no existe
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Copiar archivo
        destino = carpeta_destino / archivo_path.name
        try:
            shutil.copy2(archivo, destino)
            self.mostrar_mensaje(f"✓ Sprite añadido: {archivo_path.name}")
            # Recargar biblioteca
            self.cargar_biblioteca_sprites()
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error copiando sprite: {e}")
    
    def crear_objeto_desde_sprite(self, sprite_info):
        """Crea un nuevo objeto desde un SpriteInfo"""
        # Generar ID único
        num = len([o for o in self.objetos if o.tipo == sprite_info.tipo]) + 1
        nuevo_id = f"{sprite_info.tipo}_{num}"
        
        # Posición en centro de la vista
        x = self.camara_x + AREA_MAPA_ANCHO // 2
        y = self.camara_y + ALTO // 2
        
        obj = ObjetoMapa(
            tipo=sprite_info.tipo,
            id=nuevo_id,
            x=x,
            y=y,
            ancho=sprite_info.ancho_default,
            alto=sprite_info.alto_default,
            z_index=len(self.objetos),
            sprite_ref=sprite_info.id  # Usar el ID del sprite como referencia
        )
        
        self.objetos.append(obj)
        self.objeto_seleccionado = obj
        self.cambios_sin_guardar = True
        self.mostrar_mensaje(f"✓ Creado: {nuevo_id} ({sprite_info.id})")
    
    def guardar_configuracion_batalla(self):
        """Guarda la configuración de batalla actual (sprites y posiciones)"""
        if not self.modo_actual == "batalla":
            return
        
        config = {
            "fondo": self.fondo_batalla_actual,
            "num_heroes": self.num_heroes,
            "num_monstruos": self.num_monstruos,
            "sprites": []
        }
        
        # Guardar solo sprites de batalla
        for obj in self.objetos:
            if obj.tipo in ["heroe_batalla", "monstruo"]:
                config["sprites"].append({
                    "tipo": obj.tipo,
                    "id": obj.id,
                    "sprite_ref": obj.sprite_ref,
                    "x": obj.x,
                    "y": obj.y,
                    "ancho": obj.ancho,
                    "alto": obj.alto
                })
        
        # Guardar en archivo
        config_path = Path("src/database/batalla_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.mostrar_mensaje("✓ Configuración de batalla guardada")
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error guardando: {e}")
    
    def cargar_configuracion_batalla(self):
        """Carga una configuración de batalla guardada"""
        config_path = Path("src/database/batalla_config.json")
        
        if not config_path.exists():
            self.mostrar_mensaje("⚠️ No hay configuración guardada")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Limpiar sprites de batalla actuales
            self.objetos = [o for o in self.objetos if o.tipo not in ["heroe_batalla", "monstruo"]]
            
            # Cargar configuración
            self.fondo_batalla_actual = config.get("fondo")
            self.num_heroes = config.get("num_heroes", 1)
            self.num_monstruos = config.get("num_monstruos", 1)
            
            # Recrear sprites
            for sprite_data in config.get("sprites", []):
                obj = ObjetoMapa(
                    tipo=sprite_data["tipo"],
                    id=sprite_data["id"],
                    x=sprite_data["x"],
                    y=sprite_data["y"],
                    ancho=sprite_data["ancho"],
                    alto=sprite_data["alto"],
                    z_index=len(self.objetos),
                    sprite_ref=sprite_data.get("sprite_ref", "")
                )
                self.objetos.append(obj)
            
            self.mostrar_mensaje(f"✓ Configuración cargada: {len(config['sprites'])} sprites")
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error cargando: {e}")
    

    
    def eliminar_objeto(self, objeto):
        """Elimina un objeto"""
        if objeto in self.objetos:
            self.objetos.remove(objeto)
            self.objeto_seleccionado = None
            self.cambios_sin_guardar = True
            self.mostrar_mensaje(f"✓ Eliminado: {objeto.id}")
    
    def duplicar_objeto(self, objeto):
        """Duplica un objeto"""
        if not objeto:
            return
        
        num = len([o for o in self.objetos if o.tipo == objeto.tipo]) + 1
        nuevo_id = f"{objeto.tipo}_{num}"
        
        obj_nuevo = ObjetoMapa(
            tipo=objeto.tipo,
            id=nuevo_id,
            x=objeto.x + 50,
            y=objeto.y + 50,
            ancho=objeto.ancho,
            alto=objeto.alto,
            z_index=len(self.objetos),
            sprite_ref=objeto.sprite_ref,
            datos_extra=objeto.datos_extra.copy()
        )
        
        self.objetos.append(obj_nuevo)
        self.objeto_seleccionado = obj_nuevo
        self.cambios_sin_guardar = True
        self.mostrar_mensaje(f"✓ Duplicado: {nuevo_id}")
    
    def obtener_objeto_en_posicion(self, x_pantalla, y_pantalla):
        """Obtiene objeto en posición de pantalla"""
        # Convertir a coordenadas del mundo considerando zoom
        mundo_x = x_pantalla / self.zoom + self.camara_x
        mundo_y = y_pantalla / self.zoom + self.camara_y
        
        # Buscar de atrás hacia adelante (objetos superiores primero)
        for obj in reversed(self.objetos):
            if obj.contiene_punto(mundo_x, mundo_y):
                return obj
        return None
    
    def dibujar_grid(self, surface):
        """Dibuja grid de referencia con zoom"""
        if not self.mostrar_grid:
            return
        
        grid_size = int(50 * self.zoom)
        if grid_size < 5:  # No dibujar grid si es muy pequeño
            return
        
        offset_x = int(-self.camara_x * self.zoom) % grid_size
        offset_y = int(-self.camara_y * self.zoom) % grid_size
        
        # Líneas verticales
        for x in range(offset_x, AREA_MAPA_ANCHO, grid_size):
            pygame.draw.line(surface, COLOR_GRID, 
                           (PANEL_IZQUIERDO + x, 0), 
                           (PANEL_IZQUIERDO + x, ALTO), 1)
        
        # Líneas horizontales
        for y in range(offset_y, ALTO, grid_size):
            pygame.draw.line(surface, COLOR_GRID, 
                           (PANEL_IZQUIERDO, y), 
                           (ANCHO - PANEL_DERECHO, y), 1)
    
    def dibujar_objeto(self, surface, obj):
        """Dibuja un objeto en el área del mapa"""
        # Convertir coordenadas del mundo a pantalla con zoom
        x_pantalla = (obj.x - self.camara_x) * self.zoom + PANEL_IZQUIERDO
        y_pantalla = (obj.y - self.camara_y) * self.zoom
        
        # Verificar si está visible
        ancho_zoom = int(obj.ancho * self.zoom)
        alto_zoom = int(obj.alto * self.zoom)
        
        if (x_pantalla + ancho_zoom < PANEL_IZQUIERDO or 
            x_pantalla > ANCHO - PANEL_DERECHO or
            y_pantalla + alto_zoom < 0 or 
            y_pantalla > ALTO):
            return
        
        # Intentar cargar sprite real si existe
        sprite_dibujado = False
        if obj.sprite_ref:
            # Primero intentar con la ruta completa
            if obj.sprite_ref in self.imagenes_sprites:
                img = self.imagenes_sprites[obj.sprite_ref]
                img_escalada = pygame.transform.scale(img, (ancho_zoom, alto_zoom))
                surface.blit(img_escalada, (x_pantalla, y_pantalla))
                sprite_dibujado = True
            else:
                # Buscar por ID si no es una ruta
                for categoria, sprites in self.biblioteca_sprites.items():
                    for sprite in sprites:
                        if sprite.id == obj.sprite_ref or sprite.ruta_imagen == obj.sprite_ref:
                            if sprite.ruta_imagen in self.imagenes_sprites:
                                img = self.imagenes_sprites[sprite.ruta_imagen]
                                img_escalada = pygame.transform.scale(img, (ancho_zoom, alto_zoom))
                                surface.blit(img_escalada, (x_pantalla, y_pantalla))
                                sprite_dibujado = True
                                break
                    if sprite_dibujado:
                        break
        
        # Si no se dibujó el sprite, dibujar rectángulo de color
        if not sprite_dibujado:
            # Color según tipo
            colores = {
                "cofre": (139, 69, 19),
                "npc": (0, 150, 255),
                "zona_batalla": (255, 50, 50),
                "heroe_mapa": (50, 255, 50),
                "heroe_batalla": (50, 200, 50),
                "monstruo_batalla": (255, 50, 150),
                "muro": (100, 100, 100),
                "portal": (255, 200, 0)
            }
            color_base = colores.get(obj.tipo, (128, 128, 128))
            
            # Dibujar rectángulo semitransparente
            rect_superficie = pygame.Surface((ancho_zoom, alto_zoom))
            rect_superficie.set_alpha(120)
            rect_superficie.fill(color_base)
            surface.blit(rect_superficie, (x_pantalla, y_pantalla))
        
        # Borde
        rect = pygame.Rect(int(x_pantalla), int(y_pantalla), ancho_zoom, alto_zoom)
        
        if obj == self.objeto_seleccionado:
            pygame.draw.rect(surface, COLOR_SELECCION, rect, 3)
            # Dibujar handles de redimensionamiento
            self.dibujar_handles(surface, obj, x_pantalla, y_pantalla, ancho_zoom, alto_zoom)
        elif obj == self.objeto_hover:
            pygame.draw.rect(surface, COLOR_HOVER, rect, 2)
        else:
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)
        
        # Texto con ID (solo si zoom > 0.5)
        if self.zoom > 0.5:
            texto = self.fuente_pequena.render(f"{obj.tipo}: {obj.id}", True, COLOR_TEXTO)
            # Fondo para el texto
            fondo_texto = pygame.Surface((texto.get_width() + 10, texto.get_height() + 4))
            fondo_texto.set_alpha(180)
            fondo_texto.fill((0, 0, 0))
            surface.blit(fondo_texto, (x_pantalla + 2, y_pantalla + 2))
            surface.blit(texto, (x_pantalla + 5, y_pantalla + 4))
            
            # Dimensiones
            dim_texto = self.fuente_pequena.render(f"{obj.ancho}x{obj.alto}", True, COLOR_TEXTO)
            fondo_dim = pygame.Surface((dim_texto.get_width() + 10, dim_texto.get_height() + 4))
            fondo_dim.set_alpha(180)
            fondo_dim.fill((0, 0, 0))
            surface.blit(fondo_dim, (x_pantalla + 2, y_pantalla + alto_zoom - 22))
            surface.blit(dim_texto, (x_pantalla + 5, y_pantalla + alto_zoom - 20))
    
    def dibujar_handles(self, surface, obj, x_pantalla, y_pantalla, ancho_zoom, alto_zoom):
        """Dibuja handles de redimensionamiento con zoom"""
        
        tam_handle = max(6, int(8 * self.zoom))  # Ajustar tamaño del handle con zoom
        handles = [
            (x_pantalla, y_pantalla),  # NW
            (x_pantalla + ancho_zoom, y_pantalla),  # NE
            (x_pantalla, y_pantalla + alto_zoom),  # SW
            (x_pantalla + ancho_zoom, y_pantalla + alto_zoom),  # SE
        ]
        
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_RESIZE_HANDLE, (int(hx), int(hy)), tam_handle)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam_handle, 2)
    
    def dibujar_panel_izquierdo(self, surface):
        """Dibuja panel izquierdo con opciones"""
        # Fondo del panel
        pygame.draw.rect(surface, COLOR_PANEL, (0, 0, PANEL_IZQUIERDO, ALTO))
        
        # Título
        y = 10
        
        # Dibujar botones de modo
        for boton in self.botones_modo:
            boton.draw(surface)
        
        y = 100
        
        # Contenido según el modo
        if self.modo_actual == "mapas":
            self.dibujar_lista_mapas(surface, 10, y)
        elif self.modo_actual == "cofres":
            self.dibujar_lista_sprites(surface, 10, y, "cofres")
        elif self.modo_actual == "npcs":
            self.dibujar_lista_sprites(surface, 10, y, "npcs")
        elif self.modo_actual == "héroes":
            self.dibujar_lista_sprites(surface, 10, y, "héroes")
        elif self.modo_actual == "monstruos":
            self.dibujar_lista_sprites(surface, 10, y, "monstruos")
        elif self.modo_actual == "portales":
            self.dibujar_modo_portales(surface, 10, y)
        elif self.modo_actual == "batalla":
            self.dibujar_modo_batalla(surface, 10, y)
    
    def dibujar_lista_mapas(self, surface, x, y):
        """Dibuja lista de mapas disponibles"""
        texto = self.fuente.render("Mapas Disponibles:", True, COLOR_TEXTO)
        surface.blit(texto, (x, y))
        y += 35
        
        # Botón de actualizar
        rect_actualizar = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 25)
        color = COLOR_BOTON_HOVER if rect_actualizar.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50)
        pygame.draw.rect(surface, color, rect_actualizar, border_radius=3)
        texto = self.fuente_pequena.render("↻ Actualizar Lista", True, COLOR_TEXTO)
        surface.blit(texto, (x + 5, y + 5))
        y += 35
        
        for mapa_info in self.mapas_disponibles[:15]:  # Mostrar hasta 15
            nombre = mapa_info["nombre"]
            carpeta = mapa_info["carpeta"]
            
            # Botón para cargar mapa
            rect_boton = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 30)
            es_actual = (self.mapa_actual == nombre and self.carpeta_actual == carpeta)
            if es_actual:
                color = COLOR_BOTON_ACTIVO
            else:
                color = COLOR_BOTON_HOVER if rect_boton.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            pygame.draw.rect(surface, color, rect_boton, border_radius=3)
            
            texto_nombre = self.fuente_pequena.render(f"{nombre}", True, COLOR_TEXTO)
            texto_carpeta = self.fuente_pequena.render(f"({carpeta})", True, COLOR_TEXTO_SEC)
            surface.blit(texto_nombre, (x + 5, y + 3))
            surface.blit(texto_carpeta, (x + 5, y + 16))
            
            y += 35
    
    def dibujar_lista_sprites(self, surface, x, y, categoria):
        """Dibuja lista de sprites de una categoría"""
        texto = self.fuente.render(f"{categoria.capitalize()}:", True, COLOR_TEXTO)
        surface.blit(texto, (x, y))
        y += 35
        
        # Botón de actualizar
        ancho_boton = (PANEL_IZQUIERDO - 30) // 2
        rect_actualizar = pygame.Rect(x, y, ancho_boton, 25)
        color = COLOR_BOTON_HOVER if rect_actualizar.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50)
        pygame.draw.rect(surface, color, rect_actualizar, border_radius=3)
        texto_act = self.fuente_pequena.render("↻ Actualizar", True, COLOR_TEXTO)
        surface.blit(texto_act, (x + 5, y + 5))
        
        # Botón de explorar/añadir
        rect_explorar = pygame.Rect(x + ancho_boton + 10, y, ancho_boton, 25)
        color_exp = COLOR_BOTON_HOVER if rect_explorar.collidepoint(pygame.mouse.get_pos()) else (50, 100, 200)
        pygame.draw.rect(surface, color_exp, rect_explorar, border_radius=3)
        texto_exp = self.fuente_pequena.render("+ Añadir", True, COLOR_TEXTO)
        surface.blit(texto_exp, (x + ancho_boton + 15, y + 5))
        
        y += 35
        
        sprites = self.biblioteca_sprites.get(categoria, [])
        if len(sprites) == 0:
            texto_vacio = self.fuente_pequena.render("(No hay sprites)", True, COLOR_TEXTO_SEC)
            surface.blit(texto_vacio, (x + 5, y))
            return
        
        for sprite in sprites[:10]:  # Limitar a 10 por ahora
            # Botón para añadir sprite
            rect_boton = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 30)
            color = COLOR_BOTON_HOVER if rect_boton.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            pygame.draw.rect(surface, color, rect_boton, border_radius=3)
            
            # Nombre del sprite
            texto = self.fuente_pequena.render(sprite.id[:25], True, COLOR_TEXTO)
            surface.blit(texto, (x + 5, y + 3))
            
            # Descripción/carpeta
            if sprite.descripcion:
                desc = sprite.descripcion.split('(')[-1].replace(')', '') if '(' in sprite.descripcion else ""
                if desc:
                    texto_desc = self.fuente_pequena.render(f"({desc[:15]})", True, COLOR_TEXTO_SEC)
                    surface.blit(texto_desc, (x + 5, y + 16))
            
            y += 35
    
    def dibujar_modo_portales(self, surface, x, y):
        """Dibuja interfaz del modo portales con thumbnails de mapas"""
        texto = self.fuente.render("Portales:", True, COLOR_TEXTO)
        surface.blit(texto, (x, y))
        y += 30
        
        instruccion = self.fuente_pequena.render("Selecciona mapa destino:", True, COLOR_TEXTO_SEC)
        surface.blit(instruccion, (x, y))
        y += 25
        
        # Lista de mapas con thumbnails
        for i, mapa_info in enumerate(self.mapas_disponibles[:8]):
            nombre = mapa_info["nombre"]
            carpeta = mapa_info["carpeta"]
            ruta = mapa_info["ruta"]
            
            # Área del botón
            rect_boton = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 50)
            color = COLOR_BOTON_HOVER if rect_boton.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            pygame.draw.rect(surface, color, rect_boton, border_radius=3)
            
            # Thumbnail del mapa
            try:
                thumb = self.crear_thumbnail(ruta, 70, 40)
                surface.blit(thumb, (x + 5, y + 5))
            except:
                pass
            
            # Nombre del mapa
            texto_nombre = self.fuente_pequena.render(nombre[:15], True, COLOR_TEXTO)
            surface.blit(texto_nombre, (x + 85, y + 8))
            
            # Carpeta
            texto_carpeta = self.fuente_pequena.render(f"({carpeta})", True, COLOR_TEXTO_SEC)
            surface.blit(texto_carpeta, (x + 85, y + 26))
            
            y += 55
    
    def dibujar_modo_batalla(self, surface, x, y):
        """Dibuja interfaz del modo batalla"""
        texto = self.fuente.render("Vista Batalla:", True, COLOR_TEXTO)
        surface.blit(texto, (x, y))
        y += 30
        
        # Controles de cantidad
        texto_config = self.fuente_pequena.render("Configuración:", True, COLOR_TEXTO_SEC)
        surface.blit(texto_config, (x, y))
        y += 25
        
        # Cantidad de héroes (1-4)
        texto_heroes_cant = self.fuente_pequena.render(f"Héroes: {self.num_heroes}", True, (100, 255, 100))
        surface.blit(texto_heroes_cant, (x, y))
        y += 20
        
        for i in range(1, 5):
            rect_num = pygame.Rect(x + (i-1) * 30, y, 25, 25)
            color = COLOR_BOTON_ACTIVO if i == self.num_heroes else COLOR_BOTON
            if rect_num.collidepoint(pygame.mouse.get_pos()):
                color = COLOR_BOTON_HOVER
            pygame.draw.rect(surface, color, rect_num, border_radius=3)
            texto_num = self.fuente_pequena.render(str(i), True, COLOR_TEXTO)
            surface.blit(texto_num, (x + (i-1) * 30 + 8, y + 5))
        y += 35
        
        # Cantidad de monstruos (1-5)
        texto_mons_cant = self.fuente_pequena.render(f"Monstruos: {self.num_monstruos}", True, (255, 100, 100))
        surface.blit(texto_mons_cant, (x, y))
        y += 20
        
        for i in range(1, 6):
            rect_num = pygame.Rect(x + (i-1) * 30, y, 25, 25)
            color = COLOR_BOTON_ACTIVO if i == self.num_monstruos else COLOR_BOTON
            if rect_num.collidepoint(pygame.mouse.get_pos()):
                color = COLOR_BOTON_HOVER
            pygame.draw.rect(surface, color, rect_num, border_radius=3)
            texto_num = self.fuente_pequena.render(str(i), True, COLOR_TEXTO)
            surface.blit(texto_num, (x + (i-1) * 30 + 8, y + 5))
        y += 40
        
        # Sección Fondos
        texto_fondos = self.fuente_pequena.render("Fondos de batalla:", True, (100, 200, 255))
        surface.blit(texto_fondos, (x, y))
        y += 25
        
        if hasattr(self, 'fondos_batalla'):
            for i, fondo in enumerate(self.fondos_batalla[:3]):
                rect_fondo = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 45)
                es_actual = (self.fondo_batalla_actual == fondo["nombre"])
                color = COLOR_BOTON_ACTIVO if es_actual else (COLOR_BOTON_HOVER if rect_fondo.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON)
                pygame.draw.rect(surface, color, rect_fondo, border_radius=3)
                
                # Thumbnail
                try:
                    thumb = self.crear_thumbnail(fondo["ruta"], 60, 35)
                    surface.blit(thumb, (x + 5, y + 5))
                except:
                    pass
                
                # Nombre
                texto_nombre = self.fuente_pequena.render(fondo["nombre"][:15], True, COLOR_TEXTO)
                surface.blit(texto_nombre, (x + 75, y + 15))
                
                y += 50
        
        y += 10
        
        # Botones de Guardar/Cargar configuración
        rect_guardar = pygame.Rect(x, y, (PANEL_IZQUIERDO - 30) // 2, 35)
        color_guardar = (50, 200, 50) if rect_guardar.collidepoint(pygame.mouse.get_pos()) else (30, 150, 30)
        pygame.draw.rect(surface, color_guardar, rect_guardar, border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), rect_guardar, 2, border_radius=3)
        texto_guardar = self.fuente_pequena.render("Guardar", True, COLOR_TEXTO)
        surface.blit(texto_guardar, (x + 15, y + 10))
        
        rect_cargar = pygame.Rect(x + (PANEL_IZQUIERDO - 30) // 2 + 10, y, (PANEL_IZQUIERDO - 30) // 2, 35)
        color_cargar = (50, 150, 200) if rect_cargar.collidepoint(pygame.mouse.get_pos()) else (30, 100, 150)
        pygame.draw.rect(surface, color_cargar, rect_cargar, border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), rect_cargar, 2, border_radius=3)
        texto_cargar = self.fuente_pequena.render("Cargar", True, COLOR_TEXTO)
        surface.blit(texto_cargar, (x + (PANEL_IZQUIERDO - 30) // 2 + 20, y + 10))
        
        y += 45
        
        # Sección Héroes - ARRASTRABLES
        texto_heroes = self.fuente_pequena.render("Héroes (arrastra al mapa):", True, (50, 255, 50))
        surface.blit(texto_heroes, (x, y))
        y += 25
        
        heroes_batalla = [s for s in self.biblioteca_sprites.get("héroes", []) if "batalla" in s.ruta_imagen.lower()]
        for i, sprite in enumerate(heroes_batalla[:3]):
            rect_sprite = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 30)
            
            # Highlight si es el sprite siendo arrastrado
            if self.sprite_siendo_arrastrado == sprite:
                color = (100, 255, 150)
            else:
                color = COLOR_BOTON_HOVER if rect_sprite.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            
            pygame.draw.rect(surface, color, rect_sprite, border_radius=3)
            
            texto_nombre = self.fuente_pequena.render(sprite.id[:20], True, COLOR_TEXTO)
            surface.blit(texto_nombre, (x + 5, y + 8))
            
            # Icono de arrastre
            icono = self.fuente_pequena.render("⋮⋮", True, COLOR_TEXTO_SEC)
            surface.blit(icono, (x + PANEL_IZQUIERDO - 35, y + 8))
            
            y += 35
        
            y += 10        # Sección Monstruos - ARRASTRABLES
        texto_monstruos = self.fuente_pequena.render("Monstruos (arrastra al mapa):", True, (255, 100, 100))
        surface.blit(texto_monstruos, (x, y))
        y += 25
        
        # Mostrar TODOS los monstruos arrastrables
        monstruos = self.biblioteca_sprites.get("monstruos", [])
        if len(monstruos) == 0:
            texto_vacio = self.fuente_pequena.render("(No hay monstruos)", True, COLOR_TEXTO_SEC)
            surface.blit(texto_vacio, (x + 5, y))
        else:
            # Mostrar hasta 10 monstruos arrastrables
            for i, sprite in enumerate(monstruos[:10]):
                rect_sprite = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 30)
                
                # Highlight si es el sprite siendo arrastrado
                if self.sprite_siendo_arrastrado == sprite:
                    color = (255, 150, 150)
                else:
                    color = COLOR_BOTON_HOVER if rect_sprite.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
                
                pygame.draw.rect(surface, color, rect_sprite, border_radius=3)
                
                # Nombre del monstruo
                texto_nombre = self.fuente_pequena.render(sprite.id[:20], True, COLOR_TEXTO)
                surface.blit(texto_nombre, (x + 5, y + 8))
                
                # Icono de arrastre
                icono = self.fuente_pequena.render("⋮⋮", True, COLOR_TEXTO_SEC)
                surface.blit(icono, (x + PANEL_IZQUIERDO - 35, y + 8))
                
                y += 35
    
    def dibujar_panel_derecho(self, surface):
        """Dibuja panel derecho con propiedades"""
        # Fondo del panel
        pygame.draw.rect(surface, COLOR_PANEL, (ANCHO - PANEL_DERECHO, 0, PANEL_DERECHO, ALTO))
        
        x = ANCHO - PANEL_DERECHO + 10
        y = 10
        
        # Título
        texto = self.fuente.render("Propiedades", True, COLOR_TEXTO)
        surface.blit(texto, (x, y))
        y += 35
        
        # Info del objeto seleccionado
        if self.objeto_seleccionado:
            obj = self.objeto_seleccionado
            
            info = [
                f"ID: {obj.id}",
                f"Tipo: {obj.tipo}",
                f"Pos: ({int(obj.x)}, {int(obj.y)})",
                f"Tamaño: {obj.ancho}x{obj.alto}",
                f"Z-Index: {obj.z_index}",
            ]
            
            if obj.sprite_ref:
                info.append(f"Sprite: {obj.sprite_ref}")
            
            for linea in info:
                texto = self.fuente_pequena.render(linea, True, COLOR_TEXTO)
                surface.blit(texto, (x, y))
                y += 25
            
            # Botones de acción
            y += 20
            boton_duplicar = pygame.Rect(x, y, PANEL_DERECHO - 40, 35)
            color = COLOR_BOTON_HOVER if boton_duplicar.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            pygame.draw.rect(surface, color, boton_duplicar, border_radius=3)
            texto = self.fuente.render("Duplicar (D)", True, COLOR_TEXTO)
            surface.blit(texto, (x + 10, y + 8))
            
            y += 45
            boton_eliminar = pygame.Rect(x, y, PANEL_DERECHO - 40, 35)
            color = COLOR_BOTON_HOVER if boton_eliminar.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
            pygame.draw.rect(surface, (200, 50, 50), boton_eliminar, border_radius=3)
            texto = self.fuente.render("Eliminar (DEL)", True, COLOR_TEXTO)
            surface.blit(texto, (x + 10, y + 8))
        
        else:
            texto = self.fuente_pequena.render("Ningún objeto seleccionado", True, COLOR_TEXTO_SEC)
            surface.blit(texto, (x, y))
    
    def dibujar_barra_estado(self, surface):
        """Dibuja barra de estado en la parte inferior"""
        barra_alto = 30
        pygame.draw.rect(surface, COLOR_PANEL_TITULO, (0, ALTO - barra_alto, ANCHO, barra_alto))
        
        # Info general
        if self.mapa_actual:
            texto = f"Mapa: {self.mapa_actual} | Objetos: {len(self.objetos)} | Cámara: ({int(self.camara_x)}, {int(self.camara_y)}) | Zoom: {self.zoom:.2f}"
        else:
            texto = "Selecciona un mapa para editar"
        
        if self.cambios_sin_guardar:
            texto += " | ⚠️ CAMBIOS SIN GUARDAR"
        
        texto_surf = self.fuente_pequena.render(texto, True, COLOR_TEXTO)
        surface.blit(texto_surf, (10, ALTO - barra_alto + 8))
        
        # Mensaje temporal
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_tiempo < 3000:
            mensaje_surf = self.fuente.render(self.mensaje, True, (100, 255, 100))
            surface.blit(mensaje_surf, (ANCHO // 2 - mensaje_surf.get_width() // 2, ALTO - barra_alto - 40))
        # Overlay con modo dibujo, pincel y zoom (arriba derecha área mapa)
        overlay = [f"Modo: {self.modo_dibujo}", f"Pincel: {self.pincel_tamano}px", f"Zoom: {self.zoom:.2f}x"]
        for i, linea in enumerate(overlay):
            surf = self.fuente_pequena.render(linea, True, (220, 220, 230))
            fondo = pygame.Surface((surf.get_width() + 10, surf.get_height() + 4))
            fondo.set_alpha(150)
            fondo.fill((0, 0, 0))
            surface.blit(fondo, (PANEL_IZQUIERDO + AREA_MAPA_ANCHO - 240, 10 + i * 22))
            surface.blit(surf, (PANEL_IZQUIERDO + AREA_MAPA_ANCHO - 235, 12 + i * 22))

    # === UTILIDADES DE DIBUJO ===
    def _cursor_mundo(self):
        mx, my = pygame.mouse.get_pos()
        if PANEL_IZQUIERDO <= mx <= ANCHO - PANEL_DERECHO:
            x_mapa = mx - PANEL_IZQUIERDO
            mundo_x = x_mapa / self.zoom + self.camara_x
            mundo_y = my / self.zoom + self.camara_y
            return mundo_x, mundo_y
        return 0, 0

    def _pincel_colocar_muro(self, x, y):
        # Evitar duplicar demasiados en misma zona
        for obj in self.objetos:
            if obj.tipo == 'muro' and abs(obj.x - (x - self.pincel_tamano/2)) < 5 and abs(obj.y - (y - self.pincel_tamano/2)) < 5:
                return
        nuevo = ObjetoMapa(
            tipo='muro',
            id=f"muro_{len([o for o in self.objetos if o.tipo=='muro'])+1}",
            x=x - self.pincel_tamano/2,
            y=y - self.pincel_tamano/2,
            ancho=self.pincel_tamano,
            alto=self.pincel_tamano,
            z_index=len(self.objetos),
            sprite_ref=''
        )
        self.objetos.append(nuevo)
        self.cambios_sin_guardar = True

    def _borrar_muro_en_pos(self, x, y):
        borrar = None
        for obj in self.objetos:
            if obj.tipo == 'muro' and obj.contiene_punto(x, y):
                borrar = obj
                break
        if borrar:
            self.objetos.remove(borrar)
            self.cambios_sin_guardar = True

    def _crear_muro_rectangulo(self, x, y, ancho, alto):
        nuevo = ObjetoMapa(
            tipo='muro',
            id=f"muro_{len([o for o in self.objetos if o.tipo=='muro'])+1}",
            x=x,
            y=y,
            ancho=int(ancho),
            alto=int(alto),
            z_index=len(self.objetos),
            sprite_ref=''
        )
        self.objetos.append(nuevo)
        self.cambios_sin_guardar = True

    def _bounding_rect_muro(self, muro: MuroDibujable):
        xs = [p[0] for p in muro.puntos]
        ys = [p[1] for p in muro.puntos]
        if not xs or not ys:
            return pygame.Rect(0, 0, 0, 0)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return pygame.Rect(int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y))

    def _mover_muro_dibujable(self, muro: MuroDibujable, dx, dy):
        muro.puntos = [(px + dx, py + dy) for (px, py) in muro.puntos]
        self.cambios_sin_guardar = True
    
    def guardar_configuracion_batalla(self):
        """Guarda la configuración actual de batalla"""
        if not self.fondo_batalla_actual:
            self.mostrar_mensaje("⚠️ Selecciona un fondo primero")
            return False
        
        # Recopilar datos de batalla
        heroes_config = []
        monstruos_config = []
        
        for obj in self.objetos:
            if obj.tipo == "heroe_batalla":
                heroes_config.append({
                    "sprite_ref": obj.sprite_ref,
                    "x": obj.x,
                    "y": obj.y,
                    "ancho": obj.ancho,
                    "alto": obj.alto
                })
            elif obj.tipo == "monstruo_batalla":
                monstruos_config.append({
                    "sprite_ref": obj.sprite_ref,
                    "x": obj.x,
                    "y": obj.y,
                    "ancho": obj.ancho,
                    "alto": obj.alto
                })
        
        config = {
            "fondo": self.fondo_batalla_actual,
            "num_heroes": self.num_heroes,
            "num_monstruos": self.num_monstruos,
            "heroes": heroes_config,
            "monstruos": monstruos_config
        }
        
        # Guardar en archivo JSON
        try:
            ruta_config = Path("src/database/batalla_config.json")
            ruta_config.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje(f"✓ Configuración guardada: {len(heroes_config)} héroes, {len(monstruos_config)} monstruos")
            print(f"✓ Configuración de batalla guardada: {ruta_config}")
            return True
        
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {str(e)}")
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def cargar_configuracion_batalla(self):
        """Carga una configuración de batalla guardada"""
        ruta_config = Path("src/database/batalla_config.json")
        
        if not ruta_config.exists():
            self.mostrar_mensaje("⚠️ No hay configuración guardada")
            return False
        
        try:
            with open(ruta_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Limpiar objetos de batalla actuales
            self.objetos = [o for o in self.objetos if o.tipo not in ["heroe_batalla", "monstruo_batalla"]]
            
            # Cargar fondo
            self.fondo_batalla_actual = config.get("fondo", None)
            
            # Cargar cantidades
            self.num_heroes = config.get("num_heroes", 1)
            self.num_monstruos = config.get("num_monstruos", 1)
            
            # Cargar héroes
            for hero_data in config.get("heroes", []):
                obj = ObjetoMapa(
                    tipo="heroe_batalla",
                    id=f"heroe_batalla_{len([o for o in self.objetos if o.tipo == 'heroe_batalla']) + 1}",
                    x=hero_data["x"],
                    y=hero_data["y"],
                    ancho=hero_data["ancho"],
                    alto=hero_data["alto"],
                    z_index=len(self.objetos),
                    sprite_ref=hero_data["sprite_ref"]
                )
                self.objetos.append(obj)
            
            # Cargar monstruos
            for mons_data in config.get("monstruos", []):
                obj = ObjetoMapa(
                    tipo="monstruo_batalla",
                    id=f"monstruo_batalla_{len([o for o in self.objetos if o.tipo == 'monstruo_batalla']) + 1}",
                    x=mons_data["x"],
                    y=mons_data["y"],
                    ancho=mons_data["ancho"],
                    alto=mons_data["alto"],
                    z_index=len(self.objetos),
                    sprite_ref=mons_data["sprite_ref"]
                )
                self.objetos.append(obj)
            
            self.mostrar_mensaje(f"✓ Configuración cargada: {len(config.get('heroes', []))} héroes, {len(config.get('monstruos', []))} monstruos")
            print(f"✓ Configuración de batalla cargada desde: {ruta_config}")
            return True
        
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error: {str(e)}")
            print(f"❌ Error cargando configuración: {e}")
            return False
    
    def manejar_clicks_panel_izquierdo(self, mouse_pos):
        """Maneja clicks en el panel izquierdo"""
        x, y = mouse_pos
        
        # Verificar si se clickeó un mapa
        if self.modo_actual == "mapas":
            # Botón actualizar
            rect_actualizar = pygame.Rect(10, 135, PANEL_IZQUIERDO - 20, 25)
            if rect_actualizar.collidepoint(mouse_pos):
                self.cargar_lista_mapas()
                self.mostrar_mensaje("✓ Lista de mapas actualizada")
                return True
            
            y_inicio = 180
            for i, mapa_info in enumerate(self.mapas_disponibles[:15]):
                rect_boton = pygame.Rect(10, y_inicio + i * 35, PANEL_IZQUIERDO - 20, 30)
                if rect_boton.collidepoint(mouse_pos):
                    self.cargar_mapa(mapa_info["nombre"], mapa_info["carpeta"])
                    return True
        
        # Modo batalla - clicks en héroes/monstruos
        elif self.modo_actual == "batalla" and self.modo_editor == ModoEditor.VISTA_BATALLA:
            # Botones Guardar/Cargar (posición ajustada)
            y_botones = 430
            rect_guardar = pygame.Rect(10, y_botones, (PANEL_IZQUIERDO - 30) // 2, 35)
            if rect_guardar.collidepoint(mouse_pos):
                self.guardar_configuracion_batalla()
                return True
            
            rect_cargar = pygame.Rect(10 + (PANEL_IZQUIERDO - 30) // 2 + 10, y_botones, (PANEL_IZQUIERDO - 30) // 2, 35)
            if rect_cargar.collidepoint(mouse_pos):
                self.cargar_configuracion_batalla()
                return True
            
            # Selector de cantidad de héroes (1-4)
            y_heroes = 155
            for i in range(1, 5):
                rect_num = pygame.Rect(10 + (i-1) * 30, y_heroes, 25, 25)
                if rect_num.collidepoint(mouse_pos):
                    self.num_heroes = i
                    self.mostrar_mensaje(f"✓ Cantidad de héroes: {i}")
                    return True
            
            # Selector de cantidad de monstruos (1-5)
            y_mons = 210
            for i in range(1, 6):
                rect_num = pygame.Rect(10 + (i-1) * 30, y_mons, 25, 25)
                if rect_num.collidepoint(mouse_pos):
                    self.num_monstruos = i
                    self.mostrar_mensaje(f"✓ Cantidad de monstruos: {i}")
                    return True
            
            # Fondos de batalla
            if hasattr(self, 'fondos_batalla'):
                y_fondos = 280
                for i, fondo in enumerate(self.fondos_batalla[:3]):
                    rect_fondo = pygame.Rect(10, y_fondos + i * 50, PANEL_IZQUIERDO - 20, 45)
                    if rect_fondo.collidepoint(mouse_pos):
                        self.fondo_batalla_actual = fondo["nombre"]
                        self.mostrar_mensaje(f"✓ Fondo: {fondo['nombre']}")
                        return True
            
            # Héroes (arrastrables) - POSICIÓN AJUSTADA
            heroes_batalla = [s for s in self.biblioteca_sprites.get("héroes", []) if "batalla" in s.ruta_imagen.lower()]
            y_heroes_lista = 490
            for i, sprite in enumerate(heroes_batalla[:3]):
                rect_sprite = pygame.Rect(10, y_heroes_lista + i * 35, PANEL_IZQUIERDO - 20, 30)
                if rect_sprite.collidepoint(mouse_pos):
                    if not self.fondo_batalla_actual:
                        self.mostrar_mensaje("⚠️ Selecciona un fondo primero")
                        return True
                    # Iniciar drag & drop
                    self.sprite_siendo_arrastrado = sprite
                    self.tipo_sprite_arrastrado = "heroe"
                    self.arrastrando_desde_panel = True
                    self.offset_drag_x = mouse_pos[0]
                    self.offset_drag_y = mouse_pos[1]
                    print(f"🎯 Arrastrando héroe: {sprite.id}")
                    return True
            
            # Monstruos (arrastrables) - POSICIÓN AJUSTADA
            monstruos = self.biblioteca_sprites.get("monstruos", [])
            y_mons_lista = 600
            for i, sprite in enumerate(monstruos[:10]):
                rect_sprite = pygame.Rect(10, y_mons_lista + i * 35, PANEL_IZQUIERDO - 20, 30)
                if rect_sprite.collidepoint(mouse_pos):
                    if not self.fondo_batalla_actual:
                        self.mostrar_mensaje("⚠️ Selecciona un fondo primero")
                        return True
                    # Iniciar drag & drop
                    self.sprite_siendo_arrastrado = sprite
                    self.tipo_sprite_arrastrado = "monstruo"
                    self.arrastrando_desde_panel = True
                    self.offset_drag_x = mouse_pos[0]
                    self.offset_drag_y = mouse_pos[1]
                    print(f"🎯 Arrastrando monstruo: {sprite.id}")
                    return True
        
        # Verificar si se clickeó un sprite para añadir
        elif self.modo_actual in ["cofres", "npcs", "héroes", "monstruos"]:
            # Botón actualizar
            ancho_boton = (PANEL_IZQUIERDO - 30) // 2
            rect_actualizar = pygame.Rect(10, 135, ancho_boton, 25)
            if rect_actualizar.collidepoint(mouse_pos):
                self.cargar_biblioteca_sprites()
                self.mostrar_mensaje("✓ Biblioteca de sprites actualizada")
                return True
            
            # Botón explorar/añadir
            rect_explorar = pygame.Rect(10 + ancho_boton + 10, 135, ancho_boton, 25)
            if rect_explorar.collidepoint(mouse_pos):
                self.explorar_y_añadir_sprite(self.modo_actual)
                return True
            
            y_inicio = 170
            sprites = self.biblioteca_sprites.get(self.modo_actual, [])
            for i, sprite in enumerate(sprites[:15]):
                rect_boton = pygame.Rect(10, y_inicio + i * 35, PANEL_IZQUIERDO - 20, 30)
                if rect_boton.collidepoint(mouse_pos):
                    # Pasar el ID del sprite como referencia
                    self.crear_objeto_desde_sprite(sprite)
                    return True
        
        return False
    
    def crear_objeto_batalla(self, sprite_info, tipo_batalla):
        """Crea un objeto específico para modo batalla (héroe o monstruo)"""
        # Determinar el tipo correcto EXACTO
        if tipo_batalla == "heroe":
            tipo_obj = "heroe_batalla"
            pos_x_base = 100
            offset_x = 120
            pos_y = 400 - 200  # 200px encima del borde inferior
        elif tipo_batalla == "monstruo":
            tipo_obj = "monstruo_batalla"
            pos_x_base = 700
            offset_x = 150
            pos_y = 300 - 200  # 100px encima de los héroes
        else:
            print(f"❌ ERROR: tipo_batalla desconocido: '{tipo_batalla}'")
            return
        
        # Generar ID único
        num = len([o for o in self.objetos if o.tipo == tipo_obj]) + 1
        nuevo_id = f"{sprite_info.id}_{num}"
        
        # Posición según cantidad de objetos del mismo tipo
        pos_x = pos_x_base + (num - 1) * offset_x
        
        # Crear objeto inmediatamente (sin delays para 60 FPS)
        obj = ObjetoMapa(
            tipo=tipo_obj,
            id=nuevo_id,
            x=pos_x,
            y=pos_y,
            ancho=sprite_info.ancho_default,
            alto=sprite_info.alto_default,
            z_index=len(self.objetos),
            sprite_ref=sprite_info.ruta_imagen  # Usar ruta completa como referencia
        )
        
        self.objetos.append(obj)
        self.objeto_seleccionado = obj
        self.cambios_sin_guardar = True
        
        print(f"✓ {tipo_obj} creado: {nuevo_id} en ({pos_x}, {pos_y})")
        self.mostrar_mensaje(f"✓ {sprite_info.id} añadido")
    
    def crear_objeto_batalla_en_posicion(self, sprite_info, tipo_batalla, pos_x, pos_y):
        """Crea un objeto en una posición específica (para drag & drop)"""
        # Determinar el tipo correcto
        if tipo_batalla == "heroe":
            tipo_obj = "heroe_batalla"
        elif tipo_batalla == "monstruo":
            tipo_obj = "monstruo_batalla"
        else:
            print(f"❌ ERROR: tipo_batalla desconocido: '{tipo_batalla}'")
            return
        
        # Generar ID único
        num = len([o for o in self.objetos if o.tipo == tipo_obj]) + 1
        nuevo_id = f"{sprite_info.id}_{num}"
        
        # Ajustar posición para centrar el sprite en el cursor
        pos_x_centrado = pos_x - (sprite_info.ancho_default // 2)
        pos_y_centrado = pos_y - (sprite_info.alto_default // 2)
        
        # Crear objeto en la posición del drop
        obj = ObjetoMapa(
            tipo=tipo_obj,
            id=nuevo_id,
            x=pos_x_centrado,
            y=pos_y_centrado,
            ancho=sprite_info.ancho_default,
            alto=sprite_info.alto_default,
            z_index=len(self.objetos),
            sprite_ref=sprite_info.ruta_imagen
        )
        
        self.objetos.append(obj)
        self.objeto_seleccionado = obj
        self.cambios_sin_guardar = True
        
        print(f"✓ {tipo_obj} creado en ({pos_x_centrado}, {pos_y_centrado})")
        self.mostrar_mensaje(f"✓ {sprite_info.id} añadido")
    
    def manejar_eventos(self):
        """Maneja eventos del pygame"""
        mouse_pos = pygame.mouse.get_pos()
        click_izq = False
        click_der = False
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                # ESC - Salir
                if evento.key == pygame.K_ESCAPE:
                    if self.cambios_sin_guardar:
                        print("⚠️ Cambios sin guardar. Presiona G para guardar.")
                    return False
                
                # G - Guardar
                elif evento.key == pygame.K_g:
                    self.guardar_mapa()
                
                # D - Duplicar
                elif evento.key == pygame.K_d:
                    if self.objeto_seleccionado:
                        self.duplicar_objeto(self.objeto_seleccionado)
                
                # DELETE - Eliminar
                elif evento.key == pygame.K_DELETE:
                    if self.objeto_seleccionado:
                        self.eliminar_objeto(self.objeto_seleccionado)
                
                # Grid toggle
                elif evento.key == pygame.K_h:
                    self.mostrar_grid = not self.mostrar_grid
                
                # CTRL+Z - Deshacer (placeholder)
                elif evento.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.mostrar_mensaje("Deshacer - No implementado aún")
                # --- NUEVOS MODOS DE DIBUJO ---
                elif evento.key == pygame.K_r:
                    self.modo_dibujo = 'rectangulo'
                    self.mostrar_mensaje("Modo Rectángulo")
                elif evento.key == pygame.K_p:
                    self.modo_dibujo = 'pincel'
                    self.mostrar_mensaje("Modo Pincel")
                elif evento.key == pygame.K_e:
                    if self.modo_dibujo == 'borrador':
                        self.modo_dibujo = 'rectangulo'
                        self.mostrar_mensaje("Borrador desactivado")
                    else:
                        self.modo_dibujo = 'borrador'
                        self.mostrar_mensaje("Modo Borrador")
                elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    if self.modo_dibujo == 'pincel':
                        self.pincel_tamano = min(self.pincel_max, self.pincel_tamano + 5)
                        self.mostrar_mensaje(f"Pincel: {self.pincel_tamano}px")
                elif evento.key == pygame.K_MINUS:
                    if self.modo_dibujo == 'pincel':
                        self.pincel_tamano = max(self.pincel_min, self.pincel_tamano - 5)
                        self.mostrar_mensaje(f"Pincel: {self.pincel_tamano}px")
                elif evento.key == pygame.K_0:
                    self.zoom = 1.0
                    self.camara_x = 0
                    self.camara_y = 0
                    self.mostrar_mensaje("Zoom reiniciado")
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    click_izq = True
                    self.mouse_izquierdo_presionado = True
                    
                    print(f"🖱️ CLICK IZQUIERDO en ({mouse_pos[0]}, {mouse_pos[1]})")
                    print(f"   Modo actual: {self.modo_actual}")
                    print(f"   Modo editor: {self.modo_editor}")
                    
                    # Click en panel izquierdo
                    if mouse_pos[0] < PANEL_IZQUIERDO:
                        print(f"   📍 Click en PANEL IZQUIERDO")
                        # Actualizar botones de modo
                        for boton in self.botones_modo:
                            boton.update(mouse_pos, True)
                        
                        resultado = self.manejar_clicks_panel_izquierdo(mouse_pos)
                        print(f"   Resultado manejar_clicks: {resultado}")
                    
                    # Click en área del mapa
                    elif PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                        x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                        # --- Acciones de dibujo (solo fuera vista batalla) ---
                        if self.modo_editor != ModoEditor.VISTA_BATALLA:
                            mundo_x_preciso = x_mapa / self.zoom + self.camara_x
                            mundo_y_preciso = mouse_pos[1] / self.zoom + self.camara_y
                            # Seleccionar muro dibujable para mover (modo muros)
                            if self.modo_editor == ModoEditor.DIBUJAR_MUROS:
                                for muro in reversed(self.muros):
                                    rect_muro = self._bounding_rect_muro(muro)
                                    if rect_muro.collidepoint(mundo_x_preciso, mundo_y_preciso):
                                        self.muro_seleccionado = muro
                                        self.muro_arrastrando = True
                                        self.muro_offset = (mundo_x_preciso, mundo_y_preciso)
                                        break
                            # Comenzar rectángulo
                            if self.modo_dibujo == 'rectangulo':
                                self.dibujando_rectangulo = True
                                self.rect_inicio = (mundo_x_preciso, mundo_y_preciso)
                            elif self.modo_dibujo == 'pincel':
                                self._pincel_colocar_muro(mundo_x_preciso, mundo_y_preciso)
                            elif self.modo_dibujo == 'borrador':
                                self._borrar_muro_en_pos(mundo_x_preciso, mundo_y_preciso)
                        
                        # En modo batalla, permitir mover objetos de batalla
                        if self.modo_editor == ModoEditor.VISTA_BATALLA:
                            # Convertir a coordenadas relativas al área de batalla
                            y_mapa = mouse_pos[1]
                            obj = None
                            for o in reversed(self.objetos):
                                if o.tipo in ["heroe_batalla", "monstruo_batalla"]:
                                    # Verificar si el click está en este objeto
                                    if (x_mapa >= o.x and x_mapa <= o.x + o.ancho and
                                        y_mapa >= o.y and y_mapa <= o.y + o.alto):
                                        obj = o
                                        break
                            
                            if obj:
                                self.objeto_seleccionado = obj
                                
                                # Verificar si se clickeó un handle
                                handle = obj.get_handle_en_punto(x_mapa, y_mapa, 10)
                                
                                if handle:
                                    obj.redimensionando = True
                                    obj.handle_activo = handle
                                else:
                                    obj.arrastrando = True
                                    obj.offset_x = obj.x - x_mapa
                                    obj.offset_y = obj.y - y_mapa
                            else:
                                self.objeto_seleccionado = None
                        
                        # Solo buscar objetos en modo normal
                        elif self.modo_editor == ModoEditor.NORMAL:
                            obj = self.obtener_objeto_en_posicion(x_mapa, mouse_pos[1])
                            
                            if obj:
                                self.objeto_seleccionado = obj
                                
                                # Verificar si se clickeó un handle (convertir a coordenadas del mundo con zoom)
                                mundo_x = x_mapa / self.zoom + self.camara_x
                                mundo_y = mouse_pos[1] / self.zoom + self.camara_y
                                handle = obj.get_handle_en_punto(mundo_x, mundo_y, 10 / self.zoom)
                                
                                if handle:
                                    obj.redimensionando = True
                                    obj.handle_activo = handle
                                else:
                                    obj.arrastrando = True
                                    obj.offset_x = obj.x - mundo_x
                                    obj.offset_y = obj.y - mundo_y
                            else:
                                # Si no hay objeto, iniciar arrastre del mapa
                                self.arrastrando_camara = True
                                self.mouse_anterior = mouse_pos
                                self.objeto_seleccionado = None
                        else:
                            # En otros modos, solo arrastre de cámara
                            self.arrastrando_camara = True
                            self.mouse_anterior = mouse_pos
                
                elif evento.button == 2 or evento.button == 3:  # Click medio o derecho
                    # En modo batalla, eliminar sprite con click derecho
                    if self.modo_editor == ModoEditor.VISTA_BATALLA:
                        if PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                            x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                            
                            # Buscar objeto bajo el cursor
                            obj_eliminar = None
                            for o in reversed(self.objetos):
                                if o.tipo in ["heroe_batalla", "monstruo_batalla"]:
                                    if (x_mapa >= o.x and x_mapa <= o.x + o.ancho and
                                        mouse_pos[1] >= o.y and mouse_pos[1] <= o.y + o.alto):
                                        obj_eliminar = o
                                        break
                            
                            if obj_eliminar:
                                self.eliminar_objeto(obj_eliminar)
                                self.mostrar_mensaje(f"✓ Eliminado: {obj_eliminar.id}")
                                return True
                    
                    # Fuera de modo batalla, pan de cámara
                    else:
                        self.arrastrando_camara = True
                        self.mouse_anterior = mouse_pos
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    self.mouse_izquierdo_presionado = False
                    # ¡NUEVO! Soltar sprite arrastrado desde panel
                    if self.arrastrando_desde_panel and self.sprite_siendo_arrastrado:
                        # Verificar si soltamos en área del mapa (modo batalla)
                        if (self.modo_editor == ModoEditor.VISTA_BATALLA and 
                            PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO):
                            # Convertir posición del mouse a coordenadas del área de batalla
                            x_drop = mouse_pos[0] - PANEL_IZQUIERDO
                            y_drop = mouse_pos[1]
                            
                            # Crear sprite en esa posición
                            self.crear_objeto_batalla_en_posicion(
                                self.sprite_siendo_arrastrado, 
                                self.tipo_sprite_arrastrado,
                                x_drop, 
                                y_drop
                            )
                            print(f"✓ Sprite soltado en ({x_drop}, {y_drop})")
                        else:
                            print("⚠️ Sprite soltado fuera del área válida")
                        
                        # Resetear estado de drag
                        self.sprite_siendo_arrastrado = None
                        self.tipo_sprite_arrastrado = None
                        self.arrastrando_desde_panel = False
                    
                    # Soltar objetos
                    for obj in self.objetos:
                        if obj.arrastrando or obj.redimensionando:
                            obj.arrastrando = False
                            obj.redimensionando = False
                            obj.handle_activo = None
                            self.cambios_sin_guardar = True
                    
                    # Soltar arrastre de cámara
                    if self.arrastrando_camara:
                        self.arrastrando_camara = False
                    # Finalizar rectángulo
                    if self.dibujando_rectangulo and self.rect_inicio and self.modo_dibujo == 'rectangulo' and self.modo_editor != ModoEditor.VISTA_BATALLA:
                        fin_x, fin_y = self._cursor_mundo()
                        inicio_x, inicio_y = self.rect_inicio
                        ancho = abs(fin_x - inicio_x)
                        alto = abs(fin_y - inicio_y)
                        if ancho >= 5 and alto >= 5:
                            x_final = min(inicio_x, fin_x)
                            y_final = min(inicio_y, fin_y)
                            self._crear_muro_rectangulo(x_final, y_final, ancho, alto)
                        self.dibujando_rectangulo = False
                        self.rect_inicio = None
                    # Terminar arrastre de muro dibujable
                    if self.muro_arrastrando:
                        self.muro_arrastrando = False
                        self.muro_seleccionado = None
                
                elif evento.button == 2 or evento.button == 3:
                    self.arrastrando_camara = False
            
            elif evento.type == pygame.MOUSEMOTION:
                # Verificar si estamos en área del mapa
                if PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                    x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                    
                    # En modo batalla, coordenadas directas
                    if self.modo_editor == ModoEditor.VISTA_BATALLA:
                        mundo_x = x_mapa
                        mundo_y = mouse_pos[1]
                    else:
                        # Convertir a coordenadas del mundo considerando zoom
                        mundo_x = x_mapa / self.zoom + self.camara_x
                        mundo_y = mouse_pos[1] / self.zoom + self.camara_y
                    
                    # Arrastrar objetos tiene prioridad sobre cámara
                    hay_objeto_siendo_arrastrado = False
                    
                    for obj in self.objetos:
                        if obj.arrastrando:
                            obj.x = mundo_x + obj.offset_x
                            obj.y = mundo_y + obj.offset_y
                            obj.actualizar_rect()
                            hay_objeto_siendo_arrastrado = True
                        
                        elif obj.redimensionando and obj.handle_activo:
                            # Redimensionar según el handle
                            if 'e' in obj.handle_activo:  # Este (derecha)
                                nuevo_ancho = max(20, mundo_x - obj.x)
                                obj.ancho = nuevo_ancho
                            elif 'w' in obj.handle_activo:  # Oeste (izquierda)
                                nuevo_ancho = max(20, obj.x + obj.ancho - mundo_x)
                                if nuevo_ancho >= 20:
                                    obj.x = mundo_x
                                    obj.ancho = nuevo_ancho
                            
                            if 's' in obj.handle_activo:  # Sur (abajo)
                                nuevo_alto = max(20, mundo_y - obj.y)
                                obj.alto = nuevo_alto
                            elif 'n' in obj.handle_activo:  # Norte (arriba)
                                nuevo_alto = max(20, obj.y + obj.alto - mundo_y)
                                if nuevo_alto >= 20:
                                    obj.y = mundo_y
                                    obj.alto = nuevo_alto
                            
                            obj.actualizar_rect()
                            hay_objeto_siendo_arrastrado = True
                    
                    # Arrastrar cámara solo si no hay objetos siendo arrastrados
                    if self.arrastrando_camara and not hay_objeto_siendo_arrastrado:
                        dx = mouse_pos[0] - self.mouse_anterior[0]
                        dy = mouse_pos[1] - self.mouse_anterior[1]
                        # Ajustar movimiento de cámara según zoom
                        self.camara_x -= dx / self.zoom
                        self.camara_y -= dy / self.zoom
                        # Limitar cámara dentro de los límites del mapa
                        self.camara_x = max(0, min(self.camara_x, max(0, self.ancho_mapa - AREA_MAPA_ANCHO / self.zoom)))
                        self.camara_y = max(0, min(self.camara_y, max(0, self.alto_mapa - ALTO / self.zoom)))
                        self.mouse_anterior = mouse_pos

                    # Pintar / borrar mientras se mueve el mouse con botón
                    if self.mouse_izquierdo_presionado and self.modo_editor != ModoEditor.VISTA_BATALLA:
                        if self.modo_dibujo == 'pincel':
                            self._pincel_colocar_muro(mundo_x, mundo_y)
                        elif self.modo_dibujo == 'borrador':
                            self._borrar_muro_en_pos(mundo_x, mundo_y)
                    # Arrastrar muro dibujable
                    if self.muro_arrastrando and self.muro_seleccionado:
                        dx_m = mundo_x - self.muro_offset[0]
                        dy_m = mundo_y - self.muro_offset[1]
                        self._mover_muro_dibujable(self.muro_seleccionado, dx_m, dy_m)
                        self.muro_offset = (mundo_x, mundo_y)
                    
                    # Actualizar hover solo si no estamos arrastrando
                    if not hay_objeto_siendo_arrastrado and not self.arrastrando_camara:
                        if self.modo_editor == ModoEditor.VISTA_BATALLA:
                            # En modo batalla, revisar objetos de batalla
                            self.objeto_hover = None
                            for o in reversed(self.objetos):
                                if o.tipo in ["heroe_batalla", "monstruo_batalla"]:
                                    if (x_mapa >= o.x and x_mapa <= o.x + o.ancho and
                                        mouse_pos[1] >= o.y and mouse_pos[1] <= o.y + o.alto):
                                        self.objeto_hover = o
                                        break
                        else:
                            self.objeto_hover = self.obtener_objeto_en_posicion(x_mapa, mouse_pos[1])
                
                # Si estamos fuera del área del mapa pero arrastrando cámara
                elif self.arrastrando_camara:
                    dx = mouse_pos[0] - self.mouse_anterior[0]
                    dy = mouse_pos[1] - self.mouse_anterior[1]
                    self.camara_x -= dx / self.zoom
                    self.camara_y -= dy / self.zoom
                    self.camara_x = max(0, min(self.camara_x, max(0, self.ancho_mapa - AREA_MAPA_ANCHO / self.zoom)))
                    self.camara_y = max(0, min(self.camara_y, max(0, self.alto_mapa - ALTO / self.zoom)))
                    self.mouse_anterior = mouse_pos
            
            elif evento.type == pygame.MOUSEWHEEL:
                # ZOOM CON RUEDA DEL MOUSE
                # Verificar que estamos en el área del mapa
                if PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                    # Guardar zoom anterior
                    zoom_anterior = self.zoom
                    
                    # Ajustar zoom
                    factor_zoom = 1.1 if evento.y > 0 else 0.9
                    self.zoom *= factor_zoom
                    
                    # Limitar zoom entre 0.1x y 5x
                    # Nuevo rango: 0.25x - 4.0x
                    self.zoom = max(0.25, min(4.0, self.zoom))
                    
                    # Ajustar cámara para que el zoom sea centrado en el cursor
                    # Convertir posición del mouse a coordenadas del mundo antes del zoom
                    x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                    mundo_x_antes = (x_mapa / self.zoom) + self.camara_x
                    mundo_y_antes = (mouse_pos[1] / self.zoom) + self.camara_y
                    
                    # Después del zoom, ajustar cámara para mantener punto bajo cursor
                    self.camara_x = mundo_x_antes - (x_mapa / self.zoom)
                    self.camara_y = mundo_y_antes - (mouse_pos[1] / self.zoom)
        
        # Actualizar hover en botones
        for boton in self.botones_modo:
            boton.update(mouse_pos, False)
        
        # Mover cámara con teclado
        teclas = pygame.key.get_pressed()
        velocidad = 10
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.camara_x = max(0, self.camara_x - velocidad)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.camara_x = min(self.ancho_mapa - AREA_MAPA_ANCHO, self.camara_x + velocidad)
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.camara_y = max(0, self.camara_y - velocidad)
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.camara_y = min(self.alto_mapa - ALTO, self.camara_y + velocidad)
        
        return True
    
    def dibujar_vista_batalla(self, surface):
        """Dibuja la vista especial para configurar batallas"""
        # Fondo de batalla (el seleccionado o el primero disponible)
        if hasattr(self, 'fondos_batalla') and len(self.fondos_batalla) > 0:
            try:
                # Buscar el fondo actual o usar el primero
                fondo_usar = self.fondos_batalla[0]
                if self.fondo_batalla_actual:
                    for f in self.fondos_batalla:
                        if f["nombre"] == self.fondo_batalla_actual:
                            fondo_usar = f
                            break
                
                fondo = pygame.image.load(fondo_usar["ruta"]).convert()
                fondo_escalado = pygame.transform.scale(fondo, (AREA_MAPA_ANCHO, ALTO))
                surface.blit(fondo_escalado, (0, 0))
            except:
                surface.fill((30, 20, 40))
        else:
            surface.fill((30, 20, 40))
        
        # Simular ventana UI inferior (200px)
        ui_alto = 200
        ui_rect = pygame.Rect(0, ALTO - ui_alto, AREA_MAPA_ANCHO, ui_alto)
        pygame.draw.rect(surface, (20, 20, 30), ui_rect)
        pygame.draw.rect(surface, (100, 100, 120), ui_rect, 3)
        
        texto_ui = self.fuente.render("Área de UI (200px)", True, (150, 150, 150))
        surface.blit(texto_ui, (AREA_MAPA_ANCHO // 2 - texto_ui.get_width() // 2, ALTO - ui_alto + 90))
        
        # Área de batalla real (sin UI)
        area_batalla_alto = ALTO - ui_alto
        
        # Dibujar objetos de batalla (héroes y monstruos)
        for obj in sorted(self.objetos, key=lambda o: o.z_index):
            if obj.tipo in ["heroe_batalla", "monstruo_batalla"]:
                self.dibujar_objeto_batalla(surface, obj)
        
        # Líneas de referencia
        pygame.draw.line(surface, (80, 80, 100), (0, area_batalla_alto), (AREA_MAPA_ANCHO, area_batalla_alto), 2)
        
        # Información
        info_texto = self.fuente_pequena.render(f"Área batalla: {AREA_MAPA_ANCHO}x{area_batalla_alto} | UI: {AREA_MAPA_ANCHO}x{ui_alto}", True, (180, 180, 200))
        surface.blit(info_texto, (10, 10))
        
        # Indicadores de guía mejorados
        if len([o for o in self.objetos if o.tipo == "heroe_batalla"]) == 0:
            texto_guia = self.fuente.render("← ARRASTRA héroes desde el panel", True, (100, 255, 100))
            surface.blit(texto_guia, (80, 350))
        
        if len([o for o in self.objetos if o.tipo == "monstruo_batalla"]) == 0:
            texto_guia = self.fuente.render("ARRASTRA monstruos desde el panel →", True, (255, 100, 100))
            surface.blit(texto_guia, (AREA_MAPA_ANCHO - 420, 300))
        
        # Instrucción de drag & drop si hay sprite siendo arrastrado
        if self.arrastrando_desde_panel:
            texto_drag = self.fuente.render("⬇ Suelta aquí para colocar ⬇", True, (255, 255, 0))
            surface.blit(texto_drag, (AREA_MAPA_ANCHO // 2 - texto_drag.get_width() // 2, 50))
    
    def dibujar_objeto_batalla(self, surface, obj):
        """Dibuja un objeto en modo batalla (sin zoom)"""
        # Intentar cargar sprite real si existe
        sprite_dibujado = False
        if obj.sprite_ref:
            # Primero intentar con la ruta directa (preferido)
            if obj.sprite_ref in self.imagenes_sprites:
                img = self.imagenes_sprites[obj.sprite_ref]
                img_escalada = pygame.transform.scale(img, (obj.ancho, obj.alto))
                surface.blit(img_escalada, (int(obj.x), int(obj.y)))
                sprite_dibujado = True
                print(f"✓ Dibujado sprite batalla: {obj.id} desde ruta directa")
            else:
                # Buscar por ID o ruta en la biblioteca
                for categoria, sprites in self.biblioteca_sprites.items():
                    for sprite in sprites:
                        if sprite.id == obj.sprite_ref or sprite.ruta_imagen == obj.sprite_ref:
                            if sprite.ruta_imagen in self.imagenes_sprites:
                                img = self.imagenes_sprites[sprite.ruta_imagen]
                                img_escalada = pygame.transform.scale(img, (obj.ancho, obj.alto))
                                surface.blit(img_escalada, (int(obj.x), int(obj.y)))
                                sprite_dibujado = True
                                print(f"✓ Dibujado sprite batalla: {obj.id} desde biblioteca")
                                break
                    if sprite_dibujado:
                        break
            
            if not sprite_dibujado:
                print(f"⚠️  No se pudo cargar sprite para: {obj.id}, ref={obj.sprite_ref}")
        
        # Si no se dibujó el sprite, dibujar rectángulo de color
        if not sprite_dibujado:
            color_base = (50, 255, 50) if obj.tipo == "heroe_batalla" else (200, 50, 200)
            rect_superficie = pygame.Surface((obj.ancho, obj.alto))
            rect_superficie.set_alpha(120)
            rect_superficie.fill(color_base)
            surface.blit(rect_superficie, (int(obj.x), int(obj.y)))
        
        # Borde
        rect = pygame.Rect(int(obj.x), int(obj.y), obj.ancho, obj.alto)
        
        if obj == self.objeto_seleccionado:
            pygame.draw.rect(surface, COLOR_SELECCION, rect, 3)
            # Dibujar handles de redimensionamiento
            self.dibujar_handles_batalla(surface, obj)
        elif obj == self.objeto_hover:
            pygame.draw.rect(surface, COLOR_HOVER, rect, 2)
        else:
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)
        
        # Texto con ID
        texto = self.fuente_pequena.render(f"{obj.id}", True, COLOR_TEXTO)
        fondo_texto = pygame.Surface((texto.get_width() + 10, texto.get_height() + 4))
        fondo_texto.set_alpha(180)
        fondo_texto.fill((0, 0, 0))
        surface.blit(fondo_texto, (obj.x + 2, obj.y + 2))
        surface.blit(texto, (obj.x + 5, obj.y + 4))
    
    def dibujar_handles_batalla(self, surface, obj):
        """Dibuja handles de redimensionamiento en modo batalla"""
        tam_handle = 8
        handles = [
            (obj.x, obj.y),  # NW
            (obj.x + obj.ancho, obj.y),  # NE
            (obj.x, obj.y + obj.alto),  # SW
            (obj.x + obj.ancho, obj.y + obj.alto),  # SE
        ]
        
        for hx, hy in handles:
            pygame.draw.circle(surface, COLOR_RESIZE_HANDLE, (int(hx), int(hy)), tam_handle)
            pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), tam_handle, 2)
    
    def dibujar_sprite_fantasma(self, surface, mouse_pos):
        """Dibuja un sprite semitransparente siguiendo el cursor durante drag & drop"""
        if not self.sprite_siendo_arrastrado:
            return
        
        sprite = self.sprite_siendo_arrastrado
        
        # Calcular posición centrada en el cursor
        x = mouse_pos[0] - (sprite.ancho_default // 2)
        y = mouse_pos[1] - (sprite.alto_default // 2)
        
        # Intentar cargar imagen del sprite
        if sprite.ruta_imagen in self.imagenes_sprites:
            img = self.imagenes_sprites[sprite.ruta_imagen]
            img_escalada = pygame.transform.scale(img, (sprite.ancho_default, sprite.alto_default))
            
            # Hacer semitransparente
            img_fantasma = img_escalada.copy()
            img_fantasma.set_alpha(150)
            surface.blit(img_fantasma, (x, y))
        else:
            # Rectángulo semitransparente como fallback
            color = (50, 255, 50) if self.tipo_sprite_arrastrado == "heroe" else (255, 50, 150)
            rect_fantasma = pygame.Surface((sprite.ancho_default, sprite.alto_default))
            rect_fantasma.set_alpha(150)
            rect_fantasma.fill(color)
            surface.blit(rect_fantasma, (x, y))
        
        # Borde del sprite fantasma
        rect = pygame.Rect(x, y, sprite.ancho_default, sprite.alto_default)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        
        # Texto con nombre del sprite
        texto = self.fuente_pequena.render(sprite.id[:15], True, COLOR_TEXTO)
        fondo = pygame.Surface((texto.get_width() + 10, texto.get_height() + 4))
        fondo.set_alpha(200)
        fondo.fill((0, 0, 0))
        surface.blit(fondo, (x + 2, y - 20))
        surface.blit(texto, (x + 5, y - 18))
    
    def ejecutar(self):
        """Bucle principal del editor"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área del mapa
            area_mapa = self.pantalla.subsurface((PANEL_IZQUIERDO, 0, AREA_MAPA_ANCHO, ALTO))
            
            # Si estamos en modo batalla, dibujar vista especial
            if self.modo_editor == ModoEditor.VISTA_BATALLA:
                self.dibujar_vista_batalla(area_mapa)
            else:
                # Fondo del mapa con zoom
                if self.imagen_mapa:
                    # Escalar la imagen según el zoom
                    ancho_escalado = int(self.ancho_mapa * self.zoom)
                    alto_escalado = int(self.alto_mapa * self.zoom)
                    imagen_escalada = pygame.transform.scale(self.imagen_mapa, (ancho_escalado, alto_escalado))
                    area_mapa.blit(imagen_escalada, (int(-self.camara_x * self.zoom), int(-self.camara_y * self.zoom)))
                else:
                    area_mapa.fill((30, 30, 40))
                
                # Grid
                self.dibujar_grid(area_mapa)
                
                # Objetos
                for obj in sorted(self.objetos, key=lambda o: o.z_index):
                    self.dibujar_objeto(self.pantalla, obj)
            
            # Paneles
            self.dibujar_panel_izquierdo(self.pantalla)
            self.dibujar_panel_derecho(self.pantalla)
            
            # ¡NUEVO! Dibujar sprite fantasma si se está arrastrando
            if self.arrastrando_desde_panel and self.sprite_siendo_arrastrado:
                mouse_pos = pygame.mouse.get_pos()
                self.dibujar_sprite_fantasma(self.pantalla, mouse_pos)
            
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
║  EDITOR DE MAPAS PROFESIONAL - CodeVerso RPG          ║
║                                                        ║
║  Características:                                      ║
║  ✓ Selector de mapas con preview                      ║
║  ✓ Biblioteca de sprites organizados                  ║
║  ✓ Redimensionamiento con esquinas                    ║
║  ✓ Sistema de capas                                   ║
║  ✓ Historial de uso                                   ║
║  ✓ Exportación automática                             ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    editor = EditorMapaAvanzado()
    editor.ejecutar()
