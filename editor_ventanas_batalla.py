"""
========================================
EDITOR DE VENTANAS DE BATALLA
========================================
Editor visual para configurar las ventanas de batalla con efecto glassmorphism.

Ventanas editables:
- Ventana de Acciones (Atacar, Magia, Items, etc.)
- Ventana de Magia
- Ventana de Items  
- Ventana de Victoria

Controles:
- Click y drag: Mover ventana
- Drag en esquinas: Redimensionar
- G: Guardar configuracion
- L: Cargar configuracion
- R: Reset a valores por defecto
- 1-4: Seleccionar ventana
- ESC: Salir
"""

import pygame
import json
import os
from pathlib import Path
from typing import Optional, List

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

# Colores para glassmorphism
COLOR_GLASS_BG = (40, 40, 60)  # Fondo del vidrio
COLOR_GLASS_BORDER = (100, 100, 150)  # Borde brillante
COLOR_GLASS_SHADOW = (0, 0, 0)  # Sombra

class VentanaEditable:
    """Ventana editable con efecto glassmorphism"""
    
    def __init__(self, x, y, ancho, alto, titulo, tipo, color_acento=(100, 150, 255)):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.tipo = tipo  # "acciones", "magia", "items", "victoria"
        self.color_acento = color_acento
        
        # Estado
        self.visible = True
        self.alpha = 230  # Transparencia (0-255)
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Contenido de ejemplo
        self.contenido = self._generar_contenido()
        
        self.actualizar_rect()
    
    def _generar_contenido(self):
        """Genera contenido de ejemplo segun el tipo"""
        if self.tipo == "acciones":
            return ["Atacar", "Magia", "Habilidades", "Items", "Huir"]
        elif self.tipo == "magia":
            return [
                "Fuego - 10 MP",
                "Rayo - 15 MP", 
                "Curar - 8 MP",
                "Hielo - 12 MP"
            ]
        elif self.tipo == "items":
            return [
                "Pocion x5",
                "Eter x3",
                "Antidoto x2",
                "Elixir x1"
            ]
        elif self.tipo == "victoria":
            return [
                "VICTORIA!",
                "",
                "EXP ganada: 150",
                "Oro ganado: 75",
                "",
                "Items obtenidos:",
                "- Pocion x2"
            ]
        return []
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px, py):
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px, py, tam=10):
        """Retorna que handle esta en el punto"""
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
    
    def dibujar(self, surface, seleccionada=False):
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
        
        # Barra de titulo
        titulo_rect = pygame.Rect(self.x, self.y, self.ancho, 35)
        titulo_surface = pygame.Surface((self.ancho, 35))
        titulo_surface.set_alpha(180)
        titulo_surface.fill(self.color_acento)
        surface.blit(titulo_surface, (self.x, self.y))
        
        # Texto del titulo
        fuente_titulo = pygame.font.Font(None, 24)
        texto_titulo = fuente_titulo.render(self.titulo, True, COLOR_TEXTO)
        surface.blit(texto_titulo, (self.x + 10, self.y + 8))
        
        # Contenido
        fuente_contenido = pygame.font.Font(None, 20)
        y_offset = 45
        
        for linea in self.contenido:
            if linea:  # Solo si no esta vacia
                texto = fuente_contenido.render(linea, True, COLOR_TEXTO)
                surface.blit(texto, (self.x + 15, self.y + y_offset))
            y_offset += 25
        
        # Handles de redimensionamiento si esta seleccionada
        if seleccionada:
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
            "visible": self.visible
        }
    
    def from_dict(self, data):
        """Importa desde diccionario"""
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.ancho = data.get("ancho", self.ancho)
        self.alto = data.get("alto", self.alto)
        self.alpha = data.get("alpha", self.alpha)
        self.visible = data.get("visible", self.visible)
        self.actualizar_rect()


class EditorVentanasBatalla:
    """Editor principal para configurar ventanas de batalla"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Editor de Ventanas de Batalla - CodeVerso RPG")
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
                (200, 150, 80)
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
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        # Cargar configuracion si existe
        self.cargar_configuracion()
        
        print("=" * 60)
        print("EDITOR DE VENTANAS DE BATALLA INICIADO")
        print("=" * 60)
        print("Controles:")
        print("  - Click y drag: Mover ventana")
        print("  - Drag esquinas: Redimensionar")
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
        """Guarda la configuracion actual"""
        config = {}
        for nombre, ventana in self.ventanas.items():
            config[f"ventana_{nombre}"] = ventana.to_dict()
        
        try:
            ruta = Path("src/database/batalla_ventanas.json")
            ruta.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje("Configuracion guardada exitosamente")
            return True
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar: {e}")
            return False
    
    def cargar_configuracion(self):
        """Carga la configuracion guardada"""
        try:
            ruta = Path("src/database/batalla_ventanas.json")
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
        self.ventanas["acciones"].x = 300
        self.ventanas["acciones"].y = 520
        self.ventanas["acciones"].ancho = 600
        self.ventanas["acciones"].alto = 120
        
        self.ventanas["magia"].x = 300
        self.ventanas["magia"].y = 150
        self.ventanas["magia"].ancho = 400
        self.ventanas["magia"].alto = 300
        
        self.ventanas["items"].x = 750
        self.ventanas["items"].y = 150
        self.ventanas["items"].ancho = 400
        self.ventanas["items"].alto = 300
        
        self.ventanas["victoria"].x = 400
        self.ventanas["victoria"].y = 100
        self.ventanas["victoria"].ancho = 600
        self.ventanas["victoria"].alto = 400
        
        for ventana in self.ventanas.values():
            ventana.alpha = 230
            ventana.actualizar_rect()
        
        self.mostrar_mensaje("Configuracion reseteada")
    
    def manejar_eventos(self):
        """Maneja eventos del editor"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
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
                    
                    # Solo procesar si esta en el area de batalla (no en panel)
                    if mouse_pos[0] >= PANEL_ANCHO:
                        # Verificar click en ventanas (de adelante hacia atras)
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
                    # Soltar todas las ventanas
                    for ventana in self.ventanas.values():
                        ventana.arrastrando = False
                        ventana.escalando = False
                        ventana.handle_activo = None
            
            elif evento.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                for ventana in self.ventanas.values():
                    if ventana.arrastrando:
                        ventana.x = mouse_pos[0] + ventana.offset_x
                        ventana.y = mouse_pos[1] + ventana.offset_y
                        ventana.actualizar_rect()
                    
                    elif ventana.escalando and ventana.handle_activo:
                        # Redimensionar segun el handle
                        if 'e' in ventana.handle_activo:  # Este (derecha)
                            nuevo_ancho = max(200, mouse_pos[0] - ventana.x)
                            ventana.ancho = nuevo_ancho
                        elif 'w' in ventana.handle_activo:  # Oeste (izquierda)
                            nuevo_ancho = max(200, ventana.x + ventana.ancho - mouse_pos[0])
                            if nuevo_ancho >= 200:
                                ventana.x = mouse_pos[0]
                                ventana.ancho = nuevo_ancho
                        
                        if 's' in ventana.handle_activo:  # Sur (abajo)
                            nuevo_alto = max(100, mouse_pos[1] - ventana.y)
                            ventana.alto = nuevo_alto
                        elif 'n' in ventana.handle_activo:  # Norte (arriba)
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
        
        # Titulo
        texto_titulo = self.fuente_titulo.render("Ventanas", True, COLOR_TEXTO)
        self.pantalla.blit(texto_titulo, (20, 20))
        
        # Lista de ventanas con checkboxes
        y_offset = 80
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
        y_botones = ALTO - 200
        botones = [
            ("G - Guardar", y_botones),
            ("L - Cargar", y_botones + 40),
            ("R - Reset", y_botones + 80),
            ("ESC - Salir", y_botones + 120)
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
            # Informacion de la ventana seleccionada
            if self.ventana_seleccionada:
                ventana = self.ventanas[self.ventana_seleccionada]
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
            
            # Area de batalla (fondo degradado)
            for y in range(0, ALTO, 2):
                color = (20 + y // 20, 20 + y // 20, 30 + y // 15)
                pygame.draw.line(self.pantalla, color, (PANEL_ANCHO, y), (ANCHO, y))
            
            # Dibujar ventanas (de atras hacia adelante)
            for nombre, ventana in self.ventanas.items():
                seleccionada = (nombre == self.ventana_seleccionada)
                ventana.dibujar(self.pantalla, seleccionada)
            
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
