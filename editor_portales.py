import pygame
import json
import subprocess
import sys
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
COLOR_PORTAL_ENLAZADO = (255, 105, 180)
COLOR_SPAWN = (80, 180, 255)
COLOR_SELECCION = (255, 215, 0)
COLOR_BORDE_DEST = (255, 140, 0)
COLOR_VINCULO_HOVER = (0, 255, 100)

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

class EditorPortales:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Portales - Dual Map - CodeVerso RPG")
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

        self.modo = 'portal'  # 'portal' | 'spawn'
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
        
        # Vinculación de portales
        self.portal_vinculo_1 = None
        self.lado_vinculo_1 = None
        
        # Vinculación portal→spawn
        self.portal_para_spawn = None
        self.lado_portal_spawn = None
        
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
        
        self.arrastrando_mapa = False
        self.mapa_arrastrado = None
        self._last_click_time = 0
        
        # Contadores para auto-numeración
        self.contador_portales = 0
        
        # Lista de portales vinculados
        self.seccion_vinculos = None
        self.seccion_portal_spawns = None

        self.cargar_mapas()

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
        # Crear sección de vínculos
        self.seccion_vinculos = SeccionDesplegable(10, y, PANEL_ANCHO-20, "Portales Vinculados")
        self.seccion_vinculos.expandida = True
        y += self.seccion_vinculos.get_alto_total() + 10
        # Crear sección portal→spawn
        self.seccion_portal_spawns = SeccionDesplegable(10, y, PANEL_ANCHO-20, "Portal → Spawn")
        self.seccion_portal_spawns.expandida = True

    def _buscar_mapas(self, carpeta: Path, categoria: str, subcarpeta: str = "") -> List[MapaInfo]:
        # Recolectar entradas por nombre base y evitar duplicados.
        # Preferimos archivos encontrados en subcarpetas (más específicos) frente a los del nivel superior.
        import os
        entries = {}
        base_path = Path(carpeta)
        for root, dirs, files in os.walk(base_path):
            rel_root = os.path.relpath(root, base_path)
            rel_root = '' if rel_root == '.' else rel_root.replace('\\', '/')
            for f in files:
                if not f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue
                stem = os.path.splitext(f)[0]
                # subcarpeta relativa dentro de la categoria
                sub = rel_root
                ruta = os.path.join(root, f)
                # Si ya existe una entrada con este stem, preferir la que tenga subcarpeta no vacía
                if stem in entries:
                    existing = entries[stem]
                    # si la existente no tiene subcarpeta but current does, replace
                    if (existing.subcarpeta == '' or existing.subcarpeta is None) and sub:
                        entries[stem] = MapaInfo(stem, f, ruta, categoria, sub)
                else:
                    entries[stem] = MapaInfo(stem, f, ruta, categoria, sub)
        return sorted(list(entries.values()), key=lambda m: m.nombre)
    
    def _actualizar_lista_vinculos(self):
        """Actualiza la lista de portales vinculados para mostrar en el panel"""
        vinculos = []
        # Buscar portales con mapa_destino en ambos lados
        for p in self.izq_portales:
            if isinstance(p, (PortalRect, PortalPoly)) and p.mapa_destino and p.id:
                info = MapaInfo(f"{p.id} <-> {p.mapa_destino}", "", "", "", "")
                vinculos.append(info)
        for p in self.der_portales:
            if isinstance(p, (PortalRect, PortalPoly)) and p.mapa_destino and p.id:
                info = MapaInfo(f"{p.id} <-> {p.mapa_destino}", "", "", "", "")
                vinculos.append(info)
        self.seccion_vinculos.items = vinculos
    
    def _actualizar_lista_portal_spawns(self):
        """Actualiza la lista de conexiones portal→spawn"""
        conexiones = []
        # Buscar portales con spawn_destino_id
        for p in self.izq_portales:
            if isinstance(p, (PortalRect, PortalPoly)) and p.spawn_destino_id:
                info = MapaInfo(f"{p.id or '(sin nombre)'} → {p.spawn_destino_id}", "", "", "", "")
                conexiones.append(info)
        for p in self.der_portales:
            if isinstance(p, (PortalRect, PortalPoly)) and p.spawn_destino_id:
                info = MapaInfo(f"{p.id or '(sin nombre)'} → {p.spawn_destino_id}", "", "", "", "")
                conexiones.append(info)
        self.seccion_portal_spawns.items = conexiones

    # --------- IO ----------
    def _ruta_json(self, mapa: MapaInfo) -> Path:
        carpeta = Path('src/database/mapas')/mapa.categoria
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta/(mapa.nombre + '.json')

    def guardar(self):
        # Validación: no permitir portales con mapa_destino vacío
        def tiene_portal_invalido(portales):
            for p in portales:
                md = getattr(p, 'mapa_destino', None)
                # permitir si None (no seteado)?? Requerimos no vacío string
                if md is not None and isinstance(md, str) and md.strip() == '':
                    return True
            return False

        if self.mapa_izq and tiene_portal_invalido(self.izq_portales):
            self._msg("⚠ Guardado abortado: portales con mapa_destino vacío en lado IZQ")
            return
        if self.mapa_der and tiene_portal_invalido(self.der_portales):
            self._msg("⚠ Guardado abortado: portales con mapa_destino vacío en lado DER")
            return

        if self.mapa_izq:
            self._guardar_mapa(self.mapa_izq, self.izq_portales, self.izq_spawns)
        if self.mapa_der:
            self._guardar_mapa(self.mapa_der, self.der_portales, self.der_spawns)
        self._msg("✓ Guardado")
        self.cambios_pendientes = False

        # Llamar al unificador para mantener JSONs finales consistentes
        try:
            merge_cmd = [sys.executable, str(Path('tools') / 'merge_map_parts.py'), '--apply']
            subprocess.run(merge_cmd, check=False)
            # Regenerar índice también
            gen = Path('tools') / 'generate_maps_index.py'
            if gen.exists():
                subprocess.run([sys.executable, str(gen)], check=False)
        except Exception:
            pass

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

    def _get_viewport_rects(self):
        w = (ANCHO - PANEL_ANCHO) // 2
        izq = pygame.Rect(PANEL_ANCHO, 0, w, ALTO)
        der = pygame.Rect(PANEL_ANCHO + w, 0, w, ALTO)
        return izq, der

    def _detectar_lado(self, mx):
        if mx < PANEL_ANCHO: return None
        izq_rect, der_rect = self._get_viewport_rects()
        if izq_rect.collidepoint(mx, ALTO//2): return 'izq'
        if der_rect.collidepoint(mx, ALTO//2): return 'der'
        return None

    def _map_to_screen(self, x, y, lado, offset_x, offset_y, zoom):
        izq_rect, der_rect = self._get_viewport_rects()
        base_x = izq_rect.x if lado == 'izq' else der_rect.x
        return int(x*zoom + offset_x + base_x), int(y*zoom + offset_y)

    def _screen_to_map(self, sx, sy, lado, offset_x, offset_y, zoom):
        izq_rect, der_rect = self._get_viewport_rects()
        base_x = izq_rect.x if lado == 'izq' else der_rect.x
        return int((sx - base_x - offset_x)/zoom), int((sy - offset_y)/zoom)

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

    def _obj_en_pos(self, x, y, portales, spawns) -> Optional[object]:
        for p in reversed(portales):
            if isinstance(p, PortalPoly):
                if self._punto_en_poly(p.puntos, x, y):
                    return p
            else:
                if p.x <= x <= p.x+p.w and p.y <= y <= p.y+p.h:
                    return p
        for s in reversed(spawns):
            half = max(8, int(s.tam/2))
            if abs(s.x - x) <= half and abs(s.y - y) <= half:
                return s
        return None

    # --------- Cargar mapa en viewport ----------
    def cargar_mapa_en_lado(self, info: MapaInfo, lado: str):
        try:
            img = pygame.image.load(info.ruta).convert_alpha()
            rect = img.get_rect()
            vp_rect = self._get_viewport_rects()[0 if lado=='izq' else 1]
            escala_x = vp_rect.width / rect.width
            escala_y = ALTO / rect.height
            zoom = min(escala_x, escala_y, 1.0)
            w = max(1, int(rect.width*zoom))
            h = max(1, int(rect.height*zoom))
            img_scaled = pygame.transform.smoothscale(img, (w,h))
            
            portales, spawns = self._cargar_mapa_data(info)
            
            if lado == 'izq':
                self.mapa_izq = info
                self.izq_img_orig = img
                self.izq_img = img_scaled
                self.izq_rect = rect
                self.izq_zoom = zoom
                self.izq_offset_x = (vp_rect.width - w)//2
                self.izq_offset_y = (ALTO - h)//2
                self.izq_portales = portales
                self.izq_spawns = spawns
            else:
                self.mapa_der = info
                self.der_img_orig = img
                self.der_img = img_scaled
                self.der_rect = rect
                self.der_zoom = zoom
                self.der_offset_x = (vp_rect.width - w)//2
                self.der_offset_y = (ALTO - h)//2
                self.der_portales = portales
                self.der_spawns = spawns
                
            self._msg(f"Mapa cargado en {lado}: {info.nombre}")
        except Exception as e:
            self._msg(f"Error: {e}")

    def _aplicar_zoom_lado(self, lado: str):
        if lado == 'izq' and self.izq_img_orig:
            w = max(1, int(self.izq_rect.width*self.izq_zoom))
            h = max(1, int(self.izq_rect.height*self.izq_zoom))
            self.izq_img = pygame.transform.smoothscale(self.izq_img_orig, (w,h))
        elif lado == 'der' and self.der_img_orig:
            w = max(1, int(self.der_rect.width*self.der_zoom))
            h = max(1, int(self.der_rect.height*self.der_zoom))
            self.der_img = pygame.transform.smoothscale(self.der_img_orig, (w,h))

    # --------- Draw ----------
    def dibujar_panel(self):
        surf = self.screen
        pygame.draw.rect(surf, COLOR_PANEL, (0,0,PANEL_ANCHO,ALTO))
        titulo = self.font_title.render("PORTALES", True, COLOR_TEXTO)
        surf.blit(titulo, (10,10))
        hint = self.font_small.render("Arrastra mapa a izq/der", True, COLOR_TEXTO_SEC)
        surf.blit(hint, (10, 40))
        y = 65
        for s in self.secciones:
            s.y = y
            s.dibujar(surf)
            y += s.get_alto_total() + 10
        # Lista de portales vinculados
        if self.seccion_vinculos:
            self._actualizar_lista_vinculos()
            self.seccion_vinculos.y = y
            self.seccion_vinculos.dibujar(surf)
            y += self.seccion_vinculos.get_alto_total() + 10
        # Lista de portal→spawn
        if self.seccion_portal_spawns:
            self._actualizar_lista_portal_spawns()
            self.seccion_portal_spawns.y = y
            self.seccion_portal_spawns.dibujar(surf)
            y += self.seccion_portal_spawns.get_alto_total() + 10
        # Botón de ayuda
        btn = pygame.Rect(PANEL_ANCHO-42, 12, 30, 26)
        mp = pygame.mouse.get_pos()
        pygame.draw.rect(surf, COLOR_BOTON_HOVER if btn.collidepoint(mp) else COLOR_BOTON, btn, border_radius=6)
        pygame.draw.rect(surf, COLOR_TEXTO, btn, 1, border_radius=6)
        q = self.font.render("?", True, COLOR_TEXTO)
        surf.blit(q, q.get_rect(center=btn.center))

    def dibujar_mapas(self):
        izq_rect, der_rect = self._get_viewport_rects()
        
        # Separador
        pygame.draw.line(self.screen, (60,60,80), (izq_rect.right,0), (izq_rect.right,ALTO), 2)
        
        # Labels
        if self.mapa_izq:
            txt = self.font.render(self.mapa_izq.nombre, True, COLOR_TEXTO)
            self.screen.blit(txt, (izq_rect.x+10, 10))
        if self.mapa_der:
            txt = self.font.render(self.mapa_der.nombre, True, COLOR_TEXTO)
            self.screen.blit(txt, (der_rect.x+10, 10))
        
        # Izquierda
        if self.izq_img:
            self.screen.set_clip(izq_rect)
            self.screen.blit(self.izq_img, (izq_rect.x+self.izq_offset_x, self.izq_offset_y))
            self._dibujar_objetos('izq', self.izq_portales, self.izq_spawns, self.izq_offset_x, self.izq_offset_y, self.izq_zoom)
            if self.dibujando_poligono and self.lado_poly == 'izq':
                self._dibujar_poligono_construccion('izq', self.izq_offset_x, self.izq_offset_y, self.izq_zoom)
            self.screen.set_clip(None)
        
        # Derecha
        if self.der_img:
            self.screen.set_clip(der_rect)
            self.screen.blit(self.der_img, (der_rect.x+self.der_offset_x, self.der_offset_y))
            self._dibujar_objetos('der', self.der_portales, self.der_spawns, self.der_offset_x, self.der_offset_y, self.der_zoom)
            if self.dibujando_poligono and self.lado_poly == 'der':
                self._dibujar_poligono_construccion('der', self.der_offset_x, self.der_offset_y, self.der_zoom)
            self.screen.set_clip(None)

    def _dibujar_objetos(self, lado, portales, spawns, offset_x, offset_y, zoom):
        # Portales
        for p in portales:
            if self.portal_para_spawn is p:
                color = (255, 255, 0)  # Amarillo para portal→spawn
            elif self.portal_vinculo_1 is p:
                color = COLOR_VINCULO_HOVER
            else:
                color = COLOR_PORTAL_ENLAZADO
            if isinstance(p, PortalPoly):
                pts = [self._map_to_screen(x,y, lado, offset_x, offset_y, zoom) for x,y in p.puntos]
                if len(pts)>=3:
                    pygame.draw.polygon(self.screen, color, pts, 0)
                    pygame.draw.polygon(self.screen, COLOR_BORDE_DEST, pts, 2)
                    cx = sum(pt[0] for pt in pts)//len(pts)
                    cy = sum(pt[1] for pt in pts)//len(pts)
                    if p.id:
                        txt = self.font_small.render(p.id, True, COLOR_TEXTO)
                        bg_rect = txt.get_rect(center=(cx, cy-15))
                        bg_rect.inflate_ip(8, 4)
                        pygame.draw.rect(self.screen, (0,0,0), bg_rect, border_radius=4)
                        pygame.draw.rect(self.screen, COLOR_BORDE_DEST, bg_rect, 1, border_radius=4)
                        self.screen.blit(txt, txt.get_rect(center=(cx, cy-15)))
            else:
                sx, sy = self._map_to_screen(p.x, p.y, lado, offset_x, offset_y, zoom)
                pygame.draw.rect(self.screen, color, (sx, sy, int(p.w*zoom), int(p.h*zoom)))
                pygame.draw.rect(self.screen, COLOR_BORDE_DEST, (sx, sy, int(p.w*zoom), int(p.h*zoom)), 2)
                if p.id:
                    txt = self.font_small.render(p.id, True, COLOR_TEXTO)
                    bg_rect = txt.get_rect(topleft=(sx+4, sy-20))
                    bg_rect.inflate_ip(8, 4)
                    pygame.draw.rect(self.screen, (0,0,0), bg_rect, border_radius=4)
                    pygame.draw.rect(self.screen, COLOR_BORDE_DEST, bg_rect, 1, border_radius=4)
                    self.screen.blit(txt, (sx+6, sy-18))
        
        # Spawns
        for s in spawns:
            sx, sy = self._map_to_screen(s.x, s.y, lado, offset_x, offset_y, zoom)
            half = max(6, int(s.tam * zoom / 2))
            pygame.draw.rect(self.screen, COLOR_SPAWN, (sx-half, sy-half, half*2, half*2), 1)
            vec = {"arriba":(0,-18),"abajo":(0,18),"izquierda":(-18,0),"derecha":(18,0)}.get(s.direccion, (0,18))
            pygame.draw.line(self.screen, COLOR_SPAWN, (sx, sy), (sx+vec[0], sy+vec[1]), 2)
            if s.id:
                self.screen.blit(self.font_small.render(s.id, True, COLOR_TEXTO), (sx+8, sy-18))

    def _dibujar_poligono_construccion(self, lado, offset_x, offset_y, zoom):
        if not self.poligono_puntos: return
        pts = [self._map_to_screen(x,y, lado, offset_x, offset_y, zoom) for x,y in self.poligono_puntos]
        if len(pts)>=2:
            pygame.draw.lines(self.screen, (0,255,255), False, pts, 2)
        if len(pts)>=3:
            pygame.draw.line(self.screen, (0,255,100), pts[-1], pts[0], 2)
        for i,pt in enumerate(pts):
            pygame.draw.circle(self.screen, (0,255,255), pt, 5)
            self.screen.blit(self.font_small.render(str(i+1), True, COLOR_TEXTO), (pt[0]+8, pt[1]-8))

    def dibujar_overlay(self):
        info = []
        if self.editando_nombre:
            info.append(f"Editando: {self.texto_nombre}_")
            info.append("ENTER: confirmar | ESC: cancelar")
        elif self.portal_para_spawn:
            info.append(f"Portal: {self.portal_para_spawn.id or '(sin nombre)'}")
            info.append("Click DERECHO en mapa para crear spawn")
            info.append("ESC: cancelar")
        elif self.portal_vinculo_1:
            lado_dest = 'derecho' if self.lado_vinculo_1 == 'izq' else 'izquierdo'
            info.append(f"PASO 2: Click en portal del lado {lado_dest}")
            info.append(f"Portal 1: {self.portal_vinculo_1.id or '(sin nombre)'}")
        else:
            info.append(f"Modo: {self.modo}/{self.submodo}")
            if self.mapa_izq and self.mapa_der:
                info.append("Portal: Click izq vincular | Click der→spawn")
        x = ANCHO - 380; y = 10
        for linea in info:
            t = self.font_small.render(linea, True, (230,230,230))
            pygame.draw.rect(self.screen, (40,40,50), (x-8,y-4, 260, t.get_height()+8), border_radius=6)
            self.screen.blit(t, (x, y))
            y += t.get_height()+6
        if self.mensaje and pygame.time.get_ticks()-self.mensaje_ts<3000:
            t = self.font_small.render(self.mensaje, True, COLOR_TEXTO)
            rect = t.get_rect(center=(ANCHO//2, 40))
            pygame.draw.rect(self.screen, (40,40,50), rect.inflate(16,8), border_radius=6)
            self.screen.blit(t, rect)

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
            "Arrastra mapa desde panel a izq/der para cargarlo",
            "P: Modo Portal | S: Modo Spawn | L: Polígono",
            "Click en portal: vinculación portal-portal",
            "Shift+Click en portal: modo portal→spawn, luego click derecho",
            "Doble-click: editar nombre | ENTER: confirmar",
            "DEL: eliminar | Rueda: Zoom | G: Guardar | H: Ayuda",
        ]
        for li in lineas:
            self.screen.blit(self.font_small.render(li, True, COLOR_TEXTO), (rect.x+18, y)); y+=22

    # --------- Main loop ---------
    def run(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if self.editando_nombre:
                        # Bloquear todas las teclas excepto edición
                        if ev.key == pygame.K_RETURN:
                            if self.portal_editando:
                                self.portal_editando.id = self.texto_nombre
                                self.cambios_pendientes = True
                                self._msg(f"✓ Nombre actualizado: {self.texto_nombre}")
                            self.editando_nombre = False
                            self.portal_editando = None
                        elif ev.key == pygame.K_ESCAPE:
                            self.editando_nombre = False
                            self.portal_editando = None
                            self._msg("Edición cancelada")
                        elif ev.key == pygame.K_BACKSPACE:
                            self.texto_nombre = self.texto_nombre[:-1]
                        else:
                            if ev.unicode and ev.unicode.isprintable():
                                self.texto_nombre += ev.unicode
                    else:
                        if ev.key == pygame.K_ESCAPE:
                            if self.mostrar_ayuda:
                                self.mostrar_ayuda = False
                            elif self.dibujando_poligono:
                                self.poligono_puntos=[]; self.dibujando_poligono=False
                            elif self.portal_para_spawn:
                                self.portal_para_spawn = None; self.lado_portal_spawn = None
                                self._msg("Vinculación portal→spawn cancelada")
                            elif self.portal_vinculo_1:
                                self.portal_vinculo_1 = None; self.lado_vinculo_1 = None
                                self._msg("Vinculación cancelada")
                            else:
                                running = False
                        elif ev.key == pygame.K_p:
                            self.modo = 'portal'; self._msg("Modo Portal (P)")
                        elif ev.key == pygame.K_s:
                            self.modo = 'spawn'; self._msg("Modo Spawn (S)")
                        elif ev.key == pygame.K_l:
                            if self.modo == 'portal':
                                self.submodo = 'poly'
                                self._msg("Polígono: Click, Enter crea")
                        elif ev.key == pygame.K_g:
                            self.guardar()
                        elif ev.key == pygame.K_h:
                            self.mostrar_ayuda = not self.mostrar_ayuda
                        elif ev.key == pygame.K_0:
                            lado = self._detectar_lado(pygame.mouse.get_pos()[0])
                            if lado == 'izq' and self.izq_img_orig:
                                self.izq_zoom = 1.0
                                self._aplicar_zoom_lado('izq')
                            elif lado == 'der' and self.der_img_orig:
                                self.der_zoom = 1.0
                                self._aplicar_zoom_lado('der')
                        elif ev.key == pygame.K_RETURN:
                            if self.submodo=='poly' and self.dibujando_poligono and len(self.poligono_puntos)>=3:
                                lado = self.lado_poly
                                self.contador_portales += 1
                                if lado == 'izq':
                                    self.izq_portales.append(PortalPoly(id=f"#{self.contador_portales}", puntos=self.poligono_puntos[:]))
                                else:
                                    self.der_portales.append(PortalPoly(id=f"#{self.contador_portales}", puntos=self.poligono_puntos[:]))
                                self.poligono_puntos=[]; self.dibujando_poligono=False
                                self._msg(f"✓ Portal poligonal #{self.contador_portales} creado")
                                self.cambios_pendientes = True
                        elif ev.key == pygame.K_DELETE:
                            if self.seleccionados and self.lado_seleccion:
                                portales = self.izq_portales if self.lado_seleccion=='izq' else self.der_portales
                                spawns = self.izq_spawns if self.lado_seleccion=='izq' else self.der_spawns
                                for o in self.seleccionados:
                                    if isinstance(o, Spawn) and o in spawns:
                                        spawns.remove(o)
                                    elif o in portales:
                                        portales.remove(o)
                                self.seleccionados.clear()
                                self.lado_seleccion = None
                                self.cambios_pendientes = True
                elif ev.type == pygame.MOUSEWHEEL:
                    mx = pygame.mouse.get_pos()[0]
                    lado = self._detectar_lado(mx)
                    if lado == 'izq' and self.izq_img_orig:
                        factor = 1.1 if ev.y>0 else 0.9
                        self.izq_zoom = max(0.25, min(1.0, self.izq_zoom*factor))
                        self._aplicar_zoom_lado('izq')
                    elif lado == 'der' and self.der_img_orig:
                        factor = 1.1 if ev.y>0 else 0.9
                        self.der_zoom = max(0.25, min(1.0, self.der_zoom*factor))
                        self._aplicar_zoom_lado('der')
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = ev.pos
                    if ev.button == 1:
                        # Detectar doble-click
                        tiempo_ahora = pygame.time.get_ticks()
                        es_doble = (tiempo_ahora - self._last_click_time) < 300
                        self._last_click_time = tiempo_ahora
                        
                        # Panel clicks
                        if mx < PANEL_ANCHO:
                            if pygame.Rect(PANEL_ANCHO-42,12,30,26).collidepoint((mx,my)):
                                self.mostrar_ayuda = not self.mostrar_ayuda
                            else:
                                for s in self.secciones:
                                    if s.click_en_titulo((mx,my)):
                                        s.toggle(); break
                                    item = s.get_item_en_posicion((mx,my))
                                    if item:
                                        # Iniciar arrastre
                                        self.arrastrando_mapa = True
                                        self.mapa_arrastrado = item
                                        break
                        else:
                            lado = self._detectar_lado(mx)
                            if lado:
                                portales = self.izq_portales if lado=='izq' else self.der_portales
                                spawns = self.izq_spawns if lado=='izq' else self.der_spawns
                                offset_x = self.izq_offset_x if lado=='izq' else self.der_offset_x
                                offset_y = self.izq_offset_y if lado=='izq' else self.der_offset_y
                                zoom = self.izq_zoom if lado=='izq' else self.der_zoom
                                x,y = self._screen_to_map(mx,my, lado, offset_x, offset_y, zoom)
                                obj = self._obj_en_pos(x,y, portales, spawns)
                                
                                if obj:
                                    # Doble-click para editar nombre
                                    if es_doble and isinstance(obj, (PortalRect, PortalPoly)):
                                        self.editando_nombre = True
                                        self.portal_editando = obj
                                        self.lado_editando = lado
                                        self.texto_nombre = obj.id or ""
                                        self._msg("Editando nombre...")
                                    else:
                                        # Vinculación
                                        if isinstance(obj, (PortalRect, PortalPoly)):
                                            # Shift+Click para modo portal→spawn
                                            mods = pygame.key.get_mods()
                                            if mods & pygame.KMOD_SHIFT:
                                                # Activar modo portal→spawn
                                                self.portal_para_spawn = obj
                                                self.lado_portal_spawn = lado
                                                self._msg(f"✓ {obj.id or 'Portal'} seleccionado. Click DERECHO para spawn")
                                            elif self.portal_vinculo_1 is None:
                                                # Verificar que hay dos mapas cargados
                                                if not (self.mapa_izq and self.mapa_der):
                                                    self._msg("⚠ Carga 2 mapas primero")
                                                else:
                                                    self.portal_vinculo_1 = obj
                                                    self.lado_vinculo_1 = lado
                                                    self._msg("✓ Portal 1 seleccionado")
                                            elif self.portal_vinculo_1 is not obj:
                                                # Verificar que sea del otro lado
                                                if lado == self.lado_vinculo_1:
                                                    self._msg("⚠ Debes seleccionar portal del otro mapa")
                                                else:
                                                    # Vincular y auto-nombrar
                                                    mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                                    mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                                    
                                                    nombre_vinculo = f"{mapa_origen}_{mapa_dest}"
                                                    self.portal_vinculo_1.id = f"P{nombre_vinculo}"
                                                    obj.id = f"P{mapa_dest}_{mapa_origen}"
                                                    
                                                    self.portal_vinculo_1.mapa_destino = mapa_dest
                                                    obj.mapa_destino = mapa_origen
                                                    
                                                    self._msg(f"✓ Vinculados: {self.portal_vinculo_1.id} <-> {obj.id}")
                                                    self.portal_vinculo_1 = None
                                                    self.lado_vinculo_1 = None
                                                    self.cambios_pendientes = True
                                        
                                        # Selección
                                        mods = pygame.key.get_mods()
                                        if mods & pygame.KMOD_SHIFT:
                                            if obj in self.seleccionados:
                                                self.seleccionados.remove(obj)
                                            else:
                                                self.seleccionados.append(obj)
                                        else:
                                            self.seleccionados = [obj]
                                        self.lado_seleccion = lado
                                        self.arrastrando = True
                                        self.grupo_offsets = []
                                        for o in self.seleccionados:
                                            if isinstance(o, PortalPoly) and o.puntos:
                                                px,py = o.puntos[0]
                                                self.grupo_offsets.append((px-x, py-y))
                                            elif isinstance(o, PortalRect):
                                                self.grupo_offsets.append((o.x-x, o.y-y))
                                            else:
                                                self.grupo_offsets.append((o.x-x, o.y-y))
                                else:
                                    # Crear
                                    if self.modo=='spawn':
                                        self.contador_portales += 1
                                        spawns.append(Spawn(id=f"S{self.contador_portales}", x=x, y=y))
                                        self._msg(f"✓ Spawn S{self.contador_portales} creado")
                                        self.cambios_pendientes = True
                                    elif self.modo=='portal':
                                        if self.submodo=='poly':
                                            self.poligono_puntos.append((x,y))
                                            self.dibujando_poligono=True
                                            self.lado_poly = lado
                                        else:
                                            self.creando_rect = True
                                            self.rect_inicio = (x,y)
                                            self.lado_rect = lado
                    elif ev.button == 3:
                        if self.submodo=='poly' and self.dibujando_poligono and self.poligono_puntos:
                            self.poligono_puntos.pop()
                            if not self.poligono_puntos: self.dibujando_poligono=False
                        elif self.portal_para_spawn:
                            # Click derecho para crear/vincular spawn
                            lado = self._detectar_lado(mx)
                            if lado and lado == self.lado_portal_spawn:
                                portales = self.izq_portales if lado=='izq' else self.der_portales
                                spawns = self.izq_spawns if lado=='izq' else self.der_spawns
                                offset_x = self.izq_offset_x if lado=='izq' else self.der_offset_x
                                offset_y = self.izq_offset_y if lado=='izq' else self.der_offset_y
                                zoom = self.izq_zoom if lado=='izq' else self.der_zoom
                                x,y = self._screen_to_map(mx,my, lado, offset_x, offset_y, zoom)
                                
                                # Verificar si click en spawn existente
                                spawn_existente = None
                                for s in spawns:
                                    half = max(8, int(s.tam/2))
                                    if abs(s.x - x) <= half and abs(s.y - y) <= half:
                                        spawn_existente = s
                                        break
                                
                                if spawn_existente:
                                    # Vincular a spawn existente
                                    self.portal_para_spawn.spawn_destino_id = spawn_existente.id
                                    self._msg(f"✓ {self.portal_para_spawn.id} → {spawn_existente.id}")
                                else:
                                    # Crear nuevo spawn y vincular
                                    self.contador_portales += 1
                                    nuevo_spawn = Spawn(id=f"S{self.contador_portales}", x=x, y=y)
                                    spawns.append(nuevo_spawn)
                                    self.portal_para_spawn.spawn_destino_id = nuevo_spawn.id
                                    self._msg(f"✓ Spawn {nuevo_spawn.id} creado y vinculado a {self.portal_para_spawn.id}")
                                
                                self.portal_para_spawn = None
                                self.lado_portal_spawn = None
                                self.cambios_pendientes = True
                            elif lado and lado != self.lado_portal_spawn:
                                self._msg("⚠ Debes crear el spawn en el mismo mapa del portal")
                        else:
                            self.arrastrando_camara = True
                            self.mouse_anterior = (mx,my)
                            self.lado_pan = self._detectar_lado(mx)
                    elif ev.button == 2:
                        self.arrastrando_camara = True
                        self.mouse_anterior = (mx,my)
                        self.lado_pan = self._detectar_lado(mx)
                elif ev.type == pygame.MOUSEBUTTONUP:
                    mx,my = ev.pos
                    if ev.button == 1:
                        if self.arrastrando_mapa:
                            lado = self._detectar_lado(mx)
                            if lado and self.mapa_arrastrado:
                                self.cargar_mapa_en_lado(self.mapa_arrastrado, lado)
                            self.arrastrando_mapa = False
                            self.mapa_arrastrado = None
                        if getattr(self,'creando_rect', False):
                            lado = getattr(self, 'lado_rect', None)
                            if lado:
                                portales = self.izq_portales if lado=='izq' else self.der_portales
                                offset_x = self.izq_offset_x if lado=='izq' else self.der_offset_x
                                offset_y = self.izq_offset_y if lado=='izq' else self.der_offset_y
                                zoom = self.izq_zoom if lado=='izq' else self.der_zoom
                                x1,y1 = self.rect_inicio
                                x2,y2 = self._screen_to_map(mx,my, lado, offset_x, offset_y, zoom)
                                x=min(x1,x2); y=min(y1,y2); w=abs(x2-x1); h=abs(y2-y1)
                                if w>5 and h>5:
                                    self.contador_portales += 1
                                    portales.append(PortalRect(id=f"#{self.contador_portales}", x=x, y=y, w=w, h=h))
                                    self._msg(f"✓ Portal #{self.contador_portales} creado")
                                    self.cambios_pendientes = True
                            self.creando_rect=False
                        if self.arrastrando:
                            self.arrastrando = False
                    if ev.button in (2,3):
                        self.arrastrando_camara = False
                        self.lado_pan = None
                elif ev.type == pygame.MOUSEMOTION:
                    mx,my = ev.pos
                    if self.arrastrando and self.seleccionados and self.lado_seleccion:
                        lado = self.lado_seleccion
                        offset_x = self.izq_offset_x if lado=='izq' else self.der_offset_x
                        offset_y = self.izq_offset_y if lado=='izq' else self.der_offset_y
                        zoom = self.izq_zoom if lado=='izq' else self.der_zoom
                        x,y = self._screen_to_map(mx,my, lado, offset_x, offset_y, zoom)
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
                    if self.arrastrando_camara and self.lado_pan:
                        dx = mx - self.mouse_anterior[0]
                        dy = my - self.mouse_anterior[1]
                        if self.lado_pan == 'izq':
                            self.izq_offset_x += dx
                            self.izq_offset_y += dy
                        else:
                            self.der_offset_x += dx
                            self.der_offset_y += dy
                        self.mouse_anterior = (mx,my)

            # Draw
            self.screen.fill(COLOR_FONDO)
            self.dibujar_panel()
            self.dibujar_mapas()
            self.dibujar_overlay()
            if self.mostrar_ayuda:
                self._dibujar_ayuda()
            pygame.display.flip()
            self.clock.tick(FPS)

            # Autosave
            if self.cambios_pendientes and pygame.time.get_ticks()-self.ultimo_autosave>2000:
                self.ultimo_autosave = pygame.time.get_ticks()
                self.guardar()

if __name__ == '__main__':
    EditorPortales().run()
