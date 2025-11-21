"""
========================================
EDITOR DE MAPAS PROFESIONAL - CodeVerso RPG
========================================
Editor completo con:
- Selector de mapas
- Biblioteca de sprites (Héroes, Monstruos, NPCs, Cofres)
- Redimensionamiento con mouse (esquinas)
- Sistema de capas
- Historial de sprites usados
- Guardar/Cargar proyectos

Controles:
- Click Izquierdo: Seleccionar objeto
- Arrastrar: Mover objeto
- Arrastrar esquina: Redimensionar
- Flechas: Mover cámara
- Mouse Rueda: Zoom
- G: Guardar
- CTRL+Z: Deshacer
- ESC: Salir
"""

import pygame
import json
import os
from pathlib import Path
from enum import Enum

# Configuración
ANCHO = 800
ALTO = 600
FPS = 60

# Colores
COLOR_FONDO = (20, 20, 25)
COLOR_GRID = (40, 40, 50)
COLOR_SELECCION = (255, 215, 0)
COLOR_HOVER = (100, 200, 255)
COLOR_TEXTO = (255, 255, 255)
COLOR_PANEL = (30, 30, 40)
COLOR_PANEL_TITULO = (50, 50, 70)
COLOR_BOTON = (60, 60, 80)
COLOR_BOTON_HOVER = (80, 80, 120)
COLOR_BOTON_ACTIVO = (100, 150, 255)

class TipoSprite(Enum):
    """Tipos de sprites disponibles"""
    COFRE = "cofre"
    NPC = "npc"
    HEROE_MAPA = "heroe_mapa"
    HEROE_BATALLA = "heroe_batalla"
    MONSTRUO = "monstruo"
    DECORACION = "decoracion"
    ZONA_BATALLA = "zona_batalla"

class ObjetoMapa:
    """Representa un objeto editable en el mapa (cofre, NPC, etc.)"""
    
    def __init__(self, tipo, x, y, ancho, alto, id_objeto, datos_extra=None):
        self.tipo = tipo  # "cofre", "npc", "zona_batalla", etc.
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.id_objeto = id_objeto
        self.datos_extra = datos_extra or {}
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.arrastrando = False
        self.offset_x = 0
        self.offset_y = 0
    
    def contiene_punto(self, px, py):
        """Verifica si un punto está dentro del objeto"""
        return self.rect.collidepoint(px, py)
    
    def actualizar_rect(self):
        """Actualiza el rect con las coordenadas y tamaño actuales"""
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
    
    def dibujar(self, pantalla, seleccionado=False, hover=False, offset_x=0, offset_y=0):
        """Dibuja el objeto en pantalla con offset de cámara"""
        # Ajustar posición según cámara
        x_pantalla = self.x - offset_x
        y_pantalla = self.y - offset_y
        
        # Solo dibujar si está visible en pantalla
        if (x_pantalla + self.ancho < 0 or x_pantalla > ANCHO or 
            y_pantalla + self.alto < 0 or y_pantalla > ALTO):
            return
        
        # Color según tipo
        if self.tipo == "cofre":
            color_base = (139, 69, 19)  # Marrón
        elif self.tipo == "npc":
            color_base = (0, 128, 255)  # Azul
        elif self.tipo == "zona_batalla":
            color_base = (255, 0, 0)  # Rojo
        else:
            color_base = (128, 128, 128)  # Gris
        
        # Dibujar rectángulo semitransparente
        superficie = pygame.Surface((self.ancho, self.alto))
        superficie.set_alpha(150)
        superficie.fill(color_base)
        pantalla.blit(superficie, (x_pantalla, y_pantalla))
        
        # Borde
        rect_pantalla = pygame.Rect(x_pantalla, y_pantalla, self.ancho, self.alto)
        if seleccionado:
            pygame.draw.rect(pantalla, COLOR_SELECCION, rect_pantalla, 3)
        elif hover:
            pygame.draw.rect(pantalla, COLOR_HOVER, rect_pantalla, 2)
        else:
            pygame.draw.rect(pantalla, color_base, rect_pantalla, 1)
        
        # Texto con info
        fuente = pygame.font.Font(None, 20)
        texto = f"{self.tipo}: {self.id_objeto}"
        texto_surf = fuente.render(texto, True, COLOR_TEXTO)
        pantalla.blit(texto_surf, (x_pantalla + 5, y_pantalla + 5))
        
        # Dimensiones
        dim_texto = f"{self.ancho}x{self.alto}"
        dim_surf = fuente.render(dim_texto, True, COLOR_TEXTO)
        pantalla.blit(dim_surf, (x_pantalla + 5, y_pantalla + self.alto - 20))
    
    def to_dict(self):
        """Convierte el objeto a diccionario para guardar"""
        return {
            "tipo": self.tipo,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "alto": self.alto,
            "id": self.id_objeto,
            "datos_extra": self.datos_extra
        }


class EditorMapa:
    """Editor interactivo de mapas"""
    
    def __init__(self, nombre_mapa, carpeta_mapa):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption(f"Editor de Mapa - {nombre_mapa}")
        self.reloj = pygame.time.Clock()
        
        self.nombre_mapa = nombre_mapa
        self.carpeta_mapa = carpeta_mapa
        self.ruta_json = Path(f"src/database/mapas/{carpeta_mapa}/{nombre_mapa}.json")
        
        # Cargar mapa de fondo
        ruta_imagen = Path(f"assets/maps/{carpeta_mapa}/{nombre_mapa}.jpg")
        if ruta_imagen.exists():
            self.imagen_mapa = pygame.image.load(str(ruta_imagen)).convert()
            print(f"✓ Mapa cargado: {ruta_imagen} | Tamaño: {self.imagen_mapa.get_size()}")
            # NO escalar, mostrar el mapa completo
        else:
            self.imagen_mapa = None
            print(f"⚠️ No se encontró imagen del mapa: {ruta_imagen}")
        
        # Configuración de cámara para mapas grandes
        if self.imagen_mapa:
            self.ancho_mapa = self.imagen_mapa.get_width()
            self.alto_mapa = self.imagen_mapa.get_height()
        else:
            self.ancho_mapa = ANCHO
            self.alto_mapa = ALTO
        
        self.camara_x = 0
        self.camara_y = 0
        self.velocidad_camara = 10
        
        # Lista de objetos en el mapa
        self.objetos = []
        self.objeto_seleccionado = None
        self.objeto_hover = None
        
        # Estado del editor
        self.mostrar_grid = True
        self.cambios_sin_guardar = False
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 18)
        
        # Cargar objetos existentes
        self.cargar_objetos()
        
        print(f"✓ Editor iniciado para: {nombre_mapa}")
        print(f"  Objetos cargados: {len(self.objetos)}")
    
    def cargar_objetos(self):
        """Carga objetos existentes del archivo JSON"""
        if not self.ruta_json.exists():
            print(f"⚠️ No existe archivo JSON, creando nuevo: {self.ruta_json}")
            return
        
        try:
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar cofres
            if "cofres" in data:
                for cofre_data in data["cofres"]:
                    obj = ObjetoMapa(
                        tipo="cofre",
                        x=cofre_data.get("x", 0),
                        y=cofre_data.get("y", 0),
                        ancho=cofre_data.get("ancho", 64),
                        alto=cofre_data.get("alto", 64),
                        id_objeto=cofre_data.get("id", "cofre_1"),
                        datos_extra=cofre_data
                    )
                    self.objetos.append(obj)
            
            # Cargar NPCs (si existen)
            if "npcs" in data:
                for npc_data in data["npcs"]:
                    obj = ObjetoMapa(
                        tipo="npc",
                        x=npc_data.get("x", 0),
                        y=npc_data.get("y", 0),
                        ancho=npc_data.get("ancho", 48),
                        alto=npc_data.get("alto", 64),
                        id_objeto=npc_data.get("id", "npc_1"),
                        datos_extra=npc_data
                    )
                    self.objetos.append(obj)
            
            print(f"✓ Cargados {len(self.objetos)} objetos del mapa")
        
        except Exception as e:
            print(f"❌ Error cargando objetos: {e}")
    
    def guardar_objetos(self):
        """Guarda todos los objetos al archivo JSON"""
        # Organizar por tipo
        cofres = []
        npcs = []
        zonas_batalla = []
        
        for obj in self.objetos:
            datos = obj.to_dict()
            
            if obj.tipo == "cofre":
                cofres.append(datos)
            elif obj.tipo == "npc":
                npcs.append(datos)
            elif obj.tipo == "zona_batalla":
                zonas_batalla.append(datos)
        
        # Crear estructura JSON
        data = {
            "nombre": self.nombre_mapa,
            "carpeta": self.carpeta_mapa,
            "cofres": cofres,
            "npcs": npcs,
            "zonas_batalla": zonas_batalla
        }
        
        # Guardar
        try:
            # Crear directorio si no existe
            self.ruta_json.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Guardado: {len(self.objetos)} objetos en {self.ruta_json}")
            self.cambios_sin_guardar = False
            return True
        
        except Exception as e:
            print(f"❌ Error guardando: {e}")
            return False
    
    def obtener_objeto_en_posicion(self, x, y):
        """Retorna el objeto en la posición del mouse (o None)"""
        # Ajustar coordenadas del mouse con la cámara
        mundo_x = x + self.camara_x
        mundo_y = y + self.camara_y
        
        for obj in reversed(self.objetos):  # Revisar de atrás hacia adelante
            if obj.contiene_punto(mundo_x, mundo_y):
                return obj
        return None
    
    def crear_objeto_nuevo(self, tipo="cofre"):
        """Crea un nuevo objeto en el centro de la pantalla visible"""
        nuevo_id = f"{tipo}_{len([o for o in self.objetos if o.tipo == tipo]) + 1}"
        
        # Crear en el centro de la vista actual (con cámara)
        obj = ObjetoMapa(
            tipo=tipo,
            x=self.camara_x + ANCHO // 2 - 32,
            y=self.camara_y + ALTO // 2 - 32,
            ancho=64,
            alto=64,
            id_objeto=nuevo_id
        )
        
        self.objetos.append(obj)
        self.objeto_seleccionado = obj
        self.cambios_sin_guardar = True
        print(f"✓ Creado: {nuevo_id} en ({obj.x}, {obj.y})")
    
    def duplicar_objeto(self, objeto):
        """Duplica el objeto seleccionado"""
        if not objeto:
            return
        
        nuevo_id = f"{objeto.tipo}_{len([o for o in self.objetos if o.tipo == objeto.tipo]) + 1}"
        
        obj_nuevo = ObjetoMapa(
            tipo=objeto.tipo,
            x=objeto.x + 50,
            y=objeto.y + 50,
            ancho=objeto.ancho,
            alto=objeto.alto,
            id_objeto=nuevo_id,
            datos_extra=objeto.datos_extra.copy()
        )
        
        self.objetos.append(obj_nuevo)
        self.objeto_seleccionado = obj_nuevo
        self.cambios_sin_guardar = True
        print(f"✓ Duplicado: {nuevo_id}")
    
    def eliminar_objeto(self, objeto):
        """Elimina el objeto seleccionado"""
        if objeto in self.objetos:
            self.objetos.remove(objeto)
            print(f"✓ Eliminado: {objeto.id_objeto}")
            self.objeto_seleccionado = None
            self.cambios_sin_guardar = True
    
    def dibujar_grid(self):
        """Dibuja una cuadrícula de referencia sobre el mapa"""
        # Crear superficie semitransparente para la cuadrícula
        grid_surface = pygame.Surface((ANCHO, ALTO))
        grid_surface.set_alpha(80)  # Transparencia
        grid_surface.fill((0, 0, 0))  # Fondo negro semitransparente
        
        # Calcular offset de la cuadrícula basado en la cámara
        grid_size = 50
        offset_x = -self.camara_x % grid_size
        offset_y = -self.camara_y % grid_size
        
        # Dibujar líneas verticales
        for x in range(offset_x, ANCHO, grid_size):
            pygame.draw.line(grid_surface, COLOR_GRID, (x, 0), (x, ALTO), 1)
            
            # Mostrar coordenadas cada 200 píxeles
            mundo_x = x + self.camara_x
            if mundo_x % 200 == 0 and mundo_x != 0:
                fuente = pygame.font.Font(None, 16)
                texto = fuente.render(str(mundo_x), True, (150, 150, 150))
                grid_surface.blit(texto, (x + 2, 2))
        
        # Dibujar líneas horizontales
        for y in range(offset_y, ALTO, grid_size):
            pygame.draw.line(grid_surface, COLOR_GRID, (0, y), (ANCHO, y), 1)
            
            # Mostrar coordenadas cada 200 píxeles
            mundo_y = y + self.camara_y
            if mundo_y % 200 == 0 and mundo_y != 0:
                fuente = pygame.font.Font(None, 16)
                texto = fuente.render(str(mundo_y), True, (150, 150, 150))
                grid_surface.blit(texto, (2, y + 2))
        
        self.pantalla.blit(grid_surface, (0, 0))
    
    def dibujar_panel_info(self):
        """Dibuja panel con información y controles"""
        panel_alto = 150
        panel = pygame.Surface((ANCHO, panel_alto))
        panel.set_alpha(200)
        panel.fill(COLOR_PANEL)
        self.pantalla.blit(panel, (0, ALTO - panel_alto))
        
        y_texto = ALTO - panel_alto + 10
        
        # Título
        texto = self.fuente.render(f"Editor: {self.nombre_mapa}", True, COLOR_TEXTO)
        self.pantalla.blit(texto, (10, y_texto))
        y_texto += 30
        
        # Info del objeto seleccionado
        if self.objeto_seleccionado:
            info = f"Seleccionado: {self.objeto_seleccionado.id_objeto} | Pos: ({self.objeto_seleccionado.x}, {self.objeto_seleccionado.y}) | Tamaño: {self.objeto_seleccionado.ancho}x{self.objeto_seleccionado.alto}"
            texto = self.fuente_pequena.render(info, True, (255, 255, 0))
            self.pantalla.blit(texto, (10, y_texto))
        else:
            texto = self.fuente_pequena.render("Ningún objeto seleccionado", True, (150, 150, 150))
            self.pantalla.blit(texto, (10, y_texto))
        
        y_texto += 25
        
        # Controles
        controles = [
            "Click: Seleccionar | Arrastrar: Mover | +/-: Ancho | W/S: Alto | Flechas: Mover Cámara",
            "N: Nuevo Cofre | D: Duplicar | SUPR: Eliminar | G: Guardar | ESC: Salir"
        ]
        
        for control in controles:
            texto = self.fuente_pequena.render(control, True, COLOR_TEXTO)
            self.pantalla.blit(texto, (10, y_texto))
            y_texto += 20
        
        # Aviso de cambios sin guardar
        if self.cambios_sin_guardar:
            aviso = self.fuente.render("¡CAMBIOS SIN GUARDAR!", True, (255, 100, 100))
            self.pantalla.blit(aviso, (ANCHO - 250, ALTO - panel_alto + 10))
    
    def ejecutar(self):
        """Bucle principal del editor"""
        ejecutando = True
        
        while ejecutando:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Actualizar hover
            self.objeto_hover = self.obtener_objeto_en_posicion(mouse_x, mouse_y)
            
            # Mover cámara con flechas del teclado
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT]:
                self.camara_x = max(0, self.camara_x - self.velocidad_camara)
            if teclas[pygame.K_RIGHT]:
                self.camara_x = min(self.ancho_mapa - ANCHO, self.camara_x + self.velocidad_camara)
            if teclas[pygame.K_UP]:
                self.camara_y = max(0, self.camara_y - self.velocidad_camara)
            if teclas[pygame.K_DOWN]:
                self.camara_y = min(self.alto_mapa - ALTO, self.camara_y + self.velocidad_camara)
            
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    if self.cambios_sin_guardar:
                        print("⚠️ Hay cambios sin guardar. Presiona G para guardar.")
                    ejecutando = False
                
                elif evento.type == pygame.KEYDOWN:
                    # ESC - Salir
                    if evento.key == pygame.K_ESCAPE:
                        if self.cambios_sin_guardar:
                            print("⚠️ Cambios sin guardar. Presiona G para guardar o ESC de nuevo para salir.")
                            self.cambios_sin_guardar = False  # Permitir salir en segundo ESC
                        else:
                            ejecutando = False
                    
                    # G - Guardar
                    elif evento.key == pygame.K_g:
                        self.guardar_objetos()
                    
                    # N - Nuevo cofre
                    elif evento.key == pygame.K_n:
                        self.crear_objeto_nuevo("cofre")
                    
                    # D - Duplicar
                    elif evento.key == pygame.K_d:
                        if self.objeto_seleccionado:
                            self.duplicar_objeto(self.objeto_seleccionado)
                    
                    # SUPR - Eliminar
                    elif evento.key == pygame.K_DELETE:
                        if self.objeto_seleccionado:
                            self.eliminar_objeto(self.objeto_seleccionado)
                    
                    # Ajustar tamaño del objeto seleccionado
                    elif self.objeto_seleccionado:
                        if evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                            self.objeto_seleccionado.ancho += 5
                            self.objeto_seleccionado.actualizar_rect()
                            self.cambios_sin_guardar = True
                        
                        elif evento.key == pygame.K_MINUS:
                            self.objeto_seleccionado.ancho = max(10, self.objeto_seleccionado.ancho - 5)
                            self.objeto_seleccionado.actualizar_rect()
                            self.cambios_sin_guardar = True
                        
                        elif evento.key == pygame.K_w:
                            self.objeto_seleccionado.alto = max(10, self.objeto_seleccionado.alto - 5)
                            self.objeto_seleccionado.actualizar_rect()
                            self.cambios_sin_guardar = True
                        
                        elif evento.key == pygame.K_s:
                            self.objeto_seleccionado.alto += 5
                            self.objeto_seleccionado.actualizar_rect()
                            self.cambios_sin_guardar = True
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Click izquierdo
                        obj = self.obtener_objeto_en_posicion(mouse_x, mouse_y)
                        
                        if obj:
                            self.objeto_seleccionado = obj
                            obj.arrastrando = True
                            # Guardar offset en coordenadas del mundo
                            mundo_x = mouse_x + self.camara_x
                            mundo_y = mouse_y + self.camara_y
                            obj.offset_x = obj.x - mundo_x
                            obj.offset_y = obj.y - mundo_y
                        else:
                            self.objeto_seleccionado = None
                
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if evento.button == 1:  # Soltar click
                        for obj in self.objetos:
                            if obj.arrastrando:
                                obj.arrastrando = False
                                self.cambios_sin_guardar = True
                
                elif evento.type == pygame.MOUSEMOTION:
                    # Arrastrar objeto
                    for obj in self.objetos:
                        if obj.arrastrando:
                            mundo_x = mouse_x + self.camara_x
                            mundo_y = mouse_y + self.camara_y
                            obj.x = mundo_x + obj.offset_x
                            obj.y = mundo_y + obj.offset_y
                            obj.actualizar_rect()
            
            # Dibujar
            self.pantalla.fill(COLOR_FONDO)
            
            # Mapa de fondo con offset de cámara
            if self.imagen_mapa:
                self.pantalla.blit(self.imagen_mapa, (-self.camara_x, -self.camara_y))
            
            # Grid (siempre visible para orientarse)
            self.dibujar_grid()
            
            # Objetos con offset de cámara
            for obj in self.objetos:
                seleccionado = (obj == self.objeto_seleccionado)
                hover = (obj == self.objeto_hover)
                obj.dibujar(self.pantalla, seleccionado, hover, self.camara_x, self.camara_y)
            
            # Panel de información
            self.dibujar_panel_info()
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        pygame.quit()
        print("Editor cerrado.")


# ========================================
# EJECUTAR EDITOR
# ========================================
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║   EDITOR DE MAPAS - CodeVerso RPG      ║
╚════════════════════════════════════════╝
    """)
    
    # Configurar el mapa a editar
    nombre_mapa = "mapa_pradera"  # Sin extensión
    carpeta_mapa = "mundo"
    
    editor = EditorMapa(nombre_mapa, carpeta_mapa)
    editor.ejecutar()
