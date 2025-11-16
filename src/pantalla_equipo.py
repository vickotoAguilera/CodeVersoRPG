import pygame
import sys

# --- (¡NUEVO ARCHIVO!) ---
# Esta es la pantalla de "Equipamiento".
# Muestra las 11 ranuras de equipo del héroe y la lista de
# ítems equipables del inventario.

class PantallaEquipo:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, heroe_obj, equipo_db_completa, cursor_img):
        print(f"¡Abriendo Pantalla de Equipo para {heroe_obj.nombre_en_juego}!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.heroe = heroe_obj
        self.equipo_db = equipo_db_completa
        self.cursor_img = cursor_img
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 40)
            self.fuente_opcion = pygame.font.Font(None, 30)
            self.fuente_datos = pygame.font.Font(None, 28)
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Control y Estados ---
        self.modo = "seleccion_slot" # "seleccion_slot", "seleccion_item" o "ver_detalles"
        
        # Lista de las 11 ranuras (en el orden que las seleccionaremos)
        self.ranuras_equipo = [
            "mano_principal", "mano_secundaria",
            "cabeza", "pecho", "manos",
            "piernas", "pies", "espalda",
            "accesorio1", "accesorio2", "accesorio3"
        ]
        
        self.slot_seleccionado_idx = 0 # 0-10
        self.item_seleccionado_idx = 0 # Para la lista de inventario
        
        self.lista_items_equipables = [] # Lista de items del inventario

        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Colores y Geometría ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_CAJA_SLOT = (0, 0, 139)  # Mismo color que la caja central
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_EQUIPADO = (0, 255, 0) # Verde
        self.COLOR_TEXTO_DESHABILITADO = (100, 100, 100) # Gris
        self.UI_BORDER_RADIUS = 12
        
        # --- ¡GEOMETRÍA CORREGIDA! (Inventario al Centro) ---

        # 1. Caja de Estadísticas (Abajo)
        self.caja_stats_rect = pygame.Rect(30, 400, self.ANCHO - 60, self.ALTO - 400 - 30)
        
        # 2. Caja Central de Detalles (Centro - para mostrar info del item seleccionado)
        # Más compacta y separada de los slots
        self.caja_detalles_rect = pygame.Rect(0, 0, 320, 280)
        self.caja_detalles_rect.centerx = self.ANCHO // 2
        self.caja_detalles_rect.y = 80
        
        # 3. Caja de Inventario (Centro - aparece cuando seleccionas una ranura)
        # (Se moverá aquí cuando el modo sea "seleccion_item")
        self.caja_inventario_rect = pygame.Rect(0, 0, 250, 350)
        self.caja_inventario_rect.centerx = self.ANCHO // 2
        self.caja_inventario_rect.y = 30
        
        # 3. Cajas de Slots (Las 11 ranuras, Izquierda y Derecha)
        self.cajas_slots_dict = {} 
        
        caja_ancho = 180 # Cajas un poco más anchas
        caja_alto = 50
        
        # --- Columna Izquierda (Armadura) ---
        base_x_izq = 50
        base_y_izq = 50
        padding_y_izq = 60
        # (Añadimos "col" y "row" para la navegación)
        self.cajas_slots_dict["cabeza"] =    {"rect": pygame.Rect(base_x_izq, base_y_izq, caja_ancho, caja_alto), "col": 0, "row": 0}
        self.cajas_slots_dict["pecho"] =     {"rect": pygame.Rect(base_x_izq, base_y_izq + padding_y_izq, caja_ancho, caja_alto), "col": 0, "row": 1}
        self.cajas_slots_dict["manos"] =     {"rect": pygame.Rect(base_x_izq, base_y_izq + (padding_y_izq * 2), caja_ancho, caja_alto), "col": 0, "row": 2}
        self.cajas_slots_dict["piernas"] =   {"rect": pygame.Rect(base_x_izq, base_y_izq + (padding_y_izq * 3), caja_ancho, caja_alto), "col": 0, "row": 3}
        self.cajas_slots_dict["pies"] =      {"rect": pygame.Rect(base_x_izq, base_y_izq + (padding_y_izq * 4), caja_ancho, caja_alto), "col": 0, "row": 4}
        
        # --- Columna Derecha (Arma y Accesorios) ---
        base_x_der = self.ANCHO - caja_ancho - 50
        base_y_der = 50
        padding_y_der = 60
        self.cajas_slots_dict["mano_principal"] =  {"rect": pygame.Rect(base_x_der, base_y_der, caja_ancho, caja_alto), "col": 1, "row": 0}
        self.cajas_slots_dict["mano_secundaria"] = {"rect": pygame.Rect(base_x_der, base_y_der + padding_y_der, caja_ancho, caja_alto), "col": 1, "row": 1}
        self.cajas_slots_dict["espalda"] =         {"rect": pygame.Rect(base_x_der, base_y_der + (padding_y_der * 2), caja_ancho, caja_alto), "col": 1, "row": 2}
        self.cajas_slots_dict["accesorio1"] =      {"rect": pygame.Rect(base_x_der, base_y_der + (padding_y_der * 3), caja_ancho, caja_alto), "col": 1, "row": 3}
        self.cajas_slots_dict["accesorio2"] =      {"rect": pygame.Rect(base_x_der, base_y_der + (padding_y_der * 4), caja_ancho, caja_alto), "col": 1, "row": 4}
        self.cajas_slots_dict["accesorio3"] =      {"rect": pygame.Rect(base_x_der, base_y_der + (padding_y_der * 5), caja_ancho, caja_alto), "col": 1, "row": 5}
        # (Accesorio 3 queda fuera por ahora para mantener 2 columnas limpias)
        # (self.cajas_slots_dict["accesorio3"] = ...)
        
        # Actualizamos la lista de ranuras (ahora 10 ranuras)
        self.ranuras_equipo = [
            "cabeza", "pecho", "manos", "piernas", "pies", 
            "mano_principal", "mano_secundaria", "espalda", "accesorio1", "accesorio2",
            "accesorio3"
        ]
        
        # Variables de navegación por grilla
        self.col_actual = 0
        self.row_actual = 0
        self.max_rows_col_0 = 5 # 5 ítems en la columna 0
        self.max_rows_col_1 = 6 # 6 ítems en la columna 1
        
        # --- Variables de Scroll para Inventario ---
        self.scroll_inventario = 0
        self.max_items_visibles_inventario = 7

    # --- 2. EL UPDATE (¡MODIFICADO PARA GRILLA!) ---
    def update(self, teclas):
        
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # [MODO 1: Seleccionando la Ranura (Grilla de Slots)]
            if self.modo == "seleccion_slot":
                
                # Mover Arriba/Abajo
                if teclas[pygame.K_DOWN]:
                    self.tiempo_ultimo_input = tiempo_actual
                    if self.col_actual == 0: # Columna Izquierda
                        self.row_actual = (self.row_actual + 1) % self.max_rows_col_0
                    else: # Columna Derecha
                        self.row_actual = (self.row_actual + 1) % self.max_rows_col_1
                        
                elif teclas[pygame.K_UP]:
                    self.tiempo_ultimo_input = tiempo_actual
                    if self.col_actual == 0: # Columna Izquierda
                        self.row_actual = (self.row_actual - 1) % self.max_rows_col_0
                    else: # Columna Derecha
                        self.row_actual = (self.row_actual - 1) % self.max_rows_col_1
                
                # Mover Izquierda/Derecha
                elif teclas[pygame.K_RIGHT]:
                    self.tiempo_ultimo_input = tiempo_actual
                    self.col_actual = 1 # Mover a la columna derecha
                    # Ajustar la fila si la columna es más corta
                    self.row_actual = min(self.row_actual, self.max_rows_col_1 - 1)
                    
                elif teclas[pygame.K_LEFT]:
                    self.tiempo_ultimo_input = tiempo_actual
                    self.col_actual = 0 # Mover a la columna izquierda
                    # Ajustar la fila si la columna es más corta
                    self.row_actual = min(self.row_actual, self.max_rows_col_0 - 1)

            # [MODO 2: Seleccionando el Ítem (Centro)]
            elif self.modo == "seleccion_item":
                if not self.lista_items_equipables:
                    pass
                else:
                    num_items = len(self.lista_items_equipables)
                    if teclas[pygame.K_DOWN]:
                        self.item_seleccionado_idx = (self.item_seleccionado_idx + 1) % num_items
                        self.tiempo_ultimo_input = tiempo_actual
                        
                        # Ajustar scroll
                        if self.item_seleccionado_idx >= self.scroll_inventario + self.max_items_visibles_inventario:
                            self.scroll_inventario = self.item_seleccionado_idx - self.max_items_visibles_inventario + 1
                        elif self.item_seleccionado_idx < self.scroll_inventario:
                            self.scroll_inventario = self.item_seleccionado_idx
                            
                    elif teclas[pygame.K_UP]:
                        self.item_seleccionado_idx = (self.item_seleccionado_idx - 1) % num_items
                        self.tiempo_ultimo_input = tiempo_actual
                        
                        # Ajustar scroll
                        if self.item_seleccionado_idx >= self.scroll_inventario + self.max_items_visibles_inventario:
                            self.scroll_inventario = self.item_seleccionado_idx - self.max_items_visibles_inventario + 1
                        elif self.item_seleccionado_idx < self.scroll_inventario:
                            self.scroll_inventario = self.item_seleccionado_idx
        
        return None

    # --- 3. EL UPDATE_INPUT (¡CORREGIDO!) ---
    def update_input(self, tecla):
        
        # [ESCAPE: Salir o Volver]
        if tecla == pygame.K_ESCAPE:
            if self.modo == "ver_detalles":
                print("Cerrando pop-up de Detalles...")
                self.modo = "seleccion_item"
                return None
            elif self.modo == "seleccion_item":
                self.modo = "seleccion_slot"
                print("Volviendo a selección de slot.")
                return None
            elif self.modo == "seleccion_slot":
                print("¡Cerrando Pantalla de Equipo!")
                return "volver_al_menu"
        
        # [ENTER: Seleccionar]
        if tecla == pygame.K_RETURN:
            
            # --- ¡LÓGICA ANIDADA CORRECTAMENTE! ---
            if self.modo == "seleccion_slot":
                # --- ¡NUEVA LÓGICA DE TRADUCCIÓN DE GRILLA! ---
                ranura_actual = ""
                idx_ranura_encontrada = 0
                
                for i, (nombre_slot, info_slot) in enumerate(self.cajas_slots_dict.items()):
                    if info_slot["col"] == self.col_actual and info_slot["row"] == self.row_actual:
                        ranura_actual = nombre_slot
                        idx_ranura_encontrada = i
                        break

                if not ranura_actual:
                    return None
                    
                self.slot_seleccionado_idx = idx_ranura_encontrada
                # --- FIN LÓGICA DE GRILLA ---

                print(f"Abriendo lista de inventario para: {ranura_actual}")
                self.modo = "seleccion_item"
                self.item_seleccionado_idx = 0
                self.lista_items_equipables = [] 
                
                self.lista_items_equipables.append({"id_equipo": "NINGUNO", "nombre": "Quitar Equipo"})

                for id_item, cantidad in self.heroe.inventario.items():
                    if cantidad > 0:
                        item_data = self.equipo_db.get(id_item)
                        if item_data:
                            ranuras_compatibles = item_data.get("ranuras_que_ocupa", [])
                            if ranura_actual in ranuras_compatibles:
                                self.lista_items_equipables.append(item_data)
                
                return None
            
            elif self.modo == "seleccion_item":
                if self.lista_items_equipables:
                    item_seleccionado = self.lista_items_equipables[self.item_seleccionado_idx]
                    id_item_nuevo = item_seleccionado.get("id_equipo")
                    
                    ranura_actual = self.ranuras_equipo[self.slot_seleccionado_idx]
                    
                    self.heroe.equipar_item_en_ranura(id_item_nuevo, ranura_actual)
                    
                    print("Volviendo a selección de slot.")
                    self.modo = "seleccion_slot"
                return None
            # --- FIN LÓGICA ANIDADA ---

        # [Tecla D: Ver Detalles]
        if tecla == pygame.K_d:
            if self.modo == "seleccion_item" and self.lista_items_equipables:
                print("Abriendo pop-up de Detalles...")
                self.modo = "ver_detalles"
                return None
            
            elif self.modo == "ver_detalles":
                print("Cerrando pop-up de Detalles...")
                self.modo = "seleccion_item"
                return None
                
        return None
    
    def _wrap_text(self, texto, fuente, max_ancho):
        """
        Divide un texto largo en múltiples líneas para que quepa 
        dentro de un ancho máximo.
        """
        palabras = texto.split(' ')
        lineas = []
        linea_actual = ""
        
        for palabra in palabras:
            # Prueba a añadir la palabra
            linea_prueba = f"{linea_actual} {palabra}".strip()
            
            # Medimos el ancho de la línea de prueba
            ancho_prueba = fuente.size(linea_prueba)[0]
            
            # Si la línea (con la nueva palabra) es demasiado ancha...
            if ancho_prueba > max_ancho:
                # ...guarda la línea anterior (sin la palabra nueva)
                lineas.append(linea_actual)
                # Y empieza una línea nueva con la palabra actual
                linea_actual = palabra
            else:
                # Si cabe, sigue construyendo la línea
                linea_actual = linea_prueba
        
        # Añadir la última línea que quedó
        lineas.append(linea_actual)
        
        return lineas

    # --- 4. EL DRAW (¡ORDEN CORREGIDO!) ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo"
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar Caja de Stats (siempre visible)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_stats_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_stats_rect, 3, border_radius=self.UI_BORDER_RADIUS)

        # 3. Dibujar las 11 Cajas de Slots (siempre visibles)
        for nombre_slot, info_slot in self.cajas_slots_dict.items():
            caja_rect = info_slot["rect"]
            
            # Dibujar fondo de la caja con el mismo color que la central
            pygame.draw.rect(pantalla, self.COLOR_CAJA_SLOT, caja_rect, border_radius=self.UI_BORDER_RADIUS)
            
            # Obtener item equipado
            id_item_equipado = self.heroe.equipo.get(nombre_slot)
            
            if id_item_equipado:
                # Si hay un ítem, muestra el nombre del ítem en verde
                item_data = self.equipo_db.get(id_item_equipado)
                item_texto = item_data["nombre"] if item_data else "???"
                item_color = self.COLOR_TEXTO_EQUIPADO
            else:
                # Si está vacío, muestra el nombre de la ranura en gris
                item_texto = f"{nombre_slot.replace('_', ' ').capitalize()}"
                item_color = self.COLOR_TEXTO_DESHABILITADO
            
            item_surf = self.fuente_datos.render(item_texto, True, item_color)
            item_rect = item_surf.get_rect(center=caja_rect.center)
            pantalla.blit(item_surf, item_rect)
            
            # Dibujar el borde (resaltado si está seleccionado)
            if info_slot["col"] == self.col_actual and info_slot["row"] == self.row_actual and self.modo == "seleccion_slot":
                pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, caja_rect, 3, border_radius=self.UI_BORDER_RADIUS)
                # Dibujar Cursor
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(caja_rect.left - 5, caja_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
            else:
                pygame.draw.rect(pantalla, self.COLOR_BORDE, caja_rect, 1, border_radius=self.UI_BORDER_RADIUS)

        # 4. Dibujar Caja Central de Detalles (en modo seleccion_slot)
        if self.modo == "seleccion_slot":
            pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_detalles_rect, border_radius=self.UI_BORDER_RADIUS)
            pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_detalles_rect, 3, border_radius=self.UI_BORDER_RADIUS)
            
            # Obtener la ranura actual seleccionada
            ranura_actual = ""
            for nombre_slot, info_slot in self.cajas_slots_dict.items():
                if info_slot["col"] == self.col_actual and info_slot["row"] == self.row_actual:
                    ranura_actual = nombre_slot
                    break
            
            if ranura_actual:
                id_item_equipado = self.heroe.equipo.get(ranura_actual)
                if id_item_equipado:
                    item_data = self.equipo_db.get(id_item_equipado)
                    if item_data:
                        # Posiciones dentro de la caja de detalles
                        start_x_det = self.caja_detalles_rect.x + 15
                        start_y_det = self.caja_detalles_rect.y + 15
                        
                        # Título del item (más pequeño)
                        titulo_surf = self.fuente_opcion.render(item_data["nombre"], True, self.COLOR_TEXTO_SEL)
                        pantalla.blit(titulo_surf, (start_x_det, start_y_det))
                        
                        # Descripción (con wrap)
                        desc = item_data.get("descripcion", "")
                        if desc:
                            max_ancho_desc = self.caja_detalles_rect.width - 30
                            lineas_desc = self._wrap_text(desc, self.fuente_datos, max_ancho_desc)
                            desc_y = start_y_det + 35
                            for linea in lineas_desc:
                                desc_surf = self.fuente_datos.render(linea, True, self.COLOR_TEXTO)
                                pantalla.blit(desc_surf, (start_x_det, desc_y))
                                desc_y += self.fuente_datos.get_height()
                        
                        # Stats del item (más compactos)
                        stats = item_data.get("stats", {})
                        stat_y = start_y_det + 100
                        for stat_nombre, valor in stats.items():
                            if valor != 0:
                                color_stat = self.COLOR_TEXTO_EQUIPADO if valor > 0 else (255, 0, 0)
                                stat_texto = f"{stat_nombre.capitalize()}: {valor:+}"
                                stat_surf = self.fuente_datos.render(stat_texto, True, color_stat)
                                pantalla.blit(stat_surf, (start_x_det, stat_y))
                                stat_y += 25
                else:
                    # Si no hay item equipado, mostrar mensaje
                    msg_surf = self.fuente_datos.render("Ranura vacía", True, self.COLOR_TEXTO_DESHABILITADO)
                    msg_rect = msg_surf.get_rect(center=self.caja_detalles_rect.center)
                    pantalla.blit(msg_surf, msg_rect)
        
        # 5. Dibujar Caja de Inventario (en modo seleccion_item)
        if self.modo == "seleccion_item":
            pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_inventario_rect, border_radius=self.UI_BORDER_RADIUS)
            pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_inventario_rect, 3, border_radius=self.UI_BORDER_RADIUS)
            
            start_x_inv = self.caja_inventario_rect.x + 20
            start_y_inv = self.caja_inventario_rect.y + 20
            line_height_inv = 35

            # Título
            titulo_inv_surf = self.fuente_titulo.render("Inventario", True, self.COLOR_TEXTO)
            pantalla.blit(titulo_inv_surf, (start_x_inv, start_y_inv))
            
            base_y_inv = start_y_inv + 50
            
            if not self.lista_items_equipables:
                texto_surf = self.fuente_opcion.render("--- Vacío ---", True, self.COLOR_TEXTO_DESHABILITADO)
                pantalla.blit(texto_surf, (start_x_inv, base_y_inv))
            else:
                # Calcular items visibles con scroll
                total_items = len(self.lista_items_equipables)
                items_fin = min(self.scroll_inventario + self.max_items_visibles_inventario, total_items)
                items_visibles = self.lista_items_equipables[self.scroll_inventario:items_fin]
                
                for idx_visual, item_data in enumerate(items_visibles):
                    idx_real = self.scroll_inventario + idx_visual
                    item_texto = item_data["nombre"]
                    
                    if idx_real == self.item_seleccionado_idx:
                        color_item = self.COLOR_TEXTO_SEL
                        if self.cursor_img:
                            cursor_rect = self.cursor_img.get_rect(midright=(start_x_inv - 5, base_y_inv + (idx_visual * line_height_inv) + 10))
                            pantalla.blit(self.cursor_img, cursor_rect)
                    else:
                        color_item = self.COLOR_TEXTO

                    item_surf = self.fuente_opcion.render(item_texto, True, color_item)
                    pantalla.blit(item_surf, (start_x_inv, base_y_inv + (idx_visual * line_height_inv)))
                
                # Dibujar Scrollbar si es necesario
                if total_items > self.max_items_visibles_inventario:
                    scrollbar_altura = self.caja_inventario_rect.height - 80
                    scrollbar_x = self.caja_inventario_rect.right - 15
                    scrollbar_y = self.caja_inventario_rect.y + 70
                    
                    # Barra de fondo
                    pygame.draw.rect(pantalla, (50, 50, 100), 
                                   (scrollbar_x, scrollbar_y, 8, scrollbar_altura), border_radius=4)
                    
                    # Calcular posición y tamaño del thumb
                    thumb_altura = max(20, int((self.max_items_visibles_inventario / total_items) * scrollbar_altura))
                    thumb_pos_max = scrollbar_altura - thumb_altura
                    thumb_y = scrollbar_y + int((self.scroll_inventario / (total_items - self.max_items_visibles_inventario)) * thumb_pos_max)
                    
                    # Thumb
                    pygame.draw.rect(pantalla, (100, 100, 255),
                                   (scrollbar_x, thumb_y, 8, thumb_altura), border_radius=4)
        
        # 6. Dibujar Panel de Estadísticas (Abajo)
        start_x_stats = self.caja_stats_rect.x + 20
        start_y_stats = self.caja_stats_rect.y + 15
        line_height_stats = 30
        
        # --- Lógica de Vista Previa ---
        stats_preview = {} # Un diccionario para guardar los stats de vista previa
        
        # Si estamos en modo "seleccion_item" Y la lista no está vacía
        if self.modo == "seleccion_item" and self.lista_items_equipables:
            
            # 1. Obtener el ítem resaltado en el inventario
            item_preview_data = self.lista_items_equipables[self.item_seleccionado_idx]
            id_item_preview = item_preview_data.get("id_equipo") # "NINGUNO" o "ESPADA_COBRE"
            
            # 2. Obtener el ítem actualmente equipado en esa ranura
            ranura_actual = self.ranuras_equipo[self.slot_seleccionado_idx]
            id_item_equipado = self.heroe.equipo.get(ranura_actual)
            
            # 3. Calcular el bono del ítem de vista previa
            bono_preview = {"fuerza": 0, "defensa": 0, "inteligencia": 0, "espiritu": 0, "velocidad": 0, "suerte": 0, "hp_max": 0, "mp_max": 0}
            if id_item_preview != "NINGUNO":
                data = self.equipo_db.get(id_item_preview)
                if data:
                    bono_preview = data["stats"]
            
            # 4. Calcular el bono del ítem equipado actualmente
            bono_equipado = {"fuerza": 0, "defensa": 0, "inteligencia": 0, "espiritu": 0, "velocidad": 0, "suerte": 0, "hp_max": 0, "mp_max": 0}
            if id_item_equipado:
                data = self.equipo_db.get(id_item_equipado)
                if data:
                    bono_equipado = data["stats"]
            
            # 5. Calcular la diferencia (Preview - Equipado)
            stats_preview["hp_max"] = bono_preview.get("hp_max", 0) - bono_equipado.get("hp_max", 0)
            stats_preview["mp_max"] = bono_preview.get("mp_max", 0) - bono_equipado.get("mp_max", 0)
            stats_preview["fuerza"] = bono_preview.get("fuerza", 0) - bono_equipado.get("fuerza", 0)
            stats_preview["defensa"] = bono_preview.get("defensa", 0) - bono_equipado.get("defensa", 0)
            stats_preview["inteligencia"] = bono_preview.get("inteligencia", 0) - bono_equipado.get("inteligencia", 0)
            stats_preview["espiritu"] = bono_preview.get("espiritu", 0) - bono_equipado.get("espiritu", 0)
            stats_preview["velocidad"] = bono_preview.get("velocidad", 0) - bono_equipado.get("velocidad", 0)
            stats_preview["suerte"] = bono_preview.get("suerte", 0) - bono_equipado.get("suerte", 0)

        # --- Fin Lógica de Vista Previa ---

        # Lista de stats base del héroe
        stats_a_mostrar = [
            ("HP Máx", self.heroe.HP_max_base, self.heroe.HP_max, stats_preview.get("hp_max")),
            ("MP Máx", self.heroe.MP_max_base, self.heroe.MP_max, stats_preview.get("mp_max")),
            ("Fuerza", self.heroe.fuerza_base, self.heroe.fuerza, stats_preview.get("fuerza")),
            ("Defensa", self.heroe.defensa_base, self.heroe.defensa, stats_preview.get("defensa")),
        ]
        stats_a_mostrar_2 = [
            ("Inteligencia", self.heroe.inteligencia_base, self.heroe.inteligencia, stats_preview.get("inteligencia")),
            ("Espíritu", self.heroe.espiritu_base, self.heroe.espiritu, stats_preview.get("espiritu")),
            ("Velocidad", self.heroe.velocidad_base, self.heroe.velocidad, stats_preview.get("velocidad")),
            ("Suerte", self.heroe.suerte_base, self.heroe.suerte, stats_preview.get("suerte"))
        ]

        # Columna 1 de Stats
        for i, (nombre, valor_base, valor_total, diff) in enumerate(stats_a_mostrar):
            y_pos_stat = start_y_stats + (i * line_height_stats)
            bono_actual = valor_total - valor_base
            
            nombre_surf = self.fuente_datos.render(f"{nombre}:", True, self.COLOR_TEXTO)
            base_surf = self.fuente_datos.render(f"{valor_total}", True, self.COLOR_TEXTO) # Mostramos el total actual
            
            pantalla.blit(nombre_surf, (start_x_stats, y_pos_stat))
            pantalla.blit(base_surf, (start_x_stats + 120, y_pos_stat))
            
            # Dibujar la vista previa (la diferencia)
            if diff is not None:
                if diff > 0:
                    bono_txt = f"--> {valor_total + diff}"
                    bono_color = self.COLOR_TEXTO_EQUIPADO # Verde
                elif diff < 0:
                    bono_txt = f"--> {valor_total + diff}"
                    bono_color = (255, 0, 0) # Rojo
                else: # diff == 0
                    bono_txt = ""
                    bono_color = self.COLOR_TEXTO

                bono_surf = self.fuente_datos.render(bono_txt, True, bono_color)
                pantalla.blit(bono_surf, (start_x_stats + 170, y_pos_stat))

        # Columna 2 de Stats
        start_x_stats_2 = start_x_stats + 300
        for i, (nombre, valor_base, valor_total, diff) in enumerate(stats_a_mostrar_2):
            y_pos_stat = start_y_stats + (i * line_height_stats)
            
            nombre_surf = self.fuente_datos.render(f"{nombre}:", True, self.COLOR_TEXTO)
            base_surf = self.fuente_datos.render(f"{valor_total}", True, self.COLOR_TEXTO) # Mostramos el total actual
            
            pantalla.blit(nombre_surf, (start_x_stats_2, y_pos_stat))
            pantalla.blit(base_surf, (start_x_stats_2 + 120, y_pos_stat))
            
            # Dibujar la vista previa (la diferencia)
            if diff is not None:
                if diff > 0:
                    bono_txt = f"--> {valor_total + diff}"
                    bono_color = self.COLOR_TEXTO_EQUIPADO # Verde
                elif diff < 0:
                    bono_txt = f"--> {valor_total + diff}"
                    bono_color = (255, 0, 0) # Rojo
                else: # diff == 0
                    bono_txt = ""
                    bono_color = self.COLOR_TEXTO
                
                bono_surf = self.fuente_datos.render(bono_txt, True, bono_color)
                pantalla.blit(bono_surf, (start_x_stats_2 + 170, y_pos_stat))

        # 6. Dibujar Pop-up de Detalles (ENCIMA de todo)
        if self.modo == "ver_detalles":
            if self.lista_items_equipables:
                # 1. Obtener el ítem resaltado
                item_data = self.lista_items_equipables[self.item_seleccionado_idx]
                
                # 2. Definir geometría del pop-up
                caja_detalles_rect = pygame.Rect(0, 0, 300, 300)
                caja_detalles_rect.center = (self.ANCHO // 2, self.ALTO // 2)
                
                # 3. Dibujar la caja
                pygame.draw.rect(pantalla, self.COLOR_CAJA, caja_detalles_rect, border_radius=self.UI_BORDER_RADIUS)
                pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, caja_detalles_rect, 3, border_radius=self.UI_BORDER_RADIUS)
                
                # 4. Dibujar el contenido
                start_x = caja_detalles_rect.x + 20
                start_y = caja_detalles_rect.y + 20
                line_height = 25 # (Altura de línea para stats)

                # Nombre del Ítem
                nombre_surf = self.fuente_titulo.render(item_data["nombre"], True, self.COLOR_TEXTO_SEL)
                pantalla.blit(nombre_surf, (start_x, start_y))
                
                # --- ¡BLOQUE CORREGIDO CON WRAP! ---
                desc_texto = item_data.get("descripcion", "...")
                max_ancho_desc = caja_detalles_rect.width - 40 # Ancho de la caja (con padding)
                
                # Usamos la nueva función
                lineas_desc = self._wrap_text(desc_texto, self.fuente_datos, max_ancho_desc)
                
                # Dibujamos cada línea de la descripción
                desc_y = start_y + 40
                for linea in lineas_desc:
                    desc_surf = self.fuente_datos.render(linea, True, self.COLOR_TEXTO)
                    pantalla.blit(desc_surf, (start_x, desc_y))
                    desc_y += self.fuente_datos.get_height() # Mover a la siguiente línea
                # --- FIN BLOQUE CORREGIDO ---

                # Stats (si existen)
                stats = item_data.get("stats")
                if stats:
                    # ¡CORREGIDO! La 'Y' de las stats empieza DESPUÉS de la descripción
                    stat_y = desc_y + 10 
                    
                    for stat_nombre, valor in stats.items():
                        if valor != 0: # Solo mostrar stats que no sean 0
                            color_stat = self.COLOR_TEXTO_EQUIPADO if valor > 0 else (255, 0, 0)
                            stat_texto = f"{stat_nombre.capitalize()}: {valor:+} "
                            stat_surf = self.fuente_datos.render(stat_texto, True, color_stat)
                            pantalla.blit(stat_surf, (start_x, stat_y))
                            stat_y += line_height

        