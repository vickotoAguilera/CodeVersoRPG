# Editor de Cofres - Guía Completa

## 📋 Descripción General

Editor visual para colocar y configurar cofres en los mapas del RPG. Permite gestionar el contenido (items, equipo, oro), asignar sprites para diferentes estados, y configurar sistema de llaves y reapertura.

---

## 🚀 Ejecutar el Editor

### Método 1: Batch (Recomendado)

```cmd
ejecutar_cofres.bat
```

### Método 2: Python directo

```powershell
python editor_cofres.py
```

---

## 🎮 Controles Básicos

### Navegación

| Acción           | Control                                    |
| ---------------- | ------------------------------------------ |
| Cargar mapa      | Click en nombre del mapa (panel izquierdo) |
| Zoom In          | Rueda del ratón arriba                     |
| Zoom Out         | Rueda del ratón abajo                      |
| Mover mapa (Pan) | Click derecho + arrastrar                  |

### Cofres

| Acción            | Control                       |
| ----------------- | ----------------------------- |
| Crear cofre       | Click izquierdo en mapa       |
| Seleccionar cofre | Click izquierdo sobre cofre   |
| Mover cofre       | Arrastrar desde centro        |
| Redimensionar     | Arrastrar desde borde/esquina |
| Editar contenido  | Click derecho sobre cofre     |
| Eliminar cofre    | Seleccionar + tecla `DEL`     |

### Archivo

| Acción  | Control     |
| ------- | ----------- |
| Guardar | Tecla `G`   |
| Ayuda   | Tecla `H`   |
| Salir   | Tecla `ESC` |

---

## 📦 Tipos de Cofres

### 1. Madera

- **Color**: Marrón
- **Llave**: No requiere
- **Oro**: 10-50
- **Items**: 2-5 consumibles básicos
- **Equipo**: Pool básico (50% probabilidad)
- **Reapertura**: Sí (1 hora in-game)

### 2. Bronce

- **Color**: Naranja claro
- **Llave**: LLAVE_BRONCE
- **Oro**: 100-250
- **Items**: 3-5 consumibles básicos/intermedios
- **Equipo**: Pool básico/intermedio
- **Reapertura**: Sí (1 hora in-game)

### 3. Plata

- **Color**: Gris plateado
- **Llave**: LLAVE_PLATA
- **Oro**: 300-600
- **Items**: 4-5 consumibles intermedios/avanzados
- **Equipo**: Pool intermedio
- **Reapertura**: Sí (1 hora in-game)

### 4. Oro

- **Color**: Amarillo dorado
- **Llave**: LLAVE_ORO
- **Oro**: 800-1500
- **Items**: 5 consumibles avanzados
- **Equipo**: Pool avanzado
- **Reapertura**: Sí (1 hora in-game)

### 5. Especial

- **Color**: Morado
- **Llave**: No requiere
- **Oro**: 0
- **Items**: 1-3 items especiales únicos
- **Equipo**: No
- **Reapertura**: No (única vez)

---

## 🔧 Modal de Edición

Al hacer **click derecho** sobre un cofre, se abre el modal con:

### Sección 1: Tipo de Cofre

- Botones para cambiar entre: Madera, Bronce, Plata, Oro, Especial
- Al cambiar tipo, se aplica configuración automática (llave, oro, reapertura)

### Sección 2: Oro

- Muestra cantidad actual de oro
- Botón **"Random Oro"**: Genera cantidad aleatoria según tipo

### Sección 3: Contenido

- **Items Consumibles**: Pociones, éteres, antídotos
- **Equipo**: Armas, armaduras, accesorios
- **Items Especiales**: Llaves, expansores, quest items

### Sección 4: Botones

- **Generar Loot Random**: Llena el cofre automáticamente según tipo
- **Cerrar**: Cierra el modal

---

## 🎲 Sistema de Loot Random

El botón **"Generar Loot Random"** crea contenido automáticamente:

### Madera

```
Oro: 10-50
Consumibles: 2-5 de [POCION_BASICA, ETER_BASICO, ANTIDOTO]
Equipo: 50% probabilidad de 1 item básico
```

### Bronce

```
Oro: 100-250
Consumibles: 3-5 de [POCION_BASICA, POCION_INTERMEDIA, ETER_BASICO, ETER_INTERMEDIO, ANTIDOTO]
Equipo: Random del pool básico/intermedio
```

### Plata

```
Oro: 300-600
Consumibles: 4-5 de [POCION_INTERMEDIA, POCION_GRANDE, ETER_INTERMEDIO, ETER_GRANDE, ELIXIR]
Equipo: Random del pool intermedio
```

### Oro

```
Oro: 800-1500
Consumibles: 5 de [POCION_GRANDE, ETER_GRANDE, ELIXIR]
Equipo: Random del pool avanzado
```

### Especial

```
Oro: 0
Especiales: 1-3 de [EXPANSOR_RANURAS, MAPA_TESORO, SELLO_REAL, FRAGMENTO_CRISTAL,
                     LLAVE_MAESTRA, PIEDRA_LUNA, PLUMA_FENIX, CRISTAL_RESURRECION,
                     ORBE_EXPERIENCIA, AMULETO_PROTECCION, PERGAMINO_TELETRANSPORTE]
```

---

## 🗝️ Sistema de Llaves

### Tipos de Llaves

| Llave           | Abre Cofre       | Ubicación en DB          |
| --------------- | ---------------- | ------------------------ |
| `LLAVE_BRONCE`  | Cofres de Bronce | items_especiales_db.json |
| `LLAVE_PLATA`   | Cofres de Plata  | items_especiales_db.json |
| `LLAVE_ORO`     | Cofres de Oro    | items_especiales_db.json |
| `LLAVE_MAESTRA` | Todos (especial) | items_especiales_db.json |

### Lógica en el Juego

El jugador necesita tener la llave en `heroe.inventario_especiales`:

```python
# Verificar si tiene llave
if cofre.requiere_llave:
    if not heroe.tiene_item_especial(cofre.requiere_llave):
        mostrar_mensaje("Necesitas una llave")
        return

# Consumir llave (opcional, según diseño)
heroe.inventario_especiales[cofre.requiere_llave] -= 1
```

---

## ⏰ Sistema de Reapertura

### Cofres Reabribles (Madera, Bronce, Plata, Oro)

```json
{
  "puede_reabrir": true,
  "tiempo_reapertura": 60
}
```

- Después de abrir, se guarda `ultima_apertura` con `tiempo_juego_segundos`
- Tras 60 minutos (3600 segundos) in-game, el cofre se puede reabrir
- Al reabrir, se regenera el loot automáticamente

### Cofres Únicos (Especial)

```json
{
  "puede_reabrir": false,
  "tiempo_reapertura": 0
}
```

- Solo se pueden abrir una vez
- Contienen items especiales/quest

### Lógica en el Juego

```python
# Verificar si puede abrir
if not cofre.puede_reabrir and cofre.ya_abierto:
    mostrar_mensaje("Este cofre ya fue abierto")
    return

if cofre.puede_reabrir:
    tiempo_transcurrido = (tiempo_juego_segundos - cofre.ultima_apertura) / 60
    if tiempo_transcurrido < cofre.tiempo_reapertura:
        minutos_restantes = int(cofre.tiempo_reapertura - tiempo_transcurrido)
        mostrar_mensaje(f"Cofre reabrirá en {minutos_restantes} minutos")
        return
    else:
        # Regenerar loot
        generar_loot_random(cofre)

# Abrir cofre
dar_items_al_heroe(cofre.items_contenido)
dar_equipo_al_heroe(cofre.equipo_contenido)
dar_especiales_al_heroe(cofre.especiales_contenido)
heroe.oro += cofre.oro

cofre.ultima_apertura = tiempo_juego_segundos
cofre.ya_abierto = True
```

---

## 🎨 Sistema de Sprites (3 Estados)

Cada cofre debe tener 3 sprites:

### 1. Sprite Cerrado (`sprite_cerrado`)

- Estado inicial
- Mostrar cuando: `not cofre.ya_abierto` o cofre reabierto

### 2. Sprite Abierto con Items (`sprite_abierto_items`)

- Cofre abierto con items visibles
- Mostrar cuando: `cofre.ya_abierto and (items or oro > 0)`

### 3. Sprite Abierto Vacío (`sprite_abierto_vacio`)

- Cofre abierto sin contenido
- Mostrar cuando: `cofre.ya_abierto and not items and oro == 0`

### Ubicación de Sprites

```
assets/sprites/cofres y demas/cofres/
  ├─ madera/
  │   ├─ cofre_madera_cerrado.png
  │   ├─ cofre_madera_abierto.png
  │   └─ cofre_madera_vacio.png
  ├─ bronce/
  │   ├─ cofre_bronce_cerrado.png
  │   ├─ cofre_bronce_abierto.png
  │   └─ cofre_bronce_vacio.png
  ├─ plata/
  ├─ oro/
  └─ especial/
```

**Nota**: Actualmente solo `madera/` tiene sprites. Las carpetas vacías están listas para cuando agregues los demás.

---

## 💾 Formato JSON

Los cofres se guardan en `src/database/mapas/[categoria]/[mapa].json`:

```json
{
  "cofres": [
    {
      "id": "C1",
      "nombre": "Cofre_Madera_1",
      "tipo": "madera",
      "x": 450,
      "y": 320,
      "ancho": 64,
      "alto": 64,
      "sprite_cerrado": "cofres/madera/cofre_madera_cerrado.png",
      "sprite_abierto_items": "cofres/madera/cofre_madera_abierto.png",
      "sprite_abierto_vacio": "cofres/madera/cofre_madera_vacio.png",
      "oro": 35,
      "items_contenido": {
        "POCION_BASICA": 3,
        "ETER_BASICO": 1
      },
      "equipo_contenido": {
        "ESPADA_COBRE": 1
      },
      "especiales_contenido": {},
      "requiere_llave": null,
      "puede_reabrir": true,
      "tiempo_reapertura": 60
    },
    {
      "id": "C2",
      "nombre": "Cofre_Oro_2",
      "tipo": "oro",
      "x": 800,
      "y": 450,
      "ancho": 80,
      "alto": 80,
      "sprite_cerrado": "cofres/oro/cofre_oro_cerrado.png",
      "sprite_abierto_items": "cofres/oro/cofre_oro_abierto.png",
      "sprite_abierto_vacio": "cofres/oro/cofre_oro_vacio.png",
      "oro": 1200,
      "items_contenido": {
        "POCION_GRANDE": 5,
        "ELIXIR": 2
      },
      "equipo_contenido": {
        "COLLAR_SALUD": 1
      },
      "especiales_contenido": {},
      "requiere_llave": "LLAVE_ORO",
      "puede_reabrir": true,
      "tiempo_reapertura": 60
    },
    {
      "id": "C3",
      "nombre": "Cofre_Especial_3",
      "tipo": "especial",
      "x": 1200,
      "y": 600,
      "ancho": 96,
      "alto": 96,
      "sprite_cerrado": "cofres/especial/cofre_especial_cerrado.png",
      "sprite_abierto_items": "cofres/especial/cofre_especial_abierto.png",
      "sprite_abierto_vacio": "cofres/especial/cofre_especial_vacio.png",
      "oro": 0,
      "items_contenido": {},
      "equipo_contenido": {},
      "especiales_contenido": {
        "EXPANSOR_RANURAS": 2,
        "PIEDRA_LUNA": 1
      },
      "requiere_llave": null,
      "puede_reabrir": false,
      "tiempo_reapertura": 0
    }
  ]
}
```

---

## 🗄️ Bases de Datos Actualizadas

### `items_db.json`

Nuevos items añadidos:

- `POCION_INTERMEDIA` (100 HP)
- `POCION_GRANDE` (200 HP)
- `ETER_INTERMEDIO` (50 MP)
- `ETER_GRANDE` (100 MP)
- `ANTIDOTO` (cura veneno)
- `ELIXIR` (restaura todo)

### `items_especiales_db.json` (NUEVO)

Items especiales para cofres especiales:

- **Llaves**: `LLAVE_BRONCE`, `LLAVE_PLATA`, `LLAVE_ORO`, `LLAVE_MAESTRA`
- **Mejoras**: `EXPANSOR_RANURAS`, `ORBE_EXPERIENCIA`
- **Batalla**: `CRISTAL_RESURRECION`, `PLUMA_FENIX`
- **Quest**: `MAPA_TESORO`, `SELLO_REAL`, `FRAGMENTO_CRISTAL`, `PIEDRA_LUNA`
- **Utilidad**: `PERGAMINO_TELETRANSPORTE`, `AMULETO_PROTECCION`
- **Oro**: `BOLSA_ORO_PEQUENA`, `BOLSA_ORO_MEDIANA`, `BOLSA_ORO_GRANDE`, `COFRE_ORO`

### `cofres_db.json`

Estructura actualizada con:

- `tipos_cofre`: Configuraciones por tipo (oro, items, pools)
- `cofres_mapa`: Ejemplos de cofres configurados

---

## 🔄 Flujo de Trabajo Recomendado

### 1. Preparar Sprites

```
1. Crear sprites para cada tipo (cerrado, abierto, vacío)
2. Guardar en: assets/sprites/cofres y demas/cofres/[tipo]/
3. Nombrar claramente: cofre_[tipo]_[estado].png
```

### 2. Diseñar Mapa

```
1. Ejecutar: ejecutar_cofres.bat
2. Cargar mapa desde panel izquierdo
3. Colocar cofres con click izquierdo
4. Ajustar tamaño arrastrando bordes
5. Posicionar estratégicamente
```

### 3. Configurar Contenido

```
1. Click derecho en cofre → Modal
2. Seleccionar tipo (madera/bronce/plata/oro/especial)
3. Opción A: Click "Generar Loot Random"
4. Opción B: Manual (futura implementación drag&drop)
5. Cerrar modal
```

### 4. Guardar

```
1. Presionar G o ESC (auto-guarda al salir)
2. Verificar en: src/database/mapas/[categoria]/[mapa].json
```

### 5. Probar en Juego

```
1. python main.py
2. Navegar al mapa
3. Interactuar con cofre
4. Verificar loot, llaves, reapertura
```

---

## 🐛 Solución de Problemas

### El editor no inicia

- Verificar que Python 3.12 esté instalado
- Verificar que Pygame esté instalado: `pip install pygame`
- Ejecutar desde terminal para ver errores

### No veo mapas en el panel

- Verificar que exista `src/database/mapas/`
- Verificar que haya archivos `.json` en subcarpetas

### Los cofres no se guardan

- Verificar permisos de escritura
- Verificar que el JSON no esté corrupto
- Usar tecla G para guardar manualmente

### No puedo redimensionar cofres

- Acercar zoom (rueda arriba) para mayor precisión
- Arrastrar desde bordes o esquinas, no desde centro

### Modal no se abre

- Asegurarse de hacer click derecho SOBRE un cofre existente
- Verificar que el cofre esté dentro del viewport

---

## 📊 Estadísticas del Editor

- **Archivos creados**: 3

  - `editor_cofres.py` (950 líneas)
  - `ejecutar_cofres.bat`
  - `items_especiales_db.json`

- **Archivos actualizados**: 2

  - `items_db.json` (7 items nuevos)
  - `cofres_db.json` (estructura completa)

- **Funcionalidades**: 15+
  - Cargar/guardar mapas
  - Crear/editar/eliminar cofres
  - Redimensionar arrastrando
  - 5 tipos de cofres
  - Sistema de llaves
  - Sistema de reapertura
  - Generación random de loot
  - Zoom y pan
  - Modal de edición
  - Auto-guardado
  - Ayuda contextual

---

## 🚧 Pendiente (Futuras Mejoras)

### Versión 1.1

- [ ] Drag & drop de items desde listas al cofre
- [ ] Asignar sprites desde modal
- [ ] Preview visual de sprites
- [ ] Búsqueda de items por nombre
- [ ] Copiar/pegar configuración de cofre

### Versión 1.2

- [ ] Importar/exportar configuraciones
- [ ] Templates de cofres predefinidos
- [ ] Estadísticas por mapa (oro total, items)
- [ ] Validación de balance (mucho oro?)

### Versión 2.0

- [ ] Editor unificado (cofres + portales + spawns + muros)
- [ ] Vista 3D de cofres
- [ ] Animaciones de apertura

---

## 📖 Referencias

- **Código principal**: `main.py` (líneas 90, 318, 373, 439, 550)
- **Sistema de héroe**: `src/heroe.py` (líneas 29, 35, 540-551)
- **Database**: `src/database/`
  - `items_db.json`
  - `equipo_db.json`
  - `items_especiales_db.json`
  - `cofres_db.json`

---

## 🎓 Consejos de Diseño

### Distribución de Cofres

- **Madera**: 3-5 por mapa (áreas comunes)
- **Bronce**: 1-2 por mapa (áreas ocultas)
- **Plata**: 0-1 por mapa (secretos)
- **Oro**: 0-1 por zona grande (tesoros)
- **Especial**: 1 por quest importante

### Balance de Loot

- Evitar demasiado oro temprano
- Cofres especiales para quest items únicos
- Usar reapertura para farming controlado
- Llaves como recompensas de misiones

### Colocación Estratégica

- Cofres visibles en caminos principales
- Cofres ocultos tras muros/obstáculos
- Cofres especiales en ubicaciones narrativas
- Agrupar cofres para "salas de tesoro"

---

## 📝 Changelog

### v1.0.0 (19 Nov 2025)

- ✅ Editor completo funcional
- ✅ 5 tipos de cofres
- ✅ Sistema de llaves
- ✅ Sistema de reapertura
- ✅ Loot random
- ✅ Redimensionar arrastrando
- ✅ Modal de edición
- ✅ Auto-guardado
- ✅ Bases de datos actualizadas

---

**Desarrollado para CodeVerso RPG**  
Editor de Cofres v1.0.0  
2025
