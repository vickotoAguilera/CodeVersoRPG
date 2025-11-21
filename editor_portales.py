import pygame
import json
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

ANCHO, ALTO = 800, 600
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
    linked_portal: Optional[object] = None

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
    linked_portal: Optional[object] = None

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": "portal_enlazado",
            "forma": "poly",
            "puntos": [[int(pt[0]), int(pt[1])] for pt in self.puntos],
            "mapa_destino": self.mapa_destino,
            "spawn_destino_id": self.spawn_destino_id
        }


class SeccionDesplegable:
    """Implementación mínima para el panel de mapas: título, lista de items y expand/collapse."""
    def __init__(self, x, y, width, titulo):
        self.x = x
        self.y = y
        self.width = width
        self.titulo = titulo
        self.items = []
        self.expandida = False
        self.item_height = 20

    def toggle(self):
        self.expandida = not self.expandida

    def click_en_titulo(self, pos: Tuple[int,int]) -> bool:
        rx = pygame.Rect(self.x, self.y, self.width, 24)
        return rx.collidepoint(pos)

    def get_item_en_posicion(self, pos: Tuple[int,int]):
        if not self.expandida: return None
        ox, oy = pos
        rel_y = oy - (self.y + 24)
        if rel_y < 0: return None
        idx = rel_y // self.item_height
        if 0 <= idx < len(self.items):
            return self.items[int(idx)]
        return None

    def get_alto_total(self) -> int:
        return 24 + (len(self.items) * self.item_height if self.expandida else 0)

    def dibujar(self, surf):
        # Título
        pygame.draw.rect(surf, COLOR_BOTON, (self.x, self.y, self.width, 24), border_radius=4)
        txt = pygame.font.SysFont(None, 16).render(self.titulo, True, COLOR_TEXTO)
        surf.blit(txt, (self.x + 6, self.y + 4))
        # Items
        if self.expandida:
            y = self.y + 24
            for it in self.items:
                txt = pygame.font.SysFont(None, 14).render(str(it.nombre if hasattr(it,'nombre') else it), True, COLOR_TEXTO_SEC)
                surf.blit(txt, (self.x + 8, y + 2))
                y += self.item_height

@dataclass
class Spawn:
    id: str
    x: int
    y: int
    direccion: str = 'abajo'
    tam: int = 12
    linked_portal_id: str = ''

    def to_dict(self):
        return {"id": self.id, "x": int(self.x), "y": int(self.y), "direccion": self.direccion, "tam": int(self.tam), "linked_portal_id": self.linked_portal_id}


class EditorPortales:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 18)
        self.font_small = pygame.font.SysFont(None, 14)
        self.font_title = pygame.font.SysFont(None, 28)

        # Estado del editor
        self.secciones = []
        self.mostrar_ayuda = False
        self.editando_nombre = False
        self.portal_editando = None
        self.texto_nombre = ""
        self.portal_para_spawn = None
        self.lado_portal_spawn = None
        self.portal_vinculo_1 = None
        self.lado_vinculo_1 = None
        self.seleccionados = []
        self.lado_seleccion = None
        self.arrastrando = False
        self.arrastrando_mapa = False
        self.arrastrando_camara = False
        self.mouse_anterior = (0,0)
        self.lado_pan = None

        # Imágenes y transformaciones
        self.izq_img = None
        self.der_img = None
        self.izq_img_orig = None
        self.der_img_orig = None
        self.izq_rect = None
        self.der_rect = None
        self.izq_zoom = 1.0
        self.der_zoom = 1.0
        self.izq_offset_x = 0
        self.izq_offset_y = 0
        self.der_offset_x = 0
        self.der_offset_y = 0

        # Polígono / rect creation
        self.poligono_puntos = []
        self.dibujando_poligono = False
        self.lado_poly = None
        self.creando_rect = False
        self.rect_inicio = (0,0)
        self.lado_rect = None

        # Listas de objetos
        self.izq_portales = []
        self.der_portales = []
        self.izq_spawns = []
        self.der_spawns = []

        # Contadores y flags
        self.contador_spawns = 0
        self.contador_portales = 0
        self.cambios_pendientes = False
        self.ultimo_autosave = 0
        self._last_click_time = 0

        # Mapas cargados
        self.mapa_izq = None
        self.mapa_der = None

        # Mensajes/estado UI
        self.mensaje = None
        self.mensaje_ts = 0
        # usamos toggles para modos; eliminamos el campo 'modo' antiguo
        self.submodo = ''

        # Modal de confirmación (None o dict con tipo y datos)
        self.confirm_modal = None
        
        # Lista de portales vinculados
        self.seccion_vinculos = None
        self.seccion_portal_spawns = None

        # Toggle buttons state
        self.toggle_crear_portales = False
        self.toggle_crear_spawns = False
        self.toggle_enlazar_spawns = False
        self.cargar_mapas()
        # Inicializar contador de spawns leyendo los JSON existentes
        try:
            self._inicializar_contador_spawns()
        except Exception:
            # No crítico; continuar con contador en 0
            pass

    def _inicializar_contador_spawns(self):
        """Escanea los JSONs en `src/database/mapas` para inicializar
        `self.contador_spawns` con el mayor número encontrado en IDs existentes.
        Esto reduce la probabilidad de generar IDs duplicados.
        """
        base_dir = Path('src/database/mapas')
        if not base_dir.exists():
            return

        max_n = 0
        for json_file in base_dir.rglob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for s in data.get('spawns', []):
                    sid = None
                    if isinstance(s, dict):
                        sid = s.get('id')
                    elif isinstance(s, str):
                        sid = s
                    if not sid or not isinstance(sid, str):
                        continue
                    # Buscar un sufijo numérico al final del id
                    parts = sid.replace('-', '_').split('_')
                    if parts:
                        last = parts[-1]
                        try:
                            n = int(last)
                            if n > max_n:
                                max_n = n
                        except Exception:
                            # intentar detectar patrones como S_auto_12
                            for token in parts[::-1]:
                                try:
                                    n2 = int(token)
                                    if n2 > max_n:
                                        max_n = n2
                                    break
                                except Exception:
                                    continue
            except Exception:
                continue

        # Asegurar que el contador comience por encima del máximo encontrado
        if max_n > 0:
            self.contador_spawns = max_n

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
        
        # Incluir subcarpeta si existe (fix para sincronización con otros editores)
        if mapa.subcarpeta:
            carpeta = carpeta / mapa.subcarpeta
        
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

        # Antes de guardar, limpiar spawns huérfanos en cada mapa
        removed = []
        if self.mapa_izq:
            removed += self._limpiar_spawns_huerfanos(self.izq_portales, self.izq_spawns)
            self._guardar_mapa(self.mapa_izq, self.izq_portales, self.izq_spawns)
        if self.mapa_der:
            removed += self._limpiar_spawns_huerfanos(self.der_portales, self.der_spawns)
            self._guardar_mapa(self.mapa_der, self.der_portales, self.der_spawns)
        if removed:
            self._msg(f"✓ Eliminados spawns huérfanos: {', '.join(removed)}")
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
            
            # Contador para generar IDs únicos al cargar portales sin ID
            portal_counter = {}
            
            for p in data.get('portales', []):
                # Detectar estructura antigua con 'caja' (formato del juego)
                if 'caja' in p:
                    # Estructura del juego: {"caja": {"x": ..., "y": ..., "w": ..., "h": ...}, "mapa_destino": ...}
                    caja = p['caja']
                    x, y, w, h = caja['x'], caja['y'], caja['w'], caja['h']
                    mapa_dest = p.get('mapa_destino', '')
                    # Generar ID único basado en el mapa
                    portal_id = self._generar_portal_id_from_loaded(mapa.nombre, portal_counter)
                    spawn_dest_id = ''  # Los JSON antiguos no tienen spawn_destino_id
                else:
                    # Estructura del editor: {"id": ..., "x": ..., "y": ..., "w": ..., "h": ..., "mapa_destino": ..., "spawn_destino_id": ...}
                    x = p.get('x')
                    y = p.get('y')
                    w = p.get('w')
                    h = p.get('h')
                    mapa_dest = p.get('mapa_destino', '')
                    spawn_dest_id = p.get('spawn_destino_id', '')
                    # Si no tiene ID o está vacío, generar uno
                    portal_id = p.get('id', '') or self._generar_portal_id_from_loaded(mapa.nombre, portal_counter)
                
                # Crear portal según su forma
                if p.get('forma') == 'poly':
                    portales.append(PortalPoly(
                        portal_id,
                        [tuple(pt) for pt in p['puntos']],
                        mapa_dest,
                        spawn_dest_id
                    ))
                else:
                    # Solo crear si tenemos coordenadas válidas
                    if x is not None and y is not None and w is not None and h is not None:
                        portales.append(PortalRect(
                            portal_id,
                            x, y, w, h,
                            mapa_dest,
                            spawn_dest_id
                        ))
            
            for s in data.get('spawns', []):
                spawns.append(Spawn(
                    s.get('id', ''),
                    s['x'], s['y'],
                    s.get('direccion', 'abajo'),
                    s.get('tam', 12),
                    s.get('linked_portal_id', '')
                ))
        return portales, spawns


    def _limpiar_spawns_huerfanos(self, portales: List[object], spawns: List[Spawn]) -> List[str]:
        """Eliminar spawns que no están referenciados por ningún portal en este mapa.
        Devuelve la lista de ids eliminadas."""
        referenced = set()
        for p in portales:
            sid = getattr(p, 'spawn_destino_id', None)
            if sid:
                referenced.add(sid)
        removed = []
        # Mantener spawns cuyo id esté en referenced O que tengan linked_portal_id
        keep = []
        for s in spawns:
            # Mantener si está referenciado por un portal O si tiene un linked_portal_id válido
            has_portal_ref = s.id and s.id in referenced
            has_linked_portal = bool(getattr(s, 'linked_portal_id', ''))
            
            # DEBUG
            print(f"[DEBUG] Spawn {s.id}: portal_ref={has_portal_ref}, linked_portal_id='{getattr(s, 'linked_portal_id', '')}', has_linked={has_linked_portal}")
            
            if has_portal_ref or has_linked_portal:
                keep.append(s)
            else:
                if s.id:
                    removed.append(s.id)
                    print(f"[DEBUG] ❌ Eliminando spawn {s.id} (no tiene referencia ni linked_portal_id)")
        if removed:
            spawns[:] = keep
        return removed

    def _generar_spawn_id(self, mapa_from: str, mapa_to: str) -> str:
        """Genera un id de spawn legible y único, incluyendo nombres de mapas.

        El id tiene formato: S_{from}_{to}_{n} donde from/to son los nombres de mapa
        limpiados (solo alfanuméricos y guiones bajos) y n es un contador incremental.
        """
        def clean(name: str) -> str:
            if not name:
                return 'unknown'
            return ''.join(c if c.isalnum() else '_' for c in str(name))

        base_from = clean(mapa_from)
        base_to = clean(mapa_to)

        # Intentar generar un id que no exista ya en las listas cargadas
        while True:
            self.contador_spawns += 1
            candidate = f"S_{base_from}_{base_to}_{self.contador_spawns}"
            exists = False
            for s in (self.izq_spawns + self.der_spawns):
                if getattr(s, 'id', None) == candidate:
                    exists = True
                    break
            if not exists:
                return candidate

    def _generar_portal_id(self, mapa_name: str) -> str:
        """Genera un id legible para portal: portal_{mapa}, añadiendo sufijo numérico si ya existe."""
        def clean(name: str) -> str:
            if not name:
                return 'unknown'
            return ''.join(c if c.isalnum() else '_' for c in str(name))
        base = clean(mapa_name)
        candidate = f"portal_{base}"
        taken = {getattr(p, 'id', '') for p in (self.izq_portales + self.der_portales)}
        if candidate not in taken:
            return candidate
        # añadir sufijo incremental
        i = 1
        while True:
            c = f"{candidate}_{i}"
            if c not in taken:
                return c
            i += 1

    def _generar_portal_id_from_loaded(self, mapa_name: str, counter_dict: dict) -> str:
        """Genera ID único para portales cargados sin ID.
        
        Args:
            mapa_name: Nombre del mapa
            counter_dict: Diccionario para rastrear contadores por mapa
        
        Returns:
            ID único como 'portal_{mapa}_{n}'
        """
        def clean(name: str) -> str:
            if not name:
                return 'unknown'
            return ''.join(c if c.isalnum() else '_' for c in str(name))
        
        base = clean(mapa_name)
        if base not in counter_dict:
            counter_dict[base] = 0
        
        counter_dict[base] += 1
        return f"portal_{base}_{counter_dict[base]}"

    # --------- Confirm/Action helpers for modal ----------
    def _confirm_create_pair_spawns(self, modal):
        a = modal.get('portal_a')
        b = modal.get('portal_b')
        lado_a = modal.get('lado_a')
        lado_b = modal.get('lado_b')
        mapa_origen = modal.get('mapa_origen')
        mapa_dest = modal.get('mapa_dest')

        # Debug: log attempt
        try:
            print(f"[DEBUG] _confirm_create_pair_spawns called: a.id={getattr(a,'id',None)} lado_a={lado_a} a.spawn={getattr(a,'spawn_destino_id',None)} | b.id={getattr(b,'id',None)} lado_b={lado_b} b.spawn={getattr(b,'spawn_destino_id',None)} | mapa_origen={mapa_origen} mapa_dest={mapa_dest}")
        except Exception:
            print('[DEBUG] _confirm_create_pair_spawns called (could not format)')

        def centro_portal(p):
            if isinstance(p, PortalRect):
                cx = p.x + p.w//2
                cy = p.y + p.h//2
                return cx, cy
            elif isinstance(p, PortalPoly):
                xs = [pt[0] for pt in p.puntos]
                ys = [pt[1] for pt in p.puntos]
                if xs and ys:
                    return sum(xs)//len(xs), sum(ys)//len(ys)
            return 0, 0

        # Seguridad: no sobrescribir spawns o enlaces existentes.
        if getattr(a, 'spawn_destino_id', None):
            self._msg(f"⚠ '{a.id}' ya vinculado a '{a.mapa_destino}'. Click derecho en lista para desvincular.")
            print(f"[DEBUG] abort linking: portal_a ({getattr(a,'id',None)}) already has spawn {getattr(a,'spawn_destino_id',None)}")
            # limpiar selección de vinculación
            self.portal_vinculo_1 = None
            self.lado_vinculo_1 = None
            return
        if getattr(b, 'spawn_destino_id', None):
            self._msg(f"⚠ '{b.id}' ya vinculado a '{b.mapa_destino}'. Click derecho en lista para desvincular.")
            print(f"[DEBUG] abort linking: portal_b ({getattr(b,'id',None)}) already has spawn {getattr(b,'spawn_destino_id',None)}")
            self.portal_vinculo_1 = None
            self.lado_vinculo_1 = None
            return

        # Asignar IDs legibles a los portales si no tienen (respetando numeración única)
        if not getattr(a, 'id', None):
            a.id = self._generar_portal_id(mapa_origen)
        if not getattr(b, 'id', None):
            b.id = self._generar_portal_id(mapa_dest)
        # Marcar los mapas destino y enlace directo entre objetos
        a.mapa_destino = mapa_dest
        b.mapa_destino = mapa_origen
        a.linked_portal = b
        b.linked_portal = a

        spawn_a_id = self._generar_spawn_id(mapa_origen, mapa_dest)
        cx_a, cy_a = centro_portal(a)
        # Colocar spawn arriba del portal (50 píxeles arriba del centro)
        spawn_a = Spawn(id=spawn_a_id, x=cx_a, y=cy_a - 50, linked_portal_id=a.id)
        spawn_b_id = self._generar_spawn_id(mapa_dest, mapa_origen)
        cx_b, cy_b = centro_portal(b)
        # Colocar spawn arriba del portal (50 píxeles arriba del centro)
        spawn_b = Spawn(id=spawn_b_id, x=cx_b, y=cy_b - 50, linked_portal_id=b.id)

        # Añadir spawns a las listas correspondientes según el lado
        if lado_a == 'izq':
            self.izq_spawns.append(spawn_a)
        else:
            self.der_spawns.append(spawn_a)

        if lado_b == 'izq':
            self.izq_spawns.append(spawn_b)
        else:
            self.der_spawns.append(spawn_b)

        # Update portals to point to spawn destino ids (cross-link)
        a.spawn_destino_id = spawn_b_id
        b.spawn_destino_id = spawn_a_id

        self._msg(f"✓ Vinculados y spawns creados: {a.id} <-> {b.id}")
        self.cambios_pendientes = True
        # Limpiar selección de vinculación
        self.portal_vinculo_1 = None
        self.lado_vinculo_1 = None

    def _confirm_create_spawn(self, modal):
        portal = modal.get('portal')
        lado = modal.get('lado')
        mapa_name = modal.get('mapa_name')
        x,y = modal.get('pos')
        spawns_list = modal.get('spawns_list')

        if getattr(portal, 'spawn_destino_id', None):
            self._msg(f"⚠ {portal.id} ya tiene spawn vinculado ({portal.spawn_destino_id})")
            return

        nuevo_id = self._generar_spawn_id(mapa_name, '')
        nuevo_spawn = Spawn(id=nuevo_id, x=x, y=y, linked_portal_id=portal.id)
        spawns_list.append(nuevo_spawn)
        portal.spawn_destino_id = nuevo_spawn.id
        self._msg(f"✓ Spawn {nuevo_spawn.id} creado y vinculado a {portal.id}")
        self.cambios_pendientes = True

    def _confirm_unlink_spawn(self, modal):
        portal = modal.get('portal')
        lado = modal.get('lado')
        spawn_id = modal.get('spawn_id')
        # Limpiar referencia en el portal
        portal.spawn_destino_id = ''
        
        # Buscar el spawn y limpiar su linked_portal_id
        spawns = self.izq_spawns if lado=='izq' else self.der_spawns
        for s in spawns:
            if s.id == spawn_id:
                s.linked_portal_id = ''
                break
        
        # Intentar eliminar spawn si es huérfano en ese mapa
        # ¿Está referenciado por otro portal en el mismo mapa?
        referenced = False
        for p in (self.izq_portales if lado=='izq' else self.der_portales):
            if getattr(p, 'spawn_destino_id', None) == spawn_id:
                referenced = True
                break
        if not referenced:
            # eliminar del listado
            for s in list(spawns):
                if s.id == spawn_id:
                    spawns.remove(s)
                    self._msg(f"✓ Spawn {spawn_id} desvinculado y eliminado")
                    self.cambios_pendientes = True
                    return
        self._msg(f"✓ Spawn {spawn_id} desvinculado")
        self.cambios_pendientes = True

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

        # Botones toggles (pequeños) en el panel izquierdo, siempre visibles y fuera del área de mapas
        btn_h = 28
        btn_w = 86
        spacing = 8
        bx = 10
        by = ALTO - btn_h - 12

        rect_cp = pygame.Rect(bx, by, btn_w, btn_h)
        color_cp = (40, 160, 40) if self.toggle_crear_portales else COLOR_BOTON
        pygame.draw.rect(surf, color_cp, rect_cp, border_radius=6)
        txt = self.font_small.render("Crear P.", True, (0,0,0) if self.toggle_crear_portales else COLOR_TEXTO)
        surf.blit(txt, txt.get_rect(center=rect_cp.center))

        rect_cs = pygame.Rect(bx + btn_w + spacing, by, btn_w, btn_h)
        color_cs = (40, 160, 40) if self.toggle_crear_spawns else COLOR_BOTON
        pygame.draw.rect(surf, color_cs, rect_cs, border_radius=6)
        txt2 = self.font_small.render("Crear S.", True, (0,0,0) if self.toggle_crear_spawns else COLOR_TEXTO)
        surf.blit(txt2, txt2.get_rect(center=rect_cs.center))

        rect_en = pygame.Rect(bx + (btn_w + spacing) * 2, by, btn_w, btn_h)
        color_en = (40, 160, 40) if self.toggle_enlazar_spawns else COLOR_BOTON
        pygame.draw.rect(surf, color_en, rect_en, border_radius=6)
        txt3 = self.font_small.render("Enlazar", True, (0,0,0) if self.toggle_enlazar_spawns else COLOR_TEXTO)
        surf.blit(txt3, txt3.get_rect(center=rect_en.center))

        # Guardar rects para interacción de clicks (panel)
        self._btn_rects = {'crear_portales': rect_cp, 'crear_spawns': rect_cs, 'enlazar_spawns': rect_en}

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
            # Live-preview para rect mientras se está creando en el lado izquierdo
            if getattr(self, 'creando_rect', False) and getattr(self, 'lado_rect', None) == 'izq':
                mx,my = pygame.mouse.get_pos()
                # calcular coords en mapa
                x1,y1 = self.rect_inicio
                x2,y2 = self._screen_to_map(mx,my, 'izq', self.izq_offset_x, self.izq_offset_y, self.izq_zoom)
                x = min(x1,x2); y = min(y1,y2); w = abs(x2-x1); h = abs(y2-y1)
                if w>0 and h>0:
                    sx, sy = self._map_to_screen(x, y, 'izq', self.izq_offset_x, self.izq_offset_y, self.izq_zoom)
                    sw, sh = int(w*self.izq_zoom), int(h*self.izq_zoom)
                    # fondo semitransparente y borde
                    surf = pygame.Surface((max(1,sw), max(1,sh)), pygame.SRCALPHA)
                    surf.fill((40,180,40,60))
                    self.screen.blit(surf, (sx, sy))
                    pygame.draw.rect(self.screen, (40,200,40), (sx, sy, max(1,sw), max(1,sh)), 2)
                    # mostrar ID provisional y tamaño
                    mapa_name = self.mapa_izq.nombre if self.mapa_izq else ''
                    prov = self._generar_portal_id(mapa_name)
                    info_txt = f"{prov} ({w}x{h})"
                    t = self.font_small.render(info_txt, True, (220,220,220))
                    self.screen.blit(t, (sx+6, sy-18))
            self.screen.set_clip(None)
        
        # Derecha
        if self.der_img:
            self.screen.set_clip(der_rect)
            self.screen.blit(self.der_img, (der_rect.x+self.der_offset_x, self.der_offset_y))
            self._dibujar_objetos('der', self.der_portales, self.der_spawns, self.der_offset_x, self.der_offset_y, self.der_zoom)
            if self.dibujando_poligono and self.lado_poly == 'der':
                self._dibujar_poligono_construccion('der', self.der_offset_x, self.der_offset_y, self.der_zoom)
            # Live-preview para rect mientras se está creando en el lado derecho
            if getattr(self, 'creando_rect', False) and getattr(self, 'lado_rect', None) == 'der':
                mx,my = pygame.mouse.get_pos()
                x1,y1 = self.rect_inicio
                x2,y2 = self._screen_to_map(mx,my, 'der', self.der_offset_x, self.der_offset_y, self.der_zoom)
                x = min(x1,x2); y = min(y1,y2); w = abs(x2-x1); h = abs(y2-y1)
                if w>0 and h>0:
                    sx, sy = self._map_to_screen(x, y, 'der', self.der_offset_x, self.der_offset_y, self.der_zoom)
                    sw, sh = int(w*self.der_zoom), int(h*self.der_zoom)
                    surf = pygame.Surface((max(1,sw), max(1,sh)), pygame.SRCALPHA)
                    surf.fill((40,180,40,60))
                    self.screen.blit(surf, (sx, sy))
                    pygame.draw.rect(self.screen, (40,200,40), (sx, sy, max(1,sw), max(1,sh)), 2)
                    mapa_name = self.mapa_der.nombre if self.mapa_der else ''
                    prov = self._generar_portal_id(mapa_name)
                    info_txt = f"{prov} ({w}x{h})"
                    t = self.font_small.render(info_txt, True, (220,220,220))
                    self.screen.blit(t, (sx+6, sy-18))
            self.screen.set_clip(None)

        # (Live-preview and buttons moved to the left panel drawing to avoid overlap with map images)

    def _dibujar_objetos(self, lado, portales, spawns, offset_x, offset_y, zoom):
        # Portales
        for p in portales:
            # Visual según estado: disponible (no linked_portal) => fondo negro + borde VERDE + texto VERDE
            # enlazado => fondo negro + borde BLANCO + texto BLANCO
            linked = getattr(p, 'linked_portal', None)
            if linked:
                border_col = (255,255,255)
                text_col = (255,255,255)
            else:
                border_col = (0,200,80)
                text_col = (0,200,80)

            if isinstance(p, PortalPoly):
                pts = [self._map_to_screen(x,y, lado, offset_x, offset_y, zoom) for x,y in p.puntos]
                if len(pts)>=3:
                    # fondo negro
                    pygame.draw.polygon(self.screen, (0,0,0), pts, 0)
                    pygame.draw.polygon(self.screen, border_col, pts, 2)
                    cx = sum(pt[0] for pt in pts)//len(pts)
                    cy = sum(pt[1] for pt in pts)//len(pts)
                    if p.id:
                        txt = self.font_small.render(p.id, True, text_col)
                        bg_rect = txt.get_rect(center=(cx, cy-15))
                        bg_rect.inflate_ip(8, 4)
                        pygame.draw.rect(self.screen, (0,0,0), bg_rect, border_radius=4)
                        pygame.draw.rect(self.screen, border_col, bg_rect, 1, border_radius=4)
                        self.screen.blit(txt, txt.get_rect(center=(cx, cy-15)))
                        # Mostrar destino si está vinculado
                        if linked and p.mapa_destino:
                            dest_txt = self.font_small.render(f"→ {p.mapa_destino}", True, (180,180,180))
                            self.screen.blit(dest_txt, (cx-dest_txt.get_width()//2, cy+15))
            else:
                sx, sy = self._map_to_screen(p.x, p.y, lado, offset_x, offset_y, zoom)
                rw, rh = int(p.w*zoom), int(p.h*zoom)
                pygame.draw.rect(self.screen, (0,0,0), (sx, sy, rw, rh))
                pygame.draw.rect(self.screen, border_col, (sx, sy, rw, rh), 2)
                if p.id:
                    txt = self.font_small.render(p.id, True, text_col)
                    bg_rect = txt.get_rect(topleft=(sx+4, sy-20))
                    bg_rect.inflate_ip(8, 4)
                    pygame.draw.rect(self.screen, (0,0,0), bg_rect, border_radius=4)
                    pygame.draw.rect(self.screen, border_col, bg_rect, 1, border_radius=4)
                    self.screen.blit(txt, (sx+6, sy-18))
                    # Mostrar destino si está vinculado
                    if linked and p.mapa_destino:
                        dest_txt = self.font_small.render(f"→ {p.mapa_destino}", True, (180,180,180))
                        self.screen.blit(dest_txt, (sx+6, sy+rh+2))
        
        
        # Spawns
        for s in spawns:
            sx, sy = self._map_to_screen(s.x, s.y, lado, offset_x, offset_y, zoom)
            half = max(6, int(s.tam * zoom / 2))
            
            # Determinar color según estado de enlazado
            is_linked = bool(getattr(s, 'linked_portal_id', ''))
            if is_linked:
                # Spawn enlazado: BLANCO con fondo NEGRO
                spawn_col = (255, 255, 255)
                text_col = (255, 255, 255)
                bg_rect = pygame.Rect(sx-half-2, sy-half-2, half*2+4, half*2+4)
                pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
                pygame.draw.rect(self.screen, spawn_col, bg_rect, 2)
            else:
                # Spawn sin enlazar: VERDE
                spawn_col = (0, 200, 80)
                text_col = (0, 200, 80)
                pygame.draw.rect(self.screen, spawn_col, (sx-half, sy-half, half*2, half*2), 2)
            
            # Línea de dirección
            vec = {"arriba":(0,-18),"abajo":(0,18),"izquierda":(-18,0),"derecha":(18,0)}.get(s.direccion, (0,18))
            pygame.draw.line(self.screen, spawn_col, (sx, sy), (sx+vec[0], sy+vec[1]), 2)
            
            # Nombre (fusionado si está enlazado)
            if s.id:
                if is_linked and s.linked_portal_id:
                    display_name = f"{s.linked_portal_id}_{s.id}"
                else:
                    display_name = s.id
                
                txt = self.font_small.render(display_name, True, text_col)
                if is_linked:
                    txt_rect = txt.get_rect(topleft=(sx+8, sy-20))
                    txt_rect.inflate_ip(4, 2)
                    pygame.draw.rect(self.screen, (0, 0, 0), txt_rect, border_radius=3)
                    pygame.draw.rect(self.screen, spawn_col, txt_rect, 1, border_radius=3)
                self.screen.blit(txt, (sx+8, sy-18))

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
            modo_txt = []
            if self.toggle_crear_portales:
                modo_txt.append('Crear Portales')
            if self.toggle_crear_spawns:
                modo_txt.append('Crear Spawns')
            if self.toggle_enlazar_spawns:
                modo_txt.append('Enlazar Spawns')
            if modo_txt:
                info.append(' | '.join(modo_txt))
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

        # Indicador de modo en esquina superior derecha (fondo negro)
        modo_txt = None
        if self.toggle_crear_portales:
            modo_txt = "MODO: CREAR PORTALES"
        elif self.toggle_crear_spawns:
            modo_txt = "MODO: CREAR SPAWNS"

        if modo_txt:
            box_w = 320
            box_h = 28
            x = ANCHO - box_w - 10
            y = 8
            fondo = pygame.Surface((box_w, box_h))
            fondo.fill((0,0,0))
            fondo.set_alpha(220)
            self.screen.blit(fondo, (x, y))
            txt = self.font_small.render(modo_txt, True, (220,220,220))
            self.screen.blit(txt, (x + 8, y + 6))

        # Dibujar modal de confirmación si existe
        if self.confirm_modal:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            rect = pygame.Rect(ANCHO//2-300, ALTO//2-80, 600, 160)
            pygame.draw.rect(self.screen, (30,30,40), rect, border_radius=8)
            pygame.draw.rect(self.screen, (120,160,220), rect, 2, border_radius=8)
            tlines = []
            ctype = self.confirm_modal.get('type')
            if ctype == 'create_pair_spawns':
                tlines = ["Crear 2 spawns automáticos para la vinculación?", "ENTER: Confirmar | ESC: Cancelar"]
            elif ctype == 'create_spawn':
                tlines = ["Crear spawn en el centro del viewport y vincular?", "ENTER: Confirmar | ESC: Cancelar"]
            elif ctype == 'unlink_spawn':
                sid = self.confirm_modal.get('spawn_id')
                tlines = [f"Desvincular spawn {sid} del portal seleccionado?", "ENTER: Confirmar | ESC: Cancelar"]
            y = rect.y + 18
            for line in tlines:
                t = self.font_small.render(line, True, COLOR_TEXTO)
                self.screen.blit(t, (rect.x+20, y))
                y += t.get_height() + 8

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
                    # Si hay un modal de confirmación activo, procesarlo primero
                    if self.confirm_modal:
                        if ev.key == pygame.K_RETURN:
                            c = self.confirm_modal
                            if c.get('type') == 'create_pair_spawns':
                                self._confirm_create_pair_spawns(c)
                            elif c.get('type') == 'create_spawn':
                                self._confirm_create_spawn(c)
                            elif c.get('type') == 'unlink_spawn':
                                self._confirm_unlink_spawn(c)
                            self.confirm_modal = None
                        elif ev.key == pygame.K_ESCAPE:
                            self._msg('Acción cancelada')
                            self.confirm_modal = None
                        # No procesar otras teclas cuando modal activo
                        continue
                    else:
                        # Si estamos editando un nombre, procesar entrada de texto primero
                        if self.editando_nombre:
                            if ev.key == pygame.K_RETURN:
                                if self.portal_editando:
                                    new_name = self.texto_nombre.strip()
                                    if new_name:
                                        # aplicar al portal y propagar al enlazado
                                        self.portal_editando.id = new_name
                                        linked = getattr(self.portal_editando, 'linked_portal', None)
                                        if linked:
                                            linked.id = new_name
                                        self._actualizar_lista_vinculos()
                                        self._actualizar_lista_portal_spawns()
                                        self.cambios_pendientes = True
                                        self._msg(f"✓ Nombre actualizado: {new_name}")
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
                            # ya procesado
                            continue

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
                            # Alternativa: activar toggle Crear Portales
                            self.toggle_crear_portales = not self.toggle_crear_portales
                            if self.toggle_crear_portales:
                                self.toggle_crear_spawns = False
                                self.toggle_enlazar_spawns = False
                            self._msg("Toggle Crear Portales")
                        elif ev.key == pygame.K_s:
                            self.toggle_crear_spawns = not self.toggle_crear_spawns
                            if self.toggle_crear_spawns:
                                self.toggle_crear_portales = False
                                self.toggle_enlazar_spawns = False
                            self._msg("Toggle Crear Spawns")
                        elif ev.key == pygame.K_l:
                            # 'L' ahora activa el submodo polígono si Crear Portales está activo
                            if self.toggle_crear_portales:
                                self.submodo = 'poly'
                                self._msg("Polígono: Click, Enter crea")
                        elif ev.key == pygame.K_g:
                            self.guardar()
                        elif ev.key == pygame.K_u:
                            # Desvincular spawn del portal seleccionado
                            if self.seleccionados and len(self.seleccionados)==1:
                                sel = self.seleccionados[0]
                                if isinstance(sel, (PortalRect, PortalPoly)) and getattr(sel, 'spawn_destino_id', None):
                                    # abrir modal de confirmación
                                    self.confirm_modal = {
                                        'type': 'unlink_spawn',
                                        'portal': sel,
                                        'lado': self.lado_seleccion,
                                        'spawn_id': sel.spawn_destino_id
                                    }
                                else:
                                    self._msg("Selecciona un portal con spawn vinculado")
                            else:
                                self._msg("Selecciona un solo portal para desvincular")
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
                            # Solo permitir creación de polígonos si el toggle de crear portales está activo
                            if self.toggle_crear_portales and self.submodo=='poly' and self.dibujando_poligono and len(self.poligono_puntos)>=3:
                                lado = self.lado_poly
                                mapa_name = self.mapa_izq.nombre if lado=='izq' and self.mapa_izq else (self.mapa_der.nombre if lado=='der' and self.mapa_der else '')
                                new_id = self._generar_portal_id(mapa_name)
                                if lado == 'izq':
                                    self.izq_portales.append(PortalPoly(id=new_id, puntos=self.poligono_puntos[:]))
                                else:
                                    self.der_portales.append(PortalPoly(id=new_id, puntos=self.poligono_puntos[:]))
                                self.poligono_puntos=[]; self.dibujando_poligono=False
                                self._msg(f"✓ Portal poligonal {new_id} creado")
                                self.cambios_pendientes = True
                                # Si estamos en modo ENLAZAR y hay un portal 1 seleccionado en el otro lado,
                                # abrir modal para crear pair spawns y vincular ambos portales.
                                if self.toggle_enlazar_spawns and getattr(self, 'portal_vinculo_1', None):
                                    # determinar el portal recién creado (ultimo de la lista)
                                    new_portal = (self.izq_portales[-1] if lado=='izq' else self.der_portales[-1])
                                    if self.lado_vinculo_1 and self.lado_vinculo_1 != lado:
                                        mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                        mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                        self.confirm_modal = {
                                            'type': 'create_pair_spawns',
                                            'portal_a': self.portal_vinculo_1,
                                            'lado_a': self.lado_vinculo_1,
                                            'portal_b': new_portal,
                                            'lado_b': lado,
                                            'mapa_origen': mapa_origen,
                                            'mapa_dest': mapa_dest
                                        }
                                        self._msg('Confirmar creación de spawns para vinculación (ENTER/ESC)')
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
                                # ¿Click en botones toggles?
                                br = getattr(self, '_btn_rects', None)
                                if br:
                                    if br['crear_portales'].collidepoint((mx,my)):
                                        # activar crear portales y desactivar otros
                                        self.toggle_crear_portales = not self.toggle_crear_portales
                                        if self.toggle_crear_portales:
                                            self.toggle_crear_spawns = False
                                            self.toggle_enlazar_spawns = False
                                        continue
                                    if br['crear_spawns'].collidepoint((mx,my)):
                                        self.toggle_crear_spawns = not self.toggle_crear_spawns
                                        if self.toggle_crear_spawns:
                                            self.toggle_crear_portales = False
                                            self.toggle_enlazar_spawns = False
                                        continue
                                    if br['enlazar_spawns'].collidepoint((mx,my)):
                                        self.toggle_enlazar_spawns = not self.toggle_enlazar_spawns
                                        if self.toggle_enlazar_spawns:
                                            self.toggle_crear_portales = False
                                            self.toggle_crear_spawns = False
                                        continue
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

                                # Alt+LeftClick: seleccionar/link por nombres
                                keys = pygame.key.get_pressed()
                                mods = pygame.key.get_mods()
                                alt_held = keys[pygame.K_LALT] or keys[pygame.K_RALT]
                                if alt_held and isinstance(obj, (PortalRect, PortalPoly)):
                                    if self.portal_vinculo_1 is None:
                                        self.portal_vinculo_1 = obj
                                        self.lado_vinculo_1 = lado
                                        self._msg("✓ Portal 1 seleccionado (Alt+Click)")
                                    elif self.portal_vinculo_1 is obj:
                                        self._msg("Portal ya seleccionado")
                                    else:
                                        if lado == self.lado_vinculo_1:
                                            self._msg("⚠ Debes seleccionar portal del otro mapa")
                                        else:
                                            if getattr(self.portal_vinculo_1, 'spawn_destino_id', None):
                                                self._msg("⚠ Portal origen ya tiene un spawn vinculado. Desvincula primero.")
                                            elif getattr(obj, 'spawn_destino_id', None):
                                                self._msg("⚠ Portal destino ya tiene un spawn vinculado. Desvincula primero.")
                                            else:
                                                mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                                mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                                self.confirm_modal = {
                                                    'type': 'create_pair_spawns',
                                                    'portal_a': self.portal_vinculo_1,
                                                    'lado_a': self.lado_vinculo_1,
                                                    'portal_b': obj,
                                                    'lado_b': lado,
                                                    'mapa_origen': mapa_origen,
                                                    'mapa_dest': mapa_dest
                                                }
                                                # Ejecutar inmediatamente la creación/vinculación en vez de abrir modal
                                                self._confirm_create_pair_spawns({
                                                    'portal_a': self.portal_vinculo_1,
                                                    'lado_a': self.lado_vinculo_1,
                                                    'portal_b': obj,
                                                    'lado_b': lado,
                                                    'mapa_origen': mapa_origen,
                                                    'mapa_dest': mapa_dest
                                                })
                                    continue

                                if obj:
                                    # Doble-click para editar nombre
                                    if es_doble and isinstance(obj, (PortalRect, PortalPoly)):
                                        self.editando_nombre = True
                                        self.portal_editando = obj
                                        self.lado_editando = lado
                                        self.texto_nombre = obj.id or ""
                                        self._msg("Editando nombre...")
                                    else:
                                        # Vinculación — solo disponible en modo 'portal'
                                        if isinstance(obj, (PortalRect, PortalPoly)):
                                            if not (self.toggle_crear_portales or self.toggle_enlazar_spawns):
                                                self._msg("Modo SPAWN: portales desactivados")
                                            else:
                                                # Shift+Click para modo portal→spawn
                                                if mods & pygame.KMOD_SHIFT:
                                                    self.portal_para_spawn = obj
                                                    self.lado_portal_spawn = lado
                                                    self._msg(f"✓ {obj.id or 'Portal'} seleccionado. Click DERECHO para spawn")
                                                elif self.portal_vinculo_1 is None:
                                                    if not (self.mapa_izq and self.mapa_der):
                                                        self._msg("⚠ Carga 2 mapas primero")
                                                    else:
                                                        self.portal_vinculo_1 = obj
                                                        self.lado_vinculo_1 = lado
                                                        self._msg("✓ Portal 1 seleccionado")
                                                elif self.portal_vinculo_1 is not obj:
                                                    if lado == self.lado_vinculo_1:
                                                        self._msg("⚠ Debes seleccionar portal del otro mapa")
                                                    else:
                                                        if getattr(self.portal_vinculo_1, 'spawn_destino_id', None):
                                                            self._msg("⚠ Portal origen ya tiene un spawn vinculado. Desvincula primero.")
                                                        elif getattr(obj, 'spawn_destino_id', None):
                                                            self._msg("⚠ Portal destino ya tiene un spawn vinculado. Desvincula primero.")
                                                        else:
                                                            mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                                            mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                                            self.confirm_modal = {
                                                                'type': 'create_pair_spawns',
                                                                'portal_a': self.portal_vinculo_1,
                                                                'lado_a': self.lado_vinculo_1,
                                                                'portal_b': obj,
                                                                'lado_b': lado,
                                                                'mapa_origen': mapa_origen,
                                                                'mapa_dest': mapa_dest
                                                            }
                                                            self._msg('Confirmar creación de spawns para vinculación (ENTER/ESC)')

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
                                    if self.toggle_crear_spawns:
                                        izq_rect, der_rect = self._get_viewport_rects()
                                        vp_rect = izq_rect if lado=='izq' else der_rect
                                        center_screen_x = vp_rect.x + vp_rect.width//2
                                        center_screen_y = ALTO//2
                                        cx, cy = self._screen_to_map(center_screen_x, center_screen_y, lado, offset_x, offset_y, zoom)
                                        new_id = self._generar_spawn_id(
                                            self.mapa_izq.nombre if lado=='izq' and self.mapa_izq else (self.mapa_der.nombre if lado=='der' and self.mapa_der else ''),
                                            '')
                                        spawns.append(Spawn(id=new_id, x=cx, y=cy))
                                        self._msg(f"✓ Spawn {new_id} creado en el centro")
                                        self.cambios_pendientes = True
                                    elif self.toggle_crear_portales:
                                        if self.submodo=='poly':
                                            self.poligono_puntos.append((x,y))
                                            self.dibujando_poligono=True
                                            self.lado_poly = lado
                                        else:
                                            self.creando_rect = True
                                            self.rect_inicio = (x,y)
                                            self.lado_rect = lado
                    elif ev.button == 3:
                        # Right-click: manejar polígono o acciones específicas
                        if self.submodo=='poly' and self.dibujando_poligono and self.poligono_puntos:
                            self.poligono_puntos.pop()
                            if not self.poligono_puntos: self.dibujando_poligono=False
                        else:
                            # Si el click derecho cae en el panel izquierdo, interpretar como acción sobre listas
                            if mx < PANEL_ANCHO:
                                # comprobar si se clickeó un item en vínculos
                                item_v = self.seccion_vinculos.get_item_en_posicion((mx,my)) if self.seccion_vinculos else None
                                if item_v:
                                    # formato: "{portal_id} <-> {mapa_destino}"
                                    texto = str(item_v.nombre)
                                    parts = texto.split(' <-> ')
                                    portal_id = parts[0].strip() if parts else texto
                                    # localizar el portal y desvincularlo
                                    found = None
                                    for lst, lado in ((self.izq_portales,'izq'), (self.der_portales,'der')):
                                        for p in list(lst):
                                            if getattr(p,'id',None) == portal_id:
                                                found = (p,lst,lado)
                                                break
                                        if found: break
                                    if found:
                                        p, lst, lado_p = found
                                        linked = getattr(p, 'linked_portal', None)
                                        # eliminar spawns relacionados (el spawn que quedó en este mapa suele estar en linked.spawn_destino_id)
                                        spawns = self.izq_spawns if lado_p=='izq' else self.der_spawns
                                        if linked:
                                            # spawn en este mapa referenciado por linked.spawn_destino_id
                                            spawn_to_remove = getattr(linked, 'spawn_destino_id', None)
                                            if spawn_to_remove:
                                                for s in list(spawns):
                                                    if s.id == spawn_to_remove:
                                                        spawns.remove(s)
                                                        break
                                            # limpiar partner
                                            linked.linked_portal = None
                                            linked.mapa_destino = ''
                                            linked.spawn_destino_id = ''
                                        # si este portal referenciaba spawn en otro mapa, eliminar ese spawn también
                                        other_spawns = self.der_spawns if lado_p=='izq' else self.izq_spawns
                                        spawn_id_ref = getattr(p,'spawn_destino_id', None)
                                        if spawn_id_ref:
                                            for s in list(other_spawns):
                                                if s.id == spawn_id_ref:
                                                    other_spawns.remove(s)
                                                    break
                                        # finalmente eliminar el portal
                                        try:
                                            lst.remove(p)
                                        except Exception:
                                            pass
                                        self._msg(f"✓ Vinculo {portal_id} eliminado")
                                        self.cambios_pendientes = True
                                    else:
                                        self._msg("No se encontró portal para eliminar")
                                    continue

                                item_s = self.seccion_portal_spawns.get_item_en_posicion((mx,my)) if self.seccion_portal_spawns else None
                                if item_s:
                                    # formato: "{portal_id} → {spawn_id}"
                                    texto = str(item_s.nombre)
                                    parts = texto.split(' → ')
                                    if len(parts) < 2:
                                        parts = texto.split(' -> ')
                                    portal_id = parts[0].strip()
                                    spawn_id = parts[1].strip() if len(parts)>1 else ''
                                    # localizar portal y desvincular spawn
                                    found = None
                                    for lst, spawns, lado in ((self.izq_portales,self.izq_spawns,'izq'), (self.der_portales,self.der_spawns,'der')):
                                        for p in lst:
                                            if getattr(p,'id',None) == portal_id:
                                                found = (p, spawns, lado)
                                                break
                                        if found: break
                                    if found:
                                        p, spawns_list, lado_p = found
                                        # desvincular
                                        sid = getattr(p,'spawn_destino_id',None)
                                        p.spawn_destino_id = ''
                                        # eliminar spawn si no referenciado por otros
                                        referenced = False
                                        for other in (self.izq_portales if lado_p=='izq' else self.der_portales):
                                            if getattr(other,'spawn_destino_id',None) == sid:
                                                referenced = True; break
                                        if not referenced:
                                            for s in list(spawns_list):
                                                if s.id == sid:
                                                    spawns_list.remove(s)
                                                    break
                                        self._msg(f"✓ Spawn {sid} desvinculado de {portal_id}")
                                        self.cambios_pendientes = True
                                    else:
                                        self._msg("No se encontró portal para desvincular spawn")
                                    continue

                                # Si no fue item del panel, caer a comportamiento normal
                            lado = self._detectar_lado(mx)
                            if lado:
                                portales = self.izq_portales if lado=='izq' else self.der_portales
                                spawns = self.izq_spawns if lado=='izq' else self.der_spawns
                                offset_x = self.izq_offset_x if lado=='izq' else self.der_offset_x
                                offset_y = self.izq_offset_y if lado=='izq' else self.der_offset_y
                                zoom = self.izq_zoom if lado=='izq' else self.der_zoom
                                x,y = self._screen_to_map(mx,my, lado, offset_x, offset_y, zoom)
                                obj = self._obj_en_pos(x,y, portales, spawns)

                                if obj and isinstance(obj, (PortalRect, PortalPoly)):
                                    # Si estamos en modo CREAR PORTALES, click derecho elimina el portal
                                    if self.toggle_crear_portales:
                                        # eliminar portal y limpiar referencias cruzadas
                                        linked = getattr(obj, 'linked_portal', None)
                                        # spawns en este lado
                                        spawns_this = self.izq_spawns if lado=='izq' else self.der_spawns
                                        # spawns en otro lado
                                        spawns_other = self.der_spawns if lado=='izq' else self.izq_spawns
                                        # si hay partner, eliminar spawn correspondiente en este mapa (normalmente linked.spawn_destino_id)
                                        if linked:
                                            spawn_in_this = getattr(linked, 'spawn_destino_id', None)
                                            if spawn_in_this:
                                                for s in list(spawns_this):
                                                    if s.id == spawn_in_this:
                                                        spawns_this.remove(s)
                                                        break
                                            # limpiar partner
                                            linked.linked_portal = None
                                            linked.mapa_destino = ''
                                            linked.spawn_destino_id = ''
                                        # eliminar spawn en otro lado que este portal referenciaba
                                        spawn_ref = getattr(obj, 'spawn_destino_id', None)
                                        if spawn_ref:
                                            for s in list(spawns_other):
                                                if s.id == spawn_ref:
                                                    spawns_other.remove(s)
                                                    break
                                        # finalmente eliminar el portal
                                        try:
                                            portales.remove(obj)
                                        except Exception:
                                            pass
                                        self.seleccionados = []
                                        self.lado_seleccion = None
                                        self.cambios_pendientes = True
                                        self._msg(f"✓ Portal eliminado")
                                        continue

                                    # Preferir portal->spawn flow si está activo
                                    if self.toggle_crear_spawns and self.portal_para_spawn and lado == self.lado_portal_spawn:
                                        izq_rect, der_rect = self._get_viewport_rects()
                                        vp_rect = izq_rect if lado=='izq' else der_rect
                                        center_screen_x = vp_rect.x + vp_rect.width//2
                                        center_screen_y = ALTO//2
                                        cx,cy = self._screen_to_map(center_screen_x, center_screen_y, lado, offset_x, offset_y, zoom)
                                        spawn_existente = None
                                        for s in spawns:
                                            half = max(8, int(s.tam/2))
                                            if abs(s.x - cx) <= half and abs(s.y - cy) <= half:
                                                spawn_existente = s
                                                break
                                        if spawn_existente:
                                            self.portal_para_spawn.spawn_destino_id = spawn_existente.id
                                            self._msg(f"✓ {self.portal_para_spawn.id} → {spawn_existente.id}")
                                        else:
                                            if getattr(self.portal_para_spawn, 'spawn_destino_id', None):
                                                self._msg(f"⚠ {self.portal_para_spawn.id} ya tiene spawn vinculado ({self.portal_para_spawn.spawn_destino_id})")
                                            else:
                                                mapa_name = self.mapa_izq.nombre if lado=='izq' and self.mapa_izq else (self.mapa_der.nombre if lado=='der' and self.mapa_der else '')
                                                self.confirm_modal = {
                                                    'type': 'create_spawn',
                                                    'portal': self.portal_para_spawn,
                                                    'lado': lado,
                                                    'mapa_name': mapa_name,
                                                    'pos': (cx, cy),
                                                    'spawns_list': spawns
                                                }
                                                self._msg('Confirmar creación de spawn en centro del viewport (ENTER/ESC)')

                                        self.portal_para_spawn = None
                                        self.lado_portal_spawn = None
                                        self.cambios_pendientes = True
                                    else:
                                        # Right-click linking between two portals
                                        if self.portal_vinculo_1 is None:
                                            self.portal_vinculo_1 = obj
                                            self.lado_vinculo_1 = lado
                                            self._msg("✓ Portal 1 seleccionado (right-click)")
                                        elif self.portal_vinculo_1 is obj:
                                            self._msg("Portal ya seleccionado")
                                        else:
                                            if lado == self.lado_vinculo_1:
                                                self._msg("⚠ Debes seleccionar portal del otro mapa")
                                            else:
                                                if getattr(self.portal_vinculo_1, 'spawn_destino_id', None):
                                                    self._msg("⚠ Portal origen ya tiene un spawn vinculado. Desvincula primero.")
                                                elif getattr(obj, 'spawn_destino_id', None):
                                                    self._msg("⚠ Portal destino ya tiene un spawn vinculado. Desvincula primero.")
                                                else:
                                                    mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                                    mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                                    self.confirm_modal = {
                                                        'type': 'create_pair_spawns',
                                                        'portal_a': self.portal_vinculo_1,
                                                        'lado_a': self.lado_vinculo_1,
                                                        'portal_b': obj,
                                                        'lado_b': lado,
                                                        'mapa_origen': mapa_origen,
                                                        'mapa_dest': mapa_dest
                                                    }
                                                    self._msg('Confirmar creación de spawns para vinculación (ENTER/ESC)')
                                else:
                                    self.arrastrando_camara = True
                                    self.mouse_anterior = (mx,my)
                                    self.lado_pan = lado
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
                                    # Generar id legible automático basado en el mapa
                                    mapa_name = self.mapa_izq.nombre if lado=='izq' and self.mapa_izq else (self.mapa_der.nombre if lado=='der' and self.mapa_der else '')
                                    new_id = self._generar_portal_id(mapa_name)
                                    self.contador_portales += 1
                                    portales.append(PortalRect(id=new_id, x=x, y=y, w=w, h=h))
                                    self._msg(f"✓ Portal {new_id} creado")
                                    self.cambios_pendientes = True
                                    # Si estamos en modo ENLAZAR y hay un portal 1 seleccionado en el otro lado,
                                    # abrir modal para crear pair spawns y vincular ambos portales.
                                    if self.toggle_enlazar_spawns and getattr(self, 'portal_vinculo_1', None):
                                        new_portal = (self.izq_portales[-1] if lado=='izq' else self.der_portales[-1])
                                        if self.lado_vinculo_1 and self.lado_vinculo_1 != lado:
                                            mapa_origen = self.mapa_izq.nombre if self.lado_vinculo_1=='izq' else self.mapa_der.nombre
                                            mapa_dest = self.mapa_der.nombre if self.lado_vinculo_1=='izq' else self.mapa_izq.nombre
                                            # Vincular inmediatamente al crear el segundo portal
                                            self._confirm_create_pair_spawns({
                                                'portal_a': self.portal_vinculo_1,
                                                'lado_a': self.lado_vinculo_1,
                                                'portal_b': new_portal,
                                                'lado_b': lado,
                                                'mapa_origen': mapa_origen,
                                                'mapa_dest': mapa_dest
                                            })
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

            # (modal handled in KEYDOWN event processing)

if __name__ == '__main__':
    EditorPortales().run()
