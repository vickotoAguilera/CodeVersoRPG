import pygame
import os
import sys 
import json 
from src.config import MAPS_PATH, DATABASE_PATH, MAPAS_INTERIORES
from src.cofre import Cofre 

class Mapa:
    # --- 1. EL CONSTRUCTOR (¡MODIFICADO!) ---
    # ¡Ahora pide una "categoria" para saber en qué carpeta buscar!
    def __init__(self, archivo_mapa, categoria_mapa, ancho_pantalla, alto_pantalla, estado_cofres=None, tiempo_juego=0.0):
        print(f"¡Creando el Mapa! Cargando '{categoria_mapa}/{archivo_mapa}'...")
        
        self.ANCHO_PANTALLA = ancho_pantalla
        self.ALTO_PANTALLA = alto_pantalla
        self.nombre_archivo = archivo_mapa 
        self.categoria = categoria_mapa # ¡NUEVO! Guardamos la categoría
        
        # NUEVO: Sistema de persistencia de cofres con recuperación
        self.estado_cofres_guardado = estado_cofres if estado_cofres is not None else {}
        self.tiempo_juego_actual = tiempo_juego
        # Lista de mapas que son "interiores" (centralizada en config)
        self.mapas_interiores = MAPAS_INTERIORES
        
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
                orig_img = pygame.image.load(ruta_elegida).convert()
            else:
                orig_img = pygame.image.load(ruta_elegida).convert_alpha()

            # Guardar el nombre de archivo con extensión real (opcional)
            self.nombre_archivo = os.path.basename(ruta_elegida)

            # Guardar tamaño original y calcular factores de escala (por defecto 1.0)
            orig_w, orig_h = orig_img.get_size()
            self.scale_x = 1.0
            self.scale_y = 1.0

            if self.nombre_archivo in self.mapas_interiores:
                print(f"Detectado mapa interior. ¡Escalando a {self.ANCHO_PANTALLA}x{self.ALTO_PANTALLA}!")
                self.scale_x = float(self.ANCHO_PANTALLA) / float(orig_w) if orig_w else 1.0
                self.scale_y = float(self.ALTO_PANTALLA) / float(orig_h) if orig_h else 1.0
                self.mapa_img = pygame.transform.scale(orig_img, (self.ANCHO_PANTALLA, self.ALTO_PANTALLA))
            else:
                self.mapa_img = orig_img

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
        self.spawns_ids = {}  # mapeo id -> (x,y)
        self.cofres = []  # ¡NUEVO! Lista de cofres en el mapa
        self.debug_draw = False
        
        self.cargar_cofres_db()  # ¡NUEVO! Cargar base de datos de cofres PRIMERO
        self.cargar_datos_mapa()  # Luego cargar datos del mapa (que usa cofres_db)


    # --- ¡MODIFICADO! "EL MOTOR" PARA LEER JSON ---
    def cargar_datos_mapa(self):
        # 1. Averiguamos el nombre del archivo JSON
        nombre_base = os.path.splitext(self.nombre_archivo)[0]
        
        # ¡NUEVO! PRIORIDAD 1: Intentar cargar desde mapas_unificados/
        nombre_unificado = f"{nombre_base}_unificado.json"
        ruta_unificado = os.path.join(DATABASE_PATH, "mapas_unificados", nombre_unificado)
        
        datos = None
        ruta_cargada = None
        
        # Intentar cargar archivo unificado primero
        if os.path.exists(ruta_unificado):
            try:
                with open(ruta_unificado, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                ruta_cargada = ruta_unificado
                print(f"[UNIFICADO] Cargando desde: {ruta_unificado}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] Archivo unificado mal formado: {ruta_unificado}")
                print(f"  Error: {e}")
                datos = None
            except Exception as e:
                print(f"[ERROR] No se pudo leer archivo unificado: {e}")
                datos = None
        
        # PRIORIDAD 2: Si no hay archivo unificado, buscar en mapas/{categoria}/
        if datos is None:
            nombre_json = f"{nombre_base}.json"
            ruta_json = os.path.join(DATABASE_PATH, "mapas", self.categoria, nombre_json)
            
            if os.path.exists(ruta_json):
                try:
                    with open(ruta_json, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    ruta_cargada = ruta_json
                    print(f"[PARCIAL] Cargando desde: {ruta_json}")
                except json.JSONDecodeError as e:
                    print(f"[ERROR] El archivo JSON está mal escrito: {ruta_json}")
                    print(f"  Error: {e}")
                    pygame.quit(); sys.exit()
                except Exception as e:
                    print(f"[ERROR] No se pudo leer: {e}")
                    datos = None
        
        # PRIORIDAD 3: Intentar resolver mediante el índice maps_index.json
        if datos is None:
            ruta_indice = os.path.join(DATABASE_PATH, 'maps_index.json')
            if os.path.exists(ruta_indice):
                try:
                    with open(ruta_indice, 'r', encoding='utf-8') as fi:
                        entradas = json.load(fi)
                    for e in entradas:
                        if e.get('id') == nombre_base or os.path.splitext(os.path.basename(e.get('ruta_json','')))[0] == nombre_base:
                            posible = e.get('ruta_json')
                            if posible and os.path.exists(posible):
                                try:
                                    with open(posible, 'r', encoding='utf-8') as f:
                                        datos = json.load(f)
                                    ruta_cargada = posible
                                    print(f"[INDICE] Cargado desde índice: {posible}")
                                    break
                                except Exception:
                                    datos = None
                except Exception as e:
                    print(f"[!] Error leyendo maps_index.json: {e}")
        
        # Si no se encontró ningún archivo, advertir y salir
        if datos is None:
            print(f"[ADVERTENCIA] No se encontró archivo de datos para '{nombre_base}'")
            print(f"  Intentado:")
            print(f"    1. {ruta_unificado}")
            if 'ruta_json' in locals():
                print(f"    2. {ruta_json}")
            print(f"    3. Índice de mapas")
            print("El mapa se cargará vacío (sin muros, portales, etc.)")
            return

        # 3. "Traducimos" los datos JSON (¡MODIFICADO!)
        # Helper local para escalar coordenadas si el mapa fue escalado
        def sx(val):
            try:
                return int(val * getattr(self, 'scale_x', 1.0))
            except Exception:
                return int(val)

        def sy(val):
            try:
                return int(val * getattr(self, 'scale_y', 1.0))
            except Exception:
                return int(val)
        
        # Muros (ahora soportamos rect y poly)
        if "muros" in datos:
            for muro_data in datos["muros"]:
                try:
                    tipo = muro_data.get('tipo', 'rect')
                    if tipo == 'poly' or muro_data.get('tipo') == 'poly':
                        # Extraer lista de puntos
                        pts_raw = muro_data.get('puntos') or muro_data.get('puntos_xy') or muro_data.get('puntos_list')
                        if not pts_raw and 'puntos' in muro_data:
                            pts_raw = muro_data['puntos']
                        if not pts_raw:
                            print(f"¡ADVERTENCIA! Muro poligonal sin puntos: {muro_data}")
                            continue
                        pts = []
                        xs = []
                        ys = []
                        for p in pts_raw:
                            if isinstance(p, (list, tuple)) and len(p) >= 2:
                                x_raw, y_raw = p[0], p[1]
                            elif isinstance(p, dict) and 'x' in p and 'y' in p:
                                x_raw, y_raw = p['x'], p['y']
                            else:
                                continue
                            x_s = sx(x_raw); y_s = sy(y_raw)
                            pts.append((x_s, y_s))
                            xs.append(x_s); ys.append(y_s)
                        if not pts:
                            print(f"¡ADVERTENCIA! Puntos inválidos para muro poligonal: {muro_data}")
                            continue
                        minx, maxx = min(xs), max(xs)
                        miny, maxy = min(ys), max(ys)
                        rect_bbox = pygame.Rect(int(minx), int(miny), int(maxx - minx), int(maxy - miny))
                        self.muros.append({"tipo": "poly", "puntos": pts, "rect": rect_bbox})
                    else:
                        x = muro_data.get('x')
                        y = muro_data.get('y')
                        w = muro_data.get('w', muro_data.get('width', 0))
                        h = muro_data.get('h', muro_data.get('height', 0))
                        if x is None or y is None:
                            pos = muro_data.get('pos')
                            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                                x, y = pos[0], pos[1]
                        if x is None or y is None:
                            print(f"¡ADVERTENCIA! Muro sin posición válida: {muro_data}")
                            continue
                        rect = pygame.Rect(sx(x), sy(y), sx(w) if w is not None else 0, sy(h) if h is not None else 0)
                        self.muros.append({"tipo": "rect", "rect": rect})
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
                    zona_rect = pygame.Rect(sx(x), sy(y), sx(w) if w is not None else 0, sy(h) if h is not None else 0)
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
                        caja = portal_data['caja']
                        caja_rect = pygame.Rect(
                            sx(caja.get('x', 0)),
                            sy(caja.get('y', 0)),
                            sx(caja.get('w', caja.get('width', 0))),
                            sy(caja.get('h', caja.get('height', 0)))
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
                            # Escalar bbox
                            caja_rect = pygame.Rect(sx(minx), sy(miny), sx(maxx - minx), sy(maxy - miny))
                    except Exception:
                        caja_rect = None

                # 3) Si viene con x,y y opcional w,h
                if caja_rect is None and 'x' in portal_data and 'y' in portal_data:
                    x = portal_data.get('x')
                    y = portal_data.get('y')
                    w = portal_data.get('w', portal_data.get('width', 16))
                    h = portal_data.get('h', portal_data.get('height', 16))
                    try:
                        caja_rect = pygame.Rect(sx(x), sy(y), sx(w), sy(h))
                    except Exception:
                        caja_rect = None

                # 4) Fallback: evitar crash creando rect 1x1 muy pequeño fuera de pantalla (se puede ajustar)
                if caja_rect is None:
                    print(f"¡ADVERTENCIA! Portal sin 'caja' ni 'puntos' en JSON; usando fallback en (0,0,1,1). Datos: {portal_data}")
                    caja_rect = pygame.Rect(0, 0, 1, 1)

                # Campos opcionales con fallback
                mapa_dest = portal_data.get("mapa_destino")
                categoria_dest = portal_data.get("categoria_destino", self.categoria)
                pos_dest_raw = portal_data.get("pos_destino")
                pos_dest = tuple(pos_dest_raw) if pos_dest_raw else None

                nuevo_portal = {
                    "caja": caja_rect,
                    "mapa_destino": mapa_dest,
                    "categoria_destino": categoria_dest,
                    "pos_destino": pos_dest,
                    "spawn_destino_id": portal_data.get("spawn_destino_id")
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
                    coord = (sx(int(x)), sy(int(y)))
                    self.spawns.append(coord)
                    # Si el spawn tiene un id en el JSON, guardarlo en el mapeo
                    if isinstance(s, dict) and s.get('id'):
                        self.spawns_ids[s.get('id')] = coord
        
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
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        escala=escala
                    )
                    self.cofres.append(nuevo_cofre)
                    
                    # NUEVO: Aplicar estado guardado si existe, verificando recuperación
                    if self.nombre_archivo in self.estado_cofres_guardado:
                        estado_cofre = self.estado_cofres_guardado[self.nombre_archivo].get(id_cofre)
                        if estado_cofre:
                            tiempo_apertura = estado_cofre.get("tiempo_apertura", 0.0)
                            tiempo_transcurrido = self.tiempo_juego_actual - tiempo_apertura
                            
                            # Importar constante de recuperación desde main
                            TIEMPO_RECUPERACION = 10  # TESTING: 10 segundos (cambiar a 3600 para 1 hora real)
                            
                            if tiempo_transcurrido >= TIEMPO_RECUPERACION:
                                # Cofre recuperado: NO aplicar estado guardado
                                print(f"[Cofre] '{id_cofre}' RECUPERADO (pasaron {tiempo_transcurrido:.1f}s)")
                                # Eliminar del estado guardado
                                del self.estado_cofres_guardado[self.nombre_archivo][id_cofre]
                            else:
                                # Cofre aún no se recupera: aplicar estado guardado
                                nuevo_cofre.cargar_desde_guardado(estado_cofre)
                                nuevo_cofre.actualizar_sprite()
                                tiempo_restante = TIEMPO_RECUPERACION - tiempo_transcurrido
                                print(f"[Cofre] '{id_cofre}' cargado (recupera en {tiempo_restante:.1f}s)")
                else:
                    print(f"¡ADVERTENCIA! Cofre '{id_cofre}' no encontrado en cofres_db.json")
        
        print(f"¡Datos del mapa cargados con éxito desde: {ruta_cargada}!")
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
                if isinstance(muro, dict):
                    if muro.get('tipo') == 'rect':
                        r = muro['rect'].move(-self.camara_rect.x, -self.camara_rect.y)
                        pygame.draw.rect(pantalla, (255, 0, 0), r, 2)
                    elif muro.get('tipo') == 'poly':
                        pts = [(p[0] - self.camara_rect.x, p[1] - self.camara_rect.y) for p in muro.get('puntos', [])]
                        if len(pts) >= 3:
                            pygame.draw.polygon(pantalla, (255, 0, 0), pts, 2)
                        # también dibujar bbox
                        bbox = muro.get('rect')
                        if bbox:
                            bbox_s = bbox.move(-self.camara_rect.x, -self.camara_rect.y)
                            pygame.draw.rect(pantalla, (255, 120, 120), bbox_s, 1)
                else:
                    # compatibilidad: si es un Rect
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
                datos_completos = json.load(f)
            # Extraer solo el diccionario de cofres_mapa
            self.cofres_db = datos_completos.get("cofres_mapa", {})
            print(f"[OK] Base de datos de cofres cargada: {len(self.cofres_db)} cofres definidos")
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