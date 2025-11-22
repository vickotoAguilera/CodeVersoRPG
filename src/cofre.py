import pygame
import os
from src.config import ASSETS_PATH

class Cofre:
    """
    Clase para manejar cofres interactivos en el mapa.
    Un cofre puede estar: ABIERTO_CON_ITEMS, CERRADO, o VACIO
    """
    
    def __init__(self, x, y, id_cofre, requiere_llave=None, items_contenido=None, escala=1.0, sprite_cerrado=None, sprite_abierto=None):
        """
        Constructor del cofre.
        
        Args:
            x, y: Posición en el mapa
            id_cofre: ID único del cofre (para guardado)
            requiere_llave: ID de la llave necesaria (None si no requiere)
            items_contenido: Diccionario de items {"item_id": cantidad}
            escala: Escala del sprite (1.0 = tamaño original)
            sprite_cerrado: Nombre del archivo sprite cerrado (ej: "cofre_madera_1.png")
            sprite_abierto: Nombre del archivo sprite abierto (ej: "cofre_madera_3.png")
        """
        self.id_cofre = id_cofre
        self.requiere_llave = requiere_llave
        self.items_contenido = items_contenido if items_contenido else {}
        self.escala = escala
        self.sprite_cerrado_path = sprite_cerrado
        self.sprite_abierto_path = sprite_abierto
        
        # Estados del cofre
        self.abierto = False  # Si ya fue abierto alguna vez
        self.vacio = False    # Si ya se recogieron los items
        
        # Cargar sprites del cofre
        self._cargar_sprites()
        
        # Posición y rect de colisión
        self.rect = self.sprite_cerrado.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Sprite actual
        self.sprite_actual = self.sprite_cerrado
    
    def _cargar_sprites(self):
        """Carga los sprites del cofre desde archivos individuales o spritesheet"""
        # Si se proporcionaron rutas de sprites individuales, usarlas
        if self.sprite_cerrado_path and self.sprite_abierto_path:
            try:
                ruta_cerrado = os.path.join(ASSETS_PATH, "sprites", "cofres y demas", self.sprite_cerrado_path)
                ruta_abierto = os.path.join(ASSETS_PATH, "sprites", "cofres y demas", self.sprite_abierto_path)
                
                sprite_cerrado = pygame.image.load(ruta_cerrado).convert_alpha()
                sprite_abierto = pygame.image.load(ruta_abierto).convert_alpha()
                
                # Escalar si es necesario
                if self.escala != 1.0:
                    ancho_cerrado, alto_cerrado = sprite_cerrado.get_size()
                    ancho_abierto, alto_abierto = sprite_abierto.get_size()
                    
                    self.sprite_cerrado = pygame.transform.scale(
                        sprite_cerrado, 
                        (int(ancho_cerrado * self.escala), int(alto_cerrado * self.escala))
                    )
                    self.sprite_abierto = pygame.transform.scale(
                        sprite_abierto,
                        (int(ancho_abierto * self.escala), int(alto_abierto * self.escala))
                    )
                    self.sprite_vacio = self.sprite_abierto  # Usar mismo sprite para vacío
                else:
                    self.sprite_cerrado = sprite_cerrado
                    self.sprite_abierto = sprite_abierto
                    self.sprite_vacio = sprite_abierto  # Usar mismo sprite para vacío
                
                print(f"[OK] Sprites del cofre '{self.id_cofre}' cargados: {self.sprite_cerrado_path}, {self.sprite_abierto_path}")
                return
                
            except FileNotFoundError as e:
                print(f"¡ADVERTENCIA! No se encontraron sprites individuales: {e}")
                print(f"  Intentando cargar desde spritesheet...")
        
        # Fallback: Cargar desde spritesheet (código original)
        try:
            ruta_cofre = os.path.join(ASSETS_PATH, "sprites", "cofres y demas", "cofre.png")
            hoja_completa = pygame.image.load(ruta_cofre).convert_alpha()
            
            # Dimensiones según tu descripción
            # Hoja completa: 700x350
            # Cada estado: 203x275 (aproximadamente)
            ancho_frame = 203
            alto_frame = 275
            
            # Extraer los 3 estados (de izquierda a derecha)
            # Estado 1: Abierto con items (x=0)
            sprite_abierto = hoja_completa.subsurface((0, 0, ancho_frame, alto_frame))
            
            # Estado 2: Cerrado (x=233 aprox, con espacio)
            sprite_cerrado = hoja_completa.subsurface((233, 0, ancho_frame, alto_frame))
            
            # Estado 3: Vacío (x=466 aprox, con espacio)
            sprite_vacio = hoja_completa.subsurface((466, 0, ancho_frame, alto_frame))
            
            # Escalar si es necesario
            if self.escala != 1.0:
                nuevo_ancho = int(ancho_frame * self.escala)
                nuevo_alto = int(alto_frame * self.escala)
                self.sprite_abierto = pygame.transform.scale(sprite_abierto, (nuevo_ancho, nuevo_alto))
                self.sprite_cerrado = pygame.transform.scale(sprite_cerrado, (nuevo_ancho, nuevo_alto))
                self.sprite_vacio = pygame.transform.scale(sprite_vacio, (nuevo_ancho, nuevo_alto))
            else:
                self.sprite_abierto = sprite_abierto
                self.sprite_cerrado = sprite_cerrado
                self.sprite_vacio = sprite_vacio
            
            print(f"[OK] Sprites del cofre '{self.id_cofre}' cargados correctamente")
            
        except FileNotFoundError:
            print(f"¡ERROR! No se encontró el sprite del cofre en: {ruta_cofre}")
            # Crear sprites de fallback (rectángulos de colores)
            tam = int(50 * self.escala)
            self.sprite_abierto = pygame.Surface((tam, tam))
            self.sprite_abierto.fill((255, 215, 0))  # Dorado (abierto)
            self.sprite_cerrado = pygame.Surface((tam, tam))
            self.sprite_cerrado.fill((139, 69, 19))  # Marrón (cerrado)
            self.sprite_vacio = pygame.Surface((tam, tam))
            self.sprite_vacio.fill((105, 105, 105))  # Gris (vacío)
    
    def interactuar(self, grupo_heroes, items_db):
        """
        Intenta abrir el cofre.
        
        Args:
            grupo_heroes: Lista de héroes
            items_db: Base de datos de items para obtener nombres
        
        Returns:
            dict con resultado de la interacción:
            {
                "exito": bool,
                "mensaje": str,
                "nombre_llave_necesaria": str (si requiere llave y no la tiene),
                "items_obtenidos": dict (si exito=True)
            }
        """
        # Si ya está vacío, no hacer nada
        if self.vacio:
            return {
                "exito": False,
                "mensaje": "El cofre está vacío...",
                "items_obtenidos": {}
            }
        
        # Si requiere llave, verificar que el jugador la tenga
        if self.requiere_llave:
            lider = grupo_heroes[0]
            
            # Buscar la llave en inventario normal y especial (SIN CONSUMIRLA)
            tiene_llave = False
            if self.requiere_llave in lider.inventario and lider.inventario[self.requiere_llave] > 0:
                tiene_llave = True
            elif self.requiere_llave in lider.inventario_especiales and lider.inventario_especiales[self.requiere_llave] > 0:
                tiene_llave = True
            
            if not tiene_llave:
                # Obtener el nombre de la llave desde la base de datos
                nombre_llave = "una llave"
                if items_db and self.requiere_llave in items_db:
                    nombre_llave = items_db[self.requiere_llave].get("nombre", "una llave")
                
                return {
                    "exito": False,
                    "mensaje": f"Este cofre está cerrado.",
                    "nombre_llave_necesaria": nombre_llave,
                    "items_obtenidos": {}
                }
            
            # IMPORTANTE: La llave NO se consume, solo se verifica
            print(f"[OK] Llave encontrada: {self.requiere_llave} (no se consume)")
        
        # Abrir el cofre y dar items
        self.abierto = True
        self.sprite_actual = self.sprite_abierto
        
        # Agregar items al inventario del líder
        lider = grupo_heroes[0]
        for item_id, cantidad in self.items_contenido.items():
            # Verificar si es un item especial
            es_especial = False
            if items_db and item_id in items_db:
                item_data = items_db[item_id]
                if item_data.get("tipo") == "Especial":
                    es_especial = True
            
            if es_especial:
                # Usar el método centralizado para items especiales
                lider.agregar_item_especial(item_id, cantidad, items_db, grupo_heroes)
            else:
                # Items normales van al inventario normal
                if item_id in lider.inventario:
                    lider.inventario[item_id] += cantidad
                else:
                    lider.inventario[item_id] = cantidad
                print(f"  -> {item_id} x{cantidad} agregado al inventario")
        
        items_obtenidos = self.items_contenido.copy()
        
        # Marcar como vacío y cambiar sprite
        self.vacio = True
        self.sprite_actual = self.sprite_vacio
        
        return {
            "exito": True,
            "mensaje": "¡Cofre abierto!",
            "items_obtenidos": items_obtenidos
        }
    
    def actualizar_sprite(self):
        """Actualiza el sprite según el estado actual"""
        if self.vacio:
            self.sprite_actual = self.sprite_vacio
        elif self.abierto:
            self.sprite_actual = self.sprite_abierto
        else:
            self.sprite_actual = self.sprite_cerrado
    
    def draw(self, pantalla, camara_rect):
        """Dibuja el cofre en pantalla"""
        # Calcular posición relativa a la cámara
        pos_x = self.rect.x - camara_rect.x
        pos_y = self.rect.y - camara_rect.y
        
        pantalla.blit(self.sprite_actual, (pos_x, pos_y))
    
    def obtener_datos_guardado(self):
        """Retorna los datos del cofre para guardar en el save"""
        return {
            "id_cofre": self.id_cofre,
            "abierto": self.abierto,
            "vacio": self.vacio,
            "x": self.rect.x,
            "y": self.rect.y
        }
    
    def cargar_desde_guardado(self, datos):
        """Carga el estado del cofre desde un save"""
        self.abierto = datos.get("abierto", False)
        self.vacio = datos.get("vacio", False)
        self.actualizar_sprite()
