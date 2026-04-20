import pygame
from src.config import UI_PATH

class PantallaCofre:
    """
    Pantalla para mostrar el contenido de un cofre y permitir recoger items.
    Usa navegación por teclado (flechas + ENTER).
    """
    
    def __init__(self, ancho, alto, cofre, grupo_heroes, items_db, cursor_img=None):
        """
        Constructor de la pantalla de cofre.
        
        Args:
            ancho, alto: Dimensiones de la pantalla
            cofre: Objeto Cofre a mostrar
            grupo_heroes: Lista de héroes (para agregar items)
            items_db: Base de datos de items
            cursor_img: Imagen del cursor personalizado
        """
        self.ancho = ancho
        self.alto = alto
        self.cofre = cofre
        self.grupo_heroes = grupo_heroes
        self.items_db = items_db
        self.cursor_img = cursor_img
        
        # Fuentes
        self.font_titulo = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colores
        self.COLOR_FONDO = (20, 20, 30)
        self.COLOR_PANEL = (40, 40, 50)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_BOTON = (60, 60, 80)
        self.COLOR_BOTON_SELECCIONADO = (100, 150, 255)  # Azul para selección
        self.COLOR_DORADO = (255, 215, 0)
        
        # Dimensiones del panel
        self.panel_ancho = 600
        self.panel_alto = 400
        self.panel_x = (ancho - self.panel_ancho) // 2
        self.panel_y = (alto - self.panel_alto) // 2
        
        # Opciones de navegación
        self.opciones = ["tomar_todo", "cerrar"]
        self.opcion_seleccionada = 0  # 0 = Tomar Todo, 1 = Cerrar
        
        # Estado
        self.items_tomados = False
        self.mensaje_feedback = ""
        self.tiempo_mensaje = 0
    
    def update(self, teclas):
        """Actualiza la lógica de la pantalla"""
        # Actualizar tiempo del mensaje
        if self.tiempo_mensaje > 0:
            self.tiempo_mensaje -= 1
    
    def update_input(self, key):
        """
        Maneja input de teclado.
        
        Returns:
            str: Acción a realizar ("cerrar", "tomar_todo", None)
        """
        # ESC siempre cierra
        if key == pygame.K_ESCAPE:
            return "cerrar"
        
        # Navegación con flechas
        if key == pygame.K_LEFT or key == pygame.K_RIGHT:
            # Solo permitir navegación si hay items
            if not self.cofre.vacio and self.cofre.items_contenido:
                self.opcion_seleccionada = 1 - self.opcion_seleccionada  # Toggle entre 0 y 1
        
        # E ejecuta la acción seleccionada
        if key == pygame.K_e:
            if self.opcion_seleccionada == 0:  # Tomar Todo
                if not self.cofre.vacio and self.cofre.items_contenido:
                    self.tomar_todos_items()
                    return None  # No cerrar aún, mostrar feedback
                else:
                    return "cerrar"  # Si está vacío, cerrar
            else:  # Cerrar
                return "cerrar"
        
        return None
    
    def tomar_todos_items(self):
        """Toma todos los items del cofre y los agrega al inventario"""
        if self.cofre.vacio or not self.cofre.items_contenido:
            self.mensaje_feedback = "El cofre está vacío"
            self.tiempo_mensaje = 120  # 2 segundos a 60 FPS
            return
        
        lider = self.grupo_heroes[0]
        items_agregados = []
        
        for item_id, cantidad in self.cofre.items_contenido.items():
            # Verificar si es un item especial
            es_especial = False
            nombre_item = item_id
            
            if item_id in self.items_db:
                item_data = self.items_db[item_id]
                nombre_item = item_data.get("nombre", item_id)
                if item_data.get("tipo") == "Especial":
                    es_especial = True
            
            if es_especial:
                # Usar el método centralizado para items especiales
                lider.agregar_item_especial(item_id, cantidad, self.items_db, self.grupo_heroes)
            else:
                # Items normales van al inventario normal
                if item_id in lider.inventario:
                    lider.inventario[item_id] += cantidad
                else:
                    lider.inventario[item_id] = cantidad
            
            items_agregados.append(f"{nombre_item} x{cantidad}")
        
        # Marcar cofre como vacío
        self.cofre.vacio = True
        self.cofre.abierto = True
        self.cofre.actualizar_sprite()
        self.items_tomados = True
        
        # Cambiar a opción "Cerrar" automáticamente
        self.opcion_seleccionada = 1
        
        # Mensaje de feedback
        if len(items_agregados) > 0:
            self.mensaje_feedback = f"¡Obtenido: {', '.join(items_agregados)}!"
        else:
            self.mensaje_feedback = "¡Items obtenidos!"
        self.tiempo_mensaje = 180  # 3 segundos
    
    def draw(self, pantalla):
        """Dibuja la pantalla del cofre"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))
        
        # Panel principal
        pygame.draw.rect(pantalla, self.COLOR_PANEL, 
                        (self.panel_x, self.panel_y, self.panel_ancho, self.panel_alto))
        pygame.draw.rect(pantalla, self.COLOR_DORADO, 
                        (self.panel_x, self.panel_y, self.panel_ancho, self.panel_alto), 3)
        
        # Título
        titulo = self.font_titulo.render(f"Cofre: {self.cofre.id_cofre}", True, self.COLOR_DORADO)
        titulo_rect = titulo.get_rect(center=(self.ancho // 2, self.panel_y + 40))
        pantalla.blit(titulo, titulo_rect)
        
        # Contenido del cofre
        y_offset = self.panel_y + 100
        
        if self.cofre.vacio or not self.cofre.items_contenido:
            # Cofre vacío
            texto_vacio = self.font_normal.render("El cofre está vacío...", True, (150, 150, 150))
            texto_rect = texto_vacio.get_rect(center=(self.ancho // 2, y_offset + 50))
            pantalla.blit(texto_vacio, texto_rect)
        else:
            # Mostrar items
            texto_contenido = self.font_normal.render("Contenido:", True, self.COLOR_TEXTO)
            pantalla.blit(texto_contenido, (self.panel_x + 50, y_offset))
            y_offset += 40
            
            for item_id, cantidad in self.cofre.items_contenido.items():
                # Obtener nombre del item
                nombre_item = item_id
                if item_id in self.items_db:
                    nombre_item = self.items_db[item_id].get("nombre", item_id)
                
                # Dibujar item
                texto_item = self.font_small.render(f"• {nombre_item} x{cantidad}", True, self.COLOR_TEXTO)
                pantalla.blit(texto_item, (self.panel_x + 70, y_offset))
                y_offset += 30
        
        # Botones con navegación por teclado
        boton_y = self.panel_y + self.panel_alto - 70
        
        # Botón "Tomar Todo" (solo si hay items)
        if not self.cofre.vacio and self.cofre.items_contenido:
            boton_tomar_rect = pygame.Rect(self.panel_x + 50, boton_y, 200, 50)
            color_tomar = self.COLOR_BOTON_SELECCIONADO if self.opcion_seleccionada == 0 else self.COLOR_BOTON
            pygame.draw.rect(pantalla, color_tomar, boton_tomar_rect)
            pygame.draw.rect(pantalla, self.COLOR_TEXTO, boton_tomar_rect, 2)
            texto_tomar = self.font_normal.render("Tomar Todo", True, self.COLOR_TEXTO)
            texto_rect = texto_tomar.get_rect(center=boton_tomar_rect.center)
            pantalla.blit(texto_tomar, texto_rect)
        
        # Botón "Cerrar"
        boton_cerrar_rect = pygame.Rect(self.panel_x + self.panel_ancho - 250, boton_y, 200, 50)
        color_cerrar = self.COLOR_BOTON_SELECCIONADO if self.opcion_seleccionada == 1 else self.COLOR_BOTON
        pygame.draw.rect(pantalla, color_cerrar, boton_cerrar_rect)
        pygame.draw.rect(pantalla, self.COLOR_TEXTO, boton_cerrar_rect, 2)
        texto_cerrar = self.font_normal.render("Cerrar", True, self.COLOR_TEXTO)
        texto_rect = texto_cerrar.get_rect(center=boton_cerrar_rect.center)
        pantalla.blit(texto_cerrar, texto_rect)
        
        # Mensaje de feedback
        if self.tiempo_mensaje > 0:
            texto_msg = self.font_small.render(self.mensaje_feedback, True, self.COLOR_DORADO)
            msg_rect = texto_msg.get_rect(center=(self.ancho // 2, self.panel_y + self.panel_alto - 100))
            pantalla.blit(texto_msg, msg_rect)
        
        # Instrucciones
        if not self.cofre.vacio and self.cofre.items_contenido:
            texto_inst = self.font_small.render("← -> para navegar | E para aceptar | ESC para cerrar", True, (150, 150, 150))
        else:
            texto_inst = self.font_small.render("E o ESC para cerrar", True, (150, 150, 150))
        inst_rect = texto_inst.get_rect(center=(self.ancho // 2, self.alto - 30))
        pantalla.blit(texto_inst, inst_rect)
