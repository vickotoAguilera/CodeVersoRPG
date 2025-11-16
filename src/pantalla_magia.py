import pygame
import sys

# --- ¡"RECABLEADO" (MODIFICADO) BKN! (Paso 56.7) ---
# Este es el "Motor" (Engine) de UI para el sub-menú de Magia en la batalla.

class PantallaMagia:
    
    # --- 1. EL CONSTRUCTOR (¡"RECABLEADO" (MODIFICADO)!) ---
    # ¡Ahora "pilla" (recibe) el cursor BKN!
    def __init__(self, ancho_pantalla, alto_pantalla, heroe_actor, magia_db_completa, cursor_img_bkn):
        print(f"¡Abriendo Pantalla de Magia para {heroe_actor.nombre_clase}!")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        
        self.heroe_actor = heroe_actor
        self.magia_db = magia_db_completa
        
        # --- ¡NUEVO BKN! "Guardamos" (Almacenamos) el cursor (Paso 56.7) ---
        self.cursor_img = cursor_img_bkn
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_opcion = pygame.font.Font(None, 30) # "Cura", "Piro"
            self.fuente_datos = pygame.font.Font(None, 28) # "MP:", "Costo:"
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

        # --- Colores (Sin cambios) ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180) 
        self.COLOR_CAJA = (0, 0, 139) 
        self.COLOR_BORDE = (255, 255, 255) 
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_NO_MP = (150, 150, 150) 
        self.UI_BORDER_RADIUS = 12 

        # --- Geometría de las Cajas (Sin cambios) ---
        self.caja_desc_rect = pygame.Rect(30, 30, self.ANCHO - 60, 100)
        self.caja_mp_rect = pygame.Rect(30, self.caja_desc_rect.bottom + 15, 250, 60)
        self.caja_magia_rect = pygame.Rect(self.caja_mp_rect.right + 15, self.caja_desc_rect.bottom + 15, 
                                          self.ANCHO - self.caja_mp_rect.right - 15 - 30, 
                                          self.ALTO - self.caja_desc_rect.bottom - 15 - 30)


    # --- 2. BUILD LISTA (QUEDA 100% IGUAL) ---
    def _build_lista_opciones(self):
        """
        "Arma" (Construye) la lista de magias que mostraremos en el menú.
        "Pilla" (Lee) el inventario del héroe y "traduce" (busca) los datos
        en la "enciclopedia" (magia_db).
        """
        self.opciones_mostradas = []
        
        print(f"Magias que 'cacha' (sabe) {self.heroe_actor.nombre_clase}: {self.heroe_actor.magias}")
        
        for id_magia in self.heroe_actor.magias:
            magia_data = self.magia_db.get(id_magia)
            
            if magia_data:
                self.opciones_mostradas.append(magia_data)
            else:
                print(f"¡ADVERTENCIA! Héroe 'cacha' (sabe) '{id_magia}' pero no existe en magia_db.json")

        self.opciones_mostradas.append({
            "id_magia": "VOLVER", 
            "nombre": "Volver",
            "descripcion": "Vuelve al menú de batalla anterior.",
            "costo_mp": 0
        })

    # --- 3. EL UPDATE (QUEDA 100% IGUAL) ---
    def update(self, teclas):
        """Maneja el input del teclado para mover el cursor."""
        tiempo_actual = pygame.time.get_ticks()

        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            if teclas[pygame.K_DOWN]:
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones_mostradas)
                self.tiempo_ultimo_input = tiempo_actual
            elif teclas[pygame.K_UP]:
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_mostradas)
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
            id_opcion = opcion.get("id_magia", "VOLVER")

            if id_opcion == "VOLVER":
                print("¡Volviendo (Selección)!")
                return "volver"
            
            costo = opcion.get("costo_mp", 0)
            
            if self.heroe_actor.MP_actual >= costo:
                print(f"¡Acción seleccionada: {id_opcion}!")
                return {
                    "accion": "lanzar_magia", 
                    "magia_data": opcion 
                }
            else:
                print(f"¡No hay suficiente MP para {id_opcion}!")
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
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_mp_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_magia_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # 3. Dibujar los Bordes Blancos (Sin cambios)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_mp_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_magia_rect, 3, border_radius=self.UI_BORDER_RADIUS)

        # 4. Dibujar Contenido: Caja Descripción (Arriba) (Sin cambios)
        opcion_actual = self.opciones_mostradas[self.opcion_seleccionada]
        
        desc_texto = opcion_actual.get("descripcion", "...")
        desc_surf = self.fuente_desc.render(desc_texto, True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.y + 35))
        pantalla.blit(desc_surf, desc_rect)
        
        costo_texto = f"Costo: {opcion_actual.get('costo_mp', 0)} MP"
        costo_surf = self.fuente_datos.render(costo_texto, True, self.COLOR_TEXTO)
        costo_rect = costo_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.y + 65))
        pantalla.blit(costo_surf, costo_rect)

        # 5. Dibujar Contenido: Caja MP (Medio) (Sin cambios)
        mp_texto = f"MP: {self.heroe_actor.MP_actual} / {self.heroe_actor.MP_max}"
        mp_surf = self.fuente_datos.render(mp_texto, True, self.COLOR_TEXTO)
        mp_rect = mp_surf.get_rect(midleft=(self.caja_mp_rect.x + 20, self.caja_mp_rect.centery))
        pantalla.blit(mp_surf, mp_rect)
        
        # 6. Dibujar Contenido: Lista de Magias (Medio/Derecha) (¡"RECABLEADO" (MODIFICADO)!)
        padding_y_opciones = 15
        start_y_opciones = self.caja_magia_rect.y + 25
        
        for i, opcion_data in enumerate(self.opciones_mostradas):
            
            opcion_texto = opcion_data.get("nombre", "ERROR")
            costo_magia = opcion_data.get("costo_mp", 0)
            
            color_base = self.COLOR_TEXTO
            if self.heroe_actor.MP_actual < costo_magia and opcion_data.get("id_magia") != "VOLVER":
                color_base = self.COLOR_TEXTO_NO_MP 
            
            if i == self.opcion_seleccionada:
                color = self.COLOR_TEXTO_SEL
            else:
                color = color_base

            texto_surf = self.fuente_opcion.render(opcion_texto, True, color)
            
            pos_x = self.caja_magia_rect.x + 50
            pos_y = start_y_opciones + (i * (self.fuente_opcion.get_height() + padding_y_opciones))
            opcion_rect = texto_surf.get_rect(midleft=(pos_x, pos_y))
            
            # --- ¡"PEGA DE CIRUJANO" (PRECISIÓN) BKN! (Paso 56.7) ---
            if i == self.opcion_seleccionada:
                if self.cursor_img:
                    # ¡"Enchufamos" (Dibujamos) la Mano BKN!
                    cursor_rect = self.cursor_img.get_rect(midright=(opcion_rect.left - 5, opcion_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    # ¡"Enchufamos" (Dibujamos) el "fallback" (alternativa) BKN!
                    cursor_surf = self.fuente_opcion.render(">", True, color)
                    cursor_rect = cursor_surf.get_rect(midright=(opcion_rect.left - 10, opcion_rect.centery))
                    pantalla.blit(cursor_surf, cursor_rect)
            # --- FIN "PEGA DE CIRUJANO" (PRECISIÓN) ---
            
            pantalla.blit(texto_surf, opcion_rect)