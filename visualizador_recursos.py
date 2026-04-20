import pygame
import os
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 1280, 720
FPS = 60

# Colores
COLOR_FONDO = (20, 20, 30)
COLOR_PANEL = (35, 35, 50)
COLOR_TEXTO = (240, 240, 240)
COLOR_TEXTO_DIM = (150, 150, 150)
COLOR_BOTON = (55, 55, 80)
COLOR_BOTON_HOVER = (75, 75, 105)
COLOR_BOTON_ACTIVO = (90, 90, 255)
COLOR_SELECCION = (255, 215, 0)
COLOR_USADO = (80, 80, 80)
COLOR_PLANTILLA = (0, 200, 255)

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_BUSQUEDA_EXTRA = os.environ.get("VISUALIZADOR_RECURSOS_EXTRA", "").strip()
RUTAS_BUSQUEDA = [BASE_DIR]
if RUTA_BUSQUEDA_EXTRA:
    RUTAS_BUSQUEDA.append(RUTA_BUSQUEDA_EXTRA)

class FrameData:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.usado = False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Fragmento:
    def __init__(self, rect_original, pos_virtual):
        self.rect_original = rect_original # Rect en la imagen real
        self.pos_virtual = pos_virtual     # (vx, vy) donde se dibuja en el canvas virtual

class EditorMaestroSprites:
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = ANCHO, ALTO
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto), pygame.RESIZABLE)
        pygame.display.set_caption("EDITOR MAESTRO DE SPRITES - WORKFLOW ORIGINAL")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente_ui = pygame.font.SysFont("Arial", 14)
        self.fuente_bold = pygame.font.SysFont("Arial", 16, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Estado Recursos
        self.categorias = ["HEROES", "ENEMIGOS", "NPCs", "OBJETOS", "MUNDO", "UI / FX", "OTROS"]
        self.cat_activa = "HEROES"
        self.lista_recursos = []
        self.recurso_seleccionado = None
        self.img_sheet = None
        self.barra_carpetas = []
        self.barra_folder_activa = None
        self.scroll_barra_x = 0
        
        # Carpetas de Destino (assets y subcarpetas)
        self.path_assets = Path(BASE_DIR) / "assets"
        self.path_config_ui = Path(BASE_DIR) / "visualizador_recursos_ui.json"
        self.ruta_guardado_actual = self.path_assets
        self.carpetas_destino = []
        self.idx_carpeta_destino = 0
        self.carpeta_hovered = False
        self.scroll_panel_derecho = 0
        self.max_scroll_panel_derecho = 0
        self._actualizar_carpetas_destino()
        self._cargar_preferencias_ui()
        self._actualizar_barra_carpetas()
        
        # Plantilla
        self.template_rect = None  # [x, y, w, h]
        self.dibujando_template = False
        self.resizing_handle_plantilla = None
        
        # Grid
        self.frames_grid = []
        self.seleccionados = []
        self.caja_seleccionando = False
        self.caja_inicio = (0, 0)
        self.caja_fin = (0, 0)
        
        # Editor State
        self.resizing_frame_idx = None
        self.resizing_frame_dir = None
        self.creando_frame = False
        self.frame_creando_rect = None
        self.arrastrando_grupo = False
        self.grupo_drag_offset = []
        self.grupo_drag_offset_idx = None
        
        # Zoom y Pan
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging_canvas = False
        self.last_mouse_pos = (0, 0)
        
        # Sistema de Fragmentos (Corte Virtual)
        self.fragmentos = [] # Lista de objetos Fragmento
        self.seleccionando_corte = False
        self.rect_seleccion_corte = None # [ix, iy, iw, ih]
        
        self.input_personaje = ""
        self.opciones_accion = [
            {"label": "Caminar arriba", "valor": "caminar_arriba"},
            {"label": "Caminar abajo", "valor": "caminar_abajo"},
            {"label": "Caminar izq.", "valor": "caminar_izquierda"},
            {"label": "Caminar der.", "valor": "caminar_derecha"},
            {"label": "Atacar", "valor": "atacar"},
            {"label": "Defenderse", "valor": "defenderse"},
            {"label": "Custom", "valor": "custom"},
        ]
        self.indice_accion = None
        self.input_accion = ""
        self.input_activo = None
        
        # Nuevos estados: Filtro de Carpetas y Modos
        self.modo_corte = "GLOBAL"
        self.fragmento_activo_plantilla = -1
        self.carpeta_externa = None
        
        # UI
        self.scroll_lista = 0
        self.rect_lista = pygame.Rect(10, 80, 250, 600)
        self.rect_canvas = pygame.Rect(270, 80, 750, 600)
        self.rect_panel = pygame.Rect(1030, 80, 240, 600)
        
        self._escanear_recursos()
        self.actualizar_lista_categoria()
        
        # === ATLAS PACKER ===
        self.atlas_padding = 2  # píxeles entre sprites en el atlas

        # === ANIMATION PREVIEWER ===
        self.anim_playing    = False
        self.anim_fps        = 8          # frames por segundo
        self.anim_frame_idx  = 0          # índice actual dentro de self.seleccionados
        self.anim_last_tick  = 0          # tiempo del último avance de frame

        # === GRID OVERLAY ===
        self.grid_visible    = False
        self.grid_cell_w     = 32
        self.grid_cell_h     = 32
        self.input_grid_w    = ""
        self.input_grid_h    = ""
        self.input_activo_grid = None     # "grid_w" | "grid_h"

        self.mensaje_ui = ""
        self.mensaje_tick = 0

        self.reordenar_ui()

    def reordenar_ui(self):
        w, h = self.pantalla.get_size()
        if w < 100 or h < 100: return
        self.ancho, self.alto = w, h
        self.rect_barra = pygame.Rect(10, 10, w - 20, 40)
        panel_y = self.rect_barra.bottom + 10
        panel_h = h - panel_y - 20
        
        self.rect_lista = pygame.Rect(10, panel_y, 250, panel_h)
        self.rect_panel = pygame.Rect(w - 250, panel_y, 240, panel_h)
        self.rect_canvas = pygame.Rect(270, panel_y, w - 270 - 260, panel_h)

    def _ruta_relativa_assets(self, ruta):
        try:
            return Path(ruta).resolve().relative_to(self.path_assets.resolve())
        except Exception:
            return None

    def _texto_ruta_assets(self, ruta):
        rel = self._ruta_relativa_assets(ruta)
        if rel is None:
            return str(ruta)
        texto = rel.as_posix()
        return texto if texto else "<assets>"

    def _elegir_carpeta_assets(self, titulo):
        root = tk.Tk()
        root.withdraw()
        carpeta = filedialog.askdirectory(title=titulo, initialdir=str(self.path_assets), mustexist=True)
        root.destroy()
        if not carpeta:
            return None
        ruta = Path(carpeta)
        if self._ruta_relativa_assets(ruta) is None:
            self._set_mensaje("⚠️ ELIGE UNA CARPETA DENTRO DE ASSETS")
            return None
        return ruta

    def _actualizar_barra_carpetas(self):
        if not self.path_assets.exists():
            self.path_assets.mkdir(parents=True, exist_ok=True)

        carpetas = []
        for item in self.barra_carpetas:
            ruta = Path(item["path"])
            if self._ruta_relativa_assets(ruta) is None:
                continue
            if not ruta.is_dir():
                continue
            carpetas.append({"nombre": item.get("nombre", ruta.name), "path": ruta})
        self.barra_carpetas = carpetas

        if self.barra_folder_activa is not None:
            actuales = [str(item["path"]) for item in self.barra_carpetas]
            if str(self.barra_folder_activa) not in actuales:
                self.barra_folder_activa = None

        if self.barra_folder_activa is None and self.barra_carpetas:
            self.barra_folder_activa = self.barra_carpetas[0]["path"]

    def _guardar_preferencias_ui(self):
        data = {
            "barra_carpetas": [],
            "barra_folder_activa": None,
            "ruta_guardado_actual": None,
        }

        for item in self.barra_carpetas:
            rel = self._ruta_relativa_assets(item["path"])
            if rel is not None:
                data["barra_carpetas"].append(rel.as_posix())

        rel_activa = self._ruta_relativa_assets(self.barra_folder_activa) if self.barra_folder_activa else None
        if rel_activa is not None:
            data["barra_folder_activa"] = rel_activa.as_posix()

        rel_guardado = self._ruta_relativa_assets(self.ruta_guardado_actual) if self.ruta_guardado_actual else None
        if rel_guardado is not None:
            data["ruta_guardado_actual"] = rel_guardado.as_posix()
        else:
            data["ruta_guardado_actual"] = ""

        try:
            with open(self.path_config_ui, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _cargar_preferencias_ui(self):
        if not self.path_config_ui.exists():
            return

        try:
            with open(self.path_config_ui, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        carpetas_guardadas = data.get("barra_carpetas", [])
        self.barra_carpetas = []
        for rel in carpetas_guardadas:
            ruta = (self.path_assets / rel).resolve() if rel else self.path_assets.resolve()
            if self._ruta_relativa_assets(ruta) is None:
                continue
            if not ruta.is_dir():
                continue
            self.barra_carpetas.append({"nombre": ruta.name, "path": ruta})

        activa = data.get("barra_folder_activa")
        if isinstance(activa, str):
            ruta_activa = (self.path_assets / activa).resolve() if activa else self.path_assets.resolve()
            self.barra_folder_activa = ruta_activa if ruta_activa.is_dir() else None

        guardado = data.get("ruta_guardado_actual")
        if isinstance(guardado, str):
            ruta_guardado = (self.path_assets / guardado).resolve() if guardado else self.path_assets.resolve()
            if ruta_guardado.is_dir() and self._ruta_relativa_assets(ruta_guardado) is not None:
                self.ruta_guardado_actual = ruta_guardado

    def _agregar_carpeta_barra(self, ruta):
        ruta = Path(ruta)
        if self._ruta_relativa_assets(ruta) is None:
            return
        if not ruta.is_dir():
            return

        if not any(item["path"] == ruta for item in self.barra_carpetas):
            self.barra_carpetas.append({"nombre": ruta.name, "path": ruta})
        self.barra_folder_activa = ruta
        self.carpeta_externa = str(ruta)
        self.actualizar_lista_categoria()
        self._guardar_preferencias_ui()

    def _quitar_carpeta_barra(self, ruta):
        ruta = Path(ruta)
        self.barra_carpetas = [item for item in self.barra_carpetas if item["path"] != ruta]
        if self.barra_folder_activa == ruta:
            self.barra_folder_activa = self.barra_carpetas[0]["path"] if self.barra_carpetas else None
        if self.carpeta_externa and Path(self.carpeta_externa) == ruta:
            self.carpeta_externa = str(self.barra_folder_activa) if self.barra_folder_activa else None
            self.actualizar_lista_categoria()
        if self.ruta_guardado_actual == ruta:
            self.ruta_guardado_actual = self.path_assets
            self._actualizar_carpetas_destino()
        self._guardar_preferencias_ui()

    def _selector_guardado_actual(self):
        rel = self._ruta_relativa_assets(self.ruta_guardado_actual)
        return rel.as_posix() if rel else "<assets>"

    def _escanear_recursos(self):
        self.base_datos = {}
        extensiones = ('.png', '.jpg', '.jpeg')
        for ruta_base in RUTAS_BUSQUEDA:
            if not os.path.exists(ruta_base): continue
            for root, dirs, files in os.walk(ruta_base):
                if any(x in root.lower() for x in ['.git', '__pycache__', 'node_modules']): continue
                
                img_files = [f for f in files if f.lower().endswith(extensiones)]
                if not img_files: continue
                
                root_lower = root.lower()
                cat_target = "OTROS"
                
                if any(x in root_lower for x in ['hero', 'personaje', 'avatar', 'char', 'player', 'prota']): 
                    cat_target = "HEROES"
                elif any(x in root_lower for x in ['monst', 'enemy', 'boss', 'enemigo', 'creature']): 
                    cat_target = "ENEMIGOS"
                elif any(x in root_lower for x in ['npc', 'town', 'civil', 'aldeano']): 
                    cat_target = "NPCs"
                elif any(x in root_lower for x in ['item', 'object', 'chest', 'weapon', 'prop', 'objeto']): 
                    cat_target = "OBJETOS"
                elif any(x in root_lower for x in ['tile', 'map', 'world', 'bg', 'background', 'fondo']): 
                    cat_target = "MUNDO"
                elif any(x in root_lower for x in ['ui', 'fx', 'effect', 'icon', 'menu', 'partic']): 
                    cat_target = "UI / FX"

                if cat_target not in self.base_datos:
                    self.base_datos[cat_target] = []
                    
                for f in img_files:
                    # Mostrar la carpeta contenedora para saber distinguir entre ej: 100AVATARS_001 y 100AVATARS_002
                    carpeta_padre = os.path.basename(root)
                    nombre_mostrar = f if carpeta_padre == "" else f"{carpeta_padre}/{f}"
                    self.base_datos[cat_target].append({"nombre": nombre_mostrar, "path": os.path.join(root, f)})
                    
        # Ordenar las categorías, forzando un orden lógico si es posible
        orden_deseado = ["HEROES", "ENEMIGOS", "NPCs", "OBJETOS", "MUNDO", "UI / FX", "OTROS"]
        self.categorias = [c for c in orden_deseado if c in self.base_datos]
        # Añadir cualquier categoría extra que no esté en la lista deseada por si acaso
        for c in sorted(self.base_datos.keys()):
            if c not in self.categorias:
                self.categorias.append(c)
                
        if not self.categorias:
            self.categorias = ["VACÍO"]
            self.base_datos["VACÍO"] = []
        
        if not hasattr(self, 'cat_activa') or self.cat_activa not in self.categorias:
            self.cat_activa = self.categorias[0]

    def actualizar_lista_categoria(self):
        ruta_uso = None
        if self.barra_folder_activa and Path(self.barra_folder_activa).exists():
            ruta_uso = Path(self.barra_folder_activa)
        elif self.carpeta_externa and os.path.exists(self.carpeta_externa):
            ruta_uso = Path(self.carpeta_externa)

        if ruta_uso and ruta_uso.exists():
            self.lista_recursos = []
            extensiones = ('.png', '.jpg', '.jpeg')
            for root, dirs, files in os.walk(ruta_uso):
                if any(x in root.lower() for x in ['.git', '__pycache__', 'node_modules']):
                    continue
                for f in files:
                    if f.lower().endswith(extensiones):
                        carpeta_padre = os.path.basename(root)
                        nombre_mostrar = f if carpeta_padre == "" else f"{carpeta_padre}/{f}"
                        self.lista_recursos.append({"nombre": nombre_mostrar, "path": os.path.join(root, f)})
        else:
            self.lista_recursos = self.base_datos.get(self.cat_activa, [])
        self.scroll_lista = 0
        self.recurso_seleccionado = None

    def _actualizar_carpetas_destino(self):
        if not self.path_assets.exists(): self.path_assets.mkdir(parents=True, exist_ok=True)
        carpetas = ["<assets>"]
        for ruta in self.path_assets.rglob("*"):
            if ruta.is_dir():
                carpetas.append(ruta.relative_to(self.path_assets).as_posix())
        self.carpetas_destino = carpetas
        actual_rel = self._ruta_relativa_assets(self.ruta_guardado_actual)
        if actual_rel and actual_rel.as_posix() in self.carpetas_destino:
            self.idx_carpeta_destino = self.carpetas_destino.index(actual_rel.as_posix())
        else:
            self.idx_carpeta_destino = 0

    def _ruta_destino_actual(self):
        return self.ruta_guardado_actual if self.ruta_guardado_actual else self.path_assets

    def _nombre_limpio(self, texto):
        texto = texto.strip()
        if not texto:
            return ""
        limpio = []
        for caracter in texto:
            if caracter.isalnum() or caracter in ("-", "_"):
                limpio.append(caracter)
            else:
                limpio.append("_")
        resultado = "".join(limpio)
        while "__" in resultado:
            resultado = resultado.replace("__", "_")
        return resultado.strip("_")

    def _accion_actual(self):
        if self.indice_accion is None:
            return ""
        valor = self.opciones_accion[self.indice_accion]["valor"]
        if valor == "custom":
            return self.input_accion.strip()
        return valor

    def _rects_acciones(self, px, py):
        rects = []
        cols = 2
        btn_w = 105
        btn_h = 24
        gap_x = 10
        gap_y = 6
        for indice, opcion in enumerate(self.opciones_accion):
            col = indice % cols
            fila = indice // cols
            x = px + col * (btn_w + gap_x)
            y = py + fila * (btn_h + gap_y)
            rects.append((pygame.Rect(x, y, btn_w, btn_h), indice))
        filas = (len(self.opciones_accion) + cols - 1) // cols
        alto_total = filas * btn_h + max(0, filas - 1) * gap_y
        return rects, py + alto_total

    def cargar_sheet(self, recurso):
        self.recurso_seleccionado = recurso
        self.img_sheet = pygame.image.load(recurso["path"]).convert_alpha()
        self.template_rect = None
        self.frames_grid = []
        self.seleccionados = []
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.fragmentos = [Fragmento(self.img_sheet.get_rect(), (0, 0))]
        print(f"[OK] Cargado: {recurso['nombre']}")

    def _get_canvas_coords(self, mx, my):
        """Convierte coordenadas de pantalla a coordenadas del canvas VIRTUAL (con zoom y pan)"""
        vx = (mx - self.rect_canvas.x - self.pan_x) / self.zoom
        vy = (my - self.rect_canvas.y - self.pan_y) / self.zoom
        return vx, vy

    def _get_image_coords(self, vx, vy):
        """Convierte coordenadas VIRTUALES a coordenadas reales de la IMAGEN basándose en los fragmentos"""
        for f in self.fragmentos:
            rect_v = pygame.Rect(f.pos_virtual[0], f.pos_virtual[1], f.rect_original.w, f.rect_original.h)
            if rect_v.collidepoint(vx, vy):
                ix = f.rect_original.x + (vx - f.pos_virtual[0])
                iy = f.rect_original.y + (vy - f.pos_virtual[1])
                return ix, iy
        return None, None

    def _get_screen_coords(self, vx, vy):
        """Convierte coordenadas VIRTUALES a coordenadas de pantalla"""
        sx = vx * self.zoom + self.rect_canvas.x + self.pan_x
        sy = vy * self.zoom + self.rect_canvas.y + self.pan_y
        return sx, sy

    def _generar_grid_completo(self):
        if not self.img_sheet or not self.template_rect: return
        # La plantilla está en coordenadas VIRTUALES
        tx, ty, tw, th = int(self.template_rect[0]), int(self.template_rect[1]), int(abs(self.template_rect[2])), int(abs(self.template_rect[3]))
        if tw < 4 or th < 4: return
        
        nuevos_frames = []
        frames_existentes = [pygame.Rect(f.x, f.y, f.w, f.h) for f in self.frames_grid]
        
        # Determinar sobre qué fragmentos operar basándose en el modo
        fragmentos_a_procesar = self.fragmentos
        if self.modo_corte == "AISLADO" and 0 <= self.fragmento_activo_plantilla < len(self.fragmentos):
            fragmentos_a_procesar = [self.fragmentos[self.fragmento_activo_plantilla]]

        # Iterar sobre cada fragmento válido
        for f_layout in fragmentos_a_procesar:
            vx_start, vy_start = f_layout.pos_virtual
            vw, vh = f_layout.rect_original.w, f_layout.rect_original.h
            
            # Generar grid local al fragmento
            for y in range(vy_start, vy_start + vh, th):
                for x in range(vx_start, vx_start + vw, tw):
                    # Ajustar al final del fragmento
                    fw = tw if x + tw <= vx_start + vw else (vx_start + vw) - x
                    fh = th if y + th <= vy_start + vh else (vy_start + vh) - y
                    
                    if fw > 2 and fh > 2:
                        nuevo_rect = pygame.Rect(x, y, fw, fh)
                        # Evitar duplicados
                        if not any(nuevo_rect.colliderect(e) for e in frames_existentes):
                            nuevos_frames.append(FrameData(x, y, fw, fh))
                            
        self.frames_grid.extend(nuevos_frames)
        self.seleccionados = []

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.VIDEORESIZE: self.reordenar_ui()
            mx, my = pygame.mouse.get_pos()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 0. Pan o Corte del canvas (clic derecho)
                if event.button == 3 and self.rect_canvas.collidepoint(mx, my):
                    if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        # Empezar selección de CORTE
                        ix, iy = self._get_canvas_coords(mx, my)
                        self.seleccionando_corte = True
                        self.rect_seleccion_corte = [ix, iy, 0, 0]
                    else:
                        # Pan normal
                        self.dragging_canvas = True
                        self.last_mouse_pos = (mx, my)

                # 1. Barra superior de carpetas
                if self.rect_barra.collidepoint(mx, my):
                    btn_agregar = pygame.Rect(self.rect_barra.x, self.rect_barra.y + 4, 30, 28)
                    if btn_agregar.collidepoint(mx, my):
                        carpeta = self._elegir_carpeta_assets("Elige una carpeta para agregar a la barra")
                        if carpeta:
                            self._agregar_carpeta_barra(carpeta)
                    else:
                        x_cursor = self.rect_barra.x + 40 - self.scroll_barra_x
                        for item in self.barra_carpetas:
                            txt = self.fuente_bold.render(item["nombre"], True, COLOR_TEXTO)
                            br = pygame.Rect(x_cursor, self.rect_barra.y + 4, txt.get_width() + 20, 28)
                            cerrar_rect = pygame.Rect(br.right - 16, br.y + 2, 14, 14)
                            if cerrar_rect.collidepoint(mx, my):
                                self._quitar_carpeta_barra(item["path"])
                                break
                            if br.collidepoint(mx, my):
                                self.barra_folder_activa = item["path"]
                                self.carpeta_externa = str(item["path"])
                                self.actualizar_lista_categoria()
                                self._guardar_preferencias_ui()
                                break
                            x_cursor += br.w + 10
                
                # 2. Lista y Carpeta
                if self.rect_lista.collidepoint(mx, my):
                    btn_carpeta = pygame.Rect(self.rect_lista.x + 10, self.rect_lista.y + 10, self.rect_lista.w - 20, 25)
                    if btn_carpeta.collidepoint(mx, my):
                        if self.carpeta_externa:
                            self.carpeta_externa = None
                            self.actualizar_lista_categoria()
                        else:
                            root = tk.Tk()
                            root.withdraw()
                            carpeta_elegida = filedialog.askdirectory(title="Elige una carpeta con Sprites")
                            root.destroy()
                            if carpeta_elegida:
                                self.carpeta_externa = carpeta_elegida
                                self.actualizar_lista_categoria()
                    else:
                        idx = (my - (self.rect_lista.y + 45) + self.scroll_lista) // 25
                        if 0 <= idx < len(self.lista_recursos): self.cargar_sheet(self.lista_recursos[idx])
                
                # 3. Canvas
                if self.rect_canvas.collidepoint(mx, my) and self.img_sheet:
                    ix, iy = self._get_canvas_coords(mx, my)
                    if not self.frames_grid:
                        if self.template_rect:
                            tx, ty, tw, th = self.template_rect
                            # 8 handles: esquinas + medios
                            handles = {
                                "tl": (tx, ty), "tr": (tx + tw, ty),
                                "bl": (tx, ty + th), "br": (tx + tw, ty + th),
                                "t": (tx + tw // 2, ty), "b": (tx + tw // 2, ty + th),
                                "l": (tx, ty + th // 2), "r": (tx + tw, ty + th // 2)
                            }
                            encontro = False
                            for d, (hx, hy) in handles.items():
                                hx_s, hy_s = self._get_screen_coords(hx, hy)
                                if abs(mx - hx_s) < 15 and abs(my - hy_s) < 15:
                                    self.resizing_handle_plantilla = d
                                    encontro = True
                                    break
                            if not encontro and event.button == 1:
                                self.dibujando_template = True
                                self.template_rect = [ix, iy, 0, 0]
                                self.fragmento_activo_plantilla = next((j for j, frag in enumerate(self.fragmentos) if pygame.Rect(frag.pos_virtual[0], frag.pos_virtual[1], frag.rect_original.w, frag.rect_original.h).collidepoint(ix, iy)), -1)
                        elif event.button == 1:
                            self.dibujando_template = True
                            self.template_rect = [ix, iy, 0, 0]
                            self.fragmento_activo_plantilla = next((j for j, frag in enumerate(self.fragmentos) if pygame.Rect(frag.pos_virtual[0], frag.pos_virtual[1], frag.rect_original.w, frag.rect_original.h).collidepoint(ix, iy)), -1)
                    else:
                        # Resizing de frames del grid
                        encontro_handle = False
                        if self.seleccionados and len(self.seleccionados) == 1:
                            f = self.frames_grid[self.seleccionados[0]]
                            handles = {
                                "tl": (f.x, f.y), "tr": (f.x + f.w, f.y),
                                "bl": (f.x, f.y + f.h), "br": (f.x + f.w, f.y + f.h),
                                "t": (f.x + f.w // 2, f.y), "b": (f.x + f.w // 2, f.y + f.h),
                                "l": (f.x, f.y + f.h // 2), "r": (f.x + f.w, f.y + f.h // 2)
                            }
                            for dir, (hx, hy) in handles.items():
                                hx_s, hy_s = self._get_screen_coords(hx, hy)
                                if abs(mx - hx_s) < 15 and abs(my - hy_s) < 15:
                                    self.resizing_frame_idx = self.seleccionados[0]
                                    self.resizing_frame_dir = dir
                                    encontro_handle = True
                                    break
                        
                        if not encontro_handle and event.button == 1:
                            frame_idx = self._get_frame_por_punto(mx, my)
                            if frame_idx is not None:
                                if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                                    if frame_idx in self.seleccionados: self.seleccionados.remove(frame_idx)
                                    else: self.seleccionados.append(frame_idx)
                                else:
                                    self.seleccionados = [frame_idx]
                            else:
                                self.seleccionados = []
                                self.caja_seleccionando = True
                                self.caja_inicio = (mx, my)
                                self.caja_fin = (mx, my)

                # 4. Panel Derecho (Detección Dinámica)
                if self.rect_panel.collidepoint(mx, my):
                    px, py = self.rect_panel.x + 10, self.rect_panel.y + 148 - self.scroll_panel_derecho
                    
                    # Selector de Carpeta de Destino
                    if pygame.Rect(px, py + 20, 180, 28).collidepoint(mx, my):
                        carpeta = self._elegir_carpeta_assets("Elige la carpeta donde guardar")
                        if carpeta:
                            self.ruta_guardado_actual = carpeta
                            self._actualizar_carpetas_destino()
                            self._guardar_preferencias_ui()
                    
                    # Botón [+]
                    if pygame.Rect(px + 190, py + 20, 30, 28).collidepoint(mx, my):
                        carpeta = self._elegir_carpeta_assets("Elige otra carpeta dentro de assets")
                        if carpeta:
                            self.ruta_guardado_actual = carpeta
                            self._actualizar_carpetas_destino()
                            self._guardar_preferencias_ui()
                    
                    # Input Personaje
                    py += 60
                    if pygame.Rect(px, py + 20, 220, 28).collidepoint(mx, my):
                        self.input_activo = "personaje"
                    
                    # Input Acción
                    py += 60
                    rects_accion, fin_accion = self._rects_acciones(px, py + 20)
                    for rect, indice in rects_accion:
                        if rect.collidepoint(mx, my):
                            self.indice_accion = indice
                            if self.opciones_accion[indice]["valor"] == "custom":
                                self.input_activo = "accion_custom"
                            else:
                                self.input_activo = None
                                self.input_accion = ""
                            break
                    else:
                        if self.indice_accion is not None and self.opciones_accion[self.indice_accion]["valor"] == "custom":
                            rect_custom = pygame.Rect(px, fin_accion + 8, 220, 28)
                            if rect_custom.collidepoint(mx, my):
                                self.input_activo = "accion_custom"
                    
                    # Toggle de Modo de Corte
                    py = fin_accion + 20
                    if self.indice_accion is not None and self.opciones_accion[self.indice_accion]["valor"] == "custom":
                        py = fin_accion + 44
                    if pygame.Rect(px, py, 220, 30).collidepoint(mx, my):
                        self.modo_corte = "AISLADO" if self.modo_corte == "GLOBAL" else "GLOBAL"

                    # -- Botones accion --
                    py += 38 # CORTAR TODO
                    if pygame.Rect(px, py, 220, 36).collidepoint(mx, my):
                        self._generar_grid_completo()

                    py += 44 # AUTO DETECTAR
                    if pygame.Rect(px, py, 220, 36).collidepoint(mx, my):
                        self.auto_detectar_sprites()

                    py += 44 # GUARDAR
                    if pygame.Rect(px, py, 220, 36).collidepoint(mx, my):
                        self._guardar_seleccion()

                    py += 44 # GENERAR ATLAS
                    if pygame.Rect(px, py, 220, 36).collidepoint(mx, my):
                        self.generar_atlas()

                    # -- Animation Previewer --
                    py += 44 # PLAY/STOP
                    if pygame.Rect(px, py, 220, 30).collidepoint(mx, my):
                        self.toggle_animacion()

                    py += 38 # FPS
                    if pygame.Rect(px + 35, py, 68, 26).collidepoint(mx, my):
                        if pygame.Rect(px + 75, py, 30, 26).collidepoint(mx, my):
                            self.anim_fps = min(60, self.anim_fps + 1)
                        elif pygame.Rect(px + 35, py, 40, 26).collidepoint(mx, my):
                            self.anim_fps = max(1, self.anim_fps - 1)

                    # -- Grid Overlay --
                    py += 36 # GRID ON/OFF
                    if pygame.Rect(px, py, 220, 28).collidepoint(mx, my):
                        self.toggle_grid()

                    py += 34 # W/H inputs
                    if pygame.Rect(px + 20, py, 80, 22).collidepoint(mx, my):
                        self.input_activo_grid = "grid_w"
                        self.input_grid_w = str(self.grid_cell_w)
                    if pygame.Rect(px + 135, py, 80, 22).collidepoint(mx, my):
                        self.input_activo_grid = "grid_h"
                        self.input_grid_h = str(self.grid_cell_h)

                    py += 34 # LIMPIAR
                    if pygame.Rect(px, py, 220, 28).collidepoint(mx, my):
                        self.frames_grid = []
                        self.template_rect = None
                        self.seleccionados = []
                else:
                    # Desactivar input si se pulsa fuera del panel
                    if not self.rect_lista.collidepoint(mx, my):
                        self.input_activo = None

            if event.type == pygame.MOUSEMOTION:
                ix, iy = self._get_canvas_coords(mx, my)
                
                # 0. Pan o Corte del canvas
                if self.dragging_canvas:
                    dx = mx - self.last_mouse_pos[0]
                    dy = my - self.last_mouse_pos[1]
                    self.pan_x += dx
                    self.pan_y += dy
                    self.last_mouse_pos = (mx, my)
                elif self.seleccionando_corte:
                    self.rect_seleccion_corte[2] = ix - self.rect_seleccion_corte[0]
                    self.rect_seleccion_corte[3] = iy - self.rect_seleccion_corte[1]

                # Hover dinámico para borrar carpetas (DEL)
                if self.rect_panel.collidepoint(mx, my):
                    px, py = self.rect_panel.x + 10, self.rect_panel.y + 148 - self.scroll_panel_derecho
                    self.carpeta_hovered = pygame.Rect(px, py + 20, 180, 28).collidepoint(mx, my)
                else:
                    self.carpeta_hovered = False
                
                if self.dibujando_template:
                    self.template_rect[2] = ix - self.template_rect[0]
                    self.template_rect[3] = iy - self.template_rect[1]
                elif self.resizing_handle_plantilla:
                    tx, ty, tw, th = self.template_rect
                    dir = self.resizing_handle_plantilla
                    if "r" in dir: tw = ix - tx
                    if "l" in dir: tw = tx + tw - ix; tx = ix
                    if "b" in dir: th = iy - ty
                    if "t" in dir: th = ty + th - iy; ty = iy
                    self.template_rect = [tx, ty, tw, th]
                elif self.resizing_frame_idx is not None and self.resizing_frame_dir:
                    f = self.frames_grid[self.resizing_frame_idx]
                    dir = self.resizing_frame_dir
                    old_x, old_y, old_w, old_h = f.x, f.y, f.w, f.h
                    if "r" in dir: f.w = max(4, ix - f.x)
                    if "l" in dir: 
                        nuevo_w = max(4, old_x + old_w - ix)
                        f.x = ix if nuevo_w > 4 else old_x
                        f.w = nuevo_w
                    if "b" in dir: f.h = max(4, iy - f.y)
                    if "t" in dir:
                        nuevo_h = max(4, old_y + old_h - iy)
                        f.y = iy if nuevo_h > 4 else old_y
                        f.h = nuevo_h
                elif self.caja_seleccionando:
                    self.caja_fin = (mx, my)
                    self._update_caja_seleccion()

            if event.type == pygame.MOUSEBUTTONUP:
                if self.seleccionando_corte:
                    self._aplicar_corte_manual()
                    self.seleccionando_corte = False
                    self.rect_seleccion_corte = None
                
                self.dragging_canvas = False
                self.dibujando_template = False
                self.resizing_handle_plantilla = None
                self.resizing_frame_idx = None
                self.resizing_frame_dir = None
                self.caja_seleccionando = False

            if event.type == pygame.KEYDOWN:
                if self.input_activo == "personaje":
                    if event.key == pygame.K_BACKSPACE: self.input_personaje = self.input_personaje[:-1]
                    elif event.unicode.isprintable(): self.input_personaje += event.unicode
                elif self.input_activo == "accion_custom":
                    if event.key == pygame.K_BACKSPACE: self.input_accion = self.input_accion[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.input_activo = None
                    elif event.unicode.isprintable(): self.input_accion += event.unicode
                elif event.key == pygame.K_a:
                    self.auto_detectar_sprites()
                elif event.key == pygame.K_p:
                    self.toggle_animacion()
                elif event.key == pygame.K_g:
                    self.toggle_grid()
                elif event.key == pygame.K_r:
                    # Resetear cortes manuales
                    if self.img_sheet:
                        self.fragmentos = [Fragmento(self.img_sheet.get_rect(), (0, 0))]
                        self.frames_grid = []
                        self.seleccionados = []
                        print("[OK] Cortes manuales reseteados")
                elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.seleccionados:
                    for i in sorted(self.seleccionados, reverse=True): self.frames_grid.pop(i)
                    self.seleccionados = []
                # Grid size inputs
                elif self.input_activo_grid == "grid_w":
                    if event.key == pygame.K_BACKSPACE:
                        self.input_grid_w = self.input_grid_w[:-1]
                    elif event.key == pygame.K_RETURN:
                        try:
                            self.grid_cell_w = max(1, int(self.input_grid_w))
                        except ValueError:
                            pass
                        self.input_activo_grid = None
                    elif event.unicode.isdigit():
                        self.input_grid_w += event.unicode
                elif self.input_activo_grid == "grid_h":
                    if event.key == pygame.K_BACKSPACE:
                        self.input_grid_h = self.input_grid_h[:-1]
                    elif event.key == pygame.K_RETURN:
                        try:
                            self.grid_cell_h = max(1, int(self.input_grid_h))
                        except ValueError:
                            pass
                        self.input_activo_grid = None
                    elif event.unicode.isdigit():
                        self.input_grid_h += event.unicode

            if event.type == pygame.MOUSEWHEEL:
                if self.rect_barra.collidepoint(mx, my):
                    self.scroll_barra_x = max(0, self.scroll_barra_x - event.y * 40)
                if self.rect_lista.collidepoint(mx, my):
                    self.scroll_lista = max(0, self.scroll_lista - event.y * 20)
                elif self.rect_panel.collidepoint(mx, my):
                    self.scroll_panel_derecho = max(0, self.scroll_panel_derecho - event.y * 24)
                elif self.rect_canvas.collidepoint(mx, my):
                    # Zoom centrado en el ratón
                    old_ix, old_iy = self._get_canvas_coords(mx, my)
                    zoom_factor = 1.1 if event.y > 0 else 0.9
                    self.zoom = max(0.1, min(10.0, self.zoom * zoom_factor))
                    new_sx, new_sy = self._get_screen_coords(old_ix, old_iy)
                    self.pan_x += mx - new_sx
                    self.pan_y += my - new_sy

        return True

    def _get_frame_por_punto(self, mx, my):
        vx, vy = self._get_canvas_coords(mx, my)
        for i, f in enumerate(self.frames_grid):
            if f.x <= vx < f.x + f.w and f.y <= vy < f.y + f.h: return i
        return None

    def _update_caja_seleccion(self):
        x1, y1 = self.caja_inicio
        x2, y2 = self.caja_fin
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
        self.seleccionados = []
        for i, f in enumerate(self.frames_grid):
            # Usamos coordenadas de pantalla para la colisión de la caja
            fr_s = pygame.Rect(self._get_screen_coords(f.x, f.y), (f.w * self.zoom, f.h * self.zoom))
            if rect.colliderect(fr_s): self.seleccionados.append(i)

    def _aplicar_corte_manual(self):
        """Divide un fragmento en dos: el área seleccionada y el resto de ese fragmento"""
        if not self.rect_seleccion_corte or not self.img_sheet: return
        
        vx, vy, vw, vh = self.rect_seleccion_corte
        if vw < 0: vx += vw; vw = abs(vw)
        if vh < 0: vy += vh; vh = abs(vh)
        
        if vw < 5 or vh < 5: return
        
        # 1. Buscar fragmento padre
        idx_padre = -1
        for i, f in enumerate(self.fragmentos):
            rect_v = pygame.Rect(f.pos_virtual[0], f.pos_virtual[1], f.rect_original.w, f.rect_original.h)
            if rect_v.collidepoint(vx, vy):
                idx_padre = i
                break
        
        if idx_padre == -1: return
        padre = self.fragmentos[idx_padre]

        # 2. Calcular rect de la selección relativo al origen de la imagen real
        ix = padre.rect_original.x + (vx - padre.pos_virtual[0])
        iy = padre.rect_original.y + (vy - padre.pos_virtual[1])
        
        rect_seleccion_real = pygame.Rect(int(ix), int(iy), int(vw), int(vh)).clip(padre.rect_original)
        
        if rect_seleccion_real.width < 5 or rect_seleccion_real.height < 5: return

        # 3. Crear el nuevo fragmento (la selección)
        nuevo_fragmento = Fragmento(rect_seleccion_real, (0, 0)) # Posición se recalculará

        # 4. Crear el fragmento del "resto" (lo que queda debajo de la selección en el padre)
        # Asumimos división vertical principalmente para hojas largas
        rect_resto_real = pygame.Rect(
            padre.rect_original.x, 
            rect_seleccion_real.bottom, 
            padre.rect_original.w, 
            padre.rect_original.bottom - rect_seleccion_real.bottom
        ).clip(padre.rect_original)

        # 5. Actualizar lista de fragmentos
        self.fragmentos.pop(idx_padre)
        self.fragmentos.insert(idx_padre, nuevo_fragmento)
        if rect_resto_real.height > 5:
            self.fragmentos.insert(idx_padre + 1, Fragmento(rect_resto_real, (0, 0)))

        # 6. Recalcular todas las posiciones virtuales para que queden en fila horizontal
        cur_vx = 0
        for f in self.fragmentos:
            f.pos_virtual = (cur_vx, 0)
            cur_vx += f.rect_original.w + 20
            
        print(f"[OK] Imagen dividida. Fragmentos actuales: {len(self.fragmentos)}")

    def auto_detectar_sprites(self):
        """Algoritmo fiel al sprite-detector.worker.js de The Spriters Toolkit.
        1. Detecta si la imagen tiene transparencia o samplea color de fondo por bordes/esquinas.
        2. BFS flood-fill en 8 direcciones para islas de píxeles.
        3. Filtra por tamaño mínimo relativo al promedio.
        4. Merge de cajas superpuestas.
        """
        if not self.img_sheet:
            return

        surface = self.img_sheet
        W, H = surface.get_width(), surface.get_height()

        # ---- 1. Detectar si hay transparencia (muestra cada 10 píxeles aprox) ----
        transparent_count = 0
        sample_count = 0
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                alpha = surface.get_at((x, y))[3]
                if alpha < 250:
                    transparent_count += 1
                sample_count += 1
        has_transparency = sample_count > 0 and (transparent_count / sample_count) > 0.05

        # ---- 2. Detectar color de fondo si no es transparente ----
        bg_r, bg_g, bg_b = 0, 0, 0
        bg_is_transparent = has_transparency

        if not has_transparency:
            color_counts = {}
            sample_pts = []
            edge_step_x = max(1, W // 100)
            edge_step_y = max(1, H // 100)

            for x in range(0, W, edge_step_x):
                sample_pts.append((x, 0))
                sample_pts.append((x, H - 1))
            for y in range(0, H, edge_step_y):
                sample_pts.append((0, y))
                sample_pts.append((W - 1, y))
            # Esquinas densas
            for cx in range(0, min(W // 10, 50), 2):
                for cy in range(0, min(H // 10, 50), 2):
                    sample_pts += [(cx, cy), (W-1-cx, cy), (cx, H-1-cy), (W-1-cx, H-1-cy)]

            for (x, y) in sample_pts:
                if not (0 <= x < W and 0 <= y < H): continue
                col = surface.get_at((x, y))
                if col[3] < 50: continue
                key = (col[0], col[1], col[2])
                is_edge = x == 0 or y == 0 or x == W-1 or y == H-1
                is_corner = (x < 10 or x > W-10) and (y < 10 or y > H-10)
                if key not in color_counts:
                    color_counts[key] = {"count": 0, "edges": 0, "corners": 0}
                color_counts[key]["count"] += 1
                if is_edge: color_counts[key]["edges"] += 1
                if is_corner: color_counts[key]["corners"] += 1

            best_key, best_score = None, -1
            for key, v in color_counts.items():
                score = v["count"] + v["edges"] * 2 + v["corners"] * 3
                if score > best_score:
                    best_score = score
                    best_key = key
            if best_key:
                bg_r, bg_g, bg_b = best_key

        # ---- 3. Función isBackground ----
        def is_background(x, y):
            if x < 0 or y < 0 or x >= W or y >= H:
                return True
            col = surface.get_at((x, y))
            if bg_is_transparent:
                return col[3] < 128
            if col[3] == 0:
                return True
            if col[3] < 255:   # semi-transparente = parte del sprite
                return False
            return col[0] == bg_r and col[1] == bg_g and col[2] == bg_b

        # ---- 4. BFS Flood-fill en 4 direcciones (componentes conexas) ----
        visited = bytearray(W * H)   # 0=no visitado, 1=visitado
        raw_sprites = []
        # Solo usar 4 direcciones (arriba, abajo, izq, der), evitar diagonales 
        # para que personajes pegados por una esquina se corten bien.
        DIRS = [(-1,0),(1,0),(0,-1),(0,1)]

        for start_y in range(H):
            for start_x in range(W):
                idx = start_y * W + start_x
                if visited[idx]:
                    continue
                visited[idx] = 1
                if is_background(start_x, start_y):
                    continue

                # Nueva isla
                queue = [(start_x, start_y)]
                min_x = max_x = start_x
                min_y = max_y = start_y
                pixel_count = 0

                while queue:
                    cx, cy = queue.pop()
                    pixel_count += 1
                    if cx < min_x: min_x = cx
                    if cx > max_x: max_x = cx
                    if cy < min_y: min_y = cy
                    if cy > max_y: max_y = cy

                    for dx, dy in DIRS:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < W and 0 <= ny < H:
                            nidx = ny * W + nx
                            if not visited[nidx]:
                                visited[nidx] = 1
                                if not is_background(nx, ny):
                                    queue.append((nx, ny))

                raw_sprites.append({
                    "x": min_x, "y": min_y,
                    "width": max_x - min_x + 1,
                    "height": max_y - min_y + 1,
                    "pixels": pixel_count
                })

        # ---- 5. Filtrar ruido ----
        if raw_sprites:
            total_area = sum(s["width"] * s["height"] for s in raw_sprites)
            avg_area = total_area / len(raw_sprites)
            min_size = max(4, int((avg_area ** 0.5) * 0.05))
            raw_sprites = [
                s for s in raw_sprites
                if s["width"] >= min_size
                and s["height"] >= min_size
                and s["pixels"] > (min_size * min_size * 0.5)
            ]

        # ---- 6. Merge cajas solapadas (tolerance=0 = solo superpuestas) ----
        def merge_sprites(sprites, tolerance=0):
            if len(sprites) <= 1 or tolerance == 0:
                return sprites
            working = [dict(s) for s in sprites]
            merged_flags = [False] * len(working)
            result = []
            for i in range(len(working)):
                if merged_flags[i]: continue
                cur = dict(working[i])
                changed = True
                while changed:
                    changed = False
                    for j in range(len(working)):
                        if merged_flags[j] or j == i: continue
                        o = working[j]
                        # En un sprite sheet denso, las cajas delimitadoras a menudo se cruzan (ej. una espada sobre la cabeza del de abajo)
                        # Si unimos todas las que se cruzan, terminamos con columnas gigantes de sprites fundidos.
                        # Para replicar un buen Auto-Detect, SOLO unimos si una caja está COMPLETAMENTE contenida dentro de la otra.
                        contained_in_o = (
                            cur["x"] >= o["x"] - tolerance and
                            cur["x"] + cur["width"] <= o["x"] + o["width"] + tolerance and
                            cur["y"] >= o["y"] - tolerance and
                            cur["y"] + cur["height"] <= o["y"] + o["height"] + tolerance
                        )
                        o_contained_in_cur = (
                            o["x"] >= cur["x"] - tolerance and
                            o["x"] + o["width"] <= cur["x"] + cur["width"] + tolerance and
                            o["y"] >= cur["y"] - tolerance and
                            o["y"] + o["height"] <= cur["y"] + cur["height"] + tolerance
                        )
                        overlap = contained_in_o or o_contained_in_cur
                        if overlap:
                            new_x = min(cur["x"], o["x"])
                            new_y = min(cur["y"], o["y"])
                            new_r = max(cur["x"]+cur["width"], o["x"]+o["width"])
                            new_b = max(cur["y"]+cur["height"], o["y"]+o["height"])
                            cur = {"x":new_x, "y":new_y, "width":new_r-new_x, "height":new_b-new_y, "pixels":0}
                            merged_flags[j] = True
                            changed = True
                result.append(cur)
            return result

        final_sprites = merge_sprites(raw_sprites, tolerance=0)

        # ---- 7. Convertir a FrameData en coordenadas VIRTUALES ----
        self.frames_grid = []
        for s in final_sprites:
            # Los frames del visualizador se guardan en coords virtuales
            # Pero en este editor virtual=imagen (fragmento principal 0,0)
            self.frames_grid.append(FrameData(s["x"], s["y"], s["width"], s["height"]))
        self.seleccionados = []
        print(f"[OK] Auto-detect: {len(self.frames_grid)} sprites encontrados")

    # ============================================================
    #  ATLAS PACKER
    # ============================================================
    def _set_mensaje(self, msg):
        self.mensaje_ui = msg
        self.mensaje_tick = pygame.time.get_ticks()

    def generar_atlas(self):
        """Empaca los frames seleccionados en un PNG atlas + JSON de coordenadas.
        Algoritmo Shelf (filas) ordenado por altura descendente.
        """
        import json as _json

        if not self.img_sheet or not self.seleccionados:
            self._set_mensaje("⚠️ SELECCIONA LOS SPRITES PARA EL ATLAS")
            return

        nombre_personaje = self._nombre_limpio(self.input_personaje)
        accion = self._nombre_limpio(self._accion_actual())
        if not nombre_personaje or not accion:
            self._set_mensaje("⚠️ NOMBRE Y ACCIÓN SON OBLIGATORIOS")
            return

        # Guardado automático con la misma lógica base de sprites: carpeta destino/ personaje/
        # y nombre base personaje_accion para PNG y JSON.
        path_destino = self._ruta_destino_actual() / nombre_personaje
        path_destino.mkdir(parents=True, exist_ok=True)
        base_nombre = f"{nombre_personaje}_{accion}"
        png_path = path_destino / f"{base_nombre}.png"
        json_path = path_destino / f"{base_nombre}.json"
        pad = self.atlas_padding

        # Recoger rect reales de cada frame SELECCIONADO
        sprites_info = []
        for idx in self.seleccionados:
            f = self.frames_grid[idx]
            ix, iy = self._get_image_coords(f.x + f.w // 2, f.y + f.h // 2)
            if ix is None:
                continue
            rx = int(ix - f.w // 2)
            ry = int(iy - f.h // 2)
            rect_img = pygame.Rect(rx, ry, int(f.w), int(f.h)).clip(self.img_sheet.get_rect())
            if rect_img.width > 0 and rect_img.height > 0:
                sprites_info.append({"rect": rect_img, "surf": self.img_sheet.subsurface(rect_img)})

        if not sprites_info:
            self._set_mensaje("⚠️ SIN RECORTES VÁLIDOS")
            return

        # Ordenar por altura descendente (Shelf algorithm funciona mejor)
        sprites_info.sort(key=lambda s: s["rect"].height, reverse=True)

        # Calcular ancho del atlas (potencia de 2 más cercana que sea suficiente)
        max_w = max(s["rect"].width for s in sprites_info)
        total_area = sum((s["rect"].width + pad) * (s["rect"].height + pad) for s in sprites_info)
        atlas_w = 128
        while atlas_w < max_w or atlas_w * atlas_w < total_area * 1.2:
            atlas_w *= 2
            if atlas_w > 4096:
                break

        # Shelf packing
        placed = []
        cur_x, cur_y, shelf_h = pad, pad, 0
        for s in sprites_info:
            sw, sh = s["rect"].width, s["rect"].height
            if cur_x + sw + pad > atlas_w:
                cur_x = pad
                cur_y += shelf_h + pad
                shelf_h = 0
            placed.append({"surf": s["surf"], "rect": s["rect"],
                           "atlas_x": cur_x, "atlas_y": cur_y, "w": sw, "h": sh})
            shelf_h = max(shelf_h, sh)
            cur_x += sw + pad

        atlas_h = cur_y + shelf_h + pad
        # Potencia de 2 en altura también
        ah = 128
        while ah < atlas_h:
            ah *= 2
        atlas_h = min(ah, 8192)

        # Crear superficie atlas con alpha
        atlas_surf = pygame.Surface((atlas_w, atlas_h), pygame.SRCALPHA)
        atlas_surf.fill((0, 0, 0, 0))

        json_data = {"atlas": {"width": atlas_w, "height": atlas_h}, "sprites": []}
        for i, p in enumerate(placed):
            atlas_surf.blit(p["surf"], (p["atlas_x"], p["atlas_y"]))
            nombre = f"{nombre_personaje}_{accion}_{i+1}"
            json_data["sprites"].append({
                "name":   nombre,
                "x":      p["atlas_x"],
                "y":      p["atlas_y"],
                "width":  p["w"],
                "height": p["h"]
            })

        # Guardar archivos
        pygame.image.save(atlas_surf, str(png_path))
        with open(json_path, "w", encoding="utf-8") as f:
            _json.dump(json_data, f, indent=2, ensure_ascii=False)

        self._set_mensaje(f"✅ ATLAS GENERADO: {png_path.name}")
        print(f"[OK] Atlas generado: {png_path}")
        print(f"[OK] JSON generado:  {json_path}")
        print(f"  {len(placed)} sprites | {atlas_w}x{atlas_h}px")

    # ============================================================
    #  ANIMATION PREVIEWER
    # ============================================================
    def toggle_animacion(self):
        if not self.seleccionados:
            print("⚠️ Selecciona al menos 2 frames para animar")
            return
        self.anim_playing    = not self.anim_playing
        self.anim_frame_idx  = 0
        self.anim_last_tick  = pygame.time.get_ticks()
        estado = "PLAY" if self.anim_playing else "STOP"
        print(f"▶️ Animación {estado} | {len(self.seleccionados)} frames @ {self.anim_fps} FPS")

    def _tick_animacion(self):
        """Avanza el frame de la animación según FPS. Llamar en cada ciclo de dibujo."""
        if not self.anim_playing or not self.seleccionados:
            return
        ahora = pygame.time.get_ticks()
        ms_por_frame = 1000 // max(1, self.anim_fps)
        if ahora - self.anim_last_tick >= ms_por_frame:
            self.anim_frame_idx = (self.anim_frame_idx + 1) % len(self.seleccionados)
            self.anim_last_tick = ahora

    # ============================================================
    #  GRID OVERLAY
    # ============================================================
    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        print(f"▦ Grid overlay: {'ON' if self.grid_visible else 'OFF'} | {self.grid_cell_w}x{self.grid_cell_h}px")

    def _guardar_seleccion(self):
        if not self.seleccionados or not self.img_sheet:
            self._set_mensaje("⚠️ NADA SELECCIONADO")
            return

        nombre_personaje = self._nombre_limpio(self.input_personaje)
        accion = self._nombre_limpio(self._accion_actual())
        if not nombre_personaje or not accion:
            self._set_mensaje("⚠️ NOMBRE Y ACCIÓN SON OBLIGATORIOS")
            return

        root = tk.Tk()
        root.withdraw()
        carpeta_inicial = self._ruta_destino_actual()
        path_elegido = filedialog.askdirectory(
            title="Elige la carpeta destino dentro de assets",
            initialdir=str(carpeta_inicial),
            mustexist=True,
        )
        root.destroy()

        if not path_elegido:
            return

        path = Path(path_elegido)
        try:
            path.relative_to(self.path_assets)
        except ValueError:
            self._set_mensaje("⚠️ ELIGE UNA CARPETA DENTRO DE ASSETS")
            return

        path = path / nombre_personaje
        path.mkdir(parents=True, exist_ok=True)
        count = 0
        for i, idx in enumerate(self.seleccionados):
            f = self.frames_grid[idx]
            ix, iy = self._get_image_coords(f.x + f.w // 2, f.y + f.h // 2)
            if ix is not None:
                rect_img = pygame.Rect(int(ix - f.w // 2), int(iy - f.h // 2), int(f.w), int(f.h))
                rect_img = rect_img.clip(self.img_sheet.get_rect())
                if rect_img.width > 0 and rect_img.height > 0:
                    pygame.image.save(self.img_sheet.subsurface(rect_img), str(path / f"{nombre_personaje}_{accion}_{i+1}.png"))
                    f.usado = True
                    count += 1
        self._set_mensaje(f"✅ {count} SPRITES GUARDADOS")
        self.seleccionados = []

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        self._actualizar_carpetas_destino()

        pygame.draw.rect(self.pantalla, COLOR_PANEL, self.rect_barra, border_radius=8)
        clip_anterior = self.pantalla.get_clip()
        self.pantalla.set_clip(self.rect_barra)

        btn_agregar = pygame.Rect(self.rect_barra.x, self.rect_barra.y + 4, 30, 28)
        pygame.draw.rect(self.pantalla, (70, 130, 180), btn_agregar, border_radius=4)
        self.pantalla.blit(self.fuente_bold.render("+", True, COLOR_TEXTO), (btn_agregar.centerx - 4, btn_agregar.centery - 8))

        x_cursor = self.rect_barra.x + 40 - self.scroll_barra_x
        for item in self.barra_carpetas:
            txt = self.fuente_bold.render(item["nombre"], True, COLOR_TEXTO)
            br = pygame.Rect(x_cursor, self.rect_barra.y + 4, txt.get_width() + 20, 28)
            if br.right >= self.rect_barra.left and br.left <= self.rect_barra.right:
                activo = self.barra_folder_activa == item["path"]
                pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if activo else COLOR_BOTON, br, border_radius=5)
                self.pantalla.blit(txt, (br.centerx - txt.get_width()//2, br.centery - txt.get_height()//2))
                cerrar_rect = pygame.Rect(br.right - 16, br.y + 2, 14, 14)
                pygame.draw.rect(self.pantalla, (180, 70, 70), cerrar_rect, border_radius=3)
                cruz = self.fuente_ui.render("x", True, (255, 255, 255))
                self.pantalla.blit(cruz, (cerrar_rect.centerx - cruz.get_width()//2, cerrar_rect.centery - cruz.get_height()//2 - 1))
            x_cursor += br.w + 10

        self.pantalla.set_clip(clip_anterior)
        
        pygame.draw.rect(self.pantalla, COLOR_PANEL, self.rect_lista, border_radius=8)
        
        # Botón Selector de Carpeta
        btn_carpeta = pygame.Rect(self.rect_lista.x + 10, self.rect_lista.y + 10, self.rect_lista.w - 20, 25)
        pygame.draw.rect(self.pantalla, (200, 80, 50) if self.carpeta_externa else (50, 100, 180), btn_carpeta, border_radius=4)
        txt_carpeta = "QUITAR EXTERNO [X]" if self.carpeta_externa else "📁 CARPETA ESPECÍFICA"
        cx = self.fuente_bold.render(txt_carpeta, True, (255,255,255))
        self.pantalla.blit(cx, (btn_carpeta.centerx - cx.get_width()//2, btn_carpeta.centery - cx.get_height()//2))

        for i, rec in enumerate(self.lista_recursos):
            y = self.rect_lista.y + 45 + i * 25 - self.scroll_lista
            if self.rect_lista.y + 40 <= y <= self.rect_lista.bottom - 20:
                is_sel = self.recurso_seleccionado and self.recurso_seleccionado["path"] == rec["path"]
                if is_sel: pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO, (self.rect_lista.x+5, y-2, self.rect_lista.w-10, 22), border_radius=4)
                self.pantalla.blit(self.fuente_ui.render(rec["nombre"][:28], True, (255,255,255) if is_sel else COLOR_TEXTO), (self.rect_lista.x+10, y))
        
        # CANVAS con Clip para Zoom y Pan
        pygame.draw.rect(self.pantalla, (10, 10, 15), self.rect_canvas, border_radius=8)
        if self.img_sheet:
            # Crear una superficie para el canvas con el tamaño real del canvas para clipping
            canvas_surf = pygame.Surface((self.rect_canvas.w, self.rect_canvas.h))
            canvas_surf.fill((10, 10, 15))
            
            # DIBUJAR FRAGMENTOS (Reemplaza al dibujo directo de img_sheet)
            for f in self.fragmentos:
                # El fragmento se dibuja en vx, vy escalado por zoom
                vx, vy = f.pos_virtual
                vw, vh = f.rect_original.w, f.rect_original.h
                
                # Rectángulo de dibujo en el canvas_surf
                dest_rect = pygame.Rect(vx * self.zoom + self.pan_x, vy * self.zoom + self.pan_y, vw * self.zoom, vh * self.zoom)
                
                if dest_rect.colliderect(canvas_surf.get_rect()):
                    # Obtener el sub-sprite real
                    sub_sprite = self.img_sheet.subsurface(f.rect_original)
                    # Escalar solo lo necesario para el zoom
                    sub_scaled = pygame.transform.scale(sub_sprite, (int(vw * self.zoom), int(vh * self.zoom)))
                    canvas_surf.blit(sub_scaled, dest_rect.topleft)
                    # Borde de fragmento
                    pygame.draw.rect(canvas_surf, (60, 60, 80), dest_rect, 1)

            # Dibujar la Plantilla (escalada)
            if not self.frames_grid and self.template_rect:
                tx, ty, tw, th = self.template_rect
                r = pygame.Rect(tx * self.zoom + self.pan_x, ty * self.zoom + self.pan_y, tw * self.zoom, th * self.zoom)
                pygame.draw.rect(canvas_surf, COLOR_PLANTILLA, r, 2)
                # Handles
                handles = [(r.topleft, 8), (r.topright, 8), (r.bottomleft, 8), (r.bottomright, 8),
                           (r.midtop, 6), (r.midbottom, 6), (r.midleft, 6), (r.midright, 6)]
                for hpos, size in handles:
                    pygame.draw.rect(canvas_surf, COLOR_PLANTILLA, (hpos[0]-size//2, hpos[1]-size//2, size, size))
            
            # Dibujar el Grid (escalado)
            for i, f in enumerate(self.frames_grid):
                fr = pygame.Rect(f.x * self.zoom + self.pan_x, f.y * self.zoom + self.pan_y, f.w * self.zoom, f.h * self.zoom)
                # Solo dibujar si es visible en el canvas_surf
                if fr.colliderect(canvas_surf.get_rect()):
                    if f.usado:
                        s = pygame.Surface((int(fr.w), int(fr.h))); s.set_alpha(150); s.fill((50, 50, 50))
                        canvas_surf.blit(s, fr.topleft)
                    
                    pygame.draw.rect(canvas_surf, COLOR_SELECCION if i in self.seleccionados else (100, 100, 120), fr, 1 if i not in self.seleccionados else 3)
                    
                    if i in self.seleccionados and len(self.seleccionados) == 1:
                        handles = [(fr.topleft, 8), (fr.topright, 8), (fr.bottomleft, 8), (fr.bottomright, 8),
                                   (fr.midtop, 6), (fr.midbottom, 6), (fr.midleft, 6), (fr.midright, 6)]
                        for hpos, size in handles:
                            pygame.draw.rect(canvas_surf, COLOR_SELECCION, (hpos[0]-size//2, hpos[1]-size//2, size, size))
            
            # Caja de selección (coordenadas de pantalla a canvas_surf)
            if self.caja_seleccionando:
                r_screen = pygame.Rect(min(self.caja_inicio[0], self.caja_fin[0]), min(self.caja_inicio[1], self.caja_fin[1]),
                                       abs(self.caja_fin[0]-self.caja_inicio[0]), abs(self.caja_fin[1]-self.caja_inicio[1]))
                r_canvas = pygame.Rect(r_screen.x - self.rect_canvas.x, r_screen.y - self.rect_canvas.y, r_screen.w, r_screen.h)
                pygame.draw.rect(canvas_surf, COLOR_SELECCION, r_canvas, 2)

            # Dibujar selección de CORTE MANUAL
            if self.seleccionando_corte and self.rect_seleccion_corte:
                vx, vy, vw, vh = self.rect_seleccion_corte
                r = pygame.Rect(vx * self.zoom + self.pan_x, vy * self.zoom + self.pan_y, vw * self.zoom, vh * self.zoom)
                pygame.draw.rect(canvas_surf, (255, 50, 50), r, 2)
                txt = self.fuente_ui.render("CORTE MANUAL", True, (255, 50, 50))
                canvas_surf.blit(txt, (r.x, r.y - 18))

            # === GRID OVERLAY ===
            if self.grid_visible and self.img_sheet:
                gw = max(1, self.grid_cell_w)
                gh = max(1, self.grid_cell_h)
                # Tamaño total de la imagen virtual (primer fragmento como referencia)
                img_w = self.img_sheet.get_width()
                img_h = self.img_sheet.get_height()
                grid_color = (255, 255, 0, 80)
                grid_surf = pygame.Surface((self.rect_canvas.w, self.rect_canvas.h), pygame.SRCALPHA)
                # Líneas verticales
                x = 0
                while x <= img_w:
                    sx = int(x * self.zoom + self.pan_x)
                    if 0 <= sx <= self.rect_canvas.w:
                        pygame.draw.line(grid_surf, grid_color, (sx, 0), (sx, self.rect_canvas.h))
                    x += gw
                # Líneas horizontales
                y = 0
                while y <= img_h:
                    sy = int(y * self.zoom + self.pan_y)
                    if 0 <= sy <= self.rect_canvas.h:
                        pygame.draw.line(grid_surf, grid_color, (0, sy), (self.rect_canvas.w, sy))
                    y += gh
                canvas_surf.blit(grid_surf, (0, 0))

            self.pantalla.blit(canvas_surf, self.rect_canvas.topleft)

        pygame.draw.rect(self.pantalla, COLOR_PANEL, self.rect_panel, border_radius=8)
        prev_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(self.rect_panel)

        # == PANEL: Preview de sprite / animación ==
        self._tick_animacion()
        preview_surf = None
        if self.img_sheet and self.frames_grid:
            if self.anim_playing and self.seleccionados:
                idx_anim = self.seleccionados[self.anim_frame_idx % len(self.seleccionados)]
                f = self.frames_grid[idx_anim]
            elif self.seleccionados:
                # Cicla estiláticamente cuando no anima
                idx_anim = self.seleccionados[(pygame.time.get_ticks()//150) % len(self.seleccionados)]
                f = self.frames_grid[idx_anim]
            else:
                f = None

            if f:
                ix, iy = self._get_image_coords(f.x + f.w // 2, f.y + f.h // 2)
                if ix is not None:
                    rect_img = pygame.Rect(int(ix - f.w // 2), int(iy - f.h // 2), int(f.w), int(f.h)).clip(self.img_sheet.get_rect())
                    if rect_img.width > 0 and rect_img.height > 0:
                        preview_surf = self.img_sheet.subsurface(rect_img)

        if preview_surf:
            sw, sh = preview_surf.get_size()
            scale = min(200 / max(sw, 1), 120 / max(sh, 1))
            preview_surf = pygame.transform.scale(preview_surf, (int(sw * scale), int(sh * scale)))
            self.pantalla.blit(
                preview_surf,
                (
                    self.rect_panel.centerx - preview_surf.get_width() // 2,
                    self.rect_panel.y + 70 - preview_surf.get_height() // 2,
                ),
            )
            if self.anim_playing:
                dot_color = (50, 255, 100) if (pygame.time.get_ticks() // 300) % 2 == 0 else (30, 180, 70)
                pygame.draw.circle(self.pantalla, dot_color, (self.rect_panel.x + 20, self.rect_panel.y + 20), 7)
                txt_fps = self.fuente_ui.render(f"▶ {self.anim_fps} FPS", True, (100, 255, 150))
                self.pantalla.blit(txt_fps, (self.rect_panel.x + 32, self.rect_panel.y + 13))

        px, py = self.rect_panel.x + 10, self.rect_panel.y + 148 - self.scroll_panel_derecho

        self.pantalla.blit(self.fuente_bold.render("GUARDAR EN:", True, COLOR_TEXTO), (px, py))
        pygame.draw.rect(self.pantalla, COLOR_BOTON, (px, py + 20, 180, 28), border_radius=4)
        self.pantalla.blit(
            self.fuente_ui.render(self._selector_guardado_actual().upper(), True, COLOR_TEXTO),
            (px + 8, py + 25),
        )
        pygame.draw.rect(self.pantalla, (50, 100, 50), (px + 190, py + 20, 30, 28), border_radius=4)
        self.pantalla.blit(self.fuente_bold.render("+", True, COLOR_TEXTO), (px + 200, py + 24))

        py += 60
        self.pantalla.blit(self.fuente_bold.render("PERSONAJE:", True, COLOR_TEXTO), (px, py))
        pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if self.input_activo == "personaje" else COLOR_BOTON, (px, py + 20, 220, 28))
        nombre_mostrar = self.input_personaje if self.input_personaje else "<ESCRIBE NOMBRE>"
        self.pantalla.blit(self.fuente_ui.render(nombre_mostrar, True, COLOR_TEXTO), (px + 5, py + 25))

        py += 60
        self.pantalla.blit(self.fuente_bold.render("ACCIÓN:", True, COLOR_TEXTO), (px, py))
        rects_accion, fin_accion = self._rects_acciones(px, py + 20)
        for rect, indice in rects_accion:
            opcion = self.opciones_accion[indice]
            activo = self.indice_accion == indice
            pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if activo else COLOR_BOTON, rect, border_radius=4)
            self.pantalla.blit(self.fuente_ui.render(opcion["label"], True, COLOR_TEXTO), (rect.x + 5, rect.y + 4))

        if self.indice_accion is not None and self.opciones_accion[self.indice_accion]["valor"] == "custom":
            py_custom = fin_accion + 8
            pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if self.input_activo == "accion_custom" else COLOR_BOTON, (px, py_custom, 220, 28), border_radius=4)
            accion_mostrar = self.input_accion if self.input_accion else "<ESCRIBE ACCIÓN CUSTOM>"
            self.pantalla.blit(self.fuente_ui.render(accion_mostrar, True, COLOR_TEXTO), (px + 5, py_custom + 5))
            py = py_custom + 36
        else:
            py = fin_accion + 20

        pygame.draw.rect(self.pantalla, (180, 100, 30) if self.modo_corte == "AISLADO" else (30, 100, 180), (px, py, 220, 30), border_radius=5)
        txt_modo = self.fuente_bold.render(f"MODO: {self.modo_corte}", True, COLOR_TEXTO)
        self.pantalla.blit(txt_modo, (px + 110 - txt_modo.get_width() // 2, py + 5))

        py += 38
        pygame.draw.rect(self.pantalla, (50, 150, 50), (px, py, 220, 36), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("CORTAR TODO", True, COLOR_TEXTO), (px + 25, py + 8))

        py += 44
        pygame.draw.rect(self.pantalla, (130, 60, 200), (px, py, 220, 36), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("AUTO DETECTAR [A]", True, COLOR_TEXTO), (px + 14, py + 8))

        py += 44
        pygame.draw.rect(self.pantalla, (50, 120, 50), (px, py, 220, 36), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("GUARDAR", True, COLOR_TEXTO), (px + 70, py + 8))

        py += 44
        pygame.draw.rect(self.pantalla, (30, 100, 180), (px, py, 220, 36), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("GENERAR ATLAS [atlas]", True, COLOR_TEXTO), (px + 5, py + 8))

        py += 44
        color_anim = (20, 160, 80) if self.anim_playing else (70, 130, 170)
        pygame.draw.rect(self.pantalla, color_anim, (px, py, 220, 30), border_radius=5)
        lbl_anim = "⏹ STOP ANIM [P]" if self.anim_playing else "▶ PLAY ANIM [P]"
        self.pantalla.blit(self.fuente_bold.render(lbl_anim, True, COLOR_TEXTO), (px + 10, py + 6))

        py += 38
        self.pantalla.blit(self.fuente_ui.render("FPS:", True, COLOR_TEXTO_DIM), (px, py + 5))
        pygame.draw.rect(self.pantalla, COLOR_BOTON, (px + 35, py, 68, 26), border_radius=4)
        self.pantalla.blit(self.fuente_bold.render(str(self.anim_fps), True, COLOR_TEXTO), (px + 60, py + 4))
        pygame.draw.rect(self.pantalla, (60, 100, 60), (px + 35, py, 30, 26), border_radius=4)
        self.pantalla.blit(self.fuente_bold.render("-", True, COLOR_TEXTO), (px + 46, py + 3))
        pygame.draw.rect(self.pantalla, (60, 100, 60), (px + 75, py, 30, 26), border_radius=4)
        self.pantalla.blit(self.fuente_bold.render("+", True, COLOR_TEXTO), (px + 83, py + 3))

        py += 36
        color_grid = (200, 160, 30) if self.grid_visible else (80, 80, 100)
        pygame.draw.rect(self.pantalla, color_grid, (px, py, 220, 28), border_radius=5)
        lbl_grid = "▦ GRID ON [G]" if self.grid_visible else "▦ GRID OFF [G]"
        self.pantalla.blit(self.fuente_bold.render(lbl_grid, True, COLOR_TEXTO), (px + 15, py + 5))

        py += 34
        self.pantalla.blit(self.fuente_ui.render("W:", True, COLOR_TEXTO_DIM), (px, py + 4))
        color_gw = COLOR_BOTON_ACTIVO if self.input_activo_grid == "grid_w" else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_gw, (px + 20, py, 80, 22), border_radius=3)
        val_w = (self.input_grid_w + "|") if self.input_activo_grid == "grid_w" else str(self.grid_cell_w)
        self.pantalla.blit(self.fuente_ui.render(val_w, True, COLOR_TEXTO), (px + 25, py + 3))

        self.pantalla.blit(self.fuente_ui.render("H:", True, COLOR_TEXTO_DIM), (px + 115, py + 4))
        color_gh = COLOR_BOTON_ACTIVO if self.input_activo_grid == "grid_h" else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_gh, (px + 135, py, 80, 22), border_radius=3)
        val_h = (self.input_grid_h + "|") if self.input_activo_grid == "grid_h" else str(self.grid_cell_h)
        self.pantalla.blit(self.fuente_ui.render(val_h, True, COLOR_TEXTO), (px + 140, py + 3))

        py += 34
        pygame.draw.rect(self.pantalla, (120, 50, 50), (px, py, 220, 28), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("LIMPIAR", True, COLOR_TEXTO), (px + 55, py + 5))

        self.max_scroll_panel_derecho = max(0, py + 40 - self.rect_panel.height)
        if self.scroll_panel_derecho > self.max_scroll_panel_derecho:
            self.scroll_panel_derecho = self.max_scroll_panel_derecho

        self.pantalla.set_clip(prev_clip)

        # --- MENSAJE UI ---
        if self.mensaje_ui and pygame.time.get_ticks() - self.mensaje_tick < 3000:
            # Dibujar un banner en la parte inferior
            msg_surf = self.fuente_bold.render(self.mensaje_ui, True, (255, 255, 255))
            bg_rect = pygame.Rect(0, self.alto - 40, self.ancho, 40)
            pygame.draw.rect(self.pantalla, (40, 40, 60), bg_rect)
            pygame.draw.line(self.pantalla, (100, 100, 255), (0, self.alto - 40), (self.ancho, self.alto - 40), 2)
            self.pantalla.blit(msg_surf, (self.ancho // 2 - msg_surf.get_width() // 2, self.alto - 30))

        pygame.display.flip()

    def ejecutar(self):
        while self.manejar_eventos():
            self.dibujar()
            self.reloj.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    EditorMaestroSprites().ejecutar()
