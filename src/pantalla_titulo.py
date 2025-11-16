import pygame
import sys

class PantallaTitulo:
    # --- 1. EL CONSTRUCTOR (¡"RECABLEADO" (MODIFICADO)!) ---
    def __init__(self, ancho_pantalla, alto_pantalla, cursor_img_bkn): # ¡"Pilla" (Recibe) el cursor BKN!
        print(" Creando la pantalla de titulo!")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        
        # --- ¡NUEVO BKN! "Guardamos" (Almacenamos) el cursor (Paso 56.4) ---
        self.cursor_img = cursor_img_bkn
    
        # FUENTE PARA EL TEXTO
        try:
            pygame.font.init()
            self.fuente_titulo = pygame.font.Font(None, 80)# <---- fuente para el titulo
            self.fuente_menu = pygame.font.Font(None, 50)#<--- fuente para las opciones
        # --- (¡"PALANQUEO" (ERROR) "PARCHADO" (FIXED)!) ---
        except pygame.error as e: # (¡Era "erro" BKN!)
            print(f"ERROR al cargar la fuente {e}")
            pygame.quit() ; sys.exit()
        
        # opciones del menu
        self.opciones = ["Juego Nuevo", "Cargar Juego", "Salir"] # (¡"Fileteado" (Corregido) "juego Nuevo"!)
        self.opcion_seleccionada = 0
    
        # Coldown para el input 
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200 # en milisegundos
    
    # --- 2. EL UPDATE (QUEDA 100% IGUAL) ---
    def update(self, teclas):
        """
        Maneja el input del teclado para mover el cursor.
        Devuelve la acción a tomar (ej: "juego_nuevo") si se presiona Enter.
        """
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            #Mover cursor hacia abajo
            if teclas[pygame.K_DOWN]:
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
                self.tiempo_ultimo_input = tiempo_actual
            # mover el cursor hacia arriba 
            elif teclas[pygame.K_UP]:
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
                self.tiempo_ultimo_input = tiempo_actual
        return None 
    
    # --- 3. EL UPDATE_INPUT (QUEDA 100% IGUAL) ---
    def update_input(self, tecla):
        """
        Se llama desde main.py SOLO cuando se presiona una tecla.
        Maneja la selección (Enter).
        """
        if tecla == pygame.K_RETURN:# tecla enter
            if self.opcion_seleccionada == 0:
                print("Seleccionado 'Juego Nuevo'!")
                return "juego_nuevo"
            elif self.opcion_seleccionada == 1:
                print("Seleccionado 'Cargar Juego'!")
                return "cargar_juego" 
            elif self.opcion_seleccionada == 2:
                print("Seleccionado 'Salir'! ")
                return "salir"
        return None 
    
    # --- 4. EL DRAW (¡"RECABLEADO" (MODIFICADO)!) ---
    def draw(self, pantalla):
        
        pantalla.fill((0, 0, 0))
        
        # 1. Dibujar el Título del Juego (Sin cambios)
        texto_titulo_surf = self.fuente_titulo.render("Code Verso RPG", True, (255, 255, 255))
        titulo_rect = texto_titulo_surf.get_rect(center=(self.ANCHO // 2, int(self.ALTO * 0.4)))
        pantalla.blit(texto_titulo_surf, titulo_rect)
        
        # 2. Dibujar las Opciones del Menú
        for i, opcion_texto in enumerate(self.opciones):
            
            if i == self.opcion_seleccionada:
                color = (255, 255, 0) # Amarillo
            else:
                color = (255, 255, 255) # Blanco
            
            texto_opcion_surf = self.fuente_menu.render(opcion_texto, True, color)
            
            pos_x = self.ANCHO // 2
            pos_y = int(self.ALTO * 0.6) + (i * 60)
            
            opcion_rect = texto_opcion_surf.get_rect(center=(pos_x, pos_y))
            
            # --- ¡"PEGA DE CIRUJANO" (PRECISIÓN) BKN! (Paso 56.4) ---
            if i == self.opcion_seleccionada:
                # "Chequeamos" (Verificamos) si "pillamos" (cargamos) la imagen BKN
                if self.cursor_img:
                    # ¡"Enchufamos" (Dibujamos) la Mano BKN!
                    cursor_rect = self.cursor_img.get_rect(midright=(opcion_rect.left - 10, opcion_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    # ¡"Enchufamos" (Dibujamos) el "fallback" (alternativa) BKN!
                    cursor_surf = self.fuente_menu.render(">", True, color)
                    cursor_rect = cursor_surf.get_rect(midright=(opcion_rect.left - 20, opcion_rect.centery))
                    pantalla.blit(cursor_surf, cursor_rect)
            # --- FIN "PEGA DE CIRUJANO" (PRECISIÓN) ---
            
            pantalla.blit(texto_opcion_surf, opcion_rect)