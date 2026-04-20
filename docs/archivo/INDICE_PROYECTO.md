# Índice Completo del Proyecto - Code Verso RPG

Este documento lista TODOS los archivos del proyecto, su propósito y estado.

---

## 📚 Documentación (Raíz del proyecto)

| Archivo | Tamaño | Estado | Descripción |
|---------|--------|--------|-------------|
| INICIO_RAPIDO.md | 10 KB | ✅ Completo | Guía rápida para empezar |
| README.md | 8 KB | ✅ Completo | Documentación principal |
| ARQUITECTURA.md | 12 KB | ✅ Completo | Diseño del sistema |
| DATABASE.md | 18 KB | ✅ Completo | Estructura de datos |
| REFACTORIZACION.md | 18 KB | ✅ Completo | Plan de trabajo |
| RESUMEN_CAMBIOS.md | 14 KB | ✅ Completo | Qué se ha hecho |
| INDICE_PROYECTO.md | - | ✅ Completo | Este archivo |

**Total:** 6 documentos principales

---

## ⚙️ Configuración (Raíz del proyecto)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| main.py | ✅ Funcional | Punto de entrada (código antiguo) |
| requirements.txt | ✅ Completo | Dependencias del proyecto |
| settings.json | ✅ Completo | Configuración del juego |
| .gitignore | ✅ Completo | Archivos ignorados por Git |
| setup_structure.py | ✅ Completo | Script para crear directorios |
| crear_estructura_completa.py | ✅ Completo | Script de organización |

---

## 🔧 src/ - Código Fuente

### src/ (Raíz)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| __init__.py | ✅ | Módulo principal |
| config.py | ✅ Funcional | Configuración de rutas |
| constants.py | ✅ Completo | Todas las constantes |

### src/core/ - Motor del Juego

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 15 |
| logger.py | ⏳ Crear | Sistema de logging | 150 |
| resource_manager.py | ⏳ Crear | Gestor de recursos | 200 |
| input_manager.py | ⏳ Crear | Gestor de entrada | 150 |
| state_machine.py | ⏳ Crear | Máquina de estados | 180 |
| game_engine.py | ⏳ Crear | Motor principal | 250 |

**Total estimado:** ~945 líneas

### src/states/ - Estados del Juego

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| base_state.py | ⏳ Crear | Estado base abstracto | 80 |
| titulo_state.py | ⏳ Crear | Estado pantalla título | 120 |
| mapa_state.py | ⏳ Crear | Estado exploración | 250 |
| batalla_state.py | ⏳ Crear | Estado de batalla | 200 |
| menu_pausa_state.py | ⏳ Crear | Estado menú pausa | 180 |
| slots_state.py | ⏳ Crear | Estado guardar/cargar | 150 |

**Total estimado:** ~990 líneas

### src/entities/ - Entidades del Juego

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| heroe.py | 🔄 Refactorizar | Clase Héroe | 450 |
| monstruo.py | 🔄 Refactorizar | Clase Monstruo | 150 |
| grupo.py | ⏳ Crear | Grupo de héroes | 120 |

**Total estimado:** ~730 líneas

### src/systems/ - Sistemas del Juego

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| batalla_system.py | 🔄 Refactorizar | Sistema de combate | 500 |
| guardado_system.py | 🔄 Refactorizar | Sistema de guardado | 200 |
| inventario_system.py | ⏳ Crear | Sistema de inventario | 180 |
| equipo_system.py | ⏳ Crear | Sistema de equipo | 200 |
| progresion_system.py | ⏳ Crear | Sistema de XP/nivel | 150 |

**Total estimado:** ~1,240 líneas

### src/ui/ - Interfaces de Usuario

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| base_ui.py | ⏳ Crear | UI base | 100 |
| pantalla_titulo.py | 🔄 Refactorizar | Pantalla título | 150 |
| pantalla_slots.py | 🔄 Refactorizar | Pantalla slots | 200 |
| menu_pausa.py | 🔄 Refactorizar | Menú pausa | 250 |
| pantalla_estado.py | 🔄 Refactorizar | Pantalla estado | 200 |
| pantalla_equipo.py | 🔄 Refactorizar | Pantalla equipo | 300 |
| pantalla_inventario.py | 🔄 Refactorizar | Pantalla inventario | 250 |
| pantalla_magia.py | 🔄 Refactorizar | Pantalla magia | 200 |
| pantalla_items.py | 🔄 Refactorizar | Pantalla items | 200 |
| pantalla_victoria.py | 🔄 Refactorizar | Pantalla victoria | 250 |
| texto_flotante.py | 🔄 Refactorizar | Texto flotante | 80 |

**Total estimado:** ~2,190 líneas

### src/world/ - Mundo del Juego

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| mapa.py | 🔄 Refactorizar | Clase Mapa | 250 |
| zona.py | ⏳ Crear | Clase Zona | 80 |

**Total estimado:** ~340 líneas

### src/data/ - Gestión de Datos

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| database_manager.py | ⏳ Crear | Gestor de BD | 250 |
| validators.py | ⏳ Crear | Validadores | 200 |
| schemas.py | ⏳ Crear | Schemas JSON | 300 |
| game_data.py | 🔄 Refactorizar | Datos del juego | 100 |

**Total estimado:** ~860 líneas

### src/utils/ - Utilidades

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Exports del módulo | 10 |
| asset_coords_db.py | 🔄 Mover | Coordenadas sprites | 250 |
| helpers.py | ⏳ Crear | Funciones auxiliares | 150 |

**Total estimado:** ~410 líneas

### Archivos Antiguos en src/ (A refactorizar/deprecar)

| Archivo | Estado | Acción |
|---------|--------|--------|
| batalla.py | 🔄 | Migrar a systems/ y states/ |
| heroe.py | 🔄 | Migrar a entities/ |
| monstruo.py | 🔄 | Migrar a entities/ |
| mapa.py | 🔄 | Migrar a world/ |
| gestor_guardado.py | 🔄 | Migrar a systems/ |
| pantalla_*.py (10 archivos) | 🔄 | Migrar a ui/ |
| asset_coords_db.py | 🔄 | Migrar a utils/ |
| game_data.py | 🔄 | Migrar a data/ |
| texto_flotante.py | 🔄 | Migrar a ui/ |

---

## 💾 database/ - Base de Datos

### database/ (Raíz)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| heroes_db.json | ✅ | Definiciones de héroes |
| equipo_db.json | ✅ | Armas y armaduras |
| items_db.json | ✅ | Items consumibles |
| habilidades_db.json | ✅ | Habilidades físicas |
| magia_db.json | ✅ | Hechizos mágicos |
| monstruos_db.json | ✅ | Definiciones de enemigos |
| grupo_inicial.json | ✅ | Grupo inicial |

### database/mapas/ - Datos de Mapas

| Carpeta | Estado | Descripción |
|---------|--------|-------------|
| mundo/ | ✅ | Mapas del overworld |
| pueblo_inicial/ | ✅ | Edificios del pueblo |

### database/monstruos/ - Encuentros

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| pradera.json | ✅ | Encuentros en pradera |
| bosque.json | ⏳ | Encuentros en bosque |
| cueva.json | ⏳ | Encuentros en cueva |
| default.json | ✅ | Encuentros por defecto |

### database/schemas/ - Validación

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| heroe_schema.json | ⏳ Crear | Schema de héroe |
| item_schema.json | ⏳ Crear | Schema de item |
| monstruo_schema.json | ⏳ Crear | Schema de monstruo |

---

## 🖼️ assets/ - Recursos Gráficos

### assets/sprites/

| Carpeta | Estado | Contenido |
|---------|--------|-----------|
| heroes/ | ✅ | Sprites de héroes |
| monstruos/ | ✅ | Sprites de enemigos |

### assets/maps/

| Carpeta | Estado | Contenido |
|---------|--------|-----------|
| mundo/ | ✅ | Imágenes de mapas overworld |
| pueblo_inicial/ | ✅ | Imágenes de edificios |

### assets/backgrounds/

| Contenido | Estado |
|-----------|--------|
| Fondos de batalla | ✅ |

### assets/ui/

| Contenido | Estado |
|-----------|--------|
| Cursor, iconos | ✅ |

### assets/audio/

| Carpeta | Estado | Contenido |
|---------|--------|-----------|
| music/ | ⏳ | Música del juego |
| sfx/ | ⏳ | Efectos de sonido |

---

## 💿 saves/ - Partidas Guardadas

| Archivo | Descripción |
|---------|-------------|
| save_1.json | Slot 1 (generado por usuario) |
| save_2.json | Slot 2 (generado por usuario) |
| save_3.json | Slot 3 (autoguardado) |
| .gitkeep | Mantener carpeta en Git |

---

## 📊 logs/ - Archivos de Log

| Archivo | Descripción |
|---------|-------------|
| game_YYYY-MM-DD.log | Log del día actual |
| game_YYYY-MM-DD.log.1 | Backup rotado |
| .gitkeep | Mantener carpeta en Git |

---

## 🧪 tests/ - Tests Unitarios

| Archivo | Estado | Descripción | Líneas Est. |
|---------|--------|-------------|-------------|
| __init__.py | ⏳ Crear | Módulo tests | 5 |
| conftest.py | ⏳ Crear | Configuración pytest | 50 |
| test_heroe.py | ⏳ Crear | Tests de Heroe | 200 |
| test_monstruo.py | ⏳ Crear | Tests de Monstruo | 150 |
| test_batalla.py | ⏳ Crear | Tests de Batalla | 300 |
| test_guardado.py | ⏳ Crear | Tests de Guardado | 200 |
| test_inventario.py | ⏳ Crear | Tests de Inventario | 150 |
| test_equipo.py | ⏳ Crear | Tests de Equipo | 150 |
| test_resource_manager.py | ⏳ Crear | Tests de Resources | 150 |
| test_validators.py | ⏳ Crear | Tests de Validación | 150 |

**Total estimado:** ~1,505 líneas

---

## 📈 Resumen de Código

### Archivos Completados

- **Documentación:** 6 archivos (80 KB)
- **Configuración:** 6 archivos
- **Constantes:** 1 archivo (constants.py)
- **Base de datos:** 7 archivos JSON principales

### Archivos a Crear

- **Core:** 5 archivos (~945 líneas)
- **States:** 6 archivos (~990 líneas)
- **Entities:** 1 archivo nuevo + 2 refactorizar (~730 líneas)
- **Systems:** 3 nuevos + 2 refactorizar (~1,240 líneas)
- **UI:** 1 nuevo + 10 refactorizar (~2,190 líneas)
- **World:** 1 archivo nuevo + 1 refactorizar (~340 líneas)
- **Data:** 3 nuevos + 1 refactorizar (~860 líneas)
- **Utils:** 1 nuevo + 1 mover (~410 líneas)
- **Tests:** 10 archivos (~1,505 líneas)

### Total Líneas de Código

- **Existente:** ~8,000 líneas
- **A crear/refactorizar:** ~9,210 líneas
- **Total proyectado:** ~12,000 líneas (más organizado)

---

## 🎯 Estado del Proyecto

### ✅ Fase 1: Preparación (100%)

- [x] Documentación completa
- [x] Configuración y constantes
- [x] Scripts de setup
- [x] Errores críticos corregidos
- [x] Estructura planificada

### 🔄 Fase 2: Core (0%)

- [ ] logger.py
- [ ] resource_manager.py
- [ ] input_manager.py
- [ ] state_machine.py
- [ ] game_engine.py

### ⏳ Fases Restantes (0%)

- [ ] Fase 3: Entities (0%)
- [ ] Fase 4: Systems (0%)
- [ ] Fase 5: States (0%)
- [ ] Fase 6: UI (0%)
- [ ] Fase 7: Data (0%)
- [ ] Fase 8: Testing (0%)
- [ ] Fase 9: Migración Final (0%)

---

## 📋 Leyenda

- ✅ **Completo** - Archivo terminado y funcional
- 🔄 **Refactorizar** - Existe pero necesita mejoras
- ⏳ **Crear** - No existe, debe crearse
- 🚫 **Deprecado** - Será reemplazado

---

## 🔗 Referencias

Para más información:

- **Cómo empezar:** INICIO_RAPIDO.md
- **Arquitectura:** ARQUITECTURA.md
- **Datos:** DATABASE.md
- **Plan de trabajo:** REFACTORIZACION.md
- **Cambios:** RESUMEN_CAMBIOS.md

---

**Última actualización:** 2025-11-15  
**Versión:** 1.0  
**Total de archivos documentados:** 100+
