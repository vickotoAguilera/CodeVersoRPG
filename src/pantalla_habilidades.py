import pygame
import sys

# --- Sistema de Habilidades Equipables (Paso 7.17) ---
# Esta pantalla permite al jugador:
# - Ver todas las habilidades aprendidas (inventario_habilidades)
# - Equipar/desequipar habilidades en las ranuras activas (4 slots)
# - Filtrar habilidades por clase del héroe
# - Ver descripción detallada de cada habilidad

class PantallaHabilidades:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, heroe_obj, habilidades_db_completa, cursor_img):
        print(f"¡Abriendo Pantalla de Habilidades para {heroe_obj.nombre_en_juego}!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.heroe = heroe_obj
        self.habilidades_db = habilidades_db_completa
        self.cursor_img = cursor_img
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 40)
            self.fuente_opcion = pygame.font.Font(None, 30)
            self.fuente_datos = pygame.font.Font(None, 28)
            self.fuente_pequeña = pygame.font.Font(None, 24)
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Control y Estados ---
        # Modos: "inventario", "ranuras", "boton_volver", "descripcion"
        self.panel_activo = "inventario"
        self.modo = "navegacion"  # "navegacion" o "equipando"
        self.habilidad_a_equipar = None  # ID de la habilidad seleccionada para equipar
        
        # Índices de selección
        self.inventario_seleccionado_idx = 0 # Para la lista de inventario
        self.ranura_seleccionada_idx = 0 # 0-3 para las ranuras activas
        
        # Listas de habilidades filtradas
        self.lista_inventario_habilidades = [] # Habilidades disponibles (filtradas por clase)
        self.lista_ranuras_activas = [] # Las ranuras activas (dinámicas)
        
        # Scroll para listas largas
        self.scroll_inventario = 0 # Offset de scroll para inventario
        self.scroll_descripcion = 0 # Offset de scroll para descripción
        self.scroll_ranuras = 0 # Offset de scroll para ranuras activas
        self.max_items_visibles_inventario = 8 # Cuántos items se ven a la vez
        self.max_items_visibles_ranuras = 4 # Cuántas ranuras se ven a la vez

        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Animación del sprite del héroe ---
        self.tiempo_ultimo_anim = pygame.time.get_ticks()
        self.velocidad_anim = 800
        self.frame_anim_actual = 0

        # --- Colores y Estilo ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0) # Amarillo para selección
        self.COLOR_TEXTO_EQUIPADO = (0, 255, 0) # Verde para equipado
        self.COLOR_TEXTO_DESHABILITADO = (100, 100, 100) # Gris para vacío
        self.COLOR_FISICA = (255, 100, 100) # Rojo claro para habilidades físicas
        self.COLOR_MAGICA = (100, 150, 255) # Azul claro para habilidades mágicas
        self.UI_BORDER_RADIUS = 12
        
        # --- Geometría de las Cajas (4 Paneles) ---
        
        padding = 20
        
        # 1. Panel Izquierdo: Sprite del Héroe
        self.caja_sprite_rect = pygame.Rect(
            padding, 
            padding, 
            150, 
            200
        )
        
        # Botón de "Volver al Menú" debajo del sprite
        self.boton_volver_rect = pygame.Rect(
            padding,
            self.caja_sprite_rect.bottom + 10,
            150,
            40
        )
        
        # 2. Panel Derecho: Inventario de Habilidades (scrollable)
        self.caja_inventario_rect = pygame.Rect(
            self.caja_sprite_rect.right + padding,
            padding,
            250,
            370
        )
        
        # 3. Panel Central-Derecho: Descripción (scrollable)
        self.caja_descripcion_rect = pygame.Rect(
            self.caja_inventario_rect.right + padding,
            padding,
            self.ANCHO - self.caja_inventario_rect.right - padding * 2,
            370
        )
        
        # 4. Panel Inferior: Ranuras Activas (4 slots)
        self.caja_ranuras_rect = pygame.Rect(
            padding,
            self.caja_inventario_rect.bottom + padding,
            self.ANCHO - padding * 2,
            self.ALTO - self.caja_inventario_rect.bottom - padding * 2
        )
        
        # Cargar las listas iniciales
        self._actualizar_listas()

    # --- 2. ACTUALIZAR LISTAS ---
    def _actualizar_listas(self):
        """Filtra y actualiza las listas de habilidades según la clase del héroe"""
        
        # Limpiar listas
        self.lista_inventario_habilidades = []
        self.lista_ranuras_activas = []
        
        # Obtener la clase del héroe
        clase_heroe = self.heroe.clase
        
        # Obtener lista de IDs de habilidades ya equipadas (para filtrarlas del inventario)
        habilidades_equipadas = [h for h in self.heroe.habilidades_activas if h is not None]
        
        # Filtrar inventario de habilidades (EXCLUIR LAS YA EQUIPADAS)
        for id_habilidad in self.heroe.inventario_habilidades:
            if id_habilidad: # Ignorar None
                # NO MOSTRAR si ya está equipada
                if id_habilidad in habilidades_equipadas:
                    continue
                    
                hab_data = self.habilidades_db.get(id_habilidad)
                if hab_data:
                    # Filtrar por clase (si la habilidad especifica clase_requerida)
                    clase_req = hab_data.get("clase_requerida", None)
                    if clase_req is None or clase_req == clase_heroe:
                        self.lista_inventario_habilidades.append(hab_data)
        
        # Cargar ranuras activas (las 4 ranuras)
        for i in range(self.heroe.ranuras_habilidad_max):
            id_hab = None
            if i < len(self.heroe.habilidades_activas):
                id_hab = self.heroe.habilidades_activas[i]
            
            if id_hab and id_hab in self.habilidades_db:
                hab_data = self.habilidades_db[id_hab]
                self.lista_ranuras_activas.append({
                    "indice": i,
                    "id_habilidad": id_hab,
                    "nombre": hab_data.get("nombre", "???"),
                    "data": hab_data
                })
            else:
                # Ranura vacía
                self.lista_ranuras_activas.append({
                    "indice": i,
                    "id_habilidad": None,
                    "nombre": "[Vacío]",
                    "data": None
                })

    # --- 3. EL UPDATE ---
    def update(self, teclas):
        
        tiempo_actual = pygame.time.get_ticks()
        
        # Animación del sprite
        if tiempo_actual - self.tiempo_ultimo_anim > self.velocidad_anim:
            self.tiempo_ultimo_anim = tiempo_actual
            self.frame_anim_actual = (self.frame_anim_actual + 1) % 2
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # ===== NAVEGACIÓN ENTRE PANELES =====
            
            # [PANEL: Inventario]
            if self.panel_activo == "inventario":
                if self.lista_inventario_habilidades:
                    num_items = len(self.lista_inventario_habilidades)
                    
                    if teclas[pygame.K_DOWN]:
                        self.inventario_seleccionado_idx = (self.inventario_seleccionado_idx + 1) % num_items
                        if self.inventario_seleccionado_idx >= self.scroll_inventario + self.max_items_visibles_inventario:
                            self.scroll_inventario += 1
                        elif self.inventario_seleccionado_idx < self.scroll_inventario:
                            self.scroll_inventario = self.inventario_seleccionado_idx
                        self.tiempo_ultimo_input = tiempo_actual
                        
                    elif teclas[pygame.K_UP]:
                        self.inventario_seleccionado_idx = (self.inventario_seleccionado_idx - 1) % num_items
                        if self.inventario_seleccionado_idx < self.scroll_inventario:
                            self.scroll_inventario = self.inventario_seleccionado_idx
                        elif self.inventario_seleccionado_idx >= self.scroll_inventario + self.max_items_visibles_inventario:
                            self.scroll_inventario = self.inventario_seleccionado_idx - self.max_items_visibles_inventario + 1
                        self.tiempo_ultimo_input = tiempo_actual
                    
                    elif teclas[pygame.K_LEFT]:
                        # Ir al botón volver
                        self.panel_activo = "boton_volver"
                        self.tiempo_ultimo_input = tiempo_actual
                    
                    elif teclas[pygame.K_RIGHT]:
                        # Ir a la descripción
                        self.panel_activo = "descripcion"
                        self.tiempo_ultimo_input = tiempo_actual
            
            # [PANEL: Descripción]
            elif self.panel_activo == "descripcion":
                if teclas[pygame.K_LEFT]:
                    # Volver al inventario
                    self.panel_activo = "inventario"
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif teclas[pygame.K_DOWN]:
                    # Ir a las ranuras
                    self.panel_activo = "ranuras"
                    self.tiempo_ultimo_input = tiempo_actual
                
                # Scroll en la descripción con arriba/abajo si hay texto largo
                elif teclas[pygame.K_UP]:
                    if self.scroll_descripcion > 0:
                        self.scroll_descripcion -= 1
                    self.tiempo_ultimo_input = tiempo_actual

            # [PANEL: Botón Volver]
            elif self.panel_activo == "boton_volver":
                if teclas[pygame.K_RIGHT]:
                    # Ir al inventario
                    self.panel_activo = "inventario"
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif teclas[pygame.K_DOWN]:
                    # Ir a las ranuras
                    self.panel_activo = "ranuras"
                    self.tiempo_ultimo_input = tiempo_actual

            # [PANEL: Ranuras Activas]
            elif self.panel_activo == "ranuras":
                num_ranuras = len(self.lista_ranuras_activas)
                
                if teclas[pygame.K_RIGHT]:
                    self.ranura_seleccionada_idx = (self.ranura_seleccionada_idx + 1) % num_ranuras
                    if self.ranura_seleccionada_idx >= self.scroll_ranuras + self.max_items_visibles_ranuras:
                        self.scroll_ranuras += 1
                    elif self.ranura_seleccionada_idx < self.scroll_ranuras:
                        self.scroll_ranuras = self.ranura_seleccionada_idx
                    self.tiempo_ultimo_input = tiempo_actual
                    
                elif teclas[pygame.K_LEFT]:
                    self.ranura_seleccionada_idx = (self.ranura_seleccionada_idx - 1) % num_ranuras
                    if self.ranura_seleccionada_idx < self.scroll_ranuras:
                        self.scroll_ranuras = self.ranura_seleccionada_idx
                    elif self.ranura_seleccionada_idx >= self.scroll_ranuras + self.max_items_visibles_ranuras:
                        self.scroll_ranuras = self.ranura_seleccionada_idx - self.max_items_visibles_ranuras + 1
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif teclas[pygame.K_UP]:
                    # Volver al inventario o al botón según la posición horizontal
                    if self.ranura_seleccionada_idx < 2:
                        self.panel_activo = "boton_volver"
                    else:
                        self.panel_activo = "inventario"
                    self.tiempo_ultimo_input = tiempo_actual
        
        return None

    # --- 4. EL UPDATE_INPUT ---
    def update_input(self, tecla):
        
        # [ESCAPE: Salir siempre]
        if tecla == pygame.K_ESCAPE:
            # Si estamos en modo "equipando", cancelar
            if self.modo == "equipando":
                print("¡Cancelando equipar habilidad!")
                self.modo = "navegacion"
                self.habilidad_a_equipar = None
                return None
            else:
                print("¡Cerrando Pantalla de Habilidades!")
                return {"accion": "volver_menu_pausa"}
        
        # [ENTER: Acciones según panel activo y modo]
        if tecla == pygame.K_RETURN:
            
            # Si está en el botón volver
            if self.panel_activo == "boton_volver":
                print("¡Cerrando Pantalla de Habilidades!")
                return {"accion": "volver_menu_pausa"}
            
            # Si está en inventario
            elif self.panel_activo == "inventario":
                if self.modo == "navegacion":
                    # Paso 1: Seleccionar habilidad para equipar
                    if self.lista_inventario_habilidades:
                        hab_seleccionada = self.lista_inventario_habilidades[self.inventario_seleccionado_idx]
                        id_hab = hab_seleccionada.get("id_habilidad")
                        
                        print(f"Habilidad '{id_hab}' seleccionada. Ahora elige una ranura.")
                        self.habilidad_a_equipar = id_hab
                        self.modo = "equipando"
                        # Cambiar automáticamente al panel de ranuras
                        self.panel_activo = "ranuras"
                        return None
            
            # Si está en ranuras
            elif self.panel_activo == "ranuras":
                if self.modo == "equipando":
                    # Paso 2: Confirmar equipar en la ranura seleccionada
                    if self.habilidad_a_equipar:
                        self._equipar_habilidad(self.habilidad_a_equipar, self.ranura_seleccionada_idx)
                        print(f"Habilidad equipada en ranura {self.ranura_seleccionada_idx + 1}.")
                        # Volver al modo navegación
                        self.modo = "navegacion"
                        self.habilidad_a_equipar = None
                        # Volver al inventario
                        self.panel_activo = "inventario"
                        return None
                else:
                    # Modo navegación: desequipar
                    self._desequipar_habilidad(self.ranura_seleccionada_idx)
                    print(f"Habilidad desequipada de ranura {self.ranura_seleccionada_idx + 1}.")
                    return None

        # [Tecla X: Desequipar de Ranura desde cualquier panel]
        if tecla == pygame.K_x:
            if self.panel_activo == "ranuras" and self.modo == "navegacion":
                self._desequipar_habilidad(self.ranura_seleccionada_idx)
                print(f"Habilidad desequipada de ranura {self.ranura_seleccionada_idx + 1}.")
                return None
                
        return None

    # --- 5. EQUIPAR HABILIDAD ---
    def _equipar_habilidad(self, id_habilidad, ranura_idx):
        """Equipa una habilidad en una ranura específica"""
        
        # Validar que el índice de ranura sea válido
        if ranura_idx < 0 or ranura_idx >= self.heroe.ranuras_habilidad_max:
            print(f"¡Error! Ranura {ranura_idx} inválida.")
            return
        
        # Validar que la habilidad esté en el inventario
        if id_habilidad not in self.heroe.inventario_habilidades:
            print(f"¡Error! Habilidad {id_habilidad} no está en el inventario.")
            return
        
        # VALIDAR: No permitir equipar la misma habilidad si ya está equipada en otra ranura
        if id_habilidad in self.heroe.habilidades_activas:
            print(f"¡Error! La habilidad '{id_habilidad}' ya está equipada en otra ranura.")
            return
        
        # Asegurar que la lista de habilidades activas tenga el tamaño correcto
        while len(self.heroe.habilidades_activas) < self.heroe.ranuras_habilidad_max:
            self.heroe.habilidades_activas.append(None)
        
        # Si la ranura ya tiene una habilidad, esta volverá al inventario automáticamente
        # (porque la lista inventario_habilidades siempre la contiene, solo se filtra visualmente)
        habilidad_anterior = self.heroe.habilidades_activas[ranura_idx]
        if habilidad_anterior:
            print(f"  → La habilidad '{habilidad_anterior}' regresa al inventario disponible.")
        
        # Equipar la nueva habilidad
        self.heroe.habilidades_activas[ranura_idx] = id_habilidad
        
        # Actualizar listas (esto filtrará la habilidad equipada del inventario visible)
        self._actualizar_listas()
        
        # Reiniciar índice de selección de inventario si es necesario
        if self.inventario_seleccionado_idx >= len(self.lista_inventario_habilidades):
            self.inventario_seleccionado_idx = max(0, len(self.lista_inventario_habilidades) - 1)
        
        print(f"✓ Habilidad '{id_habilidad}' equipada en ranura {ranura_idx + 1}.")

    # --- 6. DESEQUIPAR HABILIDAD ---
    def _desequipar_habilidad(self, ranura_idx):
        """Desequipa una habilidad de una ranura específica"""
        
        # Validar que el índice de ranura sea válido
        if ranura_idx < 0 or ranura_idx >= len(self.heroe.habilidades_activas):
            print(f"¡Error! Ranura {ranura_idx} inválida.")
            return
        
        # Obtener la habilidad a desequipar
        hab_id = self.heroe.habilidades_activas[ranura_idx]
        
        # Si la ranura ya está vacía, no hacer nada
        if hab_id is None:
            print(f"La ranura {ranura_idx + 1} ya está vacía.")
            return
        
        # Desequipar (poner a None)
        self.heroe.habilidades_activas[ranura_idx] = None
        
        # Actualizar listas (esto hará que la habilidad vuelva a aparecer en el inventario)
        self._actualizar_listas()
        
        print(f"✓ Habilidad '{hab_id}' desequipada de ranura {ranura_idx + 1} y regresó al inventario.")

    # --- 7. FUNCIÓN AUXILIAR: WRAP TEXT ---
    def _wrap_text(self, texto, fuente, max_ancho):
        """Divide un texto largo en múltiples líneas"""
        palabras = texto.split(' ')
        lineas = []
        linea_actual = ""
        
        for palabra in palabras:
            linea_prueba = f"{linea_actual} {palabra}".strip()
            ancho_prueba = fuente.size(linea_prueba)[0]
            
            if ancho_prueba > max_ancho:
                lineas.append(linea_actual)
                linea_actual = palabra
            else:
                linea_actual = linea_prueba
        
        lineas.append(linea_actual)
        return lineas

    # --- 8. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el velo de fondo
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar título
        titulo_surf = self.fuente_titulo.render(
            f"HABILIDADES: {self.heroe.nombre_en_juego}", 
            True, 
            self.COLOR_TEXTO
        )
        pantalla.blit(titulo_surf, (self.ANCHO // 2 - titulo_surf.get_width() // 2, 5))
        
        # 3. Dibujar los 4 paneles
        self._draw_panel_sprite(pantalla)
        self._draw_boton_volver(pantalla)
        self._draw_panel_inventario(pantalla)
        self._draw_panel_descripcion(pantalla)
        self._draw_panel_ranuras(pantalla)
        
        # 4. Dibujar instrucciones
        self._draw_instrucciones(pantalla)
        
        # 5. Si está en modo detalles, dibujar pop-up
        if self.modo == "ver_detalles":
            self._draw_popup_detalles(pantalla)

    # --- 9. PANEL 1: SPRITE DEL HÉROE ---
    def _draw_panel_sprite(self, pantalla):
        """Dibuja el panel izquierdo con el sprite del héroe"""
        
        # Fondo del panel
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_sprite_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_sprite_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        # Dibujar sprite del héroe usando el sprite "parado_abajo"
        if hasattr(self.heroe, 'img_parado_abajo'):
            sprite_actual = self.heroe.img_parado_abajo
            # Calcular tamaño escalado (mantener proporción)
            ancho_original = sprite_actual.get_width()
            alto_original = sprite_actual.get_height()
            # Escalar para que quepa bien en el panel (96px de alto máximo)
            factor_escala = 96 / alto_original
            nuevo_ancho = int(ancho_original * factor_escala)
            nuevo_alto = 96
            sprite_escalado = pygame.transform.scale(sprite_actual, (nuevo_ancho, nuevo_alto))
            # Centrar en el panel
            sprite_x = self.caja_sprite_rect.centerx - sprite_escalado.get_width() // 2
            sprite_y = self.caja_sprite_rect.top + 10
            pantalla.blit(sprite_escalado, (sprite_x, sprite_y))
        
        # Nombre y clase del héroe
        y_offset = self.caja_sprite_rect.top + 115
        
        nombre_surf = self.fuente_opcion.render(self.heroe.nombre_en_juego, True, self.COLOR_TEXTO)
        pantalla.blit(nombre_surf, (self.caja_sprite_rect.centerx - nombre_surf.get_width() // 2, y_offset))
        
        clase_surf = self.fuente_datos.render(f"{self.heroe.clase}", True, self.COLOR_TEXTO)
        pantalla.blit(clase_surf, (self.caja_sprite_rect.centerx - clase_surf.get_width() // 2, y_offset + 35))
        
        # Ranuras disponibles
        ranuras_surf = self.fuente_pequeña.render(
            f"Ranuras: {self.heroe.ranuras_habilidad_max}", 
            True, 
            self.COLOR_TEXTO
        )
        pantalla.blit(ranuras_surf, (self.caja_sprite_rect.centerx - ranuras_surf.get_width() // 2, y_offset + 60))

    # --- 9B. BOTÓN VOLVER AL MENÚ ---
    def _draw_boton_volver(self, pantalla):
        """Dibuja el botón de volver al menú debajo del sprite"""
        
        # Color según si está seleccionado
        if self.panel_activo == "boton_volver":
            color_fondo = (100, 100, 200)
            color_texto = self.COLOR_TEXTO_SEL
        else:
            color_fondo = (50, 50, 120)
            color_texto = self.COLOR_TEXTO
        
        # Dibujar botón
        pygame.draw.rect(pantalla, color_fondo, self.boton_volver_rect, border_radius=8)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.boton_volver_rect, 2, border_radius=8)
        
        # Texto del botón
        texto_surf = self.fuente_pequeña.render("VOLVER", True, color_texto)
        pantalla.blit(texto_surf, (
            self.boton_volver_rect.centerx - texto_surf.get_width() // 2,
            self.boton_volver_rect.centery - texto_surf.get_height() // 2
        ))

    # --- 10. PANEL 2: INVENTARIO DE HABILIDADES ---
    def _draw_panel_inventario(self, pantalla):
        """Dibuja el panel central con la lista de habilidades"""
        
        # Fondo del panel
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_inventario_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # Borde especial si está seleccionado
        if self.panel_activo == "inventario":
            pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, self.caja_inventario_rect, 4, border_radius=self.UI_BORDER_RADIUS)
        else:
            pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_inventario_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        # Título del panel
        titulo_surf = self.fuente_opcion.render("INVENTARIO", True, self.COLOR_TEXTO)
        pantalla.blit(titulo_surf, (self.caja_inventario_rect.centerx - titulo_surf.get_width() // 2, self.caja_inventario_rect.top + 10))
        
        # Lista de habilidades (scrollable)
        if not self.lista_inventario_habilidades:
            vacio_surf = self.fuente_datos.render("(Sin habilidades)", True, self.COLOR_TEXTO_DESHABILITADO)
            pantalla.blit(vacio_surf, (self.caja_inventario_rect.centerx - vacio_surf.get_width() // 2, self.caja_inventario_rect.centery))
        else:
            y_offset = self.caja_inventario_rect.top + 50
            altura_item = 38
            
            # Mostrar solo los items visibles según el scroll
            inicio = self.scroll_inventario
            fin = min(inicio + self.max_items_visibles_inventario, len(self.lista_inventario_habilidades))
            
            for i in range(inicio, fin):
                hab_data = self.lista_inventario_habilidades[i]
                nombre_hab = hab_data.get("nombre", "???")
                tipo_hab = hab_data.get("tipo", "")
                
                # Color según tipo
                if "Fisica" in tipo_hab or "Físic" in tipo_hab:
                    color_texto = self.COLOR_FISICA
                elif "Magia" in tipo_hab or "Mágic" in tipo_hab:
                    color_texto = self.COLOR_MAGICA
                else:
                    color_texto = self.COLOR_TEXTO
                
                # Resaltar si está seleccionado
                if i == self.inventario_seleccionado_idx and self.panel_activo == "inventario":
                    color_texto = self.COLOR_TEXTO_SEL
                    # Dibujar cursor
                    if self.cursor_img:
                        cursor_x = self.caja_inventario_rect.left + 10
                        cursor_y = y_offset + (i - inicio) * altura_item + 3
                        pantalla.blit(self.cursor_img, (cursor_x, cursor_y))
                
                # Marcar si está equipada
                id_hab = hab_data.get("id_habilidad")
                equipada = id_hab in self.heroe.habilidades_activas
                
                prefijo = "• " if equipada else "  "
                texto_completo = f"{prefijo}{nombre_hab}"
                
                # Limitar longitud del texto
                if len(texto_completo) > 20:
                    texto_completo = texto_completo[:18] + ".."
                
                hab_surf = self.fuente_datos.render(texto_completo, True, color_texto)
                pantalla.blit(hab_surf, (self.caja_inventario_rect.left + 40, y_offset + (i - inicio) * altura_item))
            
            # Scrollbar visual
            if len(self.lista_inventario_habilidades) > self.max_items_visibles_inventario:
                scrollbar_altura = self.caja_inventario_rect.height - 100
                scrollbar_x = self.caja_inventario_rect.right - 15
                scrollbar_y = self.caja_inventario_rect.y + 50
                
                # Barra de fondo
                pygame.draw.rect(pantalla, (50, 50, 100), 
                               (scrollbar_x, scrollbar_y, 8, scrollbar_altura), border_radius=4)
                
                # Calcular posición y tamaño del thumb
                total_items = len(self.lista_inventario_habilidades)
                thumb_altura = max(20, int((self.max_items_visibles_inventario / total_items) * scrollbar_altura))
                thumb_pos_max = scrollbar_altura - thumb_altura
                thumb_y = scrollbar_y + int((self.scroll_inventario / (total_items - self.max_items_visibles_inventario)) * thumb_pos_max)
                
                # Thumb
                pygame.draw.rect(pantalla, (100, 100, 255),
                               (scrollbar_x, thumb_y, 8, thumb_altura), border_radius=4)
            
            # Indicadores de scroll (sin Unicode)
            if self.scroll_inventario > 0:
                flecha_arriba = self.fuente_pequeña.render("^", True, self.COLOR_TEXTO)
                pantalla.blit(flecha_arriba, (self.caja_inventario_rect.centerx - flecha_arriba.get_width() // 2, self.caja_inventario_rect.top + 48))
            
            if fin < len(self.lista_inventario_habilidades):
                flecha_abajo = self.fuente_pequeña.render("v", True, self.COLOR_TEXTO)
                pantalla.blit(flecha_abajo, (self.caja_inventario_rect.centerx - flecha_abajo.get_width() // 2, self.caja_inventario_rect.bottom - 30))

    # --- 11. PANEL 3: DESCRIPCIÓN ---
    def _draw_panel_descripcion(self, pantalla):
        """Dibuja el panel derecho con la descripción de la habilidad seleccionada"""
        
        # Fondo del panel
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_descripcion_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # Borde especial si está seleccionado
        if self.panel_activo == "descripcion":
            pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, self.caja_descripcion_rect, 4, border_radius=self.UI_BORDER_RADIUS)
        else:
            pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_descripcion_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        # Título del panel
        titulo_surf = self.fuente_opcion.render("DESCRIPCIÓN", True, self.COLOR_TEXTO)
        pantalla.blit(titulo_surf, (self.caja_descripcion_rect.centerx - titulo_surf.get_width() // 2, self.caja_descripcion_rect.top + 10))
        
        # Mostrar descripción de la habilidad seleccionada
        if not self.lista_inventario_habilidades:
            return
        
        hab_seleccionada = self.lista_inventario_habilidades[self.inventario_seleccionado_idx]
        
        y_offset = self.caja_descripcion_rect.top + 50
        padding_x = 15
        max_ancho = self.caja_descripcion_rect.width - padding_x * 2
        
        # Nombre
        nombre = hab_seleccionada.get("nombre", "???")
        nombre_surf = self.fuente_opcion.render(nombre, True, self.COLOR_TEXTO_SEL)
        pantalla.blit(nombre_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
        y_offset += 35
        
        # Tipo
        tipo = hab_seleccionada.get("tipo", "???")
        tipo_surf = self.fuente_datos.render(f"Tipo: {tipo}", True, self.COLOR_TEXTO)
        pantalla.blit(tipo_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
        y_offset += 30
        
        # Costo MP
        costo_mp = hab_seleccionada.get("costo_mp", 0)
        costo_surf = self.fuente_datos.render(f"Costo MP: {costo_mp}", True, self.COLOR_TEXTO)
        pantalla.blit(costo_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
        y_offset += 30
        
        # Poder
        poder = hab_seleccionada.get("poder", 0)
        if poder > 0:
            poder_surf = self.fuente_datos.render(f"Poder: {poder}", True, self.COLOR_TEXTO)
            pantalla.blit(poder_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
            y_offset += 30
        
        # Alcance
        alcance = hab_seleccionada.get("alcance", "???")
        alcance_surf = self.fuente_datos.render(f"Alcance: {alcance}", True, self.COLOR_TEXTO)
        pantalla.blit(alcance_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
        y_offset += 35
        
        # Descripción (wrapped)
        descripcion = hab_seleccionada.get("descripcion", "Sin descripción.")
        lineas_desc = self._wrap_text(descripcion, self.fuente_pequeña, max_ancho)
        
        for linea in lineas_desc:
            if y_offset + 25 > self.caja_descripcion_rect.bottom - 10:
                break # No dibujar fuera del panel
            linea_surf = self.fuente_pequeña.render(linea, True, self.COLOR_TEXTO)
            pantalla.blit(linea_surf, (self.caja_descripcion_rect.left + padding_x, y_offset))
            y_offset += 25

    # --- 12. PANEL 4: RANURAS ACTIVAS ---
    def _draw_panel_ranuras(self, pantalla):
        """Dibuja el panel inferior con las ranuras de habilidades activas (scrollable)"""
        
        # Fondo del panel
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_ranuras_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # Borde especial si está seleccionado
        if self.panel_activo == "ranuras":
            pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, self.caja_ranuras_rect, 4, border_radius=self.UI_BORDER_RADIUS)
        else:
            pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_ranuras_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        # Título del panel
        titulo_surf = self.fuente_opcion.render("RANURAS ACTIVAS", True, self.COLOR_TEXTO)
        pantalla.blit(titulo_surf, (self.caja_ranuras_rect.left + 20, self.caja_ranuras_rect.top + 8))
        
        # Dibujar las ranuras horizontalmente (con scroll)
        num_ranuras = len(self.lista_ranuras_activas)
        if num_ranuras == 0:
            return
        
        # Calcular ranuras visibles según scroll
        inicio = self.scroll_ranuras
        fin = min(inicio + self.max_items_visibles_ranuras, num_ranuras)
        ranuras_visibles = self.lista_ranuras_activas[inicio:fin]
        
        ranura_ancho = (self.caja_ranuras_rect.width - 80) // self.max_items_visibles_ranuras
        ranura_alto = 70
        padding_x = 30
        y_ranura = self.caja_ranuras_rect.top + 45
        
        for idx_visual, ranura_info in enumerate(ranuras_visibles):
            i = inicio + idx_visual
            x_ranura = self.caja_ranuras_rect.left + padding_x + (idx_visual * ranura_ancho)
            ranura_rect = pygame.Rect(x_ranura, y_ranura, ranura_ancho - 10, ranura_alto)
            
            # Color del borde según estado
            if i == self.ranura_seleccionada_idx and self.panel_activo == "ranuras":
                color_borde = self.COLOR_TEXTO_SEL
                grosor = 4
            else:
                color_borde = self.COLOR_BORDE
                grosor = 2
            
            # Fondo de la ranura
            pygame.draw.rect(pantalla, (30, 30, 60), ranura_rect, border_radius=8)
            pygame.draw.rect(pantalla, color_borde, ranura_rect, grosor, border_radius=8)
            
            # Icono y número de ranura
            if ranura_info["id_habilidad"] is None:
                icono_ranura = f"[{i + 1}]"  # Ranura vacía
            else:
                icono_ranura = f"[#{i + 1}]"  # Ranura ocupada
            
            numero_surf = self.fuente_pequeña.render(icono_ranura, True, self.COLOR_TEXTO)
            pantalla.blit(numero_surf, (ranura_rect.centerx - numero_surf.get_width() // 2, ranura_rect.top + 8))
            
            # Nombre de la habilidad
            nombre = ranura_info["nombre"]
            if ranura_info["id_habilidad"] is None:
                color_texto = self.COLOR_TEXTO_DESHABILITADO
            else:
                color_texto = self.COLOR_TEXTO_EQUIPADO
            
            # Dividir nombre si es muy largo
            max_chars = 10
            if len(nombre) > max_chars:
                nombre = nombre[:max_chars - 1] + "."
            
            nombre_surf = self.fuente_datos.render(nombre, True, color_texto)
            pantalla.blit(nombre_surf, (ranura_rect.centerx - nombre_surf.get_width() // 2, ranura_rect.centery + 5))
        
        # Scrollbar horizontal
        if num_ranuras > self.max_items_visibles_ranuras:
            scrollbar_ancho = self.caja_ranuras_rect.width - 60
            scrollbar_x = self.caja_ranuras_rect.left + 30
            scrollbar_y = self.caja_ranuras_rect.bottom - 15
            
            # Barra de fondo
            pygame.draw.rect(pantalla, (50, 50, 100),
                           (scrollbar_x, scrollbar_y, scrollbar_ancho, 6), border_radius=3)
            
            # Calcular posición y tamaño del thumb
            thumb_ancho = max(30, int((self.max_items_visibles_ranuras / num_ranuras) * scrollbar_ancho))
            thumb_pos_max = scrollbar_ancho - thumb_ancho
            thumb_x = scrollbar_x + int((self.scroll_ranuras / (num_ranuras - self.max_items_visibles_ranuras)) * thumb_pos_max)
            
            # Thumb
            pygame.draw.rect(pantalla, (100, 100, 255),
                           (thumb_x, scrollbar_y, thumb_ancho, 6), border_radius=3)
        
        # Indicadores de scroll horizontal
        if self.scroll_ranuras > 0:
            flecha_izq = self.fuente_opcion.render("◀", True, self.COLOR_TEXTO)
            pantalla.blit(flecha_izq, (self.caja_ranuras_rect.left + 5, self.caja_ranuras_rect.centery + 10))
        
        if fin < num_ranuras:
            flecha_der = self.fuente_opcion.render("▶", True, self.COLOR_TEXTO)
            pantalla.blit(flecha_der, (self.caja_ranuras_rect.right - 25, self.caja_ranuras_rect.centery + 10))

    # --- 13. INSTRUCCIONES ---
    def _draw_instrucciones(self, pantalla):
        """Dibuja las instrucciones de control en la parte superior"""
        
        y_instruc = self.caja_ranuras_rect.bottom + 10
        
        if self.modo == "equipando":
            # Modo especial: equipando habilidad
            instruc = "SELECCIONA UNA RANURA con ←→ | ENTER: Confirmar | ESC: Cancelar"
            color_instruc = self.COLOR_TEXTO_SEL  # Amarillo para destacar
        elif self.panel_activo == "inventario":
            instruc = "FLECHAS: Navegar | ENTER: Equipar | ESC: Salir"
            color_instruc = self.COLOR_TEXTO
        elif self.panel_activo == "ranuras":
            instruc = "←→: Cambiar Ranura | ENTER: Desequipar | X: Desequipar | ESC: Salir"
            color_instruc = self.COLOR_TEXTO
        elif self.panel_activo == "boton_volver":
            instruc = "ENTER: Volver al Menú | FLECHAS: Navegar"
            color_instruc = self.COLOR_TEXTO
        elif self.panel_activo == "descripcion":
            instruc = "FLECHAS: Navegar entre paneles | ESC: Salir"
            color_instruc = self.COLOR_TEXTO
        else:
            instruc = "FLECHAS: Navegar | ESC: Salir"
            color_instruc = self.COLOR_TEXTO
        
        instruc_surf = self.fuente_pequeña.render(instruc, True, color_instruc)
        pantalla.blit(instruc_surf, (self.ANCHO // 2 - instruc_surf.get_width() // 2, y_instruc))

    # --- 14. POP-UP DE DETALLES ---
    def _draw_popup_detalles(self, pantalla):
        """Dibuja un pop-up grande con los detalles completos de la habilidad"""
        
        # Fondo oscuro semi-transparente
        overlay = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        pantalla.blit(overlay, (0, 0))
        
        # Caja del pop-up
        popup_ancho = 500
        popup_alto = 400
        popup_rect = pygame.Rect(0, 0, popup_ancho, popup_alto)
        popup_rect.center = (self.ANCHO // 2, self.ALTO // 2)
        
        pygame.draw.rect(pantalla, self.COLOR_CAJA, popup_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_TEXTO_SEL, popup_rect, 5, border_radius=self.UI_BORDER_RADIUS)
        
        # Contenido
        if not self.lista_inventario_habilidades:
            return
        
        hab_seleccionada = self.lista_inventario_habilidades[self.inventario_seleccionado_idx]
        
        y_offset = popup_rect.top + 20
        padding_x = 30
        max_ancho = popup_rect.width - padding_x * 2
        
        # Título
        titulo_surf = self.fuente_titulo.render("DETALLES DE HABILIDAD", True, self.COLOR_TEXTO_SEL)
        pantalla.blit(titulo_surf, (popup_rect.centerx - titulo_surf.get_width() // 2, y_offset))
        y_offset += 50
        
        # Nombre
        nombre = hab_seleccionada.get("nombre", "???")
        nombre_surf = self.fuente_opcion.render(nombre, True, self.COLOR_TEXTO)
        pantalla.blit(nombre_surf, (popup_rect.left + padding_x, y_offset))
        y_offset += 40
        
        # Datos
        datos = [
            f"Tipo: {hab_seleccionada.get('tipo', '???')}",
            f"Costo MP: {hab_seleccionada.get('costo_mp', 0)}",
            f"Poder: {hab_seleccionada.get('poder', 0)}",
            f"Alcance: {hab_seleccionada.get('alcance', '???')}",
            f"Efecto: {hab_seleccionada.get('efecto', 'Ninguno') or 'Ninguno'}",
        ]
        
        for dato in datos:
            dato_surf = self.fuente_datos.render(dato, True, self.COLOR_TEXTO)
            pantalla.blit(dato_surf, (popup_rect.left + padding_x, y_offset))
            y_offset += 30
        
        y_offset += 10
        
        # Descripción
        desc_titulo_surf = self.fuente_datos.render("Descripción:", True, self.COLOR_TEXTO_SEL)
        pantalla.blit(desc_titulo_surf, (popup_rect.left + padding_x, y_offset))
        y_offset += 30
        
        descripcion = hab_seleccionada.get("descripcion", "Sin descripción.")
        lineas_desc = self._wrap_text(descripcion, self.fuente_pequeña, max_ancho)
        
        for linea in lineas_desc:
            if y_offset + 25 > popup_rect.bottom - 40:
                break
            linea_surf = self.fuente_pequeña.render(linea, True, self.COLOR_TEXTO)
            pantalla.blit(linea_surf, (popup_rect.left + padding_x, y_offset))
            y_offset += 25
        
        # Instrucción de cerrar
        cerrar_surf = self.fuente_pequeña.render("[Presiona D o ESC para cerrar]", True, self.COLOR_TEXTO_SEL)
        pantalla.blit(cerrar_surf, (popup_rect.centerx - cerrar_surf.get_width() // 2, popup_rect.bottom - 30))
