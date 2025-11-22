"""
Editor Unificado de Mapas - CodeVerso RPG
==========================================
Editor visual centralizado que muestra y permite editar TODOS los elementos
del mapa en una sola vista: muros, portales, spawns, cofres, NPCs, etc.

Características:
- Vista multi-capa con toggles
- Movimiento y redimensionamiento de cualquier elemento
- Copiar/pegar entre elementos
- Selección múltiple y operaciones en lote
- Grid y snap to grid
- Hot-reload automático de archivos
- Validación de elementos
- Exportación de screenshots
- Sincronización bidireccional con editores específicos
"""

import pygame
import json
import os
import time
import sys
import subprocess
from pathlib import Path
from pathlib import Path
from datetime import datetime

# === CONFIGURACIÓN ===
ANCHO, ALTO = 800, 600
FPS = 60
PANEL_ANCHO = 300
ZOOM_MIN, ZOOM_MAX = 0.25, 3.0

# Colores
COLOR_FONDO = (30, 30, 35)
COLOR_PANEL = (40, 40, 45)
COLOR_TEXTO = (220, 220, 220)
COLOR_HOVER = (70, 70, 80)
COLOR_SELECCION = (100, 150, 255)
COLOR_GRID = (60, 60, 65)

# Colores por tipo de elemento
COLOR_MURO = (255, 100, 100)
COLOR_PORTAL = (100, 150, 255)
COLOR_SPAWN = (100, 255, 150)
COLOR_COFRE = (255, 165, 0)
COLOR_NPC = (200, 100, 255)
COLOR_EVENTO = (255, 255, 255)

# === CLASES DE DATOS ===
class ElementoMapa:
    """Clase base para todos los elementos del mapa"""
    def __init__(self, tipo, id, x, y, ancho, alto, datos=None, puntos=None):
        self.tipo = tipo  # 'muro', 'portal', 'spawn', 'cofre', 'npc'
        self.id = id
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.datos = datos or {}  # Datos específicos del elemento
        self.puntos = puntos  # Para polígonos
        self.seleccionado = False
        self.color = self._get_color()
    
    def _get_color(self):
        colores = {
            'muro': COLOR_MURO,
            'portal': COLOR_PORTAL,
            'spawn': COLOR_SPAWN,
            'cofre': COLOR_COFRE,
            'npc': COLOR_NPC,
            'evento': COLOR_EVENTO
        }
        return colores.get(self.tipo, (200, 200, 200))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        if self.puntos:
            # Polígono: usar ray casting
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
        else:
            # Rectángulo
            return self.get_rect().collidepoint(px, py)

class MapaInfo:
    def __init__(self, nombre, categoria, ruta_json, ruta_imagen):
        self.nombre = nombre
        self.categoria = categoria
        self.ruta_json = ruta_json
        self.ruta_imagen = ruta_imagen

# === EDITOR PRINCIPAL ===
class EditorUnificado:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Editor Unificado - CodeVerso RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fuentes
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Mapa actual
        self.mapa_actual = None
        self.mapa_img = None
        self.mapa_zoom = 1.0
        self.mapa_offset_x = 0
        self.mapa_offset_y = 0
        
        # Elementos del mapa
        self.elementos = []  # Lista de todos los elementos
        self.elementos_seleccionados = []  # Lista de elementos seleccionados
        
        # Capas visibles - TODAS VISIBLES POR DEFECTO para ver elementos superpuestos
        self.capas_visibles = {
            'muros': True,
            'portales': True,
            'spawns': True,
            'cofres': True,
            'npcs': True,
            'eventos': True
        }
        # Estados de expansión por capa (mostrar lista de elementos)
        self.capas_expandidas = {k: False for k in self.capas_visibles.keys()}
        # Hitboxes para el control de expandir/contraer y para cada elemento expandido
        self.capas_expanded_hitboxes = {}
        
        # Navegación
        self.panning = False
        self.ultimo_mouse_pos = (0, 0)
        
        # Edición
        self.elemento_hover = None
        self.arrastrando = False
        self.redimensionando = False
        self.borde_seleccionado = None
        self.offset_arrastre = (0, 0)
        
        # Copiar/pegar
        self.elementos_copiados = []
        
        # Grid
        self.grid_visible = True
        self.grid_size = 32
        self.snap_to_grid = False
        
        # Hot-reload
        self.archivos_modificados = {}
        self.ultimo_check = time.time()
        
        # UI
        self.mostrar_info = True
        self.mostrar_ayuda = False
        self.mensaje_guardado = None
        self.tiempo_mensaje_guardado = 0
        self.mostrar_selector_mapas = False
        self.mapas_por_categoria = {}
        self.categorias_expandidas = {}
        self.scroll_mapas = 0
        # Hitboxes para UI (generadas al dibujar)
        self.capas_hitboxes = {}
        # Hitbox para el botón de selector de mapas (panel)
        self.boton_mapas_rect = None
        self.selector_hitboxes = {'categorias': {}, 'mapas': [], 'cerrar': None}
        
        # Validación
        self.elementos_con_error = []
        
        # Confirmación de borrado
        self.confirmar_borrado = False
        self.tiempo_confirmacion_borrado = 0
        
        # Cargar mapas disponibles
        self._cargar_lista_mapas()
        self._agrupar_mapas_por_categoria()
        
        # Cargar base de datos de cofres para sprites
        self.cofres_db = self._cargar_json("src/database/cofres_db.json")
        
        print("Editor Unificado iniciado")
        print("H: Ayuda | G: Grid | S: Snap | V: Validar | E: Exportar | M: Mapas")
    
    def _cargar_json(self, ruta):
        """Carga un archivo JSON de forma segura"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando JSON {ruta}: {e}")
            return {}

    def _cargar_lista_mapas(self):
        """Carga lista de mapas disponibles"""
        self.mapas_disponibles = []
        
        ruta_mapas = Path("src/database/mapas")
        if not ruta_mapas.exists():
            print(f"[!] No se encontró: {ruta_mapas}")
            return
        
        # Buscar recursivamente en todas las subcarpetas
        for json_file in ruta_mapas.rglob("*.json"):
            nombre = json_file.stem
            
            # FILTRAR archivos que NO son mapas completos
            # Excluir archivos parciales (muros, portales, spawns, cofres individuales)
            if any(palabra in nombre.lower() for palabra in ['_muros', '_portales', '_spawns', '_cofres', '_batalla']):
                continue
            
            # Excluir archivos de test
            if nombre.lower().startswith('test_'):
                continue
            
            # Verificar que el JSON tenga estructura de mapa completo
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Un mapa completo debe tener al menos una de estas claves
                if not any(key in data for key in ['muros', 'portales', 'spawns', 'zonas_batalla', 'cofres']):
                    print(f"  [SKIP] {nombre} - no parece un mapa completo")
                    continue
            except:
                # Si no se puede leer, saltar
                continue
            
            # Categoría relativa a src/database/mapas
            categoria_rel = json_file.relative_to(ruta_mapas).parent
            
            # Buscar imagen correspondiente
            ruta_img = self._buscar_imagen_mapa(str(categoria_rel), nombre)
            
            # Agregar mapa incluso si no tiene imagen (se creará placeholder al cargar)
            mapa_info = MapaInfo(nombre, str(categoria_rel), json_file, ruta_img)
            self.mapas_disponibles.append(mapa_info)
        
        print(f"[OK] Cargados {len(self.mapas_disponibles)} mapas")
    
    def _agrupar_mapas_por_categoria(self):
        """Agrupa mapas por categoría para el selector"""
        self.mapas_por_categoria = {}
        
        for mapa in self.mapas_disponibles:
            if mapa.categoria not in self.mapas_por_categoria:
                self.mapas_por_categoria[mapa.categoria] = []
                self.categorias_expandidas[mapa.categoria] = False  # Colapsado por defecto
            
            self.mapas_por_categoria[mapa.categoria].append(mapa)
        
        # Ordenar categorías y mapas
        for categoria in self.mapas_por_categoria:
            self.mapas_por_categoria[categoria].sort(key=lambda m: m.nombre)
    
    def _buscar_imagen_mapa(self, categoria, nombre):
        """Busca la imagen del mapa"""
        # Primero buscar en la categoría exacta
        base_path = Path("assets/maps") / categoria
        
        if base_path.exists():
            for ext in ['.png', '.jpg', '.jpeg']:
                # Buscar recursivamente
                for img in base_path.rglob(f"{nombre}{ext}"):
                    return img
                for img in base_path.rglob(f"{nombre.upper()}{ext}"):
                    return img
                for img in base_path.rglob(f"{nombre.lower()}{ext}"):
                    return img
        
        # Si no encuentra, buscar en toda la carpeta assets/maps
        base_path = Path("assets/maps")
        for ext in ['.png', '.jpg', '.jpeg']:
            for img in base_path.rglob(f"{nombre}{ext}"):
                return img
            for img in base_path.rglob(f"{nombre.upper()}{ext}"):
                return img
            for img in base_path.rglob(f"{nombre.lower()}{ext}"):
                return img
        
        # Si aún no encuentra, crear imagen placeholder
        print(f"[!] No se encontró imagen para: {nombre}")
        return None
    
    def cargar_mapa(self, mapa_info):
        """Carga un mapa y todos sus elementos"""
        print(f"\n[>>] Cargando mapa: {mapa_info.nombre}")
        
        self.mapa_actual = mapa_info
        self.elementos = []
        
        # Cargar imagen del mapa
        if mapa_info.ruta_imagen and Path(mapa_info.ruta_imagen).exists():
            try:
                self.mapa_img = pygame.image.load(str(mapa_info.ruta_imagen)).convert()
                print(f"  [OK] Imagen cargada: {Path(mapa_info.ruta_imagen).name}")
            except Exception as e:
                print(f"  [!] Error cargando imagen: {e}")
                self._crear_imagen_placeholder()
        else:
            print(f"  [!] No se encontro imagen del mapa")
            self._crear_imagen_placeholder()
        
        # Cargar elementos del mapa
        self._cargar_muros(mapa_info.nombre)
        self._cargar_portales(mapa_info.nombre)
        self._cargar_spawns(mapa_info.nombre)
        self._cargar_cofres(mapa_info.ruta_json)
        
        # Configurar zoom y offset iniciales
        if self.mapa_img:
            ancho_img = self.mapa_img.get_width()
            alto_img = self.mapa_img.get_height()
            viewport_ancho = ANCHO - PANEL_ANCHO
            viewport_alto = ALTO
            
            zoom_x = viewport_ancho / ancho_img
            zoom_y = viewport_alto / alto_img
            self.mapa_zoom = min(zoom_x, zoom_y, 1.0)
            
            self.mapa_offset_x = (viewport_ancho - ancho_img * self.mapa_zoom) // 2
            self.mapa_offset_y = (viewport_alto - alto_img * self.mapa_zoom) // 2
        
        # Actualizar timestamps para hot-reload
        self._actualizar_timestamps()
        
        print(f"[OK] Mapa cargado: {len(self.elementos)} elementos totales")
    
    def _crear_imagen_placeholder(self):
        """Crea una imagen placeholder dinámica basada en los elementos cargados"""
        if not self.elementos:
            # Si no hay elementos, crear placeholder fijo
            ancho, alto = 800, 600
            self.mapa_img = pygame.Surface((ancho, alto))
            self.mapa_img.fill((60, 60, 70))
            self.mapa_offset_x = 0
            self.mapa_offset_y = 0
            return
        
        # Calcular bounding box de todos los elementos
        min_x = min(elem.x for elem in self.elementos)
        min_y = min(elem.y for elem in self.elementos)
        max_x = max(elem.x + elem.ancho for elem in self.elementos)
        max_y = max(elem.y + elem.alto for elem in self.elementos)
        
        # Añadir margen
        margen = 32
        ancho = int(max_x - min_x + 2 * margen)
        alto = int(max_y - min_y + 2 * margen)
        
        # Crear superficie
        self.mapa_img = pygame.Surface((ancho, alto))
        self.mapa_img.fill((60, 60, 70))
        
        # Dibujar grid
        for x in range(0, ancho, 32):
            pygame.draw.line(self.mapa_img, (70, 70, 75), (x, 0), (x, alto))
        for y in range(0, alto, 32):
            pygame.draw.line(self.mapa_img, (70, 70, 75), (0, y), (ancho, y))
        
        # Ajustar offsets para que el origen del mapa esté correctamente posicionado
        self.mapa_offset_x = -int(min_x - margen)
        self.mapa_offset_y = -int(min_y - margen)
        
        print(f"  [OK] Placeholder dinamico creado: {ancho}x{alto} px")
    
    def _cargar_muros(self, nombre_mapa):
        """Carga muros desde JSON del mapa"""
        try:
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            muros_data = data.get('muros', [])
            print(f"  DEBUG: Encontrados {len(muros_data)} muros")
            
            for i, muro in enumerate(muros_data):
                # Determinar si es polígono o rectángulo
                tipo_muro = 'rect'
                if 'puntos' in muro or muro.get('forma') == 'poly':
                    tipo_muro = 'poly'
                
                if tipo_muro == 'poly':
                    # Polígono: calcular bounding box
                    puntos = muro.get('puntos', [])
                    if puntos:
                        xs = [p[0] for p in puntos]
                        ys = [p[1] for p in puntos]
                        x_min, x_max = min(xs), max(xs)
                        y_min, y_max = min(ys), max(ys)
                        
                        elemento = ElementoMapa(
                            tipo='muro',
                            id=f'M{i+1}',
                            x=x_min,
                            y=y_min,
                            ancho=x_max - x_min,
                            alto=y_max - y_min,
                            datos=muro,
                            puntos=puntos
                        )
                        self.elementos.append(elemento)
                
                elif tipo_muro == 'rect':
                    # Rectángulo
                    elemento = ElementoMapa(
                        tipo='muro',
                        id=f'M{i+1}',
                        x=muro['x'],
                        y=muro['y'],
                        ancho=muro['w'],
                        alto=muro['h'],
                        datos=muro
                    )
                    self.elementos.append(elemento)
        
        except Exception as e:
            print(f"[!] Error cargando muros: {e}")
    
    def _cargar_portales(self, nombre_mapa):
        """Carga portales desde JSON del mapa"""
        try:
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            portales_data = data.get('portales', [])
            print(f"  DEBUG: Claves en JSON: {list(data.keys())}")
            if portales_data:
                print(f"  DEBUG: Encontrados {len(portales_data)} portales")
            else:
                print("  DEBUG: No se encontró la clave 'portales' o está vacía")
            
            for i, portal in enumerate(portales_data):
                # Soportar diferentes estructuras, incluyendo polígonos ('puntos')
                # 1) Polígono: tiene 'puntos' o 'forma' == 'poly'
                if portal.get('forma') == 'poly' or 'puntos' in portal:
                    puntos = portal.get('puntos', [])
                    if puntos:
                        xs = [p[0] for p in puntos]
                        ys = [p[1] for p in puntos]
                        x_min, x_max = min(xs), max(xs)
                        y_min, y_max = min(ys), max(ys)

                        elemento = ElementoMapa(
                            tipo='portal',
                            id=f'P{i+1}',
                            x=x_min,
                            y=y_min,
                            ancho=x_max - x_min,
                            alto=y_max - y_min,
                            datos=portal,
                            puntos=puntos
                        )
                        self.elementos.append(elemento)
                        print(f"    [OK] Portal P{i+1} (poly) cargado en bbox ({x_min}, {y_min})")
                        continue

                # 2) Estructura con 'caja'
                if 'caja' in portal:
                    caja = portal['caja']
                    x = caja.get('x', 0)
                    y = caja.get('y', 0)
                    ancho = caja.get('w', 64)
                    alto = caja.get('h', 64)
                else:
                    # 3) Estructura antigua con x, y, w, h directos
                    x = portal.get('x', 0)
                    y = portal.get('y', 0)
                    ancho = portal.get('w', portal.get('ancho', 64))
                    alto = portal.get('h', portal.get('alto', 64))

                elemento = ElementoMapa(
                    tipo='portal',
                    id=f'P{i+1}',
                    x=x,
                    y=y,
                    ancho=ancho,
                    alto=alto,
                    datos=portal
                )
                self.elementos.append(elemento)
                print(f"    [OK] Portal P{i+1} cargado en ({x}, {y})")
        
        except Exception as e:
            print(f"[!] Error cargando portales: {e}")
    
    def _cargar_spawns(self, nombre_mapa):
        """Carga zonas de spawn desde JSON del mapa"""
        try:
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Buscar spawns en diferentes estructuras
            spawns_data = data.get('zonas_batalla', []) or data.get('spawns', [])
            if spawns_data:
                print(f"  DEBUG: Encontrados {len(spawns_data)} spawns (zonas_batalla/spawns)")
            else:
                print("  DEBUG: No se encontraron 'zonas_batalla' ni 'spawns'")
            
            for i, zona in enumerate(spawns_data):
                # Soportar diferentes estructuras
                if 'caja' in zona:
                    # Estructura con 'caja'
                    caja = zona['caja']
                    x = caja.get('x', 0)
                    y = caja.get('y', 0)
                    ancho = caja.get('w', 100)
                    alto = caja.get('h', 100)
                elif 'x' in zona and 'y' in zona:
                    # Estructura con x, y directos (punto de spawn)
                    x = zona.get('x', 0)
                    y = zona.get('y', 0)
                    ancho = zona.get('w', zona.get('tam', 32))  # tam a ancho
                    alto = zona.get('h', zona.get('tam', 32))
                else:
                    continue
                
                elemento = ElementoMapa(
                    tipo='spawn',
                    id=f'S{i+1}',
                    x=x,
                    y=y,
                    ancho=ancho,
                    alto=alto,
                    datos=zona
                )
                self.elementos.append(elemento)
                print(f"    [OK] Spawn S{i+1} cargado en ({x}, {y})")
        
        except Exception as e:
            print(f"[!] Error cargando spawns: {e}")
    
    def _cargar_cofres(self, ruta_json):
        """Carga cofres desde JSON del mapa"""
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for cofre in data.get('cofres', []):
                elemento = ElementoMapa(
                    tipo='cofre',
                    id=cofre.get('id', 'C?'),
                    x=cofre['x'],
                    y=cofre['y'],
                    ancho=cofre.get('ancho', 64),
                    alto=cofre.get('alto', 64),
                    datos=cofre
                )
                self.elementos.append(elemento)
        
        except Exception as e:
            print(f"[!] Error cargando cofres: {e}")
    
    def _actualizar_timestamps(self):
        """Guarda timestamps de archivos para hot-reload"""
        if not self.mapa_actual:
            return
        # Simplificar: vigilar únicamente el JSON principal del mapa para hot-reload.
        ruta_principal = Path(self.mapa_actual.ruta_json)
        self.archivos_modificados = {}
        if ruta_principal.exists():
            self.archivos_modificados['mapa_json'] = ruta_principal.stat().st_mtime
    
    def _check_hot_reload(self):
        """Verifica si hay cambios en archivos y recarga"""
        if not self.mapa_actual:
            return
        
        # Check cada 1 segundo para mejor respuesta
        now = time.time()
        if now - self.ultimo_check < 1.0:
            return

        self.ultimo_check = now

        # Vigilar el JSON principal del mapa
        ruta_principal = Path(self.mapa_actual.ruta_json)
        cambios = []
        if ruta_principal.exists():
            mtime = ruta_principal.stat().st_mtime
            prev = self.archivos_modificados.get('mapa_json')
            if prev is None or prev < mtime:
                cambios.append('mapa_json')
                self.archivos_modificados['mapa_json'] = mtime

        # Vigilar el índice global de mapas (para detectar nuevos mapas creados fuera)
        ruta_indice = Path('src/database/maps_index.json')
        if ruta_indice.exists():
            try:
                mtime_idx = ruta_indice.stat().st_mtime
                prev_idx = self.archivos_modificados.get('maps_index')
                if prev_idx is None or prev_idx < mtime_idx:
                    cambios.append('maps_index')
                    self.archivos_modificados['maps_index'] = mtime_idx
            except Exception:
                pass
        
        if cambios:
            print(f"\n[RELOAD] Hot-reload: Cambios detectados en {', '.join(cambios)}")
            # Guardar estado de selección y zoom actual
            zoom_actual = self.mapa_zoom
            offset_x = self.mapa_offset_x
            offset_y = self.mapa_offset_y
            
            # Recargar elementos
            self.elementos = []
            self.elementos_seleccionados = []
            self._cargar_muros(self.mapa_actual.nombre)
            self._cargar_portales(self.mapa_actual.nombre)
            self._cargar_spawns(self.mapa_actual.nombre)
            self._cargar_cofres(self.mapa_actual.ruta_json)

            # Si cambió el índice global, recargar la lista de mapas y agrupaciones
            if 'maps_index' in cambios:
                print('[RELOAD] maps_index cambiado: recargando lista de mapas')
                self._cargar_lista_mapas()
                self._agrupar_mapas_por_categoria()
            
            # Restaurar zoom y offset
            self.mapa_zoom = zoom_actual
            self.mapa_offset_x = offset_x
            self.mapa_offset_y = offset_y
            
            print(f"[OK] Recargados {len(self.elementos)} elementos")
    
    def _guardar_archivo_unificado(self):
        """Genera el archivo unificado consolidando todos los elementos con metadata"""
        if not self.mapa_actual:
            return False
        
        print("\n[UNIFY] Generando archivo unificado...")
        
        # Crear directorio si no existe
        dir_unificados = Path("src/database/mapas_unificados")
        dir_unificados.mkdir(parents=True, exist_ok=True)
        
        # Nombre del archivo unificado
        nombre_archivo = dir_unificados / f"{self.mapa_actual.nombre}_unificado.json"
        
        # Agrupar elementos por tipo
        elementos_por_tipo = {
            'muro': [],
            'portal': [],
            'spawn': [],
            'cofre': [],
            'npc': [],
            'evento': []
        }
        
        for elem in self.elementos:
            if elem.tipo in elementos_por_tipo:
                # Actualizar datos del elemento con posición/tamaño actual
                datos = elem.datos.copy()
                
                if elem.puntos:
                    # Polígono: actualizar puntos
                    datos['puntos'] = elem.puntos
                else:
                    # Rectángulo: actualizar coordenadas
                    if elem.tipo == 'portal' and 'caja' in datos:
                        datos['caja']['x'] = elem.x
                        datos['caja']['y'] = elem.y
                        datos['caja']['w'] = elem.ancho
                        datos['caja']['h'] = elem.alto
                    elif elem.tipo == 'spawn' and 'caja' in datos:
                        datos['caja']['x'] = elem.x
                        datos['caja']['y'] = elem.y
                        datos['caja']['w'] = elem.ancho
                        datos['caja']['h'] = elem.alto
                    else:
                        datos['x'] = elem.x
                        datos['y'] = elem.y
                        datos['w'] = elem.ancho
                        datos['h'] = elem.alto
                
                elementos_por_tipo[elem.tipo].append(datos)
        
        # Construir estructura unificada con metadata
        estructura_unificada = {
            "metadata": {
                "mapa_base": self.mapa_actual.nombre,
                "categoria": str(self.mapa_actual.categoria),
                "imagen": str(self.mapa_actual.ruta_imagen.name) if self.mapa_actual.ruta_imagen else None,
                "ultima_modificacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version_editor": "1.0",
                "editado_por": "Editor Unificado"
            },
            "muros": elementos_por_tipo['muro'],
            "portales": elementos_por_tipo['portal'],
            "spawns": elementos_por_tipo['spawn'],
            "cofres": elementos_por_tipo['cofre'],
            "npcs": elementos_por_tipo['npc'],
            "eventos": elementos_por_tipo['evento']
        }
        
        # Guardar archivo
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(estructura_unificada, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Archivo unificado guardado: {nombre_archivo.name}")
            print(f"     - Muros: {len(elementos_por_tipo['muro'])}")
            print(f"     - Portales: {len(elementos_por_tipo['portal'])}")
            print(f"     - Spawns: {len(elementos_por_tipo['spawn'])}")
            print(f"     - Cofres: {len(elementos_por_tipo['cofre'])}")
            return True
        except Exception as e:
            print(f"[X] Error guardando archivo unificado: {e}")
            return False
    
    def guardar_cambios(self):
        """Guarda todos los cambios en los archivos correspondientes Y genera archivo unificado"""
        if not self.mapa_actual:
            return
        
        print("\n[SAVE] Guardando cambios...")
        
        nombre = self.mapa_actual.nombre
        
        # Agrupar elementos por tipo
        elementos_por_tipo = {
            'muro': [],
            'portal': [],
            'spawn': [],
            'cofre': []
        }
        
        for elem in self.elementos:
            if elem.tipo in elementos_por_tipo:
                elementos_por_tipo[elem.tipo].append(elem)
        
        # Guardar muros
        self._guardar_muros(nombre, elementos_por_tipo['muro'])
        
        # Guardar portales (con validación)
        ok_portales = self._guardar_portales(nombre, elementos_por_tipo['portal'])
        if not ok_portales:
            print('[X] Guardado cancelado por validación de portales')
            return
        
        # Guardar spawns
        self._guardar_spawns(nombre, elementos_por_tipo['spawn'])
        
        # Guardar cofres
        self._guardar_cofres(elementos_por_tipo['cofre'])
        
        self._actualizar_timestamps()
        
        # Generar archivo unificado
        exito_unificado = self._guardar_archivo_unificado()
        
        if exito_unificado:
            print("[OK] Cambios guardados y archivo unificado generado")
            # Mensaje visual
            self.mensaje_guardado = "[OK] GUARDADO + UNIFICADO"
            self.tiempo_mensaje_guardado = time.time()
        else:
            print("[OK] Cambios guardados (error en unificado)")
            self.mensaje_guardado = "[OK] GUARDADO"
            self.tiempo_mensaje_guardado = time.time()
        
        # Actualizar índice de mapas y ejecutar merge unificador
        try:
            gen = Path('tools') / 'generate_maps_index.py'
            if gen.exists():
                print('Actualizando índice de mapas...')
                subprocess.run([sys.executable, str(gen)], check=False)
            # Ejecutar merge unificador para consolidar parciales
            merge = Path('tools') / 'merge_map_parts.py'
            if merge.exists():
                print('Ejecutando merge de parciales...')
                subprocess.run([sys.executable, str(merge), '--apply'], check=False)
        except Exception as e:
            print('[!] Error al actualizar índice/merge:', e)
    
    def _guardar_muros(self, nombre_mapa, muros):
        """Guarda muros en JSON del mapa"""
        try:
            # Leer JSON completo del mapa
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Actualizar solo los muros
            data['muros'] = []
            for muro in muros:
                if muro.puntos:
                    # Polígono: actualizar puntos si se movió
                    muro.datos['puntos'] = muro.puntos
                else:
                    # Rectángulo: actualizar coordenadas
                    muro.datos['x'] = muro.x
                    muro.datos['y'] = muro.y
                    muro.datos['w'] = muro.ancho
                    muro.datos['h'] = muro.alto
                data['muros'].append(muro.datos)
            
            # Guardar
            with open(self.mapa_actual.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"[X] Error guardando muros: {e}")
    
    def _guardar_portales(self, nombre_mapa, portales):
        """Guarda portales en JSON del mapa"""
        try:
            # Leer JSON completo del mapa
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Actualizar solo los portales
            data['portales'] = []
            # Validación: verificar que ningún portal tenga 'mapa_destino' vacío (cadena vacía)
            for portal in portales:
                md = portal.datos.get('mapa_destino') if isinstance(portal.datos, dict) else None
                if md is not None and isinstance(md, str) and md.strip() == '':
                    print(f"[!] Portal inválido: {portal.datos} -> mapa_destino vacío")
                    return False

            for portal in portales:
                # Si el portal es poligonal, actualizar 'puntos' si es necesario
                if portal.puntos:
                    portal.datos['puntos'] = portal.puntos
                    # Opcional: mantener forma explícita
                    portal.datos['forma'] = portal.datos.get('forma', 'poly')
                else:
                    # Asegurar que exista la subestructura 'caja'
                    if 'caja' not in portal.datos:
                        portal.datos['caja'] = {}
                    portal.datos['caja']['x'] = portal.x
                    portal.datos['caja']['y'] = portal.y
                    portal.datos['caja']['w'] = portal.ancho
                    portal.datos['caja']['h'] = portal.alto

                data['portales'].append(portal.datos)
            
            # Guardar
            with open(self.mapa_actual.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"[X] Error guardando portales: {e}")
    
    def _guardar_spawns(self, nombre_mapa, spawns):
        """Guarda spawns en JSON del mapa"""
        try:
            # Leer JSON completo del mapa
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Actualizar solo las zonas de batalla
            data['zonas_batalla'] = []
            for spawn in spawns:
                # Si el spawn tiene caja en sus datos, actualizarla
                if 'caja' in spawn.datos and isinstance(spawn.datos['caja'], dict):
                    spawn.datos['caja']['x'] = spawn.x
                    spawn.datos['caja']['y'] = spawn.y
                    spawn.datos['caja']['w'] = spawn.ancho
                    spawn.datos['caja']['h'] = spawn.alto
                    data['zonas_batalla'].append(spawn.datos)
                elif 'x' in spawn.datos and 'y' in spawn.datos:
                    # Spawn definido como punto (x,y,tam,direccion)
                    nueva = spawn.datos.copy()
                    nueva['x'] = spawn.x
                    nueva['y'] = spawn.y
                    # actualizar tam si existe
                    if 'tam' in nueva:
                        nueva['tam'] = spawn.ancho
                    data['zonas_batalla'].append(nueva)
                else:
                    # Fallback: escribir como caja
                    nueva = {'caja': {'x': spawn.x, 'y': spawn.y, 'w': spawn.ancho, 'h': spawn.alto}}
                    data['zonas_batalla'].append(nueva)
            
            # Guardar
            with open(self.mapa_actual.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"[X] Error guardando spawns: {e}")
    
    def _guardar_cofres(self, cofres):
        """Guarda cofres en JSON del mapa"""
        try:
            with open(self.mapa_actual.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['cofres'] = []
            for cofre in cofres:
                cofre.datos['x'] = cofre.x
                cofre.datos['y'] = cofre.y
                cofre.datos['ancho'] = cofre.ancho
                cofre.datos['alto'] = cofre.alto
                data['cofres'].append(cofre.datos)
            
            with open(self.mapa_actual.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"[X] Error guardando cofres: {e}")
    
    def _get_capa_key(self, tipo):
        """Devuelve la clave correcta para el diccionario de capas"""
        mapa_plural = {
            'muro': 'muros',
            'portal': 'portales',
            'spawn': 'spawns',
            'cofre': 'cofres',
            'npc': 'npcs',
            'evento': 'eventos'
        }
        return mapa_plural.get(tipo, tipo + 's')

    def _screen_to_map(self, screen_x, screen_y):
        """Convierte coordenadas de pantalla a coordenadas del mapa"""
        map_x = (screen_x - PANEL_ANCHO - self.mapa_offset_x) / self.mapa_zoom
        map_y = (screen_y - self.mapa_offset_y) / self.mapa_zoom
        return int(map_x), int(map_y)
    
    def _map_to_screen(self, map_x, map_y):
        """Convierte coordenadas del mapa a coordenadas de pantalla"""
        screen_x = map_x * self.mapa_zoom + self.mapa_offset_x + PANEL_ANCHO
        screen_y = map_y * self.mapa_zoom + self.mapa_offset_y
        return int(screen_x), int(screen_y)
    
    def _snap_to_grid(self, x, y):
        """Ajusta coordenadas al grid si snap está activo"""
        if not self.snap_to_grid:
            return x, y
        
        grid = self.grid_size
        return (x // grid) * grid, (y // grid) * grid
    
    def _get_elemento_en_posicion(self, mx, my):
        """Obtiene el elemento bajo el mouse (solo si capa visible)"""
        mx_map, my_map = self._screen_to_map(mx, my)
        
        # Revisar en orden inverso (últimos elementos primero)
        for elemento in reversed(self.elementos):
            capa = self._get_capa_key(elemento.tipo)
            if not self.capas_visibles.get(capa, True):
                continue
            
            if elemento.contiene_punto(mx_map, my_map):
                return elemento
        
        return None
    
    def _detectar_borde(self, elemento, mx, my):
        """Detecta si el mouse está en un borde del elemento"""
        mx_map, my_map = self._screen_to_map(mx, my)
        
        margen = 8 / self.mapa_zoom
        rect = elemento.get_rect()
        
        cerca_izq = abs(mx_map - rect.left) < margen
        cerca_der = abs(mx_map - rect.right) < margen
        cerca_arr = abs(my_map - rect.top) < margen
        cerca_aba = abs(my_map - rect.bottom) < margen
        
        if cerca_arr and cerca_izq: return 'nw'
        if cerca_arr and cerca_der: return 'ne'
        if cerca_aba and cerca_izq: return 'sw'
        if cerca_aba and cerca_der: return 'se'
        if cerca_arr: return 'n'
        if cerca_aba: return 's'
        if cerca_izq: return 'w'
        if cerca_der: return 'e'
        
        return None
    
    def run(self):
        """Loop principal"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Hot-reload
            self._check_hot_reload()
            
            self._handle_events()
            self._update()
            self._draw()
        
        pygame.quit()
    
    def _handle_events(self):
        """Maneja eventos"""
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.guardar_cambios()
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self._handle_click_izquierdo(mx, my)
                elif event.button == 3:  # Click derecho
                    self._handle_click_derecho(mx, my)
                elif event.button == 4:  # Rueda arriba
                    if self.mostrar_selector_mapas and mx < PANEL_ANCHO:
                        self.scroll_mapas = max(0, self.scroll_mapas - 30)
                    else:
                        self.mapa_zoom = min(self.mapa_zoom * 1.1, ZOOM_MAX)
                elif event.button == 5:  # Rueda abajo
                    if self.mostrar_selector_mapas and mx < PANEL_ANCHO:
                        self.scroll_mapas += 30
                    else:
                        self.mapa_zoom = max(self.mapa_zoom / 1.1, ZOOM_MIN)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.arrastrando = False
                    self.redimensionando = False
                elif event.button == 3:
                    self.panning = False
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(mx, my)
    
    def _handle_keydown(self, event):
        """Maneja teclas"""
        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL
        sh = mods & pygame.KMOD_SHIFT
        
        if event.key == pygame.K_ESCAPE:
            self.guardar_cambios()
            self.running = False
        
        elif event.key == pygame.K_g:
            if ctrl:
                self.guardar_cambios()
            else:
                self.grid_visible = not self.grid_visible
        
        elif event.key == pygame.K_s and not ctrl:
            self.snap_to_grid = not self.snap_to_grid
            print(f"Snap to grid: {'ON' if self.snap_to_grid else 'OFF'}")
        
        elif event.key == pygame.K_h:
            self.mostrar_ayuda = not self.mostrar_ayuda
        
        elif event.key == pygame.K_i:
            self.mostrar_info = not self.mostrar_info
        
        elif event.key == pygame.K_DELETE:
            if self.elementos_seleccionados:
                # Primera vez: pedir confirmación
                if not self.confirmar_borrado:
                    self.confirmar_borrado = True
                    self.tiempo_confirmacion_borrado = time.time()
                    print(f"[!] Presiona DELETE de nuevo para confirmar borrado de {len(self.elementos_seleccionados)} elementos")
                # Segunda vez (dentro de 3 segundos): borrar
                elif time.time() - self.tiempo_confirmacion_borrado < 3.0:
                    for elem in self.elementos_seleccionados:
                        self.elementos.remove(elem)
                    print(f"[OK] Eliminados {len(self.elementos_seleccionados)} elementos")
                    self.elementos_seleccionados = []
                    self.confirmar_borrado = False
                else:
                    # Timeout: reiniciar confirmación
                    self.confirmar_borrado = True
                    self.tiempo_confirmacion_borrado = time.time()
                    print(f"[!] Presiona DELETE de nuevo para confirmar borrado de {len(self.elementos_seleccionados)} elementos")
        
        elif event.key == pygame.K_c and ctrl:
            if self.elementos_seleccionados:
                self.elementos_copiados = [e for e in self.elementos_seleccionados]
                print(f"[OK] Copiados {len(self.elementos_copiados)} elementos")
        
        elif event.key == pygame.K_v and ctrl:
            if self.elementos_copiados:
                mx, my = pygame.mouse.get_pos()
                mx_map, my_map = self._screen_to_map(mx, my)
                
                # Calcular offset desde el primer elemento
                if self.elementos_copiados:
                    offset_x = mx_map - self.elementos_copiados[0].x
                    offset_y = my_map - self.elementos_copiados[0].y
                    
                    nuevos = []
                    for elem_orig in self.elementos_copiados:
                        # Crear copia
                        nuevo_id = self._generar_id(elem_orig.tipo)
                        datos_copia = elem_orig.datos.copy()
                        datos_copia['id'] = nuevo_id
                        
                        nuevo_elem = ElementoMapa(
                            tipo=elem_orig.tipo,
                            id=nuevo_id,
                            x=elem_orig.x + offset_x,
                            y=elem_orig.y + offset_y,
                            ancho=elem_orig.ancho,
                            alto=elem_orig.alto,
                            datos=datos_copia
                        )
                        self.elementos.append(nuevo_elem)
                        nuevos.append(nuevo_elem)
                    
                    # Seleccionar los nuevos
                    for elem in self.elementos:
                        elem.seleccionado = False
                    for elem in nuevos:
                        elem.seleccionado = True
                    self.elementos_seleccionados = nuevos
                    
                    print(f"[OK] Pegados {len(nuevos)} elementos")
        
        elif event.key == pygame.K_a and ctrl:
            # Seleccionar todos
            self.elementos_seleccionados = [e for e in self.elementos 
                                           if self.capas_visibles.get(self._get_capa_key(e.tipo), True)]
            for elem in self.elementos_seleccionados:
                elem.seleccionado = True
            print(f"[OK] Seleccionados {len(self.elementos_seleccionados)} elementos")
        
        elif event.key == pygame.K_v and not ctrl:
            # Validar
            self._validar_elementos()
        
        elif event.key == pygame.K_e:
            # Exportar
            # Ctrl+Shift+E -> exportar mapa al repo (JSON + copiar imagen si aplica)
            if ctrl and sh:
                # Ejecutar exportador CLI
                try:
                    src_json = str(self.mapa_actual.ruta_json)
                    img = str(self.mapa_actual.ruta_imagen) if self.mapa_actual.ruta_imagen else None
                    categoria = self.mapa_actual.categoria if getattr(self.mapa_actual, 'categoria', None) else ''
                    cmd = [sys.executable, str(Path('tools') / 'export_map.py'), '--src-json', src_json, '--categoria', categoria]
                    if img:
                        cmd += ['--image', img]
                    print('Exportando mapa con comando:', ' '.join(cmd))
                    subprocess.run(cmd, check=False)
                except Exception as e:
                    print('[!] Error exportando mapa:', e)
            else:
                # Exportar screenshot (comportamiento original)
                self._exportar_screenshot()
        
        elif event.key == pygame.K_m:
            # Toggle selector de mapas
            self.mostrar_selector_mapas = not self.mostrar_selector_mapas
    
    def _generar_id(self, tipo):
        """
        Genera un ID único para el tipo de elemento.
        
        LÓGICA DE AUTO-INCREMENTO CON RELLENO DE HUECOS:
        - Si hay huecos en la secuencia (ej: C1, C2, C4), usa el primer hueco (C3)
        - Si no hay huecos, incrementa al siguiente número (ej: C1, C2, C3 -> C4)
        
        Ejemplo:
        - IDs existentes: [C1, C3, C5] -> Nuevo ID: C2 (rellena hueco)
        - IDs existentes: [C1, C2, C3] -> Nuevo ID: C4 (incrementa)
        """
        prefijos = {
            'muro': 'M',
            'portal': 'P',
            'spawn': 'S',
            'cofre': 'C',
            'npc': 'N'
        }
        
        prefijo = prefijos.get(tipo, 'X')
        
        # Obtener todos los números de IDs existentes del mismo tipo
        ids_existentes = [int(e.id[1:]) for e in self.elementos 
                         if e.tipo == tipo and e.id[1:].isdigit()]
        
        if not ids_existentes:
            # No hay elementos de este tipo, empezar en 1
            nuevo_num = 1
        else:
            # Ordenar los IDs existentes
            ids_existentes.sort()
            
            # Buscar el primer hueco en la secuencia
            nuevo_num = None
            for i in range(1, max(ids_existentes) + 1):
                if i not in ids_existentes:
                    nuevo_num = i
                    break
            
            # Si no hay huecos, incrementar al siguiente
            if nuevo_num is None:
                nuevo_num = max(ids_existentes) + 1
        
        return f"{prefijo}{nuevo_num}"
    
    def _handle_click_izquierdo(self, mx, my):
        """Maneja click izquierdo"""
        if mx < PANEL_ANCHO:
            # Click en panel
            self._handle_click_panel(mx, my)
            return
        
        if not self.mapa_actual:
            return
        
        # Click en viewport
        elemento = self._get_elemento_en_posicion(mx, my)
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        
        if elemento:
            # Detectar si está en borde para redimensionar
            borde = self._detectar_borde(elemento, mx, my)
            
            if borde:
                # Iniciar redimensionamiento
                self.redimensionando = True
                self.borde_seleccionado = borde
                if not elemento.seleccionado:
                    if not ctrl:
                        for e in self.elementos:
                            e.seleccionado = False
                        self.elementos_seleccionados = []
                    elemento.seleccionado = True
                    self.elementos_seleccionados.append(elemento)
            else:
                # Selección
                if ctrl:
                    # Agregar/quitar de selección
                    if elemento.seleccionado:
                        elemento.seleccionado = False
                        self.elementos_seleccionados.remove(elemento)
                    else:
                        elemento.seleccionado = True
                        self.elementos_seleccionados.append(elemento)
                else:
                    # Selección simple
                    if not elemento.seleccionado:
                        for e in self.elementos:
                            e.seleccionado = False
                        elemento.seleccionado = True
                        self.elementos_seleccionados = [elemento]
                
                # Iniciar arrastre
                self.arrastrando = True
                mx_map, my_map = self._screen_to_map(mx, my)
                self.offset_arrastre = (mx_map - elemento.x, my_map - elemento.y)
        else:
            # Click en vacío - deseleccionar
            if not ctrl:
                for e in self.elementos:
                    e.seleccionado = False
                self.elementos_seleccionados = []
    
    def _handle_click_derecho(self, mx, my):
        """Maneja click derecho - inicia panning de cámara"""
        if mx < PANEL_ANCHO:
            return
        
        if not self.mapa_actual:
            return
        
        # Iniciar panning
        self.panning = True
        self.ultimo_mouse_pos = (mx, my)
        # Primer, manejar filas normales (checkbox filas)
        for capa, rect in self.capas_hitboxes.items():
            # Soporte para filas expandidas agrupadas bajo la clave '_expanded_items'
            if capa == '_expanded_items':
                continue
            if rect.collidepoint(mx, my):
                self.capas_visibles[capa] = not self.capas_visibles.get(capa, True)
                print(f"{capa}: {'ON' if self.capas_visibles[capa] else 'OFF'}")
                return

        # Segundo, manejar control de expandir/contraer (chevrons)
        for capa, rect in self.capas_expanded_hitboxes.items():
            if rect.collidepoint(mx, my):
                # Toggle expansion
                self.capas_expandidas[capa] = not self.capas_expandidas.get(capa, False)
                return

        # Tercero, clicks sobre elementos listados cuando una capa está expandida
        expanded_items = self.capas_hitboxes.get('_expanded_items', {})
        for capa, items in expanded_items.items():
            for elem, rect in items:
                if rect.collidepoint(mx, my):
                    # Centrar la vista en el elemento (si hay mapa cargado) o seleccionarlo
                    # Esto es un comportamiento útil: centrar en el elemento en el viewport
                    if hasattr(self, 'mapa_img') and self.mapa_img:
                        # Mover offset para centrar
                        centro_x = elem.x + elem.ancho // 2
                        centro_y = elem.y + elem.alto // 2
                        ancho_viewport = ANCHO - PANEL_ANCHO
                        alto_viewport = ALTO
                        self.mapa_offset_x = (ancho_viewport // 2) - int(centro_x * self.mapa_zoom)
                        self.mapa_offset_y = (alto_viewport // 2) - int(centro_y * self.mapa_zoom)
                    # Seleccionar elemento
                    for e in self.elementos:
                        e.seleccionado = False
                    elem.seleccionado = True
                    self.elementos_seleccionados = [elem]
                    return
    def _handle_mouse_motion(self, mx, my):
        """Maneja movimiento del mouse"""
        if self.panning:
            dx = mx - self.ultimo_mouse_pos[0]
            dy = my - self.ultimo_mouse_pos[1]
            self.mapa_offset_x += dx
            self.mapa_offset_y += dy
            self.ultimo_mouse_pos = (mx, my)
        
        elif self.arrastrando and self.elementos_seleccionados:
            mx_map, my_map = self._screen_to_map(mx, my)
            
            # Calcular nueva posición
            primer_elem = self.elementos_seleccionados[0]
            nueva_x = mx_map - self.offset_arrastre[0]
            nueva_y = my_map - self.offset_arrastre[1]
            
            # Snap to grid
            if self.snap_to_grid:
                nueva_x, nueva_y = self._snap_to_grid(nueva_x, nueva_y)
            
            # Calcular desplazamiento
            dx = nueva_x - primer_elem.x
            dy = nueva_y - primer_elem.y
            
            # Mover todos los seleccionados
            for elem in self.elementos_seleccionados:
                elem.x += dx
                elem.y += dy
                
                # Si es polígono, mover todos los puntos
                if elem.puntos:
                    elem.puntos = [[px + dx, py + dy] for px, py in elem.puntos]
        
        elif self.redimensionando and self.elementos_seleccionados:
            elemento = self.elementos_seleccionados[0]
            mx_map, my_map = self._screen_to_map(mx, my)
            
            borde = self.borde_seleccionado
            
            if 'n' in borde:
                nueva_y = int(my_map)
                diff = elemento.y - nueva_y
                elemento.y = nueva_y
                elemento.alto += diff
            if 's' in borde:
                elemento.alto = int(my_map - elemento.y)
            if 'w' in borde:
                nueva_x = int(mx_map)
                diff = elemento.x - nueva_x
                elemento.x = nueva_x
                elemento.ancho += diff
            if 'e' in borde:
                elemento.ancho = int(mx_map - elemento.x)
            
            # Asegurar tamaños mínimos
            if elemento.ancho < 16:
                elemento.ancho = 16
            if elemento.alto < 16:
                elemento.alto = 16
        
        else:
            # Actualizar hover
            self.elemento_hover = self._get_elemento_en_posicion(mx, my)
    
    def _handle_click_panel(self, mx, my):
        """Maneja clicks en el panel"""
        # Selector de mapas
        # Si se ha pulsado el botón de mapas en el panel, alternar selector
        if self.boton_mapas_rect and self.boton_mapas_rect.collidepoint(mx, my):
            self.mostrar_selector_mapas = not self.mostrar_selector_mapas
            return

        if self.mostrar_selector_mapas:
            self._handle_click_selector_mapas(mx, my)
            return
        
        # Primero verificar clicks en chevrones de expansión (tienen prioridad)
        for capa, chevron_rect in self.capas_expanded_hitboxes.items():
            if chevron_rect.collidepoint(mx, my):
                self.capas_expandidas[capa] = not self.capas_expandidas.get(capa, False)
                print(f"{'v' if self.capas_expandidas[capa] else '>'} {capa}: {'EXPANDIDO' if self.capas_expandidas[capa] else 'CONTRAÍDO'}")
                return
        
        # Verificar clicks en elementos expandidos (para seleccionarlos)
        if '_expanded_items' in self.capas_hitboxes:
            for capa, items_list in self.capas_hitboxes['_expanded_items'].items():
                for elem, item_rect in items_list:
                    if item_rect.collidepoint(mx, my):
                        # Seleccionar este elemento
                        for e in self.elementos:
                            e.seleccionado = False
                        elem.seleccionado = True
                        self.elementos_seleccionados = [elem]
                        print(f"Seleccionado: {elem.tipo} {elem.id}")
                        return
        
        # Toggles de capas (checkbox) - área clickeable más grande
        # Usar hitboxes generadas durante el draw para asegurar coincidencia visual
        for capa, rect in self.capas_hitboxes.items():
            if capa == '_expanded_items':  # Skip internal key
                continue
            if rect.collidepoint(mx, my):
                self.capas_visibles[capa] = not self.capas_visibles.get(capa, True)
                print(f"{capa}: {'ON' if self.capas_visibles[capa] else 'OFF'}")
                return
    
    def _handle_click_selector_mapas(self, mx, my):
        """Maneja clicks en el selector de mapas"""
        # Usar hitboxes generadas por el dibujado
        # Cerrar
        if self.selector_hitboxes.get('cerrar') and self.selector_hitboxes['cerrar'].collidepoint(mx, my):
            self.mostrar_selector_mapas = False
            return

        # Mapas (lista de tuplas (mapa, rect)) - ya no hay categorías
        for mapa, rect in self.selector_hitboxes.get('mapas', []):
            if rect.collidepoint(mx, my):
                print(f"\n[>>] Cambiando a mapa: {mapa.nombre}")
                self.cargar_mapa(mapa)
                self.mostrar_selector_mapas = False
                return
    
    def _update(self):
        """Actualiza estado"""
        pass
    
    def _draw(self):
        """Dibuja todo"""
        self.screen.fill(COLOR_FONDO)
        
        # Panel lateral
        self._draw_panel()
        
        # Viewport
        if self.mapa_actual and self.mapa_img:
            self._draw_viewport()
        
        # Ayuda
        if self.mostrar_ayuda:
            self._draw_ayuda()
        
        # Info
        if self.mostrar_info:
            self._draw_info()
        
        pygame.display.flip()
    
    def _draw_panel(self):
        """Dibuja panel lateral"""
        pygame.draw.rect(self.screen, COLOR_PANEL, (0, 0, PANEL_ANCHO, ALTO))
        
        # Título
        titulo = self.font.render("Editor Unificado", True, COLOR_TEXTO)
        self.screen.blit(titulo, (10, 10))
        
        # Botón selector de mapas
        boton_mapas = pygame.Rect(10, 45, PANEL_ANCHO - 20, 25)
        color_boton = (60, 60, 80) if not self.mostrar_selector_mapas else (80, 100, 120)
        pygame.draw.rect(self.screen, color_boton, boton_mapas)
        pygame.draw.rect(self.screen, (100, 100, 120), boton_mapas, 2)
        # Guardar hitbox del botón para interacción (click)
        self.boton_mapas_rect = boton_mapas
        
        if self.mapa_actual:
            # Mostrar solo el nombre del mapa para mantenerlo limpio
            texto = self.font_tiny.render(f"[>>] {self.mapa_actual.nombre}", True, COLOR_TEXTO)
            self.screen.blit(texto, (20, 52))
        else:
            texto = self.font_tiny.render("[>>] Sin mapa (M: Abrir)", True, (150, 150, 150))
            self.screen.blit(texto, (20, 52))
        
        # Selector de mapas (si está activo)
        if self.mostrar_selector_mapas:
            self._draw_selector_mapas()
            return
        
        # Capas
        y = 100
        texto = self.font_small.render("CAPAS:", True, COLOR_TEXTO)
        self.screen.blit(texto, (10, y))
        y += 30
        # Reset hitboxes
        self.capas_hitboxes = {}

        # Mapear plural->singular para contar correctamente (evita 'portale')
        singular_map = {
            'muros': 'muro',
            'portales': 'portal',
            'spawns': 'spawn',
            'cofres': 'cofre',
            'npcs': 'npc',
            'eventos': 'evento'
        }

        for capa, visible in self.capas_visibles.items():
            # Fondo hover
            rect_hover = pygame.Rect(10, y, PANEL_ANCHO - 20, 25)
            mx, my = pygame.mouse.get_pos()
            if rect_hover.collidepoint(mx, my):
                pygame.draw.rect(self.screen, (50, 50, 60), rect_hover)

            # Checkbox
            rect_check = pygame.Rect(20, y + 2, 20, 20)
            pygame.draw.rect(self.screen, (100, 100, 100), rect_check, 2)
            if visible:
                pygame.draw.rect(self.screen, (100, 255, 100), rect_check.inflate(-6, -6))

            # Nombre
            tipo_singular = singular_map.get(capa, capa[:-1])
            count = len([e for e in self.elementos if e.tipo == tipo_singular])
            texto = self.font_tiny.render(f"{capa.capitalize()} ({count})", True, COLOR_TEXTO)
            self.screen.blit(texto, (50, y + 2))

            # Color indicator
            color_tipo = {
                'muros': COLOR_MURO,
                'portales': COLOR_PORTAL,
                'spawns': COLOR_SPAWN,
                'cofres': COLOR_COFRE,
                'npcs': COLOR_NPC
            }
            color = color_tipo.get(capa, (200, 200, 200))
            pygame.draw.rect(self.screen, color, (PANEL_ANCHO - 40, y, 30, 20))

            # Expand/collapse control (small chevron on the right of the row)
            chevron_x = PANEL_ANCHO - 14
            chevron_rect = pygame.Rect(chevron_x, y, 12, 20)
            flecha = "v" if self.capas_expandidas.get(capa, False) else ">"
            chev_txt = self.font_tiny.render(flecha, True, COLOR_TEXTO)
            self.screen.blit(chev_txt, (chevron_x - 6, y + 2))
            # Guardar hitbox del control
            self.capas_expanded_hitboxes[capa] = chevron_rect

            # Si la capa está expandida, mostrar breve lista de elementos (IDs)
            if self.capas_expandidas.get(capa, False):
                # Extraer elementos del tipo correspondiente
                tipo_singular = singular_map.get(capa, capa[:-1])
                lista_elem = [e for e in self.elementos if e.tipo == tipo_singular]
                ey = y + 28
                max_visible = 6
                self.capas_hitboxes.setdefault('_expanded_items', {})
                self.capas_hitboxes['_expanded_items'].setdefault(capa, [])
                self.capas_hitboxes['_expanded_items'][capa] = []
                for i, elem in enumerate(lista_elem[:max_visible]):
                    txt = self.font_tiny.render(f"  - {elem.id}", True, (180, 180, 180))
                    self.screen.blit(txt, (20, ey + i * 18))
                    row_rect = pygame.Rect(10, ey + i * 18, PANEL_ANCHO - 20, 18)
                    self.capas_hitboxes['_expanded_items'][capa].append((elem, row_rect))
                # Ajustar y para siguientes filas del panel
                y += 18 * min(len(lista_elem), max_visible)

            # Guardar hitbox completa de la fila
            self.capas_hitboxes[capa] = rect_hover

            y += 30
        
        # Hot-reload status
        y = ALTO - 240
        texto = self.font_small.render("HOT-RELOAD:", True, COLOR_TEXTO)
        self.screen.blit(texto, (10, y))
        y += 22
        tiempo_check = int(time.time() - self.ultimo_check)
        texto = self.font_tiny.render(f"Último check: {tiempo_check}s", True, (150, 200, 150))
        self.screen.blit(texto, (15, y))
        y += 18
        
        # Controles
        y += 10
        texto = self.font_small.render("CONTROLES:", True, COLOR_TEXTO)
        self.screen.blit(texto, (10, y))
        y += 25
        
        controles = [
            "M: Mapas",
            "H: Ayuda",
            "Ctrl+G: Guardar",
            "G: Grid",
            "S: Snap",
            "I: Info",
            "V: Validar",
            "E: Exportar"
        ]
        
        for control in controles:
            texto = self.font_tiny.render(control, True, (150, 150, 150))
            self.screen.blit(texto, (15, y))
            y += 18
    
    def _draw_selector_mapas(self):
        """Dibuja el selector de mapas como lista simple (sin categorías)"""
        # Fondo
        pygame.draw.rect(self.screen, (35, 35, 40), (0, 80, PANEL_ANCHO, ALTO - 80))
        
        # Título
        texto = self.font_small.render("SELECCIONAR MAPA:", True, COLOR_TEXTO)
        self.screen.blit(texto, (10, 85))
        
        # Instrucciones
        texto = self.font_tiny.render("Click mapa = cargar", True, (150, 150, 150))
        self.screen.blit(texto, (10, 110))
        texto = self.font_tiny.render("M = cerrar selector", True, (150, 150, 150))
        self.screen.blit(texto, (10, 125))
        
        # Lista PLANA de mapas (sin categorías)
        y = 155 - self.scroll_mapas
        # Resetear hitboxes del selector
        self.selector_hitboxes = {'categorias': {}, 'mapas': [], 'cerrar': None}

        # Crear lista plana de todos los mapas
        todos_mapas = []
        for categoria in sorted(self.mapas_por_categoria.keys()):
            for mapa in self.mapas_por_categoria[categoria]:
                todos_mapas.append(mapa)
        
        # Dibujar cada mapa
        for i, mapa in enumerate(todos_mapas):
            if y > 155 and y < ALTO - 50:  # Solo dibujar si está visible
                # Highlight si es el mapa actual
                es_actual = self.mapa_actual and mapa.nombre == self.mapa_actual.nombre
                color_fondo = (70, 100, 70) if es_actual else (45, 45, 50)

                rect_mapa = pygame.Rect(10, y, PANEL_ANCHO - 20, 22)
                pygame.draw.rect(self.screen, color_fondo, rect_mapa)
                pygame.draw.rect(self.screen, (60, 60, 70), rect_mapa, 1)

                # Nombre del mapa (solo nombre, sin categoría)
                nombre_display = mapa.nombre[:25] + "..." if len(mapa.nombre) > 25 else mapa.nombre
                color_texto = (100, 255, 100) if es_actual else (200, 200, 200)
                texto = self.font_tiny.render(f"  {nombre_display}", True, color_texto)
                self.screen.blit(texto, (15, y + 3))

                # Guardar hitbox para este mapa
                self.selector_hitboxes['mapas'].append((mapa, rect_mapa))

            y += 25
        
        # Botón cerrar
        boton_cerrar = pygame.Rect(10, ALTO - 40, PANEL_ANCHO - 20, 30)
        pygame.draw.rect(self.screen, (80, 50, 50), boton_cerrar)
        pygame.draw.rect(self.screen, (120, 70, 70), boton_cerrar, 2)
        texto = self.font_small.render("CERRAR (M)", True, COLOR_TEXTO)
        texto_rect = texto.get_rect(center=boton_cerrar.center)
        self.screen.blit(texto, texto_rect)
    
    def _draw_viewport(self):
        """Dibuja viewport con mapa y elementos"""
        # Mapa
        ancho_scaled = int(self.mapa_img.get_width() * self.mapa_zoom)
        alto_scaled = int(self.mapa_img.get_height() * self.mapa_zoom)
        img_scaled = pygame.transform.scale(self.mapa_img, (ancho_scaled, alto_scaled))
        
        x_img = PANEL_ANCHO + self.mapa_offset_x
        y_img = self.mapa_offset_y
        self.screen.blit(img_scaled, (x_img, y_img))
        
        # Grid
        if self.grid_visible:
            self._draw_grid(x_img, y_img, ancho_scaled, alto_scaled)
        
        # Elementos
        for elemento in self.elementos:
            # Solo dibujar si capa visible
            capa = self._get_capa_key(elemento.tipo)
            if not self.capas_visibles.get(capa, True):
                continue
            
            self._draw_elemento(elemento)
    
    def _draw_grid(self, x_offset, y_offset, ancho, alto):
        """Dibuja grid"""
        grid_size_scaled = int(self.grid_size * self.mapa_zoom)
        
        # Líneas verticales
        x = x_offset
        while x < x_offset + ancho:
            pygame.draw.line(self.screen, COLOR_GRID, (x, y_offset), (x, y_offset + alto), 1)
            x += grid_size_scaled
        
        # Líneas horizontales
        y = y_offset
        while y < y_offset + alto:
            pygame.draw.line(self.screen, COLOR_GRID, (x_offset, y), (x_offset + ancho, y), 1)
            y += grid_size_scaled
    
    def _get_sprite_image(self, ruta_relativa):
        """Carga y cachea una imagen de sprite"""
        if not hasattr(self, 'imagenes_sprites'):
            self.imagenes_sprites = {}
            
        if not ruta_relativa:
            return None
            
        if ruta_relativa in self.imagenes_sprites:
            return self.imagenes_sprites[ruta_relativa]
            
        # Intentar cargar - CORREGIDO: ruta directa a cofres y demas
        full_path = Path("assets/sprites/cofres y demas") / ruta_relativa
        # Si la ruta ya incluye "assets/...", intentar usarla directa o ajustarla
        if "assets" in ruta_relativa:
             full_path = Path(ruta_relativa)
             
        if not full_path.exists():
             # Intentar buscar solo por nombre de archivo en la carpeta de cofres y demas
             nombre = Path(ruta_relativa).name
             found = list(Path("assets/sprites/cofres y demas").rglob(nombre))
             if found:
                 full_path = found[0]
             else:
                 return None
        
        try:
            img = pygame.image.load(str(full_path)).convert_alpha()
            self.imagenes_sprites[ruta_relativa] = img
            return img
        except Exception as e:
            print(f"Error cargando sprite {full_path}: {e}")
            return None

    def _draw_elemento(self, elemento):
        """Dibuja un elemento"""
        color = elemento.color
        
        if elemento.seleccionado:
            borde_color = COLOR_SELECCION
            borde_width = 3
            alpha = 100
        elif elemento == self.elemento_hover:
            borde_color = (255, 255, 255)
            borde_width = 2
            alpha = 80
        else:
            borde_color = color
            borde_width = 2
            alpha = 50
        
        if elemento.puntos:
            # Dibujar polígono
            puntos_screen = [self._map_to_screen(px, py) for px, py in elemento.puntos]
            
            # Fondo semi-transparente
            if len(puntos_screen) >= 3:
                pygame.draw.polygon(self.screen, (*color, alpha), puntos_screen)
                pygame.draw.polygon(self.screen, borde_color, puntos_screen, borde_width)
            
            # ID en el centro del bounding box
            x, y = self._map_to_screen(elemento.x, elemento.y)
            ancho = int(elemento.ancho * self.mapa_zoom)
            alto = int(elemento.alto * self.mapa_zoom)
            if ancho > 40 and alto > 20:
                centro_x = x + ancho // 2
                centro_y = y + alto // 2
                texto_id = self.font_tiny.render(elemento.id, True, (255, 255, 255))
                texto_rect = texto_id.get_rect(center=(centro_x, centro_y))
                self.screen.blit(texto_id, texto_rect)
        else:
            # Dibujar rectángulo
            x, y = self._map_to_screen(elemento.x, elemento.y)
            ancho = int(elemento.ancho * self.mapa_zoom)
            alto = int(elemento.alto * self.mapa_zoom)
            
            rect = pygame.Rect(x, y, ancho, alto)
            
            # Renderizado especial para cofres con sprite
            sprite_dibujado = False
            if elemento.tipo == 'cofre':
                # Intentar obtener sprite del dato del elemento
                sprite_path = elemento.datos.get('sprite_cerrado')
                
                # Si no tiene, intentar buscar en cofres_db por ID o tipo
                if not sprite_path and hasattr(self, 'cofres_db'):
                    cofre_id = elemento.id
                    # Buscar en cofres_mapa por ID
                    cofre_info = self.cofres_db.get("cofres_mapa", {}).get(cofre_id)
                    if cofre_info:
                        sprite_path = cofre_info.get("sprite_cerrado")
                
                # Si aún no tiene sprite, usar default por tipo
                if not sprite_path:
                    # Intentar obtener tipo del cofre (puede estar en datos o ser desconocido)
                    tipo_cofre = elemento.datos.get('tipo', 'madera')
                    defaults = {
                        "madera": "cofre_madera_1.png",
                        "bronce": "cofre_madera_2.png", 
                        "plata": "cofre_madera_3.png",
                        "oro": "cofre.png",
                        "especial": "cofre.png"
                    }
                    sprite_path = defaults.get(tipo_cofre)

                if sprite_path:
                    sprite_img = self._get_sprite_image(sprite_path)
                    if sprite_img:
                        img_scaled = pygame.transform.scale(sprite_img, (ancho, alto))
                        self.screen.blit(img_scaled, rect)
                        pygame.draw.rect(self.screen, borde_color, rect, borde_width)
                        sprite_dibujado = True
            
            if not sprite_dibujado:
                # Fondo semi-transparente standard
                surface = pygame.Surface((ancho, alto), pygame.SRCALPHA)
                surface.fill((*color, alpha))
                
                self.screen.blit(surface, rect)
                pygame.draw.rect(self.screen, borde_color, rect, borde_width)
            
            # ID del elemento
            if ancho > 40 and alto > 20:
                texto_id = self.font_tiny.render(elemento.id, True, (255, 255, 255))
                texto_rect = texto_id.get_rect(center=rect.center)
                self.screen.blit(texto_id, texto_rect)
    
    def _draw_info(self):
        """Dibuja información en pantalla"""
        y = 10
        x = PANEL_ANCHO + 10
        
        # Mensaje de confirmación de borrado
        if self.confirmar_borrado and time.time() - self.tiempo_confirmacion_borrado < 3.0:
            tiempo_restante = 3.0 - (time.time() - self.tiempo_confirmacion_borrado)
            texto = self.font.render(f"[!] CONFIRMAR BORRADO: Presiona DELETE ({tiempo_restante:.1f}s)", True, (255, 100, 100))
            self.screen.blit(texto, (x, y))
            y += 35
        
        # Mensaje de guardado (3 segundos)
        if self.mensaje_guardado and time.time() - self.tiempo_mensaje_guardado < 3.0:
            texto = self.font.render(self.mensaje_guardado, True, (100, 255, 100))
            self.screen.blit(texto, (x, y))
            y += 30
        
        if self.mapa_actual:
            texto = self.font_tiny.render(f"Zoom: {self.mapa_zoom:.2f}x | Grid: {self.grid_size}px | Snap: {'ON' if self.snap_to_grid else 'OFF'}", 
                                         True, COLOR_TEXTO)
            self.screen.blit(texto, (x, y))
            y += 20
            
            texto = self.font_tiny.render(f"Elementos: {len(self.elementos)} | Seleccionados: {len(self.elementos_seleccionados)}", 
                                         True, COLOR_TEXTO)
            self.screen.blit(texto, (x, y))
            y += 20
        
        # Info del elemento hover
        if self.elemento_hover:
            y += 10
            texto = self.font_tiny.render(f"Hover: {self.elemento_hover.tipo.upper()} {self.elemento_hover.id}", 
                                         True, (255, 255, 100))
            self.screen.blit(texto, (x, y))
            y += 18
            texto = self.font_tiny.render(f"Pos: ({self.elemento_hover.x}, {self.elemento_hover.y}) | Tamaño: {self.elemento_hover.ancho}x{self.elemento_hover.alto}", 
                                         True, (200, 200, 100))
            self.screen.blit(texto, (x, y))
    
    def _draw_ayuda(self):
        """Dibuja ventana de ayuda"""
        ayuda_ancho, ayuda_alto = 700, 600
        x = (ANCHO - ayuda_ancho) // 2
        y = (ALTO - ayuda_alto) // 2
        
        pygame.draw.rect(self.screen, COLOR_PANEL, (x, y, ayuda_ancho, ayuda_alto))
        pygame.draw.rect(self.screen, (255, 165, 0), (x, y, ayuda_ancho, ayuda_alto), 3)
        
        titulo = self.font.render("AYUDA - Editor Unificado", True, COLOR_TEXTO)
        self.screen.blit(titulo, (x + 20, y + 20))
        
        ayuda = [
            "",
            "NAVEGACIÓN:",
            "  Click Der + Arrastrar: Mover mapa (pan)",
            "  Rueda: Zoom in/out",
            "",
            "SELECCIÓN:",
            "  Click Izq: Seleccionar elemento",
            "  Ctrl+Click: Agregar a selección",
            "  Ctrl+A: Seleccionar todos",
            "",
            "EDICIÓN:",
            "  Arrastrar: Mover elemento(s)",
            "  Arrastrar borde: Redimensionar",
            "  DEL: Eliminar seleccionados",
            "  Ctrl+C: Copiar",
            "  Ctrl+V: Pegar en posición del mouse",
            "",
            "CAPAS:",
            "  Click en checkbox: Mostrar/Ocultar capa",
            "",
            "UTILIDADES:",
            "  G: Toggle Grid visual",
            "  Ctrl+G: Guardar cambios",
            "  S: Toggle Snap to grid",
            "  I: Toggle Info",
            "  V: Validar elementos",
            "  E: Exportar screenshot",
            "  ESC: Guardar y salir",
        ]
        
        y_texto = y + 60
        for linea in ayuda:
            texto = self.font_tiny.render(linea, True, COLOR_TEXTO)
            self.screen.blit(texto, (x + 30, y_texto))
            y_texto += 22
    
    def _validar_elementos(self):
        """Valida elementos y detecta problemas"""
        print("\n[CHECK] Validando elementos...")
        
        self.elementos_con_error = []
        errores = []
        
        # Validar superposiciones
        for i, elem1 in enumerate(self.elementos):
            for elem2 in self.elementos[i+1:]:
                if elem1.tipo == elem2.tipo:  # Solo del mismo tipo
                    rect1 = elem1.get_rect()
                    rect2 = elem2.get_rect()
                    if rect1.colliderect(rect2):
                        errores.append(f"[!] Superposición: {elem1.id} y {elem2.id}")
                        if elem1 not in self.elementos_con_error:
                            self.elementos_con_error.append(elem1)
                        if elem2 not in self.elementos_con_error:
                            self.elementos_con_error.append(elem2)
        
        # Validar límites del mapa
        if self.mapa_img:
            ancho_mapa = self.mapa_img.get_width()
            alto_mapa = self.mapa_img.get_height()
            
            for elem in self.elementos:
                if elem.x < 0 or elem.y < 0:
                    errores.append(f"[!] {elem.id} está fuera del mapa (coordenadas negativas)")
                    if elem not in self.elementos_con_error:
                        self.elementos_con_error.append(elem)
                
                if elem.x + elem.ancho > ancho_mapa or elem.y + elem.alto > alto_mapa:
                    errores.append(f"[!] {elem.id} se sale del mapa")
                    if elem not in self.elementos_con_error:
                        self.elementos_con_error.append(elem)
        
        if errores:
            print(f"[X] Encontrados {len(errores)} problemas:")
            for error in errores[:10]:  # Mostrar máximo 10
                print(f"  {error}")
        else:
            print("[OK] No se encontraron problemas")
    
    def _exportar_screenshot(self):
        """Exporta screenshot del mapa"""
        if not self.mapa_actual:
            print("[!] No hay mapa cargado")
            return
        
        # Crear carpeta de exports
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = export_dir / f"{self.mapa_actual.nombre}_{timestamp}.png"
        
        # Capturar viewport
        viewport_rect = pygame.Rect(PANEL_ANCHO, 0, ANCHO - PANEL_ANCHO, ALTO)
        sub = self.screen.subsurface(viewport_rect)
        
        pygame.image.save(sub, str(filename))
        print(f"[OK] Screenshot guardado: {filename}")

# === MAIN ===
if __name__ == "__main__":
    editor = EditorUnificado()
    
    # Auto-cargar primer mapa si existe
    if editor.mapas_disponibles:
        print(f"\nMapas disponibles: {len(editor.mapas_disponibles)}")
        
        # Buscar el mapa con más datos (muros, portales, etc)
        mejor_mapa = None
        max_elementos = 0
        
        for mapa in editor.mapas_disponibles:
            try:
                with open(mapa.ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    count = len(data.get('muros', [])) + len(data.get('portales', [])) + len(data.get('zonas_batalla', []))
                    if count > max_elementos:
                        max_elementos = count
                        mejor_mapa = mapa
            except:
                pass
        
        if mejor_mapa:
            print(f"Cargando mapa con más elementos: {mejor_mapa.nombre} ({max_elementos} elementos)")
            editor.cargar_mapa(mejor_mapa)
        else:
            print("Cargando primer mapa...")
            editor.cargar_mapa(editor.mapas_disponibles[0])
    
    editor.run()
