import pygame
import sys

# --- (¡NUEVO ARCHIVO!) ---
# Esta es la pantalla de "Habilidades" (Magia) del menú de pausa.
# Muestra la lista de héroes a la izquierda y sus magias a la derecha.

class PantallaListaMagias:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, grupo_heroes, magia_db_completa, cursor_img):
        print("¡Abriendo Pantalla de Lista de Magias!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.grupo_heroes = grupo_heroes
        self.magia_db = magia_db_completa
        self.cursor_img = cursor_img
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 35) # "Habilidades"
            self.fuente_opcion = pygame.font.Font(None, 30) # "Piro", "Cloud"
            self.fuente_datos = pygame.font.Font(None, 28) # "HP:", "MP:"
            self.fuente_desc = pygame.font.Font(None, 26) # "Daña a un enemigo..."
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Control y Estados ---
        self.modo = "seleccion_heroe" # "seleccion_heroe" (izquierda) o "seleccion_magia" (derecha)
        
        self.heroe_seleccionado_idx = 0
        self.magia_seleccionada_idx = 0
        
        self.lista_magias_mostradas = []
        self._construir_lista_magias() # Llenar la lista por primera vez

        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Colores y Geometría ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_MP = (200, 200, 255) # Color para el costo de MP
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
        
        # 2. Panel de Magias (Derecha)
        self.panel_magias_rect = pygame.Rect(
            self.panel_heroes_rect.right + 20,
            self.panel_heroes_rect.y,
            self.caja_principal_rect.width - self.panel_heroes_rect.width - 60,
            self.panel_heroes_rect.height
        )
        
        # 3. Caja de Descripción (Arriba)
        self.caja_desc_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + 20,
            self.caja_principal_rect.width - 40,
            50
        )

    # --- 2. Lógica Interna ---
    def _construir_lista_magias(self):
        """Construye la lista de magias del héroe seleccionado."""
        self.lista_magias_mostradas = []
        
        heroe_actual = self.grupo_heroes[self.heroe_seleccionado_idx]
        
        for id_magia in heroe_actual.magias:
            magia_data = self.magia_db.get(id_magia)
            if magia_data:
                self.lista_magias_mostradas.append(magia_data)
        
        print(f"Magias de {heroe_actual.nombre_en_juego}: {len(self.lista_magias_mostradas)} hechizos.")
        # Asegurarse de que el cursor no quede fuera de rango
        self.magia_seleccionada_idx = 0

    # --- 3. EL UPDATE ---
    def update(self, teclas):
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # [MODO 1: Seleccionando Héroe (Izquierda)]
            if self.modo == "seleccion_heroe":
                num_heroes = len(self.grupo_heroes)
                
                if teclas[pygame.K_DOWN]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx + 1) % num_heroes
                    self._construir_lista_magias() # ¡Actualizar lista de magias!
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx - 1) % num_heroes
                    self._construir_lista_magias() # ¡Actualizar lista de magias!
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_RIGHT]:
                    self.modo = "seleccion_magia"
                    self.magia_seleccionada_idx = 0
                    self.tiempo_ultimo_input = tiempo_actual

            # [MODO 2: Seleccionando Magia (Derecha)]
            elif self.modo == "seleccion_magia":
                if not self.lista_magias_mostradas:
                    # Si no hay magias, volver al panel de héroes
                    if teclas[pygame.K_LEFT]:
                        self.modo = "seleccion_heroe"
                        self.tiempo_ultimo_input = tiempo_actual
                    return

                num_magias = len(self.lista_magias_mostradas)
                
                if teclas[pygame.K_DOWN]:
                    self.magia_seleccionada_idx = (self.magia_seleccionada_idx + 1) % num_magias
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]:
                    self.magia_seleccionada_idx = (self.magia_seleccionada_idx - 1) % num_magias
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_LEFT]:
                    self.modo = "seleccion_heroe"
                    self.tiempo_ultimo_input = tiempo_actual
        
        return None

    # --- 4. EL UPDATE_INPUT ---
    def update_input(self, tecla):
        
        if tecla == pygame.K_ESCAPE:
            if self.modo == "seleccion_magia":
                self.modo = "seleccion_heroe"
                return None
            elif self.modo == "seleccion_heroe":
                print("¡Cerrando Pantalla de Magias!")
                return "volver_al_menu"
        
        if tecla == pygame.K_RETURN:
            # (No hace nada por ahora, solo es para ver)
            if self.modo == "seleccion_heroe":
                self.modo = "seleccion_magia"
                return None
            elif self.modo == "seleccion_magia":
                # (En el futuro, podríamos seleccionar una magia para
                # asignarla a un acceso rápido, pero por ahora no hace nada)
                print("Viendo detalles de magia (próximamente).")
                return None
                
        return None

    # --- 5. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo" y las Cajas
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_principal_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_principal_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_heroes_rect, 1, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_magias_rect, 1, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 1, border_radius=self.UI_BORDER_RADIUS)

        # 3. Dibujar Panel Izquierdo (Lista de Héroes)
        start_x_heroe = self.panel_heroes_rect.x + 20
        start_y_heroe = self.panel_heroes_rect.y + 20
        line_height_heroe = 60 # Más espacio para HP/MP
        
        for i, heroe in enumerate(self.grupo_heroes):
            heroe_texto = f"{heroe.nombre_en_juego}"
            stats_texto_hp = f"HP {heroe.HP_actual}/{heroe.HP_max}"
            stats_texto_mp = f"MP {heroe.MP_actual}/{heroe.MP_max}"
            
            color_heroe = self.COLOR_TEXTO
            
            if i == self.heroe_seleccionado_idx and self.modo == "seleccion_heroe":
                color_heroe = self.COLOR_TEXTO_SEL
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(start_x_heroe - 5, start_y_heroe + (i * line_height_heroe) + 15))
                    pantalla.blit(self.cursor_img, cursor_rect)

            heroe_surf = self.fuente_opcion.render(heroe_texto, True, color_heroe)
            stats_hp_surf = self.fuente_datos.render(stats_texto_hp, True, color_heroe)
            stats_mp_surf = self.fuente_datos.render(stats_texto_mp, True, color_heroe)
            
            pantalla.blit(heroe_surf, (start_x_heroe, start_y_heroe + (i * line_height_heroe)))
            pantalla.blit(stats_hp_surf, (start_x_heroe + 100, start_y_heroe + (i * line_height_heroe)))
            pantalla.blit(stats_mp_surf, (start_x_heroe + 100, start_y_heroe + (i * line_height_heroe) + 20))

        # 4. Dibujar Panel Derecho (Lista de Magias)
        start_x_magia = self.panel_magias_rect.x + 20
        start_y_magia = self.panel_magias_rect.y + 20
        line_height_magia = 35
        
        if not self.lista_magias_mostradas:
            texto_surf = self.fuente_opcion.render("--- Sin Habilidades ---", True, self.COLOR_TEXTO_DESHABILITADO)
            pantalla.blit(texto_surf, (start_x_magia, start_y_magia))
        else:
            for i, magia_data in enumerate(self.lista_magias_mostradas):
                magia_texto = magia_data["nombre"]
                costo_texto = f"MP: {magia_data['costo_mp']}"
                
                color_magia = self.COLOR_TEXTO
                color_costo = self.COLOR_TEXTO_MP
                
                if i == self.magia_seleccionada_idx and self.modo == "seleccion_magia":
                    color_magia = self.COLOR_TEXTO_SEL
                    color_costo = self.COLOR_TEXTO_SEL
                    if self.cursor_img:
                        cursor_rect = self.cursor_img.get_rect(midright=(start_x_magia - 5, start_y_magia + (i * line_height_magia) + 10))
                        pantalla.blit(self.cursor_img, cursor_rect)

                magia_surf = self.fuente_opcion.render(magia_texto, True, color_magia)
                costo_surf = self.fuente_opcion.render(costo_texto, True, color_costo)
                
                pantalla.blit(magia_surf, (start_x_magia, start_y_magia + (i * line_height_magia)))
                pantalla.blit(costo_surf, (self.panel_magias_rect.right - costo_surf.get_width() - 20, start_y_magia + (i * line_height_magia)))


        # 5. Dibujar Panel de Descripción (Arriba)
        desc_texto = "Selecciona un héroe."
        if self.modo == "seleccion_magia" and self.lista_magias_mostradas:
            desc_texto = self.lista_magias_mostradas[self.magia_seleccionada_idx].get("descripcion", "...")
        elif self.modo == "seleccion_heroe":
            desc_texto = f"Viendo habilidades de {self.grupo_heroes[self.heroe_seleccionado_idx].nombre_en_juego}."
            
        desc_surf = self.fuente_desc.render(desc_texto, True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.centery))
        pantalla.blit(desc_surf, desc_rect)