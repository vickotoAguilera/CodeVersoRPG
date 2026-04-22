# -*- coding: utf-8 -*-
"""
Gestor NPC Evento Batalla - Canvas Doble (v1)

Incluye:
- Paso 2: selector de mapas.
- Paso 3: asignacion de enemigos/heroes a slots.
- Modo Canvas Batalla XL (temporal) para ajustar cajas con precision.
"""

import json
import os
import sys
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config import DATABASE_PATH, MONSTRUOS_SPRITES_PATH

ANCHO = 1000
ALTO = 680
FPS = 60

COLOR_FONDO = (20, 22, 30)
COLOR_PANEL = (35, 38, 48)
COLOR_BORDE = (90, 100, 120)
COLOR_TEXTO = (220, 225, 235)
COLOR_SEL = (255, 230, 90)
COLOR_SLOT = (58, 64, 78)
COLOR_SLOT_ACTIVO = (88, 120, 88)

MAX_SLOTS = 5

RUTA_LAYOUTS = os.path.join(DATABASE_PATH, "npc_evento_batalla_layouts.json")
RUTA_POR_MAPA = os.path.join(DATABASE_PATH, "npc_evento_batalla_por_mapa")


def _cargar_json(ruta, fallback):
    if not os.path.exists(ruta):
        return fallback
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def _guardar_json(ruta, data):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class EditorNPCEventoBatalla:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Gestor NPC Evento Batalla - Canvas Doble")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.font_sm = pygame.font.Font(None, 18)

        self.running = True

        self.monstruos_db = _cargar_json(os.path.join(DATABASE_PATH, "monstruos_db.json"), {})
        self.layouts_globales = _cargar_json(RUTA_LAYOUTS, {"version": "1.0", "layouts": {}})

        self.mapas = self._listar_mapas()
        self.idx_mapa = 0
        self.mapa_actual = self.mapas[0] if self.mapas else None

        self.cantidad = 3
        self.battle_canvas_xl = False

        self.enemy_slots = []
        self.hero_slots = []
        self.drag_target = None  # ("enemy"|"hero", idx)
        self.drag_offset = (0, 0)

        self.enemy_asignados = [None for _ in range(MAX_SLOTS)]
        self.hero_asignados = [f"HEROE_{i+1}" for i in range(MAX_SLOTS)]

        self.catalogo_monstruos = list(self.monstruos_db.keys()) if self.monstruos_db else []
        self.idx_catalogo = 0

        self.sprites_monstruos = {}
        self._cargar_sprites_monstruos()

        self._cargar_layout_cantidad(self.cantidad)

    def _listar_mapas(self):
        resultado = []
        ruta_unificados = os.path.join(DATABASE_PATH, "mapas_unificados")
        if os.path.exists(ruta_unificados):
            for n in os.listdir(ruta_unificados):
                if n.endswith(".json") and n.startswith("mapa_"):
                    resultado.append(n[:-5])
        resultado.sort()
        return resultado

    def _cargar_sprites_monstruos(self):
        for mid, data in self.monstruos_db.items():
            nombre_sprite = data.get("sprite_archivo", "")
            ruta = os.path.join(MONSTRUOS_SPRITES_PATH, nombre_sprite)
            if not nombre_sprite or not os.path.exists(ruta):
                continue
            try:
                img = pygame.image.load(ruta).convert_alpha()
                s = max(0.15, float(data.get("escala_sprite", 1.0)) * 0.25)
                w = max(20, int(img.get_width() * s))
                h = max(20, int(img.get_height() * s))
                self.sprites_monstruos[mid] = pygame.transform.smoothscale(img, (w, h))
            except Exception:
                pass

    def _canvas_rects(self):
        if self.battle_canvas_xl:
            world = pygame.Rect(10, 10, 280, ALTO - 140)
            battle = pygame.Rect(300, 10, ANCHO - 310, ALTO - 140)
            side = pygame.Rect(ANCHO - 200, 10, 190, ALTO - 140)
        else:
            world = pygame.Rect(10, 10, 420, 420)
            battle = pygame.Rect(440, 10, 420, 420)
            side = pygame.Rect(870, 10, 120, 420)
        return world, battle, side

    def _calc_default_positions(self, cantidad, battle_rect):
        cx_e = battle_rect.x + int(battle_rect.w * 0.72)
        cx_h = battle_rect.x + int(battle_rect.w * 0.28)
        top = battle_rect.y + 80
        h = battle_rect.h - 130

        def ys(n):
            if n <= 1:
                return [top + h // 2]
            step = h // (n - 1)
            return [top + i * step for i in range(n)]

        yvals = ys(cantidad)
        e = [{"x": cx_e, "y": y} for y in yvals]
        hslots = [{"x": cx_h, "y": y} for y in yvals]
        return e, hslots

    def _cargar_layout_cantidad(self, cantidad):
        world, battle, _ = self._canvas_rects()
        _ = world
        data = self.layouts_globales.get("layouts", {}).get(str(cantidad), {})
        e = data.get("enemigos")
        h = data.get("heroes")
        if not e or not h:
            e, h = self._calc_default_positions(cantidad, battle)
        self.enemy_slots = [{"x": int(p["x"]), "y": int(p["y"])} for p in e[:cantidad]]
        self.hero_slots = [{"x": int(p["x"]), "y": int(p["y"])} for p in h[:cantidad]]

    def _guardar_layout_global_actual(self):
        if "layouts" not in self.layouts_globales:
            self.layouts_globales["layouts"] = {}
        self.layouts_globales["layouts"][str(self.cantidad)] = {
            "enemigos": self.enemy_slots,
            "heroes": self.hero_slots,
        }
        _guardar_json(RUTA_LAYOUTS, self.layouts_globales)

    def _guardar_por_mapa(self):
        if not self.mapa_actual:
            return
        ruta = os.path.join(RUTA_POR_MAPA, f"{self.mapa_actual}.json")
        out = {
            "version": "1.0",
            "mapa": self.mapa_actual,
            "cantidad_enemigos": self.cantidad,
            "override_layout": {
                "enemigos": self.enemy_slots,
                "heroes": self.hero_slots,
            },
            "enemigos_asignados": self.enemy_asignados[: self.cantidad],
            "heroes_asignados": self.hero_asignados[: self.cantidad],
        }
        _guardar_json(ruta, out)

    def _slot_rect(self, p):
        return pygame.Rect(int(p["x"] - 24), int(p["y"] - 24), 48, 48)

    def _pick_drag(self, mx, my):
        for i, p in enumerate(self.enemy_slots):
            r = self._slot_rect(p)
            if r.collidepoint(mx, my):
                self.drag_target = ("enemy", i)
                self.drag_offset = (mx - p["x"], my - p["y"])
                return True
        for i, p in enumerate(self.hero_slots):
            r = self._slot_rect(p)
            if r.collidepoint(mx, my):
                self.drag_target = ("hero", i)
                self.drag_offset = (mx - p["x"], my - p["y"])
                return True
        return False

    def _clamp_point_to_rect(self, x, y, rect):
        cx = max(rect.x + 24, min(rect.right - 24, x))
        cy = max(rect.y + 24, min(rect.bottom - 24, y))
        return cx, cy

    def _handle_mouse_motion(self, mx, my):
        if not self.drag_target:
            return
        _, battle_rect, _ = self._canvas_rects()
        nx = mx - self.drag_offset[0]
        ny = my - self.drag_offset[1]
        nx, ny = self._clamp_point_to_rect(nx, ny, battle_rect)
        lado, idx = self.drag_target
        if lado == "enemy":
            self.enemy_slots[idx]["x"] = nx
            self.enemy_slots[idx]["y"] = ny
        else:
            self.hero_slots[idx]["x"] = nx
            self.hero_slots[idx]["y"] = ny

    def _toggle_xl(self):
        self.battle_canvas_xl = not self.battle_canvas_xl
        # Recalcular defaults solo si no hay cambios manuales persistidos
        self._cargar_layout_cantidad(self.cantidad)

    def _asignar_actual_a_slot_libre(self):
        if not self.catalogo_monstruos:
            return
        mid = self.catalogo_monstruos[self.idx_catalogo]
        for i in range(self.cantidad):
            if self.enemy_asignados[i] is None:
                self.enemy_asignados[i] = mid
                return
        self.enemy_asignados[0] = mid

    def handle_input(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif ev.key == pygame.K_f:
                    self._toggle_xl()
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if self.mapas:
                        self.idx_mapa = max(0, self.idx_mapa - 1)
                        self.mapa_actual = self.mapas[self.idx_mapa]
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if self.mapas:
                        self.idx_mapa = min(len(self.mapas) - 1, self.idx_mapa + 1)
                        self.mapa_actual = self.mapas[self.idx_mapa]
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.cantidad = max(1, self.cantidad - 1)
                    self._cargar_layout_cantidad(self.cantidad)
                elif ev.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.cantidad = min(MAX_SLOTS, self.cantidad + 1)
                    self._cargar_layout_cantidad(self.cantidad)
                elif ev.key == pygame.K_LEFT:
                    if self.catalogo_monstruos:
                        self.idx_catalogo = (self.idx_catalogo - 1) % len(self.catalogo_monstruos)
                elif ev.key == pygame.K_RIGHT:
                    if self.catalogo_monstruos:
                        self.idx_catalogo = (self.idx_catalogo + 1) % len(self.catalogo_monstruos)
                elif ev.key == pygame.K_SPACE:
                    self._asignar_actual_a_slot_libre()
                elif ev.key == pygame.K_g:
                    self._guardar_layout_global_actual()
                elif ev.key == pygame.K_RETURN:
                    self._guardar_por_mapa()
                elif ev.key == pygame.K_BACKSPACE:
                    self.enemy_asignados = [None for _ in range(MAX_SLOTS)]

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._pick_drag(*ev.pos)

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.drag_target = None

            elif ev.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(*ev.pos)

    def _draw_world_panel(self, rect):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect)
        pygame.draw.rect(self.screen, COLOR_BORDE, rect, 2)
        self.screen.blit(self.font.render("Canvas Mundo", True, COLOR_TEXTO), (rect.x + 8, rect.y + 8))

        self.screen.blit(self.font_sm.render("Mapas (W/S o Flechas)", True, COLOR_TEXTO), (rect.x + 8, rect.y + 38))
        y = rect.y + 62
        start = max(0, self.idx_mapa - 6)
        end = min(len(self.mapas), start + 12)
        for i in range(start, end):
            col = COLOR_SEL if i == self.idx_mapa else COLOR_TEXTO
            txt = self.mapas[i]
            self.screen.blit(self.font_sm.render(txt, True, col), (rect.x + 10, y))
            y += 18

    def _draw_battle_panel(self, rect):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect)
        pygame.draw.rect(self.screen, COLOR_BORDE, rect, 2)

        modo = "XL" if self.battle_canvas_xl else "Normal"
        titulo = f"Canvas Batalla ({modo}) - Cantidad: {self.cantidad}"
        self.screen.blit(self.font.render(titulo, True, COLOR_TEXTO), (rect.x + 8, rect.y + 8))

        self.screen.blit(self.font_sm.render("Arrastra cajas para posicionar", True, COLOR_TEXTO), (rect.x + 8, rect.y + 34))

        for i in range(self.cantidad):
            p = self.enemy_slots[i]
            r = self._slot_rect(p)
            pygame.draw.rect(self.screen, COLOR_SLOT_ACTIVO if self.enemy_asignados[i] else COLOR_SLOT, r)
            pygame.draw.rect(self.screen, COLOR_BORDE, r, 2)
            self.screen.blit(self.font_sm.render(f"E{i+1}", True, COLOR_TEXTO), (r.x + 14, r.y + 16))

            asignado = self.enemy_asignados[i]
            if asignado and asignado in self.sprites_monstruos:
                spr = self.sprites_monstruos[asignado]
                self.screen.blit(spr, (r.x + 52, r.y - 2))

        for i in range(self.cantidad):
            p = self.hero_slots[i]
            r = self._slot_rect(p)
            pygame.draw.rect(self.screen, COLOR_SLOT_ACTIVO, r)
            pygame.draw.rect(self.screen, COLOR_BORDE, r, 2)
            self.screen.blit(self.font_sm.render(f"H{i+1}", True, COLOR_TEXTO), (r.x + 14, r.y + 16))

    def _draw_side_panel(self, rect):
        pygame.draw.rect(self.screen, COLOR_PANEL, rect)
        pygame.draw.rect(self.screen, COLOR_BORDE, rect, 2)

        self.screen.blit(self.font.render("Catalogo", True, COLOR_TEXTO), (rect.x + 8, rect.y + 8))
        if self.catalogo_monstruos:
            mid = self.catalogo_monstruos[self.idx_catalogo]
            self.screen.blit(self.font_sm.render("Monstruo actual:", True, COLOR_TEXTO), (rect.x + 8, rect.y + 36))
            self.screen.blit(self.font_sm.render(mid, True, COLOR_SEL), (rect.x + 8, rect.y + 54))
        else:
            self.screen.blit(self.font_sm.render("Sin monstruos", True, COLOR_TEXTO), (rect.x + 8, rect.y + 38))

    def _draw_bottom_bar(self):
        r = pygame.Rect(0, ALTO - 120, ANCHO, 120)
        pygame.draw.rect(self.screen, (30, 33, 42), r)
        pygame.draw.line(self.screen, COLOR_BORDE, (0, ALTO - 120), (ANCHO, ALTO - 120), 2)

        hints = [
            "F: Canvas Batalla XL ON/OFF",
            "W/S o Flechas: cambiar mapa",
            "+/-: cantidad enemigos (1-5)",
            "Left/Right: cambiar monstruo catalogo",
            "Space: asignar monstruo actual a slot libre",
            "Drag mouse: mover cajas E/H",
            "G: guardar layout global | Enter: guardar por mapa",
        ]
        y = ALTO - 112
        for t in hints:
            self.screen.blit(self.font_sm.render(t, True, COLOR_TEXTO), (10, y))
            y += 15

    def draw(self):
        self.screen.fill(COLOR_FONDO)
        world, battle, side = self._canvas_rects()
        self._draw_world_panel(world)
        self._draw_battle_panel(battle)
        self._draw_side_panel(side)
        self._draw_bottom_bar()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    EditorNPCEventoBatalla().run()
