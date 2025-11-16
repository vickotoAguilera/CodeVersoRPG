import pygame
import sys

# --- ¡"RECABLEADO" (MODIFICADO) BKN! (Paso 56.8) ---
# Este es el "Motor" (Engine) de UI para el sub-menú de Items en la batalla.

class PantallaItems:
    
    # --- 1. EL CONSTRUCTOR (¡"RECABLEADO" (MODIFICADO)!) ---
    # ¡Ahora "pilla" (recibe) el cursor BKN!
    def __init__(self, ancho_pantalla, alto_pantalla, heroe_actor, items_db_completa, cursor_img_bkn):
        print(f"¡Abriendo Pantalla de Items para {heroe_actor.nombre_clase}!")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        
        self.heroe_actor = heroe_actor
        self.items_db = items_db_completa
        
        # --- ¡NUEVO BKN! "Guardamos" (Almacenamos) el cursor (Paso 56.8) ---
        self.cursor_img = cursor_img_bkn
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_opcion = pygame.font.Font(None, 30) # "Poción", "Éter"
            self.fuente_datos = pygame.font.Font(None, 28) # "Usar:"
            self.fuente_desc = pygame.font.Font(None, 26) # "Restaura HP..."
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Opciones del Menú ---
        self.opciones_mostradas = [] 
        self.opcion_seleccionada = 0
        self._build_lista_opciones() 
        
        # --- Cooldown ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Sistema de Scroll ---
        self.scroll_offset = 0
        self.items_visibles_max = 8
        
        # --- Colores (Sin cambios) ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180) 
        self.COLOR_CAJA = (0, 0, 139) 
        self.COLOR_BORDE = (255, 255, 255) 
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_CANTIDAD = (200, 200, 200) 
        self.COLOR_SCROLLBAR = (100, 100, 255)
        self.UI_BORDER_RADIUS = 12 

        # --- Geometría de las Cajas (Sin cambios) ---
        self.caja_desc_rect = pygame.Rect(30, 30, self.ANCHO - 60, 100)
        self.caja_actor_rect = pygame.Rect(30, self.caja_desc_rect.bottom + 15, 250, 60)
        self.caja_items_rect = pygame.Rect(self.caja_actor_rect.right + 15, self.caja_desc_rect.bottom + 15, 
                                          self.ANCHO - self.caja_actor_rect.right - 15 - 30, 
                                          self.ALTO - self.caja_desc_rect.bottom - 15 - 30)

    # --- 2. BUILD LISTA (QUEDA 100% IGUAL) ---
    def _build_lista_opciones(self):
        """
        "Arma" (Construye) la lista de items que mostraremos en el menú.
        "Pilla" (Lee) el inventario (dict) del héroe y "traduce" (busca) los datos
        en la "enciclopedia" (items_db).
        """
        self.opciones_mostradas = []
        
        print(f"Inventario de {self.heroe_actor.nombre_clase}: {self.heroe_actor.inventario}")
        
        for id_item, cantidad in self.heroe_actor.inventario.items():
            
            if cantidad > 0:
                item_data = self.items_db.get(id_item)
                
                if item_data:
                    self.opciones_mostradas.append(item_data)
                else:
                    print(f"¡ADVERTENCIA! Héroe 'cacha' (tiene) '{id_item}' pero no existe en items_db.json")

        self.opciones_mostradas.append({
            "id_item": "VOLVER", 
            "nombre": "Volver",
            "descripcion": "Vuelve al menú de batalla anterior.",
            "tipo": "Accion"
        })

    # --- 3. EL UPDATE (CON SCROLL) ---
    def update(self, teclas):
        """Maneja el input del teclado para mover el cursor."""
        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            if teclas[pygame.K_DOWN]:
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones_mostradas)
                
                # Ajustar scroll si es necesario
                if self.opcion_seleccionada >= self.scroll_offset + self.items_visibles_max:
                    self.scroll_offset = self.opcion_seleccionada - self.items_visibles_max + 1
                    
                self.tiempo_ultimo_input = tiempo_actual
            elif teclas[pygame.K_UP]:
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_mostradas)
                
                # Ajustar scroll si es necesario
                if self.opcion_seleccionada < self.scroll_offset:
                    self.scroll_offset = self.opcion_seleccionada
                    
                self.tiempo_ultimo_input = tiempo_actual
        return None

    # --- 4. EL UPDATE_INPUT (QUEDA 100% IGUAL) ---
    def update_input(self, tecla):
        """
        Se llama desde batalla.py SOLO cuando se presiona Enter o Escape.
        Devuelve una "acción" (un dict) o "volver" (un string).
        """
        
        if tecla == pygame.K_ESCAPE:
            print("¡Volviendo (Escape)!")
            return "volver"
            
        if tecla == pygame.K_RETURN:
            
            opcion = self.opciones_mostradas[self.opcion_seleccionada]
            id_opcion = opcion.get("id_item", "VOLVER")
            tipo_opcion = opcion.get("tipo", "Accion")

            if id_opcion == "VOLVER":
                print("¡Volviendo (Selección)!")
                return "volver"
            
            if tipo_opcion == "Consumible":
                print(f"¡Acción seleccionada: {id_opcion}!")
                return {
                    "accion": "usar_item", 
                    "item_data": opcion 
                }
            else:
                print(f"¡No puedes usar {id_opcion} en batalla!")
                return None 
                
        return None

    # --- 5. EL DRAW (¡"RECABLEADO" (MODIFICADO)!) ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo" (Sin cambios)
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar las 3 Cajas Azules (Sin cambios)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_desc_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_actor_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_items_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # 3. Dibujar los Bordes Blancos (Sin cambios)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_actor_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_items_rect, 3, border_radius=self.UI_BORDER_RADIUS)

        # 4. Dibujar Contenido: Caja Descripción (Arriba) (Sin cambios)
        opcion_actual = self.opciones_mostradas[self.opcion_seleccionada]
        
        desc_texto = opcion_actual.get("descripcion", "...")
        desc_surf = self.fuente_desc.render(desc_texto, True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.centery))
        pantalla.blit(desc_surf, desc_rect)

        # 5. Dibujar Contenido: Caja Actor (Medio) (Sin cambios)
        actor_texto = f"Usar: {self.heroe_actor.nombre_clase}"
        actor_surf = self.fuente_datos.render(actor_texto, True, self.COLOR_TEXTO)
        actor_rect = actor_surf.get_rect(midleft=(self.caja_actor_rect.x + 20, self.caja_actor_rect.centery))
        pantalla.blit(actor_surf, actor_rect)
        
        # 6. Dibujar Contenido: Lista de Items (Medio/Derecha) (CON SCROLL)
        padding_y_opciones = 15
        start_y_opciones = self.caja_items_rect.y + 25
        
        # Calcular items visibles
        total_items = len(self.opciones_mostradas)
        items_fin = min(self.scroll_offset + self.items_visibles_max, total_items)
        items_visibles = self.opciones_mostradas[self.scroll_offset:items_fin]
        
        for idx_visual, item_data in enumerate(items_visibles):
            idx_real = self.scroll_offset + idx_visual
            
            item_texto = item_data.get("nombre", "ERROR")
            item_id = item_data.get("id_item")
            
            color = self.COLOR_TEXTO_SEL if idx_real == self.opcion_seleccionada else self.COLOR_TEXTO

            texto_surf = self.fuente_opcion.render(item_texto, True, color)
            
            pos_x = self.caja_items_rect.x + 50
            pos_y = start_y_opciones + (idx_visual * (self.fuente_opcion.get_height() + padding_y_opciones))
            opcion_rect = texto_surf.get_rect(midleft=(pos_x, pos_y))
            
            # --- Cursor ---
            if idx_real == self.opcion_seleccionada:
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(opcion_rect.left - 5, opcion_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    cursor_surf = self.fuente_opcion.render(">", True, color)
                    cursor_rect = cursor_surf.get_rect(midright=(opcion_rect.left - 10, opcion_rect.centery))
                    pantalla.blit(cursor_surf, cursor_rect)
            
            pantalla.blit(texto_surf, opcion_rect)
            
            # --- Cantidad ---
            if item_id != "VOLVER":
                cantidad = self.heroe_actor.inventario.get(item_id, 0)
                cantidad_texto = f"x{cantidad}"
                
                color_cantidad = self.COLOR_TEXTO_SEL if idx_real == self.opcion_seleccionada else self.COLOR_TEXTO_CANTIDAD
                
                cantidad_surf = self.fuente_opcion.render(cantidad_texto, True, color_cantidad)
                
                cantidad_rect = cantidad_surf.get_rect(midright=(self.caja_items_rect.right - 40, opcion_rect.centery))
                pantalla.blit(cantidad_surf, cantidad_rect)
        
        # 7. Dibujar Scrollbar
        if total_items > self.items_visibles_max:
            scrollbar_altura = self.caja_items_rect.height - 20
            scrollbar_x = self.caja_items_rect.right - 15
            scrollbar_y = self.caja_items_rect.y + 10
            
            # Barra de fondo
            pygame.draw.rect(pantalla, (50, 50, 100), 
                           (scrollbar_x, scrollbar_y, 8, scrollbar_altura), border_radius=4)
            
            # Calcular posición y tamaño del thumb
            thumb_altura = max(20, int((self.items_visibles_max / total_items) * scrollbar_altura))
            thumb_pos_max = scrollbar_altura - thumb_altura
            thumb_y = scrollbar_y + int((self.scroll_offset / (total_items - self.items_visibles_max)) * thumb_pos_max)
            
            # Thumb
            pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR,
                           (scrollbar_x, thumb_y, 8, thumb_altura), border_radius=4)