import pygame

class PantallaRecompensaCofre:
    """
    Pantalla que muestra los items obtenidos de un cofre.
    """
    
    def __init__(self, ancho, alto, items_obtenidos, items_db):
        """
        Args:
            ancho, alto: Dimensiones de la pantalla
            items_obtenidos: Dict {"item_id": cantidad}
            items_db: Base de datos de items
        """
        self.ANCHO = ancho
        self.ALTO = alto
        self.items_obtenidos = items_obtenidos
        self.items_db = items_db
        
        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 48)
        self.fuente_normal = pygame.font.Font(None, 32)
        
        # Colores
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_FONDO = (0, 0, 0, 200)  # Negro semi-transparente
        self.COLOR_BORDE = (255, 215, 0)  # Dorado
        
        # Animación
        self.tiempo_mostrar = 3000  # Mostrar por 3 segundos
        self.tiempo_inicio = pygame.time.get_ticks()
        
        # Indicador de cierre
        self.cerrar = False
    
    def update(self, teclas):
        """Actualiza la lógica de la pantalla"""
        # Auto-cerrar después de 3 segundos
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_inicio >= self.tiempo_mostrar:
            self.cerrar = True
    
    def update_input(self, tecla):
        """Maneja input de teclado"""
        # Enter para cerrar inmediatamente
        if tecla == pygame.K_RETURN or tecla == pygame.K_ESCAPE:
            self.cerrar = True
            return "cerrar"
        return None
    
    def draw(self, pantalla):
        """Dibuja la pantalla de recompensa"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ANCHO, self.ALTO))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))
        
        # Cuadro central
        ancho_cuadro = 500
        alto_cuadro = 300
        x_cuadro = (self.ANCHO - ancho_cuadro) // 2
        y_cuadro = (self.ALTO - alto_cuadro) // 2
        
        # Fondo del cuadro
        pygame.draw.rect(pantalla, (40, 40, 40), 
                        (x_cuadro, y_cuadro, ancho_cuadro, alto_cuadro))
        # Borde dorado
        pygame.draw.rect(pantalla, self.COLOR_BORDE, 
                        (x_cuadro, y_cuadro, ancho_cuadro, alto_cuadro), 4)
        
        # Título
        titulo = self.fuente_titulo.render("¡Cofre Abierto!", True, self.COLOR_BORDE)
        titulo_rect = titulo.get_rect(centerx=self.ANCHO // 2, top=y_cuadro + 20)
        pantalla.blit(titulo, titulo_rect)
        
        # Línea separadora
        pygame.draw.line(pantalla, self.COLOR_BORDE,
                        (x_cuadro + 20, y_cuadro + 70),
                        (x_cuadro + ancho_cuadro - 20, y_cuadro + 70), 2)
        
        # Items obtenidos
        y_item = y_cuadro + 90
        for item_id, cantidad in self.items_obtenidos.items():
            item_data = self.items_db.get(item_id)
            if item_data:
                nombre = item_data.get("nombre", item_id)
                texto = f"{nombre} x{cantidad}"
                
                # Color según tipo
                tipo = item_data.get("tipo", "")
                if tipo == "Consumible":
                    color = (100, 255, 100)  # Verde
                elif tipo == "Especial":
                    color = (255, 215, 0)  # Dorado
                else:
                    color = self.COLOR_TEXTO
                
                item_surf = self.fuente_normal.render(texto, True, color)
                item_rect = item_surf.get_rect(centerx=self.ANCHO // 2, top=y_item)
                pantalla.blit(item_surf, item_rect)
                
                y_item += 40
        
        # Instrucción
        tiempo_restante = (self.tiempo_mostrar - (pygame.time.get_ticks() - self.tiempo_inicio)) // 1000
        if tiempo_restante > 0:
            instruccion = f"Cierra automáticamente en {tiempo_restante}s"
        else:
            instruccion = "Presiona ENTER para continuar"
        
        inst_surf = self.fuente_normal.render(instruccion, True, (150, 150, 150))
        inst_rect = inst_surf.get_rect(centerx=self.ANCHO // 2, bottom=y_cuadro + alto_cuadro - 20)
        pantalla.blit(inst_surf, inst_rect)
