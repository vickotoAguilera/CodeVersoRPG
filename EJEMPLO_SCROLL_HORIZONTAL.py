# ====================================================================
# EJEMPLO PRÁCTICO: SCROLL HORIZONTAL (Pestañas)
# ====================================================================
# Este es un ejemplo simplificado y comentado línea por línea
# de cómo implementar un scroll horizontal funcional
# ====================================================================

import pygame

class EjemploScrollHorizontal:
    """
    Ejemplo de pestañas scrolleables horizontalmente.
    Muestra 3 pestañas a la vez de una lista de 6.
    """
    
    def __init__(self, pantalla_ancho, pantalla_alto):
        # ============================================
        # INICIALIZACIÓN
        # ============================================
        
        # Lista completa de categorías/pestañas (simulamos 6)
        self.categorias = [
            "Consumibles",
            "Especiales", 
            "Equipos",
            "Armas",
            "Armaduras",
            "Accesorios"
        ]
        
        # 🔑 VARIABLE CLAVE 1: Offset del scroll
        # Indica cuál es la PRIMERA pestaña visible
        # Empieza en 0 (mostramos desde la primera pestaña)
        self.scroll_offset = 0
        
        # 🔑 VARIABLE CLAVE 2: Máximo de pestañas visibles
        # Cuántas pestañas caben en pantalla a la vez
        self.tabs_visibles_max = 3
        
        # 🔑 VARIABLE CLAVE 3: Índice de la pestaña seleccionada
        # Cuál pestaña tiene el cursor encima (0-5 en este ejemplo)
        self.categoria_actual = 0
        
        # Geometría de las pestañas
        self.tab_width = 140      # Ancho de cada pestaña
        self.tab_height = 35      # Alto de cada pestaña
        self.tabs_x = 100         # Posición X inicial
        self.tabs_y = 50          # Posición Y
        self.area_ancho = 450     # Ancho total disponible (caben 3 pestañas de 140px)
        
        # Fuente
        self.fuente = pygame.font.Font(None, 28)
        
        # Colores
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_CAJA_INACTIVA = (20, 20, 80)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_SCROLLBAR_FONDO = (50, 50, 100)
        self.COLOR_SCROLLBAR = (100, 100, 255)
        
        # Cooldown
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200
    
    def update(self, teclas):
        """
        Maneja la navegación con LEFT/RIGHT
        """
        # ============================================
        # NAVEGACIÓN CON AJUSTE DE SCROLL
        # ============================================
        
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # DERECHA: Flecha derecha
            if teclas[pygame.K_RIGHT]:
                total_tabs = len(self.categorias)
                
                # Mover el cursor a la siguiente pestaña (con wrap)
                self.categoria_actual = (self.categoria_actual + 1) % total_tabs
                
                # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (hacia la derecha)
                # Ejemplo: Si estamos viendo pestañas [2-4] y movemos a la pestaña 5
                # categoria_actual = 5
                # scroll_offset = 2
                # tabs_visibles_max = 3
                # 5 >= 2 + 3 → TRUE → Ajustar scroll
                if self.categoria_actual >= self.scroll_offset + self.tabs_visibles_max:
                    # Nuevo offset: La pestaña seleccionada debe quedar al final del área visible
                    # offset = 5 - 3 + 1 = 3
                    # Ahora mostramos pestañas [3-5] y el cursor está en la 5 (última visible)
                    self.scroll_offset = self.categoria_actual - self.tabs_visibles_max + 1
                
                self.tiempo_ultimo_input = tiempo_actual
            
            # IZQUIERDA: Flecha izquierda
            elif teclas[pygame.K_LEFT]:
                total_tabs = len(self.categorias)
                
                # Mover el cursor a la pestaña anterior (con wrap)
                self.categoria_actual = (self.categoria_actual - 1) % total_tabs
                
                # 🔑 CLAVE: Ajustar scroll si el cursor sale del área visible (hacia la izquierda)
                # Ejemplo: Si estamos viendo pestañas [2-4] y movemos a la pestaña 1
                # categoria_actual = 1
                # scroll_offset = 2
                # 1 < 2 → TRUE → Ajustar scroll
                if self.categoria_actual < self.scroll_offset:
                    # Nuevo offset: La pestaña seleccionada debe quedar al inicio del área visible
                    # offset = 1
                    # Ahora mostramos pestañas [1-3] y el cursor está en la 1 (primera visible)
                    self.scroll_offset = self.categoria_actual
                
                self.tiempo_ultimo_input = tiempo_actual
    
    def draw(self, pantalla):
        """
        Dibuja las pestañas con scroll y scrollbar
        """
        # ============================================
        # PASO 1: CALCULAR QUÉ PESTAÑAS SON VISIBLES
        # ============================================
        
        total_tabs = len(self.categorias)
        
        # 🔑 CLAVE: Calcular cuántas pestañas completas caben
        # Esto se puede calcular dinámicamente dividiendo el área disponible por el ancho de pestaña
        tabs_que_caben = max(1, int(self.area_ancho / self.tab_width))
        self.tabs_visibles_max = tabs_que_caben
        # En este ejemplo: int(450 / 140) = 3 pestañas completas
        
        # 🔑 CLAVE: Calcular el índice final de pestañas visibles
        # min() asegura que no nos pasemos del final de la lista
        # Ejemplo: Si scroll_offset=4 y tabs_visibles_max=3 pero total=6
        # tabs_fin = min(4 + 3, 6) = 6 (solo mostramos 2 pestañas: [4-5])
        tabs_fin = min(self.scroll_offset + self.tabs_visibles_max, total_tabs)
        
        # 🔑 CLAVE: Extraer solo las pestañas visibles de la lista completa
        # Esto es un "slice" de Python: lista[inicio:fin]
        # Ejemplo: categorias[2:5] devuelve elementos desde índice 2 hasta 4 (3 elementos)
        tabs_visibles = self.categorias[self.scroll_offset:tabs_fin]
        
        # ============================================
        # PASO 2: DIBUJAR SOLO LAS PESTAÑAS VISIBLES
        # ============================================
        
        # Iterar solo por las pestañas visibles
        for idx_visual, categoria_texto in enumerate(tabs_visibles):
            # idx_visual: 0, 1, 2 (posición en la ventana visible)
            # idx_real: posición real en la lista completa
            # Ejemplo: Si scroll_offset=2 e idx_visual=1, entonces idx_real=3
            idx_real = self.scroll_offset + idx_visual
            
            # Calcular posición X de esta pestaña
            # Cada pestaña se dibuja a la derecha de la anterior
            tab_x = self.tabs_x + (idx_visual * self.tab_width)
            tab_rect = pygame.Rect(tab_x, self.tabs_y, self.tab_width, self.tab_height)
            
            # Determinar colores según si está seleccionada
            if idx_real == self.categoria_actual:
                color_fondo = self.COLOR_CAJA
                color_texto = self.COLOR_TEXTO_SEL
                borde_grosor = 3
            else:
                color_fondo = self.COLOR_CAJA_INACTIVA
                color_texto = self.COLOR_TEXTO
                borde_grosor = 1
            
            # Dibujar fondo de la pestaña
            pygame.draw.rect(pantalla, color_fondo, tab_rect, border_radius=8)
            
            # Dibujar borde de la pestaña
            pygame.draw.rect(pantalla, self.COLOR_BORDE, tab_rect, borde_grosor, border_radius=8)
            
            # Dibujar el texto de la pestaña (centrado)
            texto_surf = self.fuente.render(categoria_texto, True, color_texto)
            texto_rect = texto_surf.get_rect(center=tab_rect.center)
            pantalla.blit(texto_surf, texto_rect)
            
            # Dibujar cursor si está seleccionada
            if idx_real == self.categoria_actual:
                cursor_surf = self.fuente.render(">", True, self.COLOR_TEXTO_SEL)
                cursor_rect = cursor_surf.get_rect(midleft=(tab_rect.left - 15, tab_rect.centery))
                pantalla.blit(cursor_surf, cursor_rect)
        
        # ============================================
        # PASO 3: DIBUJAR SCROLLBAR (SOLO SI ES NECESARIO)
        # ============================================
        
        # 🔑 CLAVE: Solo dibujar scrollbar si hay más pestañas que las visibles
        if total_tabs > self.tabs_visibles_max:
            
            # Geometría del scrollbar (debajo de las pestañas)
            scrollbar_x = self.tabs_x + 10
            scrollbar_y = self.tabs_y + self.tab_height + 5  # Debajo de las pestañas
            scrollbar_ancho = self.area_ancho - 20  # Un poco menos que el área
            scrollbar_altura = 8  # Delgado para horizontal
            
            # 1. Dibujar barra de fondo (azul oscuro)
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR_FONDO,
                           (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura),
                           border_radius=4)
            
            # ============================================
            # PASO 4: CALCULAR TAMAÑO DEL THUMB
            # ============================================
            
            # 🔑 CLAVE: El thumb debe ser proporcional
            # Fórmula: (tabs_visibles / tabs_totales) * ancho_scrollbar
            # Ejemplo: (3 / 6) * 430 = 215 píxeles
            # Esto significa que el thumb ocupa 50% de la barra (porque vemos 50% de las pestañas)
            thumb_ancho = max(30, int((self.tabs_visibles_max / total_tabs) * scrollbar_ancho))
            
            # max(30, ...) asegura que el thumb tenga al menos 30px de ancho
            # (si hay MUCHAS pestañas, el thumb podría ser demasiado pequeño)
            
            # ============================================
            # PASO 5: CALCULAR POSICIÓN DEL THUMB
            # ============================================
            
            # Espacio disponible para mover el thumb
            thumb_pos_max = scrollbar_ancho - thumb_ancho
            
            # 🔑 CLAVE: Calcular la posición del thumb basado en el scroll actual
            # Fórmula: scroll_offset / máximo_scroll_posible
            # máximo_scroll_posible = total_tabs - tabs_visibles_max
            # Ejemplo: Si scroll_offset=2, total=6, visibles=3
            # ratio = 2 / (6-3) = 2/3 = 0.666 (66.6%)
            # thumb_x = scrollbar_x + (0.666 * thumb_pos_max)
            # El thumb está a 2/3 de su recorrido
            if total_tabs > self.tabs_visibles_max:
                scroll_ratio = self.scroll_offset / (total_tabs - self.tabs_visibles_max)
                thumb_x = scrollbar_x + int(scroll_ratio * thumb_pos_max)
            else:
                thumb_x = scrollbar_x
            
            # 2. Dibujar thumb (azul claro/amarillo)
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                           (thumb_x, scrollbar_y, thumb_ancho, scrollbar_altura),
                           border_radius=4)


# ====================================================================
# EXPLICACIÓN VISUAL DEL FUNCIONAMIENTO
# ====================================================================

"""
ESTADO INICIAL (scroll_offset = 0):

Pestañas visibles:
┌─────────────┬─────────────┬─────────────┐
│>Consumibles │  Especiales │   Equipos   │ ← Solo estas 3 son visibles
└─────────────┴─────────────┴─────────────┘
 (Armas)       (Armaduras)   (Accesorios)   ← Ocultas (no se dibujan)

Cursor: En "Consumibles" (categoria_actual = 0)

SCROLLBAR:
┌──────────────────────────────────┐
│████████████                      │ ← Thumb a la izquierda (50% de ancho porque vemos 3 de 6)
└──────────────────────────────────┘


DESPUÉS DE PRESIONAR RIGHT 3 VECES (scroll_offset = 1):

Pestañas visibles:
 (Consumibles) ← Oculta (está antes del scroll_offset)
┌─────────────┬─────────────┬─────────────┐
│  Especiales │>  Equipos   │    Armas    │ ← Solo estas 3 son visibles
└─────────────┴─────────────┴─────────────┘
              (Armaduras)   (Accesorios)   ← Aún ocultas

Cursor: En "Equipos" (categoria_actual = 2)

SCROLLBAR:
┌──────────────────────────────────┐
│        ████████████              │ ← Thumb se movió a 1/3 del recorrido
└──────────────────────────────────┘


AL FINAL (scroll_offset = 3):

Pestañas ocultas:
 (Consumibles) (Especiales) (Equipos) ← Ocultas (están antes del scroll_offset)
┌─────────────┬─────────────┬─────────────┐
│    Armas    │  Armaduras  │>Accesorios  │ ← Solo estas 3 son visibles
└─────────────┴─────────────┴─────────────┘

Cursor: En "Accesorios" (categoria_actual = 5)

SCROLLBAR:
┌──────────────────────────────────┐
│                      ████████████│ ← Thumb a la derecha (vemos las últimas 3)
└──────────────────────────────────┘


VENTAJA: No se muestran pestañas "cortadas"
┌─────────────┬─────────────┬─────────────┐
│  Especiales │   Equipos   │    Armas    │ ← Todas COMPLETAS
└─────────────┴─────────────┴─────────────┘

NUNCA vemos esto (cortado):
┌─────────────┬─────────────┬─────────────┬────
│  Especiales │   Equipos   │    Armas    │ Arm ← ❌ MAL
└─────────────┴─────────────┴─────────────┴────
"""
