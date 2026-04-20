"""Gestor de Objetos Interactivos V1

Base inicial para cofres, puertas y otros objetos seleccionables del mapa.

Rescata la logica ya existente de:
- cofres con llave no consumible,
- inventario especial persistente,
- popup de feedback,
- y cambio visual de estado al abrir.

Modos:
- audit: revisa llaves, cofres y referencias basicas en JSON.
- editor: abre una ventana base para la siguiente iteracion del flujo.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent
DATABASE_DIR = ROOT / "src" / "database"


def cargar_json(path: Path, fallback):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return fallback
    except json.JSONDecodeError as exc:
        print(f"[ERROR] JSON malformado en {path}: {exc}")
        return fallback


class GestorObjetosInteraccionV1:
    def __init__(self) -> None:
        self.items_db: Dict = cargar_json(DATABASE_DIR / "items_db.json", {})
        self.items_especiales_db: Dict = cargar_json(DATABASE_DIR / "items_especiales_db.json", {})
        self.cofres_db: Dict = cargar_json(DATABASE_DIR / "cofres_db.json", {"cofres_mapa": {}})
        self.mapas_dir = DATABASE_DIR / "mapas"
        self.issues: List[str] = []

    def audit(self) -> int:
        print("=== AUDIT OBJETOS INTERACTIVOS V1 ===")
        print(f"Items normales: {len(self.items_db)}")
        print(f"Items especiales: {len(self.items_especiales_db)}")
        cofres_mapa = self.cofres_db.get("cofres_mapa", {}) if isinstance(self.cofres_db, dict) else {}
        print(f"Cofres definidos: {len(cofres_mapa)}")

        llaves_normales = self._collect_keys(self.items_db)
        llaves_especiales = self._collect_keys(self.items_especiales_db)
        llaves_disponibles = sorted(llaves_normales | llaves_especiales)

        print("\nLlaves disponibles:")
        for key in llaves_disponibles:
            print(f"- {key}")

        for cofre_id, cofre_data in cofres_mapa.items():
            if not isinstance(cofre_data, dict):
                self.issues.append(f"Cofre {cofre_id}: registro invalido")
                continue

            req = str(cofre_data.get("requiere_llave", "")).strip()
            if req and req not in llaves_disponibles:
                self.issues.append(f"Cofre {cofre_id}: llave no encontrada -> {req}")

        self._audit_json_mapas()

        print("\nResultado:")
        if self.issues:
            for issue in self.issues:
                print(f"[WARN] {issue}")
            print(f"Total issues: {len(self.issues)}")
            return 1

        print("[OK] Sin issues basicos")
        return 0

    def _collect_keys(self, data: Dict) -> set[str]:
        keys = set()
        for item_id, item_data in data.items():
            if not isinstance(item_data, dict):
                continue
            tipo = str(item_data.get("tipo", "")).strip().lower()
            efecto = str(item_data.get("efecto", "")).strip().upper()
            nombre = str(item_data.get("nombre", item_id)).strip()
            if tipo == "llave" or efecto == "LLAVE" or "llave" in nombre.lower():
                keys.add(item_id)
        return keys

    def _audit_json_mapas(self) -> None:
        if not self.mapas_dir.exists():
            self.issues.append("No existe src/database/mapas")
            return

        for json_path in self.mapas_dir.rglob("*.json"):
            data = cargar_json(json_path, {})
            if not isinstance(data, dict):
                continue
            if "cofres" not in data and "objetos" not in data and "interacciones" not in data:
                continue
            objetos = data.get("cofres", []) or data.get("objetos", []) or data.get("interacciones", [])
            if not isinstance(objetos, list):
                self.issues.append(f"{json_path.name}: lista de objetos invalida")
                continue
            for idx, obj in enumerate(objetos):
                if not isinstance(obj, dict):
                    self.issues.append(f"{json_path.name}: objeto[{idx}] no es dict")
                    continue
                req = str(obj.get("requiere_llave", "")).strip()
                if req and req not in self._collect_keys(self.items_db) | self._collect_keys(self.items_especiales_db):
                    self.issues.append(f"{json_path.name}: objeto[{idx}] requiere llave desconocida -> {req}")

    def _build_global_buttons(self):
        """Botones globales reutilizados para mantener una UX consistente con portales."""
        labels = [
            "Buscar",
            "Enlazar",
            "Desenlazar",
            "Reiniciar",
            "Guardar Dim",
            "Eliminar",
            "Guardar",
            "Intercambiar",
        ]
        buttons = []
        x = 40
        y = 82
        h = 34
        gap = 8
        for label in labels:
            w = 128 if len(label) > 6 else 96
            buttons.append({"label": label, "rect": (x, y, w, h)})
            x += w + gap
        return buttons

    def _discover_image_files(self, base: Path) -> List[Path]:
        if not base.exists():
            return []
        files: List[Path] = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            files.extend(base.glob(ext))
        files.sort(key=lambda p: p.name.lower())
        return files

    def _discover_sprite_files(self, base: Optional[Path] = None) -> List[Path]:
        if base is None:
            base = ROOT / "assets" / "sprites" / "cofres y demas"
        return self._discover_image_files(base)

    def _prompt_directory(self, title: str, initialdir: Optional[Path] = None) -> Optional[Path]:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception:
            return None

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            folder = filedialog.askdirectory(title=title, initialdir=str(initialdir) if initialdir else str(ROOT))
        finally:
            root.destroy()
        if not folder:
            return None
        return Path(folder)

    def _prompt_image_file(self, title: str, initialdir: Optional[Path] = None) -> Optional[Path]:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception:
            return None

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            file_name = filedialog.askopenfilename(
                title=title,
                initialdir=str(initialdir) if initialdir else str(ROOT),
                filetypes=[
                    ("Imagen", "*.png *.jpg *.jpeg *.webp"),
                    ("PNG", "*.png"),
                    ("JPG", "*.jpg *.jpeg"),
                    ("WEBP", "*.webp"),
                    ("Todos", "*.*"),
                ],
            )
        finally:
            root.destroy()
        if not file_name:
            return None
        return Path(file_name)

    def _prompt_json_file(self, title: str, initialdir: Optional[Path] = None) -> Optional[Path]:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception:
            return None

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            file_name = filedialog.askopenfilename(
                title=title,
                initialdir=str(initialdir) if initialdir else str(ROOT),
                filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            )
        finally:
            root.destroy()
        if not file_name:
            return None
        return Path(file_name)

    def _objetos_mapa_dir(self) -> Path:
        return DATABASE_DIR / "objetos_interactivos_mapas"

    def _to_rel_path(self, path: Optional[Path]) -> str:
        if path is None:
            return ""
        try:
            return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
        except Exception:
            return str(path).replace("\\", "/")

    def _from_rel_path(self, raw: str) -> Optional[Path]:
        raw = str(raw or "").strip()
        if not raw:
            return None
        p = Path(raw)
        if p.is_absolute():
            return p
        return ROOT / p

    def _map_id_from_bg(self, current_bg_path: Optional[Path]) -> str:
        if current_bg_path is None:
            return "sin_mapa"
        name = current_bg_path.stem.strip().lower().replace(" ", "_")
        return name or "sin_mapa"

    def _map_json_path(self, map_id: str) -> Path:
        safe_map_id = "".join(ch for ch in map_id if ch.isalnum() or ch in ("_", "-")) or "sin_mapa"
        return self._objetos_mapa_dir() / f"{safe_map_id}.json"

    def _dimension_presets_path(self) -> Path:
        return DATABASE_DIR / "dimension_presets.json"

    def _load_dimension_presets(self) -> List[Dict[str, object]]:
        data = cargar_json(self._dimension_presets_path(), {})
        presets = data.get("presets", []) if isinstance(data, dict) else []
        if isinstance(presets, list):
            return [p for p in presets if isinstance(p, dict)]
        return []

    def _save_dimension_presets(self, presets: List[Dict[str, object]]) -> None:
        payload = {"presets": presets}
        path = self._dimension_presets_path()
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=True, indent=2)

    def _preset_label(self, preset: Dict[str, object]) -> str:
        name = str(preset.get("name") or "preset").strip()
        sprite = Path(str(preset.get("sprite") or "")).name
        w = int(preset.get("w", 0) or 0)
        h = int(preset.get("h", 0) or 0)
        return f"{name} | {sprite} {w}x{h}"

    def _find_dimension_preset(self, presets: List[Dict[str, object]], sprite_path: Path) -> Optional[Dict[str, object]]:
        sprite_key = self._to_rel_path(sprite_path)
        for preset in reversed(presets):
            if str(preset.get("sprite", "")) == sprite_key:
                return preset
        return None

    def _apply_dimension_preset_to_item(self, item: Dict[str, object], preset: Dict[str, object]) -> None:
        rect = item.get("rect")
        if rect is None:
            return
        try:
            w = max(1, int(preset.get("w", rect.w)))
            h = max(1, int(preset.get("h", rect.h)))
            center = rect.center
            rect.size = (w, h)
            rect.center = center
            item["scale"] = float(preset.get("scale", item.get("scale", 1.0)))
        except Exception:
            pass

    def _cycle_render_layer(self, item: Dict[str, object]) -> str:
        layers = ["colision", "detras", "adelante"]
        current = str(item.get("capa_render", "colision")).lower()
        if current not in layers:
            current = "colision"
        next_layer = layers[(layers.index(current) + 1) % len(layers)]
        item["capa_render"] = next_layer
        item["bloquea_paso"] = next_layer == "colision"
        return next_layer

    def _serialize_canvas_item(self, item: Dict[str, object]) -> Dict[str, object]:
        rect = item.get("rect")
        rect_data = {
            "x": int(getattr(rect, "x", 0)),
            "y": int(getattr(rect, "y", 0)),
            "w": int(getattr(rect, "w", 72)),
            "h": int(getattr(rect, "h", 72)),
        }
        return {
            "id": int(item.get("id", 0)),
            "tipo": str(item.get("tipo", "objeto")),
            "label": str(item.get("label", "")),
            "sprite": self._to_rel_path(Path(str(item.get("sprite")))) if item.get("sprite") is not None else "",
            "base_sprite": self._to_rel_path(Path(str(item.get("base_sprite")))) if item.get("base_sprite") is not None else "",
            "linked_sprite": self._to_rel_path(Path(str(item.get("linked_sprite")))) if item.get("linked_sprite") is not None else "",
            "linked_slot": item.get("linked_slot"),
            "trigger_item_id": item.get("trigger_item_id"),
            "requires_button": bool(item.get("requires_button", False)),
            "button_pressed": bool(item.get("button_pressed", False)),
            "is_open": bool(item.get("is_open", False)),
            "link_number": item.get("link_number"),
            "capa_render": str(item.get("capa_render", "colision")),
            "scale": float(item.get("scale", 1.0)),
            "rect": rect_data,
        }

    def _deserialize_canvas_item(self, pygame, data: Dict[str, object]) -> Optional[Dict[str, object]]:
        sprite_path = self._from_rel_path(str(data.get("sprite", "")))
        if sprite_path is None:
            return None

        base_sprite = self._from_rel_path(str(data.get("base_sprite", ""))) or sprite_path
        linked_sprite = self._from_rel_path(str(data.get("linked_sprite", "")))
        rect_data = data.get("rect", {}) if isinstance(data.get("rect"), dict) else {}
        x = int(rect_data.get("x", 0))
        y = int(rect_data.get("y", 0))
        w = int(rect_data.get("w", 72))
        h = int(rect_data.get("h", 72))

        item_id = int(data.get("id", 0))
        item = {
            "id": item_id,
            "tipo": str(data.get("tipo", "objeto")),
            "label": str(data.get("label", "")) or self._build_canvas_label(item_id, sprite_path),
            "sprite": sprite_path,
            "base_sprite": base_sprite,
            "linked_sprite": linked_sprite,
            "linked_slot": data.get("linked_slot"),
            "trigger_item_id": data.get("trigger_item_id"),
            "requires_button": bool(data.get("requires_button", False)),
            "button_pressed": bool(data.get("button_pressed", False)),
            "is_open": bool(data.get("is_open", False)),
            "link_number": data.get("link_number"),
            "capa_render": str(data.get("capa_render", "colision")).lower(),
            "rect": pygame.Rect(x, y, w, h),
            "scale": float(data.get("scale", 1.0)),
        }
        return item

    def _save_editor_state(
        self,
        map_id: str,
        current_bg_path: Optional[Path],
        slot_sprites: Dict[str, List[Path]],
        canvas_items: List[Dict[str, object]],
        canvas_rect=None,
        current_bg_image=None,
    ) -> Path:
        out_dir = self._objetos_mapa_dir()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = self._map_json_path(map_id)

        # Calcular conversión de coordenadas del editor -> coordenadas del mapa (imagen original)
        bg_w = bg_h = None
        canvas_w = canvas_h = None
        canvas_x = canvas_y = 0
        try:
            if current_bg_image is not None:
                bg_w, bg_h = current_bg_image.get_size()
            if canvas_rect is not None:
                canvas_w = int(getattr(canvas_rect, "w", 0))
                canvas_h = int(getattr(canvas_rect, "h", 0))
                canvas_x = int(getattr(canvas_rect, "x", 0))
                canvas_y = int(getattr(canvas_rect, "y", 0))
        except Exception:
            bg_w = bg_h = None

        serialized_items = []
        for item in canvas_items:
            data = self._serialize_canvas_item(item)
            rect_data = data.get("rect") if isinstance(data.get("rect"), dict) else {}
            # map_*: coordenadas relativas al fondo original (para runtime)
            if bg_w and bg_h and canvas_w and canvas_h:
                try:
                    local_x = int(rect_data.get("x", 0)) - canvas_x
                    local_y = int(rect_data.get("y", 0)) - canvas_y
                    local_w = int(rect_data.get("w", 0))
                    local_h = int(rect_data.get("h", 0))

                    map_x = int(round((local_x / max(1, canvas_w)) * bg_w))
                    map_y = int(round((local_y / max(1, canvas_h)) * bg_h))
                    map_w = int(round((local_w / max(1, canvas_w)) * bg_w))
                    map_h = int(round((local_h / max(1, canvas_h)) * bg_h))
                    rect_data["map_x"] = map_x
                    rect_data["map_y"] = map_y
                    rect_data["map_w"] = max(1, map_w)
                    rect_data["map_h"] = max(1, map_h)
                    data["rect"] = rect_data
                except Exception:
                    pass
            serialized_items.append(data)

        payload = {
            "map_id": map_id,
            "background": self._to_rel_path(current_bg_path),
            "slots": {
                "cerrado": self._to_rel_path(slot_sprites["cerrado"][0]) if slot_sprites.get("cerrado") else "",
                "activador": self._to_rel_path(slot_sprites["activador"][0]) if slot_sprites.get("activador") else "",
                "abierto": self._to_rel_path(slot_sprites["abierto"][0]) if slot_sprites.get("abierto") else "",
            },
            "canvas_items": serialized_items,
        }
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=True, indent=2)
        return out_path

    def _load_editor_state(self, pygame, json_path: Path) -> Optional[Dict[str, object]]:
        data = cargar_json(json_path, {})
        if not isinstance(data, dict):
            return None

        slots_raw = data.get("slots", {}) if isinstance(data.get("slots"), dict) else {}
        slot_sprites: Dict[str, List[Path]] = {"cerrado": [], "activador": [], "abierto": []}
        for key in slot_sprites.keys():
            p = self._from_rel_path(str(slots_raw.get(key, "")))
            if p is not None:
                slot_sprites[key] = [p]

        raw_items = data.get("canvas_items", []) if isinstance(data.get("canvas_items"), list) else []
        canvas_items: List[Dict[str, object]] = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            item = self._deserialize_canvas_item(pygame, raw)
            if item is not None:
                canvas_items.append(item)

        bg_path = self._from_rel_path(str(data.get("background", "")))
        return {
            "map_id": str(data.get("map_id", "sin_mapa")),
            "background": bg_path,
            "slots": slot_sprites,
            "canvas_items": canvas_items,
        }

    def _remove_sprite_from_all_slots(self, slot_sprites: Dict[str, List[Path]], sprite_path: Path) -> None:
        for sprites in slot_sprites.values():
            while sprite_path in sprites:
                sprites.remove(sprite_path)

    def _assign_sprite_to_slot(self, slot_sprites: Dict[str, List[Path]], slot_name: str, sprite_path: Path) -> None:
        self._remove_sprite_from_all_slots(slot_sprites, sprite_path)
        slot_sprites[slot_name] = [sprite_path]

    def _sprite_slot_name(self, slot_name: str) -> str:
        if slot_name == "cerrado":
            return "UNO"
        if slot_name == "activador":
            return "DOS"
        return "TRES"

    def _build_canvas_label(self, item_id: int, sprite_path: Path, linked_slot: Optional[str] = None, link_number: Optional[int] = None) -> str:
        base = f"{item_id}. {sprite_path.stem}"
        if linked_slot is None:
            return base
        if link_number is None:
            return f"{base} -> {linked_slot.upper()}"
        return f"{base} -> {linked_slot.upper()} {link_number}"

    def _slot_display_name(self, sprites: List[Path], base_name: str) -> str:
        if not sprites:
            return f"{base_name}: [vacio]"
        if len(sprites) == 1:
            return f"{base_name}: {sprites[0].stem}"
        joined = ",".join([s.stem for s in sprites])
        return f"{base_name}: {joined}"

    def _reset_item_link_state(self, item: Dict[str, object]) -> None:
        base_sprite = item.get("base_sprite")
        if base_sprite is not None:
            item["sprite"] = base_sprite
        item["linked_slot"] = None
        item["linked_sprite"] = None
        item["trigger_item_id"] = None
        item["requires_button"] = False
        item["button_pressed"] = False
        item["is_open"] = False
        item["link_number"] = None
        item["label"] = self._build_canvas_label(int(item["id"]), Path(str(item["sprite"])))

    def _clear_links_by_removed_item(self, canvas_items: List[Dict[str, object]], removed_item_id: int) -> int:
        unlinked = 0
        for item in canvas_items:
            if int(item.get("trigger_item_id") or 0) == removed_item_id:
                self._reset_item_link_state(item)
                unlinked += 1
        return unlinked

    def _load_thumb(self, pygame, cache: Dict[str, object], sprite_path: Path, size: int):
        key = f"{sprite_path}:{size}"
        surf = cache.get(key)
        if surf is not None:
            return surf
        try:
            img = pygame.image.load(str(sprite_path)).convert_alpha()
            surf = pygame.transform.smoothscale(img, (size, size))
        except Exception:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill((90, 70, 70, 255))
            pygame.draw.rect(surf, (220, 180, 180), (0, 0, size, size), 2)
        cache[key] = surf
        return surf

    def editor(self) -> int:
        try:
            import pygame
        except Exception as exc:
            print(f"[ERROR] No se pudo cargar pygame: {exc}")
            return 1

        pygame.init()
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Gestor de Objetos Interactivos V1")
        clock = pygame.time.Clock()
        font_big = pygame.font.Font(None, 48)
        font_med = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 22)
        font_tiny = pygame.font.Font(None, 18)
        font_micro = pygame.font.Font(None, 16)

        buttons = self._build_global_buttons()
        help_visible = True
        selected_button = ""
        status_msg = "Listo. Enlazar: izq cofre, izq boton, der en ABIERTO"
        object_options = ["Puerta", "Cofre", "Boton", "Palanca", "Activador"]
        selected_option = 0

        sprite_library_folder = ROOT / "assets" / "sprites" / "cofres y demas"
        sprite_files = self._discover_sprite_files(sprite_library_folder)
        sprite_index = 0
        sprite_scroll = 0
        thumb_cache: Dict[str, object] = {}

        background_folder = ROOT / "assets" / "backgrounds"
        current_bg_path: Optional[Path] = None
        current_map_id = "sin_mapa"
        current_bg_image = None
        current_bg_surface = None

        slot_sprites: Dict[str, List[Path]] = {"cerrado": [], "activador": [], "abierto": []}
        active_slot = "cerrado"
        active_drag_sprite: Optional[Path] = None
        selected_library_sprite: Optional[Path] = None
        dimension_presets = self._load_dimension_presets()
        preset_scroll = 0
        dragging_from_list = False
        dragging_canvas_index: Optional[int] = None
        drag_offset = (0, 0)
        mouse_pos = (0, 0)
        canvas_items: List[Dict[str, object]] = []
        selected_item_index: Optional[int] = None
        selected_dimension_preset_index: Optional[int] = None
        link_source_item_index: Optional[int] = None
        link_target_item_index: Optional[int] = None
        link_trigger_item_index: Optional[int] = None
        link_mode_active = False
        tab_pressed = False
        next_canvas_id = 1
        slot_link_counts: Dict[str, int] = {"cerrado": 0, "activador": 0, "abierto": 0}
        moving_item = False
        status_hint = "Arrastrar sprites. WASD mover, E interactuar, +/- escalar, rueda en canvas para escala."

        # Estado del héroe para pruebas en canvas
        hero_sprite_path = ROOT / "assets" / "sprites" / "heroes" / "heroe_cloud.png"
        hero_pos = [400, 300]  # Posición inicial que será ajustada luego
        hero_size = 48
        hero_has_key = True

        guide_lines = [
            "FLUJO DE ENLACE (Llave + Sprite Swap)",
            "1. Deja sprite de cofre cerrado en canvas",
            "2. Deja sprite de boton en canvas",
            "3. Asigna sprite ABIERTO en caja superior",
            "4. Enlazar: izq cofre, izq boton, der en caja ABIERTO",
            "5. Con E sobre boton se abre el cofre enlazado",
            "TAB + click derecho: colision / detras / adelante",
            "EXTRA: Eliminar limpia enlaces | +/- o rueda agranda/achica",
            "H: mostrar/ocultar guia | ESC: cerrar",
        ]

        running = True
        while running:
            w, h = screen.get_size()
            side_w = 300
            root_rect = pygame.Rect(16, 16, w - 32, h - 32)
            top_buttons_y = root_rect.y + 42
            
            # Canvas negro GRANDE (trabajo principal) + panel derecho
            canvas_rect = pygame.Rect(root_rect.x + 16, root_rect.y + 128, root_rect.w - side_w - 48, root_rect.h - 146)
            side_rect = pygame.Rect(canvas_rect.right + 16, root_rect.y + 112, side_w, root_rect.h - 130)

            # Botones globales
            x_btn = root_rect.x + 16
            for btn in buttons:
                bx, by, bw, bh = btn["rect"]
                btn["rect"] = (x_btn, top_buttons_y, bw, bh)
                x_btn += bw + 8

            # Tres cuadrados pequeños arriba, junto a la barra superior
            slot_size = 72
            slot_gap = 12
            slots_y = root_rect.y + 36
            slot_start_x = x_btn + 20
            slot_rects = {
                "cerrado": pygame.Rect(slot_start_x, slots_y, slot_size, slot_size),
                "activador": pygame.Rect(slot_start_x + slot_size + slot_gap, slots_y, slot_size, slot_size),
                "abierto": pygame.Rect(slot_start_x + (slot_size + slot_gap) * 2, slots_y, slot_size, slot_size),
            }

            # Panel derecho scrolleable
            # Botón para seleccionar fondo
            bg_btn_rect = pygame.Rect(side_rect.x + 8, side_rect.y + 8, side_w - 24, 28)
            
            # Selector de tipo de objeto
            opt_title_y = side_rect.y + 48
            option_item_h = 24
            options_start_y = opt_title_y + 18
            options_rects = []
            for i, opt in enumerate(object_options):
                options_rects.append((opt, pygame.Rect(side_rect.x + 8, options_start_y + i * option_item_h, side_w - 24, option_item_h - 2)))

            # Lista de sprites scrolleable
            list_title_y = options_start_y + len(object_options) * option_item_h + 8
            content_bottom_limit = side_rect.bottom - 56  # deja espacio para status/footer
            list_y = list_title_y + 20
            list_h = 138
            preview_h = 96
            preset_min_h = 72

            preview_title_y = list_y + list_h + 12
            preview_rect = pygame.Rect(side_rect.x + 8, preview_title_y + 22, side_w - 24, preview_h)
            preset_title_y = preview_rect.bottom + 10
            preset_y = preset_title_y + 20
            preset_h = content_bottom_limit - preset_y

            if preset_h < preset_min_h:
                ajuste = preset_min_h - preset_h
                list_h = max(96, list_h - ajuste)
                preview_title_y = list_y + list_h + 12
                preview_rect = pygame.Rect(side_rect.x + 8, preview_title_y + 22, side_w - 24, preview_h)
                preset_title_y = preview_rect.bottom + 10
                preset_y = preset_title_y + 20
                preset_h = content_bottom_limit - preset_y

            preset_h = max(preset_min_h, preset_h)
            list_rect = pygame.Rect(side_rect.x + 8, list_y, side_w - 24, list_h)
            preset_rect = pygame.Rect(side_rect.x + 8, preset_y, side_w - 24, preset_h)
            preset_row_h = 22
            visible_preset_rows = max(1, preset_rect.h // preset_row_h)
            max_preset_scroll = max(0, len(dimension_presets) - visible_preset_rows)
            preset_scroll = max(0, min(max_preset_scroll, preset_scroll))
            preset_start = preset_scroll
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_TAB:
                        tab_pressed = True
                    elif event.key == pygame.K_h:
                        help_visible = not help_visible
                    elif event.key == pygame.K_UP and sprite_index > 0:
                        sprite_index -= 1
                        if sprite_index < sprite_scroll:
                            sprite_scroll = sprite_index
                    elif event.key == pygame.K_DOWN and sprite_index < max(0, len(sprite_files) - 1):
                        sprite_index += 1
                        visible_rows = max(1, list_rect.h // 28)
                        if sprite_index >= sprite_scroll + visible_rows:
                            sprite_scroll = sprite_index - visible_rows + 1
                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        if selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                            item = canvas_items[selected_item_index]
                            current_scale = float(item.get("scale", 1.0))
                            current_scale = max(0.4, min(2.5, current_scale + 0.1))
                            item["scale"] = current_scale
                            status_msg = f"Escala: {current_scale:.1f}"
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        if selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                            item = canvas_items[selected_item_index]
                            current_scale = float(item.get("scale", 1.0))
                            current_scale = max(0.4, min(2.5, current_scale - 0.1))
                            item["scale"] = current_scale
                            status_msg = f"Escala: {current_scale:.1f}"
                    elif event.key == pygame.K_DELETE:
                        if selected_item_index is None or not (0 <= selected_item_index < len(canvas_items)):
                            status_msg = "Suprimir: selecciona un sprite del canvas primero."
                        else:
                            removed_item = canvas_items.pop(selected_item_index)
                            removed_id = int(removed_item.get("id", -1))
                            unlinked_count = self._clear_links_by_removed_item(canvas_items, removed_id)

                            if link_target_item_index == selected_item_index:
                                link_target_item_index = None
                            if link_trigger_item_index == selected_item_index:
                                link_trigger_item_index = None
                            if link_source_item_index == selected_item_index:
                                link_source_item_index = None

                            # Ajustar indices cuando se elimina un elemento anterior.
                            if link_target_item_index is not None and link_target_item_index > selected_item_index:
                                link_target_item_index -= 1
                            if link_trigger_item_index is not None and link_trigger_item_index > selected_item_index:
                                link_trigger_item_index -= 1
                            if link_source_item_index is not None and link_source_item_index > selected_item_index:
                                link_source_item_index -= 1

                            if not canvas_items:
                                selected_item_index = None
                            else:
                                selected_item_index = min(selected_item_index, len(canvas_items) - 1)

                            status_msg = f"Suprimir: eliminado ID {removed_id}. Enlaces limpiados: {unlinked_count}."
                    elif event.key == pygame.K_e:
                        # Interaccion del heroe
                        hero_rect = pygame.Rect(hero_pos[0], int(hero_pos[1]), hero_size, hero_size)
                        interact_rect = hero_rect.inflate(60, 60)
                        interacted = False
                        for item in reversed(canvas_items):
                            item_rect = item.get("rect")
                            if item_rect and interact_rect.colliderect(item_rect):
                                interacted = True
                                item_tipo = str(item.get("tipo", "")).lower()

                                # Si se interactua con un boton, abre automaticamente los objetivos enlazados.
                                if item_tipo == "boton":
                                    item["button_pressed"] = True
                                    opened_count = 0
                                    for target in canvas_items:
                                        if int(target.get("trigger_item_id") or 0) != int(item["id"]):
                                            continue
                                        if target.get("is_open", False):
                                            continue
                                        linked_sprite = target.get("linked_sprite")
                                        if linked_sprite is None:
                                            continue
                                        target["sprite"] = linked_sprite
                                        target["is_open"] = True
                                        target["linked_slot"] = "abierto"
                                        target["label"] = self._build_canvas_label(
                                            int(target["id"]),
                                            Path(str(target["sprite"])),
                                            "abierto",
                                            target.get("link_number"),
                                        )
                                        opened_count += 1

                                    if opened_count > 0:
                                        status_msg = f"Boton activado: {opened_count} objeto(s) abiertos."
                                    else:
                                        status_msg = "Boton activado, pero no tiene objetivo enlazado."
                                    break

                                if item.get("is_open", False):
                                    status_msg = "El objeto ya esta abierto."
                                    break

                                if item.get("requires_button", False):
                                    status_msg = "Este objeto requiere activar su boton enlazado."
                                    break

                                linked_sprite = item.get("linked_sprite")
                                if linked_sprite is None:
                                    status_msg = "No hay sprite enlazado para ABIERTO."
                                    break

                                if not hero_has_key:
                                    status_msg = "El heroe no tiene la llave necesaria."
                                    break

                                item["sprite"] = linked_sprite
                                item["is_open"] = True
                                item["linked_slot"] = "abierto"
                                item["label"] = self._build_canvas_label(int(item["id"]), Path(str(item["sprite"])), "abierto", item.get("link_number"))
                                status_msg = "Objeto interactuado y abierto."
                                break
                        if not interacted:
                            status_msg = "No hay objetos interactivos cerca."
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_TAB:
                        tab_pressed = False
                elif event.type == pygame.MOUSEWHEEL:
                    mx, my = mouse_pos
                    if list_rect.collidepoint(mx, my):
                        visible_rows = max(1, list_rect.h // 28)
                        sprite_scroll = max(0, min(max(0, len(sprite_files) - visible_rows), sprite_scroll - event.y))
                    elif preset_rect.collidepoint(mx, my):
                        max_preset_scroll = max(0, len(dimension_presets) - visible_preset_rows)
                        preset_scroll = max(0, min(max_preset_scroll, preset_scroll - event.y))
                    elif canvas_rect.collidepoint(mx, my) and selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                        item = canvas_items[selected_item_index]
                        current_scale = float(item.get("scale", 1.0))
                        current_scale = max(0.4, min(2.5, current_scale + (0.1 if event.y > 0 else -0.1)))
                        item["scale"] = current_scale
                        status_msg = f"Escala: {current_scale:.1f}"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    is_left = event.button == 1
                    is_right = event.button == 3

                    # Click en botones globales
                    if is_left:
                        for btn in buttons:
                            bx, by, bw, bh = btn["rect"]
                            if bx <= mx <= bx + bw and by <= my <= by + bh:
                                selected_button = btn["label"]
                                status_msg = f"Boton: {selected_button}"
                                if selected_button == "Buscar":
                                    chosen_folder = self._prompt_directory("Buscar carpeta de sprites", sprite_library_folder)
                                    if chosen_folder is not None:
                                        sprite_library_folder = chosen_folder
                                        sprite_files = self._discover_sprite_files(chosen_folder)
                                        sprite_index = 0
                                        sprite_scroll = 0
                                        status_msg = f"Sprites: {chosen_folder.name} ({len(sprite_files)})"
                                    else:
                                        status_msg = "Busqueda de sprites cancelada"
                                elif selected_button == "Guardar":
                                    current_map_id = self._map_id_from_bg(current_bg_path)
                                    out_path = self._save_editor_state(
                                        current_map_id,
                                        current_bg_path,
                                        slot_sprites,
                                        canvas_items,
                                        canvas_rect=canvas_rect,
                                        current_bg_image=current_bg_image,
                                    )
                                    if current_map_id == "sin_mapa":
                                        status_msg = f"Guardado: {out_path.name} ({len(canvas_items)} objetos) | OJO: no hay fondo seleccionado (sin_mapa)"
                                    else:
                                        status_msg = f"Guardado: {out_path.name} ({len(canvas_items)} objetos) | mapa_id={current_map_id}"
                                elif selected_button == "Intercambiar":
                                    map_dir = self._objetos_mapa_dir()
                                    chosen_json = self._prompt_json_file("Cargar configuracion de mapa", map_dir)
                                    if chosen_json is not None and chosen_json.exists():
                                        loaded = self._load_editor_state(pygame, chosen_json)
                                        if loaded is None:
                                            status_msg = f"No se pudo cargar: {chosen_json.name}"
                                        else:
                                            current_map_id = str(loaded.get("map_id", "sin_mapa"))
                                            slot_sprites = loaded.get("slots", slot_sprites)
                                            canvas_items = loaded.get("canvas_items", canvas_items)
                                            selected_item_index = None
                                            link_source_item_index = None
                                            link_target_item_index = None
                                            link_trigger_item_index = None
                                            link_mode_active = False
                                            next_canvas_id = (max([int(i.get("id", 0)) for i in canvas_items], default=0) + 1)

                                            loaded_bg = loaded.get("background")
                                            if isinstance(loaded_bg, Path) and loaded_bg.exists():
                                                try:
                                                    bg_img = pygame.image.load(str(loaded_bg))
                                                    current_bg_image = bg_img
                                                    current_bg_surface = pygame.transform.smoothscale(bg_img, (canvas_rect.w, canvas_rect.h))
                                                    current_bg_path = loaded_bg
                                                    background_folder = loaded_bg.parent
                                                except Exception:
                                                    pass
                                            status_msg = f"Cargado mapa: {current_map_id}"
                                    else:
                                        status_msg = "Carga de mapa cancelada"
                                elif selected_button == "Enlazar":
                                    link_mode_active = not link_mode_active
                                    if not link_mode_active:
                                        link_source_item_index = None
                                        link_target_item_index = None
                                        link_trigger_item_index = None
                                    status_msg = "Modo enlazar activo: izq objetivo, (opcional) izq boton, der en ABIERTO" if link_mode_active else "Modo enlazar desactivado"
                                elif selected_button == "Reiniciar":
                                    # Reinicia el estado de gameplay/preview en el editor sin borrar enlaces.
                                    # Útil si abriste cofres/botones con E y quieres volver a estado default.
                                    reset_count = 0
                                    for item in canvas_items:
                                        try:
                                            base_sprite = item.get("base_sprite") or item.get("sprite")
                                            if base_sprite is not None:
                                                item["sprite"] = base_sprite
                                            item["is_open"] = False
                                            item["button_pressed"] = False

                                            linked_slot = item.get("linked_slot")
                                            link_number = item.get("link_number")
                                            sprite_for_label = item.get("sprite")
                                            if sprite_for_label is not None:
                                                item["label"] = self._build_canvas_label(
                                                    int(item.get("id", 0)),
                                                    Path(str(sprite_for_label)),
                                                    linked_slot,
                                                    link_number,
                                                )
                                            reset_count += 1
                                        except Exception:
                                            continue
                                    status_msg = f"Reiniciado: {reset_count} objeto(s) a estado cerrado."
                                elif selected_button == "Guardar Dim":
                                    if selected_item_index is None or not (0 <= selected_item_index < len(canvas_items)):
                                        status_msg = "Guardar Dim: selecciona un sprite del canvas primero."
                                    else:
                                        item = canvas_items[selected_item_index]
                                        rect = item.get("rect")
                                        sprite_path = item.get("base_sprite") or item.get("sprite")
                                        if rect is None or sprite_path is None:
                                            status_msg = "Guardar Dim: el item seleccionado no tiene datos validos."
                                        else:
                                            preset_name = f"{Path(str(sprite_path)).stem}_{int(getattr(rect, 'w', 0))}x{int(getattr(rect, 'h', 0))}"
                                            preset = {
                                                "name": preset_name,
                                                "sprite": self._to_rel_path(Path(str(sprite_path))),
                                                "w": int(getattr(rect, "w", 0)),
                                                "h": int(getattr(rect, "h", 0)),
                                                "scale": float(item.get("scale", 1.0)),
                                                "categoria": str(item.get("tipo", "objeto")),
                                                "map_id": current_map_id,
                                            }
                                            dimension_presets.append(preset)
                                            self._save_dimension_presets(dimension_presets)
                                            selected_dimension_preset_index = len(dimension_presets) - 1
                                            status_msg = f"Dimensiones guardadas: {self._preset_label(preset)}"
                                elif selected_button == "Eliminar":
                                    if selected_item_index is None or not (0 <= selected_item_index < len(canvas_items)):
                                        status_msg = "Eliminar: selecciona un sprite del canvas primero."
                                    else:
                                        removed_item = canvas_items.pop(selected_item_index)
                                        removed_id = int(removed_item.get("id", -1))
                                        unlinked_count = self._clear_links_by_removed_item(canvas_items, removed_id)

                                        if link_target_item_index == selected_item_index:
                                            link_target_item_index = None
                                        if link_trigger_item_index == selected_item_index:
                                            link_trigger_item_index = None
                                        if link_source_item_index == selected_item_index:
                                            link_source_item_index = None

                                        # Ajustar indices cuando se elimina un elemento anterior.
                                        if link_target_item_index is not None and link_target_item_index > selected_item_index:
                                            link_target_item_index -= 1
                                        if link_trigger_item_index is not None and link_trigger_item_index > selected_item_index:
                                            link_trigger_item_index -= 1
                                        if link_source_item_index is not None and link_source_item_index > selected_item_index:
                                            link_source_item_index -= 1

                                        if not canvas_items:
                                            selected_item_index = None
                                        else:
                                            selected_item_index = min(selected_item_index, len(canvas_items) - 1)

                                        status_msg = f"Eliminado ID {removed_id}. Enlaces limpiados: {unlinked_count}."
                                else:
                                    link_mode_active = False
                                    link_source_item_index = None
                                    link_target_item_index = None
                                    link_trigger_item_index = None
                                break

                    # Click en cuadrados de estados: seleccionar caja activa
                    if is_left:
                        for slot_name, rect in slot_rects.items():
                            if rect.collidepoint(mx, my):
                                active_slot = slot_name
                                if not link_mode_active:
                                    chosen_sprite = active_drag_sprite or selected_library_sprite
                                    if chosen_sprite is not None:
                                        self._assign_sprite_to_slot(slot_sprites, slot_name, chosen_sprite)
                                        status_msg = f"[{slot_name.upper()}] Sprite asignado: {chosen_sprite.name}"
                                    else:
                                        status_msg = f"Caja activa: {slot_name.upper()}"
                                else:
                                    status_msg = f"Destino de enlace: {slot_name.upper()}"
                                break

                    # Click en tipo de objeto
                    if is_left:
                        for i, (_, opt_rect) in enumerate(options_rects):
                            if opt_rect.collidepoint(mx, my):
                                selected_option = i
                                status_msg = f"Tipo: {object_options[selected_option]}"

                    # Click en lista de sprites
                    if is_left and list_rect.collidepoint(mx, my):
                        local_y = my - list_rect.y
                        row_h = 28
                        row = local_y // row_h
                        idx = sprite_scroll + row
                        if 0 <= idx < len(sprite_files):
                            sprite_index = idx
                            selected_library_sprite = sprite_files[sprite_index]
                            active_drag_sprite = selected_library_sprite
                            dragging_from_list = True
                            status_msg = f"Seleccionado: {selected_library_sprite.name}"

                    # Click en presets de dimension
                    if is_left and preset_rect.collidepoint(mx, my):
                        local_y = my - preset_rect.y
                        row = local_y // preset_row_h
                        idx = preset_start + row
                        if 0 <= idx < len(dimension_presets):
                            selected_dimension_preset_index = idx
                            preset_item = dimension_presets[idx]
                            if selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                                self._apply_dimension_preset_to_item(canvas_items[selected_item_index], preset_item)
                                status_msg = f"Preset aplicado: {self._preset_label(preset_item)}"
                            else:
                                status_msg = f"Preset seleccionado: {self._preset_label(preset_item)}"

                    # Arrastrar item del canvas
                    if is_left and canvas_items:
                        for index in range(len(canvas_items) - 1, -1, -1):
                            item = canvas_items[index]
                            rect = item.get("rect")
                            if rect and rect.collidepoint(mx, my):
                                selected_item_index = index
                                if link_mode_active:
                                    if link_target_item_index is None:
                                        link_target_item_index = index
                                        link_source_item_index = index
                                        status_msg = f"Enlace 1/2 (objetivo): {item['label']}"
                                    elif link_trigger_item_index is None and index != link_target_item_index:
                                        link_trigger_item_index = index
                                        trigger_item = canvas_items[link_trigger_item_index]
                                        status_msg = f"Enlace 2/2 (boton): {trigger_item['label']}"
                                    else:
                                        link_target_item_index = index
                                        link_source_item_index = index
                                        link_trigger_item_index = None
                                        status_msg = f"Reinicio enlace. Objetivo: {item['label']}"
                                else:
                                    moving_item = True
                                    drag_offset = (mx - rect.x, my - rect.y)
                                    status_msg = f"Moviendo: {item['label']}"
                                break

                    # Tab + click derecho: ciclo de capa visual/fisica.
                    if is_right and tab_pressed and not link_mode_active and selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                        item = canvas_items[selected_item_index]
                        new_layer = self._cycle_render_layer(item)
                        status_msg = f"Capa: {new_layer.upper()}"
                        if new_layer != "colision":
                            # Una capa visual no bloquea paso.
                            item["bloquea_paso"] = False

                    # Click derecho en una caja completa el enlace desde la fuente seleccionada
                    if is_right and link_mode_active and not tab_pressed and link_source_item_index is not None:
                        for slot_name, rect in slot_rects.items():
                            if rect.collidepoint(mx, my):
                                if slot_name != "abierto":
                                    status_msg = "Para esta logica el click derecho debe ir en ABIERTO."
                                    break

                                if link_target_item_index is None:
                                    status_msg = "Falta seleccionar: izq sobre el objetivo en el canvas."
                                    break

                                source_item = canvas_items[link_target_item_index]
                                trigger_item = canvas_items[link_trigger_item_index] if link_trigger_item_index is not None else None
                                linked_target_sprite = slot_sprites[slot_name][0] if slot_sprites[slot_name] else None
                                if linked_target_sprite is None:
                                    status_msg = f"La caja {slot_name.upper()} no tiene sprite asignado."
                                    break

                                slot_link_counts[slot_name] += 1
                                source_item["linked_slot"] = slot_name
                                source_item["linked_sprite"] = linked_target_sprite
                                if trigger_item is not None:
                                    source_item["trigger_item_id"] = trigger_item["id"]
                                    source_item["requires_button"] = True
                                else:
                                    source_item["trigger_item_id"] = None
                                    source_item["requires_button"] = False
                                source_item["is_open"] = False
                                source_item["link_number"] = slot_link_counts[slot_name]
                                source_item["label"] = self._build_canvas_label(
                                    int(source_item["id"]),
                                    Path(str(source_item["sprite"])),
                                    slot_name,
                                    slot_link_counts[slot_name],
                                )
                                if trigger_item is not None:
                                    status_msg = f"Enlace aplicado: objetivo {source_item['id']} con boton {trigger_item['id']}"
                                else:
                                    status_msg = f"Enlace aplicado: objetivo {source_item['id']} -> ABIERTO (sin boton)"
                                link_source_item_index = None
                                link_target_item_index = None
                                link_trigger_item_index = None
                                link_mode_active = False
                                selected_button = ""
                                break

                    # Botón de fondo: abre selector de archivo real
                    if is_left and bg_btn_rect.collidepoint(mx, my):
                        chosen_bg = self._prompt_image_file("Seleccionar fondo", background_folder)
                        if chosen_bg is not None:
                            try:
                                bg_img = pygame.image.load(str(chosen_bg))
                                current_bg_image = bg_img
                                current_bg_surface = pygame.transform.smoothscale(bg_img, (canvas_rect.w, canvas_rect.h))
                                current_bg_path = chosen_bg
                                current_map_id = self._map_id_from_bg(current_bg_path)
                                background_folder = chosen_bg.parent
                                # Cargar automaticamente estado JSON del mapa si existe.
                                map_json_path = self._map_json_path(current_map_id)
                                if map_json_path.exists():
                                    loaded = self._load_editor_state(pygame, map_json_path)
                                    if loaded is not None:
                                        slot_sprites = loaded.get("slots", slot_sprites)
                                        canvas_items = loaded.get("canvas_items", canvas_items)
                                        selected_item_index = None
                                        link_source_item_index = None
                                        link_target_item_index = None
                                        link_trigger_item_index = None
                                        link_mode_active = False
                                        next_canvas_id = (max([int(i.get("id", 0)) for i in canvas_items], default=0) + 1)
                                        status_msg = f"Fondo cargado: {chosen_bg.name} | Estado mapa restaurado"
                                    else:
                                        status_msg = f"Fondo cargado: {chosen_bg.name}"
                                else:
                                    # Mapa nuevo: limpiar estado para no mezclar objetos entre mapas.
                                    canvas_items = []
                                    selected_item_index = None
                                    link_source_item_index = None
                                    link_target_item_index = None
                                    link_trigger_item_index = None
                                    link_mode_active = False
                                    next_canvas_id = 1
                                    slot_sprites = {"cerrado": [], "activador": [], "abierto": []}
                                    status_msg = f"Fondo cargado: {chosen_bg.name} | Mapa nuevo sin datos"
                            except Exception as e:
                                status_msg = f"Error cargando fondo: {e}"
                        else:
                            status_msg = "Seleccion de fondo cancelada"

                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    mouse_pos = (mx, my)
                    if moving_item and selected_item_index is not None and 0 <= selected_item_index < len(canvas_items):
                        item = canvas_items[selected_item_index]
                        rect = item["rect"]
                        rect.x = mx - drag_offset[0]
                        rect.y = my - drag_offset[1]
                    elif dragging_from_list and active_drag_sprite is not None:
                        status_hint = f"Arrastrando {active_drag_sprite.name}"

                elif event.type == pygame.MOUSEBUTTONUP:
                    mx, my = event.pos
                    if event.button == 1:
                        if dragging_from_list and active_drag_sprite is not None:
                            dropped = False
                            for slot_name, rect in slot_rects.items():
                                if rect.collidepoint(mx, my):
                                    self._assign_sprite_to_slot(slot_sprites, slot_name, active_drag_sprite)
                                    active_slot = slot_name
                                    status_msg = f"[{slot_name.upper()}] Sprite asignado: {active_drag_sprite.name}"
                                    dropped = True
                                    break
                            if not dropped and canvas_rect.collidepoint(mx, my):
                                item_w = 72
                                item_h = 72
                                preset = self._find_dimension_preset(dimension_presets, active_drag_sprite)
                                if preset is not None:
                                    item_w = max(1, int(preset.get("w", 72)))
                                    item_h = max(1, int(preset.get("h", 72)))
                                item_label = self._build_canvas_label(next_canvas_id, active_drag_sprite)
                                canvas_items.append({
                                    "id": next_canvas_id,
                                    "label": item_label,
                                    "tipo": object_options[selected_option].lower(),
                                    "sprite": active_drag_sprite,
                                    "base_sprite": active_drag_sprite,
                                    "linked_sprite": None,
                                    "trigger_item_id": None,
                                    "requires_button": False,
                                    "button_pressed": False,
                                    "is_open": False,
                                    "capa_render": "colision",
                                    "rect": pygame.Rect(mx - item_w // 2, my - item_h // 2, item_w, item_h),
                                    "scale": 1.0,
                                })
                                next_canvas_id += 1
                                selected_item_index = len(canvas_items) - 1
                                if preset is not None:
                                    self._apply_dimension_preset_to_item(canvas_items[selected_item_index], preset)
                                    status_msg = f"Colocado en canvas: {item_label} | preset {self._preset_label(preset)}"
                                else:
                                    status_msg = f"Colocado en canvas: {item_label}"
                            active_drag_sprite = None
                            dragging_from_list = False
                        moving_item = False

            # ============ ACTUALIZAR HEROE ============
            keys = pygame.key.get_pressed()
            hero_speed = 4
            if keys[pygame.K_w]: hero_pos[1] -= hero_speed
            if keys[pygame.K_s]: hero_pos[1] += hero_speed
            if keys[pygame.K_a]: hero_pos[0] -= hero_speed
            if keys[pygame.K_d]: hero_pos[0] += hero_speed

            # Limitar héroe dentro del canvas
            hero_pos[0] = max(canvas_rect.left, min(hero_pos[0], canvas_rect.right - hero_size))
            hero_pos[1] = max(canvas_rect.top, min(hero_pos[1], canvas_rect.bottom - hero_size))

            # ============ RENDER ============
            screen.fill((18, 20, 28))
            pygame.draw.rect(screen, (35, 40, 55), root_rect, border_radius=16)
            pygame.draw.rect(screen, (110, 160, 255), root_rect, 2, border_radius=16)

            # Título
            title = font_big.render("Gestor de Objetos Interactivos V1", True, (240, 240, 245))
            screen.blit(title, (root_rect.x + 18, root_rect.y + 8))

            # Botones globales
            for btn in buttons:
                bx, by, bw, bh = btn["rect"]
                is_active = btn["label"] == selected_button
                bg = (66, 126, 210) if is_active else (54, 60, 78)
                bd = (150, 195, 255) if is_active else (120, 132, 158)
                pygame.draw.rect(screen, bg, (bx, by, bw, bh), border_radius=6)
                pygame.draw.rect(screen, bd, (bx, by, bw, bh), 1, border_radius=6)
                txt = font_tiny.render(btn["label"], True, (240, 243, 248))
                tx = bx + (bw - txt.get_width()) // 2
                ty = by + (bh - txt.get_height()) // 2
                screen.blit(txt, (tx, ty))

            # Canvas NEGRO (trabajo principal)
            pygame.draw.rect(screen, (10, 10, 15), canvas_rect, border_radius=10)
            pygame.draw.rect(screen, (80, 96, 130), canvas_rect, 1, border_radius=10)

            # Dibujar fondo si existe
            if current_bg_image is not None:
                if current_bg_surface is None or current_bg_surface.get_size() != (canvas_rect.w, canvas_rect.h):
                    current_bg_surface = pygame.transform.smoothscale(current_bg_image, (canvas_rect.w, canvas_rect.h))
                screen.blit(current_bg_surface, canvas_rect)

            if dragging_from_list and active_drag_sprite is not None:
                ghost = self._load_thumb(pygame, thumb_cache, active_drag_sprite, 56)
                ghost_rect = ghost.get_rect(center=mouse_pos)
                screen.blit(ghost, ghost_rect)

            # Dibujar items colocados en el canvas
            for index, item in enumerate(canvas_items):
                sprite_path = item["sprite"]
                rect = item["rect"]
                scale = float(item.get("scale", 1.0))
                size = max(24, int(72 * scale))
                thumb = self._load_thumb(pygame, thumb_cache, sprite_path, size)
                draw_rect = pygame.Rect(rect.x, rect.y, size, size)
                item["rect"] = draw_rect
                screen.blit(thumb, draw_rect)
                if selected_item_index == index or link_source_item_index == index:
                    pygame.draw.rect(screen, (255, 220, 110), draw_rect, 2)
                label_text = font_micro.render(item["label"], True, (235, 238, 245))
                screen.blit(label_text, (draw_rect.x, draw_rect.bottom + 2))
                tipo_tag = str(item.get("tipo", "objeto")).upper()
                tipo_text = font_micro.render(f"TIPO: {tipo_tag}", True, (180, 200, 235))
                screen.blit(tipo_text, (draw_rect.x, draw_rect.bottom + 14))
                capa_render = str(item.get("capa_render", "colision")).upper()
                capa_text = font_micro.render(f"CAPA: {capa_render}", True, (170, 220, 255))
                screen.blit(capa_text, (draw_rect.x, draw_rect.bottom + 26))
                linked_slot = item.get("linked_slot")
                if linked_slot is not None:
                    link_tag = font_micro.render(f"ENLAZADO A {str(linked_slot).upper()}", True, (255, 220, 110))
                    screen.blit(link_tag, (draw_rect.x, draw_rect.bottom + 38))
                if str(item.get("tipo", "")).lower() == "boton":
                    pressed = bool(item.get("button_pressed", False))
                    pressed_txt = "BOTON: ON" if pressed else "BOTON: OFF"
                    pressed_col = (120, 220, 140) if pressed else (220, 160, 120)
                    pressed_tag = font_micro.render(pressed_txt, True, pressed_col)
                    screen.blit(pressed_tag, (draw_rect.x, draw_rect.bottom + 50))

            # Dibujar al héroe
            if hero_sprite_path.exists():
                hero_thumb = self._load_thumb(pygame, thumb_cache, hero_sprite_path, hero_size)
                screen.blit(hero_thumb, (hero_pos[0], hero_pos[1]))
            else:
                # Cuadrado fallback por si no se encuentra el sprite
                pygame.draw.rect(screen, (100, 200, 100), (hero_pos[0], hero_pos[1], hero_size, hero_size))
                pygame.draw.rect(screen, (255, 255, 255), (hero_pos[0], hero_pos[1], hero_size, hero_size), 2)

            # Tres cuadrados de estados
            for slot_name, rect in slot_rects.items():
                active = slot_name == active_slot
                bg = (58, 74, 110) if active else (44, 52, 74)
                bd = (220, 220, 100) if active else (106, 120, 155)
                width = 3 if active else 1
                pygame.draw.rect(screen, bg, rect, border_radius=6)
                pygame.draw.rect(screen, bd, rect, width, border_radius=6)

                label = font_tiny.render(slot_name.upper(), True, (235, 238, 245))
                screen.blit(label, (rect.x + 4, rect.y + 4))
                badge = font_tiny.render(self._sprite_slot_name(slot_name), True, (255, 220, 110))
                screen.blit(badge, (rect.right - badge.get_width() - 4, rect.y + 4))

                # Mostrar último sprite si existe
                sprites = slot_sprites[slot_name]
                if sprites:
                    try:
                        thumb = self._load_thumb(pygame, thumb_cache, sprites[-1], slot_size - 8)
                        screen.blit(thumb, (rect.x + 4, rect.y + 18))
                        sprite_name = font_micro.render(f"{self._sprite_slot_name(slot_name)}: {sprites[-1].stem}", True, (220, 225, 235))
                        screen.blit(sprite_name, (rect.x + 4, rect.bottom - 16))
                    except Exception:
                        pass

            # Etiquetas de nombres fusionados
            closed_name = self._slot_display_name(slot_sprites["cerrado"], "cerrado")
            act_name = self._slot_display_name(slot_sprites["activador"], "activador")
            open_name = self._slot_display_name(slot_sprites["abierto"], "abierto")
            
            name_y = slot_rects["cerrado"].bottom + 6
            screen.blit(font_micro.render(closed_name, True, (200, 200, 200)), (slot_rects["cerrado"].x, name_y))
            screen.blit(font_micro.render(act_name, True, (200, 200, 200)), (slot_rects["activador"].x, name_y))
            screen.blit(font_micro.render(open_name, True, (200, 200, 200)), (slot_rects["abierto"].x, name_y))

            # Panel derecho SCROLLEABLE
            pygame.draw.rect(screen, (26, 29, 40), side_rect, border_radius=10)
            pygame.draw.rect(screen, (86, 106, 148), side_rect, 1, border_radius=10)

            # Botón de fondo
            pygame.draw.rect(screen, (50, 100, 150), bg_btn_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 160, 200), bg_btn_rect, 1, border_radius=5)
            bg_txt = font_micro.render("Buscar Fondo", True, (220, 230, 250))
            screen.blit(bg_txt, (bg_btn_rect.x + 8, bg_btn_rect.y + 6))

            # Tipo de objeto
            opt_title = font_small.render("Tipo:", True, (205, 213, 229))
            screen.blit(opt_title, (side_rect.x + 8, opt_title_y))
            for i, (opt, rect) in enumerate(options_rects):
                active = i == selected_option
                pygame.draw.rect(screen, (62, 96, 155) if active else (44, 49, 67), rect, border_radius=3)
                pygame.draw.rect(screen, (136, 180, 255) if active else (90, 103, 134), rect, 1, border_radius=3)
                t = font_micro.render(opt, True, (236, 239, 246))
                screen.blit(t, (rect.x + 6, rect.y + 3))

            # Vista previa del sprite activo
            preview_title = font_small.render("Vista previa:", True, (205, 213, 229))
            screen.blit(preview_title, (side_rect.x + 8, preview_title_y))
            pygame.draw.rect(screen, (18, 20, 28), preview_rect, border_radius=6)
            pygame.draw.rect(screen, (96, 112, 148), preview_rect, 1, border_radius=6)
            preview_source = active_drag_sprite or selected_library_sprite
            if preview_source is not None:
                preview_thumb = self._load_thumb(pygame, thumb_cache, preview_source, 96)
                screen.blit(preview_thumb, (preview_rect.x + 12, preview_rect.y + 12))
                preview_name = font_micro.render(preview_source.name, True, (230, 234, 242))
                screen.blit(preview_name, (preview_rect.x + 110, preview_rect.y + 18))
            else:
                preview_name = font_micro.render("Sin sprite seleccionado", True, (170, 180, 198))
                screen.blit(preview_name, (preview_rect.x + 12, preview_rect.y + 18))

            # Presets de dimension guardados
            preset_title = font_small.render("Presets de tamano:", True, (205, 213, 229))
            screen.blit(preset_title, (side_rect.x + 8, preset_title_y))
            pygame.draw.rect(screen, (19, 22, 31), preset_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 95, 126), preset_rect, 1, border_radius=5)

            for row in range(visible_preset_rows):
                idx = preset_start + row
                if idx >= len(dimension_presets):
                    break
                preset_item = dimension_presets[idx]
                row_rect = pygame.Rect(preset_rect.x + 4, preset_rect.y + row * preset_row_h + 2, preset_rect.w - 8, preset_row_h - 4)
                active = idx == selected_dimension_preset_index
                pygame.draw.rect(screen, (60, 97, 159) if active else (34, 39, 56), row_rect, border_radius=3)
                if active:
                    pygame.draw.rect(screen, (255, 220, 110), row_rect, 2, border_radius=3)
                row_txt = font_micro.render(self._preset_label(preset_item), True, (234, 238, 247))
                screen.blit(row_txt, (row_rect.x + 6, row_rect.y + 3))

            # Lista de sprites
            list_title = font_small.render("Sprites:", True, (205, 213, 229))
            screen.blit(list_title, (side_rect.x + 8, list_title_y))
            folder_txt = font_micro.render(f"Carpeta: {sprite_library_folder.name}", True, (172, 184, 206))
            screen.blit(folder_txt, (side_rect.x + 8, list_title_y + 18))
            pygame.draw.rect(screen, (19, 22, 31), list_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 95, 126), list_rect, 1, border_radius=5)

            row_h = 28
            visible_rows = max(1, list_rect.h // row_h)
            if sprite_index < sprite_scroll:
                sprite_scroll = sprite_index
            if sprite_index >= sprite_scroll + visible_rows:
                sprite_scroll = sprite_index - visible_rows + 1

            for row in range(visible_rows):
                idx = sprite_scroll + row
                if idx >= len(sprite_files):
                    break
                item_rect = pygame.Rect(list_rect.x + 4, list_rect.y + row * row_h + 2, list_rect.w - 8, row_h - 4)
                active = idx == sprite_index
                pygame.draw.rect(screen, (60, 97, 159) if active else (34, 39, 56), item_rect, border_radius=3)
                sprite_path = sprite_files[idx]
                thumb = self._load_thumb(pygame, thumb_cache, sprite_path, 22)
                screen.blit(thumb, (item_rect.x + 4, item_rect.y + 3))
                name = sprite_path.name
                txt = font_micro.render(name, True, (234, 238, 247))
                screen.blit(txt, (item_rect.x + 32, item_rect.y + 5))
                if selected_library_sprite is not None and sprite_path == selected_library_sprite:
                    pygame.draw.rect(screen, (255, 220, 110), item_rect, 2, border_radius=3)

            # Status
            status = font_small.render(status_msg, True, (190, 205, 235))
            screen.blit(status, (side_rect.x + 8, side_rect.bottom - 28))

            hint = font_micro.render(status_hint, True, (160, 170, 190))
            screen.blit(hint, (canvas_rect.x + 8, canvas_rect.bottom - 18))

            # Help
            if help_visible:
                help_x = canvas_rect.x + 12
                help_y = canvas_rect.y + canvas_rect.h - 180
                help_w = canvas_rect.w - 24
                help_h = 160
                pygame.draw.rect(screen, (29, 34, 48), (help_x, help_y, help_w, help_h), border_radius=8)
                pygame.draw.rect(screen, (100, 150, 220), (help_x, help_y, help_w, help_h), 1, border_radius=8)

                gy = help_y + 10
                for i, line in enumerate(guide_lines):
                    if gy > help_y + help_h - 20:
                        break
                    color = (240, 240, 250) if i == 0 else (200, 210, 230)
                    gtxt = font_micro.render(line, True, color)
                    screen.blit(gtxt, (help_x + 12, gy))
                    gy += 18

            footer = font_tiny.render("H: guia | ESC: cerrar", True, (160, 170, 190))
            screen.blit(footer, (side_rect.x + 8, side_rect.bottom - 8))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gestor de Objetos Interactivos V1")
    parser.add_argument("modo", nargs="?", default="editor", choices=["audit", "editor"], help="Modo de ejecucion")
    args = parser.parse_args()

    gestor = GestorObjetosInteraccionV1()
    if args.modo == "editor":
        return gestor.editor()
    return gestor.audit()


if __name__ == "__main__":
    raise SystemExit(main())
