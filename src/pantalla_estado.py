import pygame
import sys


# Esta es la pantalla de "Carta de Personaje"
# Muestra las estadísticas detalladas de un héroe específico.

class PantallaEstado:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, heroe_obj, cursor_img):
        print(f"¡Abriendo Pantalla de Estado para {heroe_obj.nombre_en_juego}!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.heroe = heroe_obj
        self.cursor_img = cursor_img # (Guardado para uso futuro)
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 40) # "Cloud - NV 1"
            self.fuente_stats = pygame.font.Font(None, 30) # "Fuerza:", "Defensa:"
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Temporizador de Animación (para el sprite) ---
        self.ultimo_update_anim = pygame.time.get_ticks()
        self.velocidad_anim = 200 # 200 ms la velocidad del sprite
        self.frame_anim_actual = 0
        
        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200

        # --- Colores y Geometría ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_STATS = (200, 200, 200) # Un color más suave para los nombres
        self.UI_BORDER_RADIUS = 12
        
        # 1. Caja Principal (Grande, en el centro)
        padding = 50
        self.caja_principal_rect = pygame.Rect(padding, padding, self.ANCHO - (padding * 2), self.ALTO - (padding * 2))
        
        # 2. Sub-Caja del Sprite (Izquierda)
        self.caja_sprite_rect = pygame.Rect(
            self.caja_principal_rect.x + 20, 
            self.caja_principal_rect.y + 20, 
            150, 
            150
        )
        
        # 3. Sub-Caja de Stats (Derecha)
        self.caja_stats_rect = pygame.Rect(
            self.caja_sprite_rect.right + 20, 
            self.caja_principal_rect.y + 20, 
            self.caja_principal_rect.width - self.caja_sprite_rect.width - 60, 
            self.caja_principal_rect.height - 40
        )

    # --- 2. EL UPDATE (Maneja la animación) ---
    def update(self, teclas):
        # Actualizar la animación del sprite
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_update_anim > self.velocidad_anim:
            self.ultimo_update_anim = tiempo_actual
            # Usamos 2 frames (0 y 1) para la animación de caminar
            self.frame_anim_actual = (self.frame_anim_actual + 1) % 2
        
        # (Por ahora no usa 'teclas', pero lo dejamos listo)
        return None

    # --- 3. EL UPDATE_INPUT (Maneja la salida) ---
    def update_input(self, tecla):
        if tecla == pygame.K_ESCAPE:
            print("¡Cerrando Pantalla de Estado!")
            return "volver_al_menu"
        return None

    # --- 4. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo"
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar la Caja Principal
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_principal_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_principal_rect, 3, border_radius=self.UI_BORDER_RADIUS)

        # 3. Dibujar Sprite Animado (en la caja_sprite_rect)
        try:
            frames_anim = self.heroe.animaciones["caminar_abajo"]
            if frames_anim:
                idx = self.frame_anim_actual % len(frames_anim)
                frame_img = frames_anim[idx]
                
                sprite_rect = frame_img.get_rect(center=self.caja_sprite_rect.center)
                pantalla.blit(frame_img, sprite_rect)
        except (AttributeError, KeyError, IndexError):
            pass # Si falla, simplemente no dibuja el sprite

        # 4. Dibujar Stats (en la caja_stats_rect)
        start_x = self.caja_stats_rect.x + 10
        start_y = self.caja_stats_rect.y + 10
        line_height = 30 # Espacio entre líneas
        
        # --- Título (Nombre y Nivel) ---
        titulo_txt = f"{self.heroe.nombre_en_juego}  -  NV {self.heroe.nivel}"
        titulo_surf = self.fuente_titulo.render(titulo_txt, True, self.COLOR_TEXTO)
        pantalla.blit(titulo_surf, (start_x, start_y))
        
        # Separador
        pygame.draw.line(pantalla, self.COLOR_BORDE, (start_x, start_y + 40), (self.caja_stats_rect.right - 10, start_y + 40), 1)
        
        base_y_stats = start_y + 60

        # --- ¡DISEÑO CORREGIDO! ---
        # Definimos las posiciones X para las 4 columnas (Label1, Value1, Label2, Value2)
        col_1_label_x = start_x
        col_1_value_x = start_x + 140   # (Más espacio para "Siguiente NV:")
        col_2_label_x = start_x + 280   # (Más espacio para el valor "100 / 100")
        col_2_value_x = col_2_label_x + 140 # (Más espacio para "Inteligencia:")

        # --- Columna 1: Stats Básicas ---
        stats_col_1 = [
            ("HP", f"{self.heroe.HP_actual} / {self.heroe.HP_max}"),
            ("MP", f"{self.heroe.MP_actual} / {self.heroe.MP_max}"),
            ("XP Actual", f"{self.heroe.experiencia_actual}"),
            ("Siguiente NV", f"{self.heroe.experiencia_siguiente_nivel}"),
        ]
        
        # --- Columna 2: Stats de Combate ---
        stats_col_2 = [
            ("Fuerza", f"{self.heroe.fuerza}"),
            ("Defensa", f"{self.heroe.defensa}"),
            ("Inteligencia", f"{self.heroe.inteligencia}"),
            ("Espíritu", f"{self.heroe.espiritu}"),
            ("Velocidad", f"{self.heroe.velocidad}"),
            ("Suerte", f"{self.heroe.suerte}"),
        ]

        # Dibujar Columna 1
        for i, (nombre, valor) in enumerate(stats_col_1):
            nombre_surf = self.fuente_stats.render(f"{nombre}:", True, self.COLOR_STATS)
            valor_surf = self.fuente_stats.render(valor, True, self.COLOR_TEXTO)
            
            pantalla.blit(nombre_surf, (col_1_label_x, base_y_stats + (i * line_height)))
            pantalla.blit(valor_surf, (col_1_value_x, base_y_stats + (i * line_height)))

        # Dibujar Columna 2
        for i, (nombre, valor) in enumerate(stats_col_2):
            nombre_surf = self.fuente_stats.render(f"{nombre}:", True, self.COLOR_STATS)
            valor_surf = self.fuente_stats.render(valor, True, self.COLOR_TEXTO)
            
            pantalla.blit(nombre_surf, (col_2_label_x, base_y_stats + (i * line_height)))
            pantalla.blit(valor_surf, (col_2_value_x, base_y_stats + (i * line_height)))

        # --- Sección de Equipo (Placeholder) ---
        base_y_equipo = base_y_stats + (len(stats_col_1) * line_height) + 20
        pygame.draw.line(pantalla, self.COLOR_BORDE, (start_x, base_y_equipo), (self.caja_stats_rect.right - 10, base_y_equipo), 1)

        equipo_titulo_surf = self.fuente_titulo.render("Equipo", True, self.COLOR_TEXTO)
        pantalla.blit(equipo_titulo_surf, (start_x, base_y_equipo + 10))
        
        equipo_placeholder_surf = self.fuente_stats.render("(Próximamente...)", True, self.COLOR_STATS)
        pantalla.blit(equipo_placeholder_surf, (start_x, base_y_equipo + 50))