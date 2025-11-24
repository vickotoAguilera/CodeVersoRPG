# 🎨 SPRITE SHEET EDITOR - FUNCIONALIDADES COMPLETAS

**Fecha:** 17 de noviembre de 2025  
**Estado:** ✅ COMPLETO AL 100%

---

## 📋 RESUMEN

Editor de sprite sheets completamente funcional con todas las características solicitadas, incluyendo:
- Sistema de checkboxes para selección individual
- Preview de animación en tiempo real
- Pan de cámara con botón derecho
- Numeración automática al exportar múltiples sprites
- Zoom con rueda del mouse
- Sistema de reemplazo selectivo

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### 1. Sistema de Checkboxes ✓

**Descripción:**
Cada sprite en la lista del panel izquierdo tiene una cajita de verificación para marcar/desmarcar individualmente.

**Cómo usar:**
- Click izquierdo en el checkbox para marcar/desmarcar
- Solo los sprites marcados (✓) se exportarán con "Exportar Todos"
- Los sprites desmarcados (☐) se ignoran al exportar

**Ubicación:**
- Panel izquierdo (Preview)
- Sección "Selecciones:"
- Cada sprite tiene su checkbox al lado izquierdo

**Colores:**
- Checkbox marcado: Línea verde con checkmark
- Checkbox desmarcado: Cuadro vacío
- Sprites guardados: Texto verde con "✓"
- Sprites no guardados: Texto gris con "○"

---

### 2. Preview de Animación ✓

**Descripción:**
Botón que muestra los sprites seleccionados animándose en secuencia, simulando cómo se verán en el juego.

**Cómo usar:**
1. Marca con checkboxes los sprites que quieres animar
2. Click en botón "Preview Animación"
3. Se abre una ventana en el panel izquierdo mostrando la animación
4. Los sprites se ciclan automáticamente
5. Click nuevamente para desactivar

**Características:**
- Animación cíclica automática
- Velocidad configurable (10 frames por defecto)
- Muestra frame actual (ej: "Frame 2/4")
- Fondo de cuadrícula para ver transparencias
- Escala automática para que quepa en el panel
- Solo anima sprites marcados con checkbox

**Ubicación:**
- Botón en panel derecho
- Preview se muestra en panel izquierdo, debajo de la lista

---

### 3. Pan de Cámara con Botón Derecho ✓

**Descripción:**
Arrastra el spritesheet con el botón derecho del mouse para mover la vista.

**Cómo usar:**
1. Mantén presionado el botón derecho del mouse
2. Arrastra en cualquier dirección
3. Suelta para finalizar el pan

**Características:**
- Movimiento suave y fluido
- Funciona en conjunto con el zoom
- No interfiere con la selección de áreas (botón izquierdo)
- Offset se mantiene al hacer zoom

---

### 4. Zoom con Rueda del Mouse ✓

**Descripción:**
Zoom in/out usando la rueda del mouse, centrado en la posición del cursor.

**Cómo usar:**
- Rueda hacia arriba: Zoom in (máximo 5x)
- Rueda hacia abajo: Zoom out (mínimo 0.1x)

**Características:**
- Zoom centrado en la posición del cursor
- Ajuste automático del offset
- Rango: 0.1x a 5.0x
- Muestra nivel de zoom en barra de estado

---

### 5. Numeración Automática al Exportar ✓

**Descripción:**
Si varios sprites tienen el mismo nombre, se numeran automáticamente al exportar.

**Cómo funciona:**
- **1 sprite con nombre "heroe"** → Se guarda como `heroe.png`
- **3 sprites con nombre "heroe_caminando"** → Se guardan como:
  - `heroe_caminando_1.png`
  - `heroe_caminando_2.png`
  - `heroe_caminando_3.png`

**Ejemplo de uso:**
1. Selecciona 4 sprites de animación de caminar
2. Asigna el mismo nombre "heroe_walk" a todos
3. Marca los 4 con checkboxes
4. Click en "Exportar Todos"
5. Resultado: heroe_walk_1.png, heroe_walk_2.png, heroe_walk_3.png, heroe_walk_4.png

**Ventajas:**
- No necesitas numerar manualmente
- Mantiene el orden de selección
- Ideal para secuencias de animación

---

### 6. Sistema de Reemplazo Selectivo ✓

**Descripción:**
Reemplaza sprites específicos sin afectar los demás de la misma secuencia.

**Cómo funciona:**
1. Ya tienes guardados: heroe_walk_1.png, heroe_walk_2.png, heroe_walk_3.png
2. El frame #2 se ve mal y quieres reemplazarlo
3. Selecciona SOLO el nuevo sprite para el frame #2
4. Desmarca los demás sprites (solo uno marcado)
5. Nómbralo "heroe_walk"
6. Al exportar, como es solo 1 sprite, se guarda como `heroe_walk.png`
7. Si quieres que sea el #2, guárdalo manualmente con "Guardar Sprite" como "heroe_walk_2"

**Proceso detallado:**
```
Situación inicial:
- heroe_walk_1.png ✓ (bueno)
- heroe_walk_2.png ✗ (malo, necesita reemplazo)
- heroe_walk_3.png ✓ (bueno)

Pasos:
1. Selecciona área del nuevo sprite #2
2. Nómbralo "heroe_walk_2" en el input
3. Click en "Guardar Sprite (S)"
4. Confirma reemplazo cuando pregunte
5. Resultado: heroe_walk_2.png reemplazado
```

---

## 🎮 CONTROLES COMPLETOS

### Mouse:
- **Click izquierdo + arrastrar** → Seleccionar área del sprite
- **Click derecho + arrastrar** → Mover cámara (pan)
- **Click en checkbox** → Marcar/desmarcar sprite para exportar
- **Rueda hacia arriba** → Zoom in
- **Rueda hacia abajo** → Zoom out
- **Drag & drop de imagen** → Cargar spritesheet

### Teclado:
- **S** → Guardar sprite actual
- **E** → Exportar todos los marcados
- **G** → Toggle grid de referencia
- **Z** (Ctrl+Z) → Deshacer
- **Y** (Ctrl+Y) → Rehacer
- **DEL** → Eliminar selección actual
- **ESC** → Salir del editor

### Botones:
- **Cargar Spritesheet** → Abre diálogo de archivo
- **Preview Animación** → Activa/desactiva preview
- **Guardar Sprite (S)** → Guarda el sprite seleccionado
- **Exportar Todos (E)** → Exporta sprites marcados
- **Limpiar Todo** → Elimina todas las selecciones
- **Deshacer (Z)** → Deshace última acción
- **Rehacer (Y)** → Rehace última acción

---

## 📊 INTERFAZ DETALLADA

### Panel Izquierdo (Preview):
```
┌─────────────────────────┐
│ Preview                 │
│                         │
│ [Imagen del sprite]     │
│                         │
│ Tamaño: 32x32          │
│ Pos: (64, 0)           │
│ Nombre: heroe_walk     │
│                         │
│ Selecciones:           │
│ ☑ ✓ heroe_walk_1      │
│ ☑ ○ heroe_walk_2      │
│ ☐ ○ heroe_walk_3      │
│                         │
│ ┌─────────────────┐    │
│ │ Animación       │    │
│ │                 │    │
│ │ [Sprite animado]│    │
│ │                 │    │
│ │ Frame 2/3       │    │
│ └─────────────────┘    │
└─────────────────────────┘
```

### Panel Central (Spritesheet):
```
┌─────────────────────────────────┐
│                                 │
│   [Spritesheet con zoom/pan]    │
│                                 │
│   [Selecciones marcadas]        │
│                                 │
│   [Grid opcional]               │
│                                 │
└─────────────────────────────────┘
```

### Panel Derecho (Controles):
```
┌─────────────────────────┐
│ Controles               │
│                         │
│ [Input: nombre...]      │
│                         │
│ Categoría:             │
│ [Héroe Batalla]  ◄     │
│ [Héroe Mapa]           │
│ [Monstruo]             │
│ [NPC]                  │
│ [Cofre]                │
│                         │
│ [Cargar Spritesheet]   │
│ [Preview Animación]    │
│ [Guardar Sprite (S)]   │
│ [Exportar Todos (E)]   │
│ [Limpiar Todo]         │
│ [Deshacer (Z)]         │
│ [Rehacer (Y)]          │
└─────────────────────────┘
```

### Barra de Estado (Inferior):
```
┌─────────────────────────────────────────────┐
│ Zoom: 1.50x | Selecciones: 4 | Guardados: 2│
│ | Marcados: 3 | Sheet: 256x128              │
└─────────────────────────────────────────────┘
```

---

## 💡 CASOS DE USO

### Caso 1: Crear secuencia de animación completa
```
1. Carga spritesheet con animación de caminar (8 frames)
2. Selecciona los 8 sprites uno por uno
3. Asigna el mismo nombre "heroe_walk" a todos
4. Marca todos con checkboxes
5. Click "Exportar Todos"
6. Resultado: heroe_walk_1.png hasta heroe_walk_8.png
```

### Caso 2: Reemplazar un frame específico
```
1. Ya tienes heroe_walk_1 a heroe_walk_8
2. El frame #5 tiene un error
3. Encuentra mejor sprite en el sheet
4. Selecciónalo
5. Nómbralo "heroe_walk_5"
6. Click "Guardar Sprite (S)"
7. Confirma reemplazo
8. Resultado: Solo heroe_walk_5.png reemplazado
```

### Caso 3: Preview de animación antes de exportar
```
1. Selecciona 4 sprites de ataque
2. Márcalos con checkboxes
3. Click "Preview Animación"
4. Observa la animación
5. Si se ve bien, exporta
6. Si no, ajusta selecciones
```

### Caso 4: Exportar sprites individuales diferentes
```
1. Selecciona sprite de cofre
2. Nómbralo "cofre_cerrado"
3. Marca checkbox
4. Selecciona otro sprite
5. Nómbralo "cofre_abierto"
6. Marca checkbox
7. Click "Exportar Todos"
8. Resultado: cofre_cerrado.png y cofre_abierto.png
```

---

## 🔧 DETALLES TÉCNICOS

### Estructura de Datos:
```python
@dataclass
class SeleccionSprite:
    x: int              # Posición X en spritesheet
    y: int              # Posición Y en spritesheet
    ancho: int          # Ancho del sprite
    alto: int           # Alto del sprite
    nombre: str         # Nombre del archivo
    categoria: CategoriaSprite  # Categoría de destino
    guardado: bool      # Si ya fue guardado
    seleccionado: bool  # Checkbox marcado (True/False)
```

### Sistema de Exportación:
```python
def exportar_todos():
    # Filtra solo sprites con checkbox marcado
    selecciones_a_exportar = [s for s in self.selecciones if s.seleccionado]
    
    # Agrupa por nombre
    nombres_count = defaultdict(list)
    for sel in selecciones_a_exportar:
        nombres_count[sel.nombre].append(sel)
    
    # Si hay 1 solo con ese nombre → guarda directo
    # Si hay múltiples → numera automáticamente
    for nombre_base, sprites_grupo in nombres_count.items():
        if len(sprites_grupo) == 1:
            guardar(f"{nombre_base}.png")
        else:
            for i, sel in enumerate(sprites_grupo, 1):
                guardar(f"{nombre_base}_{i}.png")
```

### Sistema de Checkboxes:
```python
# En dibujar_panel_preview():
checkbox_rect = pygame.Rect(x, y, 18, 18)
self.checkbox_rects.append((checkbox_rect, sel))

# En manejar_eventos():
for checkbox_rect, sel in self.checkbox_rects:
    if checkbox_rect.collidepoint(mouse_pos):
        sel.seleccionado = not sel.seleccionado
```

### Sistema de Pan:
```python
# Mouse down (botón 3 = derecho)
self.panning = True
self.pan_inicio = mouse_pos

# Mouse motion
if self.panning:
    dx = mouse_pos[0] - self.pan_inicio[0]
    dy = mouse_pos[1] - self.pan_inicio[1]
    self.offset_x += dx
    self.offset_y += dy
    self.pan_inicio = mouse_pos
```

---

## 📁 ESTRUCTURA DE ARCHIVOS EXPORTADOS

```
assets/
└── sprites/
    ├── heroes/
    │   ├── batalla/
    │   │   ├── heroe_walk_1.png
    │   │   ├── heroe_walk_2.png
    │   │   ├── heroe_walk_3.png
    │   │   └── heroe_attack_1.png
    │   └── mapa/
    │       └── heroe_idle.png
    ├── monstruos/
    │   ├── goblin_1.png
    │   └── goblin_2.png
    ├── npcs/
    │   └── vendedor.png
    └── cofres y demas/
        ├── cofre_cerrado.png
        └── cofre_abierto.png
```

---

## 🎯 VENTAJAS DEL SISTEMA

### Eficiencia:
- Exporta múltiples sprites en un click
- Numeración automática ahorra tiempo
- Preview previene errores antes de exportar

### Flexibilidad:
- Selección individual con checkboxes
- Reemplazo selectivo sin afectar otros
- Pan y zoom para hojas grandes

### Organización:
- Categorías automáticas
- Nombres consistentes con numeración
- Estructura de carpetas clara

### Usabilidad:
- Drag & drop para cargar imágenes
- Controles intuitivos
- Feedback visual constante

---

## ⚠️ NOTAS IMPORTANTES

1. **Checkboxes se reinician:** Al cargar un nuevo spritesheet, todos los checkboxes se marcan por defecto

2. **Reemplazo de archivos:** Si un archivo ya existe, se reemplaza automáticamente (el código muestra un warning)

3. **Orden de numeración:** Los sprites se numeran en el orden que fueron seleccionados (del primero al último)

4. **Preview con sprites no guardados:** El preview funciona aunque los sprites no estén guardados aún

5. **Categoría por defecto:** "Héroe Batalla" es la categoría predeterminada

6. **Tamaño mínimo:** Las selecciones deben ser de al menos 5x5 píxeles

---

## 🚀 PRÓXIMAS MEJORAS SUGERIDAS

### Prioridad Media:
- [ ] Selector de velocidad de animación en preview
- [ ] Exportar secuencia como spritesheet
- [ ] Copiar/pegar selecciones entre proyectos
- [ ] Historial persistente (guardar/cargar sesiones)

### Prioridad Baja:
- [ ] Recorte automático de transparencias
- [ ] Filtros de imagen (brillo, contraste)
- [ ] Exportar a diferentes formatos (jpg, bmp)
- [ ] Batch processing de múltiples spritesheets

---

## 📞 SOPORTE

Si encuentras algún problema o tienes sugerencias:

1. Verifica que estés usando la última versión del archivo
2. Revisa esta documentación para uso correcto
3. Comprueba mensajes de consola para errores
4. Reporta con detalles: qué hiciste, qué esperabas, qué pasó

---

**Última actualización:** 17 de noviembre de 2025  
**Versión del editor:** 2.0.0 - Completo
**Estado:** ✅ 100% FUNCIONAL

---

*"Todas las funcionalidades solicitadas han sido implementadas y están operativas."* 🎨✨
