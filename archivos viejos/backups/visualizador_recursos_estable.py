import pygame
import os
from pathlib import Path

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
RUTAS_BUSQUEDA = [
    r"c:\Users\vicko\Documents\RPG",
    r"C:\Users\vicko\Documents\ias y programas\rpg"
]

class FrameData:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.usado = False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

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
        self.categorias = ["HEROES", "MONSTRUOS", "NPCs", "OBJETOS", "OTROS"]
        self.cat_activa = "HEROES"
        self.lista_recursos = []
        self.recurso_seleccionado = None
        self.img_sheet = None
        
        # Carpetas de Destino (assets/sprites)
        self.path_assets = Path(r"c:\Users\vicko\Documents\RPG\assets\sprites")
        self.carpetas_destino = []
        self.idx_carpeta_destino = 0
        self.creando_carpeta = False
        self.input_nueva_carpeta = ""
        self.carpeta_hovered = False
        self._actualizar_carpetas_destino()
        
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
        
        # Inputs
        self.input_personaje = "marciano"
        self.input_accion = "caminando"
        self.input_activo = None
        
        # UI
        self.scroll_lista = 0
        self.rect_lista = pygame.Rect(10, 80, 250, 600)
        self.rect_canvas = pygame.Rect(270, 80, 750, 600)
        self.rect_panel = pygame.Rect(1030, 80, 240, 600)
        
        self._escanear_recursos()
        self.actualizar_lista_categoria()
        self.reordenar_ui()

    def reordenar_ui(self):
        w, h = self.pantalla.get_size()
        if w < 100 or h < 100: return
        self.ancho, self.alto = w, h
        
        self.rect_lista = pygame.Rect(10, 80, 250, h - 100)
        self.rect_panel = pygame.Rect(w - 250, 80, 240, h - 100)
        self.rect_canvas = pygame.Rect(270, 80, w - 270 - 260, h - 100)

    def _escanear_recursos(self):
        self.base_datos = {cat: [] for cat in self.categorias}
        extensiones = ('.png', '.jpg', '.jpeg')
        for ruta_base in RUTAS_BUSQUEDA:
            if not os.path.exists(ruta_base): continue
            for root, dirs, files in os.walk(ruta_base):
                if any(x in root.lower() for x in ['.git', '__pycache__', 'node_modules']): continue
                cat_target = "OTROS"
                root_lower = root.lower()
                if any(x in root_lower for x in ['hero', 'personaje']): cat_target = "HEROES"
                elif any(x in root_lower for x in ['monst', 'enemy', 'boss']): cat_target = "MONSTRUOS"
                elif any(x in root_lower for x in ['npc', 'town']): cat_target = "NPCs"
                elif any(x in root_lower for x in ['item', 'object', 'chest']): cat_target = "OBJETOS"
                for f in files:
                    if f.lower().endswith(extensiones):
                        self.base_datos[cat_target].append({"nombre": f, "path": os.path.join(root, f)})

    def actualizar_lista_categoria(self):
        self.lista_recursos = self.base_datos[self.cat_activa]
        self.scroll_lista = 0

    def _actualizar_carpetas_destino(self):
        if not self.path_assets.exists(): self.path_assets.mkdir(parents=True, exist_ok=True)
        self.carpetas_destino = [d.name for d in self.path_assets.iterdir() if d.is_dir()]
        if not self.carpetas_destino:
            self.carpetas_destino = ["heroes", "monstruos", "npcs", "objetos", "otros"]
            for c in self.carpetas_destino: (self.path_assets / c).mkdir(exist_ok=True)
        if self.idx_carpeta_destino >= len(self.carpetas_destino): self.idx_carpeta_destino = 0

    def cargar_sheet(self, recurso):
        self.recurso_seleccionado = recurso
        self.img_sheet = pygame.image.load(recurso["path"]).convert_alpha()
        self.template_rect = None
        self.frames_grid = []
        self.seleccionados = []
        print(f"✓ Cargado: {recurso['nombre']}")

    def _generar_grid_completo(self):
        if not self.img_sheet or not self.template_rect: return
        tx, ty, tw, th = int(self.template_rect[0]), int(self.template_rect[1]), int(abs(self.template_rect[2])), int(abs(self.template_rect[3]))
        if tw < 4 or th < 4: return
        w_img, h_img = self.img_sheet.get_size()
        frames_existentes = [pygame.Rect(f.x, f.y, f.w, f.h) for f in self.frames_grid]
        nuevos_frames = []
        for y in range(ty, h_img, th):
            for x in range(tx, w_img, tw):
                fw = tw if x + tw <= w_img else w_img - x
                fh = th if y + th <= h_img else h_img - y
                if fw > 2 and fh > 2:
                    nuevo_rect = pygame.Rect(x, y, fw, fh)
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
                # 1. Categorías
                for i, cat in enumerate(self.categorias):
                    if pygame.Rect(10 + i * 110, 10, 100, 30).collidepoint(mx, my):
                        self.cat_activa = cat
                        self.actualizar_lista_categoria()
                
                # 2. Lista
                if self.rect_lista.collidepoint(mx, my):
                    idx = (my - self.rect_lista.y + self.scroll_lista) // 25
                    if 0 <= idx < len(self.lista_recursos): self.cargar_sheet(self.lista_recursos[idx])
                
                # 3. Canvas
                if self.rect_canvas.collidepoint(mx, my) and self.img_sheet:
                    ix, iy = mx - self.rect_canvas.x, my - self.rect_canvas.y
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
                                if abs(ix - hx) < 10 and abs(iy - hy) < 10:
                                    self.resizing_handle_plantilla = d
                                    encontro = True
                                    break
                            if not encontro:
                                self.dibujando_template = True
                                self.template_rect = [ix, iy, 0, 0]
                        else:
                            self.dibujando_template = True
                            self.template_rect = [ix, iy, 0, 0]
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
                                if abs(ix - hx) < 10 and abs(iy - hy) < 10:
                                    self.resizing_frame_idx = self.seleccionados[0]
                                    self.resizing_frame_dir = dir
                                    encontro_handle = True
                                    break
                        
                        if not encontro_handle:
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
                    px, py = self.rect_panel.x + 10, self.rect_panel.y + 140
                    
                    # Selector de Carpeta de Destino
                    if pygame.Rect(px, py + 20, 180, 28).collidepoint(mx, my):
                        self.idx_carpeta_destino = (self.idx_carpeta_destino + 1) % len(self.carpetas_destino)
                    
                    # Botón [+]
                    if pygame.Rect(px + 190, py + 20, 30, 28).collidepoint(mx, my):
                        self.creando_carpeta = True
                        self.input_activo = "nueva_carpeta"
                        self.input_nueva_carpeta = ""
                    
                    # Input Personaje
                    py += 60
                    if pygame.Rect(px, py + 20, 220, 28).collidepoint(mx, my):
                        self.input_activo = "personaje"
                    
                    # Input Acción
                    py += 60
                    if pygame.Rect(px, py + 20, 220, 28).collidepoint(mx, my):
                        self.input_activo = "accion"
                    
                    # Botones de Acción
                    py += 140
                    if pygame.Rect(px, py, 220, 40).collidepoint(mx, my):
                        self._generar_grid_completo()
                    
                    py += 50
                    if pygame.Rect(px, py, 220, 40).collidepoint(mx, my):
                        self._guardar_seleccion()
                    
                    py += 50
                    if pygame.Rect(px, py, 220, 30).collidepoint(mx, my):
                        self.frames_grid = []
                        self.template_rect = None
                        self.seleccionados = []
                else:
                    # Desactivar input si se pulsa fuera del panel
                    if not self.rect_lista.collidepoint(mx, my):
                        self.input_activo = None

            if event.type == pygame.MOUSEMOTION:
                ix, iy = mx - self.rect_canvas.x, my - self.rect_canvas.y
                
                # Hover dinámico para borrar carpetas (DEL)
                if self.rect_panel.collidepoint(mx, my):
                    px, py = self.rect_panel.x + 10, self.rect_panel.y + 140
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
                self.dibujando_template = False
                self.resizing_handle_plantilla = None
                self.resizing_frame_idx = None
                self.resizing_frame_dir = None
                self.caja_seleccionando = False

            if event.type == pygame.KEYDOWN:
                if self.input_activo == "personaje":
                    if event.key == pygame.K_BACKSPACE: self.input_personaje = self.input_personaje[:-1]
                    elif event.unicode.isprintable(): self.input_personaje += event.unicode
                elif self.input_activo == "accion":
                    if event.key == pygame.K_BACKSPACE: self.input_accion = self.input_accion[:-1]
                    elif event.unicode.isprintable(): self.input_accion += event.unicode
                elif self.input_activo == "nueva_carpeta":
                    if event.key == pygame.K_RETURN:
                        if self.input_nueva_carpeta.strip():
                            (self.path_assets / self.input_nueva_carpeta.strip().lower()).mkdir(parents=True, exist_ok=True)
                            self._actualizar_carpetas_destino()
                        self.creando_carpeta = False; self.input_activo = None
                    elif event.key == pygame.K_BACKSPACE: self.input_nueva_carpeta = self.input_nueva_carpeta[:-1]
                    elif event.unicode.isprintable(): self.input_nueva_carpeta += event.unicode
                elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.seleccionados:
                    for i in sorted(self.seleccionados, reverse=True): self.frames_grid.pop(i)
                    self.seleccionados = []

            if event.type == pygame.MOUSEWHEEL:
                if self.rect_lista.collidepoint(mx, my): self.scroll_lista = max(0, self.scroll_lista - event.y * 20)

        return True

    def _get_frame_por_punto(self, mx, my):
        ix, iy = mx - self.rect_canvas.x, my - self.rect_canvas.y
        for i, f in enumerate(self.frames_grid):
            if f.x <= ix < f.x + f.w and f.y <= iy < f.y + f.h: return i
        return None

    def _update_caja_seleccion(self):
        x1, y1 = self.caja_inicio
        x2, y2 = self.caja_fin
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
        self.seleccionados = []
        for i, f in enumerate(self.frames_grid):
            if rect.colliderect(pygame.Rect(self.rect_canvas.x + f.x, self.rect_canvas.y + f.y, f.w, f.h)): self.seleccionados.append(i)

    def _guardar_seleccion(self):
        if not self.seleccionados or not self.img_sheet: return
        path = self.path_assets / self.carpetas_destino[self.idx_carpeta_destino] / self.input_personaje
        path.mkdir(parents=True, exist_ok=True)
        for i, idx in enumerate(self.seleccionados):
            f = self.frames_grid[idx]
            pygame.image.save(self.img_sheet.subsurface(f.get_rect()), str(path / f"{self.input_personaje}_{self.input_accion}_{i+1}.png"))
            f.usado = True
        self.seleccionados = []

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        for i, cat in enumerate(self.categorias):
            br = pygame.Rect(10 + i * 110, 10, 100, 30)
            pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if self.cat_activa == cat else COLOR_BOTON, br, border_radius=5)
            txt = self.fuente_bold.render(cat, True, COLOR_TEXTO)
            self.pantalla.blit(txt, (br.centerx - txt.get_width()//2, br.centery - txt.get_height()//2))
        
        pygame.draw.rect(self.pantalla, COLOR_PANEL, self.rect_lista, border_radius=8)
        for i, rec in enumerate(self.lista_recursos):
            y = self.rect_lista.y + 5 + i * 25 - self.scroll_lista
            if self.rect_lista.y <= y <= self.rect_lista.bottom - 20:
                is_sel = self.recurso_seleccionado and self.recurso_seleccionado["path"] == rec["path"]
                if is_sel: pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO, (self.rect_lista.x+5, y-2, self.rect_lista.w-10, 22), border_radius=4)
                self.pantalla.blit(self.fuente_ui.render(rec["nombre"][:28], True, (255,255,255) if is_sel else COLOR_TEXTO), (self.rect_lista.x+10, y))
        
        pygame.draw.rect(self.pantalla, (10, 10, 15), self.rect_canvas, border_radius=8)
        if self.img_sheet:
            self.pantalla.blit(self.img_sheet, self.rect_canvas.topleft)
            if not self.frames_grid and self.template_rect:
                tx, ty, tw, th = self.template_rect
                r = pygame.Rect(self.rect_canvas.x + tx, self.rect_canvas.y + ty, tw, th)
                pygame.draw.rect(self.pantalla, COLOR_PLANTILLA, r, 2)
                # Handles
                handles = [(r.topleft, 8), (r.topright, 8), (r.bottomleft, 8), (r.bottomright, 8),
                           (r.midtop, 6), (r.midbottom, 6), (r.midleft, 6), (r.midright, 6)]
                for hpos, size in handles:
                    pygame.draw.rect(self.pantalla, COLOR_PLANTILLA, (hpos[0]-size//2, hpos[1]-size//2, size, size))
            for i, f in enumerate(self.frames_grid):
                fr = pygame.Rect(self.rect_canvas.x + f.x, self.rect_canvas.y + f.y, f.w, f.h)
                if f.usado:
                    s = pygame.Surface((f.w, f.h)); s.set_alpha(150); s.fill((50, 50, 50))
                    self.pantalla.blit(s, fr.topleft)
                pygame.draw.rect(self.pantalla, COLOR_SELECCION if i in self.seleccionados else (100, 100, 120), fr, 1 if i not in self.seleccionados else 3)
                if i in self.seleccionados and len(self.seleccionados) == 1:
                    handles = [(fr.topleft, 8), (fr.topright, 8), (fr.bottomleft, 8), (fr.bottomright, 8),
                               (fr.midtop, 6), (fr.midbottom, 6), (fr.midleft, 6), (fr.midright, 6)]
                    for hpos, size in handles:
                        pygame.draw.rect(self.pantalla, COLOR_SELECCION, (hpos[0]-size//2, hpos[1]-size//2, size, size))
            if self.caja_seleccionando:
                r = pygame.Rect(min(self.caja_inicio[0], self.caja_fin[0]), min(self.caja_inicio[1], self.caja_fin[1]), abs(self.caja_fin[0]-self.caja_inicio[0]), abs(self.caja_fin[1]-self.caja_inicio[1]))
                pygame.draw.rect(self.pantalla, COLOR_SELECCION, r, 2)

        pygame.draw.rect(self.pantalla, COLOR_PANEL, self.rect_panel, border_radius=8)
        if self.seleccionados and self.img_sheet:
            idx = self.seleccionados[(pygame.time.get_ticks()//150) % len(self.seleccionados)]
            sprite = self.img_sheet.subsurface(self.frames_grid[idx].get_rect())
            sw, sh = sprite.get_size()
            scale = min(200/sw, 200/sh)
            sprite = pygame.transform.scale(sprite, (int(sw*scale), int(sh*scale)))
            self.pantalla.blit(sprite, (self.rect_panel.centerx - sprite.get_width()//2, self.rect_panel.y + 100 - sprite.get_height()//2))
        
        px, py = self.rect_panel.x + 10, self.rect_panel.y + 140
        self.pantalla.blit(self.fuente_bold.render("GUARDAR EN:", True, COLOR_TEXTO), (px, py))
        pygame.draw.rect(self.pantalla, COLOR_BOTON, (px, py + 20, 180, 28), border_radius=4)
        self.pantalla.blit(self.fuente_ui.render(self.carpetas_destino[self.idx_carpeta_destino].upper(), True, COLOR_TEXTO), (px + 8, py + 25))
        pygame.draw.rect(self.pantalla, (50, 100, 50), (px + 190, py + 20, 30, 28), border_radius=4)
        self.pantalla.blit(self.fuente_bold.render("+", True, COLOR_TEXTO), (px + 200, py + 24))
        if self.creando_carpeta:
            pygame.draw.rect(self.pantalla, (40, 40, 60), (px, py + 20, 220, 28), border_radius=4)
            self.pantalla.blit(self.fuente_ui.render(self.input_nueva_carpeta + "|", True, COLOR_TEXTO), (px + 8, py + 25))

        py += 60
        self.pantalla.blit(self.fuente_bold.render("PERSONAJE:", True, COLOR_TEXTO), (px, py))
        pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if self.input_activo=="personaje" else COLOR_BOTON, (px, py + 20, 220, 28))
        self.pantalla.blit(self.fuente_ui.render(self.input_personaje, True, COLOR_TEXTO), (px + 5, py + 25))
        py += 60
        self.pantalla.blit(self.fuente_bold.render("ACCIÓN:", True, COLOR_TEXTO), (px, py))
        pygame.draw.rect(self.pantalla, COLOR_BOTON_ACTIVO if self.input_activo=="accion" else COLOR_BOTON, (px, py + 20, 220, 28))
        self.pantalla.blit(self.fuente_ui.render(self.input_accion, True, COLOR_TEXTO), (px + 5, py + 25))
        
        py += 140
        pygame.draw.rect(self.pantalla, (50, 150, 50), (px, py, 220, 40), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("CORTAR TODO", True, COLOR_TEXTO), (px + 25, py + 8))
        py += 50
        pygame.draw.rect(self.pantalla, (50, 120, 50), (px, py, 220, 40), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("GUARDAR", True, COLOR_TEXTO), (px + 50, py + 8))
        py += 50
        pygame.draw.rect(self.pantalla, (120, 50, 50), (px, py, 220, 30), border_radius=5)
        self.pantalla.blit(self.fuente_bold.render("LIMPIAR", True, COLOR_TEXTO), (px + 55, py + 7))
        
        pygame.display.flip()

    def ejecutar(self):
        while self.manejar_eventos():
            self.dibujar()
            self.reloj.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    EditorMaestroSprites().ejecutar()
