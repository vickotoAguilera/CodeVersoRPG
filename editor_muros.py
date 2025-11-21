"""
========================================
EDITOR DE MUROS - CodeVerso RPG
========================================
Editor especializado para dibujar muros de colisión en mapas:
✓ Navegación por carpetas de mapas
✓ Secciones desplegables por categoría
✓ Vista del mapa escalada
✓ Dibujo de muros con mouse (click y drag)
✓ Edición y eliminación de muros
✓ Guardado automático en JSON
"""

import pygame
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

# ========================================
# CONFIGURACIÓN
# ========================================
ANCHO = 800
ALTO = 600
FPS = 60
PANEL_ANCHO = 300
AREA_MAPA_ANCHO = ANCHO - PANEL_ANCHO

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

# Colores de muros
COLOR_MURO = (255, 50, 50, 128)  # Rojo semitransparente
COLOR_MURO_BORDE = (255, 255, 255)
COLOR_MURO_SELECCIONADO = (255, 215, 0)
COLOR_MURO_NUEVO = (50, 255, 50, 128)  # Verde para muro en construcción

# ========================================
# CLASES AUXILIARES
# ========================================

@dataclass
class MapaInfo:
    """Información de un mapa disponible"""
    nombre: str          # Nombre del archivo (sin extensión)
    archivo: str         # Nombre completo del archivo PNG
    ruta: str            # Ruta completa al PNG
    categoria: str       # Categoría (mundo, ciudades_y_pueblos, etc)
    subcarpeta: str = "" # Subcarpeta si existe (pueblo_inicio, etc)

@dataclass
class Muro:
    """Representa un muro de colisión rectangular"""
    x: int
    y: int
    w: int
    h: int
    
    def to_dict(self):
        return {"tipo": "rect", "x": self.x, "y": self.y, "w": self.w, "h": self.h}
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def contiene_punto(self, px, py):
        return self.get_rect().collidepoint(px, py)

@dataclass
class MuroPoligonal:
    """Muro adaptable con forma de polígono"""
    puntos: List[Tuple[int, int]]  # Lista de (x, y)
    cerrado: bool = False
    
    def to_dict(self):
        return {"tipo": "poly", "puntos": [[int(p[0]), int(p[1])] for p in self.puntos]}
    
    def contiene_punto(self, px, py):
        if len(self.puntos) < 3:
            return False
        # Algoritmo ray-casting para punto en polígono
        n = len(self.puntos)
        inside = False
        p1x, p1y = self.puntos[0]
        for i in range(n + 1):
            p2x, p2y = self.puntos[i % n]
            if py > min(p1y, p2y):
                if py <= max(p1y, p2y):
                    if px <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or px <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def get_bounding_rect(self):
        if not self.puntos:
            return pygame.Rect(0, 0, 0, 0)
        xs = [p[0] for p in self.puntos]
        ys = [p[1] for p in self.puntos]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return pygame.Rect(int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y))

class SeccionDesplegable:
    """Sección expandible/colapsable para categorías de mapas"""
    def __init__(self, x, y, ancho, titulo, color_titulo=(60, 100, 150)):
        self.rect_titulo = pygame.Rect(x, y, ancho, 40)
        self.titulo = titulo
        self.expandida = False
        self.color_titulo = color_titulo
        self.items: List[MapaInfo] = []
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
    
    def get_item_en_posicion(self, mouse_pos):
        """Retorna el item clickeado (si hay)"""
        if not self.expandida:
            return None
        
        x, y = mouse_pos
        if not (self.rect_titulo.x <= x <= self.rect_titulo.x + self.rect_titulo.width):
            return None
        
        y_item_inicio = self.rect_titulo.y + self.rect_titulo.height + 5
        
        for idx, item in enumerate(self.items):
            rect_item = pygame.Rect(
                self.rect_titulo.x + 10,
                y_item_inicio + idx * 35,
                self.rect_titulo.width - 20,
                30
            )
            if rect_item.collidepoint(mouse_pos):
                return item
        return None
    
    def dibujar(self, surface):
        """Dibuja la sección"""
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
        
        # Items (si está expandida)
        if self.expandida and len(self.items) > 0:
            y_item = self.rect_titulo.y + self.rect_titulo.height + 5
            
            for idx, item in enumerate(self.items):
                y_pos = y_item + idx * 35
                
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
                
                # Nombre del mapa
                nombre_mostrar = item.nombre
                if item.subcarpeta:
                    nombre_mostrar = f"{item.subcarpeta}/{item.nombre}"
                
                nombre_corto = nombre_mostrar[:25] if len(nombre_mostrar) > 25 else nombre_mostrar
                texto_item = self.fuente_item.render(nombre_corto, True, COLOR_TEXTO)
                surface.blit(texto_item, (rect_item.x + 5, rect_item.y + 8))

# ========================================
# CLASE PRINCIPAL
# ========================================

class EditorMuros:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Editor de Muros - CodeVerso RPG")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        # Cargar mapas disponibles
        self.secciones_mapas: List[SeccionDesplegable] = []
        self.cargar_mapas()
        
        # Mapa actual
        self.mapa_actual: Optional[MapaInfo] = None
        self.mapa_imagen = None
        self.mapa_rect = None
        self.escala = 1.0
        
        # Muros
        self.muros: List[Muro] = []
        self.muro_seleccionado: Optional[Muro] = None
        self.muro_hover: Optional[Muro] = None
        
        # Estado de dibujo
        self.dibujando_muro = False
        self.muro_inicio = None  # (x, y) punto inicial
        self.muro_temp = None    # Muro temporal durante el dibujo

        # Arrastre de muros existentes
        self.arrastrando_muro = False
        self.muro_offset_x = 0
        self.muro_offset_y = 0

        # --- NUEVO: Selección múltiple y grupo ---
        self.muros_seleccionados: List[Muro] = []
        self.arrastrando_grupo = False
        self.grupo_offsets: List[Tuple[int,int]] = []  # offsets relativos para cada muro

        # Redimensionamiento
        self.muro_redimensionando = False
        self.handle_activo = None  # 'nw','ne','sw','se'

        # Auto-guardado
        self.cambios_pendientes = False
        self.ultimo_autosave = 0
        self.INTERVALO_AUTOSAVE = 2000  # ms

        # --- NUEVO: Modos de dibujo y pincel ---
        # modos: 'rectangulo', 'pincel', 'borrador', 'poligono'
        self.modo_dibujo = 'rectangulo'
        self.pincel_tamano = 60
        self.pincel_min = 10
        self.pincel_max = 200
        self.mouse_izq_presionado = False
        # Polígono en construcción
        self.poligono_puntos: List[Tuple[int, int]] = []
        self.dibujando_poligono = False
        # Movimiento / pan de cámara
        self.arrastrando_camara = False
        self.mouse_anterior = (0, 0)
        # Zoom dinámico (se inicia con escala que ajusta al área)
        self.zoom = 1.0  # Se igualará a self.escala al cargar mapa

        # Para distinguir click corto derecho (eliminar) vs drag (pan)
        self.click_der_iniciado = False
        self.pos_click_der_inicio = (0, 0)
        
        # Offset de cámara (para mapas grandes)
        self.offset_x = 0
        self.offset_y = 0
        
        # Mensajes
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        # Ventana de ayuda
        self.mostrar_ayuda = False
        
        print("✓ Editor de Muros iniciado")
    
    def cargar_mapas(self):
        """Escanea las carpetas de mapas y crea secciones"""
        base_path = Path("assets/maps")
        
        if not base_path.exists():
            print(f"❌ No se encontró la carpeta: {base_path}")
            return
        
        # Obtener todas las categorías (carpetas principales)
        categorias = [d for d in base_path.iterdir() if d.is_dir()]
        
        y_pos = 50
        for categoria in sorted(categorias):
            # Crear sección para esta categoría
            nombre_categoria = categoria.name.replace("_", " ").title()
            seccion = SeccionDesplegable(10, y_pos, PANEL_ANCHO - 20, nombre_categoria)
            
            # Buscar mapas en esta categoría
            mapas_encontrados = self._buscar_mapas_en_carpeta(categoria, categoria.name)
            seccion.items = mapas_encontrados
            
            if len(seccion.items) > 0:
                self.secciones_mapas.append(seccion)
                y_pos += seccion.get_alto_total() + 10
        
        total_mapas = sum(len(s.items) for s in self.secciones_mapas)
        print(f"✓ Mapas encontrados: {total_mapas} en {len(self.secciones_mapas)} categorías")
    
    def _buscar_mapas_en_carpeta(self, carpeta: Path, categoria: str, subcarpeta: str = "") -> List[MapaInfo]:
        """Busca mapas PNG en una carpeta (recursivo para subcarpetas)"""
        mapas = []
        
        # Buscar PNG y JPG directamente en esta carpeta
        for archivo in list(carpeta.glob("*.png")) + list(carpeta.glob("*.jpg")):
            nombre_sin_ext = archivo.stem
            mapas.append(MapaInfo(
                nombre=nombre_sin_ext,
                archivo=archivo.name,
                ruta=str(archivo),
                categoria=categoria,
                subcarpeta=subcarpeta
            ))
        
        # Buscar en subcarpetas
        for subcarp in carpeta.iterdir():
            if subcarp.is_dir():
                mapas_sub = self._buscar_mapas_en_carpeta(
                    subcarp, 
                    categoria,
                    subcarp.name if not subcarpeta else f"{subcarpeta}/{subcarp.name}"
                )
                mapas.extend(mapas_sub)
        
        return sorted(mapas, key=lambda m: m.nombre)
    
    def cargar_mapa(self, mapa_info: MapaInfo):
        """Carga un mapa para editar"""
        try:
            # Cargar imagen
            self.mapa_imagen_original = pygame.image.load(mapa_info.ruta).convert_alpha()
            self.mapa_rect = self.mapa_imagen_original.get_rect()
            
            # Calcular escala para que quepa en el área actual
            ancho_pantalla, alto_pantalla = self.pantalla.get_size()
            area_ancho = ancho_pantalla - PANEL_ANCHO
            
            escala_x = area_ancho / self.mapa_rect.width
            escala_y = alto_pantalla / self.mapa_rect.height
            self.escala = min(escala_x, escala_y, 1.0)  # No agrandar, solo reducir
            
            # Zoom inicial igual a escala de ajuste
            self.zoom = self.escala
            self._aplicar_zoom_imagen()
            
            self.mapa_actual = mapa_info
            self.offset_x = 0
            self.offset_y = 0
            
            # Cargar muros existentes
            self.cargar_muros_desde_json()
            
            self.mostrar_mensaje(f"✓ Mapa cargado: {mapa_info.nombre} (escala: {self.escala:.2f}x)")
            print(f"✓ Mapa cargado: {mapa_info.ruta}")
            print(f"   Tamaño original: {mapa_info.ruta}")
            print(f"   Escala aplicada: {self.escala:.2f}x")
            
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error al cargar mapa: {e}")
            print(f"❌ Error al cargar mapa: {e}")
    
    def cargar_muros_desde_json(self):
        """Carga los muros existentes del JSON del mapa"""
        if not self.mapa_actual:
            return
        
        # Construir ruta al JSON
        ruta_json = self._get_ruta_json()
        
        if not os.path.exists(ruta_json):
            print(f"  No existe JSON para este mapa (se creará al guardar)")
            self.muros = []
            return
        
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Cargar muros
            self.muros = []
            if "muros" in datos:
                for muro_data in datos["muros"]:
                    tipo = muro_data.get('tipo', 'rect')
                    if tipo == 'poly':
                        puntos = [tuple(p) for p in muro_data['puntos']]
                        muro = MuroPoligonal(puntos=puntos, cerrado=True)
                    else:
                        muro = Muro(
                            x=muro_data['x'],
                            y=muro_data['y'],
                            w=muro_data['w'],
                            h=muro_data['h']
                        )
                    self.muros.append(muro)
            
            print(f"  ✓ Cargados {len(self.muros)} muros desde JSON")
            
        except Exception as e:
            print(f"  ❌ Error al cargar muros: {e}")
            self.muros = []
    
    def _get_ruta_json(self) -> str:
        """Obtiene la ruta al JSON del mapa actual"""
        if not self.mapa_actual:
            return ""
        
        # Construir ruta: src/database/mapas/categoria/[subcarpeta/]nombre.json
        partes = ["src", "database", "mapas", self.mapa_actual.categoria]
        
        if self.mapa_actual.subcarpeta:
            partes.append(self.mapa_actual.subcarpeta)
        
        partes.append(f"{self.mapa_actual.nombre}.json")
        
        return os.path.join(*partes)
    
    def guardar_muros_a_json(self):
        """Guarda los muros al JSON del mapa"""
        if not self.mapa_actual:
            return
        
        ruta_json = self._get_ruta_json()
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta_json), exist_ok=True)
        
        # Cargar datos existentes o crear nuevo
        datos = {}
        if os.path.exists(ruta_json):
            try:
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            except:
                datos = {}
        
        # Actualizar muros
        datos["muros"] = [m.to_dict() for m in self.muros]
        
        # Si no existen, inicializar otras secciones
        if "nombre" not in datos:
            datos["nombre"] = self.mapa_actual.nombre
        if "carpeta" not in datos:
            datos["carpeta"] = self.mapa_actual.categoria
        if "portales" not in datos:
            datos["portales"] = []
        if "zonas_batalla" not in datos:
            datos["zonas_batalla"] = []
        if "cofres" not in datos:
            datos["cofres"] = []
        if "npcs" not in datos:
            datos["npcs"] = []
        
        # Guardar
        try:
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje(f"✓ Guardados {len(self.muros)} muros")
            print(f"✓ Guardado: {ruta_json}")
            
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error al guardar: {e}")
            print(f"❌ Error al guardar: {e}")
    
    def mostrar_mensaje(self, texto):
        """Muestra un mensaje temporal"""
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
    
    def convertir_coords_pantalla_a_mapa(self, x, y):
        """Convierte coordenadas de pantalla a coordenadas del mapa original"""
        # Restar offset de panel
        x_mapa = x - PANEL_ANCHO
        
        # Restar offset de cámara
        x_mapa -= self.offset_x
        y_mapa = y - self.offset_y
        
        # Convertir de coordenadas escaladas (zoom) a originales
        x_original = int(x_mapa / self.zoom)
        y_original = int(y_mapa / self.zoom)
        
        return x_original, y_original
    
    def convertir_coords_mapa_a_pantalla(self, x, y):
        """Convierte coordenadas del mapa original a pantalla"""
        # Aplicar escala
        x_pantalla = int(x * self.zoom)
        y_pantalla = int(y * self.zoom)
        
        # Aplicar offset de cámara
        x_pantalla += self.offset_x
        y_pantalla += self.offset_y
        
        # Aplicar offset de panel
        x_pantalla += PANEL_ANCHO
        
        return x_pantalla, y_pantalla
    
    def get_muro_en_posicion(self, x, y):
        """Obtiene el muro en una posición (coordenadas del mapa original)"""
        for muro in reversed(self.muros):
            if muro.contiene_punto(x, y):
    def _aplicar_zoom_imagen(self):
        if not hasattr(self, 'mapa_imagen_original') or self.mapa_imagen_original is None:
            return
        ancho = int(self.mapa_imagen_original.get_width() * self.zoom)
        alto = int(self.mapa_imagen_original.get_height() * self.zoom)
        self.mapa_imagen = pygame.transform.scale(self.mapa_imagen_original, (ancho, alto))
        self.mapa_rect = self.mapa_imagen.get_rect()

    def _pincel_colocar_muro(self, x, y):
        # Evitar crear duplicados muy juntos
        for muro in self.muros:
            if abs(muro.x - (x - self.pincel_tamano // 2)) < 5 and abs(muro.y - (y - self.pincel_tamano // 2)) < 5 and abs(muro.w - self.pincel_tamano) < 5:
                return
        nuevo = Muro(
            x=int(x - self.pincel_tamano // 2),
            y=int(y - self.pincel_tamano // 2),
            w=int(self.pincel_tamano),
            h=int(self.pincel_tamano)
        )
        self.muros.append(nuevo)
        self.cambios_pendientes = True

    def _borrar_muro_en_pos(self, x, y):
        objetivo = None
        for muro in self.muros:
            if muro.contiene_punto(x, y):
                objetivo = muro
                break
        if objetivo:
            self.muros.remove(objetivo)
            if objetivo in self.muros_seleccionados:
                self.muros_seleccionados.remove(objetivo)
            self.cambios_pendientes = True

    def _detectar_handle_muro(self, muro, x_mapa, y_mapa):
        # Solo handles para muros rectangulares
        if not isinstance(muro, Muro) or isinstance(muro, MuroPoligonal):
            return None
        # Detectar si el punto cae cerca de una esquina (5px en coords mapa)
        margen = 8
        esquinas = {
            'nw': (muro.x, muro.y),
            'ne': (muro.x + muro.w, muro.y),
            'sw': (muro.x, muro.y + muro.h),
            'se': (muro.x + muro.w, muro.y + muro.h)
        }
        for nombre, (hx, hy) in esquinas.items():
            if abs(x_mapa - hx) <= margen and abs(y_mapa - hy) <= margen:
                return nombre
        return None

    def _aplicar_redimension_muro(self, muro: Muro, x_mapa, y_mapa, handle):
        min_size = 5
        if handle == 'se':
            muro.w = max(min_size, x_mapa - muro.x)
            muro.h = max(min_size, y_mapa - muro.y)
        elif handle == 'ne':
            muro.w = max(min_size, x_mapa - muro.x)
            muro.h = max(min_size, (muro.y + muro.h) - y_mapa)
            if muro.h >= min_size:
                muro.y = y_mapa
        elif handle == 'sw':
            muro.w = max(min_size, (muro.x + muro.w) - x_mapa)
            if muro.w >= min_size:
                muro.x = x_mapa
            muro.h = max(min_size, y_mapa - muro.y)
        elif handle == 'nw':
            muro.w = max(min_size, (muro.x + muro.w) - x_mapa)
            if muro.w >= min_size:
                muro.x = x_mapa
            muro.h = max(min_size, (muro.y + muro.h) - y_mapa)
            if muro.h >= min_size:
                muro.y = y_mapa

    def _dibujar_handles_muro(self, surface, muro: Muro):
        # Dibujar pequeños cuadrados en esquinas
        color = (0, 255, 255)
        tam = max(6, int(8 * self.zoom))
        esquinas = [
            (muro.x, muro.y),
            (muro.x + muro.w, muro.y),
            (muro.x, muro.y + muro.h),
            (muro.x + muro.w, muro.y + muro.h)
        ]
        for (hx, hy) in esquinas:
            sx, sy = self.convertir_coords_mapa_a_pantalla(hx, hy)
            pygame.draw.rect(surface, color, (sx - tam//2, sy - tam//2, tam, tam))

    def _fusionar_muros_seleccionados(self):
        if len(self.muros_seleccionados) < 2:
            return
        # Solo fusionar muros rectangulares (excluir poligonales)
        muros_rect = [m for m in self.muros_seleccionados if isinstance(m, Muro) and not isinstance(m, MuroPoligonal)]
        if len(muros_rect) < 2:
            self.mostrar_mensaje("✗ Fusión solo funciona con 2+ muros rectangulares")
            return
        xs = [m.x for m in muros_rect]
        ys = [m.y for m in muros_rect]
        ws = [m.x + m.w for m in muros_rect]
        hs = [m.y + m.h for m in muros_rect]
        min_x, min_y, max_x, max_y = min(xs), min(ys), max(ws), max(hs)
        nuevo = Muro(min_x, min_y, max_x - min_x, max_y - min_y)
        for m in muros_rect:
            if m in self.muros:
                self.muros.remove(m)
        self.muros.append(nuevo)
        self.muros_seleccionados = [nuevo]
        self.muro_seleccionado = nuevo
        self.cambios_pendientes = True
        self.mostrar_mensaje(f"✓ {len(muros_rect)} muros fusionados")

    def _exportar_muros_csv(self):
        if not self.mapa_actual:
            return
        nombre_csv = f"{self.mapa_actual.nombre}_muros.csv"
        ruta_csv = Path("saves") / nombre_csv
        try:
            ruta_csv.parent.mkdir(parents=True, exist_ok=True)
            import csv
            with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["tipo", "datos"])
                for m in self.muros:
                    if isinstance(m, MuroPoligonal):
                        writer.writerow(["poly", str(m.puntos)])
                    else:
                        writer.writerow(["rect", f"{m.x},{m.y},{m.w},{m.h}"])
            self.mostrar_mensaje(f"✓ Exportado CSV: {nombre_csv}")
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error CSV: {e}")
    
    def _finalizar_poligono(self):
        if len(self.poligono_puntos) >= 3:
            nuevo = MuroPoligonal(puntos=self.poligono_puntos[:], cerrado=True)
            self.muros.append(nuevo)
            self.muros_seleccionados = [nuevo]
            self.muro_seleccionado = nuevo
            self.cambios_pendientes = True
            self.mostrar_mensaje(f"✓ Polígono creado ({len(self.poligono_puntos)} vértices)")
        self.poligono_puntos = []
        self.dibujando_poligono = False
    
    def _dibujar_ventana_ayuda(self):
        """Dibuja ventana modal con teclas y funciones"""
        ancho_pantalla, alto_pantalla = self.pantalla.get_size()
        # Fondo semitransparente
        overlay = pygame.Surface((ancho_pantalla, alto_pantalla), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.pantalla.blit(overlay, (0, 0))
        
        # Ventana central
        ventana_w = 700
        ventana_h = 650
        ancho_pantalla, alto_pantalla = self.pantalla.get_size()
        ventana_x = (ancho_pantalla - ventana_w) // 2
        ventana_y = (alto_pantalla - ventana_h) // 2
        ventana_rect = pygame.Rect(ventana_x, ventana_y, ventana_w, ventana_h)
        
        pygame.draw.rect(self.pantalla, COLOR_PANEL, ventana_rect, border_radius=10)
        pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO, ventana_rect, 3, border_radius=10)
        
        # Título
        titulo = self.fuente_titulo.render("ATAJOS DE TECLADO", True, COLOR_SELECCION)
        titulo_rect = titulo.get_rect(centerx=ventana_x + ventana_w // 2, y=ventana_y + 20)
        self.pantalla.blit(titulo, titulo_rect)
        
        # Contenido - lista de teclas
        ayuda_items = [
            ("MODOS DE DIBUJO", ""),
            ("R", "Modo Rectángulo"),
            ("P", "Modo Pincel (dibujo continuo)"),
            ("E", "Modo Borrador"),
            ("L", "Modo Polígono libre"),
            ("", ""),
            ("POLÍGONOS", ""),
            ("Click", "Agregar vértice (modo polígono)"),
            ("Enter", "Finalizar polígono (min 3 puntos)"),
            ("Esc", "Cancelar polígono en progreso"),
            ("", ""),
            ("EDICIÓN", ""),
            ("Click", "Seleccionar muro"),
            ("Shift+Click", "Multi-selección (toggle)"),
            ("Arrastrar", "Mover muro(s) seleccionado(s)"),
            ("Arrastrar esquina", "Redimensionar muro rectangular"),
            ("Click Derecho", "Eliminar muro / Pan si arrastras"),
            ("Rueda Ratón", "Zoom in/out"),
            ("", ""),
            ("PINCEL", ""),
            ("+", "Aumentar tamaño pincel"),
            ("-", "Reducir tamaño pincel"),
            ("", ""),
            ("OTRAS FUNCIONES", ""),
            ("G", "Guardar muros manualmente"),
            ("F", "Fusionar muros seleccionados"),
            ("C", "Exportar muros a CSV"),
            ("DEL", "Eliminar muro(s) seleccionado(s)"),
            ("0", "Resetear zoom a 1:1"),
            ("H / ?", "Mostrar/ocultar esta ayuda"),
        ]
        
        y_actual = ventana_y + 70
        for tecla, descripcion in ayuda_items:
            if not tecla and not descripcion:
                y_actual += 10
                continue
            
            if not descripcion:  # Es título de sección
                texto = self.fuente.render(tecla, True, COLOR_BOTON_ACTIVO)
                self.pantalla.blit(texto, (ventana_x + 30, y_actual))
                y_actual += 25
            else:
                # Tecla en amarillo
                texto_tecla = self.fuente_pequena.render(tecla, True, COLOR_SELECCION)
                self.pantalla.blit(texto_tecla, (ventana_x + 50, y_actual))
                # Descripción en blanco
                texto_desc = self.fuente_pequena.render(descripcion, True, COLOR_TEXTO)
                self.pantalla.blit(texto_desc, (ventana_x + 220, y_actual))
                y_actual += 22
        
        # Pie de página
        pie = self.fuente_pequena.render("Presiona H o ESC para cerrar", True, COLOR_TEXTO_SEC)
        pie_rect = pie.get_rect(centerx=ventana_x + ventana_w // 2, y=ventana_y + ventana_h - 30)
        self.pantalla.blit(pie, pie_rect)

    
    def manejar_eventos(self):
        """Maneja eventos"""
        mouse_pos = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                elif evento.key == pygame.K_g:
                    self.guardar_muros_a_json()
                elif evento.key == pygame.K_DELETE:
                    if self.muros_seleccionados:
                        for m in self.muros_seleccionados:
                            if m in self.muros:
                                self.muros.remove(m)
                        self.muros_seleccionados = []
                        self.muro_seleccionado = None
                        self.mostrar_mensaje("✓ Muros eliminados")
                elif evento.key == pygame.K_f:
                    if len(self.muros_seleccionados) >= 2:
                        self._fusionar_muros_seleccionados()
                elif evento.key == pygame.K_c:
                    if self.mapa_actual:
                        self._exportar_muros_csv()
                # --- NUEVO: Controles de modos de dibujo ---
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
                    # Reset zoom a 1.0 (mostrar mapa original si cabe)
                    if self.mapa_actual and hasattr(self, 'mapa_imagen_original'):
                        self.zoom = 1.0
                        self._aplicar_zoom_imagen()
                        self.mostrar_mensaje("Zoom reiniciado")
                elif evento.key == pygame.K_l:
                    self.modo_dibujo = 'poligono'
                    self.poligono_puntos = []
                    self.dibujando_poligono = False
                    self.mostrar_mensaje("Modo Polígono: Click para agregar puntos | ENTER crea muro | ESC cancela")
                elif evento.key == pygame.K_RETURN:
                    if self.dibujando_poligono:
                        if len(self.poligono_puntos) >= 3:
                            self._finalizar_poligono()
                        else:
                            self.mostrar_mensaje(f"Necesitas al menos 3 puntos (tienes {len(self.poligono_puntos)})")
                elif evento.key == pygame.K_h:
                    self.mostrar_ayuda = not self.mostrar_ayuda
                elif evento.key == pygame.K_ESCAPE:
                    if self.mostrar_ayuda:
                        self.mostrar_ayuda = False
                        return True
                    if self.dibujando_poligono:
                        self.poligono_puntos = []
                        self.dibujando_poligono = False
                        self.mostrar_mensaje("Polígono cancelado - Presiona L para iniciar nuevo")
                        return True  # No salir del editor
                    return False
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    pos = evento.pos
                    # Verificar click en botón ayuda
                    boton_ayuda_rect = pygame.Rect(PANEL_ANCHO - 50, 20, 30, 30)
                    if boton_ayuda_rect.collidepoint(pos):
                        self.mostrar_ayuda = not self.mostrar_ayuda
                        continue
                    
                    self.mouse_izq_presionado = True
                    # Click en panel lateral
                    if mouse_pos[0] < PANEL_ANCHO:
                        # Click en sección
                        for seccion in self.secciones_mapas:
                            if seccion.click_en_titulo(mouse_pos):
                                seccion.toggle()
                                continue
                            
                            # Click en item
                            item = seccion.get_item_en_posicion(mouse_pos)
                            if item:
                                self.cargar_mapa(item)
                                continue
                    
                    # Click en área de mapa
                    elif self.mapa_actual:
                        x_mapa, y_mapa = self.convertir_coords_pantalla_a_mapa(mouse_pos[0], mouse_pos[1])
                        
                        # Verificar si clickeó un muro existente
                        muro_click = self.get_muro_en_posicion(x_mapa, y_mapa)
                        if muro_click:
                            mod_shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                            if mod_shift:
                                # Toggle selección múltiple
                                if muro_click in self.muros_seleccionados:
                                    self.muros_seleccionados.remove(muro_click)
                                else:
                                    self.muros_seleccionados.append(muro_click)
                                self.muro_seleccionado = muro_click
                            else:
                                # Selección única
                                self.muros_seleccionados = [muro_click]
                                self.muro_seleccionado = muro_click
                            # Detectar handles para redimensionar (solo selección única)
                            if len(self.muros_seleccionados) == 1:
                                handle = self._detectar_handle_muro(self.muro_seleccionado, x_mapa, y_mapa)
                                if handle:
                                    self.muro_redimensionando = True
                                    self.handle_activo = handle
                                else:
                                    # Iniciar arrastre (grupo o único)
                                    if len(self.muros_seleccionados) > 1:
                                        self.arrastrando_grupo = True
                                        self.grupo_offsets = []
                                        for m in self.muros_seleccionados:
                                            if isinstance(m, MuroPoligonal):
                                                # Usar primer punto como referencia
                                                px, py = m.puntos[0] if m.puntos else (0, 0)
                                                self.grupo_offsets.append((px - x_mapa, py - y_mapa))
                                            else:
                                                self.grupo_offsets.append((m.x - x_mapa, m.y - y_mapa))
                                    else:
                                        self.arrastrando_muro = True
                                        if isinstance(muro_click, MuroPoligonal):
                                            # Usar primer punto como referencia
                                            px, py = muro_click.puntos[0] if muro_click.puntos else (0, 0)
                                            self.muro_offset_x = px - x_mapa
                                            self.muro_offset_y = py - y_mapa
                                        else:
                                            self.muro_offset_x = muro_click.x - x_mapa
                                            self.muro_offset_y = muro_click.y - y_mapa
                        else:
                            # Modo polígono: agregar punto
                            if self.modo_dibujo == 'poligono':
                                self.poligono_puntos.append((x_mapa, y_mapa))
                                self.dibujando_poligono = True
                            else:
                                # Iniciar dibujo de nuevo muro rectangular
                                self.dibujando_muro = True
                                self.muro_inicio = (x_mapa, y_mapa)
                                self.muro_seleccionado = None
                
                elif evento.button == 3:  # Click derecho
                    # En modo polígono: borrar último punto
                    if self.dibujando_poligono and len(self.poligono_puntos) > 0:
                        self.poligono_puntos.pop()
                        self.mostrar_mensaje(f"← Punto eliminado ({len(self.poligono_puntos)} restantes)")
                        if len(self.poligono_puntos) == 0:
                            self.dibujando_poligono = False
                    else:
                        # Iniciar posible pan o eliminación (se decide al soltar)
                        self.click_der_iniciado = True
                        self.pos_click_der_inicio = mouse_pos
                        self.arrastrando_camara = True
                        self.mouse_anterior = mouse_pos
                elif evento.button == 2:  # Botón medio también pan
                    self.arrastrando_camara = True
                    self.mouse_anterior = mouse_pos
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                # Liberar botón izquierdo
                if evento.button == 1:
                    self.mouse_izq_presionado = False
                    if self.dibujando_muro:
                        # Finalizar dibujo de rectángulo
                        if self.muro_temp and (self.muro_temp.w > 5 and self.muro_temp.h > 5):
                            self.muros.append(self.muro_temp)
                            self.muros_seleccionados = [self.muro_temp]
                            self.muro_seleccionado = self.muro_temp
                            self.cambios_pendientes = True
                            self.mostrar_mensaje(f"✓ Muro creado ({self.muro_temp.w}x{self.muro_temp.h})")
                        self.dibujando_muro = False
                        self.muro_inicio = None
                        self.muro_temp = None
                elif evento.button == 3:
                    # Si no estábamos en modo polígono, procesar como pan/eliminar
                    if not self.dibujando_poligono:
                        # Determinar si fue click corto (eliminar) o drag (pan)
                        distancia = abs(mouse_pos[0] - self.pos_click_der_inicio[0]) + abs(mouse_pos[1] - self.pos_click_der_inicio[1])
                        if distancia < 8 and self.mapa_actual and mouse_pos[0] >= PANEL_ANCHO:
                            x_mapa, y_mapa = self.convertir_coords_pantalla_a_mapa(mouse_pos[0], mouse_pos[1])
                            muro = self.get_muro_en_posicion(x_mapa, y_mapa)
                            if muro:
                                self.muros.remove(muro)
                                if self.muro_seleccionado == muro:
                                    self.muro_seleccionado = None
                                self.mostrar_mensaje("✓ Muro eliminado")
                        self.arrastrando_camara = False
                        self.click_der_iniciado = False
                elif evento.button == 2:
                    self.arrastrando_camara = False
                # Terminar arrastre muro si estaba activo
                if self.arrastrando_muro and evento.button == 1:
                    self.arrastrando_muro = False
                    self.mostrar_mensaje("✓ Muro movido")
                if self.arrastrando_grupo and evento.button == 1:
                    self.arrastrando_grupo = False
                    self.mostrar_mensaje("✓ Grupo movido")
                if self.muro_redimensionando and evento.button == 1:
                    self.muro_redimensionando = False
                    self.handle_activo = None
                    self.mostrar_mensaje("✓ Muro redimensionado")
            
            elif evento.type == pygame.MOUSEMOTION:
                if self.mapa_actual and mouse_pos[0] >= PANEL_ANCHO:
                    x_mapa, y_mapa = self.convertir_coords_pantalla_a_mapa(mouse_pos[0], mouse_pos[1])
                    
                    # Actualizar hover
                    if not self.dibujando_muro:
                        self.muro_hover = self.get_muro_en_posicion(x_mapa, y_mapa)
                    
                    # Actualizar muro temporal durante dibujo
                    if self.dibujando_muro and self.muro_inicio:
                        x1, y1 = self.muro_inicio
                        x2, y2 = x_mapa, y_mapa
                        x = min(x1, x2)
                        y = min(y1, y2)
                        w = abs(x2 - x1)
                        h = abs(y2 - y1)
                        self.muro_temp = Muro(x, y, w, h)

                    # Pincel / Borrador continuos (solo si no estamos dibujando rectángulo)
                    if self.mouse_izq_presionado and not self.dibujando_muro:
                        if self.modo_dibujo == 'pincel':
                            self._pincel_colocar_muro(x_mapa, y_mapa)
                        elif self.modo_dibujo == 'borrador':
                            self._borrar_muro_en_pos(x_mapa, y_mapa)

                    # Arrastre de muro existente
                    if self.arrastrando_muro and self.muro_seleccionado:
                        if isinstance(self.muro_seleccionado, MuroPoligonal):
                            # Calcular desplazamiento para polígono
                            if self.muro_seleccionado.puntos:
                                px_ref, py_ref = self.muro_seleccionado.puntos[0]
                                nueva_x = x_mapa + self.muro_offset_x
                                nueva_y = y_mapa + self.muro_offset_y
                                dx = nueva_x - px_ref
                                dy = nueva_y - py_ref
                                # Mover todos los puntos
                                self.muro_seleccionado.puntos = [(px + dx, py + dy) for (px, py) in self.muro_seleccionado.puntos]
                        else:
                            self.muro_seleccionado.x = x_mapa + self.muro_offset_x
                            self.muro_seleccionado.y = y_mapa + self.muro_offset_y
                        self.cambios_pendientes = True
                    if self.arrastrando_grupo and self.muros_seleccionados:
                        for idx, muro in enumerate(self.muros_seleccionados):
                            offx, offy = self.grupo_offsets[idx]
                            if isinstance(muro, MuroPoligonal):
                                # Calcular desplazamiento
                                if muro.puntos:
                                    px_ref, py_ref = muro.puntos[0]
                                    nueva_x = x_mapa + offx
                                    nueva_y = y_mapa + offy
                                    dx = nueva_x - px_ref
                                    dy = nueva_y - py_ref
                                    muro.puntos = [(px + dx, py + dy) for (px, py) in muro.puntos]
                            else:
                                muro.x = x_mapa + offx
                                muro.y = y_mapa + offy
                        self.cambios_pendientes = True
                    if self.muro_redimensionando and self.muro_seleccionado and self.handle_activo:
                        self._aplicar_redimension_muro(self.muro_seleccionado, x_mapa, y_mapa, self.handle_activo)
                        self.cambios_pendientes = True

                # Pan de cámara (independiente del área)
                if self.arrastrando_camara:
                    dx = mouse_pos[0] - self.mouse_anterior[0]
                    dy = mouse_pos[1] - self.mouse_anterior[1]
                    self.offset_x += dx
                    self.offset_y += dy
                    self.mouse_anterior = mouse_pos

            elif evento.type == pygame.MOUSEWHEEL:
                # Zoom con rueda (solo si hay mapa cargado)
                if self.mapa_actual and hasattr(self, 'mapa_imagen_original'):
                    factor = 1.1 if evento.y > 0 else 0.9
                    self.zoom *= factor
                    self.zoom = max(0.25, min(1.0, self.zoom))  # Max 1.0 = escala real juego
                    self._aplicar_zoom_imagen()
                    self.mostrar_mensaje(f"Zoom: {self.zoom:.2f}x")
        
        # Auto-guardado si hay cambios pendientes
        ahora = pygame.time.get_ticks()
        if self.cambios_pendientes and (ahora - self.ultimo_autosave) > self.INTERVALO_AUTOSAVE:
            self.guardar_muros_a_json()
            self.ultimo_autosave = ahora
            self.cambios_pendientes = False
        return True
    
    def ejecutar(self):
        """Bucle principal"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Panel lateral
            self.dibujar_panel_lateral(self.pantalla)
            
            # Área de mapa
            self.dibujar_area_mapa(self.pantalla)
            
            # Barra de estado
            self.dibujar_barra_estado(self.pantalla)
            
            # Ventana de ayuda modal
            if self.mostrar_ayuda:
                self._dibujar_ventana_ayuda()
            
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
║        EDITOR DE MUROS - CodeVerso RPG                ║
║                                                        ║
║  Características:                                      ║
║  ✓ Navegación por carpetas de mapas                  ║
║  ✓ Vista escalada del mapa                           ║
║  ✓ Dibujo de muros con mouse (click y drag)          ║
║  ✓ Edición y eliminación                             ║
║  ✓ Guardado automático en JSON                       ║
║                                                        ║
║  Controles:                                            ║
║  - Click y arrastra: Dibujar muro                     ║
║  - Click en muro: Seleccionar                         ║
║  - Click derecho: Eliminar muro                       ║
║  - DEL: Eliminar muro seleccionado                    ║
║  - G: Guardar muros                                   ║
║  - ESC: Salir                                         ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    editor = EditorMuros()
    editor.ejecutar()
