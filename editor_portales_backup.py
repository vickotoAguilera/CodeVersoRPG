import pygame
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

ANCHO, ALTO = 1600, 900
PANEL_ANCHO = 300
FPS = 60

COLOR_FONDO = (15, 15, 20)
COLOR_PANEL = (25, 25, 35)
COLOR_TEXTO = (240, 240, 240)
COLOR_TEXTO_SEC = (180, 180, 180)
COLOR_BOTON = (50, 50, 70)
COLOR_BOTON_HOVER = (70, 70, 100)
COLOR_PORTAL_ENLAZADO = (255, 105, 180)  # rosado
COLOR_SPAWN = (80, 180, 255)             # azul
COLOR_SELECCION = (255, 215, 0)
COLOR_BORDE_DEST = (255, 140, 0)

@dataclass
class MapaInfo:
    nombre: str
    archivo: str
    ruta: str
    categoria: str
    subcarpeta: str = ""

@dataclass
class PortalRect:
    id: str
    x: int
    y: int
    w: int
    h: int
    mapa_destino: str = ""
    spawn_destino_id: str = ""

    def to_dict(self):
        return {
            "id": self.id, "tipo": "portal_enlazado", "forma": "rect",
            "x": self.x, "y": self.y, "w": self.w, "h": self.h,
            "mapa_destino": self.mapa_destino,
            "spawn_destino_id": self.spawn_destino_id
        }

@dataclass
class PortalPoly:
    id: str
    puntos: List[Tuple[int,int]]
    mapa_destino: str = ""
    spawn_destino_id: str = ""

    def to_dict(self):
        return {
            "id": self.id, "tipo": "portal_enlazado", "forma": "poly",
            "puntos": [[int(x), int(y)] for x,y in self.puntos],
            "mapa_destino": self.mapa_destino,
            "spawn_destino_id": self.spawn_destino_id
        }

@dataclass
class Spawn:
    id: str
    x: int
    y: int
    direccion: str = "abajo"
    tam: int = 12

    def to_dict(self):
        return {"id": self.id, "tipo": "spawn", "x": self.x, "y": self.y, "direccion": self.direccion, "tam": self.tam}

class SeccionDesplegable:
    def __init__(self, x, y, ancho, titulo):
        self.x, self.y, self.ancho = x, y, ancho
        self.titulo = titulo
        self.expandida = False
        self.items: List[MapaInfo] = []
        self.fuente = pygame.font.Font(None, 22)
        self.fuente_item = pygame.font.Font(None, 18)

    def get_alto_total(self):
        alto = 36
        if self.expandida:
            alto += 6 + 26 * len(self.items)
        return alto

    def click_en_titulo(self, pos):
        rect = pygame.Rect(self.x, self.y, self.ancho, 36)
        return rect.collidepoint(pos)

    def toggle(self):
        self.expandida = not self.expandida

    def get_item_en_posicion(self, pos) -> Optional[MapaInfo]:
        if not self.expandida: return None
        base_y = self.y + 36 + 6
        if pos[0] < self.x or pos[0] > self.x + self.ancho: return None
        if pos[1] < base_y: return None
        idx = (pos[1] - base_y) // 26
        if 0 <= idx < len(self.items):
            return self.items[idx]
        return None

    def dibujar(self, surface):
        pygame.draw.rect(surface, COLOR_PANEL, (self.x, self.y, self.ancho, self.get_alto_total()), border_radius=6)
        flecha = "▼" if self.expandida else "▶"
        titulo = self.fuente.render(f"{flecha} {self.titulo} ({len(self.items)})", True, COLOR_TEXTO)
        surface.blit(titulo, (self.x + 10, self.y + 8))
        if self.expandida:
            y = self.y + 36
            for it in self.items:
                pygame.draw.rect(surface, (35,35,50), (self.x+8, y, self.ancho-16, 22), border_radius=4)
                surface.blit(self.fuente_item.render(it.nombre, True, COLOR_TEXTO_SEC), (self.x+14, y+3))
                y += 26

class SeccionPortales:
    def __init__(self, x, y, ancho):
        self.x, self.y, self.ancho = x, y, ancho
        self.expandida = True
        self.fuente = pygame.font.Font(None, 22)
        self.fuente_item = pygame.font.Font(None, 18)
        self._cached_items: List[object] = []

    def set_items(self, portales: List[object]):
        self._cached_items = portales

    def get_alto_total(self):
        alto = 36
        if self.expandida:
            alto += 6 + 26 * len(self._cached_items)
        return alto

    def click_en_titulo(self, pos):
        rect = pygame.Rect(self.x, self.y, self.ancho, 36)
        return rect.collidepoint(pos)

    def toggle(self):
        self.expandida = not self.expandida

    def get_item_en_posicion(self, pos) -> Optional[object]:
        if not self.expandida: return None
        base_y = self.y + 36 + 6
        if pos[0] < self.x or pos[0] > self.x + self.ancho: return None
        if pos[1] < base_y: return None
        idx = (pos[1] - base_y) // 26
        if 0 <= idx < len(self._cached_items):
            return self._cached_items[idx]
        return None

    def _label_portal(self, p: object) -> str:
        pid = getattr(p, 'id', '') or '(sin id)'
        dest = getattr(p, 'mapa_destino', '') or '(sin destino)'
        return f"{pid} -> {dest}"

    def dibujar(self, surface):
        titulo = self.fuente.render(f"Portales ({len(self._cached_items)})", True, COLOR_TEXTO)
        pygame.draw.rect(surface, COLOR_PANEL, (self.x, self.y, self.ancho, self.get_alto_total()), border_radius=6)
        surface.blit(titulo, (self.x + 10, self.y + 8))
        if self.expandida:
            y = self.y + 36
            for it in self._cached_items:
                pygame.draw.rect(surface, (35,35,50), (self.x+8, y, self.ancho-16, 22), border_radius=4)
                surface.blit(self.fuente_item.render(self._label_portal(it), True, COLOR_TEXTO_SEC), (self.x+14, y+3))
                y += 26

class EditorPortales:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Portales - CodeVerso RPG")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 32)

        self.secciones: List[SeccionDesplegable] = []
        
        # Dos viewports independientes
        self.mapa_izq: Optional[MapaInfo] = None
        self.mapa_der: Optional[MapaInfo] = None
        
        # Estados izquierda
        self.izq_img_orig = None
        self.izq_img = None
        self.izq_rect = None
        self.izq_zoom = 1.0
        self.izq_offset_x = 0
        self.izq_offset_y = 0
        self.izq_portales: List[object] = []
        self.izq_spawns: List[Spawn] = []
        
        # Estados derecha
        self.der_img_orig = None
        self.der_img = None
        self.der_rect = None
        self.der_zoom = 1.0
        self.der_offset_x = 0
        self.der_offset_y = 0
        self.der_portales: List[object] = []
        self.der_spawns: List[Spawn] = []

        self.modo = 'portal'  # 'portal' | 'spawn' | 'vincular'
        self.submodo = 'rect' # 'rect' | 'poly'
        self.poligono_puntos: List[Tuple[int,int]] = []
        self.dibujando_poligono = False
        self.lado_poly = None  # 'izq' | 'der'

        self.seleccionados: List[object] = []
        self.lado_seleccion = None  # 'izq' | 'der'
        self.arrastrando = False
        self.grupo_offsets: List[Tuple[int,int]] = []
        self.arrastrando_camara = False
        self.lado_pan = None
        self.mouse_anterior = (0,0)
        self.resizing = False
        self.resize_handle = None
        self.click_der_iniciado = False
        self.pos_click_der_inicio = (0,0)
        
        # Vinculación de portales
        self.vinculando = False
        self.portal_vinculo_1 = None
        self.lado_vinculo_1 = None
        
        # Edición de nombre
        self.editando_nombre = False
        self.portal_editando = None
        self.lado_editando = None
        self.texto_nombre = ""

        self.mensaje = ""
        self.mensaje_ts = 0
        self.mostrar_ayuda = False
        self.cambios_pendientes = False
        self.ultimo_autosave = 0
        self.INTERVALO_AUTOSAVE = 2000

        self.cargar_mapas()
        self.seccion_portales = SeccionPortales(10, 0, PANEL_ANCHO-20)

    # --------- Maps ----------
    def cargar_mapas(self):
        base = Path('assets/maps')
        if not base.exists(): return
        y = 50
        for cat in sorted([d for d in base.iterdir() if d.is_dir()]):
            sec = SeccionDesplegable(10, y, PANEL_ANCHO-20, cat.name.replace('_',' ').title())
            sec.items = self._buscar_mapas(cat, cat.name)
            if sec.items:
                self.secciones.append(sec)
                y += sec.get_alto_total() + 10

    def _buscar_mapas(self, carpeta: Path, categoria: str, subcarpeta: str = "") -> List[MapaInfo]:
        lst = []
        for arch in list(carpeta.glob('*.png')) + list(carpeta.glob('*.jpg')):
            lst.append(MapaInfo(arch.stem, arch.name, str(arch), categoria, subcarpeta))
        for sub in carpeta.iterdir():
            if sub.is_dir():
                lst += self._buscar_mapas(sub, categoria, subcarpeta + ("/" if subcarpeta else "") + sub.name)
        return sorted(lst, key=lambda m: m.nombre)

    # --------- IO ----------
    def _ruta_json(self, mapa: MapaInfo) -> Path:
        carpeta = Path('src/database/mapas')/mapa.categoria
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta/(mapa.nombre + '.json')

    def guardar(self):
        if self.mapa_izq:
            self._guardar_mapa(self.mapa_izq, self.izq_portales, self.izq_spawns)
        if self.mapa_der:
            self._guardar_mapa(self.mapa_der, self.der_portales, self.der_spawns)
        self._msg("✓ Guardado")
        self.cambios_pendientes = False

    def _guardar_mapa(self, mapa: MapaInfo, portales: List[object], spawns: List[Spawn]):
        ruta = self._ruta_json(mapa)
        data = {
            "portales": [p.to_dict() for p in portales],
            "spawns": [s.to_dict() for s in spawns]
        }
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _cargar_mapa_data(self, mapa: MapaInfo) -> Tuple[List[object], List[Spawn]]:
        ruta = self._ruta_json(mapa)
        portales, spawns = [], []
        if ruta.exists():
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for p in data.get('portales', []):
                if p.get('forma') == 'poly':
                    portales.append(PortalPoly(p.get('id',''), [tuple(pt) for pt in p['puntos']], p.get('mapa_destino',''), p.get('spawn_destino_id','')))
                else:
                    portales.append(PortalRect(p.get('id',''), p['x'], p['y'], p['w'], p['h'], p.get('mapa_destino',''), p.get('spawn_destino_id','')))
            for s in data.get('spawns', []):
                spawns.append(Spawn(s.get('id',''), s['x'], s['y'], s.get('direccion','abajo'), s.get('tam', 12)))
        return portales, spawns

    # --------- Utils ----------
    def _msg(self, txt):
        self.mensaje, self.mensaje_ts = txt, pygame.time.get_ticks()

    def _map_to_screen(self, x, y):
        return int(x*self.zoom + self.offset_x + PANEL_ANCHO), int(y*self.zoom + self.offset_y)

    def _screen_to_map(self, sx, sy):
        return int((sx - PANEL_ANCHO - self.offset_x)/self.zoom), int((sy - self.offset_y)/self.zoom)

    def _punto_en_poly(self, puntos: List[Tuple[int,int]], px, py) -> bool:
        if len(puntos) < 3: return False
        inside = False
        j = len(puntos) - 1
        for i in range(len(puntos)):
            xi, yi = puntos[i]; xj, yj = puntos[j]
            intersecta = ((yi>py) != (yj>py)) and (px < (xj - xi)*(py - yi)/(yj - yi + 1e-9) + xi)
            if intersecta: inside = not inside
            j = i
        return inside

    # --------- Draw ----------
    def dibujar_panel(self):
        surf = self.screen
        pygame.draw.rect(surf, COLOR_PANEL, (0,0,PANEL_ANCHO,ALTO))
        titulo = self.font_title.render("EDITOR PORTALES", True, COLOR_TEXTO)
        surf.blit(titulo, (10,10))
        # Layout dinámico: recalcular Y para evitar traslapes
        y = 50
        for s in self.secciones:
            s.y = y
            s.dibujar(surf)
            y += s.get_alto_total() + 10
        # Sección lista de portales del mapa actual
        if self.mapa_actual is not None:
            self.seccion_portales.y = y
            self.seccion_portales.set_items(self.portales)
            self.seccion_portales.dibujar(surf)
            y += self.seccion_portales.get_alto_total() + 10
        # Botón de ayuda
        btn = pygame.Rect(PANEL_ANCHO-42, 12, 30, 26)
        mp = pygame.mouse.get_pos()
        pygame.draw.rect(surf, COLOR_BOTON_HOVER if btn.collidepoint(mp) else COLOR_BOTON, btn, border_radius=6)
        pygame.draw.rect(surf, COLOR_TEXTO, btn, 1, border_radius=6)
        q = self.font.render("?", True, COLOR_TEXTO)
        surf.blit(q, q.get_rect(center=btn.center))

    def dibujar_mapa(self):
        if not self.mapa_imagen: return
        # Determinar viewports
        if self.dual_view and len(self.seleccionados)==1 and getattr(self.seleccionados[0], 'mapa_destino', ''):
            left_w = (ANCHO - PANEL_ANCHO)//2
            left_rect = pygame.Rect(PANEL_ANCHO, 0, left_w, ALTO)
            right_rect = pygame.Rect(PANEL_ANCHO+left_w, 0, ANCHO-PANEL_ANCHO-left_w, ALTO)
            # Izquierda: mapa origen
            self.screen.set_clip(left_rect)
            self.screen.blit(self.mapa_imagen, (PANEL_ANCHO+self.offset_x, self.offset_y))
        else:
            left_rect = pygame.Rect(PANEL_ANCHO, 0, ANCHO-PANEL_ANCHO, ALTO)
            self.screen.set_clip(left_rect)
            self.screen.blit(self.mapa_imagen, (PANEL_ANCHO+self.offset_x, self.offset_y))
        # Portales
        for p in self.portales:
            if isinstance(p, PortalPoly):
                pts = [self._map_to_screen(x,y) for x,y in p.puntos]
                if len(pts)>=3:
                    pygame.draw.polygon(self.screen, COLOR_PORTAL_ENLAZADO, pts, 0)
                    pygame.draw.polygon(self.screen, COLOR_BORDE_DEST, pts, 2)
                if len(pts)>=3 and getattr(p, 'mapa_destino', ""):
                    cx = sum(pt[0] for pt in pts)//len(pts)
                    cy = sum(pt[1] for pt in pts)//len(pts)
                    self.screen.blit(self.font_small.render(p.mapa_destino, True, COLOR_TEXTO), (cx+6, cy-10))
            else:
                sx, sy = self._map_to_screen(p.x, p.y)
                pygame.draw.rect(self.screen, COLOR_PORTAL_ENLAZADO, (sx, sy, int(p.w*self.zoom), int(p.h*self.zoom)))
                pygame.draw.rect(self.screen, COLOR_BORDE_DEST, (sx, sy, int(p.w*self.zoom), int(p.h*self.zoom)), 2)
                if getattr(p, 'mapa_destino', ""):
                    self.screen.blit(self.font_small.render(p.mapa_destino, True, COLOR_TEXTO), (sx+4, sy-16))
        # Spawns
        for s in self.spawns:
            sx, sy = self._map_to_screen(s.x, s.y)
            half = max(6, int(s.tam * self.zoom / 2))
            # cuadrado centrado
            pygame.draw.rect(self.screen, COLOR_SPAWN, (sx-half, sy-half, half*2, half*2), 1)
            vec = {"arriba":(0,-18),"abajo":(0,18),"izquierda":(-18,0),"derecha":(18,0)}.get(s.direccion, (0,18))
            pygame.draw.line(self.screen, COLOR_SPAWN, (sx, sy), (sx+vec[0], sy+vec[1]), 2)
            self.screen.blit(self.font_small.render(s.id or "spawn", True, COLOR_TEXTO), (sx+8, sy-18))

        # Polígono en construcción
        if self.dibujando_poligono and self.poligono_puntos:
            pts = [self._map_to_screen(x,y) for x,y in self.poligono_puntos]
            if len(pts)>=2:
                pygame.draw.lines(self.screen, (0,255,255), False, pts, 2)
            if len(pts)>=3:
                pygame.draw.line(self.screen, (0,255,100), pts[-1], pts[0], 2)
            for i,pt in enumerate(pts):
                pygame.draw.circle(self.screen, (0,255,255), pt, 5)
                self.screen.blit(self.font_small.render(str(i+1), True, COLOR_TEXTO), (pt[0]+8, pt[1]-8))

        # Vista previa de mapa destino (si hay un portal seleccionado)
        if len(self.seleccionados) == 1:
            sel = self.seleccionados[0]
            dest = None
            if isinstance(sel, PortalPoly): dest = sel.mapa_destino
            if isinstance(sel, PortalRect): dest = sel.mapa_destino
            if dest and not self.dual_view:
                ruta = Path('assets/maps')/dest
                if ruta.exists():
                    key = str(ruta)
                    if key not in self.cache_previews:
                        try:
                            img = pygame.image.load(key).convert_alpha()
                            self.cache_previews[key] = pygame.transform.smoothscale(img, (240, 140))
                        except Exception:
                            self.cache_previews[key] = None
                    prev = self.cache_previews.get(key)
                    if prev:
                        box = pygame.Rect(ANCHO-260, 120, 250, 160)
                        pygame.draw.rect(self.screen, (40,40,60), box, border_radius=8)
                        self.screen.blit(prev, (box.x+5, box.y+5))
                        self.screen.blit(self.font_small.render(f"Destino: {dest}", True, COLOR_TEXTO), (box.x+8, box.bottom-22))
        # Si dual view activo, dibujar mapa destino a la derecha
        if self.dual_view and len(self.seleccionados)==1 and self.dv_dest_img is not None:
            left_w = (ANCHO - PANEL_ANCHO)//2
            right_rect = pygame.Rect(PANEL_ANCHO+left_w, 0, ANCHO-PANEL_ANCHO-left_w, ALTO)
            self.screen.set_clip(right_rect)
            self.screen.blit(self.dv_dest_img, (right_rect.x+self.dv_offset_x, right_rect.y+self.dv_offset_y))
            # dibujar spawns destino
            for sp in self.dv_spawns:
                sx = int(sp.x*self.dv_zoom) + right_rect.x + self.dv_offset_x
                sy = int(sp.y*self.dv_zoom) + right_rect.y + self.dv_offset_y
                half = max(4, int(sp.tam * self.dv_zoom / 2))
                color = (120,255,120) if (len(self.seleccionados)==1 and getattr(self.seleccionados[0], 'spawn_destino_id','')==sp.id) else COLOR_SPAWN
                pygame.draw.rect(self.screen, color, (sx-half, sy-half, half*2, half*2), 2)
            # separador visual
            self.screen.set_clip(None)
            pygame.draw.line(self.screen, (60,60,80), (PANEL_ANCHO+left_w,0), (PANEL_ANCHO+left_w,ALTO), 2)
        # Reset clip
        self.screen.set_clip(None)
        # Handles de redimensionado si selección única
        if len(self.seleccionados) == 1:
            o = self.seleccionados[0]
            if isinstance(o, PortalRect):
                self._dibujar_handles_portal_rect(o)
            elif isinstance(o, Spawn):
                self._dibujar_handles_spawn(o)

    def dibujar_overlay(self):
        info = [f"Modo: {self.modo}/{self.submodo}", f"Zoom: {self.zoom:.2f}x (Max 1:1)"]
        if self.dibujando_poligono:
            info.append(f"Puntos: {len(self.poligono_puntos)} | ENTER crea | Der. deshacer | ESC cancela")
        if self.dual_view:
            info.append("Dual View: ON (V para alternar)")
        x = ANCHO - 260; y = 10
        for linea in info:
            t = self.font_small.render(linea, True, (230,230,230))
            pygame.draw.rect(self.screen, (40,40,50), (x-8,y-4, 240, t.get_height()+8), border_radius=6)
            self.screen.blit(t, (x, y))
            y += t.get_height()+6
        if self.mensaje and pygame.time.get_ticks()-self.mensaje_ts<3000:
            t = self.font_small.render(self.mensaje, True, COLOR_TEXTO)
            rect = t.get_rect(center=(ANCHO//2, 40))
            pygame.draw.rect(self.screen, (40,40,50), rect.inflate(16,8), border_radius=6)
            self.screen.blit(t, rect)

    # --------- Map load/zoom ---------
    def cargar_mapa(self, info: MapaInfo):
        try:
            img = pygame.image.load(info.ruta).convert_alpha()
            rect = img.get_rect()
            escala_x = (ANCHO-PANEL_ANCHO)/rect.width
            escala_y = ALTO/rect.height
            self.escala = min(escala_x, escala_y, 1.0)
            self.zoom = self.escala
            self.mapa_imagen_original = img
            self.mapa_rect = rect
            self._aplicar_zoom()
            self.mapa_actual = info
            self.offset_x = 0; self.offset_y = 0
            self.cargar()
            self._msg(f"Mapa cargado: {info.nombre}")
        except Exception as e:
            self._msg(f"Error cargando mapa: {e}")

    def _aplicar_zoom(self):
        if not self.mapa_imagen_original: return
        w = max(1, int(self.mapa_rect.width*self.zoom))
        h = max(1, int(self.mapa_rect.height*self.zoom))
        self.mapa_imagen = pygame.transform.smoothscale(self.mapa_imagen_original, (w,h))

    # ---- Dual View helpers ----
    def _actualizar_dual_view_context(self):
        self.dv_dest_img = None; self.dv_dest_img_orig = None; self.dv_spawns = []
        if not (self.dual_view and len(self.seleccionados)==1):
            return
        sel = self.seleccionados[0]
        dest = getattr(sel, 'mapa_destino','')
        if not dest:
            return
        ruta = Path('assets/maps')/dest
        if not ruta.exists():
            return
        try:
            img = pygame.image.load(str(ruta)).convert_alpha()
            self.dv_dest_img_orig = img
            self.dv_dest_rect = img.get_rect()
            # ajustar zoom para caber en viewport derecho
            left_w = (ANCHO - PANEL_ANCHO)//2
            right_w = ANCHO - PANEL_ANCHO - left_w
            escala_x = right_w / self.dv_dest_rect.width
            escala_y = ALTO / self.dv_dest_rect.height
            self.dv_zoom = min(escala_x, escala_y, 1.0)
            w = max(1, int(self.dv_dest_rect.width*self.dv_zoom))
            h = max(1, int(self.dv_dest_rect.height*self.dv_zoom))
            self.dv_dest_img = pygame.transform.smoothscale(self.dv_dest_img_orig, (w,h))
            # centrar
            self.dv_offset_x = (right_w - w)//2
            self.dv_offset_y = (ALTO - h)//2
            # cargar spawns destino
            self.dv_spawns = self._cargar_spawns_destino(dest)
        except Exception:
            self.dv_dest_img = None

    def _cargar_spawns_destino(self, dest_rel: str) -> List[Spawn]:
        try:
            rel = Path(dest_rel)
            stem = rel.stem
            # categoria es la primera carpeta del path relativo
            parts = rel.parts
            categoria = parts[0] if len(parts)>1 else (self.mapa_actual.categoria if self.mapa_actual else "")
            ruta_json = Path('src/database/mapas')/categoria/(stem + '.json')
            if ruta_json.exists():
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sps = []
                for s in data.get('spawns', []):
                    sps.append(Spawn(s.get('id',''), s['x'], s['y'], s.get('direccion','abajo'), s.get('tam',12)))
                return sps
        except Exception:
            pass
        return []

    def _guardar_spawn_destino(self, dest_rel: str, spawn_id: str, x: int, y: int):
        try:
            rel = Path(dest_rel)
            stem = rel.stem
            parts = rel.parts
            categoria = parts[0] if len(parts)>1 else (self.mapa_actual.categoria if self.mapa_actual else "")
            ruta_json = Path('src/database/mapas')/categoria/(stem + '.json')
            data = {"portales": [], "spawns": []}
            if ruta_json.exists():
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            # buscar spawn
            encontrado = False
            for s in data.get('spawns', []):
                if s.get('id','') == spawn_id:
                    s['x'] = int(x); s['y'] = int(y)
                    if 'tam' not in s: s['tam'] = 12
                    encontrado = True
                    break
            if not encontrado:
                data.setdefault('spawns', []).append({"id": spawn_id, "tipo": "spawn", "x": int(x), "y": int(y), "direccion": "abajo", "tam": 12})
            # guardar
            ruta_json.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # refrescar cache local
            self.dv_spawns = self._cargar_spawns_destino(dest_rel)
        except Exception as e:
            self._msg(f"Error guardando spawn destino: {e}")

    def _obj_en_pos(self, x, y) -> Optional[object]:
        # Portales (reversa para top-most)
        for p in reversed(self.portales):
            if isinstance(p, PortalPoly):
                if self._punto_en_poly(p.puntos, x, y):
                    return p
            else:
                if p.x <= x <= p.x+p.w and p.y <= y <= p.y+p.h:
                    return p
        # Spawns
        for s in reversed(self.spawns):
            half = max(8, int(s.tam/2))
            if abs(s.x - x) <= half and abs(s.y - y) <= half:
                return s
        return None

    def _dibujar_ayuda(self):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        rect = pygame.Rect(ANCHO//2-360, ALTO//2-220, 720, 440)
        pygame.draw.rect(self.screen, (30,30,45), rect, border_radius=10)
        pygame.draw.rect(self.screen, (90,140,255), rect, 2, border_radius=10)
        y = rect.y+16
        self.screen.blit(self.font_title.render("Ayuda - Editor de Portales", True, COLOR_TEXTO), (rect.x+16,y)); y+=32
        lineas = [
            "P: Modo Portal | S: Modo Spawn | L: Polígono",
            "Izq: crear/seleccionar | Shift+Click: multi | DEL: eliminar",
            "Arrastrar: mover objeto | Rueda: Zoom (0.25-1.0) | 0: Reset",
            "Rect: arrastre para crear | Poly: Clicks, Enter crea, Der deshace",
            "Handles: arrastrar para redimensionar | Click der: borrar portal / crear spawn",
            "G: Guardar | H: Mostrar/ocultar esta ayuda",
        ]
        for li in lineas:
            self.screen.blit(self.font_small.render(li, True, COLOR_TEXTO), (rect.x+18, y)); y+=22

    # ----- Handles y redimensionado -----
    def _dibujar_handles_portal_rect(self, pr: PortalRect):
        # esquinas del rect
        pts = [(pr.x, pr.y), (pr.x+pr.w, pr.y), (pr.x, pr.y+pr.h), (pr.x+pr.w, pr.y+pr.h)]
        tam = max(6, int(8 * self.zoom))
        for (hx,hy) in pts:
            sx, sy = self._map_to_screen(hx, hy)
            pygame.draw.rect(self.screen, COLOR_SELECCION, (sx-tam//2, sy-tam//2, tam, tam))

    def _detectar_handle_portal_rect(self, pr: PortalRect, x, y):
        margen = 8
        corners = {
            'nw': (pr.x, pr.y),
            'ne': (pr.x+pr.w, pr.y),
            'sw': (pr.x, pr.y+pr.h),
            'se': (pr.x+pr.w, pr.y+pr.h)
        }
        for nombre,(hx,hy) in corners.items():
            if abs(x-hx)<=margen and abs(y-hy)<=margen:
                return nombre
        return None

    def _aplicar_redimension_portal_rect(self, pr: PortalRect, x, y, handle):
        min_size = 5
        if handle == 'se':
            pr.w = max(min_size, x - pr.x)
            pr.h = max(min_size, y - pr.y)
        elif handle == 'ne':
            pr.w = max(min_size, x - pr.x)
            nh = max(min_size, (pr.y + pr.h) - y)
            if nh >= min_size:
                pr.y = y
                pr.h = nh
        elif handle == 'sw':
            nw = max(min_size, (pr.x + pr.w) - x)
            if nw >= min_size:
                pr.x = x
                pr.w = nw
            pr.h = max(min_size, y - pr.y)
        elif handle == 'nw':
            nw = max(min_size, (pr.x + pr.w) - x)
            nh = max(min_size, (pr.y + pr.h) - y)
            if nw >= min_size:
                pr.x = x
                pr.w = nw
            if nh >= min_size:
                pr.y = y
                pr.h = nh

    def _dibujar_handles_spawn(self, sp: Spawn):
        half = max(6, int(sp.tam * self.zoom / 2))
        corners = [(-half,-half),(half,-half),(-half,half),(half,half)]
        tam = max(6, int(8*self.zoom))
        cx, cy = self._map_to_screen(sp.x, sp.y)
        for dx,dy in corners:
            sx, sy = cx+dx, cy+dy
            pygame.draw.rect(self.screen, COLOR_SELECCION, (sx-tam//2, sy-tam//2, tam, tam))

    def _detectar_handle_spawn(self, sp: Spawn, x, y):
        half = max(6, int(sp.tam/2))
        corners = {
            'nw': (sp.x-half, sp.y-half),
            'ne': (sp.x+half, sp.y-half),
            'sw': (sp.x-half, sp.y+half),
            'se': (sp.x+half, sp.y+half)
        }
        margen = 8
        for nombre,(hx,hy) in corners.items():
            if abs(x-hx)<=margen and abs(y-hy)<=margen:
                return nombre
        return None

    def _aplicar_redimension_spawn(self, sp: Spawn, x, y, handle):
        half = sp.tam/2
        if handle in ('se','ne'):
            # usar distancia desde centro a esquina
            nx = abs(x - sp.x); ny = abs(y - sp.y)
            sp.tam = max(6, int(2*max(nx, ny)))
        else:
            nx = abs(x - sp.x); ny = abs(y - sp.y)
            sp.tam = max(6, int(2*max(nx, ny)))

    # --------- Main loop ---------
    def run(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if self.mostrar_ayuda:
                            self.mostrar_ayuda = False
                        elif self.dibujando_poligono:
                            self.poligono_puntos=[]; self.dibujando_poligono=False
                        else:
                            running = False
                    elif ev.key == pygame.K_0 and self.mapa_imagen_original:
                        self.zoom = 1.0
                        self._aplicar_zoom()
                    elif ev.key == pygame.K_p:
                        self.modo = 'portal'; self._msg("Modo Portal (P)")
                    elif ev.key == pygame.K_s:
                        self.modo = 'spawn'; self._msg("Modo Spawn (S)")
                    elif ev.key == pygame.K_l:
                        if self.modo == 'portal':
                            self.submodo = 'poly'; self.poligono_puntos=[]; self.dibujando_poligono=False
                            self._msg("Polígono activo: Click agrega, Enter crea, Der. deshace")
                    elif ev.key == pygame.K_g:
                        self.guardar()
                    elif ev.key == pygame.K_h:
                        self.mostrar_ayuda = not self.mostrar_ayuda
                    elif ev.key == pygame.K_v:
                        self.dual_view = not self.dual_view
                        self._actualizar_dual_view_context()
                    elif ev.key == pygame.K_RETURN:
                        if self.submodo=='poly' and self.dibujando_poligono and len(self.poligono_puntos)>=3:
                            # Crear portal poligonal con ID vacío (editable luego)
                            self.portales.append(PortalPoly(id="", puntos=self.poligono_puntos[:]))
                            self.poligono_puntos=[]; self.dibujando_poligono=False
                            self._msg("✓ Portal poligonal creado")
                            self.cambios_pendientes = True
                    elif ev.key == pygame.K_DELETE:
                        if self.seleccionados:
                            for o in self.seleccionados:
                                if isinstance(o, Spawn) and o in self.spawns:
                                    self.spawns.remove(o)
                                elif o in self.portales:
                                    self.portales.remove(o)
                            self.seleccionados.clear()
                            self.cambios_pendientes = True
                elif ev.type == pygame.MOUSEWHEEL and self.mapa_imagen_original:
                    factor = 1.1 if ev.y>0 else 0.9
                    self.zoom = max(0.25, min(1.0, self.zoom*factor))
                    self._aplicar_zoom()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = ev.pos
                    if ev.button == 1:
                        # Panel clicks
                        if mx < PANEL_ANCHO:
                            # Botón ayuda
                            if pygame.Rect(PANEL_ANCHO-42,12,30,26).collidepoint((mx,my)):
                                self.mostrar_ayuda = not self.mostrar_ayuda
                            else:
                                for s in self.secciones:
                                    if s.click_en_titulo((mx,my)):
                                        s.toggle(); break
                                    item = s.get_item_en_posicion((mx,my))
                                    if item: self.cargar_mapa(item); break
                                else:
                                    # Sección portales
                                    if self.mapa_actual and self.seccion_portales.click_en_titulo((mx,my)):
                                        self.seccion_portales.toggle()
                                    else:
                                        pobj = self.seccion_portales.get_item_en_posicion((mx,my)) if self.mapa_actual else None
                                        if pobj is not None:
                                            self.seleccionados = [pobj]
                                            self._actualizar_dual_view_context()
                        elif self.mapa_actual:
                            x,y = self._screen_to_map(mx,my)
                            mods = pygame.key.get_mods()
                            # Si dual view y clic en viewport derecho para colocar spawn destino
                            if self.dual_view and len(self.seleccionados)==1:
                                left_w = (ANCHO - PANEL_ANCHO)//2
                                right_rect = pygame.Rect(PANEL_ANCHO+left_w, 0, ANCHO-PANEL_ANCHO-left_w, ALTO)
                                if right_rect.collidepoint((mx,my)) and self.dv_dest_img is not None:
                                    sel = self.seleccionados[0]
                                    dest = getattr(sel, 'mapa_destino','')
                                    if dest:
                                        # map coords en destino
                                        dx = int((mx - right_rect.x - self.dv_offset_x)/self.dv_zoom)
                                        dy = int((my - self.dv_offset_y)/self.dv_zoom)
                                        if not getattr(sel, 'spawn_destino_id',''):
                                            # crear id por defecto
                                            sel.spawn_destino_id = f"spawn_{Path(dest).stem}"
                                            self.cambios_pendientes = True
                                        self._guardar_spawn_destino(dest, sel.spawn_destino_id, dx, dy)
                                        self._msg("✓ Spawn destino actualizado")
                                        break
                            obj = self._obj_en_pos(x,y)
                            if obj:
                                if mods & pygame.KMOD_SHIFT:
                                    if obj in self.seleccionados:
                                        self.seleccionados.remove(obj)
                                    else:
                                        self.seleccionados.append(obj)
                                else:
                                    self.seleccionados = [obj]
                                self._actualizar_dual_view_context()
                                # Detectar handles para redimensionar si selección única
                                if len(self.seleccionados)==1:
                                    sel = self.seleccionados[0]
                                    h = None
                                    if isinstance(sel, PortalRect):
                                        h = self._detectar_handle_portal_rect(sel, x, y)
                                    elif isinstance(sel, Spawn):
                                        h = self._detectar_handle_spawn(sel, x, y)
                                    if h:
                                        self.resizing = True
                                        self.resize_handle = h
                                    else:
                                        # Iniciar arrastre
                                        self.arrastrando = True
                                else:
                                    # Iniciar arrastre grupal
                                    self.arrastrando = True
                                # Preparar offsets
                                self.grupo_offsets = []
                                for o in self.seleccionados:
                                    if isinstance(o, PortalPoly) and o.puntos:
                                        px,py = o.puntos[0]
                                        self.grupo_offsets.append((px-x, py-y))
                                    elif isinstance(o, PortalRect):
                                        self.grupo_offsets.append((o.x-x, o.y-y))
                                    else:  # Spawn
                                        self.grupo_offsets.append((o.x-x, o.y-y))
                            else:
                                if self.modo=='spawn':
                                    self.spawns.append(Spawn(id="", x=x, y=y))
                                    self._msg("Spawn creado")
                                    self.cambios_pendientes = True
                                elif self.modo=='portal':
                                    if self.submodo=='poly':
                                        self.poligono_puntos.append((x,y)); self.dibujando_poligono=True
                                    else:
                                        self.creando_rect = True; self.rect_inicio = (x,y)
                    elif ev.button == 3:
                        if self.submodo=='poly' and self.dibujando_poligono and self.poligono_puntos:
                            self.poligono_puntos.pop();
                            if not self.poligono_puntos: self.dibujando_poligono=False
                        else:
                            self.arrastrando_camara = True
                            self.mouse_anterior = (mx,my)
                            self.click_der_iniciado = True
                            self.pos_click_der_inicio = (mx,my)
                elif ev.type == pygame.MOUSEBUTTONUP:
                    mx,my = ev.pos
                    if ev.button == 1 and getattr(self,'creando_rect', False) and self.modo=='portal' and self.submodo=='rect':
                        x1,y1 = self.rect_inicio; x2,y2 = self._screen_to_map(mx,my)
                        x=min(x1,x2); y=min(y1,y2); w=abs(x2-x1); h=abs(y2-y1)
                        if w>5 and h>5:
                            self.portales.append(PortalRect(id="", x=x, y=y, w=w, h=h))
                            self._msg("✓ Portal rectangular creado")
                            self.cambios_pendientes = True
                        self.creando_rect=False
                    if ev.button == 1 and self.arrastrando:
                        self.arrastrando = False
                    if ev.button == 1 and self.resizing:
                        self.resizing = False
                        self.resize_handle = None
                    if ev.button in (2,3):
                        # click derecho contextual
                        if ev.button==3 and self.click_der_iniciado:
                            dx = mx - self.pos_click_der_inicio[0]
                            dy = my - self.pos_click_der_inicio[1]
                            if abs(dx) < 6 and abs(dy) < 6 and mx > PANEL_ANCHO:
                                x,y = self._screen_to_map(mx,my)
                                obj = self._obj_en_pos(x,y)
                                if isinstance(obj, (PortalRect, PortalPoly)):
                                    # eliminar portal
                                    try:
                                        self.portales.remove(obj)
                                        if obj in self.seleccionados:
                                            self.seleccionados.remove(obj)
                                        self._msg("Portal eliminado")
                                        self.cambios_pendientes = True
                                    except ValueError:
                                        pass
                                elif obj is None and self.mapa_actual:
                                    # crear spawn
                                    self.spawns.append(Spawn(id="", x=x, y=y))
                                    self._msg("Spawn creado")
                                    self.cambios_pendientes = True
                        self.arrastrando_camara = False
                        self.click_der_iniciado = False
                elif ev.type == pygame.MOUSEMOTION:
                    mx,my = ev.pos
                    if self.resizing and len(self.seleccionados)==1:
                        x,y = self._screen_to_map(mx,my)
                        sel = self.seleccionados[0]
                        if isinstance(sel, PortalRect):
                            self._aplicar_redimension_portal_rect(sel, x, y, self.resize_handle)
                        elif isinstance(sel, Spawn):
                            self._aplicar_redimension_spawn(sel, x, y, self.resize_handle)
                        self.cambios_pendientes = True
                    elif self.arrastrando and self.seleccionados:
                        x,y = self._screen_to_map(mx,my)
                        for i,o in enumerate(self.seleccionados):
                            offx, offy = self.grupo_offsets[i]
                            nx, ny = x+offx, y+offy
                            if isinstance(o, PortalPoly):
                                if o.puntos:
                                    px0,py0 = o.puntos[0]
                                    dx,dy = nx-px0, ny-py0
                                    o.puntos = [(px+dx, py+dy) for (px,py) in o.puntos]
                            elif isinstance(o, PortalRect):
                                o.x, o.y = nx, ny
                            else:
                                o.x, o.y = nx, ny
                        self.cambios_pendientes = True
                    if self.arrastrando_camara:
                        dx = mx - self.mouse_anterior[0]
                        dy = my - self.mouse_anterior[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.mouse_anterior = (mx,my)

            # Draw
            self.screen.fill(COLOR_FONDO)
            self.dibujar_panel()
            self.dibujar_mapa()
            self.dibujar_overlay()
            pygame.display.flip()
            self.clock.tick(FPS)

            # Autosave
            if self.cambios_pendientes and pygame.time.get_ticks()-self.ultimo_autosave>2000:
                self.ultimo_autosave = pygame.time.get_ticks()
                self.guardar()

if __name__ == '__main__':
    EditorPortales().run()
