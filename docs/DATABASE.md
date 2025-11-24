# Documentación de Base de Datos - Code Verso RPG

Este documento describe todos los archivos de la base de datos del juego, su estructura, propósito y relaciones.

---

## Índice

1. [Visión General](#visión-general)
2. [Archivos Principales](#archivos-principales)
3. [Estructura de Datos](#estructura-de-datos)
4. [Relaciones entre Archivos](#relaciones-entre-archivos)
5. [Guías de Uso](#guías-de-uso)

---

## Visión General

La base de datos del juego está compuesta por archivos JSON que definen:
- **Personajes:** Héroes jugables
- **Equipo:** Armas, armaduras y accesorios
- **Items:** Objetos consumibles
- **Habilidades:** Ataques especiales físicos
- **Magia:** Hechizos mágicos
- **Monstruos:** Enemigos del juego
- **Mapas:** Configuración de niveles
- **Configuración:** Grupos iniciales, encuentros, etc.

---

## Archivos Principales

### 1. heroes_db.json

**Ubicación:** `database/heroes_db.json`  
**Propósito:** Define las clases de héroes jugables con sus estadísticas base  
**Usado por:** 
- `src/entities/heroe.py` - Crea instancias de héroes
- `src/systems/guardado_system.py` - Para reconstruir héroes al cargar
- `main.py` - Al crear nuevo juego

**Estructura:**
```json
{
    "ID_HEROE": {
        "nombre_clase": "Nombre del héroe",
        "hp_max": 100,
        "mp_max": 50,
        "fuerza": 10,
        "defensa": 5,
        "inteligencia": 8,
        "espiritu": 6,
        "velocidad_base": 7,
        "suerte_base": 5,
        "nivel": 1,
        "oro_inicial": 0,
        "experiencia_actual": 0,
        "experiencia_siguiente_nivel": 100,
        "magias_iniciales": ["ID_MAGIA1", "ID_MAGIA2"],
        "items_iniciales": {
            "ID_ITEM": cantidad
        },
        "clase": "Guerrero",
        "ranuras_habilidad_max": 4,
        "habilidades_activas": ["ID_HAB1", null, null, null],
        "inventario_habilidades": ["ID_HAB1", "ID_HAB2"]
    }
}
```

**Campos:**
- `nombre_clase`: Nombre de la clase del héroe
- `hp_max/mp_max`: Puntos de vida y maná máximos
- `fuerza/defensa/etc`: Estadísticas base
- `magias_iniciales`: Lista de IDs de magias que conoce al inicio
- `items_iniciales`: Diccionario con items y cantidades iniciales
- `clase`: Tipo de clase (Guerrero, Mago, etc.)
- `habilidades_activas`: Habilidades equipadas (null = vacío)
- `inventario_habilidades`: Todas las habilidades aprendidas

**Relaciones:**
- → `magia_db.json` (via `magias_iniciales`)
- → `items_db.json` y `equipo_db.json` (via `items_iniciales`)
- → `habilidades_db.json` (via `habilidades_activas` e `inventario_habilidades`)
- → `utils/asset_coords_db.py` (para sprites)

---

### 2. equipo_db.json

**Ubicación:** `database/equipo_db.json`  
**Propósito:** Define armas, armaduras y accesorios equipables  
**Usado por:**
- `src/entities/heroe.py` - Para calcular stats con equipo
- `src/systems/equipo_system.py` - Equipar/desequipar items
- `src/ui/pantalla_equipo.py` - Mostrar equipo disponible

**Estructura:**
```json
{
    "ID_EQUIPO": {
        "id_equipo": "ID_EQUIPO",
        "nombre": "Nombre del Item",
        "tipo": "Arma (1 Mano)" | "Arma (2 Manos)" | "Escudo" | "Cabeza" | "Pecho" | "Piernas" | "Pies" | "Manos" | "Espalda" | "Accesorio",
        "ranuras_que_ocupa": ["mano_principal", "mano_secundaria"],
        "stats": {
            "fuerza": 5,
            "defensa": 0,
            "inteligencia": 0,
            "espiritu": 0,
            "velocidad": -1,
            "suerte": 0,
            "hp_max": 0,
            "mp_max": 0
        },
        "descripcion": "Descripción del item"
    }
}
```

**Tipos de Equipo:**
- **Arma (1 Mano):** Ocupa `mano_principal`
- **Arma (2 Manos):** Ocupa `mano_principal` y `mano_secundaria`
- **Escudo:** Ocupa `mano_secundaria`
- **Cabeza:** Ocupa `cabeza`
- **Pecho:** Ocupa `pecho`
- **Piernas:** Ocupa `piernas`
- **Pies:** Ocupa `pies`
- **Manos:** Ocupa `manos`
- **Espalda:** Ocupa `espalda`
- **Accesorio:** Ocupa `accesorio1`, `accesorio2` o `accesorio3`

**Relaciones:**
- ← `heroes_db.json` (items iniciales)
- ← `src/entities/heroe.py` (equipo actual)

---

### 3. items_db.json

**Ubicación:** `database/items_db.json`  
**Propósito:** Define items consumibles (pociones, éteres, etc.)  
**Usado por:**
- `src/systems/inventario_system.py` - Usar items
- `src/ui/pantalla_inventario.py` - Mostrar inventario
- `src/ui/pantalla_items.py` - Items en batalla

**Estructura:**
```json
{
    "ID_ITEM": {
        "id_item": "ID_ITEM",
        "nombre": "Poción",
        "descripcion": "Restaura 50 HP a un aliado",
        "tipo": "Consumible",
        "efecto": "RESTAURA_HP" | "RESTAURA_MP" | "CURA_VENENO" | etc,
        "poder": 50,
        "target": "Aliado" | "Enemigo" | "Todos Aliados" | etc
    }
}
```

**Efectos Disponibles:**
- `RESTAURA_HP`: Restaura puntos de vida
- `RESTAURA_MP`: Restaura puntos de maná
- `CURA_VENENO`: Cura envenenamiento
- `CURA_PARALISIS`: Cura parálisis
- `REVIVE`: Revive a un aliado caído

**Relaciones:**
- ← `heroes_db.json` (items iniciales)
- ← `src/entities/heroe.py` (inventario actual)

---

### 4. habilidades_db.json

**Ubicación:** `database/habilidades_db.json`  
**Propósito:** Define habilidades físicas especiales  
**Usado por:**
- `src/entities/heroe.py` - Habilidades del héroe
- `src/systems/batalla_system.py` - Usar habilidades en combate
- `src/ui/pantalla_lista_magias.py` - Mostrar habilidades

**Estructura:**
```json
{
    "ID_HABILIDAD": {
        "id_habilidad": "ID_HABILIDAD",
        "nombre": "Corte Cruzado",
        "tipo": "Habilidad Fisica" | "Habilidad Defensa" | "Habilidad Especial",
        "descripcion": "Descripción de la habilidad",
        "costo_mp": 5,
        "poder": 25,
        "alcance": "Un Enemigo" | "Todos Enemigos" | "Usuario",
        "efecto": null | "IGNORA_DEFENSA" | "BUFF_DEFENSA" | etc
    }
}
```

**Tipos de Habilidad:**
- **Habilidad Fisica:** Ataques físicos especiales
- **Habilidad Defensa:** Aumentan defensa o reducen daño
- **Habilidad Especial:** Efectos únicos

**Relaciones:**
- ← `heroes_db.json` (habilidades iniciales)
- ← `src/entities/heroe.py` (habilidades aprendidas)

---

### 5. magia_db.json

**Ubicación:** `database/magia_db.json`  
**Propósito:** Define hechizos mágicos  
**Usado por:**
- `src/entities/heroe.py` - Magias conocidas
- `src/systems/batalla_system.py` - Lanzar hechizos
- `src/ui/pantalla_magia.py` - Menú de magia en batalla

**Estructura:**
```json
{
    "ID_MAGIA": {
        "id_magia": "ID_MAGIA",
        "nombre": "Cura",
        "descripcion": "Restaura HP a un aliado",
        "costo_mp": 5,
        "tipo": "Curacion" | "Ataque" | "Buff" | "Debuff",
        "poder": 50,
        "target": "Aliado" | "Enemigo" | "Todos Aliados" | "Todos Enemigos"
    }
}
```

**Tipos de Magia:**
- **Curacion:** Restaura HP/MP o cura estados
- **Ataque:** Daña enemigos
- **Buff:** Mejora stats de aliados
- **Debuff:** Reduce stats de enemigos

**Relaciones:**
- ← `heroes_db.json` (magias iniciales)
- ← `src/entities/heroe.py` (magias conocidas)

---

### 6. monstruos_db.json

**Ubicación:** `database/monstruos_db.json`  
**Propósito:** Define todos los enemigos del juego  
**Usado por:**
- `src/entities/monstruo.py` - Crear instancias de monstruos
- `src/systems/batalla_system.py` - Generar encuentros
- Archivos en `database/monstruos/` (listas de encuentros)

**Estructura:**
```json
{
    "id_monstruo": {
        "nombre": "Slime",
        "hp": 30,
        "fuerza": 6,
        "defensa": 2,
        "velocidad": 6,
        "suerte": 5,
        "sprite_archivo": "dragon_prueba.png",
        "escala_sprite": 1.5,
        "xp_otorgada": 10,
        "oro_otorgado": 5
    }
}
```

**Campos:**
- `nombre`: Nombre del monstruo
- `hp`: Puntos de vida
- `fuerza/defensa/velocidad/suerte`: Stats de combate
- `sprite_archivo`: Archivo de imagen en `assets/sprites/monstruos/`
- `escala_sprite`: Multiplicador de tamaño
- `xp_otorgada`: Experiencia que otorga al derrotarlo
- `oro_otorgado`: Oro que otorga al derrotarlo

**Relaciones:**
- ← `database/monstruos/*.json` (encuentros por zona)
- ← `src/systems/batalla_system.py`

---

### 7. grupo_inicial.json

**Ubicación:** `database/grupo_inicial.json`  
**Propósito:** Define la composición del grupo al iniciar nuevo juego  
**Usado por:**
- `main.py` - Al crear nuevo juego
- Estados que inician nueva partida

**Estructura:**
```json
{
    "miembros": [
        {
            "nombre_en_juego": "Cloud",
            "id_clase_db": "HEROE_1",
            "id_coords_db": "COORDS_CLOUD"
        },
        {
            "nombre_en_juego": "Terra",
            "id_clase_db": "HEROE_2",
            "id_coords_db": "COORDS_TERRA"
        }
    ]
}
```

**Campos:**
- `nombre_en_juego`: Nombre personalizado del héroe
- `id_clase_db`: ID en `heroes_db.json`
- `id_coords_db`: ID en `asset_coords_db.py` para sprites

**Relaciones:**
- → `heroes_db.json` (via `id_clase_db`)
- → `src/utils/asset_coords_db.py` (via `id_coords_db`)

---

### 8. Archivos de Mapas

**Ubicación:** `database/mapas/[categoria]/[nombre_mapa].json`  
**Propósito:** Define colisiones, portales y zonas de cada mapa  
**Usado por:**
- `src/world/mapa.py` - Cargar configuración del mapa
- `src/states/mapa_state.py` - Gestionar exploración

**Estructura:**
```json
{
    "muros": [
        {"x": 0, "y": 0, "w": 100, "h": 20}
    ],
    "portales": [
        {
            "caja": {"x": 400, "y": 500, "w": 50, "h": 10},
            "mapa_destino": "mapa_pueblo_final.png",
            "categoria_destino": "pueblo_inicial",
            "pos_destino": [400, 100]
        }
    ],
    "zonas_batalla": [
        {
            "x": 100,
            "y": 100,
            "w": 500,
            "h": 400,
            "tipo": "pradera"
        }
    ]
}
```

**Secciones:**
- **muros:** Rectángulos de colisión (el héroe no puede atravesarlos)
- **portales:** Puntos de teletransporte a otros mapas
- **zonas_batalla:** Áreas donde pueden ocurrir encuentros aleatorios

**Categorías de Mapas:**
- `mundo/` - Mapas del overworld
- `pueblo_inicial/` - Edificios del primer pueblo
- `mazmorras/` - Dungeons y cuevas
- etc.

**Relaciones:**
- → Imágenes en `assets/maps/[categoria]/`
- → `database/monstruos/[tipo_zona].json` (para encuentros)

---

### 9. Archivos de Encuentros

**Ubicación:** `database/monstruos/[zona].json`  
**Propósito:** Define qué monstruos aparecen en cada tipo de zona  
**Usado por:**
- `src/systems/batalla_system.py` - Generar encuentros aleatorios

**Estructura:**
```json
{
    "zona": "pradera",
    "encuentros": [
        "slime",
        "murcielago",
        "lobo"
    ]
}
```

**Zonas Disponibles:**
- `pradera.json` - Campos abiertos
- `bosque.json` - Zonas boscosas
- `cueva.json` - Cuevas y cavernas
- `montaña.json` - Zonas montañosas
- `default.json` - Fallback si no se encuentra zona específica

**Relaciones:**
- → `monstruos_db.json` (lista de IDs de monstruos)
- ← Archivos de mapas (via tipo de zona_batalla)

---

## Relaciones entre Archivos

### Diagrama de Dependencias

```
grupo_inicial.json
    ↓
heroes_db.json
    ↓
    ├→ magia_db.json
    ├→ items_db.json
    ├→ equipo_db.json
    └→ habilidades_db.json

mapas/[cat]/[mapa].json
    ↓
monstruos/[zona].json
    ↓
monstruos_db.json
```

### Flujo de Creación de Nuevo Juego

1. Se lee `grupo_inicial.json`
2. Para cada miembro:
   - Se busca `id_clase_db` en `heroes_db.json`
   - Se cargan `magias_iniciales` desde `magia_db.json`
   - Se cargan `items_iniciales` desde `items_db.json` y `equipo_db.json`
   - Se cargan `habilidades` desde `habilidades_db.json`
   - Se cargan coordenadas de sprites desde `asset_coords_db.py`
3. Se crea el mapa inicial
   - Se lee el JSON del mapa desde `database/mapas/`
   - Se carga la imagen desde `assets/maps/`

### Flujo de Encuentro de Batalla

1. El héroe camina en una `zona_batalla` del mapa
2. Se consulta el tipo de zona (ej: "pradera")
3. Se lee `database/monstruos/pradera.json`
4. Se eligen 1-4 monstruos aleatorios de la lista
5. Para cada monstruo elegido:
   - Se busca en `monstruos_db.json`
   - Se crea instancia con sus stats
   - Se carga sprite desde `assets/sprites/monstruos/`

---

## Guías de Uso

### Añadir un Nuevo Héroe

1. Editar `database/heroes_db.json`:
```json
"HEROE_NUEVO": {
    "nombre_clase": "Nuevo Héroe",
    "hp_max": 120,
    "mp_max": 60,
    // ... resto de campos
}
```

2. Añadir sprite en `assets/sprites/heroes/nuevo_heroe.png`

3. Definir coordenadas en `src/utils/asset_coords_db.py`:
```python
COORDS_NUEVO = {
    "HOJA_SPRITES": "nuevo_heroe.png",
    "ESCALA": 2.0,
    // ... coordenadas de frames
}
```

4. (Opcional) Añadir a `grupo_inicial.json` si es héroe inicial

---

### Añadir un Nuevo Item Consumible

Editar `database/items_db.json`:
```json
"POCION_GRANDE": {
    "id_item": "POCION_GRANDE",
    "nombre": "Poción Grande",
    "descripcion": "Restaura 150 HP a un aliado",
    "tipo": "Consumible",
    "efecto": "RESTAURA_HP",
    "poder": 150,
    "target": "Aliado"
}
```

El sistema automáticamente lo reconocerá.

---

### Añadir un Nuevo Equipo

Editar `database/equipo_db.json`:
```json
"ESPADA_LEGENDARIA": {
    "id_equipo": "ESPADA_LEGENDARIA",
    "nombre": "Espada Legendaria",
    "tipo": "Arma (1 Mano)",
    "ranuras_que_ocupa": ["mano_principal"],
    "stats": {
        "fuerza": 50,
        "defensa": 0,
        "inteligencia": 0,
        "espiritu": 0,
        "velocidad": 5,
        "suerte": 10,
        "hp_max": 0,
        "mp_max": 0
    },
    "descripcion": "Una espada de poder legendario"
}
```

---

### Añadir un Nuevo Mapa

1. Crear imagen en `assets/maps/mundo/nuevo_mapa.jpg`

2. Crear JSON en `database/mapas/mundo/nuevo_mapa.json`:
```json
{
    "muros": [
        {"x": 0, "y": 0, "w": 800, "h": 50}
    ],
    "portales": [
        {
            "caja": {"x": 400, "y": 550, "w": 50, "h": 10},
            "mapa_destino": "mapa_pradera.jpg",
            "categoria_destino": "mundo",
            "pos_destino": [400, 100]
        }
    ],
    "zonas_batalla": [
        {
            "x": 50,
            "y": 50,
            "w": 700,
            "h": 500,
            "tipo": "bosque"
        }
    ]
}
```

3. Añadir nombre legible en `src/data/game_data.py`:
```python
MAPA_NOMBRES_LEGIBLES = {
    "nuevo_mapa.jpg": "Bosque Misterioso",
    // ...
}
```

---

### Añadir un Nuevo Monstruo

1. Editar `database/monstruos_db.json`:
```json
"dragon_rojo": {
    "nombre": "Dragón Rojo",
    "hp": 200,
    "fuerza": 25,
    "defensa": 15,
    "velocidad": 8,
    "suerte": 10,
    "sprite_archivo": "dragon_rojo.png",
    "escala_sprite": 2.0,
    "xp_otorgada": 500,
    "oro_otorgado": 200
}
```

2. Añadir sprite en `assets/sprites/monstruos/dragon_rojo.png`

3. Añadir a zona correspondiente en `database/monstruos/[zona].json`:
```json
{
    "zona": "montaña",
    "encuentros": [
        "dragon_rojo",
        // ... otros monstruos
    ]
}
```

---

### Crear una Nueva Zona de Encuentros

Crear `database/monstruos/desierto.json`:
```json
{
    "zona": "desierto",
    "encuentros": [
        "escorpion",
        "serpiente_arena",
        "elemental_fuego"
    ]
}
```

Luego usar `"tipo": "desierto"` en las zonas_batalla de los mapas.

---

## Validación de Datos

Todos los archivos JSON son validados al cargar el juego. Si hay errores:

1. Se registra en los logs (`logs/game_YYYY-MM-DD.log`)
2. Se muestra mensaje de error
3. Se intenta usar valores por defecto si es posible

### Campos Requeridos por Archivo

**heroes_db.json:**
- `nombre_clase`, `hp_max`, `mp_max`, `fuerza`, `defensa`, `inteligencia`, 
  `espiritu`, `velocidad_base`, `suerte_base`, `nivel`, `magias_iniciales`, 
  `items_iniciales`, `clase`, `ranuras_habilidad_max`, `habilidades_activas`, 
  `inventario_habilidades`

**equipo_db.json:**
- `id_equipo`, `nombre`, `tipo`, `ranuras_que_ocupa`, `stats`, `descripcion`

**items_db.json:**
- `id_item`, `nombre`, `descripcion`, `tipo`, `efecto`, `poder`, `target`

**habilidades_db.json:**
- `id_habilidad`, `nombre`, `tipo`, `descripcion`, `costo_mp`, `poder`, 
  `alcance`, `efecto`

**magia_db.json:**
- `id_magia`, `nombre`, `descripcion`, `costo_mp`, `tipo`, `poder`, `target`

**monstruos_db.json:**
- `nombre`, `hp`, `fuerza`, `defensa`, `velocidad`, `suerte`, 
  `sprite_archivo`, `escala_sprite`, `xp_otorgada`, `oro_otorgado`

---

## Consejos y Buenas Prácticas

### IDs Consistentes
- Usar MAYUSCULAS_CON_GUION para IDs (ej: `HEROE_1`, `POCION_BASICA`)
- Ser descriptivos: `ESPADA_HIERRO` mejor que `ESP01`

### Balanceo
- HP típico nivel 1: 80-120
- MP típico nivel 1: 20-50
- Stats típicos nivel 1: 5-15
- XP para nivel 2: 100-200

### Organización
- Agrupar items similares en el JSON
- Comentar secciones complejas (aunque JSON no admite comentarios oficialmente)
- Mantener formato consistente (usar 4 espacios de indentación)

### Testing
- Probar cada nuevo item/monstruo/mapa en el juego
- Verificar que los IDs coincidan exactamente (case-sensitive)
- Asegurarse de que los sprites existen antes de añadir referencias

---

## Schemas de Validación

Los schemas de validación están en `database/schemas/`. Definen la estructura exacta esperada de cada archivo JSON.

Para añadir validación a un nuevo tipo de dato, crear un schema correspondiente y actualizarlo en `src/data/validators.py`.

---

**Última actualización:** 2025-11-15  
**Versión del documento:** 1.0
