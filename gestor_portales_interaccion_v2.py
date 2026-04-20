#!/usr/bin/env python3
"""
Gestor Portales + Interaccion V2

Primera version funcional minima y separada del editor antiguo.
Se enfoca en auditar y validar datos de portales/spawns (e interacciones
si existen) en los JSON de mapas.

Uso:
  python gestor_portales_interaccion_v2.py audit
  python gestor_portales_interaccion_v2.py audit --fix
  python gestor_portales_interaccion_v2.py audit --strict
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

MAPS_DIR = Path("src/database/mapas")


@dataclass
class Issue:
    nivel: str  # ERROR | WARN | INFO
    archivo: Path
    mensaje: str


@dataclass
class Stats:
    archivos_ok: int = 0
    archivos_con_errores: int = 0
    archivos_modificados: int = 0
    total_issues: int = 0


class PortalInteraccionAuditV2:
    def __init__(self, maps_dir: Path, strict: bool = False, fix: bool = False):
        self.maps_dir = maps_dir
        self.strict = strict
        self.fix = fix
        self.issues: List[Issue] = []
        self.stats = Stats()
        self._map_file_by_name: Dict[str, Path] = {}
        self._spawn_ids_by_map: Dict[str, set] = {}

    def run(self) -> int:
        if not self.maps_dir.exists():
            print(f"[ERROR] No existe la carpeta de mapas: {self.maps_dir}")
            return 2

        files = sorted(self.maps_dir.rglob("*.json"))
        if not files:
            print(f"[WARN] No se encontraron JSON en: {self.maps_dir}")
            return 1

        # Indices para resolver destinos y validar spawn_destino_id cruzado.
        self._map_file_by_name = {p.stem: p for p in files}
        mapas_disponibles = set(self._map_file_by_name.keys())

        for file_path in files:
            ok, modificado = self._auditar_archivo(file_path, mapas_disponibles)
            if ok:
                self.stats.archivos_ok += 1
            else:
                self.stats.archivos_con_errores += 1
            if modificado:
                self.stats.archivos_modificados += 1

        self._print_reporte()

        # Codigo de salida:
        # 0 = sin errores
        # 1 = con errores o warnings en strict
        if self.stats.archivos_con_errores > 0:
            return 1
        if self.strict and self.stats.total_issues > 0:
            return 1
        return 0

    def _auditar_archivo(self, file_path: Path, mapas_disponibles: set) -> Tuple[bool, bool]:
        modificado = False

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._issue("ERROR", file_path, f"JSON invalido: {exc}")
            return False, False

        if not isinstance(data, dict):
            self._issue("ERROR", file_path, "La raiz del JSON debe ser un objeto")
            return False, False

        portales = data.get("portales", [])
        spawns = data.get("spawns", [])
        interacciones = data.get("interacciones", [])

        if not isinstance(portales, list):
            self._issue("ERROR", file_path, "'portales' debe ser lista")
            return False, False
        if not isinstance(spawns, list):
            self._issue("ERROR", file_path, "'spawns' debe ser lista")
            return False, False
        if interacciones is not None and not isinstance(interacciones, list):
            self._issue("ERROR", file_path, "'interacciones' debe ser lista si existe")
            return False, False

        ok = True

        spawn_ids = set()
        spawn_auto = 1
        for i, spawn in enumerate(spawns):
            if not isinstance(spawn, dict):
                self._issue("ERROR", file_path, f"spawn[{i}] no es objeto")
                ok = False
                continue

            sid = str(spawn.get("id", "")).strip()
            if not sid:
                self._issue("WARN", file_path, f"spawn[{i}] sin id")
                if self.fix:
                    while True:
                        candidate = f"S_AUTO_{spawn_auto}"
                        spawn_auto += 1
                        if candidate not in spawn_ids:
                            sid = candidate
                            spawn["id"] = candidate
                            modificado = True
                            self._issue("INFO", file_path, f"spawn[{i}] id asignado: {candidate}")
                            break
            if sid:
                if sid in spawn_ids:
                    self._issue("ERROR", file_path, f"spawn id duplicado: {sid}")
                    ok = False
                spawn_ids.add(sid)

            if not self._spawn_tiene_posicion(spawn):
                self._issue("ERROR", file_path, f"spawn[{i}] sin coordenadas validas")
                ok = False

        portal_ids = set()
        for i, portal in enumerate(portales):
            if not isinstance(portal, dict):
                self._issue("ERROR", file_path, f"portal[{i}] no es objeto")
                ok = False
                continue

            pid = str(portal.get("id", "")).strip()
            if not pid:
                self._issue("WARN", file_path, f"portal[{i}] sin id")
                if self.fix:
                    pid = f"portal_{file_path.stem}_{i + 1}"
                    portal["id"] = pid
                    modificado = True
                    self._issue("INFO", file_path, f"portal[{i}] id asignado: {pid}")

            if pid:
                if pid in portal_ids:
                    self._issue("ERROR", file_path, f"portal id duplicado: {pid}")
                    ok = False
                portal_ids.add(pid)

            if not self._portal_forma_valida(portal):
                self._issue("ERROR", file_path, f"portal[{i}] forma invalida (rect/poly)")
                ok = False

            destino = str(portal.get("mapa_destino", "")).strip()
            if destino:
                if destino not in mapas_disponibles:
                    self._issue("WARN", file_path, f"portal[{i}] destino no encontrado: {destino}")
                    if self.strict:
                        ok = False
            else:
                # Portal sin destino puede existir en edicion, pero en strict se trata como error.
                self._issue("WARN", file_path, f"portal[{i}] sin mapa_destino")
                if self.strict:
                    ok = False

            sid_dest = str(portal.get("spawn_destino_id", "")).strip()
            if sid_dest and destino:
                spawn_ids_destino = self._get_spawn_ids_for_map(destino)
                if spawn_ids_destino is None:
                    self._issue("WARN", file_path, f"portal[{i}] no se pudo validar spawn_destino_id: mapa destino no legible ({destino})")
                elif sid_dest not in spawn_ids_destino:
                    self._issue("WARN", file_path, f"portal[{i}] spawn_destino_id no existe en mapa destino ({destino}): {sid_dest}")

            # Consistencia optional de caja para rect
            if portal.get("forma") == "rect" and all(k in portal for k in ("x", "y", "w", "h")):
                caja = portal.get("caja")
                rect = {
                    "x": int(portal["x"]),
                    "y": int(portal["y"]),
                    "w": int(portal["w"]),
                    "h": int(portal["h"]),
                }
                if not isinstance(caja, dict) or any(caja.get(k) != rect[k] for k in rect):
                    self._issue("WARN", file_path, f"portal[{i}] caja desincronizada con x/y/w/h")
                    if self.fix:
                        portal["caja"] = rect
                        modificado = True
                        self._issue("INFO", file_path, f"portal[{i}] caja sincronizada")

        for i, inter in enumerate(interacciones or []):
            if not isinstance(inter, dict):
                self._issue("ERROR", file_path, f"interaccion[{i}] no es objeto")
                ok = False
                continue
            accion = str(inter.get("accion", "")).strip()
            if not accion:
                self._issue("WARN", file_path, f"interaccion[{i}] sin accion")
                if self.strict:
                    ok = False

        if modificado:
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        return ok, modificado

    def _spawn_tiene_posicion(self, spawn: Dict) -> bool:
        if "x" in spawn and "y" in spawn:
            return True
        caja = spawn.get("caja")
        if isinstance(caja, dict) and "x" in caja and "y" in caja:
            return True
        return False

    def _get_spawn_ids_for_map(self, map_name: str) -> Optional[set]:
        if map_name in self._spawn_ids_by_map:
            return self._spawn_ids_by_map[map_name]

        mapa_path = self._map_file_by_name.get(map_name)
        if mapa_path is None:
            return None

        try:
            data = json.loads(mapa_path.read_text(encoding="utf-8"))
            spawns = data.get("spawns", []) if isinstance(data, dict) else []
            ids = set()
            for s in spawns:
                if isinstance(s, dict):
                    sid = str(s.get("id", "")).strip()
                    if sid:
                        ids.add(sid)
            self._spawn_ids_by_map[map_name] = ids
            return ids
        except Exception:
            return None

    def _portal_forma_valida(self, portal: Dict) -> bool:
        forma = portal.get("forma", "rect")
        if forma == "poly":
            puntos = portal.get("puntos")
            if not isinstance(puntos, list) or len(puntos) < 3:
                return False
            return True

        # rect por defecto
        if all(k in portal for k in ("x", "y", "w", "h")):
            try:
                return int(portal["w"]) > 0 and int(portal["h"]) > 0
            except Exception:
                return False

        caja = portal.get("caja")
        if isinstance(caja, dict) and all(k in caja for k in ("x", "y", "w", "h")):
            try:
                return int(caja["w"]) > 0 and int(caja["h"]) > 0
            except Exception:
                return False

        return False

    def _issue(self, nivel: str, archivo: Path, mensaje: str) -> None:
        self.issues.append(Issue(nivel=nivel, archivo=archivo, mensaje=mensaje))
        self.stats.total_issues += 1

    def _print_reporte(self) -> None:
        print("=" * 68)
        print("GESTOR PORTALES + INTERACCION V2 :: REPORTE")
        print("=" * 68)

        if not self.issues:
            print("[OK] Sin issues detectados")
        else:
            for issue in self.issues:
                rel = issue.archivo.as_posix()
                print(f"[{issue.nivel}] {rel}: {issue.mensaje}")

        print("-" * 68)
        print(f"Archivos OK: {self.stats.archivos_ok}")
        print(f"Archivos con errores: {self.stats.archivos_con_errores}")
        print(f"Archivos modificados (--fix): {self.stats.archivos_modificados}")
        print(f"Issues totales: {self.stats.total_issues}")
        print("=" * 68)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gestor Portales + Interaccion V2")
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="Audita portales/spawns/interacciones")
    p_audit.add_argument("--strict", action="store_true", help="Trata warnings como fallo")
    p_audit.add_argument("--fix", action="store_true", help="Aplica correcciones seguras")
    p_audit.add_argument("--maps-dir", default=str(MAPS_DIR), help="Ruta de mapas JSON")

    p_editor = sub.add_parser("editor", help="Editor visual minimo de portales")
    p_editor.add_argument("--map", dest="map_name", default=None, help="Nombre base del mapa JSON")
    p_editor.add_argument("--maps-dir", default=str(MAPS_DIR), help="Ruta de mapas JSON")

    return parser


class PortalEditorV2:
    def __init__(self, maps_dir: Path, map_name: Optional[str] = None):
        self.maps_dir = maps_dir
        self.map_name = map_name
        self.map_files = sorted(self.maps_dir.rglob("*.json"))
        if not self.map_files:
            raise FileNotFoundError("No se encontraron mapas JSON en src/database/mapas")

        self.map_names = [p.stem for p in self.map_files]
        self.map_by_name = {p.stem: p for p in self.map_files}

        self.left_map = map_name if map_name in self.map_by_name else self.map_names[0]
        self.right_map = self._pick_default_right(self.left_map)

        self.cache_data: Dict[str, Dict] = {}
        self.cache_surface: Dict[str, pygame.Surface] = {}
        self.cache_portales: Dict[str, List[Dict]] = {}

        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Portales V2 - Doble vista")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_tiny = pygame.font.SysFont(None, 16)

        self.msg = "Botones: Nuevo Izq/Der + Enlazar par ida/vuelta + Guardar"
        self.msg_ttl = 0

        self.sel_side = "left"
        self.sel_idx = {"left": -1, "right": -1}
        self.drag_move = False
        self.drag_side: Optional[str] = None
        self.drag_offset = (0.0, 0.0)

        self.draw_mode_side: Optional[str] = None
        self.drawing_active = False
        self.create_start_map = (0.0, 0.0)
        self.create_now_map = (0.0, 0.0)

        self.link_mode_active = False
        self.link_first: Optional[Tuple[str, int]] = None

        self._buttons: Dict[str, pygame.Rect] = {}
        self._inputs: Dict[str, pygame.Rect] = {}
        self.search_text = {"left": self.left_map, "right": self.right_map}
        self.active_input: Optional[str] = None
        self.is_fullscreen = False
        self.windowed_size = (1280, 720)

        # Demo jugador para probar transiciones de portales en vivo.
        self.player_enabled = True
        self.player_side = "left"
        self.player_x = 0.0
        self.player_y = 0.0
        self.player_w = 20
        self.player_h = 28
        self.player_speed = 220.0
        self.player_portal_cooldown = 0.0
        self.player_exit_lock = False

        # Seleccion / redimensionamiento.
        self.selection_group: List[Tuple[str, int]] = []
        self.resize_active = False
        self.resize_target: Optional[Tuple[str, int]] = None
        self.resize_start = (0.0, 0.0)
        self.resize_originals: Dict[Tuple[str, int], Dict[str, float]] = {}

        self._ensure_map_loaded(self.left_map)
        self._ensure_map_loaded(self.right_map)
        self._reset_player_to_side("left")

    def _pick_default_right(self, left_name: str) -> str:
        for n in self.map_names:
            if n != left_name:
                return n
        return left_name

    def _load_json(self, file_path: Path):
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _find_image_file(self, image_name: str) -> Optional[Path]:
        assets_maps = Path("assets/maps")
        if not assets_maps.exists():
            return None
        for p in assets_maps.rglob(image_name):
            if p.is_file():
                return p
        return None

    def _build_placeholder_surface(self, map_name: str) -> pygame.Surface:
        surf = pygame.Surface((1024, 768))
        c1 = (26, 28, 36)
        c2 = (32, 36, 48)
        tile = 64
        for y in range(0, surf.get_height(), tile):
            for x in range(0, surf.get_width(), tile):
                pygame.draw.rect(surf, c1 if ((x // tile + y // tile) % 2 == 0) else c2, (x, y, tile, tile))

        # Guia visual para que no parezca "vacio"
        for x in range(0, surf.get_width(), 128):
            pygame.draw.line(surf, (55, 62, 80), (x, 0), (x, surf.get_height()), 1)
        for y in range(0, surf.get_height(), 128):
            pygame.draw.line(surf, (55, 62, 80), (0, y), (surf.get_width(), y), 1)

        txt = self.font.render(f"Sin imagen: {map_name}", True, (220, 228, 245))
        txt2 = self.font_small.render("Usa boton ... para elegir mapa por imagen", True, (170, 182, 205))
        surf.blit(txt, (20, 18))
        surf.blit(txt2, (20, 44))
        return surf

    def _load_map_surface(self, map_name: str, map_data: Dict) -> pygame.Surface:
        image_name = str(map_data.get("imagen", "")).strip()
        surf = None
        if image_name:
            img_file = self._find_image_file(image_name)
            if img_file is not None:
                try:
                    surf = pygame.image.load(str(img_file)).convert_alpha()
                except Exception:
                    surf = None

        # Fallback adicional: buscar por nombre de mapa
        if surf is None:
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                probe = self._find_image_file(map_name + ext)
                if probe is not None:
                    try:
                        surf = pygame.image.load(str(probe)).convert_alpha()
                        break
                    except Exception:
                        continue

        if surf is None:
            surf = self._build_placeholder_surface(map_name)
        return surf

    def _normalize_portales(self, map_id: str, raw_portales: List[Dict]) -> List[Dict]:
        out: List[Dict] = []
        for i, p in enumerate(raw_portales):
            if not isinstance(p, dict):
                continue
            if p.get("forma", "rect") != "rect":
                continue

            if all(k in p for k in ("x", "y", "w", "h")):
                x, y, w, h = int(p["x"]), int(p["y"]), int(p["w"]), int(p["h"])
            elif isinstance(p.get("caja"), dict) and all(k in p["caja"] for k in ("x", "y", "w", "h")):
                caja = p["caja"]
                x, y, w, h = int(caja["x"]), int(caja["y"]), int(caja["w"]), int(caja["h"])
            else:
                continue
            if w <= 0 or h <= 0:
                continue

            out.append(
                {
                    "id": str(p.get("id", "")).strip() or f"portal_{map_id}_{i+1}",
                    "tipo": str(p.get("tipo", "portal_enlazado")),
                    "forma": "rect",
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "mapa_destino": str(p.get("mapa_destino", "")).strip(),
                    "spawn_destino_id": str(p.get("spawn_destino_id", "")).strip(),
                    "linked_portal_id": str(p.get("linked_portal_id", "")).strip(),
                    "link_group_id": str(p.get("link_group_id", "")).strip(),
                }
            )
        return out

    def _color_from_link_key(self, key: str) -> Tuple[int, int, int]:
        if not key:
            return (255, 96, 150)
        h = abs(hash(key))
        # Colores vivos pero legibles sobre fondos oscuros
        r = 80 + (h % 140)
        g = 80 + ((h // 7) % 140)
        b = 80 + ((h // 17) % 140)
        return (r, g, b)

    def _link_key_for_portal(self, side: str, portal: Dict) -> str:
        this_map = self.left_map if side == "left" else self.right_map
        this_id = str(portal.get("id", "")).strip()
        other_map = str(portal.get("mapa_destino", "")).strip()
        other_id = str(portal.get("linked_portal_id", "")).strip()
        group = str(portal.get("link_group_id", "")).strip()

        if group:
            return "group:" + group
        if not this_id or not other_map or not other_id:
            return ""

        a = f"{this_map}:{this_id}"
        b = f"{other_map}:{other_id}"
        lo, hi = (a, b) if a <= b else (b, a)
        return lo + "|" + hi

    def _find_partner_index(self, side: str, idx: int) -> Optional[Tuple[str, int]]:
        arr = self._map_portales(side)
        if idx < 0 or idx >= len(arr):
            return None

        portal = arr[idx]
        dest_map = str(portal.get("mapa_destino", "")).strip()
        linked_id = str(portal.get("linked_portal_id", "")).strip()
        if not dest_map or not linked_id:
            return None

        if side == "left" and dest_map != self.right_map:
            return None
        if side == "right" and dest_map != self.left_map:
            return None

        other_side = "right" if side == "left" else "left"
        other_arr = self._map_portales(other_side)
        for j, p in enumerate(other_arr):
            if str(p.get("id", "")).strip() == linked_id:
                return (other_side, j)
        return None

    def _ensure_map_loaded(self, map_name: str):
        if map_name in self.cache_data:
            return
        file_path = self.map_by_name[map_name]
        data = self._load_json(file_path)
        if not isinstance(data, dict):
            data = {}
        data.setdefault("portales", [])
        data.setdefault("spawns", [])

        self.cache_data[map_name] = data
        self.cache_surface[map_name] = self._load_map_surface(map_name, data)
        self.cache_portales[map_name] = self._normalize_portales(map_name, data.get("portales", []))

    def _map_data(self, side: str) -> Dict:
        map_name = self.left_map if side == "left" else self.right_map
        self._ensure_map_loaded(map_name)
        return self.cache_data[map_name]

    def _map_portales(self, side: str) -> List[Dict]:
        map_name = self.left_map if side == "left" else self.right_map
        self._ensure_map_loaded(map_name)
        return self.cache_portales[map_name]

    def _map_surface(self, side: str) -> pygame.Surface:
        map_name = self.left_map if side == "left" else self.right_map
        self._ensure_map_loaded(map_name)
        return self.cache_surface[map_name]

    def _portal_item(self, side: str, idx: int) -> Optional[Dict]:
        arr = self._map_portales(side)
        if 0 <= idx < len(arr):
            return arr[idx]
        return None

    def _portal_index_by_id(self, side: str, portal_id: str) -> Optional[int]:
        portal_id = str(portal_id).strip()
        if not portal_id:
            return None
        for idx, portal in enumerate(self._map_portales(side)):
            if str(portal.get("id", "")).strip() == portal_id:
                return idx
        return None

    def _map_name_by_side(self, side: str) -> str:
        return self.left_map if side == "left" else self.right_map

    def _player_rect_map(self) -> pygame.Rect:
        return pygame.Rect(int(self.player_x), int(self.player_y), self.player_w, self.player_h)

    def _spawns_for_map(self, map_name: str) -> List[Dict]:
        self._ensure_map_loaded(map_name)
        data = self.cache_data[map_name]
        out = []
        for s in data.get("spawns", []):
            if isinstance(s, dict):
                out.append(s)
        return out

    def _spawn_pos_by_id(self, map_name: str, spawn_id: str) -> Optional[Tuple[float, float]]:
        if not spawn_id:
            return None
        for s in self._spawns_for_map(map_name):
            sid = str(s.get("id", "")).strip()
            if sid == spawn_id:
                try:
                    return float(s.get("x", 0)), float(s.get("y", 0))
                except Exception:
                    return None
        return None

    def _selection_contains(self, side: str, idx: int) -> bool:
        return (side, idx) in self.selection_group

    def _selected_portal_for_side(self, side: str) -> Optional[Tuple[int, Dict]]:
        idx = self.sel_idx[side]
        portal = self._portal_item(side, idx)
        if portal is None:
            return None
        return idx, portal

    def _partner_for_portal(self, side: str, idx: int) -> Optional[Tuple[str, int]]:
        return self._find_partner_index(side, idx)

    def _set_selection(self, side: str, idx: int, group: Optional[List[Tuple[str, int]]] = None):
        self.sel_side = side
        self.sel_idx[side] = idx
        self.selection_group = group[:] if group else [(side, idx)]

    def _portal_handle_rect(self, side: str, idx: int, canvas: pygame.Rect) -> Optional[pygame.Rect]:
        surf = self._map_surface(side)
        draw_rect = self._fit_rect(surf, canvas)
        portal = self._portal_item(side, idx)
        if portal is None:
            return None
        rr = self._map_to_screen_rect(side, portal, draw_rect, surf)
        return pygame.Rect(rr.right - 9, rr.bottom - 9, 12, 12)

    def _sync_group_selection_from_partner(self, side: str, idx: int):
        partner = self._partner_for_portal(side, idx)
        if partner is not None:
            self.selection_group = [(side, idx), partner]
        else:
            self.selection_group = [(side, idx)]

    def _reset_player_to_side(self, side: str):
        surf = self._map_surface(side)
        map_name = self._map_name_by_side(side)
        spawns = self._spawns_for_map(map_name)

        self.player_side = side
        if spawns:
            try:
                self.player_x = float(spawns[0].get("x", surf.get_width() // 2))
                self.player_y = float(spawns[0].get("y", surf.get_height() // 2))
            except Exception:
                self.player_x = float(surf.get_width() // 2)
                self.player_y = float(surf.get_height() // 2)
        else:
            self.player_x = float(surf.get_width() // 2)
            self.player_y = float(surf.get_height() // 2)

        self.player_x = max(0.0, min(float(surf.get_width() - self.player_w), self.player_x))
        self.player_y = max(0.0, min(float(surf.get_height() - self.player_h), self.player_y))

    def _move_player_to_destination(self, from_side: str, portal: Dict):
        dest_map = str(portal.get("mapa_destino", "")).strip()
        if not dest_map:
            return

        if from_side == "left":
            if self.right_map != dest_map:
                self._set_side_map("right", dest_map)
            target_side = "right"
        else:
            if self.left_map != dest_map:
                self._set_side_map("left", dest_map)
            target_side = "left"

        # La llegada debe colocarse fuera del contorno del portal destino.
        partner = None
        linked_id = str(portal.get("linked_portal_id", "")).strip()
        if linked_id:
            partner_idx = self._portal_index_by_id(target_side, linked_id)
            if partner_idx is not None:
                partner = (target_side, partner_idx)
        pos = None
        if partner is not None and partner[0] == target_side:
            other = self._map_portales(target_side)[partner[1]]
            surf_dest = self._map_surface(target_side)
            pos = self._compute_spawn_point_near_portal(other, surf_dest)

        if pos is None:
            spawn_id = str(portal.get("spawn_destino_id", "")).strip()
            pos = self._spawn_pos_by_id(dest_map, spawn_id)

        if pos is None:
            surf = self._map_surface(target_side)
            pos = (float(surf.get_width() // 2), float(surf.get_height() // 2))

        self.player_side = target_side
        surf = self._map_surface(target_side)
        self.player_x = max(0.0, min(float(surf.get_width() - self.player_w), float(pos[0])))
        self.player_y = max(0.0, min(float(surf.get_height() - self.player_h), float(pos[1])))
        self.player_portal_cooldown = 0.20
        self.player_exit_lock = True
        self._set_msg(f"Transicion: {self._map_name_by_side(from_side)} -> {dest_map}")

    def _update_player(self, dt: float):
        if not self.player_enabled:
            return

        keys = pygame.key.get_pressed()
        dx = (1 if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) else 0) - (1 if (keys[pygame.K_a] or keys[pygame.K_LEFT]) else 0)
        dy = (1 if (keys[pygame.K_s] or keys[pygame.K_DOWN]) else 0) - (1 if (keys[pygame.K_w] or keys[pygame.K_UP]) else 0)

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.player_x += dx * self.player_speed * dt
        self.player_y += dy * self.player_speed * dt

        surf = self._map_surface(self.player_side)
        self.player_x = max(0.0, min(float(surf.get_width() - self.player_w), self.player_x))
        self.player_y = max(0.0, min(float(surf.get_height() - self.player_h), self.player_y))

        if self.player_portal_cooldown > 0:
            self.player_portal_cooldown = max(0.0, self.player_portal_cooldown - dt)
            return

        player_rect = self._player_rect_map()
        if self.player_exit_lock:
            for p in self._map_portales(self.player_side):
                p_rect = pygame.Rect(int(p["x"]), int(p["y"]), int(p["w"]), int(p["h"]))
                if player_rect.colliderect(p_rect):
                    return
            self.player_exit_lock = False

        arr = self._map_portales(self.player_side)
        for p in arr:
            p_rect = pygame.Rect(int(p["x"]), int(p["y"]), int(p["w"]), int(p["h"]))
            if player_rect.colliderect(p_rect):
                self._move_player_to_destination(self.player_side, p)
                break

    def _set_msg(self, text: str):
        self.msg = text
        self.msg_ttl = 220

    def _canvases(self) -> Dict[str, pygame.Rect]:
        w, h = self.screen.get_size()
        top = 132
        bottom_pad = 14
        gap = 16
        full_w = w - 24
        each_w = max(220, (full_w - gap) // 2)
        height = max(220, h - top - bottom_pad)
        left = pygame.Rect(12, top, each_w, height)
        right = pygame.Rect(12 + each_w + gap, top, each_w, height)
        return {"left": left, "right": right}

    def _fit_rect(self, surf: pygame.Surface, canvas: pygame.Rect) -> pygame.Rect:
        sx = canvas.w / max(1, surf.get_width())
        sy = canvas.h / max(1, surf.get_height())
        s = min(sx, sy)
        draw_w = max(1, int(surf.get_width() * s))
        draw_h = max(1, int(surf.get_height() * s))
        x = canvas.x + (canvas.w - draw_w) // 2
        y = canvas.y + (canvas.h - draw_h) // 2
        return pygame.Rect(x, y, draw_w, draw_h)

    def _map_to_screen_rect(self, side: str, p: Dict, draw_rect: pygame.Rect, surf: pygame.Surface) -> pygame.Rect:
        sx = draw_rect.w / max(1, surf.get_width())
        sy = draw_rect.h / max(1, surf.get_height())
        x = draw_rect.x + int(p["x"] * sx)
        y = draw_rect.y + int(p["y"] * sy)
        w = max(2, int(p["w"] * sx))
        h = max(2, int(p["h"] * sy))
        return pygame.Rect(x, y, w, h)

    def _screen_to_map_point(self, pos: Tuple[int, int], draw_rect: pygame.Rect, surf: pygame.Surface) -> Optional[Tuple[float, float]]:
        x, y = pos
        if not draw_rect.collidepoint(x, y):
            return None
        sx = surf.get_width() / max(1, draw_rect.w)
        sy = surf.get_height() / max(1, draw_rect.h)
        mx = (x - draw_rect.x) * sx
        my = (y - draw_rect.y) * sy
        return (mx, my)

    def _current_selected(self, side: str) -> Optional[Dict]:
        arr = self._map_portales(side)
        idx = self.sel_idx[side]
        if 0 <= idx < len(arr):
            return arr[idx]
        return None

    def _btn(self, key: str, x: int, y: int, w: int, h: int):
        self._buttons[key] = pygame.Rect(x, y, w, h)

    def _draw_button(self, key: str, label: str, enabled: bool = True):
        r = self._buttons[key]
        base = (58, 64, 86) if enabled else (40, 42, 54)
        border = (120, 150, 220) if enabled else (70, 72, 90)
        pygame.draw.rect(self.screen, base, r, border_radius=6)
        pygame.draw.rect(self.screen, border, r, 1, border_radius=6)
        txt = self.font_small.render(label, True, (232, 236, 245) if enabled else (150, 156, 170))
        self.screen.blit(txt, txt.get_rect(center=r.center))

    def _draw_input(self, key: str, placeholder: str):
        r = self._inputs[key]
        focused = self.active_input == key
        pygame.draw.rect(self.screen, (28, 31, 42), r, border_radius=6)
        pygame.draw.rect(self.screen, (120, 190, 255) if focused else (90, 100, 130), r, 2 if focused else 1, border_radius=6)
        value = self.search_text[key].strip()
        label = value if value else placeholder
        color = (235, 238, 245) if value else (150, 158, 175)
        txt = self.font_small.render(label, True, color)
        self.screen.blit(txt, (r.x + 8, r.y + 8))

    def _generate_portal_id(self, map_name: str) -> str:
        existing = {str(p.get("id", "")).strip() for p in self.cache_portales[map_name]}
        i = 1
        while True:
            pid = f"portal_{map_name}_{i}"
            if pid not in existing:
                return pid
            i += 1

    def _generate_spawn_id(self, map_name: str, source_name: str) -> str:
        data = self.cache_data[map_name]
        used = set()
        for s in data.get("spawns", []):
            if isinstance(s, dict):
                sid = str(s.get("id", "")).strip()
                if sid:
                    used.add(sid)
        base = f"S_{map_name}_{source_name}_"
        i = 1
        while True:
            sid = f"{base}{i}"
            if sid not in used:
                return sid
            i += 1

    def _compute_spawn_point_near_portal(self, portal: Dict, surf: pygame.Surface) -> Tuple[int, int]:
        # Para respawn, el PJ debe aparecer centrado dentro del portal.
        x = int(portal["x"] + (portal["w"] - self.player_w) / 2)
        y = int(portal["y"] + (portal["h"] - self.player_h) / 2)

        x = max(0, min(surf.get_width() - self.player_w, x))
        y = max(0, min(surf.get_height() - self.player_h, y))

        return int(x), int(y)

    def _create_spawn_near_portal(self, map_name: str, source_name: str, portal: Dict) -> str:
        data = self.cache_data[map_name]
        spawns = data.setdefault("spawns", [])
        sid = self._generate_spawn_id(map_name, source_name)
        surf = self.cache_surface[map_name]
        cx, cy = self._compute_spawn_point_near_portal(portal, surf)

        spawns.append(
            {
                "id": sid,
                "tipo": "spawn",
                "x": cx,
                "y": cy,
                "direccion": "abajo",
                "tam": 12,
            }
        )
        return sid

    def _sync_partner_spawn_for_portal(self, side: str, idx: int):
        portal = self._portal_item(side, idx)
        if portal is None:
            return

        partner = self._partner_for_portal(side, idx)
        if partner is None:
            return

        partner_side, partner_idx = partner
        partner_portal = self._portal_item(partner_side, partner_idx)
        if partner_portal is None:
            return

        spawn_id = str(partner_portal.get("spawn_destino_id", "")).strip()
        if not spawn_id:
            return

        map_name = self._map_name_by_side(side)
        self._ensure_map_loaded(map_name)
        spawns = self.cache_data[map_name].get("spawns", [])
        target_spawn = None
        for s in spawns:
            if isinstance(s, dict) and str(s.get("id", "")).strip() == spawn_id:
                target_spawn = s
                break

        if target_spawn is None:
            return

        surf = self._map_surface(side)
        px, py = self._compute_spawn_point_near_portal(portal, surf)
        target_spawn["x"] = int(px)
        target_spawn["y"] = int(py)

    def _sync_spawns_for_side(self, side: str):
        for idx, portal in enumerate(self._map_portales(side)):
            if str(portal.get("linked_portal_id", "")).strip() and str(portal.get("spawn_destino_id", "")).strip():
                self._sync_partner_spawn_for_portal(side, idx)

    def _start_resize(self, side: str, idx: int, pos: Tuple[int, int]):
        self.resize_active = True
        self.resize_target = (side, idx)
        self.resize_start = pos
        self.resize_originals = {}
        for g_side, g_idx in self.selection_group or [(side, idx)]:
            portal = self._portal_item(g_side, g_idx)
            if portal is not None:
                self.resize_originals[(g_side, g_idx)] = {
                    "x": float(portal["x"]),
                    "y": float(portal["y"]),
                    "w": float(portal["w"]),
                    "h": float(portal["h"]),
                }

    def _apply_resize(self, side: str, idx: int, pos: Tuple[int, int]):
        if not self.resize_active or self.resize_target is None:
            return

        base_key = self.resize_target
        original = self.resize_originals.get(base_key)
        if original is None:
            return

        surf = self._map_surface(side)
        dx = pos[0] - self.resize_start[0]
        dy = pos[1] - self.resize_start[1]
        new_w = max(8, int(original["w"] + dx))
        new_h = max(8, int(original["h"] + dy))

        # Mantener el anclaje superior izquierdo del portal base.
        for g_side, g_idx in self.selection_group or [(side, idx)]:
            portal = self._portal_item(g_side, g_idx)
            if portal is None:
                continue
            orig = self.resize_originals.get((g_side, g_idx), original)
            portal["x"] = int(orig["x"])
            portal["y"] = int(orig["y"])
            portal["w"] = max(8, min(int(surf.get_width() - portal["x"]), new_w))
            portal["h"] = max(8, min(int(surf.get_height() - portal["y"]), new_h))
            self._sync_partner_spawn_for_portal(g_side, g_idx)

    def _finish_resize(self):
        self.resize_active = False
        self.resize_target = None
        self.resize_start = (0.0, 0.0)
        self.resize_originals = {}

    def _link_selected_pair(self):
        left_portal = self._current_selected("left")
        right_portal = self._current_selected("right")
        if left_portal is None or right_portal is None:
            self._set_msg("Selecciona un portal en IZQ y otro en DER")
            return

        if str(left_portal.get("linked_portal_id", "")).strip() or str(right_portal.get("linked_portal_id", "")).strip():
            self._set_msg("Uno o ambos portales ya estan enlazados. Usa Ctrl+Click IZQ para desenlazar.")
            return

        if not str(left_portal.get("id", "")).strip():
            left_portal["id"] = self._generate_portal_id(self.left_map)
        if not str(right_portal.get("id", "")).strip():
            right_portal["id"] = self._generate_portal_id(self.right_map)

        # Identificador estable del par para coloreo consistente.
        pair_group = f"{self.left_map}:{left_portal['id']}<->{self.right_map}:{right_portal['id']}"

        spawn_right = self._create_spawn_near_portal(self.right_map, self.left_map, right_portal)
        spawn_left = self._create_spawn_near_portal(self.left_map, self.right_map, left_portal)

        left_portal["mapa_destino"] = self.right_map
        left_portal["spawn_destino_id"] = spawn_right
        left_portal["linked_portal_id"] = right_portal["id"]
        left_portal["link_group_id"] = pair_group

        right_portal["mapa_destino"] = self.left_map
        right_portal["spawn_destino_id"] = spawn_left
        right_portal["linked_portal_id"] = left_portal["id"]
        right_portal["link_group_id"] = pair_group

        self._sync_partner_spawn_for_portal("left", self.sel_idx["left"])
        self._sync_partner_spawn_for_portal("right", self.sel_idx["right"])

        self._set_msg("Par enlazado ida/vuelta: al cruzar vuelves por el portal espejo")

    def _unlink_portal_pair(self, side: str, idx: int):
        arr = self._map_portales(side)
        if idx < 0 or idx >= len(arr):
            return

        p = arr[idx]
        dest_map = str(p.get("mapa_destino", "")).strip()
        partner_id = str(p.get("linked_portal_id", "")).strip()

        p["mapa_destino"] = ""
        p["spawn_destino_id"] = ""
        p["linked_portal_id"] = ""
        p["link_group_id"] = ""

        if side == "left" and dest_map == self.right_map and partner_id:
            for q in self._map_portales("right"):
                if str(q.get("id", "")).strip() == partner_id:
                    q["mapa_destino"] = ""
                    q["spawn_destino_id"] = ""
                    q["linked_portal_id"] = ""
                    q["link_group_id"] = ""
                    break
        elif side == "right" and dest_map == self.left_map and partner_id:
            for q in self._map_portales("left"):
                if str(q.get("id", "")).strip() == partner_id:
                    q["mapa_destino"] = ""
                    q["spawn_destino_id"] = ""
                    q["linked_portal_id"] = ""
                    q["link_group_id"] = ""
                    break

        self._set_msg("Par desenlazado. Ambos portales quedan libres.")

    def _new_portal_in_side(self, side: str):
        if self.draw_mode_side == side:
            self.draw_mode_side = None
            self.drawing_active = False
            self._set_msg("Modo dibujo desactivado")
            return

        self.draw_mode_side = side
        self.drawing_active = False
        etiqueta = "IZQ" if side == "left" else "DER"
        self._set_msg(f"Modo dibujo {etiqueta} ON: arrastra para crear todos los portales que quieras")

    def _start_link_mode(self):
        # Evitar conflicto con modo dibujo.
        self.draw_mode_side = None
        self.drawing_active = False

        self.link_mode_active = True
        self.link_first = None
        self._set_msg("Modo enlace ON: Click IZQ en portal izquierdo y Click DER en portal derecho")

    def _finish_link_mode(self):
        self.link_mode_active = False
        self.link_first = None

    def _delete_selected(self):
        arr = self._map_portales(self.sel_side)
        idx = self.sel_idx[self.sel_side]
        if 0 <= idx < len(arr):
            del arr[idx]
            self.sel_idx[self.sel_side] = min(idx, len(arr) - 1)
            self._set_msg("Portal eliminado")

    def _save_all(self):
        self._sync_spawns_for_side("left")
        self._sync_spawns_for_side("right")

        for map_name in (self.left_map, self.right_map):
            data = self.cache_data[map_name]
            portales = self.cache_portales[map_name]
            data["portales"] = [
                {
                    "id": str(p.get("id", "")).strip() or self._generate_portal_id(map_name),
                    "tipo": p.get("tipo", "portal_enlazado"),
                    "forma": "rect",
                    "x": int(p["x"]),
                    "y": int(p["y"]),
                    "w": int(p["w"]),
                    "h": int(p["h"]),
                    "mapa_destino": str(p.get("mapa_destino", "")).strip(),
                    "spawn_destino_id": str(p.get("spawn_destino_id", "")).strip(),
                    "linked_portal_id": str(p.get("linked_portal_id", "")).strip(),
                    "link_group_id": str(p.get("link_group_id", "")).strip(),
                    "caja": {
                        "x": int(p["x"]),
                        "y": int(p["y"]),
                        "w": int(p["w"]),
                        "h": int(p["h"]),
                    },
                }
                for p in portales
            ]

            file_path = self.map_by_name[map_name]
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        self._set_msg("Guardado OK en ambos mapas (izq/der)")

    def _set_side_map(self, side: str, map_name: str):
        if map_name not in self.map_by_name:
            self._set_msg(f"Mapa no existe: {map_name}")
            return
        if side == "left":
            self.left_map = map_name
            self.search_text["left"] = map_name
            self.sel_idx["left"] = -1
        else:
            self.right_map = map_name
            self.search_text["right"] = map_name
            self.sel_idx["right"] = -1
        self._ensure_map_loaded(map_name)
        self._set_msg(f"Mapa {side}: {map_name}")

    def _pick_map_image(self, side: str):
        if tk is None or filedialog is None:
            self._set_msg("Tkinter no disponible para selector de archivos")
            return

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            img_path = filedialog.askopenfilename(
                title="Seleccionar imagen de mapa",
                initialdir=str(Path("assets/maps")),
                filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.webp")],
            )
            root.destroy()
        except Exception:
            self._set_msg("No se pudo abrir selector de imagen")
            return

        if not img_path:
            return

        img_name = Path(img_path).name.lower()
        img_stem = Path(img_path).stem.lower()

        encontrado = None
        for map_name in self.map_names:
            self._ensure_map_loaded(map_name)
            data = self.cache_data[map_name]
            imagen = str(data.get("imagen", "")).strip().lower()
            if imagen and Path(imagen).name.lower() == img_name:
                encontrado = map_name
                break
            if map_name.lower() == img_stem:
                encontrado = map_name
                break

        if encontrado is None:
            self._set_msg(f"No hay JSON vinculado a imagen: {Path(img_path).name}")
            return

        self._set_side_map(side, encontrado)

    def _swap_sides(self):
        self.left_map, self.right_map = self.right_map, self.left_map
        self.search_text["left"] = self.left_map
        self.search_text["right"] = self.right_map
        self.sel_idx["left"] = -1
        self.sel_idx["right"] = -1
        self.sel_side = "left"
        self._set_msg("Mapas intercambiados (izq <-> der)")

    def _cycle_right_map(self, step: int):
        if not self.map_names:
            return
        try:
            idx = self.map_names.index(self.right_map)
        except ValueError:
            idx = 0
        for _ in range(len(self.map_names)):
            idx = (idx + step) % len(self.map_names)
            candidate = self.map_names[idx]
            if candidate != self.left_map:
                self.right_map = candidate
                self._ensure_map_loaded(self.right_map)
                self.search_text["right"] = self.right_map
                self.sel_idx["right"] = -1
                self._set_msg(f"Mapa destino derecho: {self.right_map}")
                return

    def _apply_search(self, side: str):
        text = self.search_text[side].strip().lower()
        if not text:
            return

        candidatos = [n for n in self.map_names if text in n.lower()]
        if not candidatos:
            self._set_msg(f"No se encontro mapa para '{self.search_text[side]}'")
            return

        elegido = candidatos[0]
        if side == "left":
            if elegido == self.right_map and len(candidatos) > 1:
                elegido = candidatos[1]
            self._set_side_map("left", elegido)
        else:
            if elegido == self.left_map and len(candidatos) > 1:
                elegido = candidatos[1]
            self._set_side_map("right", elegido)

    def _toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.windowed_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
            self._set_msg("Pantalla completa: ON")
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            self.is_fullscreen = False
            self._set_msg("Pantalla completa: OFF")

    def _draw_side(self, side: str, canvas: pygame.Rect):
        surf = self._map_surface(side)
        draw_rect = self._fit_rect(surf, canvas)
        if draw_rect.w != surf.get_width() or draw_rect.h != surf.get_height():
            vis = pygame.transform.smoothscale(surf, (draw_rect.w, draw_rect.h))
        else:
            vis = surf
        self.screen.blit(vis, draw_rect)

        partner_highlight = None
        sel_idx = self.sel_idx[side]
        if sel_idx >= 0:
            partner = self._find_partner_index(side, sel_idx)
            if partner is not None:
                partner_highlight = partner

        arr = self._map_portales(side)
        for i, p in enumerate(arr):
            rr = self._map_to_screen_rect(side, p, draw_rect, surf)
            sel = self._selection_contains(side, i)
            link_key = self._link_key_for_portal(side, p)
            linked = bool(link_key)
            base_color = self._color_from_link_key(link_key) if linked else (255, 96, 150)
            color = (255, 214, 80) if sel else base_color

            # Resaltar pareja enlazada del portal seleccionado.
            if partner_highlight is not None and partner_highlight[0] == side and partner_highlight[1] == i:
                color = (255, 214, 80)
                pygame.draw.rect(self.screen, (255, 214, 80), rr.inflate(8, 8), 2)

            pygame.draw.rect(self.screen, color, rr, 2)

            if self.link_mode_active and self.link_first is not None:
                lf_side, lf_idx = self.link_first
                if side == lf_side and i == lf_idx:
                    pygame.draw.rect(self.screen, (80, 230, 255), rr.inflate(6, 6), 2)

            if str(p.get("linked_portal_id", "")).strip():
                pygame.draw.rect(self.screen, (120, 220, 255), rr.inflate(2, 2), 1)

            if sel:
                handle = pygame.Rect(rr.right - 8, rr.bottom - 8, 10, 10)
                pygame.draw.rect(self.screen, (250, 250, 120), handle)
                pygame.draw.rect(self.screen, (20, 20, 20), handle, 1)

            if linked:
                partner = str(p.get("linked_portal_id", "")).strip()
                own_tag = self.font_small.render(str(p.get("id", "portal")), True, color)
                partner_tag = self.font_small.render(partner, True, (220, 240, 255))
                own_x = rr.centerx - own_tag.get_width() // 2
                partner_x = rr.centerx - partner_tag.get_width() // 2
                self.screen.blit(own_tag, (max(0, own_x), max(0, rr.top - own_tag.get_height() - 4)))
                self.screen.blit(partner_tag, (max(0, partner_x), min(self.screen.get_height() - partner_tag.get_height(), rr.bottom + 4)))
            else:
                pid = self.font_small.render(str(p.get("id", "portal")), True, color)
                self.screen.blit(pid, (rr.x + 1, rr.y - 18))

        if self.drawing_active and self.draw_mode_side == side:
            sx, sy = self.create_start_map
            ex, ey = self.create_now_map
            rx = min(sx, ex)
            ry = min(sy, ey)
            rw = abs(ex - sx)
            rh = abs(ey - sy)
            temp = {"x": rx, "y": ry, "w": rw, "h": rh}
            tr = self._map_to_screen_rect(side, temp, draw_rect, surf)
            pygame.draw.rect(self.screen, (100, 220, 255), tr, 2)

        if self.player_enabled and self.player_side == side:
            pr = {"x": self.player_x, "y": self.player_y, "w": self.player_w, "h": self.player_h}
            p_screen = self._map_to_screen_rect(side, pr, draw_rect, surf)
            pygame.draw.rect(self.screen, (110, 220, 255), p_screen)
            pygame.draw.rect(self.screen, (20, 30, 44), p_screen, 2)

        map_name = self.left_map if side == "left" else self.right_map
        titulo = f"Entrada (IZQ): {map_name}" if side == "left" else f"Destino (DER): {map_name}"
        t = self.font.render(titulo, True, (235, 240, 248))
        self.screen.blit(t, (canvas.x + 8, canvas.y - 26))

    def _draw_ui(self):
        self.screen.fill((16, 18, 24))
        canv = self._canvases()
        left = canv["left"]
        right = canv["right"]

        topbar = pygame.Rect(0, 0, self.screen.get_width(), 118)
        pygame.draw.rect(self.screen, (20, 23, 32), topbar)
        pygame.draw.line(self.screen, (55, 64, 90), (0, topbar.bottom), (topbar.w, topbar.bottom), 2)

        pygame.draw.rect(self.screen, (12, 12, 16), left, border_radius=8)
        pygame.draw.rect(self.screen, (12, 12, 16), right, border_radius=8)

        self._draw_side("left", left)
        self._draw_side("right", right)

        linked_visible = False
        for side_name in ("left", "right"):
            sel = self._selected_portal_for_side(side_name)
            if sel is not None and str(sel[1].get("linked_portal_id", "")).strip():
                linked_visible = True
                break

        if linked_visible:
            badge_l = pygame.Rect(left.x + 12, left.y + 10, 220, 30)
            badge_r = pygame.Rect(right.right - 232, right.bottom - 40, 220, 30)
            pygame.draw.rect(self.screen, (20, 110, 140), badge_l, border_radius=6)
            pygame.draw.rect(self.screen, (20, 110, 140), badge_r, border_radius=6)
            pygame.draw.rect(self.screen, (250, 250, 120), badge_l, 2, border_radius=6)
            pygame.draw.rect(self.screen, (250, 250, 120), badge_r, 2, border_radius=6)
            txt_l = self.font_small.render(f"{self.left_map}", True, (255, 255, 210))
            txt_r = self.font_small.render(f"{self.right_map}", True, (255, 255, 210))
            self.screen.blit(txt_l, (badge_l.x + 10, badge_l.y + 7))
            self.screen.blit(txt_r, (badge_r.x + 10, badge_r.y + 7))

        # Botonera superior
        self._buttons = {}
        self._inputs = {}
        y = 12
        x = 12
        bw = 118
        bh = 34
        gap = 8

        self._btn("new_left", x, y, bw, bh); x += bw + gap
        self._btn("new_right", x, y, bw, bh); x += bw + gap
        self._btn("link_pair", x, y, 174, bh); x += 174 + gap
        self._btn("del", x, y, 110, bh); x += 110 + gap
        self._btn("save", x, y, 98, bh); x += 98 + gap
        self._btn("demo_player", x, y, 118, bh); x += 118 + gap
        self._btn("swap", x, y, 150, bh); x += 150 + gap
        self._btn("prev_right", x, y, 34, bh); x += 34 + 4
        self._btn("next_right", x, y, 34, bh); x += 34 + gap

        # Controles de ventana dentro de la app
        wx = self.screen.get_width() - 132
        self._btn("win_min", wx, y, 34, bh)
        self._btn("win_max", wx + 42, y, 34, bh)
        self._btn("win_close", wx + 84, y, 34, bh)

        self._draw_button("new_left", "Dibujar IZQ" if self.draw_mode_side != "left" else "Dibujar IZQ ON")
        self._draw_button("new_right", "Dibujar DER" if self.draw_mode_side != "right" else "Dibujar DER ON")
        self._draw_button("link_pair", "Enlazar par ida/vuelta" if not self.link_mode_active else "Enlace ON (IZQ=LMB DER=RMB)")
        self._draw_button("del", "Eliminar")
        self._draw_button("save", "Guardar")
        self._draw_button("demo_player", "Demo PJ ON" if self.player_enabled else "Demo PJ OFF")
        self._draw_button("swap", "Intercambiar")
        self._draw_button("prev_right", "<")
        self._draw_button("next_right", ">")
        self._draw_button("win_min", "-")
        self._draw_button("win_max", "[]" if not self.is_fullscreen else "o")
        self._draw_button("win_close", "X")

        # Buscadores de mapa
        half_w = max(260, (self.screen.get_width() - 36) // 2)
        input_w = max(140, half_w - 88)
        self._inputs["left"] = pygame.Rect(12, 54, input_w, 30)
        self._inputs["right"] = pygame.Rect(12 + half_w + 12, 54, input_w, 30)
        self._buttons["apply_left"] = pygame.Rect(self._inputs["left"].right + 4, 54, 34, 30)
        self._buttons["pick_left"] = pygame.Rect(self._inputs["left"].right + 42, 54, 42, 30)
        self._buttons["apply_right"] = pygame.Rect(self._inputs["right"].right + 4, 54, 34, 30)
        self._buttons["pick_right"] = pygame.Rect(self._inputs["right"].right + 42, 54, 42, 30)
        self._draw_input("left", "Buscar mapa izquierda y Enter")
        self._draw_input("right", "Buscar mapa derecha y Enter")
        self._draw_button("apply_left", "+")
        self._draw_button("pick_left", "...")
        self._draw_button("apply_right", "+")
        self._draw_button("pick_right", "...")

        hint_l = self.font_tiny.render("Buscador IZQ (mapa entrada)", True, (165, 176, 196))
        hint_r = self.font_tiny.render("Buscador DER (mapa destino)", True, (165, 176, 196))
        self.screen.blit(hint_l, (self._inputs["left"].x + 4, self._inputs["left"].bottom + 4))
        self.screen.blit(hint_r, (self._inputs["right"].x + 4, self._inputs["right"].bottom + 4))

        # Estado
        if self.msg_ttl > 0:
            self.msg_ttl -= 1
        msg = self.font_small.render(self.msg, True, (192, 205, 228))
        self.screen.blit(msg, (12, 96))

        info_y = self.screen.get_height() - 24
        tips = self.font_small.render("Demo PJ: WASD/Flechas. F6 toggle. Click selecciona y arrastra mueve. Esc cierra.", True, (170, 178, 196))
        self.screen.blit(tips, (12, info_y))

        pygame.display.flip()

    def _hit_portal(self, side: str, pos: Tuple[int, int]) -> Optional[int]:
        canv = self._canvases()[side]
        surf = self._map_surface(side)
        draw_rect = self._fit_rect(surf, canv)
        arr = self._map_portales(side)
        for i in range(len(arr) - 1, -1, -1):
            rr = self._map_to_screen_rect(side, arr[i], draw_rect, surf)
            if rr.collidepoint(pos):
                return i
        return None

    def _pick_side_from_pos(self, pos: Tuple[int, int]) -> Optional[str]:
        canv = self._canvases()
        if canv["left"].collidepoint(pos):
            return "left"
        if canv["right"].collidepoint(pos):
            return "right"
        return None

    def _process_button_click(self, pos: Tuple[int, int]) -> bool:
        for key, rect in self._buttons.items():
            if rect.collidepoint(pos):
                if key == "new_left":
                    self._new_portal_in_side("left")
                elif key == "new_right":
                    self._new_portal_in_side("right")
                elif key == "link_pair":
                    self._start_link_mode()
                elif key == "del":
                    self._delete_selected()
                elif key == "save":
                    self._save_all()
                elif key == "demo_player":
                    self.player_enabled = not self.player_enabled
                    if self.player_enabled:
                        self._set_msg("Demo PJ activado")
                    else:
                        self._set_msg("Demo PJ desactivado")
                elif key == "swap":
                    self._swap_sides()
                elif key == "prev_right":
                    self._cycle_right_map(-1)
                elif key == "next_right":
                    self._cycle_right_map(1)
                elif key == "apply_left":
                    self._apply_search("left")
                elif key == "apply_right":
                    self._apply_search("right")
                elif key == "pick_left":
                    self._pick_map_image("left")
                elif key == "pick_right":
                    self._pick_map_image("right")
                elif key == "win_min":
                    pygame.display.iconify()
                elif key == "win_max":
                    self._toggle_fullscreen()
                elif key == "win_close":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return False

    def run(self):
        running = True
        # Dibuja una vez para inicializar rects de botones/inputs antes del primer click.
        self._draw_ui()
        while running:
            canvases = self._canvases()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if event.type == pygame.KEYDOWN:
                    if self.active_input in ("left", "right"):
                        if event.key == pygame.K_ESCAPE:
                            self.active_input = None
                            continue
                        if event.key == pygame.K_RETURN:
                            self._apply_search(self.active_input)
                            self.active_input = None
                            continue
                        if event.key == pygame.K_BACKSPACE:
                            self.search_text[self.active_input] = self.search_text[self.active_input][:-1]
                            continue
                        if event.unicode and event.unicode.isprintable():
                            self.search_text[self.active_input] += event.unicode
                            continue

                    if event.key == pygame.K_ESCAPE:
                        if self.link_mode_active:
                            self._finish_link_mode()
                            self._set_msg("Modo enlace cancelado")
                            continue
                        if self.draw_mode_side is not None:
                            self.draw_mode_side = None
                            self.drawing_active = False
                            self._set_msg("Modo dibujo cancelado")
                            continue
                        running = False
                        continue
                    if event.key == pygame.K_s:
                        self._save_all()
                        continue
                    if event.key == pygame.K_F6:
                        self.player_enabled = not self.player_enabled
                        if self.player_enabled:
                            self._set_msg("Demo PJ activado")
                        else:
                            self._set_msg("Demo PJ desactivado")
                        continue
                    if event.key == pygame.K_DELETE:
                        self._delete_selected()
                        continue

                    sel = self._current_selected(self.sel_side)
                    if sel is not None:
                        step = 1
                        if event.key == pygame.K_LEFT:
                            sel["x"] -= step
                        elif event.key == pygame.K_RIGHT:
                            sel["x"] += step
                        elif event.key == pygame.K_UP:
                            sel["y"] -= step
                        elif event.key == pygame.K_DOWN:
                            sel["y"] += step

                if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                    ctrl_pressed = bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
                    alt_pressed = bool(pygame.key.get_mods() & pygame.KMOD_ALT)

                    # Ctrl+Click IZQ sobre un portal => desenlazar par.
                    if event.button == 1 and ctrl_pressed:
                        side_for_unlink = self._pick_side_from_pos(event.pos)
                        if side_for_unlink is not None:
                            idx_for_unlink = self._hit_portal(side_for_unlink, event.pos)
                            if idx_for_unlink is not None:
                                self.sel_side = side_for_unlink
                                self.sel_idx[side_for_unlink] = idx_for_unlink
                                self._unlink_portal_pair(side_for_unlink, idx_for_unlink)
                                if self.link_mode_active:
                                    self.link_first = None
                                continue

                    # Inputs y botones se manejan con click izquierdo.
                    if event.button == 1:
                        input_hit = None
                        for ikey, irect in self._inputs.items():
                            if irect.collidepoint(event.pos):
                                input_hit = ikey
                                break
                        if input_hit is not None:
                            self.active_input = input_hit
                            continue
                        self.active_input = None

                        if self._process_button_click(event.pos):
                            continue

                    side = self._pick_side_from_pos(event.pos)
                    if side is None:
                        continue

                    surf = self._map_surface(side)
                    draw_rect = self._fit_rect(surf, canvases[side])

                    idx = self._hit_portal(side, event.pos)
                    if idx is not None:
                        portal_here = self._portal_item(side, idx)
                        if portal_here is None:
                            continue

                        # Seleccion normal o grupo con Alt si tiene pareja.
                        if event.button == 1 and alt_pressed:
                            partner = self._partner_for_portal(side, idx)
                            if partner is not None:
                                self._set_selection(side, idx, [(side, idx), partner])
                            else:
                                self._set_selection(side, idx, [(side, idx)])
                        else:
                            self._set_selection(side, idx, [(side, idx)])

                        if self.link_mode_active:
                            if side == "left" and event.button == 1:
                                portal_left = self._map_portales("left")[idx]
                                if str(portal_left.get("linked_portal_id", "")).strip():
                                    self._set_msg("Portal IZQ ya enlazado. Ctrl+Click IZQ para liberarlo.")
                                else:
                                    self.link_first = ("left", idx)
                                    self._set_msg("Portal izquierdo listo. Ahora Click DER en portal derecho.")
                                continue

                            if side == "right" and event.button == 3:
                                if self.link_first is None or self.link_first[0] != "left":
                                    self._set_msg("Primero selecciona portal izquierdo con Click IZQ.")
                                else:
                                    portal_right = self._map_portales("right")[idx]
                                    if str(portal_right.get("linked_portal_id", "")).strip():
                                        self._set_msg("Portal DER ya enlazado. Ctrl+Click IZQ para liberarlo.")
                                    else:
                                        self.sel_idx["left"] = self.link_first[1]
                                        self.sel_idx["right"] = idx
                                        self._link_selected_pair()
                                        self._finish_link_mode()
                                continue

                            self._set_msg("En modo enlace: IZQ con Click IZQ, DER con Click DER")
                            continue

                        # Fuera de modo enlace: mover solo con click izquierdo.
                        if event.button == 1:
                            handle_rect = self._portal_handle_rect(side, idx, canvases[side])
                            if handle_rect is not None and handle_rect.collidepoint(event.pos):
                                self._start_resize(side, idx, event.pos)
                            else:
                                self.drag_move = True
                                self.drag_side = side

                                portal = self._map_portales(side)[idx]
                                pt = self._screen_to_map_point(event.pos, draw_rect, surf)
                                if pt is not None:
                                    self.drag_offset = (pt[0] - portal["x"], pt[1] - portal["y"])
                        continue

                    # Entrar en dibujo solo con click izquierdo.
                    if event.button == 1 and not self.link_mode_active and self.draw_mode_side == side:
                        start = self._screen_to_map_point(event.pos, draw_rect, surf)
                        if start is not None:
                            self.drawing_active = True
                            self.create_start_map = start
                            self.create_now_map = start
                        continue

                if event.type == pygame.MOUSEMOTION:
                    if self.resize_active and self.resize_target is not None:
                        r_side, r_idx = self.resize_target
                        self._apply_resize(r_side, r_idx, event.pos)

                    if self.drawing_active and self.draw_mode_side is not None:
                        side = self.draw_mode_side
                        surf = self._map_surface(side)
                        draw_rect = self._fit_rect(surf, canvases[side])
                        pt = self._screen_to_map_point(event.pos, draw_rect, surf)
                        if pt is not None:
                            self.create_now_map = pt

                    if self.drag_move and self.drag_side is not None:
                        side = self.drag_side
                        idx = self.sel_idx[side]
                        arr = self._map_portales(side)
                        if 0 <= idx < len(arr):
                            surf = self._map_surface(side)
                            draw_rect = self._fit_rect(surf, canvases[side])
                            pt = self._screen_to_map_point(event.pos, draw_rect, surf)
                            if pt is not None:
                                p = arr[idx]
                                nx = int(pt[0] - self.drag_offset[0])
                                ny = int(pt[1] - self.drag_offset[1])
                                nx = max(0, min(surf.get_width() - int(p["w"]), nx))
                                ny = max(0, min(surf.get_height() - int(p["h"]), ny))
                                p["x"] = nx
                                p["y"] = ny
                                self._sync_spawns_for_side(side)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.resize_active:
                        self._finish_resize()

                    if self.drawing_active and self.draw_mode_side is not None:
                        side = self.draw_mode_side
                        surf = self._map_surface(side)
                        arr = self._map_portales(side)

                        x1, y1 = self.create_start_map
                        x2, y2 = self.create_now_map
                        x = int(min(x1, x2))
                        y = int(min(y1, y2))
                        w = int(abs(x2 - x1))
                        h = int(abs(y2 - y1))
                        if w >= 8 and h >= 8:
                            x = max(0, min(surf.get_width() - w, x))
                            y = max(0, min(surf.get_height() - h, y))
                            map_name = self.left_map if side == "left" else self.right_map
                            pid = self._generate_portal_id(map_name)
                            arr.append(
                                {
                                    "id": pid,
                                    "tipo": "portal_enlazado",
                                    "forma": "rect",
                                    "x": x,
                                    "y": y,
                                    "w": w,
                                    "h": h,
                                    "mapa_destino": "",
                                    "spawn_destino_id": "",
                                }
                            )
                            self._set_selection(side, len(arr) - 1, [(side, len(arr) - 1)])
                            self._set_msg(f"Portal creado en {side.upper()}: {pid}")

                        self.drawing_active = False

                    self.drag_move = False
                    self.drag_side = None

            dt = self.clock.tick(60) / 1000.0
            self._update_player(dt)
            self._draw_ui()

        pygame.quit()


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "audit":
        auditor = PortalInteraccionAuditV2(
            maps_dir=Path(args.maps_dir),
            strict=bool(args.strict),
            fix=bool(args.fix),
        )
        return auditor.run()

    if args.command == "editor":
        editor = PortalEditorV2(maps_dir=Path(args.maps_dir), map_name=args.map_name)
        editor.run()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
