import pygame
import sys

# Pantalla de "Habilidades" para batalla
# Muestra la lista de héroes a la izquierda y sus habilidades activas a la derecha.

class PantallaListaHabilidades:
    
    # --- 1. EL CONSTRUCTOR ---
    def __init__(self, ancho, alto, heroe_actual, habilidades_db_completa, cursor_img):
        print(f"¡Abriendo Pantalla de Habilidades para {heroe_actual.nombre_en_juego}!")
        self.ANCHO = ancho
        self.ALTO = alto
        self.heroe = heroe_actual  # Solo un héroe
        self.habilidades_db = habilidades_db_completa
        self.cursor_img = cursor_img
        
        # --- Fuentes ---
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 35)
            self.fuente_opcion = pygame.font.Font(None, 30)
            self.fuente_datos = pygame.font.Font(None, 28)
            self.fuente_desc = pygame.font.Font(None, 22)  # Más pequeña para más texto
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Lógica de Control y Estados ---
        self.modo = "seleccion_habilidad"  # Solo modo de selección de habilidad
        
        self.habilidad_seleccionada_idx = 0
        self.scroll_lista = 0  # Para scroll en la lista de habilidades
        
        self.lista_habilidades_mostradas = []
        self._construir_lista_habilidades() # Llenar la lista por primera vez

        # --- Cooldown de Input ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 150

        # --- Colores y Geometría ---
        self.COLOR_FONDO_VELO = (0, 0, 0, 180)
        self.COLOR_CAJA = (0, 0, 139)
        self.COLOR_BORDE = (255, 255, 255)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_TEXTO_MP = (200, 200, 255)
        self.COLOR_TEXTO_DESHABILITADO = (100, 100, 100)
        self.COLOR_SCROLLBAR = (150, 150, 150)
        self.COLOR_SCROLLBAR_THUMB = (255, 255, 0)
        self.UI_BORDER_RADIUS = 12
        
        # Panel centrado para lista de habilidades (tamaño más pequeño)
        panel_ancho = 700
        panel_alto = 400
        panel_x = (self.ANCHO - panel_ancho) // 2
        panel_y = self.ALTO - panel_alto - 100  # Justo arriba del panel de comandos
        
        self.caja_principal_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)
        
        # Panel de habilidades ocupa todo el espacio con margen para scrollbar
        self.panel_habilidades_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + 60,
            self.caja_principal_rect.width - 60,  # Espacio para scrollbar
            self.caja_principal_rect.height - 130
        )
        
        # Área de scrollbar (barra vertical a la derecha)
        self.scrollbar_rect = pygame.Rect(
            self.panel_habilidades_rect.right + 5,
            self.panel_habilidades_rect.y,
            15,
            self.panel_habilidades_rect.height
        )
        
        # Caja de título/héroe (Arriba)
        self.caja_titulo_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + 10,
            self.caja_principal_rect.width - 40,
            40
        )
        
        # Botón "VOLVER" en la parte inferior
        self.boton_volver_rect = pygame.Rect(
            self.caja_principal_rect.x + 20,
            self.caja_principal_rect.y + self.caja_principal_rect.height - 50,
            self.caja_principal_rect.width - 40,
            40
        )
        self.boton_volver_seleccionado = False
        
        # Parámetros de visualización
        self.max_habilidades_visibles = 3  # Mostrar 3 habilidades a la vez

    # --- 2. Lógica Interna ---
    def _construir_lista_habilidades(self):
        """Construye la lista de habilidades del héroe."""
        self.lista_habilidades_mostradas = []
        
        # Obtener habilidades activas (las que están equipadas)
        for id_habilidad in self.heroe.habilidades_activas:
            if id_habilidad:  # Verificar que no sea None
                habilidad_data = self.habilidades_db.get(id_habilidad)
                if habilidad_data:
                    self.lista_habilidades_mostradas.append(habilidad_data)
        
        print(f"Habilidades de {self.heroe.nombre_en_juego}: {len(self.lista_habilidades_mostradas)} habilidades.")
        # Asegurarse de que el cursor no quede fuera de rango
        if self.habilidad_seleccionada_idx >= len(self.lista_habilidades_mostradas):
            self.habilidad_seleccionada_idx = max(0, len(self.lista_habilidades_mostradas) - 1)
        self.scroll_lista = 0
        
    def _dividir_texto_en_lineas(self, texto, ancho_maximo):
        """Divide un texto largo en líneas que caben en el ancho dado."""
        palabras = texto.split(' ')
        lineas = []
        linea_actual = ""
        
        for palabra in palabras:
            # Probar si la palabra cabe en la línea actual
            prueba = linea_actual + " " + palabra if linea_actual else palabra
            ancho_prueba = self.fuente_desc.size(prueba)[0]
            
            if ancho_prueba <= ancho_maximo:
                linea_actual = prueba
            else:
                # No cabe, guardar línea actual y empezar nueva
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra
        
        # Agregar la última línea
        if linea_actual:
            lineas.append(linea_actual)
            
        return lineas

    # --- 3. EL UPDATE ---
    def update(self, teclas):
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            
            # Navegar entre habilidades y botón volver
            if teclas[pygame.K_DOWN]:
                if self.boton_volver_seleccionado:
                    # Ya estamos en el botón, no hacer nada
                    pass
                else:
                    if not self.lista_habilidades_mostradas:
                        self.boton_volver_seleccionado = True
                    else:
                        num_habilidades = len(self.lista_habilidades_mostradas)
                        if self.habilidad_seleccionada_idx >= num_habilidades - 1:
                            # Llegamos al final, ir al botón
                            self.boton_volver_seleccionado = True
                        else:
                            self.habilidad_seleccionada_idx += 1
                            # Ajustar scroll si es necesario
                            if self.habilidad_seleccionada_idx >= self.scroll_lista + self.max_habilidades_visibles:
                                self.scroll_lista = self.habilidad_seleccionada_idx - self.max_habilidades_visibles + 1
                self.tiempo_ultimo_input = tiempo_actual
                
            elif teclas[pygame.K_UP]:
                if self.boton_volver_seleccionado:
                    # Volver a las habilidades
                    self.boton_volver_seleccionado = False
                    if self.lista_habilidades_mostradas:
                        self.habilidad_seleccionada_idx = len(self.lista_habilidades_mostradas) - 1
                        # Ajustar scroll para mostrar el último elemento
                        max_scroll = max(0, len(self.lista_habilidades_mostradas) - self.max_habilidades_visibles)
                        self.scroll_lista = max_scroll
                else:
                    if self.lista_habilidades_mostradas and self.habilidad_seleccionada_idx > 0:
                        self.habilidad_seleccionada_idx -= 1
                        # Ajustar scroll si es necesario
                        if self.habilidad_seleccionada_idx < self.scroll_lista:
                            self.scroll_lista = self.habilidad_seleccionada_idx
                self.tiempo_ultimo_input = tiempo_actual
        
        return None

    # --- 4. EL UPDATE_INPUT ---
    def update_input(self, tecla):
        
        if tecla == pygame.K_ESCAPE:
            print("¡Cerrando Pantalla de Habilidades!")
            return "cerrar"
        
        if tecla == pygame.K_RETURN:
            # Si el botón volver está seleccionado
            if self.boton_volver_seleccionado:
                print("¡Volviendo al menú de batalla!")
                return "cerrar"
            
            # Si hay habilidades y se selecciona una
            if self.lista_habilidades_mostradas:
                habilidad_seleccionada = self.lista_habilidades_mostradas[self.habilidad_seleccionada_idx]
                
                # Verificar si tiene suficiente MP
                if self.heroe.MP_actual < habilidad_seleccionada['costo_mp']:
                    print(f"¡{self.heroe.nombre_en_juego} no tiene suficiente MP!")
                    return None
                
                print(f"¡{self.heroe.nombre_en_juego} usará: {habilidad_seleccionada['nombre']}!")
                
                return {
                    "accion": "usar_habilidad",
                    "heroe": self.heroe,
                    "habilidad": habilidad_seleccionada
                }
                
        return None

    # --- 5. EL DRAW ---
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo" y la Caja Principal
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_principal_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_principal_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_habilidades_rect, 1, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_titulo_rect, 1, border_radius=self.UI_BORDER_RADIUS)

        # 2. Dibujar Título con nombre del héroe
        titulo_texto = f"Habilidades - {self.heroe.nombre_en_juego}"
        titulo_surf = self.fuente_titulo.render(titulo_texto, True, self.COLOR_TEXTO_SEL)
        titulo_rect = titulo_surf.get_rect(center=self.caja_titulo_rect.center)
        pantalla.blit(titulo_surf, titulo_rect)

        # 3. Dibujar Lista de Habilidades con scroll
        if not self.lista_habilidades_mostradas:
            texto_surf = self.fuente_opcion.render("--- Sin Habilidades ---", True, self.COLOR_TEXTO_DESHABILITADO)
            texto_rect = texto_surf.get_rect(center=self.panel_habilidades_rect.center)
            pantalla.blit(texto_surf, texto_rect)
        else:
            # Crear una superficie para el área de habilidades (para recortar)
            habilidades_surface = pygame.Surface((self.panel_habilidades_rect.width, self.panel_habilidades_rect.height))
            habilidades_surface.fill(self.COLOR_CAJA)
            
            start_x_habilidad = 20
            start_y_habilidad = 10
            line_height = 80  # Altura por habilidad (nombre + descripción)
            
            # Calcular cuántas habilidades mostrar
            inicio_idx = self.scroll_lista
            fin_idx = min(inicio_idx + self.max_habilidades_visibles, len(self.lista_habilidades_mostradas))
            
            for i in range(inicio_idx, fin_idx):
                habilidad_data = self.lista_habilidades_mostradas[i]
                habilidad_texto = habilidad_data["nombre"]
                costo_texto = f"MP: {habilidad_data['costo_mp']}"
                desc_texto = habilidad_data.get("descripcion", "...")
                
                color_habilidad = self.COLOR_TEXTO
                color_costo = self.COLOR_TEXTO_MP
                
                # Verificar si el héroe tiene suficiente MP
                if self.heroe.MP_actual < habilidad_data['costo_mp']:
                    color_habilidad = self.COLOR_TEXTO_DESHABILITADO
                    color_costo = self.COLOR_TEXTO_DESHABILITADO
                
                # Posición relativa dentro de la superficie
                idx_visual = i - inicio_idx
                y_pos = start_y_habilidad + (idx_visual * line_height)
                
                # Resaltar si es la habilidad seleccionada
                if i == self.habilidad_seleccionada_idx and not self.boton_volver_seleccionado:
                    color_habilidad = self.COLOR_TEXTO_SEL
                    color_costo = self.COLOR_TEXTO_SEL
                    # Dibujar fondo de selección
                    seleccion_rect = pygame.Rect(0, y_pos - 5, self.panel_habilidades_rect.width, line_height - 10)
                    pygame.draw.rect(habilidades_surface, (50, 50, 100), seleccion_rect, border_radius=8)
                    
                    if self.cursor_img:
                        cursor_rect = self.cursor_img.get_rect(midright=(start_x_habilidad - 5, y_pos + 12))
                        habilidades_surface.blit(self.cursor_img, cursor_rect)

                # Dibujar nombre y costo
                habilidad_surf = self.fuente_opcion.render(habilidad_texto, True, color_habilidad)
                costo_surf = self.fuente_datos.render(costo_texto, True, color_costo)
                
                habilidades_surface.blit(habilidad_surf, (start_x_habilidad, y_pos))
                habilidades_surface.blit(costo_surf, (start_x_habilidad + 350, y_pos))
                
                # Dibujar descripción (max 3 líneas)
                ancho_desc = self.panel_habilidades_rect.width - 40
                lineas_desc = self._dividir_texto_en_lineas(desc_texto, ancho_desc)
                
                for j, linea in enumerate(lineas_desc[:3]):  # Máximo 3 líneas
                    desc_surf = self.fuente_desc.render(linea, True, self.COLOR_TEXTO)
                    habilidades_surface.blit(desc_surf, (start_x_habilidad, y_pos + 28 + (j * 18)))
            
            # Blit de la superficie de habilidades en el panel
            pantalla.blit(habilidades_surface, self.panel_habilidades_rect.topleft)
            
            # 4. Dibujar Scrollbar si hay más habilidades de las visibles
            if len(self.lista_habilidades_mostradas) > self.max_habilidades_visibles:
                # Barra de fondo
                pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR, self.scrollbar_rect, border_radius=7)
                
                # Calcular tamaño y posición del "thumb" (el indicador)
                total_habilidades = len(self.lista_habilidades_mostradas)
                thumb_height = max(20, int(self.scrollbar_rect.height * (self.max_habilidades_visibles / total_habilidades)))
                
                max_scroll = total_habilidades - self.max_habilidades_visibles
                if max_scroll > 0:
                    scroll_ratio = self.scroll_lista / max_scroll
                    thumb_y = self.scrollbar_rect.y + int((self.scrollbar_rect.height - thumb_height) * scroll_ratio)
                else:
                    thumb_y = self.scrollbar_rect.y
                
                thumb_rect = pygame.Rect(
                    self.scrollbar_rect.x,
                    thumb_y,
                    self.scrollbar_rect.width,
                    thumb_height
                )
                pygame.draw.rect(pantalla, self.COLOR_SCROLLBAR_THUMB, thumb_rect, border_radius=7)

        # 5. Dibujar Botón "VOLVER"
        color_boton = self.COLOR_CAJA
        color_texto_boton = self.COLOR_TEXTO
        if self.boton_volver_seleccionado:
            color_boton = (100, 100, 200)  # Azul más claro cuando está seleccionado
            color_texto_boton = self.COLOR_TEXTO_SEL
            if self.cursor_img:
                cursor_rect = self.cursor_img.get_rect(midright=(self.boton_volver_rect.x - 5, self.boton_volver_rect.centery))
                pantalla.blit(self.cursor_img, cursor_rect)
        
        pygame.draw.rect(pantalla, color_boton, self.boton_volver_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.boton_volver_rect, 2, border_radius=self.UI_BORDER_RADIUS)
        
        texto_boton = self.fuente_opcion.render("VOLVER", True, color_texto_boton)
        texto_rect = texto_boton.get_rect(center=self.boton_volver_rect.center)
        pantalla.blit(texto_boton, texto_rect)
