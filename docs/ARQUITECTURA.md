# Arquitectura del Proyecto RPG

## Estructura General del Proyecto

```
RPG/
├── main.py                     # Punto de entrada (solo inicialización)
├── requirements.txt            # Dependencias del proyecto
├── settings.json              # Configuración del juego
├── ARQUITECTURA.md            # Este archivo
├── README.md                  # Documentación del proyecto
│
├── src/                       # Código fuente
│   ├── __init__.py
│   ├── config.py              # Configuración de rutas
│   ├── constants.py           # Constantes del juego
│   │
│   ├── core/                  # Núcleo del motor del juego
│   │   ├── __init__.py
│   │   ├── game_engine.py     # Motor principal del juego
│   │   ├── state_machine.py   # Máquina de estados
│   │   ├── resource_manager.py # Gestor de recursos
│   │   ├── input_manager.py   # Gestor de entrada
│   │   └── logger.py          # Sistema de logging
│   │
│   ├── states/                # Estados del juego
│   │   ├── __init__.py
│   │   ├── base_state.py      # Estado base abstracto
│   │   ├── titulo_state.py    # Estado de pantalla título
│   │   ├── mapa_state.py      # Estado de exploración
│   │   ├── batalla_state.py   # Estado de batalla
│   │   ├── menu_pausa_state.py # Estado de menú de pausa
│   │   └── slots_state.py     # Estado de guardado/carga
│   │
│   ├── entities/              # Entidades del juego
│   │   ├── __init__.py
│   │   ├── heroe.py           # Clase Héroe
│   │   ├── monstruo.py        # Clase Monstruo
│   │   └── grupo.py           # Clase Grupo de héroes
│   │
│   ├── systems/               # Sistemas del juego
│   │   ├── __init__.py
│   │   ├── batalla_system.py  # Sistema de combate
│   │   ├── guardado_system.py # Sistema de guardado
│   │   ├── inventario_system.py # Sistema de inventario
│   │   ├── equipo_system.py   # Sistema de equipamiento
│   │   └── progresion_system.py # Sistema de progresión (XP, nivel)
│   │
│   ├── ui/                    # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── base_ui.py         # UI base
│   │   ├── pantalla_titulo.py # Pantalla de título
│   │   ├── pantalla_slots.py  # Pantalla de slots
│   │   ├── menu_pausa.py      # Menú de pausa
│   │   ├── pantalla_estado.py # Pantalla de estado
│   │   ├── pantalla_equipo.py # Pantalla de equipo
│   │   ├── pantalla_inventario.py # Pantalla de inventario
│   │   ├── pantalla_magia.py  # Pantalla de magia
│   │   ├── pantalla_items.py  # Pantalla de items en batalla
│   │   ├── pantalla_victoria.py # Pantalla de victoria
│   │   └── texto_flotante.py  # Texto flotante
│   │
│   ├── world/                 # Mundo del juego
│   │   ├── __init__.py
│   │   ├── mapa.py            # Clase Mapa
│   │   └── zona.py            # Clase Zona
│   │
│   ├── data/                  # Gestión de datos
│   │   ├── __init__.py
│   │   ├── database_manager.py # Gestor de base de datos
│   │   ├── validators.py      # Validadores de JSON
│   │   ├── schemas.py         # Schemas de validación
│   │   └── game_data.py       # Datos del juego
│   │
│   └── utils/                 # Utilidades
│       ├── __init__.py
│       ├── asset_coords_db.py # Coordenadas de sprites
│       └── helpers.py         # Funciones auxiliares
│
├── database/                  # Base de datos del juego
│   ├── heroes_db.json
│   ├── equipo_db.json
│   ├── items_db.json
│   ├── habilidades_db.json
│   ├── magia_db.json
│   ├── monstruos_db.json
│   ├── grupo_inicial.json
│   ├── mapas/                 # Datos de mapas
│   ├── monstruos/             # Encuentros por zona
│   └── schemas/               # Schemas JSON
│
├── assets/                    # Recursos gráficos y audio
│   ├── sprites/
│   ├── maps/
│   ├── backgrounds/
│   ├── ui/
│   └── audio/
│
├── saves/                     # Partidas guardadas
│
├── logs/                      # Archivos de log
│
└── tests/                     # Tests unitarios
    ├── __init__.py
    ├── test_heroe.py
    ├── test_batalla.py
    └── test_guardado.py
```

---

## Descripción de Componentes

### **1. Core (Núcleo)**

#### `game_engine.py`
- **Propósito:** Motor principal del juego
- **Responsabilidades:**
  - Inicializar Pygame
  - Gestionar el bucle principal
  - Coordinar la máquina de estados
  - Gestionar FPS y tiempo
- **Conexiones:** Usa ResourceManager, StateMachine, InputManager

#### `state_machine.py`
- **Propósito:** Gestionar transiciones entre estados
- **Responsabilidades:**
  - Cambiar entre estados (título, mapa, batalla, etc.)
  - Mantener historial de estados
  - Validar transiciones
- **Conexiones:** Usa todos los estados en src/states/

#### `resource_manager.py`
- **Propósito:** Cargar y cachear recursos
- **Responsabilidades:**
  - Cargar JSON con validación
  - Cargar sprites e imágenes
  - Cache de recursos
  - Manejo de errores de carga
- **Conexiones:** Usa database/ y assets/, usado por todo el juego

#### `input_manager.py`
- **Propósito:** Centralizar manejo de entrada
- **Responsabilidades:**
  - Capturar eventos de teclado
  - Mapear teclas a acciones
  - Cooldowns de input
- **Conexiones:** Usado por todos los estados

#### `logger.py`
- **Propósito:** Sistema de logging robusto
- **Responsabilidades:**
  - Escribir logs en archivos
  - Niveles de log (DEBUG, INFO, WARNING, ERROR)
  - Rotación de archivos de log
- **Conexiones:** Usado por todo el sistema

---

### **2. States (Estados)**

#### `base_state.py`
- **Propósito:** Clase abstracta para estados
- **Responsabilidades:**
  - Definir interfaz común (enter, exit, update, draw, handle_input)
  - Proporcionar funcionalidad base
- **Conexiones:** Heredada por todos los estados

#### `titulo_state.py`
- **Propósito:** Pantalla de título
- **Usa:** PantallaTitulo (UI), ResourceManager
- **Transiciones:** → MapaState (nuevo juego), → SlotsState (cargar)

#### `mapa_state.py`
- **Propósito:** Exploración del mundo
- **Usa:** Mapa, Heroe, Grupo
- **Transiciones:** → BatallaState (encuentro), → MenuPausaState (pause)

#### `batalla_state.py`
- **Propósito:** Sistema de combate
- **Usa:** BatallaSystem, Heroe, Monstruo
- **Transiciones:** → MapaState (victoria/huida)

#### `menu_pausa_state.py`
- **Propósito:** Menú de pausa
- **Usa:** MenuPausa (UI), varias pantallas
- **Transiciones:** → MapaState (volver), → SlotsState (guardar/cargar)

#### `slots_state.py`
- **Propósito:** Guardado y carga
- **Usa:** PantallaSlots (UI), GuardadoSystem
- **Transiciones:** → TituloState / MenuPausaState / MapaState

---

### **3. Entities (Entidades)**

#### `heroe.py`
- **Propósito:** Clase Héroe con datos y comportamiento
- **Datos:** Stats, inventario, equipo, posición
- **Conexiones:** Usado por Grupo, estados, sistemas

#### `monstruo.py`
- **Propósito:** Clase Monstruo
- **Datos:** Stats, sprites, recompensas
- **Conexiones:** Usado por BatallaSystem

#### `grupo.py`
- **Propósito:** Gestionar grupo de héroes
- **Responsabilidades:**
  - Mantener lista de héroes
  - Operaciones de grupo (curar todos, verificar vivos)
- **Conexiones:** Usado por MapaState, BatallaState

---

### **4. Systems (Sistemas)**

#### `batalla_system.py`
- **Propósito:** Lógica completa de batalla
- **Responsabilidades:**
  - Turnos de combate
  - Cálculo de daño
  - IA de enemigos
  - Distribución de recompensas
- **Conexiones:** Usa Heroe, Monstruo, ResourceManager

#### `guardado_system.py`
- **Propósito:** Guardar y cargar partidas
- **Responsabilidades:**
  - Serializar estado del juego
  - Deserializar y validar saves
  - Autoguardado
- **Conexiones:** Usa Grupo, Mapa, validators

#### `inventario_system.py`
- **Propósito:** Gestión de inventario
- **Responsabilidades:**
  - Usar items
  - Agregar/quitar items
  - Verificar cantidad
- **Conexiones:** Usa Heroe, ResourceManager

#### `equipo_system.py`
- **Propósito:** Sistema de equipamiento
- **Responsabilidades:**
  - Equipar/desequipar items
  - Calcular stats con equipo
  - Validar compatibilidad
- **Conexiones:** Usa Heroe, ResourceManager

#### `progresion_system.py`
- **Propósito:** Progresión de personajes
- **Responsabilidades:**
  - Ganar XP y subir de nivel
  - Calcular stats por nivel
  - Aprender nuevas habilidades
- **Conexiones:** Usa Heroe, ResourceManager

---

### **5. UI (Interfaz)**

Todas las pantallas tienen:
- **Propósito:** Renderizar y gestionar input de su pantalla específica
- **Responsabilidades:** Draw, update, handle_input
- **Conexiones:** Usadas por los estados correspondientes

---

### **6. World (Mundo)**

#### `mapa.py`
- **Propósito:** Representar un mapa del juego
- **Datos:** Imagen, muros, portales, zonas de batalla
- **Conexiones:** Usado por MapaState

#### `zona.py`
- **Propósito:** Representar zonas del mapa
- **Datos:** Tipo de zona, encuentros posibles
- **Conexiones:** Usado por Mapa

---

### **7. Data (Datos)**

#### `database_manager.py`
- **Propósito:** Interfaz única para acceder a datos
- **Responsabilidades:**
  - Cargar todos los JSON
  - Validar estructura
  - Proporcionar getters
- **Conexiones:** Usado por ResourceManager

#### `validators.py`
- **Propósito:** Validar estructura de datos
- **Responsabilidades:**
  - Verificar campos requeridos
  - Verificar tipos de datos
  - Manejar valores por defecto
- **Conexiones:** Usado por DatabaseManager

#### `schemas.py`
- **Propósito:** Definir schemas de validación
- **Datos:** Diccionarios con estructura esperada de cada JSON
- **Conexiones:** Usado por validators

---

### **8. Utils (Utilidades)**

#### `asset_coords_db.py`
- **Propósito:** Coordenadas de sprites en hojas
- **Datos:** Diccionarios de coordenadas
- **Conexiones:** Usado por Heroe, Monstruo

#### `helpers.py`
- **Propósito:** Funciones auxiliares
- **Funciones:** Cálculos matemáticos, conversiones, etc.
- **Conexiones:** Usado por varios módulos

---

## Flujo de Datos

### **Al Iniciar el Juego:**
1. `main.py` → inicializa `GameEngine`
2. `GameEngine` → carga `ResourceManager`
3. `ResourceManager` → carga `DatabaseManager`
4. `DatabaseManager` → lee y valida todos los JSON
5. `GameEngine` → crea `StateMachine` con estado inicial `TituloState`
6. Bucle principal comienza

### **Durante el Juego:**
1. `GameEngine` pasa control al estado actual
2. Estado procesa input via `InputManager`
3. Estado actualiza lógica (puede usar sistemas)
4. Estado renderiza UI
5. Estado puede solicitar cambio a otro estado

### **Al Guardar:**
1. Usuario activa guardado desde `MenuPausaState`
2. `SlotsState` recibe solicitud
3. `GuardadoSystem` serializa estado actual
4. JSON se escribe en `saves/`

### **Al Cargar:**
1. Usuario selecciona slot desde `SlotsState`
2. `GuardadoSystem` lee y valida JSON
3. `DatabaseManager` reconstruye objetos
4. `StateMachine` cambia a `MapaState` con datos cargados

---

## Patrones de Diseño Utilizados

1. **State Pattern:** Para la máquina de estados
2. **Singleton:** ResourceManager, DatabaseManager
3. **Factory:** Para crear Héroes y Monstruos desde JSON
4. **Observer:** Para eventos del juego
5. **Strategy:** Para IA de monstruos
6. **Facade:** DatabaseManager como fachada de datos

---

## Convenciones de Código

- **Idioma:** Español neutro, sin chilenismos
- **Nombres de clases:** PascalCase (ej: `GameEngine`)
- **Nombres de funciones:** snake_case (ej: `cargar_recursos`)
- **Constantes:** MAYUSCULAS_CON_GUION (ej: `MAX_HEROES`)
- **Privados:** prefijo con un guion bajo (ej: `_inicializar`)
- **Docstrings:** Formato Google Style en español

---

## Sistema de Logging

Niveles de log:
- **DEBUG:** Información detallada para debugging
- **INFO:** Eventos importantes del juego
- **WARNING:** Situaciones inesperadas pero manejables
- **ERROR:** Errores que impiden operaciones específicas
- **CRITICAL:** Errores que impiden continuar el juego

Ubicación: `logs/game_YYYY-MM-DD.log`

---

## Testing

Cada módulo crítico tiene tests en `tests/`:
- Tests unitarios con mocks de Pygame
- Tests de integración para flujos completos
- Cobertura mínima del 70%

Ejecutar tests: `python -m pytest tests/`

---

Este documento será actualizado conforme el proyecto evolucione.
