import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import pygame

ANCHO, ALTO = 1400, 820
FPS = 60

COLOR_FONDO = (18, 18, 24)
COLOR_PANEL = (34, 34, 46)
COLOR_PANEL_OSCURO = (26, 26, 36)
COLOR_TEXTO = (240, 240, 240)
COLOR_TEXTO_DIM = (160, 160, 170)
COLOR_BOTON = (58, 58, 82)
COLOR_BOTON_ACTIVO = (90, 90, 255)
COLOR_BORDE = (80, 80, 110)
COLOR_GRILLA = (70, 70, 92)
COLOR_SELECCION = (255, 215, 0)
COLOR_SELECCION_FONDO = (90, 210, 255)
COLOR_BLOQUEO = (220, 80, 80)
COLOR_SOBREPUESTO = (255, 120, 190)
COLOR_TIRADOR = (245, 245, 245)
COLOR_DEMO = (120, 220, 255)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
PREFABS_DIR = ASSETS_DIR / "prefabs"
PREFABS_DIR.mkdir(parents=True, exist_ok=True)

EXTS = (".png", ".jpg", ".jpeg")


class PiezaPrefab:
    def __init__(
        self,
        nombre,
        ruta,
        x=0,
        y=0,
        rotacion=0,
        flip_x=False,
        flip_y=False,
        grupo_id=None,
        en_fondo=False,
        escala=1.0,
        escala_x=None,
        escala_y=None,
    ):
        self.nombre = nombre
        self.ruta = Path(ruta)
        self.x = x
        self.y = y
        self.rotacion = rotacion
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.grupo_id = grupo_id
        self.en_fondo = en_fondo
        base_escala = float(escala)
        self.escala_x = float(escala_x) if escala_x is not None else base_escala
        self.escala_y = float(escala_y) if escala_y is not None else base_escala
        self.visible = True
        self.bloquea = True
        self.bloquea_jugador = True
        self.sobrepuesto = False
        self.surface_original = pygame.image.load(str(self.ruta)).convert_alpha()

    def get_surface(self):
        surf = self.surface_original
        if self.escala_x != 1.0 or self.escala_y != 1.0:
            w = max(1, int(surf.get_width() * self.escala_x))
            h = max(1, int(surf.get_height() * self.escala_y))
            surf = pygame.transform.smoothscale(surf, (w, h))
        if self.flip_x or self.flip_y:
            surf = pygame.transform.flip(surf, self.flip_x, self.flip_y)
        if self.rotacion % 360 != 0:
            surf = pygame.transform.rotate(surf, self.rotacion)
        return surf

    def get_rect(self):
        surf = self.get_surface()
        return pygame.Rect(self.x, self.y, surf.get_width(), surf.get_height())

    def to_dict(self):
        rel = self.ruta
        try:
            rel = self.ruta.relative_to(BASE_DIR)
        except Exception:
            pass
        return {
            "nombre": self.nombre,
            "ruta": str(rel).replace("\\", "/"),
            "x": self.x,
            "y": self.y,
            "rotacion": self.rotacion,
            "flip_x": self.flip_x,
            "flip_y": self.flip_y,
            "grupo_id": self.grupo_id,
            "en_fondo": self.en_fondo,
            "escala": (self.escala_x + self.escala_y) / 2.0,
            "escala_x": self.escala_x,
            "escala_y": self.escala_y,
            "visible": self.visible,
            "bloquea": self.bloquea,
            "bloquea_jugador": self.bloquea_jugador,
            "sobrepuesto": self.sobrepuesto,
        }


class ConstructorPrefabs:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Constructor de Prefabs - CodeVerso RPG")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("Arial", 16)
        self.fuente_bold = pygame.font.SysFont("Arial", 18, bold=True)

        self.running = True
        self.fullscreen = False
        self.scroll_lista = 0
        self.scroll_panel = 0
        self.grid_size = 32
        self.snap_to_grid = True
        self.mostrar_grilla = True

        self.mapa_fondo = None
        self.mapa_fondo_path = None

        self.ruta_base_carga = PREFABS_DIR
        self.carpetas_recursos = []
        self.recursos = []
        self.recurso_seleccionado = None
        self.recurso_hitboxes = []

        self.piezas = []
        self.pieza_activa_idx = None
        self.sel_multiple = []
        self.modo_agregar = False
        self.modo_mover = False
        self.modo_rotar = False
        self.modo_espejo = False
        self.modo_borrar = False
        self.modo_pegar = False
        self.arrastrando = False
        self.offset_arrastre = (0, 0)
        self.grilla_origen = (260, 90)
        self.portapapeles_piezas = []
        self.ultimo_grupo_id = 0
        self.resize_handles = []
        self.redimensionando = False
        self.redimension_info = None

        # Modo demo: jugador para probar choque y sobreposicion en vivo.
        self.demo_activa = False
        self.demo_velocidad = 210.0
        self.demo_jugador_surface = None
        self.demo_jugador_rect = pygame.Rect(32, 32, 28, 42)

        self.input_nombre_prefab = ""
        self.input_activo = None
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.preview_superficie = None
        self.preview_nombre = ""
        self.preview_rect = None
        self.barra_superior_h = 34

        self._cargar_demo_jugador()

        self._cargar_carpetas()
        self._cargar_recursos()

    def _cargar_demo_jugador(self):
        rutas = [
            ASSETS_DIR / "sprites" / "heroes" / "heroe_cloud.png",
            ASSETS_DIR / "sprites" / "heroes" / "heroe_sheet.png",
        ]
        for ruta in rutas:
            if not ruta.exists():
                continue
            try:
                surf = pygame.image.load(str(ruta)).convert_alpha()
                h_obj = 48
                escala = h_obj / max(1, surf.get_height())
                w = max(16, int(surf.get_width() * escala))
                h = max(24, int(surf.get_height() * escala))
                self.demo_jugador_surface = pygame.transform.smoothscale(surf, (w, h))
                self.demo_jugador_rect = pygame.Rect(32, 32, w, h)
                return
            except Exception:
                continue

    def _alternar_demo(self, canvas_rect):
        self.demo_activa = not self.demo_activa
        if self.demo_activa:
            self.demo_jugador_rect.x = max(0, min(canvas_rect.w - self.demo_jugador_rect.w, self.demo_jugador_rect.x))
            self.demo_jugador_rect.y = max(0, min(canvas_rect.h - self.demo_jugador_rect.h, self.demo_jugador_rect.y))
            self._set_mensaje("Modo DEMO ON (WASD/Flechas para mover)")
        else:
            self._set_mensaje("Modo DEMO OFF")

    def _actualizar_demo_jugador(self, canvas_rect):
        if not self.demo_activa or self.input_activo:
            return

        dt = self.reloj.get_time() / 1000.0
        if dt <= 0:
            return

        keys = pygame.key.get_pressed()
        dx = (1 if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) else 0) - (1 if (keys[pygame.K_a] or keys[pygame.K_LEFT]) else 0)
        dy = (1 if (keys[pygame.K_s] or keys[pygame.K_DOWN]) else 0) - (1 if (keys[pygame.K_w] or keys[pygame.K_UP]) else 0)
        if dx == 0 and dy == 0:
            return

        if dx != 0 and dy != 0:
            norma = 0.7071
            dx *= norma
            dy *= norma

        mov_x = dx * self.demo_velocidad * dt
        mov_y = dy * self.demo_velocidad * dt

        bloqueadores = [pieza.get_rect() for pieza in self.piezas if pieza.visible and pieza.bloquea_jugador]
        nuevo = self.demo_jugador_rect.copy()

        # Resolver eje X
        nuevo.x += int(round(mov_x))
        for rect_b in bloqueadores:
            if nuevo.colliderect(rect_b):
                if mov_x > 0:
                    nuevo.right = rect_b.left
                elif mov_x < 0:
                    nuevo.left = rect_b.right

        # Resolver eje Y
        nuevo.y += int(round(mov_y))
        for rect_b in bloqueadores:
            if nuevo.colliderect(rect_b):
                if mov_y > 0:
                    nuevo.bottom = rect_b.top
                elif mov_y < 0:
                    nuevo.top = rect_b.bottom

        nuevo.x = max(0, min(canvas_rect.w - nuevo.w, nuevo.x))
        nuevo.y = max(0, min(canvas_rect.h - nuevo.h, nuevo.y))
        self.demo_jugador_rect = nuevo

    def _aplicar_modo(self, nombre_modo):
        self.modo_agregar = nombre_modo == "agregar"
        self.modo_mover = nombre_modo == "mover"
        self.modo_rotar = nombre_modo == "rotar"
        self.modo_espejo = nombre_modo == "espejo"
        self.modo_borrar = nombre_modo == "borrar"
        self.modo_pegar = nombre_modo == "pegar"

    def _actualizar_preview_recurso(self):
        if not self.recurso_seleccionado:
            self.preview_superficie = None
            self.preview_nombre = ""
            return
        surf = pygame.image.load(str(self.recurso_seleccionado["ruta"])).convert_alpha()
        self.preview_superficie = surf
        self.preview_nombre = self.recurso_seleccionado["nombre"]

    def _alternar_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)

    def _rect_barra_superior(self):
        return pygame.Rect(0, 0, self.pantalla.get_width(), self.barra_superior_h)

    def _set_mensaje(self, texto):
        self.mensaje = texto
        self.tiempo_mensaje = pygame.time.get_ticks()

    def _cargar_carpetas(self):
        self.carpetas_recursos = []
        if not ASSETS_DIR.exists():
            ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        for ruta in sorted([p for p in ASSETS_DIR.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
            self.carpetas_recursos.append(ruta)
        if not self.carpetas_recursos:
            self.carpetas_recursos = [ASSETS_DIR]

    def _cargar_recursos(self):
        self.recursos = []
        for carpeta in self.carpetas_recursos:
            for root, _, files in os.walk(carpeta):
                if any(x in root.lower() for x in [".git", "__pycache__", "node_modules"]):
                    continue
                for archivo in files:
                    if archivo.lower().endswith(EXTS):
                        ruta = Path(root) / archivo
                        rel = ruta.relative_to(BASE_DIR) if ruta.is_relative_to(BASE_DIR) else ruta
                        nombre = f"{ruta.parent.name}/{archivo}"
                        self.recursos.append({"nombre": nombre, "ruta": ruta, "rel": str(rel).replace("\\", "/")})
        self.recursos.sort(key=lambda item: item["nombre"].lower())
        if self.recurso_seleccionado and self.recurso_seleccionado not in self.recursos:
            self.recurso_seleccionado = None
            self.preview_superficie = None
            self.preview_nombre = ""

    def _elegir_carpeta(self, titulo):
        root = tk.Tk()
        root.withdraw()
        carpeta = filedialog.askdirectory(title=titulo, initialdir=str(ASSETS_DIR), mustexist=True)
        root.destroy()
        if not carpeta:
            return None
        ruta = Path(carpeta)
        try:
            ruta.relative_to(ASSETS_DIR)
        except Exception:
            self._set_mensaje("Elige una carpeta dentro de assets")
            return None
        return ruta

    def _elegir_archivo_imagen(self, titulo):
        root = tk.Tk()
        root.withdraw()
        archivo = filedialog.askopenfilename(title=titulo, initialdir=str(ASSETS_DIR), filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        root.destroy()
        if not archivo:
            return None
        ruta = Path(archivo)
        if ruta.suffix.lower() not in EXTS:
            return None
        return ruta

    def _elegir_archivo_json(self, titulo):
        root = tk.Tk()
        root.withdraw()
        archivo = filedialog.askopenfilename(title=titulo, initialdir=str(PREFABS_DIR), filetypes=[("JSON", "*.json")])
        root.destroy()
        if not archivo:
            return None
        ruta = Path(archivo)
        if ruta.suffix.lower() != ".json":
            return None
        return ruta

    def _cargar_mapa_fondo(self, ruta):
        self.mapa_fondo_path = Path(ruta)
        self.mapa_fondo = pygame.image.load(str(self.mapa_fondo_path)).convert()
        self._set_mensaje(f"Mapa cargado: {self.mapa_fondo_path.name}")

    def _resolver_ruta_recurso(self, ruta_txt):
        ruta = Path(ruta_txt)
        candidatas = []
        if ruta.is_absolute():
            candidatas.append(ruta)
        else:
            candidatas.append(BASE_DIR / ruta)
            candidatas.append(ASSETS_DIR / ruta)
        for cand in candidatas:
            if cand.exists():
                return cand
        return None

    def _cargar_prefab_desde_json(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            self._set_mensaje(f"Error cargando JSON: {exc}")
            return

        piezas_json = data.get("piezas", [])
        nuevas_piezas = []
        faltantes = 0
        for rec in piezas_json:
            ruta_real = self._resolver_ruta_recurso(rec.get("ruta", ""))
            if not ruta_real:
                faltantes += 1
                continue

            pieza = PiezaPrefab(
                rec.get("nombre", ruta_real.name),
                ruta_real,
                int(rec.get("x", 0)),
                int(rec.get("y", 0)),
                int(rec.get("rotacion", 0)),
                bool(rec.get("flip_x", False)),
                bool(rec.get("flip_y", False)),
                rec.get("grupo_id"),
                bool(rec.get("en_fondo", False)),
                float(rec.get("escala", 1.0)),
                float(rec.get("escala_x", rec.get("escala", 1.0))),
                float(rec.get("escala_y", rec.get("escala", 1.0))),
            )
            pieza.visible = bool(rec.get("visible", True))
            bloquea = bool(rec.get("bloquea_jugador", rec.get("bloquea", True)))
            pieza.bloquea = bloquea
            pieza.bloquea_jugador = bloquea
            pieza.sobrepuesto = bool(rec.get("sobrepuesto", False))
            nuevas_piezas.append(pieza)

        indice_inicio = len(self.piezas)
        self.piezas.extend(nuevas_piezas)
        self.sel_multiple = list(range(indice_inicio, len(self.piezas)))
        self.pieza_activa_idx = self.sel_multiple[-1] if self.sel_multiple else None
        self.portapapeles_piezas = []

        nombre = data.get("nombre")
        if isinstance(nombre, str) and nombre.strip():
            self.input_nombre_prefab = nombre.strip()
        else:
            self.input_nombre_prefab = json_path.stem

        grid = data.get("grid_size")
        if isinstance(grid, int) and grid > 0:
            self.grid_size = grid

        mapa_fondo_txt = data.get("mapa_fondo")
        if mapa_fondo_txt:
            ruta_mapa = self._resolver_ruta_recurso(mapa_fondo_txt)
            if ruta_mapa:
                self._cargar_mapa_fondo(ruta_mapa)

        self._set_mensaje(f"Prefab importado: {len(nuevas_piezas)} piezas ({faltantes} faltantes)")

    def _buscar_pieza_por_pos(self, pos):
        x, y = pos
        for idx in range(len(self.piezas) - 1, -1, -1):
            pieza = self.piezas[idx]
            if pieza.visible and pieza.get_rect().collidepoint(x, y):
                return idx
        return None

    def _cargar_pieza_desde_recurso(self, rec, x, y):
        pieza = PiezaPrefab(rec["nombre"], rec["ruta"], x, y)
        if self.snap_to_grid:
            pieza.x = self._snap(pieza.x)
            pieza.y = self._snap(pieza.y)
        self.piezas.append(pieza)
        self.sel_multiple = [len(self.piezas) - 1]
        self._set_mensaje(f"Agregada pieza: {pieza.nombre}")

    def _snap(self, valor):
        if not self.snap_to_grid:
            return valor
        return (valor // self.grid_size) * self.grid_size

    def _seleccion_multiple_rects(self, rect_base):
        self.sel_multiple = []
        for idx, pieza in enumerate(self.piezas):
            if pieza.visible and rect_base.colliderect(pieza.get_rect()):
                self.sel_multiple.append(idx)

    def _mover_piezas_seleccionadas(self, dx, dy):
        for idx in self.sel_multiple:
            pieza = self.piezas[idx]
            pieza.x += dx
            pieza.y += dy

    def _escalar_seleccion(self, paso_rueda):
        if not self.sel_multiple:
            return
        factor = 1.08 if paso_rueda > 0 else 0.92
        cambio = False
        for idx in self.sel_multiple:
            pieza = self.piezas[idx]
            surf_antes = pieza.get_surface()
            cx = pieza.x + surf_antes.get_width() / 2.0
            cy = pieza.y + surf_antes.get_height() / 2.0

            nueva_escala_x = max(0.2, min(4.0, pieza.escala_x * factor))
            nueva_escala_y = max(0.2, min(4.0, pieza.escala_y * factor))
            if abs(nueva_escala_x - pieza.escala_x) < 1e-6 and abs(nueva_escala_y - pieza.escala_y) < 1e-6:
                continue

            pieza.escala_x = nueva_escala_x
            pieza.escala_y = nueva_escala_y
            surf_despues = pieza.get_surface()
            pieza.x = int(round(cx - surf_despues.get_width() / 2.0))
            pieza.y = int(round(cy - surf_despues.get_height() / 2.0))
            cambio = True

        if cambio:
            self._set_mensaje("Escala actualizada con rueda")

    def _tiradores_para_rect(self, rect, payload):
        tam = 8
        mitad = tam // 2
        puntos = {
            "nw": (rect.left, rect.top),
            "n": (rect.centerx, rect.top),
            "ne": (rect.right, rect.top),
            "e": (rect.right, rect.centery),
            "se": (rect.right, rect.bottom),
            "s": (rect.centerx, rect.bottom),
            "sw": (rect.left, rect.bottom),
            "w": (rect.left, rect.centery),
        }
        resultado = []
        for nombre, (px, py) in puntos.items():
            hrect = pygame.Rect(px - mitad, py - mitad, tam, tam)
            resultado.append((nombre, hrect, payload))
        return resultado

    def _rect_seleccion_canvas(self):
        if not self.sel_multiple:
            return None
        rects = []
        for idx in self.sel_multiple:
            if 0 <= idx < len(self.piezas):
                rects.append(self.piezas[idx].get_rect())
        if not rects:
            return None
        rect_union = rects[0].copy()
        for r in rects[1:]:
            rect_union = rect_union.union(r)
        return rect_union

    def _iniciar_redimension(self, payload, handle, mouse_canvas):
        if payload.get("tipo") == "pieza":
            idx = payload.get("idx", -1)
            if idx < 0 or idx >= len(self.piezas):
                return
            pieza = self.piezas[idx]
            surf = pieza.get_surface()
            self.redimensionando = True
            self.arrastrando = False
            self.redimension_info = {
                "tipo": "pieza",
                "idx": idx,
                "handle": handle,
                "x": float(pieza.x),
                "y": float(pieza.y),
                "w": float(max(1, surf.get_width())),
                "h": float(max(1, surf.get_height())),
                "mx": float(mouse_canvas[0]),
                "my": float(mouse_canvas[1]),
            }
            return

        if payload.get("tipo") == "grupo":
            indices = [idx for idx in payload.get("indices", []) if 0 <= idx < len(self.piezas)]
            if len(indices) < 2:
                return
            rect_grupo = self._rect_seleccion_canvas()
            if not rect_grupo:
                return

            piezas_info = []
            for idx in indices:
                pieza = self.piezas[idx]
                piezas_info.append(
                    {
                        "idx": idx,
                        "rel_x": float(pieza.x - rect_grupo.x),
                        "rel_y": float(pieza.y - rect_grupo.y),
                        "escala_x": float(pieza.escala_x),
                        "escala_y": float(pieza.escala_y),
                    }
                )

            self.redimensionando = True
            self.arrastrando = False
            self.redimension_info = {
                "tipo": "grupo",
                "indices": indices,
                "handle": handle,
                "x": float(rect_grupo.x),
                "y": float(rect_grupo.y),
                "w": float(max(1, rect_grupo.w)),
                "h": float(max(1, rect_grupo.h)),
                "mx": float(mouse_canvas[0]),
                "my": float(mouse_canvas[1]),
                "piezas": piezas_info,
            }

    def _actualizar_redimension(self, mouse_canvas):
        if not self.redimensionando or not self.redimension_info:
            return
        tipo = self.redimension_info.get("tipo")
        handle = self.redimension_info["handle"]
        dx = float(mouse_canvas[0]) - self.redimension_info["mx"]
        dy = float(mouse_canvas[1]) - self.redimension_info["my"]

        x = self.redimension_info["x"]
        y = self.redimension_info["y"]
        w = self.redimension_info["w"]
        h = self.redimension_info["h"]

        if "w" in handle:
            x += dx
            w -= dx
        if "e" in handle:
            w += dx
        if "n" in handle:
            y += dy
            h -= dy
        if "s" in handle:
            h += dy

        min_sz = 8.0
        if w < min_sz:
            if "w" in handle:
                x -= (min_sz - w)
            w = min_sz
        if h < min_sz:
            if "n" in handle:
                y -= (min_sz - h)
            h = min_sz

        # Alt + tirador en esquina: mantener proporcion al redimensionar.
        mods = pygame.key.get_mods()
        proporcional = bool(mods & pygame.KMOD_ALT) and len(handle) == 2
        if proporcional:
            w0 = max(1.0, self.redimension_info["w"])
            h0 = max(1.0, self.redimension_info["h"])
            dw = (w / w0) - 1.0
            dh = (h / h0) - 1.0
            k = 1.0 + (dw if abs(dw) >= abs(dh) else dh)
            k = max(min_sz / w0, min_sz / h0, k)
            w = w0 * k
            h = h0 * k
            x = self.redimension_info["x"] + (w0 - w if "w" in handle else 0.0)
            y = self.redimension_info["y"] + (h0 - h if "n" in handle else 0.0)

        if tipo == "pieza":
            idx = self.redimension_info["idx"]
            if idx < 0 or idx >= len(self.piezas):
                self.redimensionando = False
                self.redimension_info = None
                return

            pieza = self.piezas[idx]
            ow = max(1, pieza.surface_original.get_width())
            oh = max(1, pieza.surface_original.get_height())
            pieza.escala_x = max(0.05, min(8.0, w / ow))
            pieza.escala_y = max(0.05, min(8.0, h / oh))
            pieza.x = int(round(x))
            pieza.y = int(round(y))
            return

        if tipo == "grupo":
            w0 = max(1.0, self.redimension_info["w"])
            h0 = max(1.0, self.redimension_info["h"])
            sx = w / w0
            sy = h / h0

            for rec in self.redimension_info.get("piezas", []):
                idx = rec["idx"]
                if idx < 0 or idx >= len(self.piezas):
                    continue
                pieza = self.piezas[idx]
                pieza.x = int(round(x + rec["rel_x"] * sx))
                pieza.y = int(round(y + rec["rel_y"] * sy))
                pieza.escala_x = max(0.05, min(8.0, rec["escala_x"] * sx))
                pieza.escala_y = max(0.05, min(8.0, rec["escala_y"] * sy))

    def _actualizar_indices_seleccion(self, piezas_sel):
        piezas_set = set(piezas_sel)
        self.sel_multiple = [idx for idx, pieza in enumerate(self.piezas) if pieza in piezas_set]
        self.pieza_activa_idx = self.sel_multiple[-1] if self.sel_multiple else None

    def _enviar_seleccion_a_fondo(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        piezas_sel = [self.piezas[idx] for idx in self.sel_multiple]
        piezas_set = set(piezas_sel)
        restantes = [pieza for pieza in self.piezas if pieza not in piezas_set]
        self.piezas = piezas_sel + restantes
        for pieza in piezas_sel:
            pieza.en_fondo = True
        self._actualizar_indices_seleccion(piezas_sel)
        self._set_mensaje("Seleccion enviada al fondo")

    def _traer_seleccion_al_frente(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        piezas_sel = [self.piezas[idx] for idx in self.sel_multiple]
        piezas_set = set(piezas_sel)
        restantes = [pieza for pieza in self.piezas if pieza not in piezas_set]
        self.piezas = restantes + piezas_sel
        for pieza in piezas_sel:
            pieza.en_fondo = False
        self._actualizar_indices_seleccion(piezas_sel)
        self._set_mensaje("Seleccion traida al frente")

    def _alternar_profundidad_seleccion(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        if all(self.piezas[idx].en_fondo for idx in self.sel_multiple):
            self._traer_seleccion_al_frente()
        else:
            self._enviar_seleccion_a_fondo()

    def _alternar_colision_seleccion(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        activar = not all(self.piezas[idx].bloquea_jugador for idx in self.sel_multiple if 0 <= idx < len(self.piezas))
        for idx in self.sel_multiple:
            if 0 <= idx < len(self.piezas):
                self.piezas[idx].bloquea_jugador = activar
                self.piezas[idx].bloquea = activar
        self._set_mensaje("Colision ON" if activar else "Colision OFF")

    def _alternar_sobrepuesto_seleccion(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        activar = not all(self.piezas[idx].sobrepuesto for idx in self.sel_multiple if 0 <= idx < len(self.piezas))
        for idx in self.sel_multiple:
            if 0 <= idx < len(self.piezas):
                self.piezas[idx].sobrepuesto = activar
        self._set_mensaje("Pasar por detras ON" if activar else "Pasar por detras OFF")

    def _pegar_seleccion(self):
        if len(self.sel_multiple) < 2:
            self._set_mensaje("Selecciona 2 o mas piezas para pegar")
            return
        self.ultimo_grupo_id += 1
        for idx in self.sel_multiple:
            self.piezas[idx].grupo_id = self.ultimo_grupo_id
        self._set_mensaje(f"Bloque creado con {len(self.sel_multiple)} piezas")

    def _despegar_seleccion(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas")
            return
        total = 0
        for idx in self.sel_multiple:
            if self.piezas[idx].grupo_id is not None:
                self.piezas[idx].grupo_id = None
                total += 1
        if total:
            self._set_mensaje(f"Despegadas {total} piezas")
        else:
            self._set_mensaje("Las piezas seleccionadas ya estaban sueltas")

    def _copiar_seleccion(self):
        if not self.sel_multiple:
            self._set_mensaje("No hay piezas seleccionadas para copiar")
            return

        piezas_sel = [self.piezas[idx] for idx in self.sel_multiple]
        min_x = min(pieza.x for pieza in piezas_sel)
        min_y = min(pieza.y for pieza in piezas_sel)
        self.portapapeles_piezas = []

        for pieza in piezas_sel:
            self.portapapeles_piezas.append({
                "nombre": pieza.nombre,
                "ruta": str(pieza.ruta),
                "dx": pieza.x - min_x,
                "dy": pieza.y - min_y,
                "rotacion": pieza.rotacion,
                "flip_x": pieza.flip_x,
                "flip_y": pieza.flip_y,
                "grupo_id": pieza.grupo_id,
                "en_fondo": pieza.en_fondo,
                "escala": (pieza.escala_x + pieza.escala_y) / 2.0,
                "escala_x": pieza.escala_x,
                "escala_y": pieza.escala_y,
                "visible": pieza.visible,
                "bloquea": pieza.bloquea,
                "bloquea_jugador": pieza.bloquea_jugador,
                "sobrepuesto": pieza.sobrepuesto,
            })

        self._set_mensaje(f"Copiadas {len(self.portapapeles_piezas)} piezas")

    def _pegar_portapapeles_en(self, x, y):
        if not self.portapapeles_piezas:
            self._set_mensaje("Portapapeles vacio")
            return

        nuevos_indices = []
        for rec in self.portapapeles_piezas:
            pieza = PiezaPrefab(
                rec["nombre"],
                rec["ruta"],
                x + rec["dx"],
                y + rec["dy"],
                rec["rotacion"],
                rec["flip_x"],
                rec["flip_y"],
                rec.get("grupo_id"),
                rec.get("en_fondo", False),
                rec.get("escala", 1.0),
                rec.get("escala_x", rec.get("escala", 1.0)),
                rec.get("escala_y", rec.get("escala", 1.0)),
            )
            pieza.visible = rec["visible"]
            bloquea = rec.get("bloquea_jugador", rec.get("bloquea", True))
            pieza.bloquea = bloquea
            pieza.bloquea_jugador = bloquea
            pieza.sobrepuesto = rec.get("sobrepuesto", False)

            if self.snap_to_grid:
                pieza.x = self._snap(pieza.x)
                pieza.y = self._snap(pieza.y)

            self.piezas.append(pieza)
            nuevos_indices.append(len(self.piezas) - 1)

        self.sel_multiple = nuevos_indices
        self.pieza_activa_idx = nuevos_indices[0] if nuevos_indices else None
        self._set_mensaje(f"Pegadas {len(nuevos_indices)} piezas")

    def _pegar_portapapeles_con_offset(self):
        if not self.portapapeles_piezas:
            self._set_mensaje("Portapapeles vacio")
            return

        if self.sel_multiple:
            piezas_sel = [self.piezas[idx] for idx in self.sel_multiple]
            min_x = min(pieza.x for pieza in piezas_sel)
            min_y = min(pieza.y for pieza in piezas_sel)
            self._pegar_portapapeles_en(min_x + self.grid_size, min_y + self.grid_size)
        else:
            self._pegar_portapapeles_en(32, 32)

    def _guardar_prefab(self):
        nombre = self.input_nombre_prefab.strip()
        if not nombre:
            self._set_mensaje("Escribe un nombre para guardar")
            return
        if not self.piezas:
            self._set_mensaje("No hay piezas para guardar")
            return

        destino = PREFABS_DIR / nombre
        destino.mkdir(parents=True, exist_ok=True)

        # PNG preview
        limites = [pieza.get_rect() for pieza in self.piezas if pieza.visible]
        if not limites:
            self._set_mensaje("No hay piezas visibles")
            return
        min_x = min(r.left for r in limites)
        min_y = min(r.top for r in limites)
        max_x = max(r.right for r in limites)
        max_y = max(r.bottom for r in limites)
        w = max(1, max_x - min_x)
        h = max(1, max_y - min_y)
        preview = pygame.Surface((w, h), pygame.SRCALPHA)
        preview.fill((0, 0, 0, 0))
        for pieza in self.piezas:
            if not pieza.visible:
                continue
            surf = pieza.get_surface()
            preview.blit(surf, (pieza.x - min_x, pieza.y - min_y))

        png_path = destino / f"{nombre}.png"
        json_path = destino / f"{nombre}.json"
        pygame.image.save(preview, str(png_path))

        data = {
            "nombre": nombre,
            "ancho": w,
            "alto": h,
            "grid_size": self.grid_size,
            "mapa_fondo": str(self.mapa_fondo_path).replace("\\", "/") if self.mapa_fondo_path else None,
            "piezas": [pieza.to_dict() for pieza in self.piezas],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self._set_mensaje(f"Guardado: {png_path.name} y {json_path.name}")

    def _max_scroll_lista(self):
        alto_panel = self.pantalla.get_height() - self.barra_superior_h - 20
        panel_y = self.barra_superior_h + 10
        preview_bottom = panel_y + 108 + 108
        area_h = max(1, (panel_y + alto_panel) - (preview_bottom + 20))
        contenido_h = len(self.recursos) * 28
        return max(0, contenido_h - area_h)

    def _max_scroll_panel(self):
        alto_panel = self.pantalla.get_height() - self.barra_superior_h - 20
        area_h = max(1, alto_panel - 84)
        extras_count = 11
        lineas_count = 16
        contenido_h = 62 + 80 + (extras_count * 34) + 10 + 20 + (lineas_count * 20) + 10 + 22 + 18
        return max(0, contenido_h - area_h)

    def _dibujar_panel_izquierdo(self):
        panel = pygame.Rect(10, self.barra_superior_h + 10, 220, self.pantalla.get_height() - self.barra_superior_h - 20)
        pygame.draw.rect(self.pantalla, COLOR_PANEL, panel, border_radius=10)
        self.pantalla.blit(self.fuente_bold.render("Recursos", True, COLOR_TEXTO), (panel.x + 12, panel.y + 10))
        self.recurso_hitboxes = []

        boton_carpeta = pygame.Rect(panel.x + 10, panel.y + 38, panel.w - 20, 28)
        pygame.draw.rect(self.pantalla, COLOR_BOTON, boton_carpeta, border_radius=6)
        self.pantalla.blit(self.fuente.render("Agregar carpeta", True, COLOR_TEXTO), (boton_carpeta.x + 10, boton_carpeta.y + 6))

        boton_fondo = pygame.Rect(panel.x + 10, panel.y + 72, panel.w - 20, 28)
        pygame.draw.rect(self.pantalla, COLOR_BOTON, boton_fondo, border_radius=6)
        self.pantalla.blit(self.fuente.render("Cargar mapa fondo", True, COLOR_TEXTO), (boton_fondo.x + 10, boton_fondo.y + 6))

        preview_box = pygame.Rect(panel.x + 10, panel.y + 108, panel.w - 20, 108)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_OSCURO, preview_box, border_radius=8)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, preview_box, 2, border_radius=8)
        self.pantalla.blit(self.fuente.render("Vista previa", True, COLOR_TEXTO_DIM), (preview_box.x + 8, preview_box.y + 6))
        if self.preview_superficie:
            surf = self.preview_superficie
            escala = min((preview_box.w - 20) / max(surf.get_width(), 1), (preview_box.h - 28) / max(surf.get_height(), 1), 1.0)
            preview = pygame.transform.scale(surf, (max(1, int(surf.get_width() * escala)), max(1, int(surf.get_height() * escala))))
            self.pantalla.blit(preview, (preview_box.centerx - preview.get_width() // 2, preview_box.y + 24 + (preview_box.h - 28 - preview.get_height()) // 2))
        else:
            self.pantalla.blit(self.fuente.render("Selecciona un recurso", True, COLOR_TEXTO_DIM), (preview_box.x + 10, preview_box.y + 45))

        area_lista = pygame.Rect(panel.x + 8, preview_box.bottom + 10, panel.w - 16, panel.bottom - (preview_box.bottom + 20))
        pygame.draw.rect(self.pantalla, COLOR_PANEL_OSCURO, area_lista, border_radius=6)

        clip_prev = self.pantalla.get_clip()
        self.pantalla.set_clip(area_lista)
        y = area_lista.y - self.scroll_lista
        for rec in self.recursos:
            rect = pygame.Rect(area_lista.x, y, area_lista.w, 24)
            if rect.bottom >= area_lista.top and rect.top <= area_lista.bottom:
                activo = self.recurso_seleccionado == rec
                pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if activo else COLOR_PANEL_OSCURO, rect, border_radius=4)
                texto = self.fuente.render(rec["nombre"], True, COLOR_TEXTO)
                self.pantalla.blit(texto, (rect.x + 6, rect.y + 4))
                self.recurso_hitboxes.append((rect, rec))
            y += 28
        self.pantalla.set_clip(clip_prev)

    def _dibujar_panel_derecho(self):
        panel = pygame.Rect(self.pantalla.get_width() - 260, self.barra_superior_h + 10, 250, self.pantalla.get_height() - self.barra_superior_h - 20)
        pygame.draw.rect(self.pantalla, COLOR_PANEL, panel, border_radius=10)
        self.pantalla.blit(self.fuente_bold.render("Prefab", True, COLOR_TEXTO), (panel.x + 12, panel.y + 10))

        area_scroll = pygame.Rect(panel.x + 10, panel.y + 36, panel.w - 20, panel.h - 84)
        clip_prev = self.pantalla.get_clip()
        self.pantalla.set_clip(area_scroll)

        y = panel.y + 40 - self.scroll_panel
        self.pantalla.blit(self.fuente.render("Nombre:", True, COLOR_TEXTO_DIM), (panel.x + 12, y))
        caja_nombre = pygame.Rect(panel.x + 12, y + 20, panel.w - 24, 28)
        pygame.draw.rect(self.pantalla, COLOR_PANEL_OSCURO, caja_nombre, border_radius=6)
        nombre_mostrar = self.input_nombre_prefab if self.input_nombre_prefab else "<escribe nombre>"
        self.pantalla.blit(self.fuente.render(nombre_mostrar, True, COLOR_TEXTO), (caja_nombre.x + 8, caja_nombre.y + 6))

        y += 62
        botones = [
            ("Mover", self.modo_mover),
            ("Rotar", self.modo_rotar),
            ("Espejo", self.modo_espejo),
            ("Borrar", self.modo_borrar),
        ]
        for i, (label, activo) in enumerate(botones):
            rect = pygame.Rect(panel.x + 12 + (i % 2) * 112, y + (i // 2) * 36, 100, 28)
            pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if activo else COLOR_BOTON, rect, border_radius=5)
            self.pantalla.blit(self.fuente.render(label, True, COLOR_TEXTO), (rect.x + 16, rect.y + 6))

        y += 80
        extras = [
            ("Snap grilla", self.snap_to_grid),
            ("Grilla visible", self.mostrar_grilla),
            ("Agregar pieza", self.recurso_seleccionado is not None),
            ("Pegar seleccion", len(self.sel_multiple) >= 2),
            ("Despegar seleccion", any(self.piezas[idx].grupo_id is not None for idx in self.sel_multiple) if self.sel_multiple else False),
            ("Colision (B)", all(self.piezas[idx].bloquea_jugador for idx in self.sel_multiple) if self.sel_multiple else False),
            ("Pasar detras (Tab)", all(self.piezas[idx].sobrepuesto for idx in self.sel_multiple) if self.sel_multiple else False),
            ("Pegar bloque", bool(self.portapapeles_piezas)),
            ("Cargar prefab", True),
            ("Guardar prefab", False),
            ("Demo jugador (F5)", self.demo_activa),
        ]
        for label, estado in extras:
            rect = pygame.Rect(panel.x + 12, y, panel.w - 24, 28)
            pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if estado else COLOR_BOTON, rect, border_radius=5)
            self.pantalla.blit(self.fuente.render(label, True, COLOR_TEXTO), (rect.x + 10, rect.y + 6))
            y += 34

        y += 10
        self.pantalla.blit(self.fuente.render("Controles rápidos:", True, COLOR_TEXTO_DIM), (panel.x + 12, y))
        y += 20
        lineas = [
            "Click izq: seleccionar/mover",
            "Ctrl+Click: multi-seleccion",
            "Click der: colocar/editar rapido",
            "Shift: fondo/frente",
            "B: colision ON/OFF",
            "Tab: pasar detras ON/OFF",
            "Alt + tirador esquina: proporcional",
            "Ctrl+C / Ctrl+V: copiar/pegar",
            "Cargar prefab: importa y selecciona todo",
            "F5: demo jugador ON/OFF",
            "Supr: borrar pieza",
            "Rueda en lienzo: escalar seleccion",
            "Tiradores: estirar lados/esquinas",
            "R: rotar 90°",
            "X: espejo horizontal",
            "G: grilla",
        ]
        for linea in lineas:
            self.pantalla.blit(self.fuente.render(linea, True, COLOR_TEXTO), (panel.x + 12, y))
            y += 20

        y += 10
        self.pantalla.blit(self.fuente_bold.render("Bloqueo", True, COLOR_TEXTO), (panel.x + 12, y))
        y += 22
        self.pantalla.blit(self.fuente.render("B = colision, Tab = pasar detras.", True, COLOR_TEXTO), (panel.x + 12, y))
        y += 18
        self.pantalla.blit(self.fuente.render("Rosa indica capa sobrepuesta visual.", True, COLOR_TEXTO), (panel.x + 12, y))

        self.pantalla.set_clip(clip_prev)

        if self.mensaje and pygame.time.get_ticks() - self.tiempo_mensaje < 3000:
            msg = self.fuente_bold.render(self.mensaje, True, (255, 255, 255))
            self.pantalla.blit(msg, (panel.x + 12, panel.bottom - 30))

    def _dibujar_barra_superior(self):
        barra = self._rect_barra_superior()
        pygame.draw.rect(self.pantalla, (24, 24, 34), barra)
        titulo = self.fuente_bold.render("Constructor de Prefabs", True, COLOR_TEXTO)
        self.pantalla.blit(titulo, (12, 8))

        btn_cerrar = pygame.Rect(barra.right - 36, 5, 26, 24)
        btn_full = pygame.Rect(barra.right - 68, 5, 26, 24)
        btn_min = pygame.Rect(barra.right - 100, 5, 26, 24)

        for rect, texto in [(btn_min, "-"), (btn_full, "[]" if not self.fullscreen else "<>"), (btn_cerrar, "x")]:
            pygame.draw.rect(self.pantalla, COLOR_BOTON, rect, border_radius=4)
            label = self.fuente_bold.render(texto, True, COLOR_TEXTO)
            self.pantalla.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2 - 1))

    def _dibujar_canvas(self):
        canvas = pygame.Rect(240, self.barra_superior_h + 10, self.pantalla.get_width() - 510, self.pantalla.get_height() - self.barra_superior_h - 20)
        pygame.draw.rect(self.pantalla, (12, 12, 18), canvas, border_radius=10)
        self.resize_handles = []

        self._actualizar_demo_jugador(canvas)

        if self.mapa_fondo:
            fondo = pygame.transform.scale(self.mapa_fondo, (canvas.w, canvas.h))
            self.pantalla.blit(fondo, canvas.topleft)
        else:
            self.pantalla.blit(self.fuente_bold.render("Sin mapa de fondo", True, COLOR_TEXTO_DIM), (canvas.x + 20, canvas.y + 20))

        # grilla
        if self.mostrar_grilla:
            for x in range(canvas.x, canvas.right, self.grid_size):
                pygame.draw.line(self.pantalla, COLOR_GRILLA, (x, canvas.y), (x, canvas.bottom), 1)
            for y in range(canvas.y, canvas.bottom, self.grid_size):
                pygame.draw.line(self.pantalla, COLOR_GRILLA, (canvas.x, y), (canvas.right, y), 1)

        def dibujar_pieza(idx, pieza):
            surf = pieza.get_surface()
            rect = surf.get_rect(topleft=(canvas.x + pieza.x, canvas.y + pieza.y))
            self.pantalla.blit(surf, rect.topleft)
            if idx in self.sel_multiple:
                color = COLOR_SELECCION_FONDO if pieza.en_fondo else COLOR_SELECCION
            else:
                color = COLOR_BORDE
            pygame.draw.rect(self.pantalla, color, rect, 2)
            if pieza.bloquea_jugador:
                overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                overlay.fill((180, 60, 60, 45))
                self.pantalla.blit(overlay, rect.topleft)
            if pieza.sobrepuesto:
                inner = rect.inflate(-6, -6)
                if inner.w > 2 and inner.h > 2:
                    pygame.draw.rect(self.pantalla, COLOR_SOBREPUESTO, inner, 2)

        # piezas base (no sobrepuestas)
        for idx, pieza in enumerate(self.piezas):
            if not pieza.visible or pieza.sobrepuesto:
                continue
            dibujar_pieza(idx, pieza)

        # demo jugador
        if self.demo_activa:
            r = self.demo_jugador_rect.move(canvas.x, canvas.y)
            if self.demo_jugador_surface is not None:
                self.pantalla.blit(self.demo_jugador_surface, r.topleft)
            else:
                pygame.draw.rect(self.pantalla, COLOR_DEMO, r)
                pygame.draw.rect(self.pantalla, (15, 20, 30), r, 2)
            txt_demo = self.fuente_bold.render("DEMO", True, COLOR_DEMO)
            self.pantalla.blit(txt_demo, (canvas.x + 8, canvas.y + 8))

        # piezas sobrepuestas (se dibujan encima para probar pasar detras)
        for idx, pieza in enumerate(self.piezas):
            if not pieza.visible or not pieza.sobrepuesto:
                continue
            dibujar_pieza(idx, pieza)

        if len(self.sel_multiple) == 1:
            idx_activo = self.sel_multiple[0]
            if 0 <= idx_activo < len(self.piezas):
                pieza = self.piezas[idx_activo]
                surf = pieza.get_surface()
                rect = surf.get_rect(topleft=(canvas.x + pieza.x, canvas.y + pieza.y))
                payload = {"tipo": "pieza", "idx": idx_activo}
                self.resize_handles = self._tiradores_para_rect(rect, payload)
                for _, hrect, _ in self.resize_handles:
                    pygame.draw.rect(self.pantalla, COLOR_TIRADOR, hrect)
                    pygame.draw.rect(self.pantalla, (20, 20, 20), hrect, 1)
        elif len(self.sel_multiple) > 1:
            rect_grupo = self._rect_seleccion_canvas()
            if rect_grupo:
                rect = rect_grupo.move(canvas.x, canvas.y)
                color_grupo = COLOR_SELECCION
                if all(self.piezas[idx].en_fondo for idx in self.sel_multiple if 0 <= idx < len(self.piezas)):
                    color_grupo = COLOR_SELECCION_FONDO
                pygame.draw.rect(self.pantalla, color_grupo, rect, 2)
                payload = {"tipo": "grupo", "indices": list(self.sel_multiple)}
                self.resize_handles = self._tiradores_para_rect(rect, payload)
                for _, hrect, _ in self.resize_handles:
                    pygame.draw.rect(self.pantalla, COLOR_TIRADOR, hrect)
                    pygame.draw.rect(self.pantalla, (20, 20, 20), hrect, 1)

        pygame.draw.rect(self.pantalla, COLOR_BORDE, canvas, 2, border_radius=10)

    def manejar_eventos(self):
        canvas = pygame.Rect(240, self.barra_superior_h + 10, self.pantalla.get_width() - 510, self.pantalla.get_height() - self.barra_superior_h - 20)
        panel_izq = pygame.Rect(10, self.barra_superior_h + 10, 220, self.pantalla.get_height() - self.barra_superior_h - 20)
        panel_der = pygame.Rect(self.pantalla.get_width() - 260, self.barra_superior_h + 10, 250, self.pantalla.get_height() - self.barra_superior_h - 20)
        barra = self._rect_barra_superior()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if panel_izq.collidepoint(mx, my):
                    self.scroll_lista = max(0, min(self._max_scroll_lista(), self.scroll_lista - event.y * 22))
                elif panel_der.collidepoint(mx, my):
                    self.scroll_panel = max(0, min(self._max_scroll_panel(), self.scroll_panel - event.y * 22))
                elif canvas.collidepoint(mx, my):
                    self._escalar_seleccion(event.y)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                mx, my = event.pos

                if event.button == 1 and barra.collidepoint(mx, my):
                    btn_min = pygame.Rect(barra.right - 100, 5, 26, 24)
                    btn_full = pygame.Rect(barra.right - 68, 5, 26, 24)
                    btn_cerrar = pygame.Rect(barra.right - 36, 5, 26, 24)
                    if btn_cerrar.collidepoint(mx, my):
                        return False
                    if btn_full.collidepoint(mx, my):
                        self._alternar_fullscreen()
                        return True
                    if btn_min.collidepoint(mx, my):
                        pygame.display.iconify()
                        return True

                if event.button == 1 and panel_izq.collidepoint(mx, my):
                    boton_carpeta = pygame.Rect(panel_izq.x + 10, panel_izq.y + 38, panel_izq.w - 20, 28)
                    boton_fondo = pygame.Rect(panel_izq.x + 10, panel_izq.y + 72, panel_izq.w - 20, 28)
                    if boton_carpeta.collidepoint(mx, my):
                        carpeta = self._elegir_carpeta("Elige una carpeta de recursos")
                        if carpeta:
                            self.carpetas_recursos.append(carpeta)
                            self._cargar_carpetas()
                            self._cargar_recursos()
                            self._set_mensaje(f"Carpeta agregada: {carpeta.name}")
                        continue
                    if boton_fondo.collidepoint(mx, my):
                        archivo = self._elegir_archivo_imagen("Elige el mapa de fondo")
                        if archivo:
                            self._cargar_mapa_fondo(archivo)
                        continue

                    for rect, rec in self.recurso_hitboxes:
                        if rect.collidepoint(mx, my):
                            self.recurso_seleccionado = rec
                            self._actualizar_preview_recurso()
                            self._aplicar_modo("agregar")
                            self._set_mensaje(f"Seleccionado: {rec['nombre']}")
                            break
                    continue

                if event.button == 1 and panel_der.collidepoint(mx, my):
                    y = panel_der.y + 40 - self.scroll_panel
                    caja_nombre = pygame.Rect(panel_der.x + 12, y + 20, panel_der.w - 24, 28)
                    if caja_nombre.collidepoint(mx, my):
                        self.input_activo = "nombre"
                        continue

                    botones = {
                        "mover": pygame.Rect(panel_der.x + 12, y + 62, 100, 28),
                        "rotar": pygame.Rect(panel_der.x + 124, y + 62, 100, 28),
                        "espejo": pygame.Rect(panel_der.x + 12, y + 98, 100, 28),
                        "borrar": pygame.Rect(panel_der.x + 124, y + 98, 100, 28),
                    }
                    if botones["mover"].collidepoint(mx, my):
                        self._aplicar_modo("mover" if not self.modo_mover else "ninguno")
                        continue
                    if botones["rotar"].collidepoint(mx, my):
                        self._aplicar_modo("rotar" if not self.modo_rotar else "ninguno")
                        continue
                    if botones["espejo"].collidepoint(mx, my):
                        self._aplicar_modo("espejo" if not self.modo_espejo else "ninguno")
                        continue
                    if botones["borrar"].collidepoint(mx, my):
                        self._aplicar_modo("borrar" if not self.modo_borrar else "ninguno")
                        continue

                    extras = {
                        "snap": pygame.Rect(panel_der.x + 12, y + 140, panel_der.w - 24, 28),
                        "grid": pygame.Rect(panel_der.x + 12, y + 174, panel_der.w - 24, 28),
                        "modo_agregar": pygame.Rect(panel_der.x + 12, y + 208, panel_der.w - 24, 28),
                        "pegar_sel": pygame.Rect(panel_der.x + 12, y + 242, panel_der.w - 24, 28),
                        "despegar_sel": pygame.Rect(panel_der.x + 12, y + 276, panel_der.w - 24, 28),
                        "colision": pygame.Rect(panel_der.x + 12, y + 310, panel_der.w - 24, 28),
                        "sobrepuesto": pygame.Rect(panel_der.x + 12, y + 344, panel_der.w - 24, 28),
                        "pegar": pygame.Rect(panel_der.x + 12, y + 378, panel_der.w - 24, 28),
                        "cargar_prefab": pygame.Rect(panel_der.x + 12, y + 412, panel_der.w - 24, 28),
                        "guardar": pygame.Rect(panel_der.x + 12, y + 446, panel_der.w - 24, 28),
                        "demo": pygame.Rect(panel_der.x + 12, y + 480, panel_der.w - 24, 28),
                    }
                    if extras["snap"].collidepoint(mx, my):
                        self.snap_to_grid = not self.snap_to_grid
                        continue
                    if extras["grid"].collidepoint(mx, my):
                        self.mostrar_grilla = not self.mostrar_grilla
                        continue
                    if extras["modo_agregar"].collidepoint(mx, my):
                        if self.recurso_seleccionado:
                            self._aplicar_modo("agregar")
                        continue
                    if extras["pegar_sel"].collidepoint(mx, my):
                        self._pegar_seleccion()
                        continue
                    if extras["despegar_sel"].collidepoint(mx, my):
                        self._despegar_seleccion()
                        continue
                    if extras["colision"].collidepoint(mx, my):
                        self._alternar_colision_seleccion()
                        continue
                    if extras["sobrepuesto"].collidepoint(mx, my):
                        self._alternar_sobrepuesto_seleccion()
                        continue
                    if extras["pegar"].collidepoint(mx, my):
                        if self.portapapeles_piezas:
                            self._aplicar_modo("pegar")
                            self._set_mensaje("Haz click en el lienzo para pegar")
                        else:
                            self._set_mensaje("Copia piezas primero (Ctrl+C)")
                        continue
                    if extras["cargar_prefab"].collidepoint(mx, my):
                        archivo_json = self._elegir_archivo_json("Elige prefab JSON")
                        if archivo_json:
                            self._cargar_prefab_desde_json(archivo_json)
                        continue
                    if extras["guardar"].collidepoint(mx, my):
                        self._guardar_prefab()
                        continue
                    if extras["demo"].collidepoint(mx, my):
                        self._alternar_demo(canvas)
                        continue

                if canvas.collidepoint(mx, my):
                    mods = pygame.key.get_mods()
                    ctrl_presionado = bool(mods & pygame.KMOD_CTRL)
                    pos_canvas = (mx - canvas.x, my - canvas.y)
                    idx = self._buscar_pieza_por_pos(pos_canvas)

                    if event.button == 1:
                        click_en_tirador = False
                        for handle, hrect, payload in self.resize_handles:
                            if hrect.collidepoint(mx, my):
                                if payload.get("tipo") == "pieza":
                                    idx_h = payload.get("idx")
                                    if idx_h is not None:
                                        self.sel_multiple = [idx_h]
                                        self.pieza_activa_idx = idx_h
                                self._iniciar_redimension(payload, handle, pos_canvas)
                                click_en_tirador = True
                                break
                        if self.redimensionando:
                            continue
                        if click_en_tirador:
                            continue

                        if idx is not None:
                            if ctrl_presionado:
                                if idx in self.sel_multiple:
                                    self.sel_multiple.remove(idx)
                                else:
                                    self.sel_multiple.append(idx)
                                self.pieza_activa_idx = idx if idx in self.sel_multiple else (self.sel_multiple[0] if self.sel_multiple else None)
                                self.arrastrando = False
                                continue

                            grupo = self.piezas[idx].grupo_id
                            if grupo is not None:
                                self.sel_multiple = [i for i, p in enumerate(self.piezas) if p.grupo_id == grupo]
                            elif idx not in self.sel_multiple:
                                self.sel_multiple = [idx]

                            self.pieza_activa_idx = idx
                            if self.modo_mover or not any([self.modo_agregar, self.modo_rotar, self.modo_espejo, self.modo_borrar, self.modo_pegar]):
                                pieza = self.piezas[idx]
                                self.arrastrando = True
                                self.offset_arrastre = (pos_canvas[0] - pieza.x, pos_canvas[1] - pieza.y)
                        else:
                            if not ctrl_presionado:
                                self.sel_multiple = []
                                self.pieza_activa_idx = None
                            self.arrastrando = False
                        continue

                    if event.button == 3:
                        if self.modo_borrar and idx is not None:
                            self.piezas.pop(idx)
                            self.sel_multiple = []
                            self._set_mensaje("Pieza eliminada")
                            continue

                        if self.modo_rotar and idx is not None:
                            self.piezas[idx].rotacion = (self.piezas[idx].rotacion + 90) % 360
                            self._set_mensaje("Pieza rotada")
                            continue

                        if self.modo_espejo and idx is not None:
                            pieza = self.piezas[idx]
                            pieza.flip_x = not pieza.flip_x
                            self._set_mensaje("Espejo aplicado")
                            continue

                        if self.recurso_seleccionado and self.modo_agregar:
                            self._cargar_pieza_desde_recurso(self.recurso_seleccionado, pos_canvas[0], pos_canvas[1])
                            self._aplicar_modo("agregar")
                            continue

                        if self.modo_pegar and self.portapapeles_piezas:
                            self._pegar_portapapeles_en(pos_canvas[0], pos_canvas[1])
                            self._aplicar_modo("mover")
                            continue

                        if idx is not None and self.modo_mover:
                            grupo = self.piezas[idx].grupo_id
                            if grupo is not None:
                                self.sel_multiple = [i for i, p in enumerate(self.piezas) if p.grupo_id == grupo]
                            else:
                                self.sel_multiple = [idx]
                            self.pieza_activa_idx = idx
                            pieza = self.piezas[idx]
                            self.arrastrando = True
                            self.offset_arrastre = (pos_canvas[0] - pieza.x, pos_canvas[1] - pieza.y)
                            continue

            if event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
                self.arrastrando = False
                self.redimensionando = False
                self.redimension_info = None

            if event.type == pygame.MOUSEMOTION and self.redimensionando:
                pos_canvas = (event.pos[0] - canvas.x, event.pos[1] - canvas.y)
                self._actualizar_redimension(pos_canvas)
                continue

            if event.type == pygame.MOUSEMOTION and self.arrastrando and self.sel_multiple:
                pos_canvas = (event.pos[0] - canvas.x, event.pos[1] - canvas.y)
                idx_base = self.pieza_activa_idx if self.pieza_activa_idx in self.sel_multiple else self.sel_multiple[0]
                pieza = self.piezas[idx_base]
                nuevo_x = pos_canvas[0] - self.offset_arrastre[0]
                nuevo_y = pos_canvas[1] - self.offset_arrastre[1]
                if self.snap_to_grid:
                    nuevo_x = self._snap(nuevo_x)
                    nuevo_y = self._snap(nuevo_y)
                dx = nuevo_x - pieza.x
                dy = nuevo_y - pieza.y
                self._mover_piezas_seleccionadas(dx, dy)

            if event.type == pygame.KEYDOWN:
                if self.input_activo == "nombre":
                    if event.key == pygame.K_BACKSPACE:
                        self.input_nombre_prefab = self.input_nombre_prefab[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.input_activo = None
                    elif event.unicode.isprintable():
                        self.input_nombre_prefab += event.unicode
                else:
                    mods = pygame.key.get_mods()
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        self._alternar_profundidad_seleccion()
                        continue
                    if event.key == pygame.K_c and (mods & pygame.KMOD_CTRL):
                        self._copiar_seleccion()
                        continue
                    if event.key == pygame.K_v and (mods & pygame.KMOD_CTRL):
                        self._pegar_portapapeles_con_offset()
                        self._aplicar_modo("mover")
                        continue
                    if event.key == pygame.K_b:
                        self._alternar_colision_seleccion()
                        continue
                    if event.key == pygame.K_TAB:
                        self._alternar_sobrepuesto_seleccion()
                        continue
                    if event.key == pygame.K_F5:
                        self._alternar_demo(canvas)
                        continue
                    if event.key == pygame.K_DELETE and self.sel_multiple:
                        for idx in sorted(self.sel_multiple, reverse=True):
                            self.piezas.pop(idx)
                        self.sel_multiple = []
                    elif event.key == pygame.K_r and self.sel_multiple:
                        for idx in self.sel_multiple:
                            self.piezas[idx].rotacion = (self.piezas[idx].rotacion + 90) % 360
                    elif event.key == pygame.K_x and self.sel_multiple:
                        for idx in self.sel_multiple:
                            pieza = self.piezas[idx]
                            pieza.flip_x = not pieza.flip_x
                    elif event.key == pygame.K_g:
                        self.mostrar_grilla = not self.mostrar_grilla
                    elif event.key == pygame.K_s:
                        self.snap_to_grid = not self.snap_to_grid
                    elif event.key == pygame.K_l:
                        archivo_json = self._elegir_archivo_json("Elige prefab JSON")
                        if archivo_json:
                            self._cargar_prefab_desde_json(archivo_json)

        return True

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        self._cargar_carpetas()
        self._cargar_recursos()
        self.scroll_lista = max(0, min(self.scroll_lista, self._max_scroll_lista()))
        self.scroll_panel = max(0, min(self.scroll_panel, self._max_scroll_panel()))
        self._dibujar_barra_superior()
        self._dibujar_panel_izquierdo()
        self._dibujar_canvas()
        self._dibujar_panel_derecho()
        pygame.display.flip()

    def ejecutar(self):
        while self.running:
            self.running = self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    ConstructorPrefabs().ejecutar()
