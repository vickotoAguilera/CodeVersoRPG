"""
========================================
EDITOR DE VENTANAS DE BATALLA V2
========================================
Editor visual mejorado con áreas de contenido editables.

Nuevas características:
- Áreas de contenido movibles y redimensionables
- Texto adaptativo al tamaño de la caja
- Scroll visual configurable
- Exportación completa a JSON

Controles:
- Click y drag: Mover ventana/área
- Drag en esquinas: Redimensionar
- A: Modo edición de áreas
- G: Guardar | L: Cargar | R: Reset
- 1-4: Seleccionar ventana
- ESC: Salir
"""

import pygame
import json
import os
from pathlib import Path
from typing import Optional, List, Dict

# Configuracion
ANCHO = 1200
ALTO = 700
FPS = 60
PANEL_ANCHO = 250

# Colores
COLOR_FONDO = (20, 20, 30)
COLOR_PANEL = (30, 30, 40)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SEC = (180, 180, 180)
COLOR_SELECCION = (255, 215, 0)
COLOR_HANDLE = (255, 100, 100)
COLOR_AREA = (100, 255, 100)  # Verde para áreas de contenido

# Colores para glassmorphism
        self.tipo = tipo  # "lista", "texto", "grid"
        
        # Estado
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Configuración de scroll
        self.items_visibles_max = 5
        self.mostrar_scrollbar = True
        self.color_scrollbar = (100, 100, 255)
        
        # Contenido de ejemplo
        self.items_ejemplo = self._generar_contenido_ejemplo()
        
        self.actualizar_rect()
    
    def _generar_contenido_ejemplo(self):
        """Genera contenido de ejemplo según el tipo"""
        if self.tipo == "lista":
            return [
                "• Opción 1",
                "• Opción 2",
                "• Opción 3",
                "• Opción 4",
                "• Opción 5",
                "• Opción 6"
            ]
        elif self.tipo == "texto":
            return [
                "Texto de ejemplo",
                "que se adapta",
                "al tamaño de",
                "la caja"
            ]
        return []
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=8):
        """Retorna qué handle está en el punto"""
        handles = {
            'nw': (self.x, self.y),
            'ne': (self.x + self.ancho, self.y),
            'sw': (self.x, self.y + self.alto),
            'se': (self.x + self.ancho, self.y + self.alto)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam and abs(py - hy) <= tam:
                return nombre
        return None
    
    def dibujar(self, surface, seleccionada=False, offset_ventana=(0, 0)):
        """Dibuja el área de contenido"""
        # Posición absoluta (ventana + área)
        abs_x = offset_ventana[0] + self.x
        abs_y = offset_ventana[1] + self.y
        
        # Fondo semi-transparente
        fondo = pygame.Surface((self.ancho, self.alto))
        fondo.set_alpha(60)
        fondo.fill((50, 50, 80))
        surface.blit(fondo, (abs_x, abs_y))
        
        # Borde
        color_borde = COLOR_AREA if seleccionada else (80, 80, 120)
        pygame.draw.rect(surface, color_borde, 
                        pygame.Rect(abs_x, abs_y, self.ancho, self.alto), 
                        2, border_radius=5)
        
        # Etiqueta
        fuente_label = pygame.font.Font(None, 16)
        texto_label = fuente_label.render(self.nombre, True, color_borde)
        surface.blit(texto_label, (abs_x + 5, abs_y + 2))
        
        # Contenido de ejemplo (adaptado al tamaño)
        fuente_contenido = pygame.font.Font(None, 18)
        y_offset = 20
        line_height = 20
        
        # Calcular cuántas líneas caben
        lineas_que_caben = max(1, (self.alto - 25) // line_height)
        
        for i, linea in enumerate(self.items_ejemplo[:lineas_que_caben]):
            # Truncar texto si es muy largo
            texto_renderizado = fuente_contenido.render(linea, True, COLOR_TEXTO_SEC)
            if texto_renderizado.get_width() > self.ancho - 10:
                # Truncar
                while fuente_contenido.size(linea + "...")[0] > self.ancho - 10 and len(linea) > 0:
                    linea = linea[:-1]
                linea += "..."
                texto_renderizado = fuente_contenido.render(linea, True, COLOR_TEXTO_SEC)
            
            surface.blit(texto_renderizado, (abs_x + 5, abs_y + y_offset))
            y_offset += line_height
        
        # Scrollbar visual (si hay más items)
        if self.mostrar_scrollbar and len(self.items_ejemplo) > lineas_que_caben:
            scrollbar_x = abs_x + self.ancho - 10
            scrollbar_y = abs_y + 20
            scrollbar_alto = self.alto - 25
            
            # Barra de fondo
            pygame.draw.rect(surface, (50, 50, 70),
                           (scrollbar_x, scrollbar_y, 6, scrollbar_alto), border_radius=3)
            
            # Thumb
            thumb_alto = max(15, int((lineas_que_caben / len(self.items_ejemplo)) * scrollbar_alto))
            pygame.draw.rect(surface, self.color_scrollbar,
                           (scrollbar_x, scrollbar_y, 6, thumb_alto), border_radius=3)
        
        # Handles si está seleccionada
        if seleccionada:
            for handle_name, (hx, hy) in {
                'nw': (abs_x, abs_y),
                'ne': (abs_x + self.ancho, abs_y),
                'sw': (abs_x, abs_y + self.alto),
                'se': (abs_x + self.ancho, abs_y + self.alto)
            }.items():
                pygame.draw.circle(surface, COLOR_AREA, (int(hx), int(hy)), 5)
                pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), 3)
    
    def to_dict(self):
        """Exporta a diccionario"""
        return {
            "nombre": self.nombre,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "tipo": self.tipo,
            "items_visibles_max": self.items_visibles_max,
            "mostrar_scrollbar": self.mostrar_scrollbar,
            "color_scrollbar": list(self.color_scrollbar)
        }
    
    def from_dict(self, data):
        """Importa desde diccionario"""
        self.nombre = data.get("nombre", self.nombre)
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.ancho = data.get("ancho", self.ancho)
        self.alto = data.get("alto", self.alto)
        self.tipo = data.get("tipo", self.tipo)
        self.items_visibles_max = data.get("items_visibles_max", self.items_visibles_max)
        self.mostrar_scrollbar = data.get("mostrar_scrollbar", self.mostrar_scrollbar)
        color = data.get("color_scrollbar", list(self.color_scrollbar))
        self.color_scrollbar = tuple(color)
        self.actualizar_rect()


class VentanaEditable:
    """Ventana editable con efecto glassmorphism y áreas de contenido"""
    
    def __init__(self, x, y, ancho, alto, titulo, tipo, color_acento=(100, 150, 255)):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.tipo = tipo
        self.color_acento = color_acento
        
        # Estado
        self.visible = True
        self.alpha = 230
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Áreas de contenido
        self.areas_contenido: List[AreaContenido] = []
        self._crear_areas_por_defecto()
        
        # Contenido de ejemplo (legacy)
        self.contenido = self._generar_contenido()
        
        self.actualizar_rect()
    
    def _crear_areas_por_defecto(self):
        """Crea áreas de contenido por defecto según el tipo"""
        if self.tipo == "magia":
            self.areas_contenido.append(
                AreaContenido(20, 60, 360, 220, "lista", "Lista Magias")
            )
        elif self.tipo == "items":
            self.areas_contenido.append(
                AreaContenido(20, 60, 360, 220, "lista", "Lista Items")
            )
        elif self.tipo == "habilidades":
            self.areas_contenido.append(
                AreaContenido(20, 60, 360, 220, "lista", "Lista Habilidades")
            )
        elif self.tipo == "victoria":
            self.areas_contenido.append(
                AreaContenido(20, 60, 560, 120, "texto", "Recompensas")
            )
            self.areas_contenido.append(
                AreaContenido(20, 200, 560, 180, "lista", "Detalles")
            )
    
    def _generar_contenido(self):
        """Genera contenido de ejemplo según el tipo"""
        if self.tipo == "acciones":
            return ["Atacar", "Magia", "Habilidades", "Items", "Huir"]
        elif self.tipo == "magia":
            return ["Fuego - 10 MP", "Rayo - 15 MP", "Curar - 8 MP", "Hielo - 12 MP"]
        elif self.tipo == "items":
            return ["Pocion x5", "Eter x3", "Antidoto x2", "Elixir x1"]
        elif self.tipo == "victoria":
            return ["VICTORIA!", "", "EXP ganada: 150", "Oro ganado: 75"]
        return []
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=10):
        """Retorna qué handle está en el punto"""
        handles = {
            'nw': (self.x, self.y),
            'ne': (self.x + self.ancho, self.y),
            'sw': (self.x, self.y + self.alto),
            'se': (self.x + self.ancho, self.y + self.alto)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam and abs(py - hy) <= tam:
                return nombre
        return None
    
    def dibujar(self, surface, seleccionada=False, modo_areas=False):
        """Dibuja la ventana con efecto glassmorphism"""
        if not self.visible:
            return
        
        # Sombra
        sombra = pygame.Surface((self.ancho + 8, self.alto + 8))
        sombra.set_alpha(80)
        sombra.fill(COLOR_GLASS_SHADOW)
        surface.blit(sombra, (self.x - 4, self.y - 4))
        
        # Fondo glassmorphism
        fondo = pygame.Surface((self.ancho, self.alto))
        fondo.set_alpha(self.alpha)
        fondo.fill(COLOR_GLASS_BG)
        surface.blit(fondo, (self.x, self.y))
        
        # Borde brillante
        color_borde = COLOR_SELECCION if seleccionada else COLOR_GLASS_BORDER
        pygame.draw.rect(surface, color_borde, self.rect, 2, border_radius=10)
        
        # Barra de título
        titulo_surface = pygame.Surface((self.ancho, 35))
        titulo_surface.set_alpha(180)
        titulo_surface.fill(self.color_acento)
        surface.blit(titulo_surface, (self.x, self.y))
        
        # Texto del título
        fuente_titulo = pygame.font.Font(None, 24)
        texto_titulo = fuente_titulo.render(self.titulo, True, COLOR_TEXTO)
        surface.blit(texto_titulo, (self.x + 10, self.y + 8))
        
        # Dibujar áreas de contenido si está en modo áreas
        if modo_areas:
            for area in self.areas_contenido:
                area.dibujar(surface, False, (self.x, self.y))
        else:
            # Contenido legacy (sin áreas)
            fuente_contenido = pygame.font.Font(None, 20)
            y_offset = 45
            
            for linea in self.contenido:
                if linea:
                    texto = fuente_contenido.render(linea, True, COLOR_TEXTO)
                    surface.blit(texto, (self.x + 15, self.y + y_offset))
                y_offset += 25
        
        # Handles de redimensionamiento si está seleccionada
        if seleccionada and not modo_areas:
            for handle_name, (hx, hy) in {
                'nw': (self.x, self.y),
                'ne': (self.x + self.ancho, self.y),
                'sw': (self.x, self.y + self.alto),
                'se': (self.x + self.ancho, self.y + self.alto)
            }.items():
                pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), 6)
                pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), 4)
    
    def to_dict(self):
        """Exporta a diccionario para JSON"""
        return {
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "alpha": self.alpha,
            "visible": self.visible,
            "areas_contenido": [area.to_dict() for area in self.areas_contenido]
        }
    
    def from_dict(self, data):
        """Importa desde diccionario"""
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.ancho = data.get("ancho", self.ancho)
        self.alto = data.get("alto", self.alto)
        self.alpha = data.get("alpha", self.alpha)
        self.visible = data.get("visible", self.visible)
        
        # Cargar áreas
        if "areas_contenido" in data:
            self.areas_contenido = []
            for area_data in data["areas_contenido"]:
                area = AreaContenido(0, 0, 100, 100)
                area.from_dict(area_data)
                self.areas_contenido.append(area)
        
        self.actualizar_rect()


class EditorVentanasBatalla:
    """Editor principal para configurar ventanas de batalla"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Ventanas de Batalla V2 - CodeVerso RPG")
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        # Crear ventanas editables
        self.ventanas = {
            "acciones": VentanaEditable(
                300, 520, 600, 120,
                "Ventana de Acciones",
                "acciones",
                (80, 120, 200)
            ),
            "magia": VentanaEditable(
                300, 150, 400, 300,
                "Ventana de Magia",
                "magia",
                (150, 80, 200)
            ),
            "items": VentanaEditable(
                750, 150, 400, 300,
                "Ventana de Items",
                "items",
                (80, 200, 150)
            ),
            "victoria": VentanaEditable(
                400, 100, 600, 400,
                "Ventana de Victoria",
                "victoria",
                (255, 200, 50)
            )
        }
        
        # Solo mostrar ventana de acciones por defecto
        self.ventanas["magia"].visible = False
        self.ventanas["items"].visible = False
        self.ventanas["victoria"].visible = False
        
        # Estado
        self.ventana_seleccionada: Optional[str] = "acciones"
        self.area_seleccionada: Optional[AreaContenido] = None
        self.modo_areas = False  # Modo de edición de áreas
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        # Cargar configuración si existe
        self.cargar_configuracion()
        
        print("=" * 60)
        print("EDITOR DE VENTANAS DE BATALLA V2 INICIADO")
        print("=" * 60)
        print("Controles:")
        print("  - Click y drag: Mover ventana/area")
        print("  - Drag esquinas: Redimensionar")
        print("  - A: Modo edicion de areas")
        print("  - G: Guardar | L: Cargar | R: Reset")
        print("  - 1-4: Seleccionar ventana")
        print("  - ESC: Salir")
        print("=" * 60)
    
    def mostrar_mensaje(self, texto):
        """Muestra un mensaje temporal"""
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
        print(f"[INFO] {texto}")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        config = {}
        for nombre, ventana in self.ventanas.items():
            config[f"ventana_{nombre}"] = ventana.to_dict()
        
        try:
            ruta = Path("src/database/batalla_ventanas_v2.json")
            ruta.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje("Configuracion guardada exitosamente")
            return True
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar: {e}")
            return False
    
    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        try:
            ruta = Path("src/database/batalla_ventanas_v2.json")
            if not ruta.exists():
                self.mostrar_mensaje("No hay configuracion guardada")
                return False
            
            with open(ruta, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for nombre, ventana in self.ventanas.items():
                key = f"ventana_{nombre}"
                if key in config:
                    ventana.from_dict(config[key])
            
            self.mostrar_mensaje("Configuracion cargada exitosamente")
            return True
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar: {e}")
            return False
    
    def reset_configuracion(self):
        """Resetea a valores por defecto"""
        # Recrear ventanas
        self.__init__()
        self.mostrar_mensaje("Configuracion reseteada")
    
    def manejar_eventos(self):
        """Maneja eventos del editor"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                elif evento.key == pygame.K_a:
                    self.modo_areas = not self.modo_areas
                    modo_txt = "ACTIVADO" if self.modo_areas else "DESACTIVADO"
                    self.mostrar_mensaje(f"Modo edicion de areas: {modo_txt}")
                elif evento.key == pygame.K_g:
                    self.guardar_configuracion()
                elif evento.key == pygame.K_l:
                    self.cargar_configuracion()
                elif evento.key == pygame.K_r:
                    self.reset_configuracion()
                elif evento.key == pygame.K_1:
                    self.ventana_seleccionada = "acciones"
                elif evento.key == pygame.K_2:
                    self.ventana_seleccionada = "magia"
                elif evento.key == pygame.K_3:
                    self.ventana_seleccionada = "items"
                elif evento.key == pygame.K_4:
                    self.ventana_seleccionada = "victoria"
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click izquierdo
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Solo procesar si está en el área de batalla
                    if mouse_pos[0] >= PANEL_ANCHO:
                        if self.modo_areas and self.ventana_seleccionada:
                            # Modo edición de áreas
                            ventana = self.ventanas[self.ventana_seleccionada]
                            if ventana.visible:
                                # Convertir a coordenadas relativas
                                rel_x = mouse_pos[0] - ventana.x
                                rel_y = mouse_pos[1] - ventana.y
                                
                                # Verificar click en áreas
                                for area in reversed(ventana.areas_contenido):
                                    # Verificar handles primero
                                    handle = area.get_handle_en_punto(rel_x, rel_y)
                                    if handle:
                                        area.escalando = True
                                        area.handle_activo = handle
                                        self.area_seleccionada = area
                                        break
                                    
                                    # Verificar click en área
                                    elif area.contiene_punto(rel_x, rel_y):
                                        area.arrastrando = True
                                        area.offset_x = area.x - rel_x
                                        area.offset_y = area.y - rel_y
                                        self.area_seleccionada = area
                                        break
                        else:
                            # Modo normal - editar ventanas
                            ventanas_ordenadas = list(reversed(list(self.ventanas.items())))
                            
                            for nombre, ventana in ventanas_ordenadas:
                                if not ventana.visible:
                                    continue
                                
                                # Verificar handles primero
                                handle = ventana.get_handle_en_punto(mouse_pos[0], mouse_pos[1])
                                if handle:
                                    ventana.escalando = True
                                    ventana.handle_activo = handle
                                    self.ventana_seleccionada = nombre
                                    break
                                
                                # Verificar click en ventana
                                elif ventana.contiene_punto(mouse_pos[0], mouse_pos[1]):
                                    ventana.arrastrando = True
                                    ventana.offset_x = ventana.x - mouse_pos[0]
                                    ventana.offset_y = ventana.y - mouse_pos[1]
                                    self.ventana_seleccionada = nombre
                                    break
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    # Soltar todas las ventanas y áreas
                    for ventana in self.ventanas.values():
                        ventana.arrastrando = False
                        ventana.escalando = False
                        ventana.handle_activo = None
                        
                        for area in ventana.areas_contenido:
                            area.arrastrando = False
                            area.escalando = False
                            area.handle_activo = None
            
            elif evento.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.modo_areas and self.ventana_seleccionada:
                    # Mover/redimensionar áreas
                    ventana = self.ventanas[self.ventana_seleccionada]
                    rel_x = mouse_pos[0] - ventana.x
                    rel_y = mouse_pos[1] - ventana.y
                    
                    for area in ventana.areas_contenido:
                        if area.arrastrando:
                            area.x = rel_x + area.offset_x
                            area.y = rel_y + area.offset_y
                            # Limitar dentro de la ventana
                            area.x = max(5, min(area.x, ventana.ancho - area.ancho - 5))
                            area.y = max(40, min(area.y, ventana.alto - area.alto - 5))
                            area.actualizar_rect()
                        
                        elif area.escalando and area.handle_activo:
                            # Redimensionar área
                            if 'e' in area.handle_activo:
                                nuevo_ancho = max(100, rel_x - area.x)
                                area.ancho = min(nuevo_ancho, ventana.ancho - area.x - 5)
                            elif 'w' in area.handle_activo:
                                nuevo_ancho = max(100, area.x + area.ancho - rel_x)
                                if nuevo_ancho >= 100:
                                    area.x = max(5, rel_x)
                                    area.ancho = nuevo_ancho
                            
                            if 's' in area.handle_activo:
                                nuevo_alto = max(50, rel_y - area.y)
                                area.alto = min(nuevo_alto, ventana.alto - area.y - 5)
                            elif 'n' in area.handle_activo:
                                nuevo_alto = max(50, area.y + area.alto - rel_y)
                                if nuevo_alto >= 50:
                                    area.y = max(40, rel_y)
                                    area.alto = nuevo_alto
                            
                            area.actualizar_rect()
                else:
                    # Mover/redimensionar ventanas
                    for ventana in self.ventanas.values():
                        if ventana.arrastrando:
                            ventana.x = mouse_pos[0] + ventana.offset_x
                            ventana.y = mouse_pos[1] + ventana.offset_y
                            ventana.actualizar_rect()
                        
                        elif ventana.escalando and ventana.handle_activo:
                            # Redimensionar ventana
                            if 'e' in ventana.handle_activo:
                                nuevo_ancho = max(200, mouse_pos[0] - ventana.x)
                                ventana.ancho = nuevo_ancho
                            elif 'w' in ventana.handle_activo:
                                nuevo_ancho = max(200, ventana.x + ventana.ancho - mouse_pos[0])
                                if nuevo_ancho >= 200:
                                    ventana.x = mouse_pos[0]
                                    ventana.ancho = nuevo_ancho
                            
                            if 's' in ventana.handle_activo:
                                nuevo_alto = max(100, mouse_pos[1] - ventana.y)
                                ventana.alto = nuevo_alto
                            elif 'n' in ventana.handle_activo:
                                nuevo_alto = max(100, ventana.y + ventana.alto - mouse_pos[1])
                                if nuevo_alto >= 100:
                                    ventana.y = mouse_pos[1]
                                    ventana.alto = nuevo_alto
                            
                            ventana.actualizar_rect()
        
        return True
    
    def dibujar_panel_lateral(self):
        """Dibuja el panel lateral con controles"""
        # Fondo del panel
        pygame.draw.rect(self.pantalla, COLOR_PANEL, (0, 0, PANEL_ANCHO, ALTO))
        
        # Título
        texto_titulo = self.fuente_titulo.render("Ventanas", True, COLOR_TEXTO)
        self.pantalla.blit(texto_titulo, (20, 20))
        
        # Indicador de modo
        modo_texto = "MODO: AREAS" if self.modo_areas else "MODO: VENTANAS"
        color_modo = COLOR_AREA if self.modo_areas else COLOR_SELECCION
        texto_modo = self.fuente_pequena.render(modo_texto, True, color_modo)
        self.pantalla.blit(texto_modo, (20, 55))
        
        # Lista de ventanas con checkboxes
        y_offset = 90
        for nombre, ventana in self.ventanas.items():
            # Checkbox
            checkbox_rect = pygame.Rect(20, y_offset, 20, 20)
            color_check = (100, 200, 100) if ventana.visible else (100, 100, 100)
            pygame.draw.rect(self.pantalla, color_check, checkbox_rect, 2)
            if ventana.visible:
                pygame.draw.line(self.pantalla, color_check, 
                               (checkbox_rect.x + 4, checkbox_rect.y + 10),
                               (checkbox_rect.x + 8, checkbox_rect.y + 16), 3)
                pygame.draw.line(self.pantalla, color_check,
                               (checkbox_rect.x + 8, checkbox_rect.y + 16),
                               (checkbox_rect.x + 16, checkbox_rect.y + 4), 3)
            
            # Nombre
            color_nombre = COLOR_SELECCION if nombre == self.ventana_seleccionada else COLOR_TEXTO
            texto_nombre = self.fuente_pequena.render(ventana.titulo, True, color_nombre)
            self.pantalla.blit(texto_nombre, (50, y_offset + 2))
            
            y_offset += 40
        
        # Botones
        y_botones = ALTO - 240
        botones = [
            ("A - Modo Areas", y_botones),
            ("G - Guardar", y_botones + 40),
            ("L - Cargar", y_botones + 80),
            ("R - Reset", y_botones + 120),
            ("ESC - Salir", y_botones + 160)
        ]
        
        for texto, y in botones:
            boton_rect = pygame.Rect(20, y, PANEL_ANCHO - 40, 30)
            pygame.draw.rect(self.pantalla, (60, 60, 80), boton_rect, border_radius=5)
            pygame.draw.rect(self.pantalla, COLOR_TEXTO, boton_rect, 1, border_radius=5)
            
            texto_boton = self.fuente_pequena.render(texto, True, COLOR_TEXTO)
            texto_rect = texto_boton.get_rect(center=boton_rect.center)
            self.pantalla.blit(texto_boton, texto_rect)
    
    def dibujar_barra_estado(self):
        """Dibuja la barra de estado inferior"""
        # Fondo
        barra_rect = pygame.Rect(PANEL_ANCHO, ALTO - 30, ANCHO - PANEL_ANCHO, 30)
        pygame.draw.rect(self.pantalla, (40, 40, 50), barra_rect)
        
        # Mensaje temporal
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_tiempo < 3000:
            texto_msg = self.fuente_pequena.render(self.mensaje, True, COLOR_TEXTO)
            self.pantalla.blit(texto_msg, (PANEL_ANCHO + 10, ALTO - 25))
        else:
            # Información
            if self.ventana_seleccionada:
                ventana = self.ventanas[self.ventana_seleccionada]
                if self.modo_areas and self.area_seleccionada:
                    info = f"Area: {self.area_seleccionada.nombre} | Pos: ({int(self.area_seleccionada.x)}, {int(self.area_seleccionada.y)}) | Tam: {self.area_seleccionada.ancho}x{self.area_seleccionada.alto}"
                else:
                    info = f"{ventana.titulo} | Pos: ({int(ventana.x)}, {int(ventana.y)}) | Tam: {ventana.ancho}x{ventana.alto}"
                texto_info = self.fuente_pequena.render(info, True, COLOR_TEXTO_SEC)
                self.pantalla.blit(texto_info, (PANEL_ANCHO + 10, ALTO - 25))
    
    def ejecutar(self):
        """Bucle principal del editor"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Área de batalla (fondo degradado)
            for y in range(0, ALTO, 2):
                color = (20 + y // 20, 20 + y // 20, 30 + y // 15)
                pygame.draw.line(self.pantalla, color, (PANEL_ANCHO, y), (ANCHO, y))
            
            # Dibujar ventanas
            for nombre, ventana in self.ventanas.items():
                seleccionada = (nombre == self.ventana_seleccionada)
                ventana.dibujar(self.pantalla, seleccionada, self.modo_areas)
            
            # Dibujar áreas seleccionadas
            if self.modo_areas and self.ventana_seleccionada:
                ventana = self.ventanas[self.ventana_seleccionada]
                if ventana.visible:
                    for area in ventana.areas_contenido:
                        seleccionada_area = (area == self.area_seleccionada)
                        area.dibujar(self.pantalla, seleccionada_area, (ventana.x, ventana.y))
            
            # Panel lateral
            self.dibujar_panel_lateral()
            
            # Barra de estado
            self.dibujar_barra_estado()
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()
        print("[OK] Editor cerrado")


# Ejecutar
if __name__ == "__main__":
    editor = EditorVentanasBatalla()
    editor.ejecutar()
