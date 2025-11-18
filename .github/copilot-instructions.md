# Code Verso RPG - AI Coding Agent Instructions

## Project Overview

A 2D turn-based RPG built with Pygame featuring a state-driven architecture, JSON-based content system, and comprehensive battle/progression mechanics. ~8,000 lines of Python code across 23+ files.

## Critical Architecture

### State Management Pattern
The game uses a **manual state machine** in `main.py` with string-based states:
- States: `"titulo"`, `"mapa"`, `"batalla"`, `"menu_pausa"`, `"slots_carga"`, `"slots_guardar"`, `"pantalla_estado"`, `"pantalla_equipo"`, `"pantalla_inventario"`, `"pantalla_habilidades"`
- State transitions are managed via `estado_juego` variable and event-driven input
- Each state has its own update/draw/input handling in the main loop

### JSON Database System
All game data lives in `src/database/` as JSON files:
- **heroes_db.json**: Character classes with stats, initial items, skills
- **habilidades_db.json**: 23 abilities (physical, magical, AoE, DoT/HoT, buffs)
- **items_db.json**: Consumables with effects
- **equipo_db.json**: Equipment with `ranuras_que_ocupa` defining slot requirements
- **monstruos_db.json** + **monstruos/*.json**: Enemy stats and zone encounters

Key pattern: IDs use `MAYUSCULAS_CON_GUION` format (e.g., `HEROE_1`, `POCION_BASICA`)

### Hero System (`src/heroe.py`)
- Stats split into `_base` (from class) and computed totals (base + equipment bonuses)
- Equipment system uses 11 slots: `cabeza`, `pecho`, `piernas`, `pies`, `manos`, `espalda`, `mano_principal`, `mano_secundaria`, `accesorio1/2/3`
- Skills: `ranuras_habilidad_max_base` defines active slots, `habilidades_activas` (list with nulls), `inventario_habilidades` (all learned)
- Three inventory types: `inventario` (consumables), `inventario_especiales` (key items), `magias` (spells)
- DoT/HoT effects tracked in `efectos_activos`: `[{"tipo": "DOT_QUEMADURA", "duracion": 3, "valor": 15}, ...]`

### Battle System (`src/batalla.py`)
- Turn-based with hero/monster queues
- Supports: single-target attacks, AoE, DoT/HoT application/ticking, MP consumption
- Sub-screens: `PantallaMagia`, `PantallaItems`, `PantallaListaHabilidades` (all with scroll support)
- Enemies positioned dynamically via `calcular_posiciones_monstruos()` for 1-4 enemies

### Save System (`src/gestor_guardado.py`)
- Saves to `saves/slot_X.json` (X = 1-3, plus auto-save slot 3)
- Serializes entire game state: hero stats/inventories/positions, map location, playtime
- Auto-save every 10 minutes (`INTERVALO_AUTOGUARDADO`)

## Development Workflows

### Running the Game
```bash
python main.py
```
No build step. Pygame must be installed: `pip install pygame`

### Testing Changes
- No automated test suite exists
- Manual testing via: start game → ESC for pause menu → navigate to relevant screen
- Skills testing: Pause → Heroes → select hero → Habilidades
- Battle testing: walk on non-safe zones to trigger encounters

### Asset Coordination
Sprite coordinates defined in `src/asset_coords_db.py`:
- Heroes: `COORDS_CLOUD`, `COORDS_TERRA` (walking animations, battle poses)
- Load from `assets/sprites/heroes/` via `HEROES_SPRITES_PATH`
- Maps: `assets/maps/`, backgrounds: `assets/backgrounds/`

### Git Workflow
Custom batch scripts (Windows-focused):
- **git_push_rapido.bat**: Auto-organizes docs, commits with timestamp, pushes
- **git_push.bat**: Same but prompts for commit message
- **organizar_docs.bat**: Runs `organizar_docs.py` to move .md/.txt files to `docs/`

## Code Conventions

### Language & Style
- **Spanish neutral** throughout (no Chilean slang like "bkn", "pilla")
- Classes: `PascalCase` (`PantallaHabilidades`)
- Functions: `snake_case` (`cargar_recursos`)
- Constants: `MAYUSCULAS_CON_GUION` (`HP_MAX_BASE`)
- Private methods: `_prefixed` (`_cargar_sprites`)

### Input Handling Pattern
Events processed in `main.py` main loop:
```python
for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # State-specific ESC logic
        if event.key == pygame.K_RETURN:
            # State-specific ENTER logic (often returns action dict)
```
UI classes return action dictionaries: `{"accion": "volver_menu_pausa", "indice_heroe": 0}`

### UI Scroll Pattern
Many screens implement vertical scroll (inventory, skills, equipment):
- `indice_scroll` tracks top visible item
- `ITEMS_VISIBLES` constant (typically 6)
- Arrow keys move `cursor_indice`, auto-adjust `indice_scroll` when cursor exits visible range
- Render logic: `for i in range(indice_scroll, min(indice_scroll + ITEMS_VISIBLES, len(lista)))`

### Comments Style
Extensive inline comments in Spanish:
```python
# --- Cargar Bases de Datos Globales ---
# ¡NUEVO! Sistema de Habilidades (Paso 7.14)
```
Marker comments for changes: `# ¡NUEVO!`, `# (Sin cambios)`, `# --- FIN BLOQUE ---`

## Common Pitfalls

1. **Unicode Characters**: Avoid in UI strings (pygame font compatibility issues). Use ASCII: `[C]` not `⚗️`
2. **Stats Calculation**: Always compute from `_base` + equipment bonuses, never modify base directly
3. **Slot Conflicts**: Equipment can occupy multiple slots (`ranuras_que_ocupa`). Check before equipping.
4. **Null Skills**: `habilidades_activas` contains `null` for empty slots. Handle explicitly.
5. **Relative Paths**: Use `config.py` constants (`DATABASE_PATH`, `HEROES_SPRITES_PATH`) via `os.path.join()`, never hardcode
6. **State Leakage**: Reset sub-screen objects to `None` when exiting states (e.g., `mi_pantalla_habilidades = None`)

## Integration Points

### Adding New Hero
1. Add entry to `src/database/heroes_db.json` with class/stats/initial items
2. Define sprite coords in `src/asset_coords_db.py` (e.g., `COORDS_NEW_HERO`)
3. Update `grupo_inicial.json` to include in starting party
4. Add sprite sheet to `assets/sprites/heroes/`

### Adding New Skill
1. Add to `src/database/habilidades_db.json`: type (`"fisica"`/`"magica"`), target (`"enemigo"`/`"aliado"`/`"grupo_enemigo"`), MP cost, effects
2. Add to hero's `inventario_habilidades` in `heroes_db.json`
3. Battle execution in `src/batalla.py` → `_ejecutar_habilidad()` handles targeting/damage/effects

### Adding New Item
1. `src/database/items_db.json` or `equipo_db.json`
2. For equipment: specify `tipo`, `ranuras_que_ocupa`, `stats` bonuses
3. For consumables: `objetivo` (self/aliado/grupo), `efectos` dict (hp/mp restoration)

## Key Files Reference

- **main.py**: 8-channel event handling, state machine, auto-save logic
- **src/heroe.py**: 731 lines, stats system, equipment slots, DoT/HoT tracking
- **src/batalla.py**: 1221 lines, turn order, skill execution, reward distribution
- **src/pantalla_habilidades.py**: Skill equipping UI with scroll (3 panels: equipped/inventory/details)
- **docs/DATABASE.md**: Comprehensive database schema reference (690 lines)
- **docs/ARQUITECTURA.md**: Architecture deep-dive with planned refactor (unimplemented)

## Project Status

**Phase 7 Complete** (90% - Skills System): Abilities implemented with equip/unequip, DoT/HoT, AoE targeting, slot expansion items.

**Pending**: Character management, full equipment system, shops, more content. See `docs/ESTADO_ACTUAL_SISTEMA.md` for detailed status.
