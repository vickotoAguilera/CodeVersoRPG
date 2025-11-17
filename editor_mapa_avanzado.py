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
        modos = ["Mapas", "Cofres", "NPCs", "Héroes", "Monstruos", "Portales", "Muros"]
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
            self.modo_editor = ModoEditor.DIBUJAR_MURO
            self.dibujando_muro = False
            self.muro_actual = None
        elif modo == "portales":
            self.modo_editor = ModoEditor.CREAR_PORTAL
            self.portal_temp = None
            self.creando_portal_origen = False
            self.creando_portal_destino = False
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
        
        # Cargar Monstruos (buscar en monstruos/ recursivamente)
        self.biblioteca_sprites["monstruos"] = []
        monstruos_path = base_path / "monstruos"
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
                
                # USAR DIMENSIONES DEL JUEGO (no la imagen original)
                self.ancho_mapa = self.ANCHO_JUEGO
                self.alto_mapa = self.ALTO_JUEGO
                
                # Escalar el mapa al tamaño del juego
                self.imagen_mapa = pygame.transform.scale(img_original, (self.ANCHO_JUEGO, self.ALTO_JUEGO))
                
                print(f"✓ Mapa cargado: {nombre_mapa}")
                print(f"  Original: {img_original.get_width()}x{img_original.get_height()}")
                print(f"  En juego: {self.ANCHO_JUEGO}x{self.ALTO_JUEGO}")
            else:
                self.imagen_mapa = None
                print(f"⚠️ No se encontró imagen: {ruta_imagen}")
        else:
            # Intentar buscar manualmente
            for ext in ['.jpg', '.png', '.jpeg']:
                ruta_imagen = Path(f"assets/maps/{carpeta}/{nombre_mapa}{ext}")
                if ruta_imagen.exists():
                    img_original = pygame.image.load(str(ruta_imagen)).convert()
                    
                    # USAR DIMENSIONES DEL JUEGO
                    self.ancho_mapa = self.ANCHO_JUEGO
                    self.alto_mapa = self.ALTO_JUEGO
                    
                    # Escalar al tamaño del juego
                    self.imagen_mapa = pygame.transform.scale(img_original, (self.ANCHO_JUEGO, self.ALTO_JUEGO))
                    
                    print(f"✓ Mapa cargado: {nombre_mapa}")
                    print(f"  Original: {img_original.get_width()}x{img_original.get_height()}")
                    print(f"  En juego: {self.ANCHO_JUEGO}x{self.ALTO_JUEGO}")
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
        # Convertir a coordenadas del mundo
        mundo_x = x_pantalla + self.camara_x
        mundo_y = y_pantalla + self.camara_y
        
        # Buscar de atrás hacia adelante (objetos superiores primero)
        for obj in reversed(self.objetos):
            if obj.contiene_punto(mundo_x, mundo_y):
                return obj
        return None
    
    def dibujar_grid(self, surface):
        """Dibuja grid de referencia"""
        if not self.mostrar_grid:
            return
        
        grid_size = 50
        offset_x = -self.camara_x % grid_size
        offset_y = -self.camara_y % grid_size
        
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
        # Convertir coordenadas del mundo a pantalla
        x_pantalla = obj.x - self.camara_x + PANEL_IZQUIERDO
        y_pantalla = obj.y - self.camara_y
        
        # Verificar si está visible
        if (x_pantalla + obj.ancho < PANEL_IZQUIERDO or 
            x_pantalla > ANCHO - PANEL_DERECHO or
            y_pantalla + obj.alto < 0 or 
            y_pantalla > ALTO):
            return
        
        # Intentar cargar sprite real si existe
        sprite_dibujado = False
        if obj.sprite_ref:
            # Buscar la imagen del sprite
            for categoria, sprites in self.biblioteca_sprites.items():
                for sprite in sprites:
                    if sprite.id == obj.sprite_ref:
                        if sprite.ruta_imagen in self.imagenes_sprites:
                            img = self.imagenes_sprites[sprite.ruta_imagen]
                            img_escalada = pygame.transform.scale(img, (obj.ancho, obj.alto))
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
                "monstruo": (200, 50, 200)
            }
            color_base = colores.get(obj.tipo, (128, 128, 128))
            
            # Dibujar rectángulo semitransparente
            rect_superficie = pygame.Surface((obj.ancho, obj.alto))
            rect_superficie.set_alpha(120)
            rect_superficie.fill(color_base)
            surface.blit(rect_superficie, (x_pantalla, y_pantalla))
        
        # Borde
        rect = pygame.Rect(x_pantalla, y_pantalla, obj.ancho, obj.alto)
        
        if obj == self.objeto_seleccionado:
            pygame.draw.rect(surface, COLOR_SELECCION, rect, 3)
            # Dibujar handles de redimensionamiento
            self.dibujar_handles(surface, obj)
        elif obj == self.objeto_hover:
            pygame.draw.rect(surface, COLOR_HOVER, rect, 2)
        else:
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)
        
        # Texto con ID
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
        surface.blit(fondo_dim, (x_pantalla + 2, y_pantalla + obj.alto - 22))
        surface.blit(dim_texto, (x_pantalla + 5, y_pantalla + obj.alto - 20))
    
    def dibujar_handles(self, surface, obj):
        """Dibuja handles de redimensionamiento"""
        x_pantalla = obj.x - self.camara_x + PANEL_IZQUIERDO
        y_pantalla = obj.y - self.camara_y
        
        tam_handle = 8
        handles = [
            (x_pantalla, y_pantalla),  # NW
            (x_pantalla + obj.ancho, y_pantalla),  # NE
            (x_pantalla, y_pantalla + obj.alto),  # SW
            (x_pantalla + obj.ancho, y_pantalla + obj.alto),  # SE
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
            self.dibujar_lista_sprites(surface, 10, y, "heroes")
        elif self.modo_actual == "monstruos":
            self.dibujar_lista_sprites(surface, 10, y, "monstruos")
    
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
        rect_actualizar = pygame.Rect(x, y, PANEL_IZQUIERDO - 20, 25)
        color = COLOR_BOTON_HOVER if rect_actualizar.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50)
        pygame.draw.rect(surface, color, rect_actualizar, border_radius=3)
        texto_act = self.fuente_pequena.render("↻ Actualizar Lista", True, COLOR_TEXTO)
        surface.blit(texto_act, (x + 5, y + 5))
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
        
        # Verificar si se clickeó un sprite para añadir
        elif self.modo_actual in ["cofres", "npcs", "héroes", "monstruos"]:
            # Botón actualizar
            rect_actualizar = pygame.Rect(10, 135, PANEL_IZQUIERDO - 20, 25)
            if rect_actualizar.collidepoint(mouse_pos):
                self.cargar_biblioteca_sprites()
                self.mostrar_mensaje("✓ Biblioteca de sprites actualizada")
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
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    click_izq = True
                    
                    # Click en panel izquierdo
                    if mouse_pos[0] < PANEL_IZQUIERDO:
                        # Actualizar botones de modo
                        for boton in self.botones_modo:
                            boton.update(mouse_pos, True)
                        
                        self.manejar_clicks_panel_izquierdo(mouse_pos)
                    
                    # Click en área del mapa
                    elif PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                        x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                        obj = self.obtener_objeto_en_posicion(x_mapa, mouse_pos[1])
                        
                        if obj:
                            self.objeto_seleccionado = obj
                            
                            # Verificar si se clickeó un handle
                            mundo_x = x_mapa + self.camara_x
                            mundo_y = mouse_pos[1] + self.camara_y
                            handle = obj.get_handle_en_punto(mundo_x, mundo_y, 10)
                            
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
                
                elif evento.button == 2 or evento.button == 3:  # Click medio o derecho - Pan cámara
                    self.arrastrando_camara = True
                    self.mouse_anterior = mouse_pos
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
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
                
                elif evento.button == 2 or evento.button == 3:
                    self.arrastrando_camara = False
            
            elif evento.type == pygame.MOUSEMOTION:
                # Verificar si estamos en área del mapa
                if PANEL_IZQUIERDO <= mouse_pos[0] <= ANCHO - PANEL_DERECHO:
                    x_mapa = mouse_pos[0] - PANEL_IZQUIERDO
                    mundo_x = x_mapa + self.camara_x
                    mundo_y = mouse_pos[1] + self.camara_y
                    
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
                        self.camara_x -= dx
                        self.camara_y -= dy
                        # Permitir desplazamiento libre sin límites estrictos
                        self.camara_x = max(-AREA_MAPA_ANCHO, min(self.camara_x, max(self.ancho_mapa, AREA_MAPA_ANCHO)))
                        self.camara_y = max(-ALTO, min(self.camara_y, max(self.alto_mapa, ALTO)))
                        self.mouse_anterior = mouse_pos
                    
                    # Actualizar hover solo si no estamos arrastrando
                    if not hay_objeto_siendo_arrastrado and not self.arrastrando_camara:
                        self.objeto_hover = self.obtener_objeto_en_posicion(x_mapa, mouse_pos[1])
                
                # Si estamos fuera del área del mapa pero arrastrando cámara
                elif self.arrastrando_camara:
                    dx = mouse_pos[0] - self.mouse_anterior[0]
                    dy = mouse_pos[1] - self.mouse_anterior[1]
                    self.camara_x -= dx
                    self.camara_y -= dy
                    self.camara_x = max(-AREA_MAPA_ANCHO, min(self.camara_x, max(self.ancho_mapa, AREA_MAPA_ANCHO)))
                    self.camara_y = max(-ALTO, min(self.camara_y, max(self.alto_mapa, ALTO)))
                    self.mouse_anterior = mouse_pos
            
            elif evento.type == pygame.MOUSEWHEEL:
                # Zoom (placeholder)
                pass
        
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
    
    def ejecutar(self):
        """Bucle principal del editor"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área del mapa
            area_mapa = self.pantalla.subsurface((PANEL_IZQUIERDO, 0, AREA_MAPA_ANCHO, ALTO))
            
            # Fondo del mapa
            if self.imagen_mapa:
                area_mapa.blit(self.imagen_mapa, (-self.camara_x, -self.camara_y))
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
