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
        
        # Cargar la imagen del mapa (más robusto: prueba varias extensiones)
        try:
            # ¡Ahora busca en la sub-carpeta correcta!
            ruta_base = os.path.join(MAPS_PATH, self.categoria, self.nombre_archivo)
            ruta_elegida = None

            # 1) Si la ruta exacta existe, úsala
            if os.path.exists(ruta_base):
                ruta_elegida = ruta_base
            else:
                # 2) Probar con extensiones comunes
                for ext in ('.png', '.jpg', '.jpeg'):
                    candidate = ruta_base if ruta_base.lower().endswith(ext) else ruta_base + ext
                    if os.path.exists(candidate):
                        ruta_elegida = candidate
                        break

            # 3) Si aún no, buscar cualquier archivo en la carpeta con mismo nombre base
            if ruta_elegida is None:
                dirpath = os.path.dirname(ruta_base)
                base = os.path.splitext(os.path.basename(self.nombre_archivo))[0]
                if os.path.isdir(dirpath):
                    for f in os.listdir(dirpath):
                        if os.path.splitext(f)[0] == base:
                            ruta_elegida = os.path.join(dirpath, f)
                            break

            # 4) Si no encontramos nada, lanzar FileNotFoundError
            if ruta_elegida is None:
                raise FileNotFoundError()

            # Cargar según la extensión (jpg/jpeg -> convert, otros -> convert_alpha)
            ext_lower = os.path.splitext(ruta_elegida)[1].lower()
            if ext_lower in ('.jpg', '.jpeg'):
                self.mapa_img = pygame.image.load(ruta_elegida).convert()
            else:
                self.mapa_img = pygame.image.load(ruta_elegida).convert_alpha()

            # Guardar el nombre de archivo con extensión real (opcional)
            self.nombre_archivo = os.path.basename(ruta_elegida)

            if self.nombre_archivo in self.mapas_interiores:
                print(f"Detectado mapa interior. ¡Escalando a {self.ANCHO_PANTALLA}x{self.ALTO_PANTALLA}!")
                self.mapa_img = pygame.transform.scale(self.mapa_img, (self.ANCHO_PANTALLA, self.ALTO_PANTALLA))

        except FileNotFoundError:
            tried = ruta_base
            print(f"¡ERROR! no se cargo el mapa en la ruta: {tried} (no se encontró archivo con extensiones comunes)")
            pygame.quit()
            sys.exit()

        self.mapa_rect = self.mapa_img.get_rect()
        self.mapa_rect.topleft = (0, 0)
        
        self.camara_rect = pygame.Rect(0, 0, self.ANCHO_PANTALLA, self.ALTO_PANTALLA)
        
        self.muros = []
        self.portales = [] 
        self.zonas_batalla = []
        self.spawns = []
        self.cofres = []  # ¡NUEVO! Lista de cofres en el mapa
        self.debug_draw = False
        
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
                try:
                    x = muro_data.get('x')
                    y = muro_data.get('y')
                    w = muro_data.get('w', muro_data.get('width', 0))
                    h = muro_data.get('h', muro_data.get('height', 0))
                    if x is None or y is None:
                        # intentar 'pos' como [x,y]
                        pos = muro_data.get('pos')
                        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                            x, y = pos[0], pos[1]
                    if x is None or y is None:
                        print(f"¡ADVERTENCIA! Muro sin posición válida: {muro_data}")
                        continue
                    muro_rect = pygame.Rect(x, y, w, h)
                    self.muros.append(muro_rect)
                except Exception:
                    print(f"¡ADVERTENCIA! Error al leer muro: {muro_data}")
        
        # Zonas de Batalla (igual que antes)
        if "zonas_batalla" in datos:
            for zona_data in datos["zonas_batalla"]:
                try:
                    x = zona_data.get('x')
                    y = zona_data.get('y')
                    w = zona_data.get('w', zona_data.get('width', 0))
                    h = zona_data.get('h', zona_data.get('height', 0))
                    if x is None or y is None:
                        pos = zona_data.get('pos')
                        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                            x, y = pos[0], pos[1]
                    if x is None or y is None:
                        print(f"¡ADVERTENCIA! Zona de batalla sin posición válida: {zona_data}")
                        continue
                    zona_rect = pygame.Rect(x, y, w, h)
                    self.zonas_batalla.append(zona_rect)
                except Exception:
                    print(f"¡ADVERTENCIA! Error al leer zona de batalla: {zona_data}")

        # Portales (más tolerante: acepta 'caja', 'puntos' o solo 'x','y')
        if "portales" in datos:
            for portal_data in datos["portales"]:
                caja_rect = None

                # 1) Si viene con 'caja' (rect clásico)
                if 'caja' in portal_data and isinstance(portal_data['caja'], dict):
                    try:
                        caja_rect = pygame.Rect(
                            portal_data['caja']['x'],
                            portal_data['caja']['y'],
                            portal_data['caja']['w'],
                            portal_data['caja']['h']
                        )
                    except Exception:
                        caja_rect = None

                # 2) Si viene con 'puntos' (polígono) -> calcular bbox
                if caja_rect is None and 'puntos' in portal_data:
                    try:
                        pts = portal_data['puntos']
                        xs = []
                        ys = []
                        for p in pts:
                            # soportar [x,y] o {'x':..,'y':..}
                            if isinstance(p, (list, tuple)) and len(p) >= 2:
                                xs.append(p[0]); ys.append(p[1])
                            elif isinstance(p, dict) and 'x' in p and 'y' in p:
                                xs.append(p['x']); ys.append(p['y'])
                        if xs and ys:
                            minx, maxx = min(xs), max(xs)
                            miny, maxy = min(ys), max(ys)
                            caja_rect = pygame.Rect(minx, miny, maxx - minx, maxy - miny)
                    except Exception:
                        caja_rect = None

                # 3) Si viene con x,y y opcional w,h
                if caja_rect is None and 'x' in portal_data and 'y' in portal_data:
                    x = portal_data.get('x')
                    y = portal_data.get('y')
                    w = portal_data.get('w', portal_data.get('width', 16))
                    h = portal_data.get('h', portal_data.get('height', 16))
                    try:
                        caja_rect = pygame.Rect(x, y, w, h)
                    except Exception:
                        caja_rect = None

                # 4) Fallback: evitar crash creando rect 1x1 muy pequeño fuera de pantalla (se puede ajustar)
                if caja_rect is None:
                    print(f"¡ADVERTENCIA! Portal sin 'caja' ni 'puntos' en JSON; usando fallback en (0,0,1,1). Datos: {portal_data}")
                    caja_rect = pygame.Rect(0, 0, 1, 1)

                # Campos opcionales con fallback
                mapa_dest = portal_data.get("mapa_destino")
                categoria_dest = portal_data.get("categoria_destino", self.categoria)
                pos_dest = tuple(portal_data.get("pos_destino", (0, 0))) if portal_data.get("pos_destino") else None

                nuevo_portal = {
                    "caja": caja_rect,
                    "mapa_destino": mapa_dest,
                    "categoria_destino": categoria_dest,
                    "pos_destino": pos_dest
                }
                self.portales.append(nuevo_portal)
        # Spawns (puntos donde aparecen los héroes)
        if "spawns" in datos:
            for s in datos["spawns"]:
                x = None; y = None
                if isinstance(s, dict):
                    if 'x' in s and 'y' in s:
                        x, y = s['x'], s['y']
                    elif 'pos' in s:
                        pos = s['pos']
                        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                            x, y = pos[0], pos[1]
                    elif 'puntos' in s:
                        try:
                            pts = s['puntos']
                            xs = [p[0] if isinstance(p, (list, tuple)) else p.get('x') for p in pts]
                            ys = [p[1] if isinstance(p, (list, tuple)) else p.get('y') for p in pts]
                            if xs and ys:
                                minx, maxx = min(xs), max(xs)
                                miny, maxy = min(ys), max(ys)
                                x = (minx + maxx)//2; y = (miny + maxy)//2
                        except Exception:
                            x = None; y = None
                elif isinstance(s, (list, tuple)) and len(s) >= 2:
                    x, y = s[0], s[1]

                if x is not None and y is not None:
                    self.spawns.append((int(x), int(y)))
        
        # ¡NUEVO! Cofres
        if "cofres" in datos:
            for cofre_data in datos["cofres"]:
                # Soportar varias claves posibles para el id del cofre
                id_cofre = cofre_data.get("id_cofre") or cofre_data.get("id") or cofre_data.get("cofre_id") or cofre_data.get("tipo")

                # Extraer posición: preferir x,y; luego 'pos' como [x,y]; luego bbox/points
                x = None; y = None
                if 'x' in cofre_data and 'y' in cofre_data:
                    x = cofre_data.get('x'); y = cofre_data.get('y')
                elif 'pos' in cofre_data:
                    pos = cofre_data.get('pos')
                    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                        x, y = pos[0], pos[1]
                    elif isinstance(pos, dict) and 'x' in pos and 'y' in pos:
                        x, y = pos['x'], pos['y']
                elif 'puntos' in cofre_data:
                    # usar bbox del polígono y poner el cofre en el centro
                    try:
                        pts = cofre_data['puntos']
                        xs = [p[0] if isinstance(p, (list, tuple)) else p.get('x') for p in pts]
                        ys = [p[1] if isinstance(p, (list, tuple)) else p.get('y') for p in pts]
                        if xs and ys:
                            minx, maxx = min(xs), max(xs)
                            miny, maxy = min(ys), max(ys)
                            x = (minx + maxx) // 2
                            y = (miny + maxy) // 2
                    except Exception:
                        x = None; y = None

                escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5

                # Si no tenemos id o posición suficiente, avisar y saltar
                if not id_cofre:
                    print(f"¡ADVERTENCIA! Entrada de cofre sin 'id_cofre' ni alternativa encontrada: {cofre_data}")
                    continue
                if x is None or y is None:
                    print(f"¡ADVERTENCIA! Cofre '{id_cofre}' sin posición válida, se salta: {cofre_data}")
                    continue

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
        
        # --- DEBUG: Dibujar cajas si está activado ---
        if getattr(self, 'debug_draw', False):
            for muro in self.muros:
                muro_en_pantalla = muro.move(-self.camara_rect.x, -self.camara_rect.y)
                pygame.draw.rect(pantalla, (255, 0, 0), muro_en_pantalla, 2)
            for zona in self.zonas_batalla:
                zona_en_pantalla = zona.move(-self.camara_rect.x, -self.camara_rect.y)
                pygame.draw.rect(pantalla, (0, 255, 0), zona_en_pantalla, 2)
            for portal in self.portales:
                portal_en_pantalla = portal["caja"].move(-self.camara_rect.x, -self.camara_rect.y)
                pygame.draw.rect(pantalla, (255, 0, 255), portal_en_pantalla, 2)
            # dibujar spawns
            for s in self.spawns:
                spawn_rect = pygame.Rect(s[0]-4, s[1]-4, 8, 8).move(-self.camara_rect.x, -self.camara_rect.y)
                pygame.draw.rect(pantalla, (0, 0, 255), spawn_rect, 2)

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