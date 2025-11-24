import pygame
from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento
import sys
# (Necesitaremos esto para el futuro, para dibujar el sprite)
from src.game_data import traducir_nombre_mapa 

# --- (¡NUEVO ARCHIVO!) ---
# Esta pantalla gestiona el flujo de "post-batalla".
# Muestra los "Level Up" (Modo A) y luego las "Recompensas" (Modo B).

class PantallaVictoria:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, cursor_img, grupo_heroes, heroes_que_subieron_stats, total_xp, total_oro):
        print("¡Creando Pantalla de Victoria!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.cursor_img = cursor_img
        
        # Datos de la batalla
        self.grupo_heroes = grupo_heroes
        self.heroes_que_subieron = heroes_que_subieron_stats # ¡Importante!
        self.total_xp_ganada = total_xp
        self.total_oro_ganado = total_oro
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 40) # "¡VICTORIA!"
            self.fuente_subtitulo = pygame.font.Font(None, 35) # "Recompensas"
            self.fuente_stats = pygame.font.Font(None, 30) # "Fuerza:", "Defensa:"
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Estados y Flujo ---
        self.heroe_actual_idx = 0 # Índice para la lista heroes_que_subieron
        
        if self.heroes_que_subieron:
            self.modo = "level_up" # Empezar en Modo A
            print(f"Modo Victoria: LEVEL UP (Mostrando Héroe {self.heroe_actual_idx})")
        else:
            self.modo = "recompensas" # Empezar en Modo B
            print("Modo Victoria: RECOMPENSAS (Nadie subió de nivel)")

        # --- Temporizador de Animación (para el sprite) ---
        self.ultimo_update_anim = pygame.time.get_ticks()
        self.velocidad_anim = 400
        self.frame_anim_actual = 0
        
        # --- Colores y Geometría (Basado en menu_pausa.py) ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_STATS_NUEVO = (0, 255, 0) # Verde para stats
        self.COLOR_TEXTO_FLECHA = (255, 255, 0) # Amarillo
        self.UI_BORDER_RADIUS = 12
        
        # 1. Caja Opciones (Izquierda) - Mostrará XP/Oro
        self.caja_opciones_rect = pygame.Rect(30, 30, 250, 430)
        
        # 2. Caja Estado (Abajo Izquierda) - Título "VICTORIA"
        self.caja_estado_rect = pygame.Rect(30, self.caja_opciones_rect.bottom + 20, 250, self.ALTO - (self.caja_opciones_rect.bottom + 20) - 30)
        
        # 3. Caja Descripción (Abajo) - "Presiona ENTER"
        self.caja_desc_rect = pygame.Rect(self.caja_opciones_rect.right + 20, self.caja_estado_rect.top, self.ANCHO - (self.caja_opciones_rect.right + 20) - 30, self.caja_estado_rect.height)
        
        # 4. Caja Detalles (Derecha) - Mostrará los "Level Up"
        self.caja_detalles_rect = pygame.Rect(self.caja_opciones_rect.right + 20, 30, self.caja_desc_rect.width, self.ALTO - self.caja_desc_rect.height - 30 - 30)

    # --- 2. EL UPDATE (Maneja la animación) ---
    def update(self, teclas):
        # Actualizar la animación del sprite
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_update_anim > self.velocidad_anim:
            self.ultimo_update_anim = tiempo_actual
            self.frame_anim_actual = (self.frame_anim_actual + 1) % 2
        
        return None

    # --- 3. EL UPDATE_INPUT (Maneja el flujo de ENTER) ---
    def update_input(self, tecla):
        
        if tecla == pygame.K_RETURN:
            
            if self.modo == "level_up":
                # Avanzar al siguiente héroe que subió de nivel
                self.heroe_actual_idx += 1
                
                # Si ya mostramos a todos los que subieron...
                if self.heroe_actual_idx >= len(self.heroes_que_subieron):
                    print("Modo Victoria: Cambiando a RECOMPENSAS")
                    self.modo = "recompensas"
                else:
                    print(f"Modo Victoria: LEVEL UP (Mostrando Héroe {self.heroe_actual_idx})")
                
                return None
            
            elif self.modo == "recompensas":
                # Si ya estamos en recompensas, ENTER cierra la pantalla
                print("¡Cerrando Pantalla de Victoria!")
                return "cerrar_pantalla"
                
        return None

    # --- 4. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo"
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar las 4 Cajas con efecto glassmorphism
        dibujar_ventana_glass(pantalla, self.caja_opciones_rect, "Recompensas", 
                             obtener_color_acento("victoria"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_estado_rect, "Victoria", 
                             obtener_color_acento("victoria"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_desc_rect, "Instrucciones", 
                             obtener_color_acento("victoria"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_detalles_rect, "Detalles", 
                             obtener_color_acento("victoria"), alpha=230)

        # 4. Dibujar Contenido: Título (Abajo Izquierda)
        titulo_surf = self.fuente_titulo.render("¡VICTORIA!", True, self.COLOR_TEXTO_FLECHA)
        titulo_rect = titulo_surf.get_rect(center=self.caja_estado_rect.center)
        pantalla.blit(titulo_surf, titulo_rect)
        
        # 5. Dibujar Contenido: Descripción (Abajo)
        desc_surf = self.fuente_stats.render("Presiona ENTER para continuar...", True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(center=self.caja_desc_rect.center)
        pantalla.blit(desc_surf, desc_rect)

        # 6. Dibujar Contenido: Panel Izquierdo (Recompensas)
        # (Este panel SIEMPRE muestra las recompensas totales)
        start_x_izq = self.caja_opciones_rect.x + 20
        start_y_izq = self.caja_opciones_rect.y + 20
        line_height_izq = 35
        
        titulo_recomp_surf = self.fuente_subtitulo.render("Recompensas", True, self.COLOR_TEXTO)
        pantalla.blit(titulo_recomp_surf, (start_x_izq, start_y_izq))
        
        pygame.draw.line(pantalla, self.COLOR_BORDE, (start_x_izq, start_y_izq + 35), (self.caja_opciones_rect.right - 20, start_y_izq + 35), 1)

        xp_surf = self.fuente_stats.render(f"XP Ganada:", True, self.COLOR_TEXTO)
        xp_val_surf = self.fuente_stats.render(f"{self.total_xp_ganada}", True, self.COLOR_TEXTO_STATS_NUEVO)
        
        oro_surf = self.fuente_stats.render(f"Oro Ganado:", True, self.COLOR_TEXTO)
        oro_val_surf = self.fuente_stats.render(f"{self.total_oro_ganado}", True, self.COLOR_TEXTO_STATS_NUEVO)

        pantalla.blit(xp_surf, (start_x_izq, start_y_izq + 50))
        pantalla.blit(xp_val_surf, (start_x_izq + 130, start_y_izq + 50))
        
        pantalla.blit(oro_surf, (start_x_izq, start_y_izq + 50 + line_height_izq))
        pantalla.blit(oro_val_surf, (start_x_izq + 130, start_y_izq + 50 + line_height_izq))

        # (Aquí podríamos dibujar los "Items Obtenidos" en el futuro)

        
        # 7. Dibujar Contenido: Panel Derecho (Detalles)
        
        start_x_der = self.caja_detalles_rect.x + 20
        start_y_der = self.caja_detalles_rect.y + 20
        line_height_der = 30
        
        # [MODO A: LEVEL UP] (¡BLOQUE CORREGIDO!)
        if self.modo == "level_up":
            # Obtenemos la información del héroe que estamos mostrando
            heroe_info = self.heroes_que_subieron[self.heroe_actual_idx]
            heroe_obj = heroe_info["heroe"]
            stats_antes = heroe_info["stats_antes"]
            
            # --- 1. Título (Se queda arriba) ---
            titulo_der_txt = f"¡{heroe_obj.nombre_en_juego} subió al Nivel {heroe_obj.nivel}!"
            titulo_der_surf = self.fuente_subtitulo.render(titulo_der_txt, True, self.COLOR_TEXTO_FLECHA)
            titulo_der_rect = titulo_der_surf.get_rect(centerx=self.caja_detalles_rect.centerx, y=start_y_der)
            pantalla.blit(titulo_der_surf, titulo_der_rect)
            
            # --- 2. Sprite Animado (¡Y CORREGIDA!) ---
            # (Movemos el sprite y las stats más abajo para dar espacio al título)
            base_y_contenido = self.caja_detalles_rect.top + 100 

            try:
                frames_anim = heroe_obj.animaciones["caminar_abajo"]
                if frames_anim:
                    idx = self.frame_anim_actual % len(frames_anim)
                    frame_img = frames_anim[idx]
                    
                    sprite_pos_x = self.caja_detalles_rect.left + 80
                    # (Centramos el sprite verticalmente en el espacio restante)
                    sprite_pos_y = base_y_contenido + 60 
                    sprite_rect = frame_img.get_rect(center=(sprite_pos_x, sprite_pos_y))
                    pantalla.blit(frame_img, sprite_rect)
            except (AttributeError, KeyError, IndexError):
                pass 
            
            # --- 3. Lista de Stats (¡Y CORREGIDA!) ---
            stats_base_x = self.caja_detalles_rect.left + 180
            stats_base_y = base_y_contenido # (Usamos la nueva Y base)
            
            stats_a_mostrar = [
                ("HP Máx", stats_antes["hp_max"], heroe_obj.HP_max),
                ("MP Máx", stats_antes["mp_max"], heroe_obj.MP_max),
                ("Fuerza", stats_antes["fuerza"], heroe_obj.fuerza),
                ("Defensa", stats_antes["defensa"], heroe_obj.defensa),
                ("Inteligencia", stats_antes["inteligencia"], heroe_obj.inteligencia),
                ("Espíritu", stats_antes["espiritu"], heroe_obj.espiritu),
            ]
            
            # (Usamos el caracter '^' que sí existe en la fuente)
            flecha_surf = self.fuente_stats.render("^", True, self.COLOR_TEXTO_FLECHA)

            for i, (nombre, valor_viejo, valor_nuevo) in enumerate(stats_a_mostrar):
                y_pos_stat = stats_base_y + (i * line_height_der)
                
                # Dibujar Nombre (ej: "Fuerza:")
                nombre_surf = self.fuente_stats.render(f"{nombre}:", True, self.COLOR_TEXTO)
                pantalla.blit(nombre_surf, (stats_base_x, y_pos_stat))
                
                # Dibujar Valor Viejo (ej: "25")
                valor_viejo_surf = self.fuente_stats.render(f"{valor_viejo}", True, self.COLOR_TEXTO)
                pantalla.blit(valor_viejo_surf, (stats_base_x + 140, y_pos_stat))
                
                # Dibujar Flecha "-->"
                flecha_simple_surf = self.fuente_stats.render("-->", True, self.COLOR_TEXTO)
                pantalla.blit(flecha_simple_surf, (stats_base_x + 180, y_pos_stat))
                
                # Dibujar Valor Nuevo (ej: "28")
                valor_nuevo_surf = self.fuente_stats.render(f"{valor_nuevo}", True, self.COLOR_TEXTO_STATS_NUEVO)
                pantalla.blit(valor_nuevo_surf, (stats_base_x + 230, y_pos_stat))
                
                # Dibujar Flecha Arriba "^" (solo si cambió)
                if valor_nuevo > valor_viejo:
                    pantalla.blit(flecha_surf, (stats_base_x + 270, y_pos_stat))


        # [MODO B: RECOMPENSAS]
        elif self.modo == "recompensas":
            # Si nadie subió de nivel, mostramos un resumen
            
            # 1. Dibujar Título
            titulo_der_txt = "Resumen de la Batalla"
            titulo_der_surf = self.fuente_subtitulo.render(titulo_der_txt, True, self.COLOR_TEXTO)
            titulo_der_rect = titulo_der_surf.get_rect(centerx=self.caja_detalles_rect.centerx, y=start_y_der)
            pantalla.blit(titulo_der_surf, titulo_der_rect)
            
            # --- ¡CORREGIDO! ---
            # 2. Dibujar Texto (¡Ahora se dibuja DEBAJO del título!)
            placeholder_surf = self.fuente_stats.render("¡Grupo listo para continuar!", True, self.COLOR_TEXTO)
            
            # Lo centramos en el panel, pero usando una Y más baja
            placeholder_rect = placeholder_surf.get_rect(
                centerx=self.caja_detalles_rect.centerx, 
                centery=self.caja_detalles_rect.centery
            )
            pantalla.blit(placeholder_surf, placeholder_rect)
        
        
        