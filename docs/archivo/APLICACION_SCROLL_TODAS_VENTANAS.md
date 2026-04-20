# 📋 Aplicación del Sistema de Scroll a Todas las Ventanas

## Fecha: 2025-11-15

---

## ✅ Estado Actual de Implementación

### Pantallas CON Scroll Implementado:

#### 1. **PantallaInventario** ✅
- **Scroll Horizontal**: Pestañas de categorías (Consumibles, Especiales, Equipos)
  - Sistema de navegación por modos
  - Solo muestra pestañas completas
  - Scrollbar horizontal visual
- **Scroll Vertical**: Lista de items dentro de cada categoría
  - 10 items visibles a la vez
  - Scrollbar vertical con thumb proporcional
  
**Archivos**: `src\pantalla_inventario.py`

#### 2. **PantallaItems** (Batalla) ✅
- **Scroll Vertical**: Lista de items usables en batalla
  - 8 items visibles a la vez
  - Scrollbar vertical
  - Muestra cantidades
  
**Archivos**: `src\pantalla_items.py`

#### 3. **MenuPausa** ✅ (RECIÉN ACTUALIZADO)
- **Scroll Vertical**: Lista de héroes en el panel derecho
  - 4 héroes visibles a la vez
  - Scrollbar vertical cuando hay más de 4 héroes
  - Integrado con el sistema de navegación existente
  
**Archivos**: `src\menu_pausa.py`

**Cambios realizados:**
```python
# Variables agregadas
self.scroll_offset_heroes = 0
self.heroes_visibles_max = 4

# Navegación actualizada con ajuste de scroll
if self.heroe_seleccionado_idx >= self.scroll_offset_heroes + self.heroes_visibles_max:
    self.scroll_offset_heroes = self.heroe_seleccionado_idx - self.heroes_visibles_max + 1

# Dibujo con slice de lista
heroes_visibles = grupo_heroes[self.scroll_offset_heroes:heroes_fin]

# Scrollbar vertical agregada
```

---

## 🔄 Pantallas Pendientes de Actualización

### 4. **PantallaHabilidades**
**Estado**: Variables de scroll definidas pero necesita verificación

**Scrolls necesarios:**
- **Scroll Vertical**: Inventario de habilidades (izquierda)
  - Ya tiene `self.scroll_inventario = 0`
  - Ya tiene `self.max_items_visibles_inventario = 8`
  - ✅ Parece estar implementado

- **Scroll Vertical**: Ranuras activas (arriba derecha)
  - Ya tiene `self.scroll_ranuras = 0`
  - Ya tiene `self.max_items_visibles_ranuras = 4`
  - ✅ Parece estar implementado

**Acción**: Verificar funcionamiento y agregar scrollbars visuales si faltan

**Archivos**: `src\pantalla_habilidades.py`

### 5. **PantallaEquipo**
**Estado**: Sin scroll implementado

**Scrolls necesarios:**
- **Scroll Vertical**: Lista de items equipables (derecha)
  - Cuando hay más items que espacio disponible
  - Debe mostrar items que se pueden equipar en la ranura seleccionada
  
**Acción**: Implementar scroll vertical para lista de items

**Archivos**: `src\pantalla_equipo.py`

### 6. **PantallaListaMagias** (Batalla)
**Estado**: Desconocido

**Scrolls necesarios:**
- **Scroll Vertical**: Lista de magias/hechizos usables en batalla
  
**Acción**: Verificar e implementar scroll si es necesario

**Archivos**: `src\pantalla_lista_magias.py`

### 7. **PantallaListaHabilidades** (Batalla)
**Estado**: Desconocido

**Scrolls necesarios:**
- **Scroll Vertical**: Lista de habilidades usables en batalla
  
**Acción**: Verificar e implementar scroll si es necesario

**Archivos**: `src\pantalla_lista_habilidades.py`

---

## 📚 Patrón de Implementación Estándar

Para cualquier nueva pantalla que necesite scroll, seguir este patrón:

### Variables de Inicialización:
```python
# En __init__()
self.scroll_offset_[nombre] = 0              # Primer elemento visible
self.[nombre]_visibles_max = N               # Cuántos caben en pantalla
self.[nombre]_seleccionado_idx = 0          # Elemento seleccionado
```

### Navegación (Vertical):
```python
# En update()
if teclas[pygame.K_DOWN]:
    self.item_idx = (self.item_idx + 1) % total_items
    
    # Ajustar scroll (hacia abajo)
    if self.item_idx >= self.scroll_offset + self.visibles_max:
        self.scroll_offset = self.item_idx - self.visibles_max + 1

elif teclas[pygame.K_UP]:
    self.item_idx = (self.item_idx - 1) % total_items
    
    # Ajustar scroll (hacia arriba)
    if self.item_idx < self.scroll_offset:
        self.scroll_offset = self.item_idx
```

### Dibujo:
```python
# En draw()
# Calcular elementos visibles
total = len(lista_completa)
fin = min(self.scroll_offset + self.visibles_max, total)
visibles = lista_completa[self.scroll_offset:fin]

# Dibujar solo los visibles
for idx_visual, elemento in enumerate(visibles):
    idx_real = self.scroll_offset + idx_visual
    # ... dibujar elemento

# Scrollbar (si es necesario)
if total > self.visibles_max:
    # ... dibujar scrollbar
```

---

## 🎨 Estilo de Scrollbar Estándar

```python
# Colores estándar para todas las scrollbars
COLOR_SCROLLBAR_FONDO = (50, 50, 100)  # Azul oscuro
COLOR_SCROLLBAR = (100, 100, 255)      # Azul claro/Amarillo

# Vertical
scrollbar_x = area.right - 10
scrollbar_y = area.y + 10
scrollbar_ancho = 6
scrollbar_altura = area.height - 20

# Horizontal
scrollbar_x = area.x + 10
scrollbar_y = area.bottom + 5
scrollbar_ancho = area.width - 20
scrollbar_altura = 8

# Thumb proporcional
thumb_tam = max(15, int((visibles / totales) * scrollbar_tam))
scroll_ratio = scroll_offset / (total - visibles)
thumb_pos = scrollbar_pos + int(scroll_ratio * (scrollbar_tam - thumb_tam))
```

---

## ✨ Ventajas del Sistema Unificado

1. **Consistencia**: Todas las pantallas se comportan igual
2. **Escalabilidad**: Puedes agregar 100+ items sin problemas
3. **Visual**: Scrollbar siempre muestra tu posición
4. **Suavidad**: Navegación fluida con cooldown
5. **Reutilizable**: Copiar/pegar el código base y adaptar

---

## 📝 Checklist de Implementación

Al implementar scroll en una nueva pantalla, verificar:

- [ ] Variables inicializadas (`scroll_offset`, `visibles_max`, `seleccionado_idx`)
- [ ] Navegación con teclas (UP/DOWN o LEFT/RIGHT)
- [ ] Ajuste automático del scroll al navegar
- [ ] Slice de lista para elementos visibles
- [ ] Loop solo sobre elementos visibles
- [ ] Cálculo correcto de `idx_real` vs `idx_visual`
- [ ] Scrollbar solo si `total > visibles_max`
- [ ] Thumb con tamaño proporcional
- [ ] Thumb con posición calculada
- [ ] Cursor en elemento seleccionado (usando `idx_real`)
- [ ] Cooldown de input (200ms)

---

## 🔮 Casos de Uso Futuros

### Diálogos de NPCs:
- Scroll vertical para conversaciones largas
- Auto-scroll al final cuando habla el NPC
- Scrollbar a la derecha

### Logs de Batalla:
- Scroll vertical para historial de acciones
- Auto-scroll al final con cada nueva acción
- Limitar a últimos 100 eventos

### Tiendas:
- Scroll vertical para lista de items en venta
- Scroll horizontal para categorías de tienda
- Doble scroll como el inventario

### Libros/Documentos:
- Scroll vertical para texto largo
- Páginas renderizadas dinámicamente
- Barra de progreso de lectura

---

## 📖 Archivos de Referencia

- **Guía Completa**: `GUIA_SISTEMA_SCROLL_COMPLETO.md`
- **Ejemplo Vertical**: `EJEMPLO_SCROLL_VERTICAL.py`
- **Ejemplo Horizontal**: `EJEMPLO_SCROLL_HORIZONTAL.py`
- **Implementación Real**: `src\pantalla_inventario.py` (la más completa)

---

*Documento actualizado: 2025-11-15*
*Próxima actualización: Cuando se complete PantallaEquipo*
