import pygame
import sys

# --- (¡NUEVO ARCHIVO - DISEÑO BLUE DRAGON!) ---
# Esta es la pantalla de "Items" (Inventario) del menú de pausa.
# Muestra la lista de héroes a la izquierda y el inventario a la derecha.

class PantallaInventario:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, grupo_heroes, items_db_completa, cursor_img):
        print("¡Abriendo Pantalla de Inventario (Diseño Blue Dragon)!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.grupo_heroes = grupo_heroes
        self.items_db = items_db_completa
        self.cursor_img = cursor_img
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 35) # "Inventario"
            self.fuente_opcion = pygame.font.Font(None, 30) # "Poción", "Cloud"
            self.fuente_datos = pygame.font.Font(None, 28) # "HP:", "MP:"
            self.fuente_desc = pygame.font.Font(None, 26) # "Restaura HP..."
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Control y Estados ---
        self.modo = "seleccion_categoria" # "seleccion_categoria", "seleccion_item" o "seleccion_heroe"
        
        # Categorías de items
        self.categorias = ["Consumibles", "Especiales", "Equipos"]
        self.categoria_actual = 0  # Índice de la categoría seleccionada
        
        self.heroe_seleccionado_idx = 0
        self.item_seleccionado_idx = 0
        
        self.item_seleccionado_data = None # Guardará la poción, etc.
        
        self.lista_items_mostrados = []
        self._construir_lista_inventario() # Llenar la lista

        # --- Sistema de Scroll para Items ---
        self.scroll_offset_items = 0
        self.items_visibles_max = 10
        
        # --- Sistema de Scroll para Héroes ---
        self.scroll_offset_heroes = 0
        self.heroes_visibles_max = 6
        
        # --- Sistema de Scroll para Pestañas/Categorías ---
        self.scroll_offset_tabs = 0
        self.tabs_visibles_max = 3  # Máximo de pestañas completas visibles

        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Colores y Geometría ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_CANTIDAD = (200, 200, 200)
        self.COLOR_SCROLLBAR = (100, 100, 255)
        self.UI_BORDER_RADIUS = 12
        
        padding = 50
        self.caja_principal_rect = pygame.Rect(padding, padding, self.ANCHO - (padding * 2), self.ALTO - (padding * 2))
        
        # 1. Panel de Héroes (Izquierda)
        self.panel_heroes_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + 70,
            300,
            self.caja_principal_rect.height - 90
        )
        
        # 2. Panel de Ítems (Derecha) - Movido hacia abajo para las pestañas
        self.panel_items_rect = pygame.Rect(
            self.panel_heroes_rect.right + 20,
            self.panel_heroes_rect.y + 40,  # +40 píxeles para dar espacio a las pestañas
            self.caja_principal_rect.width - self.panel_heroes_rect.width - 60,
            self.panel_heroes_rect.height - 40  # Reducir altura para mantener dentro de la caja
        )
        
        # 3. Caja de Descripción (Arriba)
        self.caja_desc_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + 20,
            self.caja_principal_rect.width - 40,
            50
        )

    # --- 2. Lógica Interna ---
    def _construir_lista_inventario(self):
        """Construye la lista de ítems según la categoría actual."""
        self.lista_items_mostrados = []
        inventario_lider = self.grupo_heroes[0].inventario
        inventario_especiales = self.grupo_heroes[0].inventario_especiales
        
        categoria_nombre = self.categorias[self.categoria_actual]
        
        if categoria_nombre == "Consumibles":
            # Mostrar solo consumibles del inventario normal
            for id_item, cantidad in inventario_lider.items():
                if cantidad > 0:
                    item_data = self.items_db.get(id_item)
                    if item_data and item_data["tipo"] == "Consumible":
                        self.lista_items_mostrados.append(item_data)
        
        elif categoria_nombre == "Especiales":
            # Mostrar items especiales de AMBOS inventarios (normal y especial)
            # Primero del inventario normal
            for id_item, cantidad in inventario_lider.items():
                if cantidad > 0:
                    item_data = self.items_db.get(id_item)
                    if item_data and item_data["tipo"] == "Especial":
                        self.lista_items_mostrados.append(item_data)
            
            # Luego del inventario especial
            for id_item, cantidad in inventario_especiales.items():
                if cantidad > 0:
                    item_data = self.items_db.get(id_item)
                    if item_data and item_data["tipo"] == "Especial":
                        # Verificar que no se haya agregado ya del inventario normal
                        if item_data not in self.lista_items_mostrados:
                            self.lista_items_mostrados.append(item_data)
        
        elif categoria_nombre == "Equipos":
            # Mostrar items equipables del inventario normal
            # Los equipos están en el inventario normal del héroe pero hay que buscarlos en equipo_db
            equipo_db = self.grupo_heroes[0].equipo_db  # Acceder a la base de datos de equipos
            for id_item, cantidad in inventario_lider.items():
                if cantidad > 0:
                    # Buscar en equipo_db en lugar de items_db
                    item_data = equipo_db.get(id_item)
                    if item_data:  # Si existe en equipo_db, es un equipo
                        self.lista_items_mostrados.append(item_data)
        
        # Resetear índice y scroll cuando cambia la categoría
        if self.item_seleccionado_idx >= len(self.lista_items_mostrados) and len(self.lista_items_mostrados) > 0:
            self.item_seleccionado_idx = 0
            self.scroll_offset_items = 0
        
        print(f"Inventario ({categoria_nombre}): {len(self.lista_items_mostrados)} items.")

    # --- 3. EL UPDATE (CON SCROLL) ---
    def update(self, teclas):
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # [MODO 0: Seleccionando Categoría/Pestaña (Arriba)]
            if self.modo == "seleccion_categoria":
                if teclas[pygame.K_LEFT]:
                    # Cambiar categoría hacia la izquierda
                    self.categoria_actual = (self.categoria_actual - 1) % len(self.categorias)
                    self._construir_lista_inventario()
                    
                    # Ajustar scroll de pestañas si es necesario
                    if self.categoria_actual < self.scroll_offset_tabs:
                        self.scroll_offset_tabs = self.categoria_actual
                    
                    self.tiempo_ultimo_input = tiempo_actual
                    
                elif teclas[pygame.K_RIGHT]:
                    # Cambiar categoría hacia la derecha
                    self.categoria_actual = (self.categoria_actual + 1) % len(self.categorias)
                    self._construir_lista_inventario()
                    
                    # Ajustar scroll de pestañas si es necesario
                    if self.categoria_actual >= self.scroll_offset_tabs + self.tabs_visibles_max:
                        self.scroll_offset_tabs = self.categoria_actual - self.tabs_visibles_max + 1
                    
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif teclas[pygame.K_DOWN]:
                    # Bajar a seleccionar items
                    self.modo = "seleccion_item"
                    self.item_seleccionado_idx = 0
                    self.scroll_offset_items = 0
                    self.tiempo_ultimo_input = tiempo_actual
            
            # [MODO 1: Seleccionando Ítem (Derecha)]
            elif self.modo == "seleccion_item":
                if teclas[pygame.K_DOWN]:
                    if self.lista_items_mostrados:
                        num_items = len(self.lista_items_mostrados)
                        self.item_seleccionado_idx = (self.item_seleccionado_idx + 1) % num_items
                        
                        # Ajustar scroll
                        if self.item_seleccionado_idx >= self.scroll_offset_items + self.items_visibles_max:
                            self.scroll_offset_items = self.item_seleccionado_idx - self.items_visibles_max + 1
                    
                    self.tiempo_ultimo_input = tiempo_actual
                    
                elif teclas[pygame.K_UP]:
                    if self.lista_items_mostrados:
                        # Si estamos en el primer item, volver a selección de categoría
                        if self.item_seleccionado_idx == 0:
                            self.modo = "seleccion_categoria"
                            self.tiempo_ultimo_input = tiempo_actual
                        else:
                            num_items = len(self.lista_items_mostrados)
                            self.item_seleccionado_idx = (self.item_seleccionado_idx - 1) % num_items
                            
                            # Ajustar scroll
                            if self.item_seleccionado_idx < self.scroll_offset_items:
                                self.scroll_offset_items = self.item_seleccionado_idx
                            
                            self.tiempo_ultimo_input = tiempo_actual
                    else:
                        # Si no hay items, volver a selección de categoría
                        self.modo = "seleccion_categoria"
                        self.tiempo_ultimo_input = tiempo_actual

            # [MODO 2: Seleccionando Héroe (Izquierda)]
            elif self.modo == "seleccion_heroe":
                num_heroes = len(self.grupo_heroes)
                
                if teclas[pygame.K_DOWN]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx + 1) % num_heroes
                    
                    # Ajustar scroll
                    if self.heroe_seleccionado_idx >= self.scroll_offset_heroes + self.heroes_visibles_max:
                        self.scroll_offset_heroes = self.heroe_seleccionado_idx - self.heroes_visibles_max + 1
                    
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx - 1) % num_heroes
                    
                    # Ajustar scroll
                    if self.heroe_seleccionado_idx < self.scroll_offset_heroes:
                        self.scroll_offset_heroes = self.heroe_seleccionado_idx
                    
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_RIGHT]:
                    self.modo = "seleccion_item"
                    self.item_seleccionado_idx = 0
                    self.scroll_offset_items = 0
                    self.tiempo_ultimo_input = tiempo_actual
        
        return None

    # --- 4. EL UPDATE_INPUT ---
    def update_input(self, tecla):
        
        if tecla == pygame.K_ESCAPE:
            if self.modo == "seleccion_heroe":
                self.modo = "seleccion_item" # Volver al panel de ítems
                self.item_seleccionado_data = None
                return None
            elif self.modo == "seleccion_item":
                # Volver a selección de categorías
                self.modo = "seleccion_categoria"
                return None
            elif self.modo == "seleccion_categoria":
                print("¡Cerrando Pantalla de Inventario!")
                return "volver_al_menu"
        
        # Cambiar categoría con TAB (solo en modo selección de categoría)
        if tecla == pygame.K_TAB:
            if self.modo == "seleccion_categoria":
                self.categoria_actual = (self.categoria_actual + 1) % len(self.categorias)
                self._construir_lista_inventario()
                
                # Ajustar scroll de pestañas
                if self.categoria_actual >= self.scroll_offset_tabs + self.tabs_visibles_max:
                    self.scroll_offset_tabs = self.categoria_actual - self.tabs_visibles_max + 1
                elif self.categoria_actual < self.scroll_offset_tabs:
                    self.scroll_offset_tabs = self.categoria_actual
                
                return None
        
        if tecla == pygame.K_RETURN:
            # [MODO 1: Seleccionando Ítem (Derecha)]
            if self.modo == "seleccion_item":
                if self.lista_items_mostrados:
                    item_data = self.lista_items_mostrados[self.item_seleccionado_idx]
                    categoria_actual_nombre = self.categorias[self.categoria_actual]
                    
                    # Si estamos en la categoría "Equipos", no hacer nada (solo visualización)
                    if categoria_actual_nombre == "Equipos":
                        print(f"Los equipos se gestionan desde el menú de Equipo.")
                        return None
                    
                    # Si es un ítem que requiere seleccionar héroe
                    if item_data["target"] in ["Aliado", "Heroe"]:
                        self.item_seleccionado_data = item_data
                        self.modo = "seleccion_heroe" # Salta al panel de héroes
                        self.heroe_seleccionado_idx = 0
                        print(f"Seleccionado ítem: {item_data['nombre']}")
                    elif item_data["target"] == "Ninguno":
                        # Items especiales que no se usan (llaves, etc)
                        print(f"El item {item_data['nombre']} no se puede usar directamente.")
                return None
            
            # [MODO 2: Seleccionando Héroe (Izquierda)]
            elif self.modo == "seleccion_heroe":
                # Solo si venimos de seleccionar un ítem
                if self.item_seleccionado_data:
                    heroe_objetivo = self.grupo_heroes[self.heroe_seleccionado_idx]
                    item_data = self.item_seleccionado_data
                    
                    print(f"Usando {item_data['nombre']} en {heroe_objetivo.nombre_en_juego}...")
                    
                    # Aplicar efecto según tipo
                    if item_data['efecto'] == "RESTAURA_HP":
                        # Consumir del inventario normal
                        self.grupo_heroes[0].usar_item(item_data['id_item'])
                        heroe_objetivo.recibir_curacion(item_data['poder'])
                    elif item_data['efecto'] == "RESTAURA_MP":
                        # Consumir del inventario normal
                        self.grupo_heroes[0].usar_item(item_data['id_item'])
                        heroe_objetivo.recibir_curacion_mp(item_data['poder'])
                    elif item_data['efecto'] == "AUMENTA_RANURAS_HABILIDAD":
                        # Consumir desde el inventario correcto (puede estar en normal o especial)
                        id_item = item_data['id_item']
                        lider = self.grupo_heroes[0]
                        
                        # Intentar consumir del inventario normal primero
                        if lider.tiene_item(id_item):
                            lider.usar_item(id_item)
                        # Si no está en el normal, consumir del especial
                        elif lider.tiene_item_especial(id_item):
                            # Reducir cantidad en inventario especial
                            lider.inventario_especiales[id_item] -= 1
                            if lider.inventario_especiales[id_item] <= 0:
                                del lider.inventario_especiales[id_item]
                        
                        # Aplicar el efecto
                        heroe_objetivo.usar_expansor_ranuras(item_data['poder'])
                        print(f"¡{heroe_objetivo.nombre_en_juego} ahora tiene {heroe_objetivo.ranuras_habilidad_max} ranuras!")
                    
                    # Reconstruir inventario y volver
                    self._construir_lista_inventario()
                    self.modo = "seleccion_item" # Volver al panel de ítems
                    self.item_seleccionado_data = None
                return None
                
        return None

    # --- 5. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo"
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar las Cajas
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_principal_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_principal_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_heroes_rect, 1, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_items_rect, 1, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 1, border_radius=self.UI_BORDER_RADIUS)

        # 3. Dibujar Panel Izquierdo (Lista de Héroes - CON SCROLL)
        start_x_heroe = self.panel_heroes_rect.x + 20
        start_y_heroe = self.panel_heroes_rect.y + 20
        line_height_heroe = 60
        
        total_heroes = len(self.grupo_heroes)
        heroes_fin = min(self.scroll_offset_heroes + self.heroes_visibles_max, total_heroes)
        heroes_visibles = self.grupo_heroes[self.scroll_offset_heroes:heroes_fin]
        
        for idx_visual, heroe in enumerate(heroes_visibles):
            idx_real = self.scroll_offset_heroes + idx_visual
            
            heroe_texto = f"{heroe.nombre_en_juego}"
            stats_texto_hp = f"HP {heroe.HP_actual}/{heroe.HP_max}"
            stats_texto_mp = f"MP {heroe.MP_actual}/{heroe.MP_max}"
            
            color_heroe = self.COLOR_TEXTO
            
            if idx_real == self.heroe_seleccionado_idx and self.modo == "seleccion_heroe":
                color_heroe = self.COLOR_TEXTO_SEL
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(start_x_heroe - 5, start_y_heroe + (idx_visual * line_height_heroe) + 15))
                    pantalla.blit(self.cursor_img, cursor_rect)

            heroe_surf = self.fuente_opcion.render(heroe_texto, True, color_heroe)
            stats_hp_surf = self.fuente_datos.render(stats_texto_hp, True, color_heroe)
            stats_mp_surf = self.fuente_datos.render(stats_texto_mp, True, color_heroe)
            
            pantalla.blit(heroe_surf, (start_x_heroe, start_y_heroe + (idx_visual * line_height_heroe)))
            pantalla.blit(stats_hp_surf, (start_x_heroe + 100, start_y_heroe + (idx_visual * line_height_heroe)))
            pantalla.blit(stats_mp_surf, (start_x_heroe + 100, start_y_heroe + (idx_visual * line_height_heroe) + 20))
        
        # Scrollbar para héroes
        if total_heroes > self.heroes_visibles_max:
            scrollbar_altura = self.panel_heroes_rect.height - 20
            scrollbar_x = self.panel_heroes_rect.right - 10
            scrollbar_y = self.panel_heroes_rect.y + 10
            
            pygame.draw.rect(pantalla, (50, 50, 100), 
                           (scrollbar_x, scrollbar_y, 6, scrollbar_altura), border_radius=3)
            
            thumb_altura = max(15, int((self.heroes_visibles_max / total_heroes) * scrollbar_altura))
            thumb_pos_max = scrollbar_altura - thumb_altura
            thumb_y = scrollbar_y + int((self.scroll_offset_heroes / (total_heroes - self.heroes_visibles_max)) * thumb_pos_max)
            
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                           (scrollbar_x, thumb_y, 6, thumb_altura), border_radius=3)

        # 4. Dibujar Panel Derecho (Lista de Items - CON SCROLL)
        
        # 4.1 Dibujar pestañas de categorías arriba del panel (CON SCROLL HORIZONTAL)
        tab_width = 140
        tab_height = 35
        tab_x_start = self.panel_items_rect.x
        tab_y = self.panel_items_rect.y - tab_height - 5
        
        # Calcular cuántas pestañas completas caben
        total_tabs = len(self.categorias)
        tabs_area_width = self.panel_items_rect.width
        tabs_que_caben = max(1, int(tabs_area_width / tab_width))  # Al menos 1
        self.tabs_visibles_max = tabs_que_caben
        
        # Calcular pestañas visibles con scroll
        tabs_fin = min(self.scroll_offset_tabs + self.tabs_visibles_max, total_tabs)
        tabs_visibles = self.categorias[self.scroll_offset_tabs:tabs_fin]
        
        # Dibujar solo las pestañas visibles (completas)
        for idx_visual, categoria in enumerate(tabs_visibles):
            idx_real = self.scroll_offset_tabs + idx_visual
            tab_x_pos = tab_x_start + (idx_visual * tab_width)
            tab_rect = pygame.Rect(tab_x_pos, tab_y, tab_width, tab_height)
            
            # Color según si está seleccionada
            if idx_real == self.categoria_actual:
                color_tab = self.COLOR_CAJA
                color_texto_tab = self.COLOR_TEXTO_SEL
                borde_grosor = 3
            else:
                color_tab = (20, 20, 80)  # Más oscuro
                color_texto_tab = self.COLOR_TEXTO
                borde_grosor = 1
            
            pygame.draw.rect(pantalla, color_tab, tab_rect, border_radius=8)
            pygame.draw.rect(pantalla, self.COLOR_BORDE, tab_rect, borde_grosor, border_radius=8)
            
            # Texto de la categoría
            tab_surf = self.fuente_datos.render(categoria, True, color_texto_tab)
            tab_text_rect = tab_surf.get_rect(center=tab_rect.center)
            pantalla.blit(tab_surf, tab_text_rect)
            
            # Si estamos en modo selección de categoría, mostrar cursor
            if self.modo == "seleccion_categoria" and idx_real == self.categoria_actual:
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midleft=(tab_rect.left - 5, tab_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
        
        # Dibujar Scrollbar Horizontal (debajo de las pestañas) solo si hay más pestañas
        if total_tabs > self.tabs_visibles_max:
            # Barra de fondo horizontal
            scrollbar_ancho = tabs_area_width - 20
            scrollbar_x = tab_x_start + 10
            scrollbar_y = tab_y + tab_height + 3  # Justo debajo de las pestañas
            scrollbar_altura = 8
            
            pygame.draw.rect(pantalla, (50, 50, 100), 
                           (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura), border_radius=4)
            
            # Calcular posición y tamaño del thumb horizontal
            thumb_ancho = max(30, int((self.tabs_visibles_max / total_tabs) * scrollbar_ancho))
            thumb_pos_max = scrollbar_ancho - thumb_ancho
            
            # Calcular posición del thumb basado en el scroll actual
            if total_tabs > self.tabs_visibles_max:
                scroll_ratio = self.scroll_offset_tabs / (total_tabs - self.tabs_visibles_max)
                thumb_x = scrollbar_x + int(scroll_ratio * thumb_pos_max)
            else:
                thumb_x = scrollbar_x
            
            # Thumb horizontal (amarillo)
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                           (thumb_x, scrollbar_y, thumb_ancho, scrollbar_altura), border_radius=4)
        
        start_x_item = self.panel_items_rect.x + 20
        start_y_item = self.panel_items_rect.y + 20
        line_height_item = 35
        
        if not self.lista_items_mostrados:
            texto_surf = self.fuente_opcion.render("--- Vacío ---", True, self.COLOR_TEXTO)
            pantalla.blit(texto_surf, (start_x_item, start_y_item))
        else:
            total_items = len(self.lista_items_mostrados)
            items_fin = min(self.scroll_offset_items + self.items_visibles_max, total_items)
            items_visibles = self.lista_items_mostrados[self.scroll_offset_items:items_fin]
            
            for idx_visual, item_data in enumerate(items_visibles):
                idx_real = self.scroll_offset_items + idx_visual
                
                item_texto = item_data["nombre"]
                # Agregar indicador visual para items especiales
                categoria_actual_nombre = self.categorias[self.categoria_actual]
                if categoria_actual_nombre == "Especiales":
                    item_texto = f"★ {item_texto}"
                
                # Obtener cantidad desde el inventario correcto según el tipo
                id_item_actual = item_data.get('id_item', item_data.get('id_equipo', ''))
                if categoria_actual_nombre == "Especiales":
                    # Para items especiales, buscar en ambos inventarios y sumar
                    cantidad_normal = self.grupo_heroes[0].inventario.get(id_item_actual, 0)
                    cantidad_especial = self.grupo_heroes[0].inventario_especiales.get(id_item_actual, 0)
                    cantidad = cantidad_normal + cantidad_especial
                else:
                    # Para Consumibles y Equipos, usar inventario normal
                    cantidad = self.grupo_heroes[0].inventario.get(id_item_actual, 0)
                
                cantidad_texto = f"x{cantidad}"
                
                color_item = self.COLOR_TEXTO
                color_cant = self.COLOR_TEXTO_CANTIDAD
                
                if idx_real == self.item_seleccionado_idx and self.modo == "seleccion_item":
                    color_item = self.COLOR_TEXTO_SEL
                    color_cant = self.COLOR_TEXTO_SEL
                    if self.cursor_img:
                        cursor_rect = self.cursor_img.get_rect(midright=(start_x_item - 5, start_y_item + (idx_visual * line_height_item) + 10))
                        pantalla.blit(self.cursor_img, cursor_rect)

                item_surf = self.fuente_opcion.render(item_texto, True, color_item)
                cant_surf = self.fuente_opcion.render(cantidad_texto, True, color_cant)
                
                pantalla.blit(item_surf, (start_x_item, start_y_item + (idx_visual * line_height_item)))
                pantalla.blit(cant_surf, (self.panel_items_rect.right - cant_surf.get_width() - 30, start_y_item + (idx_visual * line_height_item)))
            
            # Scrollbar para items
            if total_items > self.items_visibles_max:
                scrollbar_altura = self.panel_items_rect.height - 20
                scrollbar_x = self.panel_items_rect.right - 10
                scrollbar_y = self.panel_items_rect.y + 10
                
                pygame.draw.rect(pantalla, (50, 50, 100), 
                               (scrollbar_x, scrollbar_y, 6, scrollbar_altura), border_radius=3)
                
                thumb_altura = max(15, int((self.items_visibles_max / total_items) * scrollbar_altura))
                thumb_pos_max = scrollbar_altura - thumb_altura
                thumb_y = scrollbar_y + int((self.scroll_offset_items / (total_items - self.items_visibles_max)) * thumb_pos_max)
                
                pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                               (scrollbar_x, thumb_y, 6, thumb_altura), border_radius=3)


        # 5. Dibujar Panel de Descripción (Arriba)
        if self.modo == "seleccion_categoria":
            desc_texto = "[←→] Navegar categorías | [↓] Entrar | [TAB] Siguiente categoría"
        elif self.modo == "seleccion_item" and self.lista_items_mostrados:
            item_actual = self.lista_items_mostrados[self.item_seleccionado_idx]
            desc_texto = item_actual.get("descripcion", "...")
            # Nota adicional para items especiales
            if item_actual.get("tipo") == "Especial":
                desc_texto += " (No se consume - permanece en inventario)"
        elif self.modo == "seleccion_heroe" and self.item_seleccionado_data:
            desc_texto = f"Usar {self.item_seleccionado_data['nombre']} en..."
        else:
            desc_texto = f"Categoría: {self.categorias[self.categoria_actual]}"
            
        desc_surf = self.fuente_desc.render(desc_texto, True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.centery))
        pantalla.blit(desc_surf, desc_rect)