# Editor de Portales - Guía Completa

## 📋 Índice
1. [Introducción](#introducción)
2. [Ejecutar el Editor](#ejecutar-el-editor)
3. [Interfaz](#interfaz)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Controles](#controles)
6. [Lógica de Vinculación](#lógica-de-vinculación)
7. [Formato JSON](#formato-json)

---

## Introducción

El **Editor de Portales** es una herramienta visual para crear y gestionar portales de teletransporte entre mapas del RPG. Permite vincular portales entre dos mapas simultáneamente, definir spawns (puntos de aparición), y gestionar conexiones de forma visual e intuitiva.

### Características principales:
- ✅ Dos mapas lado a lado simultáneamente
- ✅ Arrastrar y soltar mapas desde el panel
- ✅ Portales rectangulares y poligonales
- ✅ Auto-numeración y nombrado de portales
- ✅ Vinculación guiada portal ↔ portal
- ✅ Vinculación guiada portal → spawn
- ✅ Listas expandibles de conexiones
- ✅ Zoom y pan independiente por viewport
- ✅ Guardado automático

---

## Ejecutar el Editor

### Opción 1: Usando el batch (recomendado)
```cmd
ejecutar_portales.bat
```

### Opción 2: Directamente con Python
```powershell
& "C:/Program Files/Python312/python.exe" editor_portales.py
```

### Requisitos:
- Python 3.12+
- Pygame instalado (`pip install pygame`)
- Mapas en `assets/maps/`

---

## Interfaz

### Disposición de pantalla

```
┌─────────────────────────────────────────────────────────────┐
│ Panel Izquierdo │   Viewport Izq   │   Viewport Der        │
│                  │                  │                        │
│ ▼ Ciudades (6)   │   [Mapa 1]       │   [Mapa 2]            │
│   mapa_pradera   │                  │                        │
│   mapa_pueblo    │   Portal #1      │   Portal #2           │
│                  │                  │                        │
│ ▼ Mundo (1)      │   Spawn S1       │   Spawn S2            │
│                  │                  │                        │
│ ▼ Portales       │                  │                        │
│   Vinculados     │                  │                        │
│   P#1 <-> bosque │                  │                        │
│                  │                  │                        │
│ ▼ Portal→Spawn   │                  │                        │
│   P#1 → S1       │                  │                        │
│   P#2 → S2       │                  │                        │
│                  │                  │                        │
│        [?]       │                  │                        │
└─────────────────────────────────────────────────────────────┘
```

### Elementos de la interfaz:

1. **Panel Izquierdo** (300px):
   - Secciones de mapas por categoría
   - Lista de portales vinculados
   - Lista de conexiones portal→spawn
   - Botón de ayuda [?]

2. **Viewport Izquierdo**:
   - Muestra mapa 1
   - Zoom y pan independiente
   - Portales y spawns del mapa 1

3. **Viewport Derecho**:
   - Muestra mapa 2
   - Zoom y pan independiente
   - Portales y spawns del mapa 2

4. **Overlay Superior Derecha**:
   - Modo actual (portal/spawn)
   - Instrucciones contextuales
   - Estados de vinculación

---

## Flujo de Trabajo

### 1. Cargar mapas

```
1. Expande categoría en panel izquierdo
2. Arrastra mapa hacia viewport izquierdo → se carga ahí
3. Arrastra otro mapa hacia viewport derecho → se carga ahí
```

**Resultado**: Dos mapas cargados lado a lado con sus portales/spawns existentes.

---

### 2. Crear portales

#### Portal rectangular:
```
1. Presiona P (modo portal)
2. Click izquierdo y arrastra en el mapa
3. Suelta para crear
4. Se auto-numera: #1, #2, #3...
```

#### Portal poligonal:
```
1. Presiona P (modo portal)
2. Presiona L (modo polígono)
3. Click en varios puntos para formar polígono
4. Click derecho para deshacer último punto
5. Presiona ENTER para crear
6. ESC para cancelar
```

**Etiquetas**: Los portales muestran su ID con fondo negro y borde naranja.

---

### 3. Vincular Portal ↔ Portal (entre mapas)

Este es el vínculo principal para teletransporte entre mapas diferentes.

```
PASO 1: Seleccionar primer portal
├─ Click izquierdo en portal del mapa izquierdo
├─ Portal se pone VERDE
└─ Mensaje: "✓ Portal 1 seleccionado"

PASO 2: Seleccionar segundo portal
├─ Click izquierdo en portal del mapa derecho
├─ Portales se vinculan automáticamente
└─ Auto-nombrado:
    ├─ Portal izq: "Pmapa_pueblo_interior_posada"
    └─ Portal der: "Pinterior_posada_mapa_pueblo"

Resultado en JSON:
├─ Portal izq: mapa_destino = "interior_posada"
└─ Portal der: mapa_destino = "mapa_pueblo"
```

**Lista "Portales Vinculados"**: Muestra `P#1 <-> interior_posada`

---

### 4. Vincular Portal → Spawn (mismo mapa)

Define DÓNDE aparece el héroe cuando viene del otro mapa.

```
PASO 1: Seleccionar portal
├─ Shift + Click izquierdo en un portal
├─ Portal se pone AMARILLO
└─ Mensaje: "✓ [Portal] seleccionado. Click DERECHO para spawn"

PASO 2: Crear/vincular spawn
├─ Click derecho en posición deseada (mismo mapa)
├─ Opción A: Click en vacío → crea spawn nuevo (S1, S2...)
├─ Opción B: Click en spawn existente → lo vincula
└─ Portal.spawn_destino_id = "S1"

Validación:
└─ Solo puedes crear spawn en el MISMO mapa del portal
```

**Lista "Portal → Spawn"**: Muestra `P#1 → S1`

---

### 5. Ejemplo completo: Pueblo ↔ Posada

```
Mapa izquierdo: mapa_pueblo
Mapa derecho: interior_posada

[1] Crear portal #1 en puerta del pueblo
[2] Crear portal #2 en puerta de la posada
[3] Click en portal #1 (verde) → Click en portal #2
    └─ Vinculados: P#1 ↔ P#2

[4] Shift+Click en portal #2 (posada, amarillo)
    └─ Click derecho dentro posada → Spawn S1
    └─ P#2.spawn_destino_id = "S1"

[5] Shift+Click en portal #1 (pueblo, amarillo)
    └─ Click derecho en pueblo → Spawn S2
    └─ P#1.spawn_destino_id = "S2"

Resultado:
├─ Portal #1 (pueblo): lleva a posada, héroe aparece en S1
└─ Portal #2 (posada): lleva a pueblo, héroe aparece en S2
```

---

## Controles

### Modos
| Tecla | Acción |
|-------|--------|
| `P` | Modo Portal (crear portales) |
| `S` | Modo Spawn (crear spawns) |
| `L` | Modo Polígono (portales poligonales) |

### Vinculación
| Acción | Función |
|--------|---------|
| `Click izq` en portal | Iniciar vinculación portal↔portal |
| `Shift + Click izq` en portal | Iniciar vinculación portal→spawn |
| `Click derecho` (con portal amarillo) | Crear/vincular spawn |
| `ESC` | Cancelar vinculación activa |

### Edición
| Acción | Función |
|--------|---------|
| `Doble-click` en portal | Editar nombre del portal |
| `ENTER` | Confirmar nombre |
| `ESC` | Cancelar edición |
| `DEL` | Eliminar seleccionados |
| `Shift + Click` | Multi-selección |

### Vista
| Control | Función |
|---------|---------|
| `Rueda ratón` | Zoom (0.25x - 1.0x) |
| `Click derecho + arrastrar` | Pan (mover vista) |
| `Click medio + arrastrar` | Pan (alternativo) |
| `0` | Reset zoom a 1:1 |

### Archivo
| Tecla | Acción |
|-------|--------|
| `G` | Guardar ambos mapas |
| `H` | Mostrar/ocultar ayuda |

### Panel
| Acción | Función |
|--------|---------|
| `Click en sección` | Expandir/colapsar |
| `Arrastrar mapa` | Cargar en viewport izq/der |

---

## Lógica de Vinculación

### Sistema de colores

```
┌────────────────────────────────────────────────┐
│ ROSA    = Portal normal                        │
│ VERDE   = Portal seleccionado (vinc. portal)   │
│ AMARILLO = Portal seleccionado (vinc. spawn)   │
│ AZUL    = Spawn                                │
└────────────────────────────────────────────────┘
```

### Estados de vinculación

```mermaid
Portal normal (ROSA)
    ├─ Click izq ──→ Portal vinc.1 (VERDE) ──→ Click otro portal ──→ Vinculados
    └─ Shift+Click ──→ Portal→spawn (AMARILLO) ──→ Click derecho ──→ Spawn vinculado
```

### Flujo de datos

#### Vinculación Portal ↔ Portal:
```python
Portal A (mapa_pueblo):
    id: "Pmapa_pueblo_interior_posada"
    mapa_destino: "interior_posada"
    spawn_destino_id: "S2"  # Dónde aparece al SALIR de posada

Portal B (interior_posada):
    id: "Pinterior_posada_mapa_pueblo"
    mapa_destino: "mapa_pueblo"
    spawn_destino_id: "S1"  # Dónde aparece al ENTRAR a posada
```

#### En el juego:
```
Héroe entra portal A (pueblo):
1. Sistema lee: mapa_destino = "interior_posada"
2. Carga mapa interior_posada
3. Busca portal que venga de "mapa_pueblo" → Portal B
4. Lee spawn_destino_id = "S1"
5. Héroe aparece en posición de Spawn S1
```

---

## Formato JSON

### Estructura por mapa

Archivo: `src/database/mapas/[categoria]/[nombre_mapa].json`

```json
{
  "portales": [
    {
      "id": "Pmapa_pueblo_interior_posada",
      "tipo": "portal_enlazado",
      "forma": "rect",
      "x": 450,
      "y": 320,
      "w": 64,
      "h": 48,
      "mapa_destino": "ciudades_y_pueblos/interior_posada.png",
      "spawn_destino_id": "S2"
    },
    {
      "id": "#3",
      "tipo": "portal_enlazado",
      "forma": "poly",
      "puntos": [[100, 200], [150, 180], [150, 220]],
      "mapa_destino": "",
      "spawn_destino_id": ""
    }
  ],
  "spawns": [
    {
      "id": "S1",
      "tipo": "spawn",
      "x": 400,
      "y": 300,
      "direccion": "abajo",
      "tam": 12
    },
    {
      "id": "S2",
      "tipo": "spawn",
      "x": 500,
      "y": 350,
      "direccion": "arriba",
      "tam": 12
    }
  ]
}
```

### Campos de Portal

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único (auto o manual) |
| `tipo` | string | Siempre "portal_enlazado" |
| `forma` | string | "rect" o "poly" |
| `x, y, w, h` | int | Dimensiones (solo rect) |
| `puntos` | array | Lista de [x,y] (solo poly) |
| `mapa_destino` | string | Ruta relativa del mapa destino |
| `spawn_destino_id` | string | ID del spawn donde aparece héroe |

### Campos de Spawn

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único |
| `tipo` | string | Siempre "spawn" |
| `x, y` | int | Posición en píxeles |
| `direccion` | string | "arriba", "abajo", "izquierda", "derecha" |
| `tam` | int | Tamaño del área (default: 12) |

---

## Lógica Interna

### Auto-numeración

```python
self.contador_portales = 0  # Contador global

# Al crear portal:
self.contador_portales += 1
portal.id = f"#{self.contador_portales}"  # #1, #2, #3...

# Al crear spawn:
self.contador_portales += 1
spawn.id = f"S{self.contador_portales}"  # S1, S2, S3...
```

### Auto-nombrado al vincular

```python
# Portal izquierdo → derecho:
mapa_origen = "mapa_pueblo"
mapa_dest = "interior_posada"
portal_izq.id = f"P{mapa_origen}_{mapa_dest}"  # "Pmapa_pueblo_interior_posada"
portal_der.id = f"P{mapa_dest}_{mapa_origen}"  # "Pinterior_posada_mapa_pueblo"

portal_izq.mapa_destino = mapa_dest
portal_der.mapa_destino = mapa_origen
```

### Bloqueo de teclas durante edición

```python
if self.editando_nombre:
    # Solo permitir: ENTER, ESC, BACKSPACE, caracteres imprimibles
    # Bloquear: P, S, L, G, H, etc.
    if ev.key == pygame.K_RETURN:
        self.portal_editando.id = self.texto_nombre
    elif ev.key == pygame.K_ESCAPE:
        # Cancelar
    # ... resto bloqueado
```

### Detección de lado (izq/der)

```python
def _detectar_lado(self, mx):
    if mx < PANEL_ANCHO: return None
    izq_rect = pygame.Rect(PANEL_ANCHO, 0, (ANCHO-PANEL_ANCHO)//2, ALTO)
    der_rect = pygame.Rect(PANEL_ANCHO + izq_rect.width, 0, ...)
    
    if izq_rect.collidepoint(mx, ALTO//2): return 'izq'
    if der_rect.collidepoint(mx, ALTO//2): return 'der'
```

### Transformación de coordenadas

```python
def _map_to_screen(self, x, y, lado, offset_x, offset_y, zoom):
    base_x = izq_rect.x if lado == 'izq' else der_rect.x
    return int(x*zoom + offset_x + base_x), int(y*zoom + offset_y)

def _screen_to_map(self, sx, sy, lado, offset_x, offset_y, zoom):
    base_x = izq_rect.x if lado == 'izq' else der_rect.x
    return int((sx - base_x - offset_x)/zoom), int((sy - offset_y)/zoom)
```

### Actualización de listas

```python
def _actualizar_lista_vinculos(self):
    # Buscar portales con mapa_destino
    for p in self.izq_portales + self.der_portales:
        if p.mapa_destino and p.id:
            vinculos.append(f"{p.id} <-> {p.mapa_destino}")

def _actualizar_lista_portal_spawns(self):
    # Buscar portales con spawn_destino_id
    for p in self.izq_portales + self.der_portales:
        if p.spawn_destino_id:
            conexiones.append(f"{p.id} → {p.spawn_destino_id}")
```

---

## Consejos y Buenas Prácticas

### ✅ Recomendaciones

1. **Carga ambos mapas primero**: El sistema valida que haya 2 mapas antes de vincular
2. **Vincula portal↔portal antes de spawns**: Primero conecta los mapas, luego define dónde aparece
3. **Usa nombres descriptivos**: Doble-click para nombrar portales con sentido (ej: "entrada_cueva")
4. **Verifica las listas**: Las secciones expandibles muestran todas las conexiones
5. **Guarda frecuentemente**: Auto-guarda cada 2 segundos, pero usa G para forzar
6. **Un spawn por portal**: Cada portal debe tener su propio punto de aparición

### ⚠️ Errores comunes

❌ **Spawn en mapa equivocado**:
```
Portal en pueblo → Spawn debe estar en pueblo
Portal en posada → Spawn debe estar en posada
```

❌ **Olvidar vincular spawns**:
- Un portal sin spawn_destino_id causará aparición en posición por defecto

❌ **Vincular portales del mismo lado**:
- Sistema avisa: "⚠ Debes seleccionar portal del otro mapa"

---

## Comandos Rápidos (Cheatsheet)

```
CARGAR:    Arrastra mapa → izq/der
PORTAL:    P → Click+arrastra
POLÍGONO:  P → L → Clicks → ENTER
SPAWN:     S → Click

VINCULAR PORTAL↔PORTAL:
  1. Click portal izq (verde)
  2. Click portal der (vinculados)

VINCULAR PORTAL→SPAWN:
  1. Shift+Click portal (amarillo)
  2. Click derecho posición (spawn)

EDITAR:    Doble-click → escribe → ENTER
ZOOM:      Rueda ratón
PAN:       Click derecho + arrastrar
GUARDAR:   G
AYUDA:     H
```

---

## Solución de Problemas

### El portal no se vincula
- Verifica que ambos mapas estén cargados
- Asegúrate de hacer click en portales de lados DIFERENTES
- El sistema muestra mensajes de error en la parte superior

### No puedo crear spawn
- Verifica que el portal esté en modo amarillo (Shift+Click)
- El spawn debe crearse en el MISMO lado que el portal
- Click derecho para crear, no izquierdo

### Las etiquetas no se ven
- Los portales sin nombre (id vacío) no muestran etiqueta
- Doble-click para asignar nombre
- Los portales vinculados reciben nombre automático

### Los mapas no cargan
- Verifica que existan en `assets/maps/`
- Formatos soportados: PNG, JPG
- La estructura debe ser: `assets/maps/categoria/mapa.png`

---

## Archivos Relacionados

```
editor_portales.py              # Editor principal
ejecutar_portales.bat           # Launcher Windows
src/database/mapas/             # JSONs de portales/spawns
  ├─ ciudades_y_pueblos/
  │    ├─ mapa_pueblo.json
  │    └─ interior_posada.json
  └─ mundo/
       └─ mapa_pradera.json
assets/maps/                    # Imágenes de mapas
  ├─ ciudades_y_pueblos/
  └─ mundo/
```

---

## Versión y Changelog

**Versión actual**: 2.0 (Dual Map System)

### Características implementadas:
- ✅ Dual viewport side-by-side
- ✅ Drag & drop de mapas
- ✅ Portales rectangulares y poligonales
- ✅ Auto-numeración (#1, #2, S1, S2)
- ✅ Auto-nombrado al vincular
- ✅ Vinculación guiada portal↔portal
- ✅ Vinculación guiada portal→spawn
- ✅ Listas expandibles de conexiones
- ✅ Bloqueo de teclas durante edición
- ✅ Etiquetas con fondo negro
- ✅ Colores visuales por estado
- ✅ Zoom/pan independiente
- ✅ Auto-guardado cada 2s

---

## Créditos

**Proyecto**: CodeVerso RPG  
**Editor**: Sistema de Portales Dual Map  
**Desarrollado**: 2025  
**Framework**: Pygame + Python 3.12
