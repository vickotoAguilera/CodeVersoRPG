# Pantalla de Habilidades - Documentación Técnica

## 📋 Información General

**Archivo:** `src/pantalla_habilidades.py`  
**Líneas de código:** ~780  
**Creado:** 2025-11-15 (Paso 7.17)  
**Propósito:** Gestionar habilidades equipables del héroe

---

## 🎯 Funcionalidad

Permite al jugador:
- ✅ Ver todas las habilidades aprendidas (filtradas por clase)
- ✅ Equipar habilidades en 4 ranuras activas
- ✅ Desequipar habilidades
- ✅ Ver descripción detallada de cada habilidad
- ✅ Navegar con scroll en listas largas

---

## 🎨 Diseño Visual (4 Paneles)

```
┌────────────────────────────────────────────────────────────────────┐
│          HABILIDADES: Cloud                                        │
├─────────┬─────────────────────┬──────────────────────────────────┤
│         │                     │                                  │
│ SPRITE  │   INVENTARIO        │   DESCRIPCIÓN                    │
│         │   ═══════════       │   ═══════════                    │
│ [Cloud] │                     │   Nombre: Corte Cruzado          │
│         │ > Corte Cruzado     │   Tipo: Habilidad Física         │
│ Cloud   │   Golpe Fuerte      │   Costo MP: 5                    │
│ Clase:  │   Embestida         │   Poder: 25                      │
│Guerrero │   [Más abajo ▼]     │   Alcance: Un Enemigo            │
│         │                     │                                  │
│Ranuras:4│                     │   Descripción:                   │
│         │                     │   Un ataque físico cruzado...    │
│         │                     │                                  │
├─────────┴─────────────────────┴──────────────────────────────────┤
│ RANURAS ACTIVAS (4 slots)                                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│ │   [1]    │ │   [2]    │ │   [3]    │ │   [4]    │            │
│ │ Corte X  │ │  [Vacío] │ │  [Vacío] │ │  [Vacío] │            │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎮 Controles

### Modo: Selección de Inventario
| Tecla | Acción |
|-------|--------|
| ↑ / ↓ | Navegar por la lista de habilidades |
| → | Cambiar a panel de ranuras |
| ENTER | Seleccionar habilidad para equipar |
| D | Ver detalles completos (pop-up) |
| ESC | Cerrar pantalla |

### Modo: Selección de Ranura
| Tecla | Acción |
|-------|--------|
| ↑ / ↓ | Navegar por las ranuras |
| ← | Volver a inventario |
| ENTER | Equipar habilidad seleccionada |
| X | Desequipar habilidad de la ranura |
| ESC | Volver a inventario |

### Modo: Ver Detalles
| Tecla | Acción |
|-------|--------|
| D o ESC | Cerrar pop-up |

---

## 🔧 Estructura del Código

### Clase Principal: `PantallaHabilidades`

#### Constructor (`__init__`)
**Parámetros:**
- `ancho`: Ancho de la pantalla
- `alto`: Alto de la pantalla
- `heroe_obj`: Objeto héroe (clase Heroe)
- `habilidades_db_completa`: Diccionario con todas las habilidades
- `cursor_img`: Imagen del cursor

**Variables importantes:**
```python
self.modo = "seleccion_inventario"  # Estado actual
self.lista_inventario_habilidades = []  # Habilidades filtradas
self.lista_ranuras_activas = []  # 4 ranuras
self.scroll_inventario = 0  # Offset de scroll
```

---

### Métodos Principales

#### 1. `_actualizar_listas()`
**Propósito:** Filtrar y cargar habilidades según la clase del héroe

**Lógica:**
```python
# 1. Obtener clase del héroe
clase_heroe = self.heroe.clase  # "Guerrero", "Mago", etc.

# 2. Filtrar inventario
for id_hab in self.heroe.inventario_habilidades:
    hab_data = self.habilidades_db.get(id_hab)
    clase_req = hab_data.get("clase_requerida", None)
    
    # Si clase_requerida es None o coincide, agregar
    if clase_req is None or clase_req == clase_heroe:
        self.lista_inventario_habilidades.append(hab_data)

# 3. Cargar ranuras activas (4)
for i in range(4):
    id_hab = self.heroe.habilidades_activas[i]
    # Agregar a lista con info completa
```

**Cuándo se llama:**
- Al iniciar la pantalla
- Después de equipar/desequipar

---

#### 2. `update(teclas)`
**Propósito:** Actualizar lógica del juego (animaciones, navegación)

**Funciones:**
- Animar sprite del héroe
- Navegar con flechas
- Manejar scroll automático
- Cambiar entre modos

**Cooldown:** 200ms entre inputs

---

#### 3. `update_input(tecla)`
**Propósito:** Manejar input del usuario (Enter, ESC, D, X)

**Retorna:**
- `"volver_al_menu"` → Cerrar pantalla y volver al menú de pausa
- `None` → Continuar en la pantalla

**Flujo de Equipar:**
```
1. Modo inventario → Seleccionar habilidad → Enter
2. Cambia a modo ranura → Seleccionar ranura → Enter
3. Llama a _equipar_habilidad()
4. Vuelve a modo inventario
```

---

#### 4. `_equipar_habilidad(id_habilidad, ranura_idx)`
**Propósito:** Equipar una habilidad en una ranura específica

**Validaciones:**
```python
# 1. Verificar que ranura_idx sea válido (0-3)
if ranura_idx < 0 or ranura_idx >= self.heroe.ranuras_habilidad_max:
    return  # Error

# 2. Verificar que habilidad esté en inventario
if id_habilidad not in self.heroe.inventario_habilidades:
    return  # Error

# 3. Equipar (puede sobrescribir)
self.heroe.habilidades_activas[ranura_idx] = id_habilidad

# 4. Actualizar listas
self._actualizar_listas()
```

**Permite:** Sobrescribir una habilidad equipada

---

#### 5. `_desequipar_habilidad(ranura_idx)`
**Propósito:** Desequipar una habilidad (poner ranura a None)

**Lógica:**
```python
# 1. Validar ranura
if ranura_idx < 0 or ranura_idx >= len(self.heroe.habilidades_activas):
    return

# 2. Desequipar
self.heroe.habilidades_activas[ranura_idx] = None

# 3. Actualizar listas
self._actualizar_listas()
```

**Nota:** La habilidad permanece en `inventario_habilidades`

---

#### 6. `draw(pantalla)`
**Propósito:** Renderizar toda la interfaz

**Orden de dibujo:**
```
1. Velo de fondo semi-transparente
2. Título de la pantalla
3. Panel 1: Sprite del héroe
4. Panel 2: Inventario de habilidades
5. Panel 3: Descripción
6. Panel 4: Ranuras activas
7. Instrucciones de control
8. Pop-up de detalles (si está en modo ver_detalles)
```

---

### Métodos de Dibujo (Privados)

#### `_draw_panel_sprite(pantalla)`
**Dibuja:** Sprite animado, nombre, clase, cantidad de ranuras

#### `_draw_panel_inventario(pantalla)`
**Dibuja:** Lista scrollable con:
- Nombre de habilidades
- Color según tipo (física/mágica)
- Marcador "•" si está equipada
- Cursor en selección actual
- Indicadores de scroll (▲ ▼)

**Scroll:**
```python
inicio = self.scroll_inventario
fin = inicio + self.max_items_visibles_inventario  # 8 items
# Solo dibuja items visibles
```

#### `_draw_panel_descripcion(pantalla)`
**Dibuja:** Detalles de la habilidad seleccionada:
- Nombre (grande, amarillo)
- Tipo
- Costo MP
- Poder
- Alcance
- Descripción (wrapped, múltiples líneas)

#### `_draw_panel_ranuras(pantalla)`
**Dibuja:** 4 ranuras horizontales con:
- Número [1] [2] [3] [4]
- Nombre de habilidad equipada
- Color verde si equipada, gris si vacía
- Borde amarillo en selección

#### `_draw_instrucciones(pantalla)`
**Dibuja:** Barra de instrucciones según modo actual

#### `_draw_popup_detalles(pantalla)`
**Dibuja:** Pop-up grande centrado con todos los detalles

---

## 🎨 Sistema de Colores

| Color | Uso | RGB |
|-------|-----|-----|
| `COLOR_CAJA` | Fondo de cajas | (0, 0, 139) Azul oscuro |
| `COLOR_BORDE` | Borde normal | (255, 255, 255) Blanco |
| `COLOR_TEXTO` | Texto normal | (255, 255, 255) Blanco |
| `COLOR_TEXTO_SEL` | Selección | (255, 255, 0) Amarillo |
| `COLOR_TEXTO_EQUIPADO` | Equipado | (0, 255, 0) Verde |
| `COLOR_TEXTO_DESHABILITADO` | Vacío | (100, 100, 100) Gris |
| `COLOR_FISICA` | Habilidad física | (255, 100, 100) Rojo claro |
| `COLOR_MAGICA` | Habilidad mágica | (100, 150, 255) Azul claro |

---

## 📐 Geometría de Paneles

```python
# Panel 1: Sprite (Izquierda)
caja_sprite_rect = Rect(20, 20, 150, 200)

# Panel 2: Inventario (Centro-Izquierda)
caja_inventario_rect = Rect(190, 20, 250, 370)

# Panel 3: Descripción (Derecha)
caja_descripcion_rect = Rect(460, 20, 320, 370)

# Panel 4: Ranuras (Inferior, ancho completo)
caja_ranuras_rect = Rect(20, 410, 760, 160)
```

**Tamaño de pantalla:** 800x600

---

## 🔄 Flujo de Estados

```
┌─────────────────────────┐
│  seleccion_inventario   │ ← Modo inicial
│  (Panel Inventario)     │
└────────┬────────────────┘
         │
         │ ENTER (seleccionar habilidad)
         ▼
┌─────────────────────────┐
│   seleccion_ranura      │
│   (Panel Ranuras)       │
└────────┬────────────────┘
         │
         │ ENTER (equipar)
         ▼
    _equipar_habilidad()
         │
         ▼
┌─────────────────────────┐
│  Vuelve a inventario    │
│  (listas actualizadas)  │
└─────────────────────────┘

         Desde inventario:
         D → ver_detalles
         ESC → "volver_al_menu"
```

---

## 📊 Datos que Maneja

### Héroe (self.heroe)
```python
heroe.clase                      # "Guerrero", "Mago"
heroe.ranuras_habilidad_max      # 4
heroe.habilidades_activas        # [id1, None, None, id2]
heroe.inventario_habilidades     # [id1, id2, id3, id4...]
```

### Base de Datos (self.habilidades_db)
```python
{
    "CORTE_X": {
        "id_habilidad": "CORTE_X",
        "nombre": "Corte Cruzado",
        "tipo": "Habilidad Fisica",
        "costo_mp": 5,
        "poder": 25,
        "alcance": "Un Enemigo",
        "descripcion": "Un ataque...",
        "clase_requerida": "Guerrero"  # Filtro
    }
}
```

---

## 🔍 Filtrado por Clase

**Problema:** Un Mago no puede usar habilidades de Guerrero

**Solución:**
```python
clase_heroe = self.heroe.clase  # "Mago"

for id_hab in self.heroe.inventario_habilidades:
    hab_data = self.habilidades_db.get(id_hab)
    clase_req = hab_data.get("clase_requerida", None)
    
    # Solo agregar si:
    # 1. clase_requerida es None (universal), o
    # 2. clase_requerida coincide con clase del héroe
    if clase_req is None or clase_req == clase_heroe:
        self.lista_inventario_habilidades.append(hab_data)
```

**Ejemplo:**
- Cloud (Guerrero) ve: Corte X, Golpe Fuerte, Embestida
- Terra (Mago) ve: Bola de Fuego, Tormenta de Hielo

---

## 🎯 Casos de Uso

### Caso 1: Equipar Primera Habilidad
```
1. Jugador entra a la pantalla
2. Ve "Corte Cruzado" en inventario
3. Presiona Enter → Modo ranura
4. Selecciona ranura [1]
5. Presiona Enter → Equipada
6. Vuelve a inventario
7. Ahora "• Corte Cruzado" tiene marcador
```

### Caso 2: Cambiar Habilidad Equipada
```
1. Ranura [1] tiene "Corte Cruzado"
2. Jugador selecciona "Golpe Fuerte" en inventario
3. Enter → Modo ranura
4. Selecciona ranura [1] (misma)
5. Enter → "Golpe Fuerte" reemplaza "Corte Cruzado"
6. "Corte Cruzado" sigue en inventario
```

### Caso 3: Desequipar
```
1. Jugador cambia a modo ranura (flecha →)
2. Selecciona ranura [2] con "Bola de Fuego"
3. Presiona X
4. Ranura [2] ahora muestra "[Vacío]"
5. "Bola de Fuego" sigue en inventario
```

### Caso 4: Ver Detalles
```
1. Modo inventario
2. Selecciona "Tormenta de Hielo"
3. Presiona D
4. Aparece pop-up grande con todos los datos
5. Presiona D o ESC para cerrar
```

---

## ⚙️ Configuración

### Variables Ajustables

```python
# Scroll
self.max_items_visibles_inventario = 8  # Items visibles a la vez

# Animación
self.velocidad_anim = 800  # ms entre frames
self.COOLDOWN_INPUT = 200  # ms entre inputs

# Colores (personaliza en __init__)
self.COLOR_CAJA = (0, 0, 139)
self.COLOR_TEXTO_SEL = (255, 255, 0)
# ... etc
```

---

## 🐛 Validaciones Implementadas

### En _equipar_habilidad():
✅ Ranura válida (0-3)  
✅ Habilidad en inventario  
✅ Expandir lista si es necesaria  

### En _desequipar_habilidad():
✅ Ranura válida  
✅ No crash si ranura ya vacía  

### En filtrado:
✅ Ignora `None` en inventario  
✅ Maneja habilidades sin `clase_requerida`  
✅ Compatibilidad con `habilidades_db` incompleta  

---

## 🔗 Integración con Otros Archivos

### Depende de:
- `src/heroe.py` → Objeto héroe con datos
- `database/habilidades_db.json` → Base de datos
- `main.py` → Carga HABILIDADES_DB global

### Usado por:
- `main.py` → Crea la pantalla cuando se selecciona héroe

### Similar a:
- `src/pantalla_equipo.py` → Mismo estilo de UI
- `src/pantalla_inventario.py` → Mismo sistema de scroll

---

## 📈 Mejoras Futuras (Opcional)

### Posibles expansiones:
1. **Drag & Drop:** Arrastrar habilidades con mouse
2. **Sonidos:** Efectos al equipar/desequipar
3. **Animaciones:** Transiciones suaves entre paneles
4. **Comparación:** Ver stat antes/después de equipar
5. **Atajos de teclado:** Números 1-4 para ranuras directas
6. **Previsualización:** Ver efecto en batalla antes de equipar

---

## ✅ Checklist de Funcionalidad

- [x] Filtrar por clase
- [x] Mostrar 4 ranuras
- [x] Equipar habilidad
- [x] Desequipar habilidad
- [x] Scroll en inventario
- [x] Ver detalles (pop-up)
- [x] Indicador visual de equipada
- [x] Colores por tipo
- [x] Animación de sprite
- [x] Validaciones de error
- [x] Instrucciones en pantalla
- [x] Volver al menú (ESC)

---

**Archivo:** `src/pantalla_habilidades.py`  
**Estado:** ✅ COMPLETO  
**Siguiente paso:** Conectar a main.py (Paso 7.18)  
**Fecha:** 2025-11-15
