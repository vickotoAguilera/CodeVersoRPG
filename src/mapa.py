import pygame
import os
import sys 
import json 
from src.config import MAPS_PATH, DATABASE_PATH
from src.cofre import Cofre 

class Mapa:
    # --- 1. EL CONSTRUCTOR (¡MODIFICADO!) ---
    # ¡Ahora pide una "categoria" para saber en qué carpeta buscar!
    def __init__(self, archivo_mapa, categoria_mapa, ancho_pantalla, alto_pantalla):
        print(f"¡Creando el Mapa! Cargando '{categoria_mapa}/{archivo_mapa}'...")
        
        self.ANCHO_PANTALLA = ancho_pantalla
        self.ALTO_PANTALLA = alto_pantalla
        self.nombre_archivo = archivo_mapa 
        self.categoria = categoria_mapa # ¡NUEVO! Guardamos la categoría
        
        # Lista de mapas que son "interiores" (Esto queda igual)
        self.mapas_interiores = [
            "mapa_posada.png",
            "mapa_tienda_items.png",
            "mapa_tienda_magia.png",
            "mapa_herrero.png",
            "mapa_taberna.png"
        ]
        
        # Cargar la imagen del mapa (¡MODIFICADO!)
        try:
            # ¡Ahora busca en la sub-carpeta correcta!
            ruta_mapa = os.path.join(MAPS_PATH, self.categoria, self.nombre_archivo)
            
            if self.nombre_archivo.endswith((".jpg", ".jpeg")):
                self.mapa_img = pygame.image.load(ruta_mapa).convert()
            else:
                self.mapa_img = pygame.image.load(ruta_mapa).convert_alpha()
                
            if self.nombre_archivo in self.mapas_interiores:
                print(f"Detectado mapa interior. ¡Escalando a {self.ANCHO_PANTALLA}x{self.ALTO_PANTALLA}!")
                self.mapa_img = pygame.transform.scale(self.mapa_img, (self.ANCHO_PANTALLA, self.ALTO_PANTALLA))

        except FileNotFoundError:
            print(f"¡ERROR! no se cargo el mapa en la ruta: {ruta_mapa}")
            pygame.quit()
            sys.exit()

        self.mapa_rect = self.mapa_img.get_rect()
        self.mapa_rect.topleft = (0, 0)
        
        self.camara_rect = pygame.Rect(0, 0, self.ANCHO_PANTALLA, self.ALTO_PANTALLA)
        
        self.muros = []
        self.portales = [] 
        self.zonas_batalla = []
        self.cofres = []  # ¡NUEVO! Lista de cofres en el mapa
        
        self.cargar_cofres_db()  # ¡NUEVO! Cargar base de datos de cofres PRIMERO
        self.cargar_datos_mapa()  # Luego cargar datos del mapa (que usa cofres_db)


    # --- ¡MODIFICADO! "EL MOTOR" PARA LEER JSON ---
    def cargar_datos_mapa(self):
        # 1. Averiguamos el nombre del archivo JSON (igual que antes)
        nombre_base = os.path.splitext(self.nombre_archivo)[0]
        nombre_json = f"{nombre_base}.json"
        
        # ¡MODIFICADO! ¡Ahora busca el JSON en la sub-carpeta correcta!
        ruta_json = os.path.join(DATABASE_PATH, "mapas", self.categoria, nombre_json)
        
        print(f"Buscando datos del mapa en: {ruta_json}")

        # 2. Abrimos y leemos el archivo JSON (igual que antes)
        try:
            # --- ¡MODIFICADO! Añadimos encoding='utf-8' ---
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except FileNotFoundError:
            print(f"¡ADVERTENCIA! No se encontró el archivo de datos: {ruta_json}")
            print("El mapa se cargará vacío (sin muros, portales, etc.)")
            return
        except json.JSONDecodeError:
            print(f"¡ERROR! El archivo JSON está mal escrito: {ruta_json}")
            pygame.quit(); sys.exit()

        # 3. "Traducimos" los datos JSON (¡MODIFICADO!)
        
        # Muros (igual que antes)
        if "muros" in datos:
            for muro_data in datos["muros"]:
                muro_rect = pygame.Rect(muro_data['x'], muro_data['y'], muro_data['w'], muro_data['h'])
                self.muros.append(muro_rect)
        
        # Zonas de Batalla (igual que antes)
        if "zonas_batalla" in datos:
            for zona_data in datos["zonas_batalla"]:
                zona_rect = pygame.Rect(zona_data['x'], zona_data['y'], zona_data['w'], zona_data['h'])
                self.zonas_batalla.append(zona_rect)

        # Portales (¡MODIFICADO!)
        if "portales" in datos:
            for portal_data in datos["portales"]:
                caja_rect = pygame.Rect(portal_data['caja']['x'], portal_data['caja']['y'], portal_data['caja']['w'], portal_data['caja']['h'])
                
                # ¡Ahora también guardamos la "categoria_destino"!
                nuevo_portal = {
                    "caja": caja_rect,
                    "mapa_destino": portal_data["mapa_destino"],
                    "categoria_destino": portal_data["categoria_destino"], # ¡NUEVO!
                    "pos_destino": tuple(portal_data["pos_destino"])
                }
                self.portales.append(nuevo_portal)
        
        # ¡NUEVO! Cofres
        if "cofres" in datos:
            for cofre_data in datos["cofres"]:
                id_cofre = cofre_data["id_cofre"]
                x = cofre_data["x"]
                y = cofre_data["y"]
                escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5
                
                # Buscar datos del cofre en la base de datos
                cofre_info = self.cofres_db.get(id_cofre)
                if cofre_info:
                    nuevo_cofre = Cofre(
                        x, y,
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        escala=escala
                    )
                    self.cofres.append(nuevo_cofre)
                else:
                    print(f"¡ADVERTENCIA! Cofre '{id_cofre}' no encontrado en cofres_db.json")
        
        print(f"¡Datos del mapa '{nombre_json}' cargados con éxito!")
        print(f"  > Muros: {len(self.muros)}")
        print(f"  > Zonas: {len(self.zonas_batalla)}")
        print(f"  > Portales: {len(self.portales)}")
        print(f"  > Cofres: {len(self.cofres)}")

    # --- (Las funciones 2, 3, 4 y 5: update_camara, draw, chequear_zona y chequear_portales quedan 100% IGUAL) ---
    # --- 2. EL UPDATE ---
    def update_camara(self, heroe):
        # (esto queda 100% igual)
        self.camara_rect.center = heroe.heroe_rect.center
        if self.camara_rect.left < 0: self.camara_rect.left = 0
        if self.camara_rect.right > self.mapa_img.get_width(): self.camara_rect.right = self.mapa_img.get_width()
        if self.camara_rect.top < 0: self.camara_rect.top = 0
        if self.camara_rect.bottom > self.mapa_img.get_height(): self.camara_rect.bottom = self.mapa_img.get_height()

    # --- 3. EL DRAW ---
    def draw(self, pantalla):
        # (esto queda 100% igual)
        pantalla.blit(self.mapa_img, (0 - self.camara_rect.x, 0 - self.camara_rect.y))
        
        # ¡NUEVO! Dibujar cofres
        for cofre in self.cofres:
            cofre.draw(pantalla, self.camara_rect)
        
        # --- DEBUG: Dibujar cajas (Descomentar para ver) ---
        # for muro in self.muros:
        #     muro_en_pantalla = muro.move(-self.camara_rect.x, -self.camara_rect.y)
        #     pygame.draw.rect(pantalla, (255, 0, 0), muro_en_pantalla, 2) 
        # for zona in self.zonas_batalla:
        #     zona_en_pantalla = zona.move(-self.camara_rect.x, -self.camara_rect.y)
        #     pygame.draw.rect(pantalla, (0, 255, 0), zona_en_pantalla, 2) 
        # for portal in self.portales:
        #     portal_en_pantalla = portal["caja"].move(-self.camara_rect.x, -self.camara_rect.y)
        #     pygame.draw.rect(pantalla, (255, 0, 255), portal_en_pantalla, 2) 

    # --- 4. CHEQUEAR ZONA ---
    def chequear_zona(self, rect_heroe):
        # (esto queda 100% igual)
        for zona in self.zonas_batalla:
            if rect_heroe.colliderect(zona):
                return "bosque" 
        
        for portal in self.portales:
            if rect_heroe.colliderect(portal["caja"]):
                return "segura"
        
        if self.nombre_archivo in self.mapas_interiores or self.nombre_archivo == "mapa_pueblo_final.png":
            return "segura"
            
        return "pradera" 
        
    # --- 5. CHEQUEAR PORTALES ---
    def chequear_portales(self, rect_heroe):
        # (esto queda 100% igual)
        for portal in self.portales:
            if rect_heroe.colliderect(portal["caja"]):
                return portal 
        return None
    
    # ¡NUEVO! --- 6. CARGAR BASE DE DATOS DE COFRES ---
    def cargar_cofres_db(self):
        """Carga la base de datos de cofres desde JSON"""
        ruta_cofres_db = os.path.join(DATABASE_PATH, "cofres_db.json")
        
        try:
            with open(ruta_cofres_db, 'r', encoding='utf-8') as f:
                self.cofres_db = json.load(f)
            print(f"✓ Base de datos de cofres cargada: {len(self.cofres_db)} cofres definidos")
        except FileNotFoundError:
            print(f"¡ADVERTENCIA! No se encontró cofres_db.json en: {ruta_cofres_db}")
            self.cofres_db = {}
        except json.JSONDecodeError as e:
            print(f"¡ERROR! Archivo cofres_db.json malformado: {e}")
            self.cofres_db = {}
    
    # ¡NUEVO! --- 7. CHEQUEAR COFRES CERCANOS ---
    def chequear_cofre_cercano(self, rect_heroe, distancia_interaccion=50):
        """
        Verifica si hay un cofre cerca del héroe.
        
        Args:
            rect_heroe: Rectángulo del héroe
            distancia_interaccion: Distancia máxima para interactuar
        
        Returns:
            Objeto Cofre si hay uno cerca, None si no
        """
        for cofre in self.cofres:
            # Calcular distancia entre héroe y cofre
            dx = rect_heroe.centerx - cofre.rect.centerx
            dy = rect_heroe.centery - cofre.rect.centery
            distancia = (dx**2 + dy**2) ** 0.5
            
            if distancia <= distancia_interaccion:
                return cofre
        
        return None