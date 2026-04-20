# 🎯 GUÍA MAESTRA DEL SISTEMA DE SCROLL
## Patrón de Diseño Definitivo para Scrolls Horizontales y Verticales

---

## 📌 IMPORTANTE - LEER PRIMERO

**Este es el patrón de diseño definitivo para implementar scrolls en el proyecto.**

Cuando se hable de "scrollear algo", se debe implementar siguiendo estos patrones exactamente.
Este sistema se usará para:
- ✅ Listas de items (Ya implementado)
- ✅ Pestañas/Categorías (Ya implementado)  
- 🔜 Diálogos de personajes
- 🔜 Textos largos
- 🔜 Logs de batalla
- 🔜 Cualquier contenido que no quepa en pantalla

---

## 🔷 PATRÓN 1: SCROLL VERTICAL (Arriba ↕ Abajo)

### Cuándo usar:
- Listas de items
- Listas de personajes
- Textos largos (diálogos)
- Logs de eventos
- Cualquier contenido que se lee de arriba hacia abajo

### Ejemplo Completo con Explicación:

```python
# ==========================================
# PASO 1: INICIALIZACIÓN (En __init__)
# ==========================================

# Variables de control del scroll vertical
self.scroll_offset_items = 0        # Índice del primer elemento visible
self.items_visibles_max = 10        # Cuántos elementos caben en pantalla a la vez

# Lista de elementos a mostrar
self.lista_items_totales = []       # Todos los items disponibles
# Ejemplo: ["Poción", "Éter", "Llave", "Espada", ...] (20 items totales)

# ==========================================
# PASO 2: NAVEGACIÓN (En update())
# ==========================================

def update(self, teclas):
    tiempo_actual = pygame.time.get_ticks()
    
    if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
        
        # BAJAR: Mover cursor hacia abajo
        if teclas[pygame.K_DOWN]:
            num_items = len(self.lista_items_totales)
            self.item_seleccionado_idx = (self.item_seleccionado_idx + 1) % num_items
            
            # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (abajo)
            # Si el índice seleccionado >= primer_visible + máximo_visible
            # Significa que el cursor está fuera del área visible hacia abajo
            if self.item_seleccionado_idx >= self.scroll_offset_items + self.items_visibles_max:
                # Mover el scroll hacia abajo (aumentar el offset)
                self.scroll_offset_items = self.item_seleccionado_idx - self.items_visibles_max + 1
            
            self.tiempo_ultimo_input = tiempo_actual
        
        # SUBIR: Mover cursor hacia arriba
        elif teclas[pygame.K_UP]:
            num_items = len(self.lista_items_totales)
            self.item_seleccionado_idx = (self.item_seleccionado_idx - 1) % num_items
            
            # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (arriba)
            # Si el índice seleccionado < primer_visible
            # Significa que el cursor está fuera del área visible hacia arriba
            if self.item_seleccionado_idx < self.scroll_offset_items:
                # Mover el scroll hacia arriba (disminuir el offset)
                self.scroll_offset_items = self.item_seleccionado_idx
            
            self.tiempo_ultimo_input = tiempo_actual

# ==========================================
# PASO 3: DIBUJO DE ELEMENTOS (En draw())
# ==========================================

def draw(self, pantalla):
    # Área donde se dibujarán los elementos
    start_x = 100
    start_y = 100
    line_height = 35  # Altura de cada línea/elemento
    
    # 🔑 CLAVE: Calcular qué elementos son visibles
    total_items = len(self.lista_items_totales)
    items_fin = min(self.scroll_offset_items + self.items_visibles_max, total_items)
    items_visibles = self.lista_items_totales[self.scroll_offset_items:items_fin]
    
    # EJEMPLO:
    # Si tenemos 20 items totales y solo caben 10 en pantalla:
    # scroll_offset_items = 5  (empezamos desde el item 5)
    # items_visibles_max = 10  (mostramos 10 items)
    # items_fin = min(5 + 10, 20) = 15
    # items_visibles = lista[5:15]  -> Mostramos items del 5 al 14
    
    # 🔑 CLAVE: Dibujar solo los elementos visibles
    for idx_visual, item in enumerate(items_visibles):
        # idx_visual: posición visual (0-9 si mostramos 10)
        # idx_real: posición real en la lista completa
        idx_real = self.scroll_offset_items + idx_visual
        
        # Posición Y de este elemento
        pos_y = start_y + (idx_visual * line_height)
        
        # Color y cursor si está seleccionado
        color = self.COLOR_TEXTO_SEL if idx_real == self.item_seleccionado_idx else self.COLOR_TEXTO
        
        if idx_real == self.item_seleccionado_idx:
            # Dibujar cursor al lado del elemento seleccionado
            if self.cursor_img:
                cursor_rect = self.cursor_img.get_rect(midright=(start_x - 5, pos_y + 10))
                pantalla.blit(self.cursor_img, cursor_rect)
        
        # Dibujar el elemento
        item_surf = self.fuente.render(item, True, color)
        pantalla.blit(item_surf, (start_x, pos_y))
    
    # ==========================================
    # PASO 4: DIBUJO DE SCROLLBAR VERTICAL
    # ==========================================
    
    # 🔑 CLAVE: Solo dibujar scrollbar si hay más elementos que los visibles
    if total_items > self.items_visibles_max:
        # Geometría del scrollbar
        scrollbar_altura = 400  # Altura total disponible para el scrollbar
        scrollbar_x = start_x + 500  # Posición X (a la derecha del contenido)
        scrollbar_y = start_y
        scrollbar_ancho = 6  # Ancho del scrollbar
        
        # Barra de fondo (azul oscuro)
        pygame.draw.rect(pantalla, (50, 50, 100), 
                        (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura), 
                        border_radius=3)
        
        # 🔑 CLAVE: Calcular tamaño del thumb (proporcional)
        # Tamaño del thumb = (elementos_visibles / elementos_totales) * altura_scrollbar
        thumb_altura = max(15, int((self.items_visibles_max / total_items) * scrollbar_altura))
        
        # EJEMPLO: Si tenemos 10 visibles de 20 totales:
        # thumb_altura = (10 / 20) * 400 = 200 píxeles (50% de la barra)
        
        # 🔑 CLAVE: Calcular posición del thumb
        # Posición máxima = altura_scrollbar - altura_thumb
        thumb_pos_max = scrollbar_altura - thumb_altura
        
        # Ratio de scroll = offset_actual / máximo_offset_posible
        # thumb_y = posición_inicial + (ratio * posición_máxima)
        thumb_y = scrollbar_y + int((self.scroll_offset_items / (total_items - self.items_visibles_max)) * thumb_pos_max)
        
        # EJEMPLO: Si estamos en offset=5 con 20 items y 10 visibles:
        # ratio = 5 / (20-10) = 5/10 = 0.5 (50%)
        # thumb_y = 100 + (0.5 * 200) = 200 (en la mitad)
        
        # Dibujar thumb (amarillo/azul claro)
        pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                        (scrollbar_x, thumb_y, scrollbar_ancho, thumb_altura), 
                        border_radius=3)
```

---

## 🔶 PATRÓN 2: SCROLL HORIZONTAL (Izquierda ↔ Derecha)

### Cuándo usar:
- Pestañas/Categorías
- Menús horizontales
- Galerías de imágenes
- Barras de habilidades
- Cualquier contenido que se lee de izquierda a derecha

### Ejemplo Completo con Explicación:

```python
# ==========================================
# PASO 1: INICIALIZACIÓN (En __init__)
# ==========================================

# Variables de control del scroll horizontal
self.scroll_offset_tabs = 0         # Índice de la primera pestaña visible
self.tabs_visibles_max = 3          # Cuántas pestañas caben en pantalla a la vez

# Lista de pestañas a mostrar
self.categorias = ["Consumibles", "Especiales", "Equipos", "Armas", "Armaduras", "Accesorios"]
# Ejemplo: 6 pestañas totales, pero solo 3 caben en pantalla

self.categoria_actual = 0           # Índice de la pestaña seleccionada

# ==========================================
# PASO 2: NAVEGACIÓN (En update())
# ==========================================

def update(self, teclas):
    tiempo_actual = pygame.time.get_ticks()
    
    if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
        
        # DERECHA: Mover cursor hacia la derecha
        if teclas[pygame.K_RIGHT]:
            num_tabs = len(self.categorias)
            self.categoria_actual = (self.categoria_actual + 1) % num_tabs
            
            # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (derecha)
            # Si el índice seleccionado >= primer_visible + máximo_visible
            # Significa que el cursor está fuera del área visible hacia la derecha
            if self.categoria_actual >= self.scroll_offset_tabs + self.tabs_visibles_max:
                # Mover el scroll hacia la derecha (aumentar el offset)
                self.scroll_offset_tabs = self.categoria_actual - self.tabs_visibles_max + 1
            
            self.tiempo_ultimo_input = tiempo_actual
        
        # IZQUIERDA: Mover cursor hacia la izquierda
        elif teclas[pygame.K_LEFT]:
            num_tabs = len(self.categorias)
            self.categoria_actual = (self.categoria_actual - 1) % num_tabs
            
            # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (izquierda)
            # Si el índice seleccionado < primer_visible
            # Significa que el cursor está fuera del área visible hacia la izquierda
            if self.categoria_actual < self.scroll_offset_tabs:
                # Mover el scroll hacia la izquierda (disminuir el offset)
                self.scroll_offset_tabs = self.categoria_actual
            
            self.tiempo_ultimo_input = tiempo_actual

# ==========================================
# PASO 3: DIBUJO DE PESTAÑAS (En draw())
# ==========================================

def draw(self, pantalla):
    # Geometría de las pestañas
    tab_width = 140     # Ancho de cada pestaña
    tab_height = 35     # Alto de cada pestaña
    tab_x_start = 100   # Posición X inicial
    tab_y = 50          # Posición Y
    
    # 🔑 CLAVE: Calcular cuántas pestañas caben en el espacio disponible
    area_disponible_width = 500  # Ancho disponible para pestañas
    tabs_que_caben = max(1, int(area_disponible_width / tab_width))
    self.tabs_visibles_max = tabs_que_caben
    
    # EJEMPLO: Si el área es 500px y cada pestaña mide 140px:
    # tabs_que_caben = int(500 / 140) = 3 pestañas completas
    
    # 🔑 CLAVE: Calcular qué pestañas son visibles
    total_tabs = len(self.categorias)
    tabs_fin = min(self.scroll_offset_tabs + self.tabs_visibles_max, total_tabs)
    tabs_visibles = self.categorias[self.scroll_offset_tabs:tabs_fin]
    
    # EJEMPLO:
    # Si tenemos 6 pestañas totales y caben 3:
    # scroll_offset_tabs = 2  (empezamos desde la pestaña 2)
    # tabs_visibles_max = 3   (mostramos 3 pestañas)
    # tabs_fin = min(2 + 3, 6) = 5
    # tabs_visibles = categorias[2:5]  -> Mostramos pestañas 2, 3, 4
    
    # 🔑 CLAVE: Dibujar solo las pestañas visibles (completas)
    for idx_visual, categoria in enumerate(tabs_visibles):
        # idx_visual: posición visual (0, 1, 2 si mostramos 3)
        # idx_real: posición real en la lista completa
        idx_real = self.scroll_offset_tabs + idx_visual
        
        # Posición X de esta pestaña
        tab_x_pos = tab_x_start + (idx_visual * tab_width)
        tab_rect = pygame.Rect(tab_x_pos, tab_y, tab_width, tab_height)
        
        # Color y borde según si está seleccionada
        if idx_real == self.categoria_actual:
            color_tab = self.COLOR_CAJA
            color_texto = self.COLOR_TEXTO_SEL
            borde_grosor = 3
        else:
            color_tab = (20, 20, 80)
            color_texto = self.COLOR_TEXTO
            borde_grosor = 1
        
        # Dibujar la pestaña
        pygame.draw.rect(pantalla, color_tab, tab_rect, border_radius=8)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, tab_rect, borde_grosor, border_radius=8)
        
        # Dibujar el texto
        tab_surf = self.fuente.render(categoria, True, color_texto)
        tab_text_rect = tab_surf.get_rect(center=tab_rect.center)
        pantalla.blit(tab_surf, tab_text_rect)
        
        # Cursor si está seleccionada
        if idx_real == self.categoria_actual:
            if self.cursor_img:
                cursor_rect = self.cursor_img.get_rect(midleft=(tab_rect.left - 5, tab_rect.centery))
                pantalla.blit(self.cursor_img, cursor_rect)
    
    # ==========================================
    # PASO 4: DIBUJO DE SCROLLBAR HORIZONTAL
    # ==========================================
    
    # 🔑 CLAVE: Solo dibujar scrollbar si hay más pestañas que las visibles
    if total_tabs > self.tabs_visibles_max:
        # Geometría del scrollbar
        scrollbar_ancho = area_disponible_width - 20  # Ancho del scrollbar (un poco menos que el área)
        scrollbar_x = tab_x_start + 10
        scrollbar_y = tab_y + tab_height + 5  # Debajo de las pestañas
        scrollbar_altura = 8  # Alto del scrollbar (delgado)
        
        # Barra de fondo (azul oscuro)
        pygame.draw.rect(pantalla, (50, 50, 100), 
                        (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura), 
                        border_radius=4)
        
        # 🔑 CLAVE: Calcular tamaño del thumb (proporcional)
        # Tamaño del thumb = (pestañas_visibles / pestañas_totales) * ancho_scrollbar
        thumb_ancho = max(30, int((self.tabs_visibles_max / total_tabs) * scrollbar_ancho))
        
        # EJEMPLO: Si tenemos 3 visibles de 6 totales:
        # thumb_ancho = (3 / 6) * 480 = 240 píxeles (50% de la barra)
        
        # 🔑 CLAVE: Calcular posición del thumb
        # Posición máxima = ancho_scrollbar - ancho_thumb
        thumb_pos_max = scrollbar_ancho - thumb_ancho
        
        # Ratio de scroll = offset_actual / máximo_offset_posible
        # thumb_x = posición_inicial + (ratio * posición_máxima)
        if total_tabs > self.tabs_visibles_max:
            scroll_ratio = self.scroll_offset_tabs / (total_tabs - self.tabs_visibles_max)
            thumb_x = scrollbar_x + int(scroll_ratio * thumb_pos_max)
        else:
            thumb_x = scrollbar_x
        
        # EJEMPLO: Si estamos en offset=2 con 6 pestañas y 3 visibles:
        # ratio = 2 / (6-3) = 2/3 = 0.666 (66.6%)
        # thumb_x = 110 + (0.666 * 240) = 270 (a 2/3 del recorrido)
        
        # Dibujar thumb (amarillo/azul claro)
        pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                        (thumb_x, scrollbar_y, thumb_ancho, scrollbar_altura), 
                        border_radius=4)
```

---

## 📊 COMPARACIÓN DE PATRONES

| Aspecto | Scroll Vertical ↕ | Scroll Horizontal ↔ |
|---------|------------------|---------------------|
| **Teclas** | UP/DOWN | LEFT/RIGHT |
| **Offset aumenta** | Hacia abajo (+1) | Hacia la derecha (+1) |
| **Offset disminuye** | Hacia arriba (-1) | Hacia la izquierda (-1) |
| **Scrollbar posición** | X fija, Y variable | Y fija, X variable |
| **Thumb tamaño** | Altura proporcional | Ancho proporcional |
| **Thumb posición** | `thumb_y = f(offset)` | `thumb_x = f(offset)` |
| **Casos de uso** | Listas, textos | Pestañas, galerías |

---

## 🎓 FÓRMULAS CLAVE (MEMORIZAR)

### Para calcular elementos visibles:
```python
elementos_fin = min(scroll_offset + elementos_visibles_max, total_elementos)
elementos_visibles = lista_completa[scroll_offset:elementos_fin]
```

### Para ajustar scroll al navegar hacia adelante (↓ o →):
```python
if indice_seleccionado >= scroll_offset + elementos_visibles_max:
    scroll_offset = indice_seleccionado - elementos_visibles_max + 1
```

### Para ajustar scroll al navegar hacia atrás (↑ o ←):
```python
if indice_seleccionado < scroll_offset:
    scroll_offset = indice_seleccionado
```

### Para calcular tamaño de thumb:
```python
# Vertical
thumb_altura = max(15, int((visibles / totales) * altura_scrollbar))

# Horizontal
thumb_ancho = max(30, int((visibles / totales) * ancho_scrollbar))
```

### Para calcular posición de thumb:
```python
# Vertical
scroll_ratio = scroll_offset / (total - visibles)
thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_altura - thumb_altura))

# Horizontal
scroll_ratio = scroll_offset / (total - visibles)
thumb_x = scrollbar_x + int(scroll_ratio * (scrollbar_ancho - thumb_ancho))
```

---

## 🎯 REGLAS DE ORO

1. **Siempre mostrar elementos COMPLETOS**: Nunca mostrar un elemento cortado a la mitad
2. **Calcular dinámicamente los visibles**: `max(1, int(area / tamaño_elemento))`
3. **Scrollbar solo si es necesario**: `if total > visibles_max`
4. **Thumb proporcional**: Refleja la proporción de elementos visibles vs totales
5. **Mínimo de thumb**: Siempre al menos 15-30 píxeles para ser clickeable
6. **Cooldown de input**: Prevenir navegación demasiado rápida (200ms recomendado)

---

## 💡 CASOS DE USO FUTUROS

### Para Diálogos de Personajes:
```python
# Lista de líneas de diálogo
self.lineas_dialogo = ["Hola aventurero...", "Bienvenido a...", ...]
self.scroll_offset_dialogo = 0
self.lineas_visibles_max = 5  # 5 líneas a la vez

# Usar patrón VERTICAL
# Navegación: UP/DOWN
# Scrollbar: Vertical a la derecha
```

### Para Logs de Batalla:
```python
# Lista de eventos
self.log_batalla = ["Héroe atacó!", "Enemigo defendió", ...]
self.scroll_offset_log = 0
self.eventos_visibles_max = 8

# Usar patrón VERTICAL
# Auto-scroll al final cuando llegue un evento nuevo
self.scroll_offset_log = max(0, len(self.log_batalla) - self.eventos_visibles_max)
```

### Para Barra de Habilidades:
```python
# Lista de habilidades
self.habilidades = ["Fireball", "Ice Storm", "Thunder", ...]
self.scroll_offset_habilidades = 0
self.habilidades_visibles_max = 6

# Usar patrón HORIZONTAL
# Navegación: LEFT/RIGHT
# Scrollbar: Horizontal debajo
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

Cuando implementes un nuevo scroll, verifica:

- [ ] Variables inicializadas (`scroll_offset`, `visibles_max`)
- [ ] Lógica de navegación (UP/DOWN o LEFT/RIGHT)
- [ ] Ajuste de scroll al navegar
- [ ] Cálculo de elementos visibles
- [ ] Dibujo solo de elementos visibles
- [ ] Scrollbar con geometría correcta
- [ ] Thumb con tamaño proporcional
- [ ] Thumb con posición calculada
- [ ] Cursor solo en elemento seleccionado
- [ ] Scrollbar solo si es necesario
- [ ] Cooldown de input

---

## 🔧 VARIABLES ESTÁNDAR A USAR

```python
# Para cualquier scroll vertical
self.scroll_offset_[nombre] = 0
self.[nombre]_visibles_max = N
self.[nombre]_seleccionado_idx = 0

# Para cualquier scroll horizontal
self.scroll_offset_[nombre] = 0
self.[nombre]_visibles_max = N
self.[nombre]_actual = 0

# Colores estándar
self.COLOR_SCROLLBAR = (100, 100, 255)  # Azul claro/amarillo
self.COLOR_SCROLLBAR_FONDO = (50, 50, 100)  # Azul oscuro
```

---

## ✅ ARCHIVO DE REFERENCIA

**Este documento es la referencia definitiva para scrolls en el proyecto.**

Cada vez que se necesite implementar scroll:
1. Leer este archivo
2. Copiar el patrón correspondiente (vertical u horizontal)
3. Adaptar nombres de variables
4. Seguir el checklist

**No inventar nuevos patrones. Usar estos.**

---

*Documento creado: 2025-11-15*
*Archivo: GUIA_SISTEMA_SCROLL_COMPLETO.md*
*Ubicación: c:\Users\vicko\Documents\RPG\*
