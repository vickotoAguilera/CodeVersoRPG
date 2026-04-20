# Cambios Realizados en el Sistema de Inventario

## Fecha: 2025-11-15

## Problemas Solucionados

### 1. Superposición de Texto en las Pestañas
**Problema:** Las letras de las pestañas se superponían con el contenido del panel de items.

**Solución:**
- Movido el panel de items 40 píxeles hacia abajo para dar espacio a las pestañas
- Aumentado la altura de las pestañas de 30 a 35 píxeles
- Aumentado el ancho de las pestañas de 120 a 140 píxeles para acomodar 3 categorías
- Reducida la altura del panel de items en 40 píxeles para mantenerlo dentro de la caja principal
- **IMPLEMENTADO SISTEMA DE NAVEGACIÓN POR PESTAÑAS CON SCROLLBAR HORIZONTAL**

**Código modificado en `pantalla_inventario.py`:**
```python
# Línea 30: Nuevo modo de selección
self.modo = "seleccion_categoria"  # Primero seleccionas la categoría

# Línea 52-54: Sistema de scroll para pestañas
self.scroll_offset_tabs = 0
self.tabs_visibles_max = 3  # Se calcula dinámicamente

# Línea 145-209: Nueva lógica de navegación por modos
MODO 0: seleccion_categoria (navegas con LEFT/RIGHT, bajas con DOWN)
MODO 1: seleccion_item (navegas items con UP/DOWN, vuelves con UP en el primero)
MODO 2: seleccion_heroe (seleccionas a quién aplicar el item)

# Línea 391-447: Dibujo de pestañas con scroll
- Solo muestra pestañas COMPLETAS que caben en el espacio
- Calcula dinámicamente cuántas caben: tabs_que_caben = int(area_width / tab_width)
- Scrollbar horizontal aparece solo si hay más pestañas que espacio
- Cursor solo en la pestaña activa cuando estás en modo selección de categoría
```

### 2. Agregar Item de Ranuras a Especiales
**Problema:** El "Expansor de Ranuras" debía estar en la categoría "Especiales".

**Solución:**
El item ya estaba correctamente configurado en `items_db.json` con `"tipo": "Especial"` y ya se guardaba en `inventario_especiales`. El sistema ya funcionaba correctamente para mostrar estos items en la pestaña de Especiales.

### 3. Nueva Pestaña de Equipos
**Problema:** Los items de equipo necesitaban su propia pestaña separada de Consumibles y Especiales.

**Solución:**
- Agregada nueva categoría "Equipos" al array de categorías
- Implementada lógica en `_construir_lista_inventario()` para mostrar items equipables
- Los equipos se buscan en `equipo_db` en lugar de `items_db`
- Los equipos solo se pueden visualizar desde el inventario (para equiparlos hay que ir al menú de Equipo)

## Sistema de Navegación por Pestañas con Scroll Horizontal

### Flujo de Navegación

1. **Entras a la pantalla**: Estás en modo "selección de categoría" (pestañas arriba)
2. **Navegas con ←→**: Te mueves entre las pestañas (Consumibles, Especiales, Equipos, etc.)
3. **Scroll automático**: Si hay más pestañas que espacio, solo se muestran las que caben COMPLETAS
4. **Presionas ↓**: Entras al modo "selección de items" para ver los items de esa categoría
5. **Navegas items con ↑↓**: Te mueves por los items
6. **Presionas ↑ en el primer item**: Vuelves al modo "selección de categoría"
7. **ESC**: Vuelve al modo anterior (items → categorías → menú principal)

### Características del Scroll Horizontal

- **Solo pestañas COMPLETAS**: No se muestran pestañas cortadas a la mitad o por un borde
- **Cálculo dinámico**: El sistema calcula cuántas pestañas caben: `tabs_que_caben = int(area_width / tab_width)`
- **Scroll inteligente**: Cuando navegas, el scroll se ajusta para mantener visible la categoría actual
- **Scrollbar visual**: Barra horizontal amarilla (como las verticales) que muestra tu posición
- **Indicador de posición**: El cursor aparece solo en la pestaña activa cuando estás en ese modo

### Implementación Técnica

```python
# Cálculo de pestañas que caben (completas)
tabs_que_caben = max(1, int(tabs_area_width / tab_width))
self.tabs_visibles_max = tabs_que_caben

# Solo dibujar pestañas visibles
tabs_fin = min(self.scroll_offset_tabs + self.tabs_visibles_max, total_tabs)
tabs_visibles = self.categorias[self.scroll_offset_tabs:tabs_fin]

# Ajustar scroll al navegar
if self.categoria_actual >= self.scroll_offset_tabs + self.tabs_visibles_max:
    self.scroll_offset_tabs = self.categoria_actual - self.tabs_visibles_max + 1
elif self.categoria_actual < self.scroll_offset_tabs:
    self.scroll_offset_tabs = self.categoria_actual

# Scrollbar proporcional al número de pestañas ocultas
thumb_ancho = max(30, int((self.tabs_visibles_max / total_tabs) * scrollbar_ancho))
scroll_ratio = self.scroll_offset_tabs / (total_tabs - self.tabs_visibles_max)
thumb_x = scrollbar_x + int(scroll_ratio * thumb_pos_max)
```

## Estructura Final de Categorías

1. **Consumibles**: Pociones, Éteres, y otros items de un solo uso
2. **Especiales**: Llaves, Expansor de Ranuras, y otros items permanentes
3. **Equipos**: Armas, Armaduras, Accesorios (solo visualización)

## Controles

### Modo Selección de Categoría (arriba, en las pestañas)
- **Flechas Izquierda/Derecha**: Navegar entre categorías
- **TAB**: Ir a la siguiente categoría
- **Flecha Abajo**: Entrar a ver los items de la categoría
- **ESC**: Salir al menú principal

### Modo Selección de Item (abajo, en la lista)
- **Flechas Arriba/Abajo**: Navegar por los items
- **Flecha Arriba (en el primer item)**: Volver a selección de categorías
- **Enter**: Usar item (no disponible para Equipos)
- **ESC**: Volver a selección de categorías

### Modo Selección de Héroe (panel izquierdo)
- **Flechas Arriba/Abajo**: Seleccionar héroe
- **Enter**: Aplicar item al héroe seleccionado
- **ESC**: Volver a selección de items

## Notas Técnicas

- Los equipos se almacenan en `inventario` normal del héroe
- Los items especiales se almacenan en `inventario_especiales` del héroe
- Los consumibles se almacenan en `inventario` normal del héroe
- La categoría "Equipos" es solo informativa, no permite usar items
- Para equipar items hay que ir al menú "Equipo" desde el menú de pausa
- El número de pestañas visibles se calcula dinámicamente según el ancho disponible
- Solo se muestran pestañas completas, nunca cortadas
- El scrollbar horizontal solo aparece si hay más pestañas que las que caben
- El thumb del scrollbar es proporcional a la cantidad de pestañas visibles vs totales
- El cursor solo aparece en la pestaña activa cuando estás en modo "selección de categoría"
- El sistema es escalable: puedes agregar 10, 20 o más categorías y el scroll las manejará
