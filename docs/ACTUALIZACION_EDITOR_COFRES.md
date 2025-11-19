# Actualización Editor de Cofres - 19 Nov 2025

## Problemas Resueltos

### 1. Bug: Loot Random Sumaba Items

**Problema:** Al presionar "Generar Loot Random" múltiples veces, los items se acumulaban en lugar de reemplazarse.

**Solución:**

```python
# En _generar_loot_random(), línea 493:
# Limpiar contenido previo antes de generar nuevo loot
cofre.items_contenido = {}
cofre.equipo_contenido = {}
cofre.especiales_contenido = {}
cofre.oro = 0
```

Ahora cada vez que presionas el botón, se genera un loot completamente nuevo.

---

## Nuevas Funcionalidades

### 2. Sistema de Selección con Checkboxes

**Columna Izquierda del Modal:**

- ✅ Checkboxes junto a cada item disponible
- ✅ 3 categorías: Consumibles (10), Equipo (10), Especiales (10)
- ✅ Click en checkbox para marcar/desmarcar
- ✅ Items seleccionados se destacan con verde

**Botón "Agregar (N)":**

- Muestra el total de items seleccionados
- Se activa solo si hay items seleccionados (verde) o se desactiva (gris)
- Al presionar, agrega todos los items seleccionados al cofre con cantidad 1
- Limpia automáticamente las selecciones

### 3. Editor de Cantidad por Item

**Columna Derecha del Modal:**
Cada item en el cofre ahora tiene:

1. **Nombre del item** (truncado a 20 caracteres)
2. **Input de cantidad** (cuadro gris con `x N`)
3. **Botón X** (rojo para eliminar)

**Cómo Editar Cantidad:**

1. Click en el cuadro de cantidad de cualquier item
2. El input se activa (fondo amarillo con cursor `_`)
3. Escribe el nuevo número (solo dígitos)
4. Presiona **ENTER** para confirmar
5. Presiona **ESC** para cancelar

**Atajos de Teclado:**

- `ENTER` → Confirmar cantidad
- `ESC` → Cancelar edición
- `BACKSPACE` → Borrar dígito
- `0-9` → Escribir cantidad

### 4. Bloqueo de Creación Durante Edición

Ahora cuando el modal está abierto:

- ❌ No puedes crear nuevos cofres con click izquierdo
- ❌ No puedes seleccionar otros cofres
- ✅ Solo puedes editar el cofre actual

Esto previene clicks accidentales fuera del modal.

---

## Flujo de Trabajo Actualizado

### Agregar Items Manualmente:

1. Click derecho en cofre → abre modal
2. Selecciona items con checkboxes en la columna izquierda
3. Click en "Agregar (N)" → items van al cofre con cantidad 1
4. Click en la cantidad para editarla
5. Escribe nuevo número + ENTER

### Ejemplo Práctico:

```
Quiero que el cofre tenga:
- 5 Pociones de HP
- 2 Pociones de Mana
- 1 Espada de Hierro

Pasos:
1. Marca checkbox de "Poción de HP"
2. Marca checkbox de "Poción de Mana"
3. Marca checkbox de "Espada de Hierro"
4. Click "Agregar (3)"
5. Click en "x 1" de Poción HP → escribe 5 → ENTER
6. Click en "x 1" de Poción Mana → escribe 2 → ENTER
7. (Espada queda en 1)
8. Click "Cerrar"
```

### Generar Loot Random:

1. Click derecho en cofre → abre modal
2. Click "Generar Loot Random"
3. ✅ Contenido previo se limpia
4. ✅ Se genera nuevo loot según tipo de cofre
5. Edita cantidades manualmente si quieres ajustar

---

## Cambios en la UI

### Modal Ampliado:

- **Tamaño:** 1200x800 → 1300x800 px
- **Columna izquierda:** 350px → 400px (más espacio para checkboxes)
- **Columna derecha:** 350px → 400px (más espacio para inputs)

### Colores:

- Checkbox marcado: verde `(100, 255, 100)`
- Input activo: amarillo `(255, 255, 100)`
- Botón agregar activo: verde `(50, 180, 50)`
- Botón agregar inactivo: gris `(80, 80, 80)`
- Botón eliminar (X): rojo `(150, 50, 50)`

---

## Código Modificado

### Archivos:

- `editor_cofres.py` (1316 líneas)

### Líneas Clave:

- **167-176**: Variables de selección y edición
- **493-500**: Limpieza de loot en `_generar_loot_random()`
- **570-598**: Manejo de teclado para editar cantidad
- **856-1247**: Modal completo reescrito

### Nuevas Variables en `EditorCofres`:

```python
self.items_seleccionados = set()         # IDs de consumibles seleccionados
self.equipo_seleccionado = set()         # IDs de equipo seleccionado
self.especiales_seleccionados = set()    # IDs de especiales seleccionados
self.editando_cantidad = None            # Tuple: (tipo, item_id)
self.input_cantidad = ""                 # String con cantidad siendo editada
```

---

## Testing

### Casos Probados:

- ✅ Checkboxes marcan/desmarcan correctamente
- ✅ Botón agregar solo activo con selección
- ✅ Items se agregan al cofre con cantidad 1
- ✅ Click en cantidad activa input
- ✅ ENTER confirma, ESC cancela
- ✅ Botón X elimina items del cofre
- ✅ Loot random limpia contenido previo
- ✅ Modal bloquea creación de cofres
- ✅ Sin errores de compilación

### Pendiente:

- [ ] Scroll vertical si hay más de 10-12 items en categorías
- [ ] Drag & drop desde lista disponible a contenido cofre
- [ ] Filtro/búsqueda de items por nombre
- [ ] Teclas rápidas (Ctrl+A = agregar, Ctrl+L = limpiar)

---

## Notas Técnicas

### Debouncing:

Todos los clicks tienen `pygame.time.wait(150)` para evitar múltiples triggers.

### Limitaciones:

- Muestra máximo 10 items por categoría en lista disponible
- Muestra máximo 12 items por categoría en contenido cofre
- Nombres truncados a 20-28 caracteres

### Performance:

- Sin lag detectado con listas actuales
- Modal renderiza 30+ elementos interactivos por frame sin problemas

---

## Próximos Pasos Sugeridos

1. **Scroll en Listas:** Agregar scroll vertical para ver más de 10 items
2. **Búsqueda:** Input de texto para filtrar items por nombre
3. **Presets:** Guardar/cargar configuraciones de cofre predefinidas
4. **Sprites:** Mostrar miniaturas de items en las listas
5. **Validación:** Advertir si el cofre está vacío antes de cerrar

---

**Última Actualización:** 19 de noviembre de 2025, 20:30
