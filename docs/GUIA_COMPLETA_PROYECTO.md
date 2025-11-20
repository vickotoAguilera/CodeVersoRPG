# Guía Completa del Proyecto RPG

## Estructura del Proyecto

```
RPG/
├── main.py                          # Archivo principal del juego
├── requirements.txt                 # Dependencias de Python
├── settings.json                    # Configuración del juego
│
├── assets/                          # Recursos gráficos y audio
│   ├── backgrounds/                 # Fondos de batalla y pantallas
│   ├── cursor/                      # Cursor del juego
│   ├── heroes/                      # Sprites de héroes
│   ├── mapas/                       # Tiles y mapas del mundo
│   └── monstruos/                   # Sprites de enemigos
│
├── src/                             # Código fuente del juego
│   ├── __init__.py
│   ├── config.py                    # Configuración de rutas
│   ├── constants.py                 # Constantes del juego
│   │
│   ├── heroe.py                     # Clase Héroe (con sistema de efectos)
│   ├── monstruo.py                  # Clase Monstruo (con sistema de efectos)
│   ├── mapa.py                      # Sistema de mapas
│   ├── batalla.py                   # Sistema de batalla (con DOT/HOT)
│   │
│   ├── pantalla_titulo.py           # Pantalla inicial
│   ├── pantalla_slots.py            # Selección de partida
│   ├── menu_pausa.py                # Menú de pausa
│   ├── pantalla_estado.py           # Estado de personajes
│   ├── pantalla_equipo.py           # Gestión de equipo
│   ├── pantalla_habilidades.py      # Gestión de habilidades ⭐ NUEVO
│   ├── pantalla_inventario.py       # Inventario general
│   ├── pantalla_magia.py            # Menú de magia en batalla
│   ├── pantalla_items.py            # Menú de ítems en batalla
│   ├── pantalla_lista_habilidades.py # Menú de habilidades en batalla ⭐ NUEVO
│   ├── pantalla_lista_magias.py     # Lista de magias
│   ├── pantalla_victoria.py         # Pantalla de victoria
│   ├── texto_flotante.py            # Textos flotantes de daño/curación
│   │
│   ├── game_data.py                 # Datos globales del juego
│   ├── gestor_guardado.py           # Sistema de guardado/carga
│   ├── asset_coords_db.py           # Coordenadas de sprites
│   │
│   └── database/                    # Bases de datos JSON
│       ├── heroes_db.json           # Estadísticas de héroes
│       ├── habilidades_db.json      # Habilidades y efectos ⭐ NUEVO
│       ├── magia_db.json            # Hechizos y magias
│       ├── items_db.json            # Ítems y consumibles
│       ├── equipo_db.json           # Equipamiento
│       ├── monstruos_db.json        # Estadísticas de monstruos
│       ├── grupo_inicial.json       # Grupo inicial del jugador
│       │
│       ├── heroes/                  # Información detallada de héroes
│       ├── habilidades/             # (Futuro) Habilidades individuales
│       ├── items/                   # (Futuro) Ítems individuales
│       ├── jobs/                    # (Futuro) Clases y trabajos
│       ├── mapas/                   # Configuración de mapas del mundo
│       ├── monstruos/               # Encuentros por zona
│       ├── npcs/                    # (Futuro) NPCs y diálogos
│       ├── tiendas/                 # (Futuro) Tiendas y comercio
│       ├── misiones/                # (Futuro) Misiones y objetivos
│       ├── animaciones/             # (Futuro) Animaciones especiales
│       └── dialogo/                 # (Futuro) Sistema de diálogos
│
├── saves/                           # Partidas guardadas
│   ├── slot_1.json
│   ├── slot_2.json
│   └── slot_3.json
│
└── docs/                            # Documentación del proyecto
    ├── ESTADO_ACTUAL_SISTEMA.md     # Estado actual detallado
    ├── SISTEMA_DOT_HOT_IMPLEMENTADO.md # Sistema de efectos ⭐ NUEVO
    ├── SISTEMA_HABILIDADES_COMPLETO.md # Sistema de habilidades
    ├── ARQUITECTURA.md              # Arquitectura del juego
    ├── DATABASE.md                  # Estructura de bases de datos
    └── GUIA_COMPLETA_PROYECTO.md    # Este archivo
```

---

## 🎮 Sistemas Implementados

### 1. Sistema de Batalla
**Archivo**: `src/batalla.py`

**Características:**
- Batalla por turnos basada en velocidad
- Múltiples enemigos (1-4)
- Sistema de targeting para héroes y enemigos
- Menú de acciones: Atacar, Habilidades, Magia, Objeto, Huir
- Animaciones de ataque
- Textos flotantes de daño/curación
- Sistema de experiencia y oro
- Pantalla de victoria con recompensas
- **Sistema de efectos DOT/HOT** ⭐ NUEVO

**Estados de Batalla:**
1. `INICIAR_RONDA`: Crea la cola de turnos ordenada por velocidad
2. `PROCESAR_TURNO`: Procesa efectos DOT/HOT y asigna turno al actor
3. `ESPERANDO_INPUT_HEROE`: Espera selección del jugador
4. `HEROE_ELIGE_MONSTRUO`: Selección de objetivo enemigo
5. `JUGADOR_ELIGE_ALIADO`: Selección de objetivo aliado
6. `JUGADOR_ELIGE_MAGIA`: Menú de selección de magia
7. `JUGADOR_ELIGE_ITEM`: Menú de selección de ítem
8. `JUGADOR_ELIGE_HABILIDAD`: Menú de selección de habilidad ⭐ NUEVO
9. `RESOLVIENDO_ACCION`: Ejecuta la acción y muestra animación
10. `VICTORIA`: Muestra recompensas y permite continuar
11. `FIN_BATALLA`: Transición de vuelta al mapa

### 2. Sistema de Habilidades ⭐ NUEVO
**Archivos**: 
- `src/pantalla_habilidades.py`
- `src/pantalla_lista_habilidades.py`
- `src/database/habilidades_db.json`

**Características:**
- 23 habilidades variadas (físicas, mágicas, curativas, DoT, HoT)
- Sistema de ranuras activas (4 por defecto, expandible)
- Inventario de habilidades separado
- Equipar/desequipar habilidades
- Prevención de duplicados
- Sistema de clases (Guerrero, Mago)
- Navegación completa con teclado (4 paneles)
- Integración completa en batalla

**Tipos de Habilidades:**
1. **Físicas**: Corte Cruzado, Golpe Feroz, Tiro Penetrante
2. **Mágicas**: Piro, Hielo, Rayo, Viento, Terremoto, Meteoro
3. **Curativas**: Cura, Cura+, Curaga
4. **AoE**: Piro+, Terremoto, Meteoro, Llamas Infernales
5. **DoT**: Quemadura, Veneno, Sangrado
6. **HoT**: Revitalizar (HP), Éter (MP), Recuperación
7. **Buffs/Debuffs**: Guardia, Escudo Mágico, Berserker

### 3. Sistema de Efectos Temporales ⭐ NUEVO
**Archivos**: 
- `src/heroe.py` (líneas 89-489)
- `src/monstruo.py` (líneas 52-108)
- `src/batalla.py` (líneas 413-467)

**Características:**
- Efectos DOT (Damage Over Time)
- Efectos HOT (Heal Over Time)
- Regeneración de MP
- Múltiples efectos simultáneos
- Expiración automática
- Textos flotantes visuales con colores diferenciados
- Compatible con héroes y monstruos
- Compatible con habilidades AoE

**Tipos de Efectos:**
- `DOT_QUEMADURA`: Fuego (15 daño x 3 turnos)
- `DOT_VENENO`: Veneno (12 daño x 4 turnos)
- `DOT_SANGRADO`: Sangrado (variable)
- `HOT_REGENERACION`: Curación HP (20 HP x 3 turnos)
- `HOT_ETER`: Regeneración MP (10 MP x 3 turnos)

### 4. Sistema de Equipo
**Archivo**: `src/pantalla_equipo.py`

**11 Ranuras de Equipo:**
1. Cabeza (Gorro, Casco)
2. Pecho (Armadura)
3. Piernas (Pantalones)
4. Pies (Botas)
5. Manos (Guantes)
6. Espalda (Capa)
7. Mano Principal (Arma)
8. Mano Secundaria (Escudo)
9. Accesorio 1 (Anillo)
10. Accesorio 2 (Anillo)
11. Accesorio 3 (Collar)

**Características:**
- Equipar/desequipar ítems
- Visualización de stats modificados
- Comparación de stats
- Sprites de ítems
- Restricciones por tipo de ítem

### 5. Sistema de Guardado/Carga
**Archivos**:
- `src/gestor_guardado.py`
- `src/pantalla_slots.py`
- `saves/slot_1.json`, `slot_2.json`, `slot_3.json`

**Características:**
- 3 slots de guardado
- Auto-guardado al pausar
- Información de partida (tiempo, nivel, ubicación)
- Guardado de progreso completo:
  - Posición del jugador
  - Stats de héroes
  - Inventarios
  - Equipo equipado
  - **Habilidades activas** ⭐ NUEVO
  - **Inventario de habilidades** ⭐ NUEVO
  - Oro y experiencia
  - Mapa actual

### 6. Sistema de Mapas
**Archivo**: `src/mapa.py`

**Características:**
- Múltiples mapas conectados
- Sistema de colisiones
- Tiles de transporte entre mapas
- Zonas de encuentro con enemigos
- Cámara centrada en el jugador
- Scroll fluido

### 7. Interfaz de Usuario
**Menú de Pausa**:
- Estado (Ver stats de personajes)
- Equipo (Gestionar equipamiento)
- Habilidades (Gestionar habilidades) ⭐ NUEVO
- Inventario (Ver/usar ítems)
- Guardar (Guardar progreso)
- Continuar (Volver al juego)

**Pantallas Especiales**:
- Pantalla de título
- Selección de slots
- Pantalla de victoria con level up
- Textos flotantes de daño/curación

---

## 📊 Bases de Datos

### heroes_db.json
Define las clases de héroes con:
- Stats base (HP, MP, Fuerza, Defensa, Int, Espíritu)
- Sistema de nivel y experiencia
- Velocidad y suerte (para críticos)
- Clase (Guerrero, Mago)
- Ranuras de habilidades
- **Habilidades activas** ⭐ NUEVO
- **Inventario de habilidades** ⭐ NUEVO
- Magias iniciales
- Ítems iniciales

### habilidades_db.json ⭐ NUEVO
Define las 23 habilidades disponibles:
- ID único
- Nombre y descripción
- Tipo (Física, Mágica, Defensiva)
- Costo de MP
- Poder (daño/curación)
- Alcance (Un Enemigo, Todos Enemigos, Un Aliado, etc.)
- Efecto especial (DOT, HOT, Buffs, etc.)
- Parámetros de efecto (duración, valor)

### magia_db.json
Define hechizos tradicionales:
- Piro, Hielo, Rayo (daño elemental)
- Cura, Curaga (curación)
- Cada magia tiene poder, costo MP, tipo

### items_db.json
Define ítems consumibles:
- Pociones (restauran HP)
- Éteres (restauran MP)
- Efectos especiales
- **Expansor de Ranuras** (añade +2 ranuras) ⭐ NUEVO

### equipo_db.json
Define equipamiento:
- Armas (espadas, bastones, etc.)
- Armaduras (todas las piezas)
- Accesorios (anillos, collares)
- Modificadores de stats

### monstruos_db.json
Define enemigos:
- Stats (HP, Fuerza, Defensa)
- Sprites y escala
- Velocidad y suerte
- Recompensas (XP, oro)

### Mapas
**mapas/ (carpeta con JSONs)**:
- `pueblo_inicio.json`
- `bosque_1.json`
- `cueva_1.json`
- Cada mapa define:
  - Dimensiones
  - Tiles de suelo
  - Muros (colisiones)
  - Puntos de spawn
  - Zonas de encuentro
  - Conexiones con otros mapas

**monstruos/ (carpeta con JSONs)**:
- Define encuentros por zona
- `pueblo_inicio.json`: Sin encuentros
- `bosque_1.json`: Slimes, lobos
- `cueva_1.json`: Murciélagos, arañas
- Probabilidades de aparición

---

## 🎯 Cómo Jugar

### Inicio del Juego
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar juego
python main.py
```

### Controles en el Mapa
- **↑↓←→**: Movimiento
- **ESC**: Abrir menú de pausa

### Controles en Batalla
- **↑↓**: Navegar menú
- **ENTER**: Confirmar selección
- **ESC**: Cancelar/Volver

### Controles en Pantalla de Habilidades ⭐ NUEVO
- **↑↓←→**: Navegar entre paneles
- **ENTER**: Seleccionar habilidad/ranura
- **ESC**: Salir (o botón "Volver")
- **Navegación fluida** entre:
  1. Sprite del héroe
  2. Inventario de habilidades
  3. Ventana de descripción
  4. Ranuras activas

### Flujo de Juego
1. **Inicio**: Pantalla de título
2. **Selección**: Elegir o crear partida (3 slots)
3. **Exploración**: Caminar por el mapa
4. **Encuentros**: Batallas aleatorias en zonas específicas
5. **Batalla**: Combate por turnos
6. **Victoria**: Ganar experiencia, oro y subir de nivel
7. **Progreso**: Continuar explorando
8. **Pausa**: Gestionar equipo, habilidades, inventario
9. **Guardar**: Guardar progreso en cualquier momento

---

## 🔧 Personalización

### Añadir un Nuevo Héroe
1. Editar `src/database/heroes_db.json`
2. Añadir nueva entrada con stats
3. Crear sprites en `assets/heroes/`
4. Añadir coordenadas en `src/asset_coords_db.py`

### Crear una Nueva Habilidad ⭐
1. Editar `src/database/habilidades_db.json`
2. Añadir nueva entrada con:
   ```json
   {
     "id_habilidad": "ID_MI_HABILIDAD",
     "nombre": "Mi Habilidad",
     "tipo": "Magia Negra",
     "descripcion": "Descripción de la habilidad",
     "costo_mp": 10,
     "poder": 30,
     "alcance": "Un Enemigo",
     "efecto": "DOT_QUEMADURA",
     "dot_duracion": 3,
     "dot_dano": 15
   }
   ```
3. Añadir al inventario de héroes que puedan usarla

### Crear un Nuevo Efecto DOT/HOT ⭐
1. Definir nuevo tipo de efecto (ej: `"DOT_CONGELACION"`)
2. Añadir a `habilidades_db.json` con parámetros:
   - `dot_duracion`: Turnos que dura
   - `dot_dano`: Daño por turno
   - `hot_curacion`: Curación por turno (HOT)
   - `hot_mp`: MP por turno (HOT_ETER)
3. El sistema lo procesará automáticamente

### Crear un Nuevo Mapa
1. Crear JSON en `src/database/mapas/`
2. Definir dimensiones, tiles, muros
3. Crear JSON de encuentros en `src/database/monstruos/`
4. Añadir conexiones en mapas existentes

### Añadir un Nuevo Enemigo
1. Editar `src/database/monstruos_db.json`
2. Añadir sprite en `assets/monstruos/`
3. Añadir a encuentros de zona

---

## 🐛 Solución de Problemas

### Error: "NameError: name 'RUTA_ITEMS_DB' is not defined"
**Solución**: Este error ya fue corregido. Asegúrate de que `main.py` carga todas las rutas correctamente.

### El juego no inicia
```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar versión de Python (3.8+)
python --version
```

### No aparecen sprites
- Verificar que `assets/` tiene todos los archivos
- Verificar rutas en `src/config.py`

### La navegación no funciona en Pantalla de Habilidades
- Asegurarse de usar las flechas ↑↓←→
- El botón "Volver" está en la esquina inferior izquierda
- Usar ENTER para seleccionar

### Los efectos DOT/HOT no funcionan ⭐
- Verificar que la habilidad tiene los campos `efecto`, `dot_duracion`, `dot_dano`
- Verificar que la habilidad está en `habilidades_activas` del héroe
- Los efectos se procesan al INICIO del turno del actor afectado

---

## 📈 Estado del Proyecto

### ✅ Completado
- Sistema de batalla completo
- Sistema de habilidades completo ⭐
- Sistema de efectos DOT/HOT ⭐
- Sistema de equipo (11 ranuras)
- Sistema de guardado/carga (3 slots)
- Sistema de mapas con colisiones
- Sistema de experiencia y nivel
- Pantalla de victoria con level up
- Textos flotantes
- Menú de pausa completo
- 23 habilidades funcionales ⭐
- Integración completa en batalla ⭐

### 🔨 En Desarrollo (Fase 8)
- Gestión de grupo (activos vs banca)
- Más héroes (Barret, Tifa, Aerith, etc.)
- Sistema de cambio de líder

### 📋 Planificado (Fases 9-11)
- NPCs y diálogos
- Tiendas y comercio
- Misiones y objetivos
- Sistema de Game Over
- Menú de opciones (resolución, etc.)
- Soporte para gamepad

---

## 📚 Documentación Adicional

- **ESTADO_ACTUAL_SISTEMA.md**: Detalle completo del estado actual
- **SISTEMA_DOT_HOT_IMPLEMENTADO.md**: Guía del sistema de efectos ⭐
- **SISTEMA_HABILIDADES_COMPLETO.md**: Guía del sistema de habilidades
- **ARQUITECTURA.md**: Arquitectura técnica del juego
- **DATABASE.md**: Estructura de todas las bases de datos

---

## 🎉 Conclusión

Este proyecto es un RPG completo y funcional con:
- **Sistema de batalla robusto** con efectos temporales
- **Sistema de habilidades completo** con 23 habilidades
- **Sistema de efectos DOT/HOT** completamente integrado
- **Sistema de progresión** (nivel, equipo, habilidades)
- **Múltiples mapas** para explorar
- **Guardado/carga** con 3 slots

**Todo el sistema está listo para jugar y expandir.** 🎮✨
