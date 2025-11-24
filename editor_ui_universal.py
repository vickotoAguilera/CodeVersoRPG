"""
Editor UI Universal - CodeVerso RPG
Versión limpia y completa

Características:
- Ventana redimensionable con botones de Windows
- Lienzo del juego (1280x720) para ver proporciones reales
- Lista expansible de ventanas con checkboxes
- Drag & drop de ventanas y textboxes
- Scroll con teclas de dirección
- Importación de JSONs generados por extraer_diseños.py
- Exportación a JSON
"""

import pygame
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Configuración
ANCHO = 1200
ALTO = 700
FPS = 60
PANEL_ANCHO = 280

# Dimensiones del lienzo del juego
LIENZO_JUEGO_ANCHO = 1280
LIENZO_JUEGO_ALTO = 720

# Colores
COLOR_FONDO = (20, 20, 30)
COLOR_PANEL = (30, 30, 40)
COLOR_TEXTO = (255, 255, 255)
COLOR_TEXTO_SEC = (180, 180, 180)
COLOR_SELECCION = (255, 215, 0)
COLOR_HANDLE = (255, 100, 100)
COLOR_TEXTBOX = (100, 255, 100)
COLOR_VENTANA = (100, 150, 255)
COLOR_LIENZO = (40, 40, 50)

# Colores glassmorphism
COLOR_GLASS_BG = (40, 40, 60)
COLOR_GLASS_BORDER = (100, 100, 120)
COLOR_GLASS_SHADOW = (0, 0, 0)


class TextBox:
    """Caja de texto independiente - Posición ABSOLUTA"""
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, nombre: str = "TextBox"):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.nombre = nombre
        
        self.tipo = "lista"
        self.contenido = ["• Línea 1", "• Línea 2", "• Línea 3"]
        
        self.fuente_size = 20
        self.color_texto = (255, 255, 255)
        self.color_fondo = (50, 50, 80, 100)
        self.alineacion = "left"
        
        self.scroll_enabled = True
        self.items_visibles = 5
        self.color_scrollbar = (100, 100, 255)
        self.scroll_offset_y = 0
        self.scroll_offset_x = 0
        
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        
        self.actualizar_rect()
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px: int, py: int) -> bool:
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px: int, py: int, tam: int = 10) -> Optional[str]:
        handles = {
            'nw': (self.x, self.y),
            'ne': (self.x + self.ancho, self.y),
            'sw': (self.x, self.y + self.alto),
            'se': (self.x + self.ancho, self.y + self.alto),
            'n': (self.x + self.ancho // 2, self.y),
            's': (self.x + self.ancho // 2, self.y + self.alto),
            'e': (self.x + self.ancho, self.y + self.alto // 2),
            'w': (self.x, self.y + self.alto // 2)
        }
        
        for nombre, (hx, hy) in handles.items():
            if abs(px - hx) <= tam and abs(py - hy) <= tam:
                return nombre
        return None
    
    def dibujar(self, surface: pygame.Surface, seleccionada: bool = False):
        # Fondo
        fondo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        fondo.fill(self.color_fondo)
        surface.blit(fondo, (self.x, self.y))
        
        # Borde
        color_borde = COLOR_TEXTBOX if seleccionada else (100, 100, 100)
        pygame.draw.rect(surface, color_borde, self.rect, 2, border_radius=5)
        
        # Título
        fuente_titulo = pygame.font.Font(None, 16)
        texto_titulo = fuente_titulo.render(self.nombre, True, COLOR_TEXTO_SEC)
        surface.blit(texto_titulo, (self.x + 5, self.y + 2))
        
        # Contenido
        fuente_contenido = pygame.font.Font(None, self.fuente_size)
        y_offset = 18
        line_height = self.fuente_size + 2
        
        lineas_que_caben = max(1, (self.alto - 20) // line_height)
        inicio_linea = max(0, self.scroll_offset_y)
        fin_linea = min(len(self.contenido), inicio_linea + lineas_que_caben)
        
        for i in range(inicio_linea, fin_linea):
            linea = self.contenido[i]
            texto_renderizado = fuente_contenido.render(linea, True, self.color_texto)
            
            if self.alineacion == "center":
                x_pos = self.x + (self.ancho - texto_renderizado.get_width()) // 2
            elif self.alineacion == "right":
                x_pos = self.x + self.ancho - texto_renderizado.get_width() - 5
            else:
                x_pos = self.x + 5
            
            surface.blit(texto_renderizado, (x_pos, self.y + y_offset))
            y_offset += line_height
        
        # Scrollbar
        if self.scroll_enabled and len(self.contenido) > lineas_que_caben:
            scrollbar_x = self.x + self.ancho - 8
            scrollbar_y = self.y + 18
            scrollbar_alto = self.alto - 20
            
            pygame.draw.rect(surface, (50, 50, 70),
                           (scrollbar_x, scrollbar_y, 5, scrollbar_alto), border_radius=2)
            
            thumb_alto = max(15, int((lineas_que_caben / len(self.contenido)) * scrollbar_alto))
            max_scroll = len(self.contenido) - lineas_que_caben
            if max_scroll > 0:
                thumb_y = scrollbar_y + int((self.scroll_offset_y / max_scroll) * (scrollbar_alto - thumb_alto))
            else:
                thumb_y = scrollbar_y
            
            pygame.draw.rect(surface, self.color_scrollbar,
                           (scrollbar_x, thumb_y, 5, thumb_alto), border_radius=2)
        
        # Handles
        if seleccionada:
            for handle_name, (hx, hy) in {
                'nw': (self.x, self.y),
                'ne': (self.x + self.ancho, self.y),
                'sw': (self.x, self.y + self.alto),
                'se': (self.x + self.ancho, self.y + self.alto)
            }.items():
                pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), 6)
                pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), 4)
    
    def to_dict(self) -> Dict:
        return {
            "nombre": self.nombre,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "tipo": self.tipo,
            "contenido": self.contenido,
            "fuente_size": self.fuente_size,
            "color_texto": list(self.color_texto),
            "alineacion": self.alineacion,
            "scroll": {
                "enabled": self.scroll_enabled,
                "items_visibles": self.items_visibles,
                "color_scrollbar": list(self.color_scrollbar),
                "offset_y": self.scroll_offset_y,
                "offset_x": self.scroll_offset_x
            }
        }


class VentanaUI:
    """Ventana visual con glassmorphism"""
    
    def __init__(self, x: int, y: int, ancho: int, alto: int, nombre: str, color_acento: Tuple[int, int, int] = (100, 150, 255)):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.nombre = nombre
        self.titulo = nombre
        self.color_acento = color_acento
        
        self.visible = True
        self.alpha = 230
        self.arrastrando = False
        self.escalando = False
        self.handle_activo = None
        self.offset_x = 0
        self.offset_y = 0
        
        self.actualizar_rect()
    
    def actualizar_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
    
    def contiene_punto(self, px: int, py: int) -> bool:
        return self.rect.collidepoint(px, py)
    
    def get_handle_en_punto(self, px: int, py: int, tam: int = 10) -> Optional[str]:
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
    
    def dibujar(self, surface: pygame.Surface, seleccionada: bool = False):
        if not self.visible:
            return
        
        # Sombra
        sombra = pygame.Surface((self.ancho + 8, self.alto + 8), pygame.SRCALPHA)
        sombra.fill((*COLOR_GLASS_SHADOW, 80))
        surface.blit(sombra, (self.x - 4, self.y - 4))
        
        # Fondo glassmorphism
        fondo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        fondo.fill((*COLOR_GLASS_BG, self.alpha))
        surface.blit(fondo, (self.x, self.y))
        
        # Borde
        color_borde = COLOR_VENTANA if seleccionada else COLOR_GLASS_BORDER
        pygame.draw.rect(surface, color_borde, self.rect, 2, border_radius=10)
        
        # Barra de título
        titulo_surface = pygame.Surface((self.ancho, 35), pygame.SRCALPHA)
        titulo_surface.fill((*self.color_acento, 180))
        surface.blit(titulo_surface, (self.x, self.y))
        
        # Texto del título
        fuente_titulo = pygame.font.Font(None, 24)
        texto_titulo = fuente_titulo.render(self.titulo, True, COLOR_TEXTO)
        surface.blit(texto_titulo, (self.x + 10, self.y + 8))
        
        # Handles
        if seleccionada:
            for handle_name, (hx, hy) in {
                'nw': (self.x, self.y),
                'ne': (self.x + self.ancho, self.y),
                'sw': (self.x, self.y + self.alto),
                'se': (self.x + self.ancho, self.y + self.alto)
            }.items():
                pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), 6)
                pygame.draw.circle(surface, COLOR_TEXTO, (int(hx), int(hy)), 4)
    
    def to_dict(self) -> Dict:
        return {
            "nombre": self.nombre,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "titulo": self.titulo,
            "color_acento": list(self.color_acento),
            "alpha": self.alpha,
            "visible": self.visible
        }


class EditorUIUniversal:
    """Editor principal"""
    
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Editor UI Universal - CodeVerso RPG")
        self.reloj = pygame.time.Clock()
        
        self.ancho_actual = ANCHO
        self.alto_actual = ALTO
        
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_titulo = pygame.font.Font(None, 32)
        
        self.ventanas: Dict[str, VentanaUI] = {}
        self.textboxes: Dict[str, List[TextBox]] = {}
        
        self.modo = "ventanas"
        self.ventana_seleccionada: Optional[str] = None
        self.textbox_seleccionada: Optional[TextBox] = None
        self.mensaje = ""
        self.mensaje_tiempo = 0
        
        self.lista_ventanas_expandida = True
        self.mostrar_lienzo = True
        self.lienzo_escala = 0.5
        
        self.contador_ventanas = 1
        self.contador_textboxes = 1
        
        self.boton_add_textbox_rect = pygame.Rect(0, 0, 0, 0)
        self.boton_toggle_lista_rect = pygame.Rect(0, 0, 0, 0)
        self.boton_importar_rect = pygame.Rect(0, 0, 0, 0)
        
        print("="*70)
        print("EDITOR UI UNIVERSAL INICIADO")
        print("="*70)
        print("Controles:")
        print("  V: Modo ventanas | T: Modo textboxes")
        print("  N: Nueva ventana | B: Nueva textbox")
        print("  I: Importar JSON | E: Exportar | G: Guardar todo")
        print("  Delete: Eliminar | 1-9: Seleccionar | ESC: Salir")
        print("="*70)
    
    def mostrar_mensaje(self, texto: str):
        self.mensaje = texto
        self.mensaje_tiempo = pygame.time.get_ticks()
        print(f"[INFO] {texto}")
    
    def importar_desde_json(self, ruta_json):
        """Importa ventana desde JSON"""
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ventana_data = data.get("ventana", {})
            nombre = ventana_data.get("nombre", "ventana_importada")
            
            ventana = VentanaUI(
                x=ventana_data.get("x", 100),
                y=ventana_data.get("y", 100),
                ancho=ventana_data.get("ancho", 400),
                alto=ventana_data.get("alto", 300),
                nombre=nombre,
                color_acento=tuple(ventana_data.get("color_acento", [100, 150, 255]))
            )
            ventana.alpha = ventana_data.get("alpha", 200)
            ventana.visible = ventana_data.get("visible", True)
            
            self.ventanas[nombre] = ventana
            self.textboxes[nombre] = []
            
            for tb_data in data.get("textboxes", []):
                tb = TextBox(
                    x=tb_data.get("x", 100),
                    y=tb_data.get("y", 100),
                    ancho=tb_data.get("ancho", 200),
                    alto=tb_data.get("alto", 100),
                    nombre=tb_data.get("nombre", "textbox")
                )
                tb.tipo = tb_data.get("tipo", "lista")
                tb.contenido = tb_data.get("contenido", [])
                tb.fuente_size = tb_data.get("fuente_size", 20)
                tb.color_texto = tuple(tb_data.get("color_texto", [255, 255, 255]))
                tb.alineacion = tb_data.get("alineacion", "left")
                
                scroll_data = tb_data.get("scroll", {})
                tb.scroll_enabled = scroll_data.get("enabled", True)
                tb.items_visibles = scroll_data.get("items_visibles", 5)
                tb.color_scrollbar = tuple(scroll_data.get("color_scrollbar", [100, 100, 255]))
                tb.scroll_offset_y = scroll_data.get("offset_y", 0)
                tb.scroll_offset_x = scroll_data.get("offset_x", 0)
                
                self.textboxes[nombre].append(tb)
            
            self.ventana_seleccionada = nombre
            self.mostrar_mensaje(f"'{nombre}' importada ({len(self.textboxes[nombre])} textboxes)")
            
        except Exception as e:
            self.mostrar_mensaje(f"Error: {e}")
    
    def crear_ventana(self):
        nombre = f"ventana_{self.contador_ventanas}"
        self.contador_ventanas += 1
        
        ventana = VentanaUI(300, 100, 400, 300, nombre, (100, 150, 255))
        self.ventanas[nombre] = ventana
        self.textboxes[nombre] = []
        self.ventana_seleccionada = nombre
        
        self.mostrar_mensaje(f"'{nombre}' creada")
    
    def eliminar_ventana(self):
        if self.ventana_seleccionada and self.ventana_seleccionada in self.ventanas:
            del self.ventanas[self.ventana_seleccionada]
            del self.textboxes[self.ventana_seleccionada]
            self.ventana_seleccionada = None
            self.mostrar_mensaje("Ventana eliminada")
    
    def crear_textbox(self):
        if not self.ventana_seleccionada:
            self.mostrar_mensaje("Selecciona una ventana primero")
            return
        
        ventana = self.ventanas[self.ventana_seleccionada]
        nombre = f"textbox_{self.contador_textboxes}"
        self.contador_textboxes += 1
        
        tb = TextBox(ventana.x + 50, ventana.y + 80, 200, 100, nombre)
        self.textboxes[self.ventana_seleccionada].append(tb)
        self.textbox_seleccionada = tb
        
        self.mostrar_mensaje(f"'{nombre}' creada")
    
    def eliminar_textbox(self):
        if self.textbox_seleccionada and self.ventana_seleccionada:
            self.textboxes[self.ventana_seleccionada].remove(self.textbox_seleccionada)
            self.textbox_seleccionada = None
            self.mostrar_mensaje("TextBox eliminada")
    
    def exportar_ventana(self):
        if not self.ventana_seleccionada:
            self.mostrar_mensaje("Selecciona una ventana primero")
            return
        
        ventana = self.ventanas[self.ventana_seleccionada]
        textboxes = self.textboxes[self.ventana_seleccionada]
        
        data = {
            "ventana": ventana.to_dict(),
            "textboxes": [tb.to_dict() for tb in textboxes]
        }
        
        try:
            ruta = Path(f"src/database/ui/{self.ventana_seleccionada}.json")
            ruta.parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.mostrar_mensaje(f"Exportado: {ruta.name}")
        except Exception as e:
            self.mostrar_mensaje(f"Error: {e}")
    
    def guardar_todo(self):
        for nombre in self.ventanas.keys():
            self.ventana_seleccionada = nombre
            self.exportar_ventana()
        self.mostrar_mensaje("Todas guardadas")
    
    def manejar_eventos(self) -> bool:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            elif evento.type == pygame.VIDEORESIZE:
                self.ancho_actual = evento.w
                self.alto_actual = evento.h
                self.pantalla = pygame.display.set_mode((self.ancho_actual, self.alto_actual), pygame.RESIZABLE)
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                elif evento.key == pygame.K_v:
                    self.modo = "ventanas"
                    self.textbox_seleccionada = None
                    self.mostrar_mensaje("Modo: VENTANAS")
                elif evento.key == pygame.K_t:
                    self.modo = "textboxes"
                    self.mostrar_mensaje("Modo: TEXTBOXES")
                elif evento.key == pygame.K_n:
                    self.crear_ventana()
                elif evento.key == pygame.K_b:
                    self.crear_textbox()
                elif evento.key == pygame.K_i:
                    # Importar pantalla_magia.json por defecto
                    self.importar_desde_json("src/database/ui/pantalla_magia.json")
                elif evento.key == pygame.K_DELETE:
                    if self.modo == "textboxes":
                        self.eliminar_textbox()
                    else:
                        self.eliminar_ventana()
                elif evento.key == pygame.K_g:
                    self.guardar_todo()
                elif evento.key == pygame.K_e:
                    self.exportar_ventana()
                
                # Scroll
                elif self.modo == "textboxes" and self.textbox_seleccionada:
                    tb = self.textbox_seleccionada
                    
                    if evento.key == pygame.K_UP:
                        tb.scroll_offset_y = max(0, tb.scroll_offset_y - 1)
                    elif evento.key == pygame.K_DOWN:
                        lineas_que_caben = max(1, (tb.alto - 20) // (tb.fuente_size + 2))
                        max_scroll = max(0, len(tb.contenido) - lineas_que_caben)
                        tb.scroll_offset_y = min(max_scroll, tb.scroll_offset_y + 1)
                    elif evento.key == pygame.K_LEFT:
                        tb.scroll_offset_x = max(0, tb.scroll_offset_x - 1)
                    elif evento.key == pygame.K_RIGHT:
                        max_len = max(len(linea) for linea in tb.contenido) if tb.contenido else 0
                        tb.scroll_offset_x = min(max(0, max_len - 10), tb.scroll_offset_x + 1)
                
                elif evento.key >= pygame.K_1 and evento.key <= pygame.K_9:
                    idx = evento.key - pygame.K_1
                    nombres = list(self.ventanas.keys())
                    if idx < len(nombres):
                        self.ventana_seleccionada = nombres[idx]
                        self.textbox_seleccionada = None
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if mouse_pos[0] < PANEL_ANCHO:
                        # Panel lateral
                        if hasattr(self, 'boton_toggle_lista_rect') and self.boton_toggle_lista_rect.collidepoint(mouse_pos):
                            self.lista_ventanas_expandida = not self.lista_ventanas_expandida
                        
                        elif hasattr(self, 'checkboxes_ventanas'):
                            for nombre, checkbox_rect in self.checkboxes_ventanas.items():
                                if checkbox_rect.collidepoint(mouse_pos):
                                    self.ventanas[nombre].visible = not self.ventanas[nombre].visible
                                    break
                        
                        elif hasattr(self, 'boton_add_textbox_rect') and self.boton_add_textbox_rect.collidepoint(mouse_pos):
                            if self.ventana_seleccionada:
                                self.crear_textbox()
                        
                        elif hasattr(self, 'boton_importar_rect') and self.boton_importar_rect.collidepoint(mouse_pos):
                            self.importar_desde_json("src/database/ui/pantalla_magia.json")
                    
                    else:
                        # Área de trabajo
                        if self.modo == "textboxes" and self.ventana_seleccionada:
                            for tb in reversed(self.textboxes[self.ventana_seleccionada]):
                                handle = tb.get_handle_en_punto(mouse_pos[0], mouse_pos[1])
                                if handle:
                                    tb.escalando = True
                                    tb.handle_activo = handle
                                    self.textbox_seleccionada = tb
                                    break
                                elif tb.contiene_punto(mouse_pos[0], mouse_pos[1]):
                                    tb.arrastrando = True
                                    tb.offset_x = tb.x - mouse_pos[0]
                                    tb.offset_y = tb.y - mouse_pos[1]
                                    self.textbox_seleccionada = tb
                                    break
                        else:
                            for nombre, ventana in reversed(list(self.ventanas.items())):
                                if not ventana.visible:
                                    continue
                                
                                handle = ventana.get_handle_en_punto(mouse_pos[0], mouse_pos[1])
                                if handle:
                                    ventana.escalando = True
                                    ventana.handle_activo = handle
                                    self.ventana_seleccionada = nombre
                                    break
                                elif ventana.contiene_punto(mouse_pos[0], mouse_pos[1]):
                                    if mouse_pos[1] - ventana.y <= 35:
                                        ventana.arrastrando = True
                                        ventana.offset_x = ventana.x - mouse_pos[0]
                                        ventana.offset_y = ventana.y - mouse_pos[1]
                                        self.ventana_seleccionada = nombre
                                        break
            
            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    for ventana in self.ventanas.values():
                        ventana.arrastrando = False
                        ventana.escalando = False
                    
                    for textboxes_list in self.textboxes.values():
                        for tb in textboxes_list:
                            tb.arrastrando = False
                            tb.escalando = False
            
            elif evento.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                for ventana in self.ventanas.values():
                    if ventana.arrastrando:
                        ventana.x = mouse_pos[0] + ventana.offset_x
                        ventana.y = mouse_pos[1] + ventana.offset_y
                        ventana.actualizar_rect()
                    elif ventana.escalando and ventana.handle_activo:
                        if 'e' in ventana.handle_activo:
                            ventana.ancho = max(200, mouse_pos[0] - ventana.x)
                        elif 'w' in ventana.handle_activo:
                            nuevo_ancho = max(200, ventana.x + ventana.ancho - mouse_pos[0])
                            if nuevo_ancho >= 200:
                                ventana.x = mouse_pos[0]
                                ventana.ancho = nuevo_ancho
                        
                        if 's' in ventana.handle_activo:
                            ventana.alto = max(100, mouse_pos[1] - ventana.y)
                        elif 'n' in ventana.handle_activo:
                            nuevo_alto = max(100, ventana.y + ventana.alto - mouse_pos[1])
                            if nuevo_alto >= 100:
                                ventana.y = mouse_pos[1]
                                ventana.alto = nuevo_alto
                        
                        ventana.actualizar_rect()
                
                for textboxes_list in self.textboxes.values():
                    for tb in textboxes_list:
                        if tb.arrastrando:
                            tb.x = mouse_pos[0] + tb.offset_x
                            tb.y = mouse_pos[1] + tb.offset_y
                            tb.actualizar_rect()
                        elif tb.escalando and tb.handle_activo:
                            if 'e' in tb.handle_activo:
                                tb.ancho = max(100, mouse_pos[0] - tb.x)
                            elif 'w' in tb.handle_activo:
                                nuevo_ancho = max(100, tb.x + tb.ancho - mouse_pos[0])
                                if nuevo_ancho >= 100:
                                    tb.x = mouse_pos[0]
                                    tb.ancho = nuevo_ancho
                            
                            if 's' in tb.handle_activo:
                                tb.alto = max(50, mouse_pos[1] - tb.y)
                            elif 'n' in tb.handle_activo:
                                nuevo_alto = max(50, tb.y + tb.alto - mouse_pos[1])
                                if nuevo_alto >= 50:
                                    tb.y = mouse_pos[1]
                                    tb.alto = nuevo_alto
                            
                            tb.actualizar_rect()
        
        return True
    
    def dibujar_panel_lateral(self):
        pygame.draw.rect(self.pantalla, COLOR_PANEL, (0, 0, PANEL_ANCHO, self.alto_actual))
        
        texto_titulo = self.fuente_titulo.render("UI Editor", True, COLOR_TEXTO)
        self.pantalla.blit(texto_titulo, (20, 20))
        
        modo_texto = f"MODO: {self.modo.upper()}"
        color_modo = COLOR_TEXTBOX if self.modo == "textboxes" else COLOR_VENTANA
        texto_modo = self.fuente_pequena.render(modo_texto, True, color_modo)
        self.pantalla.blit(texto_modo, (20, 60))
        
        y_offset = 100
        
        boton_toggle = pygame.Rect(20, y_offset, PANEL_ANCHO - 40, 30)
        self.boton_toggle_lista_rect = boton_toggle
        
        pygame.draw.rect(self.pantalla, (60, 60, 80), boton_toggle, border_radius=5)
        pygame.draw.rect(self.pantalla, COLOR_TEXTO, boton_toggle, 1, border_radius=5)
        
        icono = "v" if self.lista_ventanas_expandida else ">"
        texto_toggle = self.fuente.render(f"{icono} Ventanas ({len(self.ventanas)})", True, COLOR_TEXTO)
        self.pantalla.blit(texto_toggle, (boton_toggle.x + 10, boton_toggle.y + 5))
        
        y_offset += 40
        
        if self.lista_ventanas_expandida:
            self.checkboxes_ventanas = {}
            for i, (nombre, ventana) in enumerate(self.ventanas.items()):
                checkbox_rect = pygame.Rect(25, y_offset, 18, 18)
                color_check = (100, 200, 100) if ventana.visible else (100, 100, 100)
                pygame.draw.rect(self.pantalla, color_check, checkbox_rect, 2, border_radius=3)
                
                if ventana.visible:
                    pygame.draw.line(self.pantalla, color_check,
                                   (checkbox_rect.x + 3, checkbox_rect.y + 9),
                                   (checkbox_rect.x + 7, checkbox_rect.y + 14), 2)
                    pygame.draw.line(self.pantalla, color_check,
                                   (checkbox_rect.x + 7, checkbox_rect.y + 14),
                                   (checkbox_rect.x + 15, checkbox_rect.y + 4), 2)
                
                color_nombre = COLOR_SELECCION if nombre == self.ventana_seleccionada else COLOR_TEXTO_SEC
                texto_nombre = self.fuente_pequena.render(f"{i+1}. {nombre}", True, color_nombre)
                self.pantalla.blit(texto_nombre, (50, y_offset + 2))
                
                self.checkboxes_ventanas[nombre] = checkbox_rect
                y_offset += 25
            
            y_offset += 10
        
        # Botón importar
        boton_importar = pygame.Rect(20, y_offset, PANEL_ANCHO - 40, 35)
        self.boton_importar_rect = boton_importar
        pygame.draw.rect(self.pantalla, (80, 120, 200), boton_importar, border_radius=8)
        pygame.draw.rect(self.pantalla, COLOR_TEXTO, boton_importar, 2, border_radius=8)
        texto_imp = self.fuente.render("Importar JSON (I)", True, COLOR_TEXTO)
        texto_rect = texto_imp.get_rect(center=boton_importar.center)
        self.pantalla.blit(texto_imp, texto_rect)
        
        y_offset += 45
        
        # Botón añadir textbox
        boton_add_textbox = pygame.Rect(20, y_offset, PANEL_ANCHO - 40, 35)
        self.boton_add_textbox_rect = boton_add_textbox
        
        color_boton = (80, 200, 120) if self.ventana_seleccionada else (100, 100, 100)
        pygame.draw.rect(self.pantalla, color_boton, boton_add_textbox, border_radius=8)
        pygame.draw.rect(self.pantalla, COLOR_TEXTO, boton_add_textbox, 2, border_radius=8)
        
        texto_add = self.fuente.render("+ TextBox (B)", True, COLOR_TEXTO)
        texto_rect = texto_add.get_rect(center=boton_add_textbox.center)
        self.pantalla.blit(texto_add, texto_rect)
        
        # Botones inferiores
        y_botones = self.alto_actual - 250
        botones = [
            ("V - Ventanas", y_botones),
            ("T - TextBoxes", y_botones + 35),
            ("N - Nueva", y_botones + 70),
            ("Delete - Eliminar", y_botones + 105),
            ("G - Guardar", y_botones + 140),
            ("E - Exportar", y_botones + 175),
            ("ESC - Salir", y_botones + 210)
        ]
        
        for texto, y in botones:
            boton_rect = pygame.Rect(15, y, PANEL_ANCHO - 30, 28)
            pygame.draw.rect(self.pantalla, (60, 60, 80), boton_rect, border_radius=5)
            pygame.draw.rect(self.pantalla, COLOR_TEXTO, boton_rect, 1, border_radius=5)
            
            texto_boton = self.fuente_pequena.render(texto, True, COLOR_TEXTO)
            texto_rect = texto_boton.get_rect(center=boton_rect.center)
            self.pantalla.blit(texto_boton, texto_rect)
    
    def dibujar_barra_estado(self):
        barra_rect = pygame.Rect(PANEL_ANCHO, self.alto_actual - 30, 
                                self.ancho_actual - PANEL_ANCHO, 30)
        pygame.draw.rect(self.pantalla, (40, 40, 50), barra_rect)
        
        if self.mensaje and pygame.time.get_ticks() - self.mensaje_tiempo < 3000:
            texto_msg = self.fuente_pequena.render(self.mensaje, True, COLOR_TEXTO)
            self.pantalla.blit(texto_msg, (PANEL_ANCHO + 10, self.alto_actual - 25))
        else:
            info = f"Ventanas: {len(self.ventanas)}"
            if self.ventana_seleccionada:
                info += f" | Actual: {self.ventana_seleccionada}"
                info += f" | TextBoxes: {len(self.textboxes.get(self.ventana_seleccionada, []))}"
            
            texto_info = self.fuente_pequena.render(info, True, COLOR_TEXTO_SEC)
            self.pantalla.blit(texto_info, (PANEL_ANCHO + 10, self.alto_actual - 25))
    
    def dibujar_lienzo_juego(self):
        if not self.mostrar_lienzo:
            return
        
        ancho_escalado = int(LIENZO_JUEGO_ANCHO * self.lienzo_escala)
        alto_escalado = int(LIENZO_JUEGO_ALTO * self.lienzo_escala)
        
        area_trabajo_ancho = self.ancho_actual - PANEL_ANCHO
        area_trabajo_alto = self.alto_actual - 80
        
        lienzo_x = PANEL_ANCHO + (area_trabajo_ancho - ancho_escalado) // 2
        lienzo_y = 40 + (area_trabajo_alto - alto_escalado) // 2
        
        borde_rect = pygame.Rect(lienzo_x - 2, lienzo_y - 2, 
                                ancho_escalado + 4, alto_escalado + 4)
        pygame.draw.rect(self.pantalla, COLOR_LIENZO, borde_rect, 3, border_radius=5)
        
        lienzo_rect = pygame.Rect(lienzo_x, lienzo_y, ancho_escalado, alto_escalado)
        pygame.draw.rect(self.pantalla, (15, 15, 25), lienzo_rect)
        
        texto_dim = self.fuente_pequena.render(
            f"Pantalla: {LIENZO_JUEGO_ANCHO}x{LIENZO_JUEGO_ALTO} ({int(self.lienzo_escala*100)}%)",
            True, COLOR_TEXTO_SEC
        )
        self.pantalla.blit(texto_dim, (lienzo_x, lienzo_y - 20))
    
    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            
            # Fondo
            for y in range(0, self.alto_actual, 2):
                color = (20 + y // 20, 20 + y // 20, 30 + y // 15)
                pygame.draw.line(self.pantalla, color, (PANEL_ANCHO, y), (self.ancho_actual, y))
            
            self.dibujar_lienzo_juego()
            
            # Ventanas
            for nombre, ventana in self.ventanas.items():
                seleccionada = (nombre == self.ventana_seleccionada and self.modo == "ventanas")
                ventana.dibujar(self.pantalla, seleccionada)
            
            # TextBoxes
            for nombre, textboxes in self.textboxes.items():
                for tb in textboxes:
                    seleccionada = (tb == self.textbox_seleccionada and self.modo == "textboxes")
                    tb.dibujar(self.pantalla, seleccionada)
            
            self.dibujar_panel_lateral()
            self.dibujar_barra_estado()
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()
        print("[OK] Editor cerrado")


if __name__ == "__main__":
    editor = EditorUIUniversal()
    editor.ejecutar()
