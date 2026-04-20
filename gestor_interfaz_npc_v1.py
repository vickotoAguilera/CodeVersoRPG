from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.npc_comercio_herrero import ejecutar_accion_panel, opciones_panel_por_modo
from src.npc_eventos_batalla import resolver_evento_npc


def prompt_directory(title: str, initial_dir: Path) -> Optional[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        folder = filedialog.askdirectory(title=title, initialdir=str(initial_dir))
    finally:
        root.destroy()
    if not folder:
        return None
    return Path(folder)


def prompt_file(title: str, initial_dir: Path, patterns: str) -> Optional[Path]:
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
            initialdir=str(initial_dir),
            filetypes=[("Archivos", patterns), ("Todos", "*.*")],
        )
    finally:
        root.destroy()
    if not file_name:
        return None
    return Path(file_name)


def prompt_text(title: str, prompt: str, initial_value: str = "") -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import simpledialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        value = simpledialog.askstring(title, prompt, initialvalue=initial_value, parent=root)
    finally:
        root.destroy()
    return value


class GestorInterfazNPCV1:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parent
        self.npc_maps_dir = self.root / "src" / "database" / "npc_interactivos_mapas"
        self.npc_maps_dir.mkdir(parents=True, exist_ok=True)
        self.npc_dim_presets_path = self.root / "src" / "database" / "npc_dimension_presets.json"
        self.npc_ui_defaults_path = self.root / "src" / "database" / "npc_ui_defaults.json"

        self.sprite_folder = self.root / "assets" / "sprites" / "npcs"
        if not self.sprite_folder.exists():
            self.sprite_folder = self.root / "assets" / "sprites"

        self.background_folder = self.root / "assets" / "maps"
        if not self.background_folder.exists():
            self.background_folder = self.root / "assets"

    def _discover_images(self, folder: Path) -> List[Path]:
        if not folder.exists():
            return []
        files: List[Path] = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            files.extend(folder.rglob(ext))
        files.sort(key=lambda p: p.name.lower())
        return files

    def _to_rel(self, p: Optional[Path]) -> str:
        if p is None:
            return ""
        try:
            return str(p.resolve().relative_to(self.root.resolve())).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")

    def _from_rel(self, raw: str) -> Optional[Path]:
        raw = str(raw or "").strip()
        if not raw:
            return None
        p = Path(raw)
        if p.is_absolute():
            return p
        return self.root / p

    def _map_id(self, bg: Optional[Path]) -> str:
        if bg is None:
            return "sin_mapa"
        return bg.stem.strip().lower().replace(" ", "_") or "sin_mapa"

    def _load_dimension_presets(self) -> List[Dict[str, object]]:
        try:
            data = json.loads(self.npc_dim_presets_path.read_text(encoding="utf-8"))
        except Exception:
            return []
        presets = data.get("presets", []) if isinstance(data, dict) else []
        if not isinstance(presets, list):
            return []
        return [p for p in presets if isinstance(p, dict)]

    def _save_dimension_presets(self, presets: List[Dict[str, object]]) -> None:
        payload = {"presets": presets}
        self.npc_dim_presets_path.parent.mkdir(parents=True, exist_ok=True)
        self.npc_dim_presets_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _default_dialog_window_cfg(self) -> Dict[str, object]:
        return {"w": 760, "h": 130, "x": 0, "y": 0, "use_default": True}

    def _default_panel_window_cfg(self) -> Dict[str, object]:
        return {"w": 220, "h": 170, "x": 0, "y": 0, "use_default": True}

    def _normalize_dialog_window_cfg(self, raw_cfg, default_cfg: Dict[str, object]) -> Dict[str, object]:
        base = default_cfg if isinstance(default_cfg, dict) else self._default_dialog_window_cfg()
        if not isinstance(raw_cfg, dict):
            return {
                "w": int(base.get("w", 760)),
                "h": int(base.get("h", 130)),
                "x": int(base.get("x", 0)),
                "y": int(base.get("y", 0)),
                "use_default": bool(base.get("use_default", True)),
            }

        use_default = bool(raw_cfg.get("use_default", False if ("w" in raw_cfg or "h" in raw_cfg) else True))
        return {
            "w": max(320, min(1200, int(raw_cfg.get("w", base.get("w", 760)) or base.get("w", 760)))),
            "h": max(90, min(360, int(raw_cfg.get("h", base.get("h", 130)) or base.get("h", 130)))),
            "x": int(raw_cfg.get("x", base.get("x", 0)) or 0),
            "y": int(raw_cfg.get("y", base.get("y", 0)) or 0),
            "use_default": use_default,
        }

    def _normalize_panel_window_cfg(self, raw_cfg, default_cfg: Dict[str, object]) -> Dict[str, object]:
        base = default_cfg if isinstance(default_cfg, dict) else self._default_panel_window_cfg()
        if not isinstance(raw_cfg, dict):
            return {
                "w": int(base.get("w", 220)),
                "h": int(base.get("h", 170)),
                "x": int(base.get("x", 0)),
                "y": int(base.get("y", 0)),
                "use_default": bool(base.get("use_default", True)),
            }

        use_default = bool(raw_cfg.get("use_default", False if ("w" in raw_cfg or "h" in raw_cfg) else True))
        return {
            "w": max(200, min(640, int(raw_cfg.get("w", base.get("w", 220)) or base.get("w", 220)))),
            "h": max(120, min(520, int(raw_cfg.get("h", base.get("h", 170)) or base.get("h", 170)))),
            "x": int(raw_cfg.get("x", base.get("x", 0)) or 0),
            "y": int(raw_cfg.get("y", base.get("y", 0)) or 0),
            "use_default": use_default,
        }

    def _load_ui_defaults(self) -> Dict[str, Dict[str, object]]:
        defaults = {
            "dialog_window": self._default_dialog_window_cfg(),
            "panel_window": self._default_panel_window_cfg(),
        }
        try:
            data = json.loads(self.npc_ui_defaults_path.read_text(encoding="utf-8"))
        except Exception:
            return defaults
        if not isinstance(data, dict):
            return defaults

        defaults["dialog_window"] = self._normalize_dialog_window_cfg(
            data.get("dialog_window", {}),
            defaults["dialog_window"],
        )
        defaults["dialog_window"]["use_default"] = True

        defaults["panel_window"] = self._normalize_panel_window_cfg(
            data.get("panel_window", {}),
            defaults["panel_window"],
        )
        defaults["panel_window"]["use_default"] = True
        return defaults

    def _save_ui_defaults(self, defaults: Dict[str, Dict[str, object]]) -> None:
        payload = {
            "dialog_window": {
                "w": int(defaults.get("dialog_window", {}).get("w", 760)),
                "h": int(defaults.get("dialog_window", {}).get("h", 130)),
                "x": int(defaults.get("dialog_window", {}).get("x", 0)),
                "y": int(defaults.get("dialog_window", {}).get("y", 0)),
            },
            "panel_window": {
                "w": int(defaults.get("panel_window", {}).get("w", 220)),
                "h": int(defaults.get("panel_window", {}).get("h", 170)),
                "x": int(defaults.get("panel_window", {}).get("x", 0)),
                "y": int(defaults.get("panel_window", {}).get("y", 0)),
            },
        }
        self.npc_ui_defaults_path.parent.mkdir(parents=True, exist_ok=True)
        self.npc_ui_defaults_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _find_dimension_preset(self, presets: List[Dict[str, object]], sprite_path: Optional[Path]) -> Optional[Dict[str, object]]:
        if sprite_path is None:
            return None
        rel = self._to_rel(sprite_path)
        for preset in reversed(presets):
            if str(preset.get("sprite", "")) == rel:
                return preset
        return None

    def _load_thumb(self, pygame, cache: Dict[str, object], sprite_path: Path, size: int):
        key = f"{sprite_path}:{int(size)}"
        surf = cache.get(key)
        if surf is not None:
            return surf

        try:
            img = pygame.image.load(str(sprite_path)).convert_alpha()
            surf = pygame.transform.smoothscale(img, (max(1, int(size)), max(1, int(size))))
        except Exception:
            surf = pygame.Surface((max(1, int(size)), max(1, int(size))), pygame.SRCALPHA)
            surf.fill((90, 70, 70, 255))
            pygame.draw.rect(surf, (220, 180, 180), (0, 0, max(1, int(size)), max(1, int(size))), 2)

        cache[key] = surf
        return surf

    def _apply_dimension_preset_to_item(self, item: Dict[str, object], preset: Dict[str, object]) -> None:
        rect = item.get("rect")
        if rect is None:
            return
        try:
            w = max(24, int(preset.get("w", rect.w) or rect.w))
            h = max(24, int(preset.get("h", rect.h) or rect.h))
            center = rect.center
            rect.size = (w, h)
            rect.center = center
        except Exception:
            return

    def _dialog_templates_for_mode(self, npc_id: int, modo_npc: str) -> List[List[str]]:
        mode = str(modo_npc or "npc").lower()
        if mode == "venta":
            return [
                ["Bienvenido a mi tienda.", "Revisa mis productos cuando quieras.", "(E siguiente, Q atras)"],
                ["Hoy tengo buenas ofertas.", "Si necesitas pociones, aqui las encuentras.", "(E siguiente, Q atras)"],
                ["Gracias por pasar.", "Vuelve cuando quieras comprar algo.", "(E siguiente, Q atras)"],
            ]
        if mode == "herrero":
            return [
                ["El fuego de la forja no descansa.", "Puedo mejorar tu equipo cuando quieras.", "(E siguiente, Q atras)"],
                ["Una buena espada salva vidas.", "Trae materiales y trabajamos en ella.", "(E siguiente, Q atras)"],
                ["Revisa tus armas antes de salir.", "Un filo cuidado hace la diferencia.", "(E siguiente, Q atras)"],
            ]
        if mode == "evento":
            return [
                ["Tengo algo importante que contarte.", "Puede que esto active un evento.", "(E siguiente, Q atras)"],
                ["No todos los caminos son seguros.", "Preparate antes de avanzar.", "(E siguiente, Q atras)"],
                ["Tu decision cambiara lo que ocurra despues.", "Piensalo bien.", "(E siguiente, Q atras)"],
            ]

        # Aldeano/NPC base: 10 dialogos de saludo y ambiente.
        return [
            [f"Hola, viajero. Soy el aldeano {npc_id}.", "Que tengas un buen dia en el pueblo.", "(E siguiente, Q atras)"],
            ["El clima esta tranquilo hoy.", "Es buen momento para explorar.", "(E siguiente, Q atras)"],
            ["Dicen que hay monstruos fuera de la aldea.", "Ten cuidado si sales de noche.", "(E siguiente, Q atras)"],
            ["La plaza siempre esta llena al atardecer.", "Si buscas rumores, pregunta alli.", "(E siguiente, Q atras)"],
            ["He visto aventureros entrenar cerca del bosque.", "Quizas encuentres buenos combates por esa zona.", "(E siguiente, Q atras)"],
            ["El herrero trabaja sin descanso.", "Si tu equipo esta danado, visitalo.", "(E siguiente, Q atras)"],
            ["El vendedor conoce todos los precios.", "Compara antes de gastar tus monedas.", "(E siguiente, Q atras)"],
            ["A veces aparecen cofres en lugares raros.", "Revisa cada rincon del mapa.", "(E siguiente, Q atras)"],
            ["Si te pierdes, vuelve a la entrada del pueblo.", "Desde ahi es mas facil orientarse.", "(E siguiente, Q atras)"],
            ["Buena suerte en tu viaje.", "Que tus batallas te den experiencia.", "(E siguiente, Q atras)"],
        ]

    def _default_dialog_pool(self, npc_id: int, modo_npc: str = "npc") -> List[List[str]]:
        templates = self._dialog_templates_for_mode(npc_id, modo_npc)
        pool: List[List[str]] = []
        for i in range(10):
            base = templates[i % len(templates)]
            lines = [str(x) for x in base]
            # Para venta/herrero/evento hay 3 bases y se ciclan hasta completar 10 slots.
            if i >= len(templates) and len(templates) < 10:
                lines[0] = f"{lines[0]} ({i + 1})"
            pool.append(lines)
        return pool

    def _default_dialog_slot_names(self) -> List[str]:
        return [f"Dialogo {i}" for i in range(1, 11)]

    def _normalize_dialog_slot_names(self, raw_names) -> List[str]:
        default_names = self._default_dialog_slot_names()
        if not isinstance(raw_names, list):
            return default_names

        out: List[str] = []
        for i in range(10):
            if i < len(raw_names):
                name = str(raw_names[i]).strip()
                out.append(name if name else default_names[i])
            else:
                out.append(default_names[i])
        return out

    def _normalize_dialog_pool(self, raw_pool, npc_id: int, modo_npc: str = "npc") -> List[List[str]]:
        default_pool = self._default_dialog_pool(npc_id, modo_npc)
        if not isinstance(raw_pool, list):
            return default_pool

        out: List[List[str]] = []
        for i in range(10):
            if i < len(raw_pool) and isinstance(raw_pool[i], list):
                lines = [str(x).strip() for x in raw_pool[i] if str(x).strip()]
                out.append(lines if lines else default_pool[i])
            else:
                out.append(default_pool[i])
        return out

    def _build_npc_item(self, pygame, npc_id: int, sprite: Optional[Path], rect) -> Dict[str, object]:
        rect_ok = rect if rect is not None else pygame.Rect(0, 0, 72, 72)
        pool = self._default_dialog_pool(npc_id, "npc")
        return {
            "id": int(npc_id),
            "tipo": "npc",
            "modo_npc": "npc",
            "sprite": sprite,
            "rect": rect_ok,
            "dialog_pool": pool,
            "dialog_slot_names": self._default_dialog_slot_names(),
            "dialogo_activo_idx": 0,
            "dialogo_lineas": pool[0],
            "ventana_dialogo": self._default_dialog_window_cfg(),
            "ventana_panel": self._default_panel_window_cfg(),
        }

    def _save_scene(self, map_id: str, bg_path: Optional[Path], canvas_items: List[Dict[str, object]]) -> Path:
        out = self.npc_maps_dir / f"{map_id}.json"
        payload = {
            "map_id": map_id,
            "background": self._to_rel(bg_path),
            "npc_items": [],
        }
        for item in canvas_items:
            rect = item["rect"]
            payload["npc_items"].append(
                {
                    "id": int(item["id"]),
                    "tipo": str(item.get("tipo", "npc")),
                    "modo_npc": str(item.get("modo_npc", "npc")),
                    "sprite": self._to_rel(item.get("sprite")),
                    "rect": {
                        "x": int(rect.x),
                        "y": int(rect.y),
                        "w": int(rect.w),
                        "h": int(rect.h),
                    },
                    "dialog_pool": item.get("dialog_pool", []),
                    "dialog_slot_names": item.get("dialog_slot_names", self._default_dialog_slot_names()),
                    "dialogo_activo_idx": int(item.get("dialogo_activo_idx", 0) or 0),
                    "dialogo_lineas": list(item.get("dialogo_lineas", [])),
                    "ventana_dialogo": item.get("ventana_dialogo", self._default_dialog_window_cfg()),
                    "ventana_panel": item.get("ventana_panel", self._default_panel_window_cfg()),
                }
            )
        with out.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=True, indent=2)
        return out

    def _load_scene(self, pygame, json_path: Path, ui_defaults: Dict[str, Dict[str, object]]) -> Optional[Dict[str, object]]:
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        items: List[Dict[str, object]] = []
        for raw in data.get("npc_items", []):
            if not isinstance(raw, dict):
                continue
            sprite = self._from_rel(str(raw.get("sprite", "")))
            rect_raw = raw.get("rect", {}) if isinstance(raw.get("rect"), dict) else {}
            rect = pygame.Rect(
                int(rect_raw.get("x", 0)),
                int(rect_raw.get("y", 0)),
                max(24, int(rect_raw.get("w", 72))),
                max(24, int(rect_raw.get("h", 72))),
            )
            npc_id = int(raw.get("id", 0) or 0)
            item = self._build_npc_item(pygame, npc_id, sprite, rect)
            item["tipo"] = str(raw.get("tipo", "npc"))
            item["modo_npc"] = str(raw.get("modo_npc", "npc")).lower()
            item["dialog_pool"] = self._normalize_dialog_pool(raw.get("dialog_pool", []), npc_id, item["modo_npc"])
            item["dialog_slot_names"] = self._normalize_dialog_slot_names(raw.get("dialog_slot_names", []))
            item["dialogo_activo_idx"] = max(0, min(9, int(raw.get("dialogo_activo_idx", 0) or 0)))
            item["dialogo_lineas"] = list(raw.get("dialogo_lineas", [])) or item["dialog_pool"][item["dialogo_activo_idx"]]
            item["ventana_dialogo"] = self._normalize_dialog_window_cfg(
                raw.get("ventana_dialogo", {}),
                ui_defaults.get("dialog_window", self._default_dialog_window_cfg()),
            )
            item["ventana_panel"] = self._normalize_panel_window_cfg(
                raw.get("ventana_panel", {}),
                ui_defaults.get("panel_window", self._default_panel_window_cfg()),
            )
            items.append(item)

        return {
            "map_id": str(data.get("map_id", "sin_mapa")),
            "background": self._from_rel(str(data.get("background", ""))),
            "items": items,
        }

    def run(self) -> int:
        try:
            import pygame
        except Exception as exc:
            print(f"[ERROR] pygame no disponible: {exc}")
            return 1

        pygame.init()
        # Misma base que otros editores del proyecto, con marco del sistema (- [] X).
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Gestor Interfaz NPC V1 (Nuevo)")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)

        sprite_files = self._discover_images(self.sprite_folder)
        sprite_idx = 0
        sprite_scroll = 0
        thumb_cache: Dict[str, object] = {}
        dimension_presets = self._load_dimension_presets()
        ui_defaults = self._load_ui_defaults()
        preset_scroll = 0
        selected_preset_idx: Optional[int] = None

        background_path: Optional[Path] = None
        background_img = None
        background_scaled = None

        canvas_items: List[Dict[str, object]] = []
        selected_item: Optional[int] = None
        selected_sprite: Optional[Path] = None
        drag_sprite: Optional[Path] = None
        dragging_from_list = False
        moving_item = False
        move_offset = (0, 0)
        next_id = 1

        hero = [260, 260]
        hero_size = 34
        dialog_active = False
        dialog_lines: List[str] = []
        dialog_idx = 0
        dialog_npc_idx: Optional[int] = None

        panel_active = False
        panel_npc_idx: Optional[int] = None
        panel_options: List[str] = []
        panel_selected = 0

        ui_edit_active = False
        ui_edit_target = "dialog"  # dialog | panel
        ui_dragging = False
        ui_resizing = False
        ui_resize_target = "dialog"
        ui_drag_offset = (0, 0)

        context_menu = {
            "visible": False,
            "x": 0,
            "y": 0,
            "npc_idx": None,
            "items": [],
        }

        status = "Listo: Buscar Sprites, Buscar Mapa, arrastrar al canvas, Guardar/Cargar"
        mouse = (0, 0)
        checklist = {
            "mapa_seleccionado": False,
            "carga_mapa": False,
            "guardado_mapa": False,
        }

        running = True
        while running:
            w, h = screen.get_size()
            root = pygame.Rect(12, 12, w - 24, h - 24)
            side_w = 360
            canvas_rect = pygame.Rect(root.x + 12, root.y + 86, root.w - side_w - 30, root.h - 98)
            side_rect = pygame.Rect(canvas_rect.right + 10, root.y + 86, side_w, root.h - 98)

            buttons = {
                "Buscar Sprites": pygame.Rect(root.x + 12, root.y + 42, 140, 32),
                "Buscar Mapa": pygame.Rect(root.x + 160, root.y + 42, 140, 32),
                "Guardar": pygame.Rect(root.x + 308, root.y + 42, 100, 32),
                "Cargar": pygame.Rect(root.x + 414, root.y + 42, 100, 32),
                "Crear Ventana": pygame.Rect(root.x + 520, root.y + 42, 140, 32),
                "Guardar Dim": pygame.Rect(root.x + 668, root.y + 42, 120, 32),
                "Eliminar": pygame.Rect(root.x + 794, root.y + 42, 110, 32),
            }

            # Panel derecho: checklist + lista sprites + presets + demo.
            checklist_rect = pygame.Rect(side_rect.x + 10, side_rect.y + 50, side_rect.w - 20, 84)

            list_y = checklist_rect.bottom + 24
            list_h = int(side_rect.h * 0.30)
            list_rect = pygame.Rect(side_rect.x + 10, list_y, side_rect.w - 20, list_h)

            presets_y = list_rect.bottom + 28
            presets_h = int(side_rect.h * 0.22)
            presets_rect = pygame.Rect(side_rect.x + 10, presets_y, side_rect.w - 20, presets_h)

            preview_y = presets_rect.bottom + 28
            preview_h = max(70, side_rect.bottom - preview_y - 10)
            preview_rect = pygame.Rect(side_rect.x + 10, preview_y, side_rect.w - 20, preview_h)

            def _cerrar_dialogo() -> None:
                nonlocal dialog_active, dialog_lines, dialog_idx, dialog_npc_idx
                dialog_active = False
                dialog_lines = []
                dialog_idx = 0
                dialog_npc_idx = None

            def _abrir_dialogo_desde_npc(npc_idx: int) -> None:
                nonlocal dialog_active, dialog_lines, dialog_idx, dialog_npc_idx, status
                if not (0 <= npc_idx < len(canvas_items)):
                    return
                npc_item = canvas_items[npc_idx]
                pool = npc_item.get("dialog_pool", [])
                active_slot = max(0, min(9, int(npc_item.get("dialogo_activo_idx", 0) or 0)))
                lines = []
                if isinstance(pool, list) and active_slot < len(pool) and isinstance(pool[active_slot], list):
                    lines = [str(x).strip() for x in pool[active_slot] if str(x).strip()]
                if not lines:
                    npc_id = int(npc_item.get("id", 0) or 0)
                    lines = [f"NPC {npc_id} sin dialogo configurado."]
                npc_item["dialogo_lineas"] = lines
                dialog_active = True
                dialog_lines = lines
                dialog_idx = 0
                dialog_npc_idx = npc_idx
                status = f"Interaccion con NPC ID {npc_item['id']} | slot dialogo {active_slot + 1}"

            def _cycle_mode(current: str) -> str:
                modes = ["npc", "venta", "herrero", "evento"]
                c = str(current or "npc").lower()
                if c not in modes:
                    c = "npc"
                return modes[(modes.index(c) + 1) % len(modes)]

            def _effective_window_cfg(npc_item: Dict[str, object], key: str) -> Dict[str, int]:
                if key == "ventana_panel":
                    base = ui_defaults.get("panel_window", self._default_panel_window_cfg())
                    own = npc_item.get("ventana_panel", self._default_panel_window_cfg())
                else:
                    base = ui_defaults.get("dialog_window", self._default_dialog_window_cfg())
                    own = npc_item.get("ventana_dialogo", self._default_dialog_window_cfg())

                if not isinstance(base, dict):
                    base = self._default_panel_window_cfg() if key == "ventana_panel" else self._default_dialog_window_cfg()
                if not isinstance(own, dict):
                    own = self._default_panel_window_cfg() if key == "ventana_panel" else self._default_dialog_window_cfg()

                use_default = bool(own.get("use_default", True))
                src = base if use_default else own
                return {
                    "w": int(src.get("w", base.get("w", 220 if key == "ventana_panel" else 760))),
                    "h": int(src.get("h", base.get("h", 170 if key == "ventana_panel" else 130))),
                    "x": int(src.get("x", base.get("x", 0))),
                    "y": int(src.get("y", base.get("y", 0))),
                }

            def _build_dialog_rect(npc_item: Dict[str, object], canvas: object):
                cfg = _effective_window_cfg(npc_item, "ventana_dialogo")
                bw = max(320, min(canvas.w - 24, int(cfg.get("w", 760) or 760)))
                bh = max(90, min(canvas.h - 24, int(cfg.get("h", 130) or 130)))
                bx = canvas.centerx - bw // 2 + int(cfg.get("x", 0) or 0)
                by = canvas.bottom - bh - 12 + int(cfg.get("y", 0) or 0)
                box = pygame.Rect(bx, by, bw, bh)
                box.clamp_ip(canvas)
                return box

            def _build_panel_rect(npc_item: Dict[str, object], canvas: object, options_count: int):
                cfg = _effective_window_cfg(npc_item, "ventana_panel")
                min_h = 34 + max(1, int(options_count)) * 28
                pw = max(200, min(canvas.w - 24, int(cfg.get("w", 220) or 220)))
                ph = max(min_h, min(canvas.h - 24, int(cfg.get("h", min_h) or min_h)))
                px = canvas.right - pw - 12 + int(cfg.get("x", 0) or 0)
                py = canvas.y + 12 + int(cfg.get("y", 0) or 0)
                panel = pygame.Rect(px, py, pw, ph)
                panel.clamp_ip(canvas)
                return panel

            def _save_window_cfg_from_rect(npc_item: Dict[str, object], key: str, rect: object, canvas: object, options_count: int = 0):
                if key == "ventana_panel":
                    min_h = 34 + max(1, int(options_count)) * 28
                    w = max(200, min(canvas.w - 24, int(rect.w)))
                    h = max(min_h, min(canvas.h - 24, int(rect.h)))
                    x = int(rect.x - (canvas.right - w - 12))
                    y = int(rect.y - (canvas.y + 12))
                    npc_item["ventana_panel"] = {"w": w, "h": h, "x": x, "y": y, "use_default": False}
                else:
                    w = max(320, min(canvas.w - 24, int(rect.w)))
                    h = max(90, min(canvas.h - 24, int(rect.h)))
                    x = int(rect.x - (canvas.centerx - w // 2))
                    y = int(rect.y - (canvas.bottom - h - 12))
                    npc_item["ventana_dialogo"] = {"w": w, "h": h, "x": x, "y": y, "use_default": False}

            def _set_window_use_default(npc_item: Dict[str, object], key: str, use_default: bool):
                if key == "ventana_panel":
                    raw = npc_item.get("ventana_panel", self._default_panel_window_cfg())
                    cfg = self._normalize_panel_window_cfg(raw, ui_defaults.get("panel_window", self._default_panel_window_cfg()))
                    cfg["use_default"] = bool(use_default)
                    npc_item["ventana_panel"] = cfg
                else:
                    raw = npc_item.get("ventana_dialogo", self._default_dialog_window_cfg())
                    cfg = self._normalize_dialog_window_cfg(raw, ui_defaults.get("dialog_window", self._default_dialog_window_cfg()))
                    cfg["use_default"] = bool(use_default)
                    npc_item["ventana_dialogo"] = cfg

            def _start_window_editor(npc_idx: int, target: str = "dialog"):
                nonlocal ui_edit_active, ui_edit_target, dialog_active, panel_active, panel_npc_idx, panel_options, panel_selected, status
                if not (0 <= npc_idx < len(canvas_items)):
                    status = "Editor de ventana: NPC invalido"
                    return

                ui_edit_active = True
                ui_edit_target = target if target in ("dialog", "panel") else "dialog"
                _abrir_dialogo_desde_npc(npc_idx)

                npc_item = canvas_items[npc_idx]
                modo = str(npc_item.get("modo_npc", "npc"))
                if modo in ("venta", "herrero"):
                    panel_active = True
                    panel_npc_idx = npc_idx
                    panel_options = opciones_panel_por_modo(modo)
                    panel_selected = 0
                else:
                    panel_active = False
                    panel_npc_idx = None
                    panel_options = []

                status = "Editor de ventana activo: arrastra para mover, esquina inferior derecha para redimensionar, 1=Dialogo 2=Panel, G=guardar default global, U=usar default"

            def _open_context_menu(npc_idx: int, x: int, y: int) -> None:
                if not (0 <= npc_idx < len(canvas_items)):
                    return
                npc_item = canvas_items[npc_idx]
                slot_names = self._normalize_dialog_slot_names(npc_item.get("dialog_slot_names", []))
                entries = []
                for i in range(10):
                    entries.append((f"{i + 1}. {slot_names[i]}", ("set_dialog", i)))
                entries.append(("Editar dialogo activo", ("edit_dialog", None)))
                entries.append(("Renombrar slot activo", ("rename_slot_name", None)))
                entries.append(("Redimensionar ventana", ("resize_window", None)))
                entries.append(("Cerrar menu", ("close", None)))
                context_menu["visible"] = True
                context_menu["x"] = x
                context_menu["y"] = y
                context_menu["npc_idx"] = npc_idx
                context_menu["items"] = entries

            def _apply_context_action(action: Tuple[str, Optional[int]]) -> None:
                nonlocal status
                npc_idx = context_menu.get("npc_idx")
                if npc_idx is None or not (0 <= int(npc_idx) < len(canvas_items)):
                    context_menu["visible"] = False
                    return
                npc_item = canvas_items[int(npc_idx)]
                act, val = action

                if act == "set_dialog":
                    slot = max(0, min(9, int(val or 0)))
                    npc_item["dialogo_activo_idx"] = slot
                    pool = npc_item.get("dialog_pool", [])
                    slot_names = self._normalize_dialog_slot_names(npc_item.get("dialog_slot_names", []))
                    npc_item["dialog_slot_names"] = slot_names
                    if isinstance(pool, list) and slot < len(pool):
                        npc_item["dialogo_lineas"] = list(pool[slot])
                    status = f"NPC {npc_item['id']}: dialogo activo -> {slot + 1} ({slot_names[slot]})"

                elif act == "edit_dialog":
                    slot = max(0, min(9, int(npc_item.get("dialogo_activo_idx", 0) or 0)))
                    pool = npc_item.get("dialog_pool", [])
                    slot_names = self._normalize_dialog_slot_names(npc_item.get("dialog_slot_names", []))
                    npc_item["dialog_slot_names"] = slot_names
                    current_lines = []
                    if isinstance(pool, list) and slot < len(pool) and isinstance(pool[slot], list):
                        current_lines = [str(x) for x in pool[slot]]
                    initial = " | ".join(current_lines)
                    text = prompt_text(
                        "Editar dialogo",
                        f"NPC {npc_item['id']} - {slot_names[slot]} (separa lineas con |)",
                        initial,
                    )
                    if text is None:
                        status = "Edicion de dialogo cancelada"
                    else:
                        new_lines = [ln.strip() for ln in text.replace("\n", "|").split("|") if ln.strip()]
                        if not new_lines:
                            new_lines = ["..."]
                        pool = self._normalize_dialog_pool(
                            pool,
                            int(npc_item.get("id", 0) or 0),
                            str(npc_item.get("modo_npc", "npc")),
                        )
                        pool[slot] = new_lines
                        npc_item["dialog_pool"] = pool
                        npc_item["dialogo_lineas"] = new_lines
                        status = f"NPC {npc_item['id']}: {slot_names[slot]} actualizado"

                elif act == "rename_slot_name":
                    slot = max(0, min(9, int(npc_item.get("dialogo_activo_idx", 0) or 0)))
                    slot_names = self._normalize_dialog_slot_names(npc_item.get("dialog_slot_names", []))
                    current_name = slot_names[slot]
                    text = prompt_text(
                        "Renombrar slot de dialogo",
                        f"NPC {npc_item['id']} - Nombre para slot {slot + 1}",
                        current_name,
                    )
                    if text is None:
                        status = "Renombrado cancelado"
                    else:
                        new_name = str(text).strip()
                        if not new_name:
                            status = "Nombre invalido"
                        else:
                            slot_names[slot] = new_name
                            npc_item["dialog_slot_names"] = slot_names
                            status = f"NPC {npc_item['id']}: slot {slot + 1} -> {new_name}"

                elif act == "resize_window":
                    _start_window_editor(int(npc_idx), "dialog")

                context_menu["visible"] = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if ui_edit_active and event.key == pygame.K_1:
                        ui_edit_target = "dialog"
                        status = "Editor de ventana: objetivo DIALOGO"
                        continue
                    if ui_edit_active and event.key == pygame.K_2:
                        ui_edit_target = "panel"
                        status = "Editor de ventana: objetivo PANEL"
                        continue
                    if ui_edit_active and event.key == pygame.K_g:
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            item = canvas_items[selected_item]
                            dialog_cfg = item.get("ventana_dialogo", {}) if isinstance(item.get("ventana_dialogo"), dict) else {}
                            panel_cfg = item.get("ventana_panel", {}) if isinstance(item.get("ventana_panel"), dict) else {}
                            ui_defaults["dialog_window"] = self._normalize_dialog_window_cfg(dialog_cfg, ui_defaults.get("dialog_window", self._default_dialog_window_cfg()))
                            ui_defaults["dialog_window"]["use_default"] = True
                            ui_defaults["panel_window"] = self._normalize_panel_window_cfg(panel_cfg, ui_defaults.get("panel_window", self._default_panel_window_cfg()))
                            ui_defaults["panel_window"]["use_default"] = True
                            self._save_ui_defaults(ui_defaults)
                            status = "Default global de ventanas guardado desde NPC seleccionado"
                        else:
                            status = "G: selecciona un NPC primero"
                        continue
                    if ui_edit_active and event.key == pygame.K_u:
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            item = canvas_items[selected_item]
                            _set_window_use_default(item, "ventana_dialogo", True)
                            _set_window_use_default(item, "ventana_panel", True)
                            status = f"NPC {item['id']}: usando default global de ventanas"
                        else:
                            status = "U: selecciona un NPC primero"
                        continue

                    if event.key == pygame.K_ESCAPE:
                        if context_menu["visible"]:
                            context_menu["visible"] = False
                        elif ui_edit_active:
                            ui_edit_active = False
                            ui_dragging = False
                            ui_resizing = False
                            status = "Editor de ventana desactivado"
                        elif dialog_active:
                            _cerrar_dialogo()
                        elif panel_active:
                            panel_active = False
                            panel_npc_idx = None
                        else:
                            running = False

                    elif event.key == pygame.K_TAB:
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            item = canvas_items[selected_item]
                            item["modo_npc"] = _cycle_mode(str(item.get("modo_npc", "npc")))
                            npc_id = int(item.get("id", 0) or 0)
                            item["dialog_pool"] = self._default_dialog_pool(npc_id, str(item.get("modo_npc", "npc")))
                            item["dialogo_activo_idx"] = 0
                            item["dialogo_lineas"] = list(item["dialog_pool"][0])
                            item["dialog_slot_names"] = self._default_dialog_slot_names()
                            status = f"NPC {item['id']}: modo -> {item['modo_npc'].upper()} | dialogos predeterminados actualizados"

                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            rect = canvas_items[selected_item].get("rect")
                            if rect is not None:
                                center = rect.center
                                rect.w = min(320, rect.w + 8)
                                rect.h = min(320, rect.h + 8)
                                rect.center = center
                                status = f"NPC {canvas_items[selected_item]['id']}: tamano {rect.w}x{rect.h}"

                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            rect = canvas_items[selected_item].get("rect")
                            if rect is not None:
                                center = rect.center
                                rect.w = max(24, rect.w - 8)
                                rect.h = max(24, rect.h - 8)
                                rect.center = center
                                status = f"NPC {canvas_items[selected_item]['id']}: tamano {rect.w}x{rect.h}"

                    elif event.key == pygame.K_DELETE:
                        if selected_item is not None and 0 <= selected_item < len(canvas_items):
                            removed_idx = selected_item
                            removed_item = canvas_items.pop(removed_idx)
                            removed_id = int(removed_item.get("id", 0) or 0)

                            if not canvas_items:
                                selected_item = None
                            else:
                                selected_item = min(removed_idx, len(canvas_items) - 1)

                            if dialog_npc_idx == removed_idx:
                                _cerrar_dialogo()
                            elif dialog_npc_idx is not None and dialog_npc_idx > removed_idx:
                                dialog_npc_idx -= 1

                            if panel_npc_idx == removed_idx:
                                panel_active = False
                                panel_npc_idx = None
                            elif panel_npc_idx is not None and panel_npc_idx > removed_idx:
                                panel_npc_idx -= 1

                            status = f"NPC eliminado: ID {removed_id}"

                        elif selected_preset_idx is not None and 0 <= selected_preset_idx < len(dimension_presets):
                            removed_name = str(dimension_presets[selected_preset_idx].get("name", "preset"))
                            confirmar = prompt_text(
                                "Eliminar preset",
                                f"Escribe SI para borrar '{removed_name}'",
                                "NO",
                            )
                            if str(confirmar or "").strip().upper() == "SI":
                                removed = dimension_presets.pop(selected_preset_idx)
                                self._save_dimension_presets(dimension_presets)
                                if not dimension_presets:
                                    selected_preset_idx = None
                                else:
                                    selected_preset_idx = min(selected_preset_idx, len(dimension_presets) - 1)
                                status = f"Preset eliminado: {removed.get('name', 'preset')}"
                            else:
                                status = "Eliminacion cancelada"
                        else:
                            status = "Suprimir: selecciona un NPC en canvas o un preset de tamano"

                    elif event.key == pygame.K_q:
                        if dialog_active:
                            if dialog_idx > 0:
                                dialog_idx -= 1
                            else:
                                status = "Ya estas en la primera linea"

                    elif event.key in (pygame.K_UP, pygame.K_DOWN):
                        if panel_active and panel_options:
                            step = -1 if event.key == pygame.K_UP else 1
                            panel_selected = (panel_selected + step) % len(panel_options)

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if panel_active and panel_options and panel_npc_idx is not None:
                            if not (0 <= panel_npc_idx < len(canvas_items)):
                                panel_active = False
                                panel_npc_idx = None
                                status = "Panel cerrado: NPC ya no existe"
                                continue

                            npc_item = canvas_items[panel_npc_idx]
                            npc_idx_local = panel_npc_idx
                            accion = panel_options[panel_selected]
                            res = ejecutar_accion_panel(str(npc_item.get("modo_npc", "npc")), accion, int(npc_item.get("id", 0) or 0))
                            status = str(res.get("mensaje", "Accion ejecutada"))
                            if res.get("cerrar_panel"):
                                panel_active = False
                                panel_npc_idx = None
                            if res.get("reabrir_dialogo") and npc_idx_local is not None and 0 <= npc_idx_local < len(canvas_items):
                                _abrir_dialogo_desde_npc(npc_idx_local)

                            if str(npc_item.get("modo_npc", "npc")) == "evento":
                                ev = resolver_evento_npc(str(npc_item.get("modo_npc", "npc")), int(npc_item.get("id", 0) or 0))
                                if ev.get("ok"):
                                    status = f"{status} | {ev.get('mensaje', '')}"

                    elif event.key == pygame.K_e:
                        if dialog_active:
                            dialog_idx += 1
                            if dialog_idx >= len(dialog_lines):
                                npc_idx = dialog_npc_idx
                                _cerrar_dialogo()
                                if npc_idx is not None and 0 <= npc_idx < len(canvas_items):
                                    npc_item = canvas_items[npc_idx]
                                    modo = str(npc_item.get("modo_npc", "npc"))
                                    if modo in ("venta", "herrero"):
                                        panel_active = True
                                        panel_npc_idx = npc_idx
                                        panel_options = opciones_panel_por_modo(modo)
                                        panel_selected = 0
                                        status = f"NPC {npc_item['id']}: panel {modo.upper()} abierto"
                            continue

                        if panel_active and panel_options and panel_npc_idx is not None:
                            if not (0 <= panel_npc_idx < len(canvas_items)):
                                panel_active = False
                                panel_npc_idx = None
                                status = "Panel cerrado: NPC ya no existe"
                                continue

                            npc_item = canvas_items[panel_npc_idx]
                            npc_idx_local = panel_npc_idx
                            accion = panel_options[panel_selected]
                            res = ejecutar_accion_panel(str(npc_item.get("modo_npc", "npc")), accion, int(npc_item.get("id", 0) or 0))
                            status = str(res.get("mensaje", "Accion ejecutada"))
                            if res.get("cerrar_panel"):
                                panel_active = False
                                panel_npc_idx = None
                            if res.get("reabrir_dialogo") and npc_idx_local is not None and 0 <= npc_idx_local < len(canvas_items):
                                _abrir_dialogo_desde_npc(npc_idx_local)
                            continue

                        hero_rect = pygame.Rect(hero[0], hero[1], hero_size, hero_size)
                        nearest = None
                        nearest_d = None
                        for idx, item in enumerate(canvas_items):
                            if str(item.get("tipo", "npc")).lower() != "npc":
                                continue
                            rect = item.get("rect")
                            if rect is None:
                                continue
                            d = ((hero_rect.centerx - rect.centerx) ** 2 + (hero_rect.centery - rect.centery) ** 2) ** 0.5
                            if d <= 80 and (nearest_d is None or d < nearest_d):
                                nearest = idx
                                nearest_d = d

                        if nearest is not None:
                            _abrir_dialogo_desde_npc(nearest)
                        else:
                            status = "No hay NPC cerca para interactuar"
                elif event.type == pygame.MOUSEWHEEL:
                    mx, my = mouse
                    if list_rect.collidepoint(mx, my):
                        visible = max(1, list_rect.h // 30)
                        max_scroll = max(0, len(sprite_files) - visible)
                        sprite_scroll = max(0, min(max_scroll, sprite_scroll - event.y))
                    elif presets_rect.collidepoint(mx, my):
                        visible_p = max(1, presets_rect.h // 24)
                        max_scroll_p = max(0, len(dimension_presets) - visible_p)
                        preset_scroll = max(0, min(max_scroll_p, preset_scroll - event.y))
                    elif canvas_rect.collidepoint(mx, my) and selected_item is not None and 0 <= selected_item < len(canvas_items):
                        rect = canvas_items[selected_item].get("rect")
                        if rect is not None:
                            center = rect.center
                            delta = 6 if event.y > 0 else -6
                            rect.w = max(24, min(320, rect.w + delta))
                            rect.h = max(24, min(320, rect.h + delta))
                            rect.center = center
                            status = f"NPC {canvas_items[selected_item]['id']}: tamano {rect.w}x{rect.h}"
                elif event.type == pygame.MOUSEMOTION:
                    mouse = event.pos
                    if (ui_dragging or ui_resizing) and selected_item is not None and 0 <= selected_item < len(canvas_items):
                        item = canvas_items[selected_item]
                        if ui_resize_target == "panel":
                            options_count = max(1, len(panel_options))
                            box = _build_panel_rect(item, canvas_rect, options_count)
                        else:
                            options_count = 0
                            box = _build_dialog_rect(item, canvas_rect)

                        if ui_dragging:
                            box.x = event.pos[0] - ui_drag_offset[0]
                            box.y = event.pos[1] - ui_drag_offset[1]
                            box.clamp_ip(canvas_rect)
                        elif ui_resizing:
                            if ui_resize_target == "panel":
                                min_h = 34 + options_count * 28
                                box.w = max(200, min(canvas_rect.w - 24, event.pos[0] - box.x))
                                box.h = max(min_h, min(canvas_rect.h - 24, event.pos[1] - box.y))
                            else:
                                box.w = max(320, min(canvas_rect.w - 24, event.pos[0] - box.x))
                                box.h = max(90, min(canvas_rect.h - 24, event.pos[1] - box.y))

                        _save_window_cfg_from_rect(
                            item,
                            "ventana_panel" if ui_resize_target == "panel" else "ventana_dialogo",
                            box,
                            canvas_rect,
                            options_count,
                        )
                        continue

                    if moving_item and selected_item is not None and 0 <= selected_item < len(canvas_items):
                        rect = canvas_items[selected_item]["rect"]
                        rect.x = event.pos[0] - move_offset[0]
                        rect.y = event.pos[1] - move_offset[1]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if context_menu["visible"] and event.button == 1:
                        cx = int(context_menu["x"])
                        cy = int(context_menu["y"])
                        row_h = 24
                        menu_w = 230
                        entries = context_menu.get("items", [])
                        menu_h = max(24, len(entries) * row_h)
                        menu_rect = pygame.Rect(cx, cy, menu_w, menu_h)
                        if menu_rect.collidepoint(mx, my):
                            idx = (my - menu_rect.y) // row_h
                            if 0 <= idx < len(entries):
                                _apply_context_action(entries[idx][1])
                            continue
                        context_menu["visible"] = False

                    if event.button == 1:
                        if ui_edit_active and selected_item is not None and 0 <= selected_item < len(canvas_items):
                            item = canvas_items[selected_item]
                            if ui_edit_target == "panel":
                                options_count = max(1, len(panel_options))
                                target_rect = _build_panel_rect(item, canvas_rect, options_count)
                            else:
                                target_rect = _build_dialog_rect(item, canvas_rect)

                            handle = pygame.Rect(target_rect.right - 14, target_rect.bottom - 14, 14, 14)
                            if handle.collidepoint(mx, my):
                                ui_resizing = True
                                ui_dragging = False
                                ui_resize_target = ui_edit_target
                                status = f"Editor ventana: redimensionando {ui_resize_target}"
                                continue

                            if target_rect.collidepoint(mx, my):
                                ui_dragging = True
                                ui_resizing = False
                                ui_resize_target = ui_edit_target
                                ui_drag_offset = (mx - target_rect.x, my - target_rect.y)
                                status = f"Editor ventana: moviendo {ui_resize_target}"
                                continue

                        for label, rect in buttons.items():
                            if not rect.collidepoint(mx, my):
                                continue
                            if label == "Buscar Sprites":
                                folder = prompt_directory("Seleccionar carpeta de sprites", self.sprite_folder)
                                if folder is not None:
                                    self.sprite_folder = folder
                                    sprite_files = self._discover_images(folder)
                                    sprite_idx = 0
                                    sprite_scroll = 0
                                    status = f"Carpeta sprites: {folder.name} ({len(sprite_files)})"
                                else:
                                    status = "Busqueda de sprites cancelada"
                            elif label == "Buscar Mapa":
                                bg = prompt_file("Seleccionar mapa", self.background_folder, "*.png *.jpg *.jpeg *.webp")
                                if bg is not None:
                                    self.background_folder = bg.parent
                                    background_path = bg
                                    try:
                                        background_img = pygame.image.load(str(bg)).convert()
                                        background_scaled = pygame.transform.smoothscale(background_img, (canvas_rect.w, canvas_rect.h))

                                        # Persistencia por mapa: cargar escena si existe; si no, limpiar.
                                        map_id = self._map_id(background_path)
                                        scene_path = self.npc_maps_dir / f"{map_id}.json"
                                        if scene_path.exists():
                                            loaded = self._load_scene(pygame, scene_path, ui_defaults)
                                            if loaded is not None:
                                                canvas_items = loaded["items"]
                                                next_id = max([int(i.get("id", 0)) for i in canvas_items], default=0) + 1
                                                selected_item = None
                                                checklist["mapa_seleccionado"] = True
                                                checklist["carga_mapa"] = True
                                                status = f"Mapa cargado: {bg.name} | NPC restaurados: {len(canvas_items)}"
                                            else:
                                                checklist["mapa_seleccionado"] = True
                                                checklist["carga_mapa"] = False
                                                status = f"Mapa cargado: {bg.name} | Error leyendo escena"
                                        else:
                                            canvas_items = []
                                            selected_item = None
                                            next_id = 1
                                            checklist["mapa_seleccionado"] = True
                                            checklist["carga_mapa"] = False
                                            status = f"Mapa cargado: {bg.name} | Mapa nuevo sin NPC"
                                    except Exception as exc:
                                        background_img = None
                                        background_scaled = None
                                        checklist["mapa_seleccionado"] = False
                                        checklist["carga_mapa"] = False
                                        status = f"Error cargando mapa: {exc}"
                                else:
                                    status = "Seleccion de mapa cancelada"
                            elif label == "Guardar":
                                map_id = self._map_id(background_path)
                                out = self._save_scene(map_id, background_path, canvas_items)
                                checklist["guardado_mapa"] = True
                                status = f"Guardado: {out.name} ({len(canvas_items)} item(s))"
                            elif label == "Cargar":
                                p = prompt_file("Cargar escena NPC", self.npc_maps_dir, "*.json")
                                if p is not None and p.exists():
                                    loaded = self._load_scene(pygame, p, ui_defaults)
                                    if loaded is None:
                                        checklist["carga_mapa"] = False
                                        status = "No se pudo cargar el JSON"
                                    else:
                                        canvas_items = loaded["items"]
                                        next_id = max([int(i.get("id", 0)) for i in canvas_items], default=0) + 1
                                        selected_item = None
                                        checklist["mapa_seleccionado"] = True
                                        checklist["carga_mapa"] = True
                                        bg = loaded.get("background")
                                        if isinstance(bg, Path) and bg.exists():
                                            background_path = bg
                                            try:
                                                background_img = pygame.image.load(str(bg)).convert()
                                                background_scaled = pygame.transform.smoothscale(background_img, (canvas_rect.w, canvas_rect.h))
                                            except Exception:
                                                background_img = None
                                                background_scaled = None
                                        status = f"Cargado: {p.name}"
                                else:
                                    status = "Carga cancelada"
                            elif label == "Crear Ventana":
                                if selected_item is None or not (0 <= selected_item < len(canvas_items)):
                                    status = "Crear Ventana: selecciona primero un NPC en canvas"
                                else:
                                    _start_window_editor(selected_item, "dialog")

                            elif label == "Guardar Dim":
                                if selected_item is None or not (0 <= selected_item < len(canvas_items)):
                                    status = "Guardar Dim: selecciona un NPC en canvas"
                                else:
                                    item = canvas_items[selected_item]
                                    rect = item.get("rect")
                                    sprite = item.get("sprite")
                                    if rect is None or not isinstance(sprite, Path):
                                        status = "Guardar Dim: item invalido"
                                    else:
                                        preset = {
                                            "name": f"{sprite.stem}_{int(rect.w)}x{int(rect.h)}",
                                            "sprite": self._to_rel(sprite),
                                            "w": int(rect.w),
                                            "h": int(rect.h),
                                            "tipo": "npc",
                                        }
                                        dimension_presets.append(preset)
                                        self._save_dimension_presets(dimension_presets)
                                        status = f"Preset guardado: {preset['name']}"
                            elif label == "Eliminar":
                                if selected_item is None or not (0 <= selected_item < len(canvas_items)):
                                    status = "Eliminar: selecciona item en canvas"
                                else:
                                    removed = canvas_items.pop(selected_item)
                                    selected_item = None
                                    status = f"Eliminado item ID {removed['id']}"
                            break

                        if list_rect.collidepoint(mx, my):
                            row = (my - list_rect.y) // 30
                            idx = sprite_scroll + row
                            if 0 <= idx < len(sprite_files):
                                sprite_idx = idx
                                selected_sprite = sprite_files[idx]
                                drag_sprite = selected_sprite
                                dragging_from_list = True
                                status = f"Sprite seleccionado: {selected_sprite.name}"

                        if presets_rect.collidepoint(mx, my):
                            row = (my - presets_rect.y) // 24
                            idx = preset_scroll + row
                            if 0 <= idx < len(dimension_presets):
                                selected_preset_idx = idx
                                preset = dimension_presets[idx]
                                if selected_item is not None and 0 <= selected_item < len(canvas_items):
                                    self._apply_dimension_preset_to_item(canvas_items[selected_item], preset)
                                    rect = canvas_items[selected_item].get("rect")
                                    if rect is not None:
                                        status = f"Preset aplicado a NPC {canvas_items[selected_item]['id']}: {rect.w}x{rect.h}"
                                else:
                                    status = f"Preset seleccionado: {preset.get('name', 'preset')}"

                        if canvas_rect.collidepoint(mx, my):
                            picked = None
                            for idx in range(len(canvas_items) - 1, -1, -1):
                                r = canvas_items[idx]["rect"]
                                if r.collidepoint(mx, my):
                                    picked = idx
                                    break
                            if picked is not None:
                                selected_item = picked
                                moving_item = True
                                rect = canvas_items[picked]["rect"]
                                move_offset = (mx - rect.x, my - rect.y)
                                status = f"Seleccionado item ID {canvas_items[picked]['id']} | TAB cambia modo"
                    elif event.button == 3:
                        if canvas_rect.collidepoint(mx, my):
                            picked = None
                            for idx in range(len(canvas_items) - 1, -1, -1):
                                r = canvas_items[idx]["rect"]
                                if r.collidepoint(mx, my):
                                    picked = idx
                                    break
                            if picked is not None:
                                selected_item = picked
                                _open_context_menu(picked, mx, my)
                                status = f"Menu NPC {canvas_items[picked]['id']}: elige Dialogo 1..10"
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        ui_dragging = False
                        ui_resizing = False
                        mx, my = event.pos
                        if dragging_from_list and drag_sprite is not None and canvas_rect.collidepoint(mx, my):
                            new_item = self._build_npc_item(pygame, next_id, drag_sprite, pygame.Rect(mx - 36, my - 36, 72, 72))
                            preset = self._find_dimension_preset(dimension_presets, drag_sprite)
                            if preset is not None:
                                self._apply_dimension_preset_to_item(new_item, preset)
                            canvas_items.append(new_item)
                            selected_item = len(canvas_items) - 1
                            next_id += 1
                            if preset is not None:
                                status = f"NPC creado: {drag_sprite.stem} | tamano preset {new_item['rect'].w}x{new_item['rect'].h}"
                            else:
                                status = f"NPC creado en canvas: {drag_sprite.stem} | pool 10 dialogos listo"
                        dragging_from_list = False
                        drag_sprite = None
                        moving_item = False

            keys = pygame.key.get_pressed()
            spd = 4
            if keys[pygame.K_w]:
                hero[1] -= spd
            if keys[pygame.K_s]:
                hero[1] += spd
            if keys[pygame.K_a]:
                hero[0] -= spd
            if keys[pygame.K_d]:
                hero[0] += spd
            hero[0] = max(canvas_rect.left, min(hero[0], canvas_rect.right - hero_size))
            hero[1] = max(canvas_rect.top, min(hero[1], canvas_rect.bottom - hero_size))

            screen.fill((20, 22, 30))
            pygame.draw.rect(screen, (40, 45, 62), root, border_radius=12)
            pygame.draw.rect(screen, (96, 132, 200), root, 2, border_radius=12)

            title = font.render("Gestor Interfaz NPC V1 (Nuevo) | Arrastra sprite -> canvas | E interactuar", True, (235, 240, 250))
            screen.blit(title, (root.x + 12, root.y + 12))

            for label, rect in buttons.items():
                pygame.draw.rect(screen, (65, 78, 110), rect, border_radius=6)
                pygame.draw.rect(screen, (150, 175, 220), rect, 1, border_radius=6)
                txt = font_small.render(label, True, (240, 243, 248))
                screen.blit(txt, (rect.x + 8, rect.y + 8))

            pygame.draw.rect(screen, (8, 8, 12), canvas_rect, border_radius=8)
            pygame.draw.rect(screen, (86, 100, 128), canvas_rect, 1, border_radius=8)

            if background_img is not None:
                if background_scaled is None or background_scaled.get_size() != (canvas_rect.w, canvas_rect.h):
                    background_scaled = pygame.transform.smoothscale(background_img, (canvas_rect.w, canvas_rect.h))
                screen.blit(background_scaled, canvas_rect)

            for idx, item in enumerate(canvas_items):
                rect = item["rect"]
                sprite = item.get("sprite")
                if isinstance(sprite, Path) and sprite.exists():
                    key = f"{sprite}:{rect.w}x{rect.h}"
                    surf = thumb_cache.get(key)
                    if surf is None:
                        try:
                            img = pygame.image.load(str(sprite)).convert_alpha()
                            surf = pygame.transform.smoothscale(img, (rect.w, rect.h))
                        except Exception:
                            surf = None
                        thumb_cache[key] = surf
                    if surf is not None:
                        screen.blit(surf, rect)
                    else:
                        pygame.draw.rect(screen, (120, 80, 80), rect)
                else:
                    pygame.draw.rect(screen, (120, 80, 80), rect)

                border = (255, 220, 110) if idx == selected_item else (120, 140, 170)
                pygame.draw.rect(screen, border, rect, 2)
                tag = font_small.render(f"ID {item['id']} {str(item.get('tipo', 'npc')).upper()}", True, (236, 240, 248))
                screen.blit(tag, (rect.x, rect.y - 16))
                mode_tag = font_small.render(f"MODO: {str(item.get('modo_npc', 'npc')).upper()}  D{int(item.get('dialogo_activo_idx', 0)) + 1}", True, (206, 225, 255))
                screen.blit(mode_tag, (rect.x, rect.bottom + 2))
                slot_names = self._normalize_dialog_slot_names(item.get("dialog_slot_names", []))
                active_idx = max(0, min(9, int(item.get("dialogo_activo_idx", 0) or 0)))
                slot_tag = font_small.render(f"Slot: {slot_names[active_idx]}", True, (190, 210, 236))
                screen.blit(slot_tag, (rect.x, rect.bottom + 18))

            pygame.draw.rect(screen, (40, 160, 80), (hero[0], hero[1], hero_size, hero_size))
            pygame.draw.rect(screen, (235, 245, 235), (hero[0], hero[1], hero_size, hero_size), 2)

            pygame.draw.rect(screen, (27, 31, 43), side_rect, border_radius=8)
            pygame.draw.rect(screen, (90, 110, 146), side_rect, 1, border_radius=8)

            side_title = font.render(f"Sprites ({len(sprite_files)}) | Carpeta: {self.sprite_folder.name}", True, (220, 228, 241))
            screen.blit(side_title, (side_rect.x + 10, side_rect.y + 14))

            # Checklist visual de flujo mapa/carga/guardado.
            pygame.draw.rect(screen, (19, 22, 32), checklist_rect, border_radius=6)
            pygame.draw.rect(screen, (88, 102, 130), checklist_rect, 1, border_radius=6)
            ck_title = font_small.render("Checklist Mapa", True, (225, 233, 246))
            screen.blit(ck_title, (checklist_rect.x + 8, checklist_rect.y + 6))

            def _ck_line(y: int, ok: bool, text: str):
                col = (120, 220, 140) if ok else (220, 130, 130)
                mark = "[OK]" if ok else "[ ]"
                t = font_small.render(f"{mark} {text}", True, col)
                screen.blit(t, (checklist_rect.x + 8, y))

            _ck_line(checklist_rect.y + 24, bool(checklist.get("mapa_seleccionado")), "Mapa seleccionado")
            _ck_line(checklist_rect.y + 42, bool(checklist.get("carga_mapa")), "Carga mapa")
            _ck_line(checklist_rect.y + 60, bool(checklist.get("guardado_mapa")), "Guardado mapa")

            pygame.draw.rect(screen, (19, 22, 32), list_rect, border_radius=6)
            pygame.draw.rect(screen, (88, 102, 130), list_rect, 1, border_radius=6)

            row_h = 30
            visible = max(1, list_rect.h // row_h)
            for row in range(visible):
                idx = sprite_scroll + row
                if idx >= len(sprite_files):
                    break
                p = sprite_files[idx]
                row_rect = pygame.Rect(list_rect.x + 4, list_rect.y + row * row_h + 2, list_rect.w - 8, row_h - 4)
                active = idx == sprite_idx
                pygame.draw.rect(screen, (60, 97, 159) if active else (36, 42, 58), row_rect, border_radius=4)
                if selected_sprite is not None and p == selected_sprite:
                    pygame.draw.rect(screen, (255, 220, 110), row_rect, 2, border_radius=4)
                txt = font_small.render(p.name, True, (235, 240, 248))
                screen.blit(txt, (row_rect.x + 6, row_rect.y + 6))

            # Presets de tamano en panel derecho.
            presets_title = font.render(f"Presets de tamano ({len(dimension_presets)})", True, (220, 228, 241))
            screen.blit(presets_title, (side_rect.x + 10, presets_rect.y - 20))
            pygame.draw.rect(screen, (19, 22, 32), presets_rect, border_radius=6)
            pygame.draw.rect(screen, (88, 102, 130), presets_rect, 1, border_radius=6)

            row_p_h = 24
            visible_p = max(1, presets_rect.h // row_p_h)
            max_scroll_p = max(0, len(dimension_presets) - visible_p)
            preset_scroll = max(0, min(max_scroll_p, preset_scroll))
            for row in range(visible_p):
                idx = preset_scroll + row
                if idx >= len(dimension_presets):
                    break
                preset = dimension_presets[idx]
                r = pygame.Rect(presets_rect.x + 4, presets_rect.y + row * row_p_h + 2, presets_rect.w - 8, row_p_h - 4)
                active = idx == selected_preset_idx
                pygame.draw.rect(screen, (60, 97, 159) if active else (36, 42, 58), r, border_radius=4)
                if active:
                    pygame.draw.rect(screen, (255, 220, 110), r, 2, border_radius=4)
                label = str(preset.get("name", "preset"))
                wh = f"{int(preset.get('w', 0) or 0)}x{int(preset.get('h', 0) or 0)}"
                t = font_small.render(f"{label} ({wh})", True, (235, 240, 248))
                screen.blit(t, (r.x + 6, r.y + 4))

            # Demo pequena de sprite en panel derecho.
            demo_title = font.render("Demo sprite", True, (220, 228, 241))
            screen.blit(demo_title, (side_rect.x + 10, preview_rect.y - 20))
            pygame.draw.rect(screen, (19, 22, 32), preview_rect, border_radius=6)
            pygame.draw.rect(screen, (88, 102, 130), preview_rect, 1, border_radius=6)

            demo_source = selected_sprite
            if demo_source is None and selected_item is not None and 0 <= selected_item < len(canvas_items):
                src = canvas_items[selected_item].get("sprite")
                if isinstance(src, Path):
                    demo_source = src

            if demo_source is not None and demo_source.exists():
                demo_size = max(32, min(preview_rect.w - 20, preview_rect.h - 36, 120))
                demo_thumb = self._load_thumb(pygame, thumb_cache, demo_source, demo_size)
                demo_rect = demo_thumb.get_rect(center=(preview_rect.centerx, preview_rect.y + (preview_rect.h // 2) - 8))
                screen.blit(demo_thumb, demo_rect)
                cap = font_small.render(demo_source.name, True, (225, 232, 245))
                screen.blit(cap, (preview_rect.x + 8, preview_rect.bottom - 18))
            else:
                empty = font_small.render("Sin sprite seleccionado", True, (170, 182, 204))
                screen.blit(empty, (preview_rect.x + 8, preview_rect.y + 8))

            hint_y = preview_rect.bottom + 6
            hints = [
                "Funciones:",
                "- Buscar carpeta de sprites",
                "- Buscar mapa especifico",
                "- Arrastrar sprite al canvas",
                "- Guardar Dim para presets de tamano",
                "- Suprimir en preset: elimina dimension",
                "- Guardar / Cargar escena",
                "- Crear Ventana: redimensionar dialogo",
                "- E avanza dialogo / Q retrocede",
                "- TAB cambia modo: NPC/VENTA/HERRERO/EVENTO",
                "- Click derecho NPC: menu Dialogo 1..10",
                "- +/- o rueda en canvas: cambiar tamano",
            ]
            for line in hints:
                if hint_y > side_rect.bottom - 26:
                    break
                t = font_small.render(line, True, (200, 212, 232))
                screen.blit(t, (side_rect.x + 10, hint_y))
                hint_y += 18

            status_bar = pygame.Rect(root.x + 12, root.bottom - 30, root.w - 24, 20)
            pygame.draw.rect(screen, (18, 20, 30), status_bar, border_radius=5)
            st = font_small.render(status, True, (180, 206, 245))
            screen.blit(st, (status_bar.x + 6, status_bar.y + 2))

            if dialog_active and dialog_lines:
                cfg = ui_defaults.get("dialog_window", self._default_dialog_window_cfg())
                if dialog_npc_idx is not None and 0 <= dialog_npc_idx < len(canvas_items):
                    box = _build_dialog_rect(canvas_items[dialog_npc_idx], canvas_rect)
                else:
                    bw = max(320, min(canvas_rect.w - 24, int(cfg.get("w", 760) or 760)))
                    bh = max(90, min(canvas_rect.h - 24, int(cfg.get("h", 130) or 130)))
                    box = pygame.Rect(canvas_rect.centerx - bw // 2, canvas_rect.bottom - bh - 12, bw, bh)
                    box.clamp_ip(canvas_rect)
                pygame.draw.rect(screen, (0, 0, 0), box, border_radius=8)
                pygame.draw.rect(screen, (220, 220, 220), box, 2, border_radius=8)
                idx = min(dialog_idx, len(dialog_lines) - 1)
                txt = font.render(dialog_lines[idx], True, (255, 255, 255))
                screen.blit(txt, (box.x + 12, box.y + 16))
                nxt = font_small.render("E: siguiente | Q: atras", True, (255, 220, 120))
                screen.blit(nxt, (box.right - nxt.get_width() - 12, box.bottom - nxt.get_height() - 10))

                if ui_edit_active and ui_edit_target == "dialog":
                    handle = pygame.Rect(box.right - 14, box.bottom - 14, 12, 12)
                    pygame.draw.rect(screen, (255, 210, 90), handle)
                    tip = font_small.render("EDIT DIALOGO", True, (255, 220, 120))
                    screen.blit(tip, (box.x + 10, box.y - 18))

            if panel_active and panel_npc_idx is not None and panel_options:
                if not (0 <= panel_npc_idx < len(canvas_items)):
                    panel_active = False
                    panel_npc_idx = None
                    status = "Panel cerrado: NPC ya no existe"
                else:
                    npc_item = canvas_items[panel_npc_idx]
                    panel = _build_panel_rect(npc_item, canvas_rect, len(panel_options))
                    pygame.draw.rect(screen, (14, 18, 28), panel, border_radius=8)
                    pygame.draw.rect(screen, (145, 170, 220), panel, 1, border_radius=8)
                    title_panel = font_small.render(f"NPC {npc_item['id']} {str(npc_item.get('modo_npc', 'npc')).upper()}", True, (230, 235, 248))
                    screen.blit(title_panel, (panel.x + 10, panel.y + 8))
                    for i, opt in enumerate(panel_options):
                        r = pygame.Rect(panel.x + 8, panel.y + 28 + i * 28, panel.w - 16, 24)
                        active = i == panel_selected
                        pygame.draw.rect(screen, (70, 105, 165) if active else (35, 42, 62), r, border_radius=4)
                        pygame.draw.rect(screen, (180, 210, 255) if active else (95, 110, 150), r, 1, border_radius=4)
                        t = font_small.render(opt, True, (240, 245, 252))
                        screen.blit(t, (r.x + 8, r.y + 4))

                    if ui_edit_active and ui_edit_target == "panel":
                        handle = pygame.Rect(panel.right - 14, panel.bottom - 14, 12, 12)
                        pygame.draw.rect(screen, (255, 210, 90), handle)
                        tip = font_small.render("EDIT PANEL", True, (255, 220, 120))
                        screen.blit(tip, (panel.x + 10, panel.y - 18))

            if context_menu["visible"]:
                entries = context_menu.get("items", [])
                row_h = 24
                menu_w = 230
                menu_h = max(24, len(entries) * row_h)
                mx = int(context_menu["x"])
                my = int(context_menu["y"])
                if mx + menu_w > root.right - 8:
                    mx = root.right - menu_w - 8
                if my + menu_h > root.bottom - 8:
                    my = root.bottom - menu_h - 8
                menu = pygame.Rect(mx, my, menu_w, menu_h)
                pygame.draw.rect(screen, (22, 25, 34), menu, border_radius=6)
                pygame.draw.rect(screen, (140, 160, 205), menu, 1, border_radius=6)
                for i, entry in enumerate(entries):
                    r = pygame.Rect(menu.x + 4, menu.y + i * row_h + 2, menu.w - 8, row_h - 4)
                    hover = r.collidepoint(mouse)
                    pygame.draw.rect(screen, (62, 92, 148) if hover else (34, 40, 56), r, border_radius=4)
                    t = font_small.render(str(entry[0]), True, (236, 240, 248))
                    screen.blit(t, (r.x + 8, r.y + 4))

            if dragging_from_list and drag_sprite is not None:
                ghost = font_small.render(drag_sprite.name, True, (255, 240, 180))
                screen.blit(ghost, mouse)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        return 0


if __name__ == "__main__":
    raise SystemExit(GestorInterfazNPCV1().run())
