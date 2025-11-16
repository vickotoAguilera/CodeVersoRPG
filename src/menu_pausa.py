import pygame
import sys
from src.game_data import traducir_nombre_mapa

class MenuPausa:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho_pantalla, alto_pantalla, cursor_img_bkn):
        print("¡Creando el Menú de Pausa (Estilo BKN)!")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        
        self.cursor_img = cursor_img_bkn
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_opcion = pygame.font.Font(None, 35) # "Items", "Guardar"
            self.fuente_datos = pygame.font.Font(None, 30) # "Oro:", "Tiempo:"
            self.fuente_desc = pygame.font.Font(None, 28) # "Guarda tu progreso..."
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}")
            pygame.quit(); sys.exit()

        # --- Opciones del Menú (Panel Izquierdo) ---
        self.opciones = [
            "Items", 
            "Habilidades", 
            "Equipo",
            "Estado", 
            "Guardar", 
            "Cargar",
            "Salir al Título"
        ]
        self.descripciones = [
            "Revisa tus objetos y consumibles.",
            "Mira tus habilidades y magias.",
            "Equipa tus armas y armaduras.",
            "Revisa las estadísticas detalladas del grupo.",
            "Guarda tu progreso en una ranura.",
            "Carga una partida desde una ranura.",
            "Vuelve a la pantalla de título. (No se guarda)"
        ]
        self.opcion_seleccionada = 0
        
        # --- Control de Foco ---
        self.modo = "opciones" # "opciones" (izquierda) o "heroes" (derecha)
        self.heroe_seleccionado_idx = 0 # Índice del héroe seleccionado
        self.proposito_foco_heroe = "estado" # "estado" o "equipo"
        
        # --- Sistema de Scroll para Héroes (Vertical) ---
        self.scroll_offset_heroes = 0  # Primer héroe visible
        self.heroes_visibles_max = 4   # Máximo de héroes visibles a la vez
        
        # --- Cooldown para el input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200
        
        # --- Temporizador para Animación de Sprites ---
        self.tiempo_ultimo_anim = pygame.time.get_ticks() 
        self.velocidad_anim = 800 
        self.frame_anim_actual = 0 

        # --- Colores del estilo ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180) 
        self.COLOR_CAJA = (0, 0, 139) 
        self.COLOR_BORDE = (255, 255, 255) 
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0) 
        self.UI_BORDER_RADIUS = 12 

        # --- Geometría de las 4 Cajas ---
        
        # 1. Caja Opciones (Izquierda) - Altura 430
        self.caja_opciones_rect = pygame.Rect(30, 30, 250, 400)
        
        # 2. Caja Estado (Abajo Izquierda)
        self.caja_estado_rect = pygame.Rect(30, self.caja_opciones_rect.bottom + 20, 250, self.ALTO - (self.caja_opciones_rect.bottom + 20) - 30)
        
        # 3. Caja Descripción (Abajo)
        self.caja_desc_rect = pygame.Rect(self.caja_opciones_rect.right + 20, self.caja_estado_rect.top, self.ANCHO - (self.caja_opciones_rect.right + 20) - 30, self.caja_estado_rect.height)
        
        # 4. Caja Detalles (Derecha)
        self.caja_detalles_rect = pygame.Rect(self.caja_opciones_rect.right + 20, 30, self.caja_desc_rect.width, self.ALTO - self.caja_desc_rect.height - 30 - 30)
        
        # --- Geometría Cajas de Héroes ---
        self.caja_heroe_rects = []
        caja_ancho = self.caja_detalles_rect.width - 40
        caja_alto = 110
        padding_y = 15
        start_x = self.caja_detalles_rect.left + 20
        start_y = self.caja_detalles_rect.top + 20
        
        for i in range(4):
            nueva_caja = pygame.Rect(
                start_x,
                start_y + (i * (caja_alto + padding_y)),
                caja_ancho,
                caja_alto
            )
            self.caja_heroe_rects.append(nueva_caja)

    # --- 2. EL UPDATE ---
    def update(self, teclas, grupo_heroes):
        
        tiempo_actual = pygame.time.get_ticks()
        
        # --- Lógica de Animación ---
        if tiempo_actual - self.tiempo_ultimo_anim > self.velocidad_anim:
            self.tiempo_ultimo_anim = tiempo_actual
            self.frame_anim_actual = (self.frame_anim_actual + 1) % 2

        # --- Lógica de Control de Foco ---
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:

            # [MODO 1: Controlando el panel de Opciones (Izquierda)]
            if self.modo == "opciones":
                if teclas[pygame.K_DOWN]:
                    self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]:
                    self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
                    self.tiempo_ultimo_input = tiempo_actual
            
            # [MODO 2: Controlando el panel de Héroes (Derecha)]
            elif self.modo == "heroes":
                num_heroes = len(grupo_heroes)
                
                if num_heroes > 0: 
                    if teclas[pygame.K_DOWN]:
                        self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx + 1) % num_heroes
                        
                        # 🔑 Ajustar scroll si el cursor sale del área visible (hacia abajo)
                        if self.heroe_seleccionado_idx >= self.scroll_offset_heroes + self.heroes_visibles_max:
                            self.scroll_offset_heroes = self.heroe_seleccionado_idx - self.heroes_visibles_max + 1
                        
                        self.tiempo_ultimo_input = tiempo_actual
                        
                    elif teclas[pygame.K_UP]:
                        self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx - 1) % num_heroes
                        
                        # 🔑 Ajustar scroll si el cursor sale del área visible (hacia arriba)
                        if self.heroe_seleccionado_idx < self.scroll_offset_heroes:
                            self.scroll_offset_heroes = self.heroe_seleccionado_idx
                        
                        self.tiempo_ultimo_input = tiempo_actual

        return None

    # --- 3. EL UPDATE_INPUT (¡LÓGICA CORREGIDA!) ---
    def update_input(self, tecla):
        
        # [ESCAPE: Salir o Volver]
        if tecla == pygame.K_ESCAPE:
            if self.modo == "heroes":
                print("¡Volviendo al panel de opciones!")
                self.modo = "opciones"
                return None 
            elif self.modo == "opciones":
                return "cerrar_menu" 

        # [ENTER: Seleccionar]
        if tecla == pygame.K_RETURN:
            
            # [MODO 1: Panel de Opciones (Izquierda)]
            if self.modo == "opciones":
                opcion = self.opciones[self.opcion_seleccionada]
                
                # --- ¡BLOQUE CORREGIDO! ---
                if opcion == "Items":
                    print("¡Abriendo menú de Items!")
                    return "abrir_items" # ¡NUEVA ACCIÓN!

                elif opcion == "Habilidades":
                    # --- ¡MODIFICADO! Sistema de Habilidades (Paso 7.16) ---
                    print("¡Cambiando foco a héroes (para HABILIDADES)!")
                    self.proposito_foco_heroe = "habilidades"
                    self.modo = "heroes"
                    self.heroe_seleccionado_idx = 0
                    return None

                elif opcion == "Equipo":
                    print("¡Cambiando foco a héroes (para EQUIPO)!")
                    self.proposito_foco_heroe = "equipo"
                    self.modo = "heroes"
                    self.heroe_seleccionado_idx = 0
                    return None 
                
                elif opcion == "Estado":
                    print("¡Cambiando foco a héroes (para ESTADO)!")
                    self.proposito_foco_heroe = "estado"
                    self.modo = "heroes"
                    self.heroe_seleccionado_idx = 0
                    return None
                
                elif opcion == "Guardar":
                    print("¡Abriendo menú de Guardar!")
                    return "abrir_guardar"
                
                elif opcion == "Cargar":
                    print("¡Abriendo menú de Cargar!")
                    return "abrir_cargar"

                elif opcion == "Salir al Título":
                    print("¡Saliendo al Título!")
                    return "salir_titulo"
                # --- FIN BLOQUE CORREGIDO ---

            # [MODO 2: Panel de Héroes (Derecha)]
            elif self.modo == "heroes":
                print(f"¡Seleccionado héroe índice {self.heroe_seleccionado_idx}!")
                
                if self.proposito_foco_heroe == "estado":
                    return {"accion": "ver_estado_heroe", "indice_heroe": self.heroe_seleccionado_idx}
                elif self.proposito_foco_heroe == "equipo":
                    return {"accion": "abrir_equipo_heroe", "indice_heroe": self.heroe_seleccionado_idx}
                # --- ¡NUEVO! Sistema de Habilidades (Paso 7.16) ---
                elif self.proposito_foco_heroe == "habilidades":
                    return {"accion": "abrir_habilidades_heroe", "indice_heroe": self.heroe_seleccionado_idx}
                
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
            linea_prueba = f"{linea_actual} {palabra}".strip()
            ancho_prueba = fuente.size(linea_prueba)[0]
            
            if ancho_prueba > max_ancho:
                lineas.append(linea_actual)
                linea_actual = palabra
            else:
                linea_actual = linea_prueba
        
        lineas.append(linea_actual)
        return lineas

    # --- 4. EL DRAW ---
    def draw(self, pantalla, grupo_heroes, tiempo_juego, nombre_mapa_actual): 
        
        # 1. Dibujar el "velo"
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar las 4 Cajas Azules
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_opciones_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_estado_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_desc_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_detalles_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # 3. Dibujar los Bordes Blancos
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_opciones_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_estado_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_detalles_rect, 3, border_radius=self.UI_BORDER_RADIUS)

        # 4. Dibujar Contenido: Opciones (Izquierda)
        padding_y_opciones = 20
        start_y_opciones = self.caja_opciones_rect.y + 30
        
        for i, opcion_texto in enumerate(self.opciones):
            
            if i == self.opcion_seleccionada and self.modo == "opciones":
                color = self.COLOR_TEXTO_SEL
            else:
                color = self.COLOR_TEXTO
            
            texto_surf = self.fuente_opcion.render(opcion_texto, True, color)
            
            pos_x = self.caja_opciones_rect.x + 50
            pos_y = start_y_opciones + (i * (self.fuente_opcion.get_height() + padding_y_opciones))
            opcion_rect = texto_surf.get_rect(midleft=(pos_x, pos_y))
            
            # --- Cursor de Opciones (Solo si modo == "opciones") ---
            if i == self.opcion_seleccionada and self.modo == "opciones":
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(opcion_rect.left - 5, opcion_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    cursor_surf = self.fuente_opcion.render(">", True, color)
                    cursor_rect = cursor_surf.get_rect(midright=(opcion_rect.left - 10, opcion_rect.centery))
                    pantalla.blit(cursor_surf, cursor_rect)
            
            pantalla.blit(texto_surf, opcion_rect)
            
        # 5. Dibujar Contenido: Estado (Abajo Izquierda)
        
        # 1. Formatear Tiempo
        segundos_totales = int(tiempo_juego)
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        tiempo_formateado = f"{horas:02}:{minutos:02}:{segundos:02}"
        
        # 2. Extraer Oro
        oro_lider = 0
        if grupo_heroes: 
            oro_lider = grupo_heroes[0].oro
            
        # 3. Traducir Mapa
        lugar_actual_str = f"Lugar: {traducir_nombre_mapa(nombre_mapa_actual)}"

        # 4. Crear Superficies de Texto
        tiempo_surf = self.fuente_datos.render(f"Tiempo: {tiempo_formateado}", True, self.COLOR_TEXTO)
        oro_surf = self.fuente_datos.render(f"Oro:    {oro_lider}", True, self.COLOR_TEXTO) 
        
        # --- ¡BLOQUE CORREGIDO CON WRAP! ---
        padding = 5 
        altura_fuente = self.fuente_datos.get_height()
        base_x = self.caja_estado_rect.x + 20
        base_y = self.caja_estado_rect.y + 15
        
        # 5. Dibujar Tiempo y Oro (Líneas 1 y 2)
        pantalla.blit(tiempo_surf, (base_x, base_y))
        pantalla.blit(oro_surf, (base_x, base_y + altura_fuente + padding))
        
        # 6. Dibujar Lugar (Línea 3, con wrap)
        max_ancho_lugar = self.caja_estado_rect.width - 40 # Ancho de caja con padding
        
        # Usamos la nueva función
        lineas_lugar = self._wrap_text(lugar_actual_str, self.fuente_datos, max_ancho_lugar)
        
        # Dibujamos cada línea del lugar
        lugar_y = base_y + (altura_fuente + padding) * 2
        for linea in lineas_lugar:
            lugar_surf = self.fuente_datos.render(linea, True, self.COLOR_TEXTO)
            pantalla.blit(lugar_surf, (base_x, lugar_y))
            lugar_y += altura_fuente # Mover a la siguiente línea

        # 6. Dibujar Contenido: Descripción (Abajo)
        desc_texto_actual = ""
        if self.modo == "opciones":
            desc_texto_actual = self.descripciones[self.opcion_seleccionada]
        elif self.modo == "heroes" and len(grupo_heroes) > 0:
             heroe_actual = grupo_heroes[self.heroe_seleccionado_idx]
             desc_texto_actual = f"{heroe_actual.nombre_en_juego} - NV {heroe_actual.nivel}. Presiona ENTER para ver {self.proposito_foco_heroe}."
        
        desc_surf = self.fuente_desc.render(desc_texto_actual, True, self.COLOR_TEXTO)
        desc_rect = desc_surf.get_rect(midleft=(self.caja_desc_rect.x + 20, self.caja_desc_rect.centery))
        pantalla.blit(desc_surf, desc_rect)
        
        # 7. Dibujar Contenido: Detalles (Derecha) - CON SCROLL
        
        # 🔑 Calcular héroes visibles
        total_heroes = len(grupo_heroes)
        heroes_fin = min(self.scroll_offset_heroes + self.heroes_visibles_max, total_heroes)
        heroes_visibles = grupo_heroes[self.scroll_offset_heroes:heroes_fin]
        
        for idx_visual, heroe in enumerate(heroes_visibles):
            idx_real = self.scroll_offset_heroes + idx_visual
            
            if idx_visual >= len(self.caja_heroe_rects): 
                break
                
            caja_rect = self.caja_heroe_rects[idx_visual]
            
            # --- Cursor de Héroes (Solo si modo == "heroes" y es el seleccionado) ---
            if self.modo == "heroes" and idx_real == self.heroe_seleccionado_idx:
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(caja_rect.left - 5, caja_rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    cursor_surf = self.fuente_opcion.render(">", True, self.COLOR_TEXTO_SEL)
                    cursor_rect = cursor_surf.get_rect(midright=(caja_rect.left - 10, caja_rect.centery))
                    pantalla.blit(cursor_surf, cursor_rect)
            
            # 1. Dibujar Sprite Animado
            try:
                frames_anim = heroe.animaciones["caminar_abajo"]
                if frames_anim: 
                    idx = self.frame_anim_actual % len(frames_anim)
                    frame_img = frames_anim[idx]
                    sprite_pos_x = caja_rect.left + 35
                    sprite_pos_y = caja_rect.centery
                    sprite_rect = frame_img.get_rect(center=(sprite_pos_x, sprite_pos_y))
                    pantalla.blit(frame_img, sprite_rect)
            except (AttributeError, KeyError, IndexError):
                pass 

            # 2. Dibujar Texto (Nombre y Nivel)
            nombre_surf = self.fuente_datos.render(heroe.nombre_en_juego, True, self.COLOR_TEXTO)
            nivel_surf = self.fuente_datos.render(f"NV {heroe.nivel}", True, self.COLOR_TEXTO)
            
            text_x = caja_rect.left + 80 
            
            pantalla.blit(nombre_surf, (text_x, caja_rect.top + 5))
            pantalla.blit(nivel_surf, (caja_rect.right - nivel_surf.get_width() - 15, caja_rect.top + 5))

            # 3. Dibujar Barras y Texto (Diseño limpio)
            largo_barra = 180 
            barra_x = text_x + 50 
            numeros_x = barra_x + largo_barra + 5 
            
            # --- HP ---
            hp_y = caja_rect.top + 32
            hp_texto_surf = self.fuente_datos.render(f"HP", True, self.COLOR_TEXTO)
            hp_num_surf = self.fuente_datos.render(f"{heroe.HP_actual}/{heroe.HP_max}", True, self.COLOR_TEXTO)
            
            pantalla.blit(hp_texto_surf, (text_x, hp_y))
            porc_hp = heroe.HP_actual / heroe.HP_max
            pygame.draw.rect(pantalla, (50, 0, 0), (barra_x, hp_y + 8, largo_barra, 8), border_radius=4)
            pygame.draw.rect(pantalla, (0, 200, 0), (barra_x, hp_y + 8, largo_barra * porc_hp, 8), border_radius=4)
            pantalla.blit(hp_num_surf, (numeros_x, hp_y))

            # --- MP ---
            mp_y = caja_rect.top + 57
            mp_texto_surf = self.fuente_datos.render(f"MP", True, self.COLOR_TEXTO)
            mp_num_surf = self.fuente_datos.render(f"{heroe.MP_actual}/{heroe.MP_max}", True, self.COLOR_TEXTO)
            
            pantalla.blit(mp_texto_surf, (text_x, mp_y))
            porc_mp = 1.0 if heroe.MP_max == 0 else (heroe.MP_actual / heroe.MP_max)
            pygame.draw.rect(pantalla, (0, 0, 50), (barra_x, mp_y + 8, largo_barra, 8), border_radius=4)
            pygame.draw.rect(pantalla, (0, 100, 200), (barra_x, mp_y + 8, largo_barra * porc_mp, 8), border_radius=4)
            pantalla.blit(mp_num_surf, (numeros_x, mp_y))

            # --- XP ---
            xp_y = caja_rect.top + 82
            xp_texto_surf = self.fuente_datos.render(f"XP", True, self.COLOR_TEXTO)
            xp_num_surf = self.fuente_datos.render(f"{heroe.experiencia_actual}/{heroe.experiencia_siguiente_nivel}", True, self.COLOR_TEXTO)
            
            pantalla.blit(xp_texto_surf, (text_x, xp_y))
            porc_xp = heroe.experiencia_actual / heroe.experiencia_siguiente_nivel
            pygame.draw.rect(pantalla, (50, 50, 0), (barra_x, xp_y + 8, largo_barra, 8), border_radius=4)
            pygame.draw.rect(pantalla, (200, 200, 0), (barra_x, xp_y + 8, largo_barra * porc_xp, 8), border_radius=4)
            pantalla.blit(xp_num_surf, (numeros_x, xp_y))
        
        # 8. Dibujar Scrollbar Vertical para Héroes (si hay más de 4)
        if total_heroes > self.heroes_visibles_max:
            scrollbar_x = self.caja_detalles_rect.right - 10
            scrollbar_y = self.caja_detalles_rect.y + 10
            scrollbar_ancho = 6
            scrollbar_altura = self.caja_detalles_rect.height - 20
            
            # Barra de fondo
            pygame.draw.rect(pantalla, (50, 50, 100),
                           (scrollbar_x, scrollbar_y, scrollbar_ancho, scrollbar_altura),
                           border_radius=3)
            
            # Calcular tamaño y posición del thumb
            thumb_altura = max(15, int((self.heroes_visibles_max / total_heroes) * scrollbar_altura))
            thumb_pos_max = scrollbar_altura - thumb_altura
            scroll_ratio = self.scroll_offset_heroes / (total_heroes - self.heroes_visibles_max)
            thumb_y = scrollbar_y + int(scroll_ratio * thumb_pos_max)
            
            # Dibujar thumb
            COLOR_SCROLLBAR = (100, 100, 255)
            pygame.draw.rect(pantalla, COLOR_SCROLLBAR,
                           (scrollbar_x, thumb_y, scrollbar_ancho, thumb_altura),
                           border_radius=3)