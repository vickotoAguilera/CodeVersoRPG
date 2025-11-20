# DOCUMENTACIÓN EDITOR DE BATALLA - CodeVerso RPG

## 📋 ÍNDICE

1. [Descripción General](#descripción-general)
2. [Arquitectura del Editor](#arquitectura-del-editor)
3. [Clases Principales](#clases-principales)
4. [Funcionalidades](#funcionalidades)
5. [Controles y Atajos](#controles-y-atajos)
6. [Sistema de Guardado](#sistema-de-guardado)
7. [Flujo de Trabajo](#flujo-de-trabajo)

---

## 🎯 DESCRIPCIÓN GENERAL

**Archivo:** `editor_batalla.py`  
**Propósito:** Editor visual para configurar y diseñar escenas de batalla del juego

### Características Principales

- **Pantalla:** 1600x900 píxeles (Panel lateral: 300px, Área de batalla: 1300px)
- **FPS:** 60
- **Formato de guardado:** JSON (`batalla_config.json`)

---

## 🏗️ ARQUITECTURA DEL EDITOR

### Estructura de Ventanas

```
┌─────────────────────────────────────────────────────────┐
│  PANEL LATERAL (300px)     │  ÁREA DE BATALLA (1300px) │
│  - Secciones desplegables  │  - Fondo de batalla       │
│  - Botones de control      │  - Sprites colocados      │
│  - Configuración cantidad  │  - Ventana de comandos    │
│                            │  - Textos flotantes       │
│                            │  - Ventanas flotantes     │
└─────────────────────────────────────────────────────────┘
```

### Componentes del Área de Batalla

1. **Fondo:** `pelea_pradera.png` escalado a 1300x900
2. **Sprites:** Héroes y monstruos arrastrables y escalables
3. **Ventana de Comandos:** Panel inferior redimensionable con opciones de batalla
4. **Textos Flotantes:** Demostraciones de daño/curación/críticos
5. **Ventanas Flotantes:**
   - **Ventana de Magia:** Lista de habilidades mágicas
   - **Ventana Emulador:** Vista previa completa de la batalla

---

## 🎨 CLASES PRINCIPALES

### 1. `SpriteInfo` (Dataclass)

**Propósito:** Almacena información de sprites disponibles para arrastrar

```python
@dataclass
class SpriteInfo:
    nombre: str              # Nombre del sprite
    ruta: str                # Ruta del archivo PNG
    tipo: str                # "heroe" o "monstruo"
    ancho_default: int = 96  # Ancho por defecto
    alto_default: int = 96   # Alto por defecto
```

**Ubicación de sprites:**

- Héroes: `assets/sprites/heroes/`
- Monstruos: `assets/sprites/monstruos/`

---

### 2. `SpriteColocado` (Dataclass)

**Propósito:** Representa un sprite ya colocado en el área de batalla

```python
@dataclass
class SpriteColocado:
    sprite_ref: str      # Referencia al sprite original
    tipo: str            # "heroe" o "monstruo"
    x: float             # Posición X en batalla
    y: float             # Posición Y en batalla
    ancho: int           # Ancho actual (redimensionable)
    alto: int            # Alto actual (redimensionable)
    slot_numero: int     # Número de slot (1-4 héroes, 1-6 monstruos)
    imagen: Surface      # Imagen de pygame cargada
```

**Funcionalidades:**

- `actualizar_rect()`: Actualiza el rectángulo de colisión
- `contiene_punto(px, py)`: Verifica si un punto está dentro
- `get_handle_en_punto(px, py, tam)`: Detecta handles de redimensionamiento
- `to_dict()`: Serializa para guardado JSON

---

### 3. `TextoFlotanteDemo` (Dataclass)

**Propósito:** Textos flotantes de demostración para visualizar daño/curación

```python
@dataclass
class TextoFlotanteDemo:
    texto: str                      # Texto a mostrar
    x: float                        # Posición X
    y: float                        # Posición Y
    color: Tuple[int, int, int]     # Color RGB
    tamano: int = 24                # Tamaño de fuente
    tipo: str = "normal"            # normal/critico/curacion/miss
```

**Tipos de texto:**

- `normal`: Daño normal (blanco)
- `critico`: Daño crítico (rojo)
- `curacion`: Curación (verde)
- `miss`: Fallo (gris)

**Funcionalidades:**

- Arrastrables por el área de batalla
- Redimensionables arrastrando handles
- Escalado manual ajustando `tamano`

---

### 4. `VentanaBatalla`

**Propósito:** Ventana de comandos inferior durante la batalla

```python
class VentanaBatalla:
    comandos = ["Ataque", "Magia", "Habilidades", "Items", "Huir"]
    seleccionado = 0  # Comando actualmente seleccionado
```

**Características:**

- Posición inicial: `(50, 650)`, tamaño `(600, 120)`
- **Redimensionable:** Sí, con handles en 4 esquinas
- **Arrastrrable:** Sí, click y drag
- **Texto escalable:** Se ajusta automáticamente al tamaño de la ventana

**Método de escalado:**

```python
def get_tamano_texto_escalado(self):
    factor = min(self.ancho / 600, self.alto / 120)  # Proporcional al tamaño
    return max(12, int(32 * factor))  # Entre 12 y infinito
```

---

### 5. `VentanaMagia`

**Propósito:** Ventana flotante que muestra lista de magias/habilidades

```python
class VentanaMagia:
    magias = [
        {"nombre": "Fuego", "mp": 10},
        {"nombre": "Rayo", "mp": 15},
        {"nombre": "Curar", "mp": 8},
        {"nombre": "Hielo", "mp": 12},
        {"nombre": "Veneno", "mp": 6}
    ]
    seleccionado = 0  # Magia seleccionada
```

**Características:**

- Posición inicial: `(100, 100)`, tamaño `(400, 300)`
- **Redimensionable:** Sí, con handles en 4 esquinas
- **Arrastrrable:** Sí, click y drag
- **Texto escalable:** Título y lista se ajustan al tamaño
- **Visible:** Solo cuando se activa el botón "Ventana Magia"

**Método de escalado:**

```python
def get_tamano_texto_escalado(self):
    factor = min(self.ancho / 400, self.alto / 300)
    return max(10, int(20 * factor))
```

---

### 6. `VentanaEmuladorBatalla`

**Propósito:** Vista previa completa de la batalla con todas las secciones

```python
class VentanaEmuladorBatalla:
    # Muestra 3 secciones:
    # 1. Menú de acción (izquierda, 25%)
    # 2. Zona de héroes (arriba centro, 20%)
    # 3. Zona de monstruos (centro, 50%)
```

**Características:**

- Posición inicial: `(700, 100)`, tamaño `(500, 400)`
- **Redimensionable:** Sí, con handles en 4 esquinas
- **Arrastrrable:** Sí, click y drag
- **Texto escalable:** Todos los textos se ajustan
- **Vista en miniatura:** Muestra sprites colocados proporcionalmente
- **Visible:** Solo cuando se activa el botón "Ventana Emulador"

**Distribución de espacio:**

```
┌───────────────────────────────────┐
│ VISTA DE BATALLA                  │
├────────┬──────────────────────────┤
│ Menú   │ Héroes (zona verde)      │
│ (25%)  │ (20% altura)             │
│        ├──────────────────────────┤
│        │ Monstruos (zona roja)    │
│        │ (50% altura)             │
└────────┴──────────────────────────┘
```

**Método de escalado:**

```python
def get_tamano_texto_escalado(self, base=20):
    factor = min(self.ancho / 500, self.alto / 400)
    return max(10, int(base * factor))
```

---

### 7. `SeccionDesplegable`

**Propósito:** Secciones expandibles/colapsables en el panel lateral

```python
class SeccionDesplegable:
    items: List[SpriteInfo]  # Lista de sprites disponibles
    expandida: bool          # Estado expandido/colapsado
    scroll_y: int            # Offset de scroll (para muchos items)
```

**Características:**

- **Expandible:** Click en título para toggle
- **Scroll:** Soporte para listas largas (flechas arriba/abajo)
- **Contador:** Muestra cantidad de items `(N)`
- **Hover:** Resalta item bajo el cursor
- **Drag & Drop:** Arrastra items al área de batalla

---

## 🎮 FUNCIONALIDADES

### 1. Sistema de Sprites

#### Carga Automática de Sprites

```python
def cargar_sprites(self):
    # Escanea carpetas automáticamente:
    # - assets/sprites/heroes/
    # - assets/sprites/monstruos/

    # Detecta nuevos sprites sin reiniciar
    # Carga imágenes en cache para rendimiento
```

#### Drag & Drop

1. **Desde Panel Lateral:**

   - Click en sprite de la sección desplegable
   - Arrastra al área de batalla
   - Suelta para colocar (se asigna slot automáticamente)

2. **Dentro del Área de Batalla:**
   - Click en sprite colocado
   - Arrastra a nueva posición
   - Handles en 4 esquinas para redimensionar

#### Sistema de Slots

- **Héroes:** 1-4 slots (configurable con botones en panel)
- **Monstruos:** 1-6 slots (configurable con botones en panel)
- **Visualización:** Número de slot en círculo en esquina superior izquierda
- **Auto-asignación:** Al colocar sprite, se asigna al siguiente slot disponible

---

### 2. Sistema de Textos Flotantes

#### Activación

- **Botón:** "Textos Flotantes" en panel lateral
- **Atajo:** Tecla `T`

#### Tipos de Texto

1. **Normal:** Daño normal - Color blanco `(255, 255, 255)`
2. **Crítico:** Daño crítico - Color rojo `(255, 50, 50)`
3. **Curación:** Restauración HP - Color verde `(50, 255, 50)`
4. **Miss:** Ataque fallido - Color gris `(150, 150, 150)`

#### Creación de Textos

1. Activa "Textos Flotantes"
2. Arrastra botón de color desde panel lateral
3. Suelta en posición deseada
4. Ajusta tamaño arrastrando handles

#### Paleta de Colores

- **Activación:** Click en "[Editar Colores]" cuando textos están activos
- **Ubicación:** Aparece en área de batalla `(350, 50)`
- **Controles:**
  - 4 botones para seleccionar tipo de texto
  - 3 sliders RGB para ajustar color
  - Preview del color actual
- **Cierre:** Tecla `ESC`

---

### 3. Sistema de Ventanas Flotantes

#### Ventana de Magia

- **Activación:** Botón "Ventana Magia" en panel lateral
- **Contenido:**
  - Título "MAGIAS" escalable
  - Lista de 5 magias con costo MP
  - Selección visual (fondo azul)
- **Interacción:**
  - Arrastra por cualquier parte (excepto handles)
  - Redimensiona desde 4 esquinas
  - Texto se ajusta automáticamente

#### Ventana Emulador

- **Activación:** Botón "Ventana Emulador" en panel lateral
- **Contenido:**
  - Vista previa completa de batalla
  - Menú de acción (izquierda)
  - Héroes en miniatura (arriba)
  - Monstruos en miniatura (centro)
  - Números de slot en cada miniatura
- **Interacción:**
  - Arrastra por cualquier parte
  - Redimensiona desde 4 esquinas
  - Miniaturas se escalan proporcionalmente

---

### 4. Ventana de Comandos de Batalla

#### Contenido

```
[ Ataque ] [ Magia ] [ Habilidades ] [ Items ] [ Huir ]
```

#### Interacción

- **Selección visual:** El comando seleccionado aparece en amarillo
- **Cambio de selección:** Click en ventana cambia `seleccionado`
- **Redimensionamiento:** Arrastra handles en esquinas
- **Arrastre:** Click en centro y arrastra

---

## ⌨️ CONTROLES Y ATAJOS

### Teclado

| Tecla | Acción                                      |
| ----- | ------------------------------------------- |
| `ESC` | Salir del editor / Cerrar paleta de colores |
| `T`   | Toggle textos flotantes ON/OFF              |
| `G`   | Guardar configuración                       |
| `L`   | Cargar configuración                        |
| `D`   | Duplicar sprite seleccionado                |
| `DEL` | Eliminar sprite/texto seleccionado          |
| `R`   | Recargar sprites (detectar nuevos)          |
| `↑/↓` | Scroll en secciones desplegables            |

### Mouse

| Acción                                   | Resultado                    |
| ---------------------------------------- | ---------------------------- |
| Click izquierdo + drag (sprite panel)    | Arrastrar sprite al área     |
| Click izquierdo + drag (sprite colocado) | Mover sprite                 |
| Click izquierdo + drag (handle)          | Redimensionar sprite/ventana |
| Click derecho (sprite)                   | Eliminar sprite              |
| Click (ventana flotante)                 | Arrastrar/redimensionar      |
| Click (paleta colores - slider)          | Ajustar color RGB            |

---

## 💾 SISTEMA DE GUARDADO

### Archivo de Configuración

**Nombre:** `batalla_config.json`  
**Ubicación:** Raíz del proyecto

### Estructura JSON

```json
{
  "sprites": [
    {
      "sprite_ref": "cloud_battle_sprite.png",
      "tipo": "heroe",
      "x": 1000,
      "y": 300,
      "ancho": 96,
      "alto": 96,
      "slot_numero": 1
    },
    {
      "sprite_ref": "slime.png",
      "tipo": "monstruo",
      "x": 500,
      "y": 400,
      "ancho": 80,
      "alto": 80,
      "slot_numero": 1
    }
  ],
  "ventana_batalla": {
    "x": 50,
    "y": 650,
    "ancho": 600,
    "alto": 120
  },
  "textos_flotantes": [
    {
      "texto": "100",
      "x": 400,
      "y": 300,
      "color": [255, 255, 255],
      "tamano": 24,
      "tipo": "normal"
    }
  ],
  "colores": {
    "normal": [255, 255, 255],
    "critico": [255, 50, 50],
    "curacion": [50, 255, 50],
    "miss": [150, 150, 150]
  }
}
```

### Métodos de Guardado/Carga

#### Guardar

```python
def guardar_configuracion(self):
    config = {
        "sprites": [s.to_dict() for s in self.sprites_colocados],
        "ventana_batalla": self.ventana_batalla.to_dict(),
        "textos_flotantes": [t.to_dict() for t in self.textos_flotantes_demo],
        "colores": self.colores_config
    }
    with open("batalla_config.json", "w") as f:
        json.dump(config, f, indent=2)
```

**Atajo:** Tecla `G` o botón "Guardar" (derecha superior)

#### Cargar

```python
def cargar_configuracion(self):
    # Lee batalla_config.json
    # Reconstruye todos los sprites
    # Restaura ventanas y colores
    # Recarga imágenes desde cache
```

**Atajo:** Tecla `L` o botón "Cargar" (derecha superior)

---

## 🔄 FLUJO DE TRABAJO

### Configuración Inicial

1. **Ejecutar editor:** `python editor_batalla.py`
2. **Configurar cantidad:**
   - Héroes: 1-4 (botones superiores panel)
   - Monstruos: 1-6 (botones debajo de héroes)

### Colocación de Sprites

1. **Expandir sección:** Click en "Héroes" o "Monstruos"
2. **Scroll (si necesario):** Flechas ↑/↓ si hay muchos sprites
3. **Arrastrar sprite:** Click + drag desde lista al área
4. **Posicionar:** Suelta en posición deseada
5. **Ajustar tamaño:** Arrastra handles en esquinas
6. **Reposicionar:** Arrastra desde centro del sprite

### Configuración de Ventanas

1. **Ventana de Comandos:**
   - Siempre visible en área de batalla
   - Ajusta posición y tamaño según layout
2. **Ventana de Magia:**

   - Click en "Ventana Magia" para toggle ON/OFF
   - Ajusta posición y tamaño
   - Redimensiona para ajustar texto

3. **Ventana Emulador:**
   - Click en "Ventana Emulador" para toggle ON/OFF
   - Visualiza miniaturas de todos los elementos
   - Ajusta tamaño para mejor visualización

### Textos Flotantes

1. **Activar:** Click en "Textos Flotantes" o tecla `T`
2. **Crear texto:** Arrastra botón de color al área
3. **Posicionar:** Suelta en posición deseada
4. **Ajustar tamaño:** Arrastra handles del texto
5. **Cambiar colores:**
   - Click en "[Editar Colores]"
   - Ajusta sliders RGB
   - Cambia entre tipos (normal/crítico/curación/miss)
   - Cierra con `ESC`

### Guardar y Reutilizar

1. **Guardar:** Tecla `G` o botón "Guardar"
2. **Mensaje:** Aparece "✓ Configuración guardada" en barra inferior
3. **Cargar:** Tecla `L` o botón "Cargar" (restaura todo)
4. **Verificar:** Revisa que sprites, ventanas y textos estén correctos

---

## 🎨 PALETA DE COLORES

### Colores del Editor

| Elemento             | Color RGB       | Descripción                          |
| -------------------- | --------------- | ------------------------------------ |
| `COLOR_FONDO`        | (15, 15, 20)    | Fondo general oscuro                 |
| `COLOR_PANEL`        | (25, 25, 35)    | Panel lateral                        |
| `COLOR_BOTON`        | (50, 50, 70)    | Botones normales                     |
| `COLOR_BOTON_HOVER`  | (70, 70, 100)   | Botones con hover                    |
| `COLOR_BOTON_ACTIVO` | (90, 140, 255)  | Botones activos/expandidos           |
| `COLOR_SELECCION`    | (255, 215, 0)   | Borde de selección (dorado)          |
| `COLOR_HOVER`        | (100, 200, 255) | Sprite con hover (cyan)              |
| `COLOR_HANDLE`       | (255, 100, 100) | Handles de redimensionamiento (rosa) |

### Colores de Textos Flotantes (Editables)

| Tipo     | Color RGB Default | Uso             |
| -------- | ----------------- | --------------- |
| Normal   | (255, 255, 255)   | Daño normal     |
| Crítico  | (255, 50, 50)     | Daño crítico    |
| Curación | (50, 255, 50)     | Restauración HP |
| Miss     | (150, 150, 150)   | Ataque fallido  |

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Sprite No Aparece

- **Causa:** Imagen no encontrada en carpeta
- **Solución:** Verificar que archivo PNG existe en `assets/sprites/heroes/` o `assets/sprites/monstruos/`
- **Recargar:** Tecla `R` para detectar nuevos sprites

### No Puedo Redimensionar Ventana

- **Causa:** No estás clickeando en el handle (esquina)
- **Solución:** Click exactamente en círculo rojo de la esquina
- **Tamaño handle:** 10 píxeles de radio

### Paleta de Colores No Aparece

- **Causa:** Textos flotantes desactivados
- **Solución:** Activa primero "Textos Flotantes" (botón o tecla `T`)
- **Luego:** Click en "[Editar Colores]"

### Configuración No Se Guarda

- **Causa:** Permisos de escritura en carpeta
- **Solución:** Ejecutar con permisos adecuados
- **Verificar:** Aparece archivo `batalla_config.json` en raíz

---

## 📊 ESTADÍSTICAS DEL CÓDIGO

- **Líneas totales:** ~2100
- **Clases:** 7 principales
- **Métodos:** ~50
- **Configurables:** Colores, tamaños, posiciones
- **Extensible:** Fácil agregar nuevos sprites/ventanas

---

## 🚀 PRÓXIMAS MEJORAS

### Planificadas

- [ ] Múltiples fondos de batalla
- [ ] Preview de animaciones
- [ ] Zoom in/out del área
- [ ] Grid/snap para alineación
- [ ] Copiar/pegar sprites
- [ ] Deshacer/rehacer acciones
- [ ] Exportar a imagen PNG

### En Consideración

- [ ] Ventana de victoria/derrota
- [ ] Efectos de partículas
- [ ] Barras de HP/MP en sprites
- [ ] Sistema de capas (z-index)
- [ ] Múltiples configuraciones guardadas

---

## 📝 NOTAS ADICIONALES

### Rendimiento

- Las imágenes se cachean en `self.imagenes_cache`
- Scroll optimizado para listas largas
- Redibujado solo cuando hay cambios

### Compatibilidad

- **Pygame:** Versión 2.0+
- **Python:** 3.7+
- **Sistema operativo:** Windows/Linux/Mac

### Convenciones de Código

- **Español neutral:** Comentarios y variables
- **Snake_case:** Funciones y variables
- **PascalCase:** Clases
- **MAYUSCULAS:** Constantes

---

**Versión del documento:** 1.0  
**Fecha:** 2025-01-18  
**Autor:** Sistema de IA - CodeVerso RPG Team
