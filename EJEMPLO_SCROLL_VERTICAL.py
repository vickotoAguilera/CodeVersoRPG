# ====================================================================
# EJEMPLO PRÁCTICO: SCROLL VERTICAL (Lista de Items)
# ====================================================================
# Este es un ejemplo simplificado y comentado línea por línea
# de cómo implementar un scroll vertical funcional
# ====================================================================

import pygame

class EjemploScrollVertical:
    """
    Ejemplo de una lista scrolleable vertical.
    Muestra 10 items a la vez de una lista de 20.
    """
    
    def __init__(self, pantalla_ancho, pantalla_alto):
        # ============================================
        # INICIALIZACIÓN
        # ============================================
        
        # Lista completa de items (simulamos 20 items)
        self.items = [f"Item {i+1}" for i in range(20)]
        
        # 🔑 VARIABLE CLAVE 1: Offset del scroll
        # Indica cuál es el PRIMER item visible
        # Empieza en 0 (mostramos desde el primer item)
        self.scroll_offset = 0
        
        # 🔑 VARIABLE CLAVE 2: Máximo de items visibles
        # Cuántos items caben en pantalla a la vez
        self.items_visibles_max = 10
        
        # 🔑 VARIABLE CLAVE 3: Índice del item seleccionado
        # Cuál item tiene el cursor encima (0-19 en este ejemplo)
        self.item_seleccionado_idx = 0
        
        # Geometría de la lista
        self.lista_x = 100
        self.lista_y = 100
        self.lista_ancho = 400
        self.lista_altura = 350  # Altura total disponible
        self.line_height = 35    # Altura de cada línea
        
        # Fuente
        self.fuente = pygame.font.Font(None, 30)
        
        # Colores
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_SCROLLBAR_FONDO = (50, 50, 100)
        self.COLOR_SCROLLBAR = (100, 100, 255)
        
        # Cooldown
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200
    
    def update(self, teclas):
        """
        Maneja la navegación con UP/DOWN
        """
        # ============================================
        # NAVEGACIÓN CON AJUSTE DE SCROLL
        # ============================================
        
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # BAJAR: Flecha abajo
            if teclas[pygame.K_DOWN]:
                total_items = len(self.items)
                
                # Mover el cursor al siguiente item (con wrap)
                self.item_seleccionado_idx = (self.item_seleccionado_idx + 1) % total_items
                
                # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (hacia abajo)
                # Ejemplo: Si estamos viendo items [5-14] y movemos al item 15
                # item_seleccionado_idx = 15
                # scroll_offset = 5
                # items_visibles_max = 10
                # 15 >= 5 + 10 → TRUE → Ajustar scroll
                if self.item_seleccionado_idx >= self.scroll_offset + self.items_visibles_max:
                    # Nuevo offset: El item seleccionado debe quedar al final del área visible
                    # offset = 15 - 10 + 1 = 6
                    # Ahora mostramos items [6-15] y el cursor está en el 15 (último visible)
                    self.scroll_offset = self.item_seleccionado_idx - self.items_visibles_max + 1
                
                self.tiempo_ultimo_input = tiempo_actual
            
            # SUBIR: Flecha arriba
            elif teclas[pygame.K_UP]:
                total_items = len(self.items)
                
                # Mover el cursor al item anterior (con wrap)
                self.item_seleccionado_idx = (self.item_seleccionado_idx - 1) % total_items
                
                # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (hacia arriba)
                # Ejemplo: Si estamos viendo items [5-14] y movemos al item 4
                # item_seleccionado_idx = 4
                # scroll_offset = 5
                # 4 < 5 → TRUE → Ajustar scroll
                if self.item_seleccionado_idx < self.scroll_offset:
                    # Nuevo offset: El item seleccionado debe quedar al inicio del área visible
                    # offset = 4
                    # Ahora mostramos items [4-13] y el cursor está en el 4 (primero visible)
                    self.scroll_offset = self.item_seleccionado_idx
                
                self.tiempo_ultimo_input = tiempo_actual
    
    def draw(self, pantalla):
        """
        Dibuja la lista con scroll y scrollbar
        """
        # ============================================
        # PASO 1: CALCULAR QUÉ ITEMS SON VISIBLES
        # ============================================
        
        total_items = len(self.items)
        
        # 🔑 CLAVE: Calcular el índice final de items visibles
        # min() asegura que no nos pasemos del final de la lista
        # Ejemplo: Si scroll_offset=15 y items_visibles_max=10 pero total=20
        # items_fin = min(15 + 10, 20) = 20 (solo mostramos 5 items: [15-19])
        items_fin = min(self.scroll_offset + self.items_visibles_max, total_items)
        
        # 🔑 CLAVE: Extraer solo los items visibles de la lista completa
        # Esto es un "slice" de Python: lista[inicio:fin]
        # Ejemplo: items[5:15] devuelve elementos desde índice 5 hasta 14 (10 elementos)
        items_visibles = self.items[self.scroll_offset:items_fin]
        
        # ============================================
        # PASO 2: DIBUJAR SOLO LOS ITEMS VISIBLES
        # ============================================
        
        # Iterar solo por los items visibles
        for idx_visual, item_texto in enumerate(items_visibles):
            # idx_visual: 0, 1, 2, ... (posición en la ventana visible)
            # idx_real: posición real en la lista completa
            # Ejemplo: Si scroll_offset=5 e idx_visual=2, entonces idx_real=7
            idx_real = self.scroll_offset + idx_visual
            
            # Calcular posición Y de este item
            pos_y = self.lista_y + (idx_visual * self.line_height)
            
            # Determinar color (amarillo si está seleccionado, blanco si no)
            color = self.COLOR_TEXTO_SEL if idx_real == self.item_seleccionado_idx else self.COLOR_TEXTO
            
            # Dibujar cursor si está seleccionado
            if idx_real == self.item_seleccionado_idx:
                cursor_surf = self.fuente.render(">", True, self.COLOR_TEXTO_SEL)
                pantalla.blit(cursor_surf, (self.lista_x - 25, pos_y))
            
            # Dibujar el texto del item
            item_surf = self.fuente.render(item_texto, True, color)
            pantalla.blit(item_surf, (self.lista_x, pos_y))
        
        # ============================================
        # PASO 3: DIBUJAR SCROLLBAR (SOLO SI ES NECESARIO)
        # ============================================
        
        # 🔑 CLAVE: Solo dibujar scrollbar si hay más items que los visibles
        if total_items > self.items_visibles_max:
            
            # Geometría del scrollbar
            scrollbar_x = self.lista_x + self.lista_ancho + 10  # A la derecha de la lista
            scrollbar_y = self.lista_y
            scrollbar_ancho = 6
            scrollbar_altura = self.lista_altura
            
            # 1. Dibujar barra de fondo (azul oscuro)
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR_FONDO,
                           (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura),
                           border_radius=3)
            
            # ============================================
            # PASO 4: CALCULAR TAMAÑO DEL THUMB
            # ============================================
            
            # 🔑 CLAVE: El thumb debe ser proporcional
            # Fórmula: (items_visibles / items_totales) * altura_scrollbar
            # Ejemplo: (10 / 20) * 350 = 175 píxeles
            # Esto significa que el thumb ocupa 50% de la barra (porque vemos 50% de los items)
            thumb_altura = max(15, int((self.items_visibles_max / total_items) * scrollbar_altura))
            
            # max(15, ...) asegura que el thumb tenga al menos 15px de alto
            # (si hay MUCHOS items, el thumb podría ser demasiado pequeño)
            
            # ============================================
            # PASO 5: CALCULAR POSICIÓN DEL THUMB
            # ============================================
            
            # Espacio disponible para mover el thumb
            thumb_pos_max = scrollbar_altura - thumb_altura
            
            # 🔑 CLAVE: Calcular la posición del thumb basado en el scroll actual
            # Fórmula: scroll_offset / máximo_scroll_posible
            # máximo_scroll_posible = total_items - items_visibles_max
            # Ejemplo: Si scroll_offset=5, total=20, visibles=10
            # ratio = 5 / (20-10) = 5/10 = 0.5 (50%)
            # thumb_y = scrollbar_y + (0.5 * thumb_pos_max)
            # El thumb está en la mitad de su recorrido
            scroll_ratio = self.scroll_offset / (total_items - self.items_visibles_max)
            thumb_y = scrollbar_y + int(scroll_ratio * thumb_pos_max)
            
            # 2. Dibujar thumb (azul claro/amarillo)
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                           (scrollbar_x, thumb_y, scrollbar_ancho, thumb_altura),
                           border_radius=3)


# ====================================================================
# EXPLICACIÓN VISUAL DEL FUNCIONAMIENTO
# ====================================================================

"""
ESTADO INICIAL (scroll_offset = 0):
┌─────────────────┐
│ > Item 1        │ ← Cursor aquí (item_seleccionado_idx = 0)
│   Item 2        │
│   Item 3        │
│   Item 4        │
│   Item 5        │
│   Item 6        │
│   Item 7        │
│   Item 8        │
│   Item 9        │
│   Item 10       │ ← Último visible
├─────────────────┤
│   (Item 11)     │ ← No visible (scroll_offset + visibles_max)
│   (Item 12)     │
│   ...           │
│   (Item 20)     │
└─────────────────┘

SCROLLBAR:
┌──┐
│██│ ← Thumb arriba (50% de altura porque vemos 10 de 20)
│██│
│  │
│  │
└──┘


DESPUÉS DE PRESIONAR DOWN 10 VECES (scroll_offset = 1):
┌─────────────────┐
│   (Item 1)      │ ← No visible (está antes del scroll_offset)
├─────────────────┤
│   Item 2        │ ← Ahora es el primero visible
│   Item 3        │
│   Item 4        │
│   Item 5        │
│   Item 6        │
│   Item 7        │
│   Item 8        │
│   Item 9        │
│   Item 10       │
│ > Item 11       │ ← Cursor aquí (item_seleccionado_idx = 10)
├─────────────────┤
│   (Item 12)     │
│   ...           │
└─────────────────┘

SCROLLBAR:
┌──┐
│  │
│██│ ← Thumb se movió un poco hacia abajo
│██│
│  │
└──┘


AL FINAL (scroll_offset = 10):
┌─────────────────┐
│   (Items 1-10)  │ ← No visibles
├─────────────────┤
│   Item 11       │ ← Primero visible
│   Item 12       │
│   Item 13       │
│   Item 14       │
│   Item 15       │
│   Item 16       │
│   Item 17       │
│   Item 18       │
│   Item 19       │
│ > Item 20       │ ← Cursor en el último (item_seleccionado_idx = 19)
└─────────────────┘

SCROLLBAR:
┌──┐
│  │
│  │
│██│ ← Thumb abajo (vemos los últimos 10 items)
│██│
└──┘
"""
