import pygame
import os
import sys
import copy # para clonar los stats de los heroes
import random 
import json 
from src.config import MONSTRUOS_SPRITES_PATH, BACKGROUNDS_PATH, DATABASE_PATH 
from src.monstruo import Monstruo
from src.texto_flotante import TextoFlotante
from src.heroe import Heroe 
from src.pantalla_magia import PantallaMagia
from src.pantalla_items import PantallaItems
from src.pantalla_lista_habilidades import PantallaListaHabilidades
from src.pantalla_victoria import PantallaVictoria

class Batalla:
    
    # --- 1. EL CONSTRUCTOR (¡"RECABLEADO" (MODIFICADO)!) ---
    # ¡Ahora "pilla" (recibe) el cursor_img_bkn BKN! (Paso 56.6)
    def __init__(self, ancho_pantalla, alto_pantalla, grupo_heroes_obj, zona_actual, cursor_img_bkn):
        print(f"¡Batalla iniciada! Zona: {zona_actual}")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        
        self.grupo_heroes = grupo_heroes_obj 

        # --- Cargar Fondo de Batalla (Sin cambios) ---
        try:
            ruta_fondo = os.path.join(BACKGROUNDS_PATH, "pelea_pradera.png") 
            fondo_img_orig = pygame.image.load(ruta_fondo).convert()
            self.fondo_img = pygame.transform.scale(fondo_img_orig, (self.ANCHO, self.ALTO))
        except FileNotFoundError:
            print(f"¡ERROR! No se encontró el fondo de batalla: {ruta_fondo}")
            self.fondo_img = pygame.Surface((self.ANCHO, self.ALTO)); self.fondo_img.fill((0, 0, 0))

        # --- "Pillamos" (Cargamos) las "Enciclopedias" (Sin cambios) ---
        ruta_monstruos_db = os.path.join(DATABASE_PATH, "monstruos_db.json")
        ruta_magia_db = os.path.join(DATABASE_PATH, "magia_db.json")
        ruta_items_db = os.path.join(DATABASE_PATH, "items_db.json")
        ruta_habilidades_db = os.path.join(DATABASE_PATH, "habilidades_db.json")
        
        self.MONSTER_STATS_DB = self._cargar_json(ruta_monstruos_db)
        self.MAGIA_DB = self._cargar_json(ruta_magia_db)
        self.ITEMS_DB = self._cargar_json(ruta_items_db)
        self.HABILIDADES_DB = self._cargar_json(ruta_habilidades_db)

        # --- Lógica de Creación de Múltiples Monstruos (Sin cambios) ---
        self.monstruos_en_batalla = [] 
        self.monstruos_sprite_group = pygame.sprite.Group() 
        self.monstruos_ui_lista = {} 
        ruta_ecosistema = os.path.join(DATABASE_PATH, "monstruos", f"{zona_actual}.json")
        datos_ecosistema = self._cargar_json(ruta_ecosistema)
        if datos_ecosistema is None:
            ruta_ecosistema = os.path.join(DATABASE_PATH, "monstruos", "default.json")
            datos_ecosistema = self._cargar_json(ruta_ecosistema)
        num_monstruos = random.randint(1, 4) 
        posiciones_monstruos = self.calcular_posiciones_monstruos(num_monstruos)
        if datos_ecosistema and "encuentros" in datos_ecosistema and self.MONSTER_STATS_DB:
            for i in range(num_monstruos):
                id_monstruo_elegido = random.choice(datos_ecosistema["encuentros"])
                stats_del_monstruo = self.MONSTER_STATS_DB.get(id_monstruo_elegido)
                if stats_del_monstruo:
                    stats_unicas = stats_del_monstruo.copy()
                    nuevo_monstruo = Monstruo(**stats_unicas)
                    pos_idx = min(i, len(posiciones_monstruos) - 1)
                    x, y = posiciones_monstruos[pos_idx]
                    nuevo_monstruo.establecer_posicion_batalla(x, y)
                    self.monstruos_en_batalla.append(nuevo_monstruo)
                    self.monstruos_sprite_group.add(nuevo_monstruo) 
                    if nuevo_monstruo.nombre in self.monstruos_ui_lista:
                        self.monstruos_ui_lista[nuevo_monstruo.nombre] += 1
                    else:
                        self.monstruos_ui_lista[nuevo_monstruo.nombre] = 1
                else:
                    print(f"¡ERROR! No se encontraron stats para '{id_monstruo_elegido}'.")
        if not self.monstruos_en_batalla:
            stats_fallback = self.MONSTER_STATS_DB.get("slime")
            if stats_fallback:
                stats_unicas = stats_fallback.copy()
                nuevo_monstruo = Monstruo(**stats_unicas)
                x, y = posiciones_monstruos[0]
                nuevo_monstruo.establecer_posicion_batalla(x, y)
                self.monstruos_en_batalla.append(nuevo_monstruo)
                self.monstruos_sprite_group.add(nuevo_monstruo)
                self.monstruos_ui_lista[nuevo_monstruo.nombre] = 1
            else:
                pygame.quit(); sys.exit()
        
        pos_heroe_x = self.ANCHO - (self.ANCHO // 4)
        pos_heroe_y_base = self.ALTO // 2 - 30 
        pos_heroe_y_salto = 60 
        for i, heroe in enumerate(self.grupo_heroes):
            heroe.establecer_posicion_batalla(pos_heroe_x, pos_heroe_y_base + (i * pos_heroe_y_salto))
            
        # --- Fuentes (Sin cambios) ---
        pygame.font.init() 
        self.fuente = pygame.font.Font(None, 20) 
        self.fuente_pequena = pygame.font.Font(None, 15) 
        self.fuente_stats = pygame.font.Font(None, 18) 
        self.fuente_cursor_targeting = pygame.font.Font(None, 30) # (¡"Pilla" (Usa) el "fallback" (alternativa) BKN!)

        # --- LÓGICA DEL MENÚ (¡ACTUALIZADO!) ---
        self.opciones_menu = ["Atacar", "Habilidades", "Objeto", "Huir"]
        self.opcion_seleccionada = 0
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 150 
        
        # --- Máquina de Estados (Sin cambios) ---
        self.estado_batalla = "INICIAR_RONDA" 
        
        # --- "Motores" (Engines) de UI (Sin cambios) ---
        self.pantalla_magia_activa = None
        self.pantalla_items_activa = None
        self.pantalla_habilidades_activa = None  # ¡NUEVO!
        
        # --- "Cerebros" (Acciones) Pendientes (Sin cambios) ---
        self.accion_magia_pendiente = None
        self.accion_item_pendiente = None
        self.accion_habilidad_pendiente = None  # ¡NUEVO!
        
        self.mensaje_batalla = None 
        self.tiempo_mensaje = 0
        self.heroe_murio = False 
        
        self.cola_de_turnos = [] 
        self.actor_actual = None
        self.monstruo_atacante_actual = None 
        
        # --- Variables de Targeting (¡"RECABLEADO" (MODIFICADO)!) ---
        self.monstruo_seleccionado_idx = 0
        self.heroe_seleccionado_idx = 0 
        
        # --- ¡NUEVO BKN! "Guardamos" (Almacenamos) el cursor (Paso 56.6) ---
        self.cursor_img = cursor_img_bkn 
        # ¡"Guardamos" (Almacenamos) el ">" "grande" BKN como "fallback" (alternativa)!
        self.cursor_targeting_surf = self.fuente_cursor_targeting.render(">", True, (255, 255, 0))
        
        # --- Colores y Geometría (Sin cambios) ---
        self.COLOR_CAJA = (0, 0, 139) 
        self.COLOR_BORDE = (255, 255, 255) 
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0) 
        self.UI_BORDER_RADIUS = 12 
        panel_altura = 100 
        panel_padding = 20 
        self.panel_principal_rect = pygame.Rect(
            panel_padding, 
            self.ALTO - panel_altura - panel_padding, 
            self.ANCHO - (panel_padding * 2), 
            panel_altura
        )
        self.pane_comandos_x = self.panel_principal_rect.x + 40
        self.pane_comandos_y_base = self.panel_principal_rect.y + 15 
        self.pane_comandos_y_salto = 22 
        self.pane_monstruo_x = self.panel_principal_rect.centerx - 100
        self.pane_monstruo_y_base = self.panel_principal_rect.y + 15 
        self.pane_monstruo_y_salto = 20 
        self.pane_heroe_x = self.panel_principal_rect.right - 250 
        self.pane_heroe_y_base = self.panel_principal_rect.y + 15 
        self.pane_heroe_y_salto = 20 
        
        self.textos_flotantes = []
        self.pantalla_victoria_activa = None 

    # --- Función _cargar_json (Sin cambios) ---
    def _cargar_json(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"¡ERROR DE BATALLA! No se encontró el archivo JSON: {ruta_archivo}")
            return None
        except json.JSONDecodeError:
            print(f"¡ERROR DE BATALLA! El archivo JSON está malformado: {ruta_archivo}")
            return None

    # --- Función calcular_posiciones_monstruos (Sin cambios) ---
    def calcular_posiciones_monstruos(self, num_monstruos):
        centro_x = self.ANCHO // 3 - 10
        centro_y = self.ALTO // 2 - 50
        offset_x_atras = 80 
        offset_x_adelante = 30 
        offset_y_grande = 120 
        offset_y_pequena = 80 
        posiciones = []
        if num_monstruos == 1:
            posiciones = [(centro_x, centro_y)]
        elif num_monstruos == 2:
            posiciones = [
                (centro_x, centro_y - offset_y_pequena // 2),
                (centro_x, centro_y + offset_y_pequena // 2)
            ]
        elif num_monstruos == 3:
            posiciones = [
                (centro_x + offset_x_adelante, centro_y),
                (centro_x - offset_x_atras, centro_y - offset_y_grande // 2),
                (centro_x - offset_x_atras, centro_y + offset_y_grande // 2)
            ]
        elif num_monstruos >= 4:
            posiciones = [
                (centro_x + offset_x_adelante, centro_y - offset_y_pequena // 2),
                (centro_x + offset_x_adelante, centro_y + offset_y_pequena // 2),
                (centro_x - offset_x_atras, centro_y - offset_y_grande // 2),
                (centro_x - offset_x_atras, centro_y + offset_y_grande // 2)
            ]
        return posiciones

    # --- crear_cola_de_turnos (Sin cambios) ---
    def crear_cola_de_turnos(self):
        print("--- ¡INICIANDO NUEVA RONDA! ---")
        self.cola_de_turnos.clear()
        lista_de_actores = [] # Lista temporal para ordenar
        
        # 1. Añadir héroes vivos a la lista
        for heroe in self.grupo_heroes:
            if not heroe.esta_muerto():
                # Guardamos al actor Y su velocidad
                lista_de_actores.append((heroe, heroe.velocidad))
                
        # 2. Añadir monstruos vivos a la lista
        for monstruo in self.monstruos_en_batalla:
            if not monstruo.esta_muerto():
                # (Por ahora los monstruos no tienen velocidad, usamos 5 como base)
                # (Podemos añadir 'velocidad' a monstruos_db.json más adelante)
                velocidad_monstruo = getattr(monstruo, "velocidad", 5)
                lista_de_actores.append((monstruo, velocidad_monstruo))
        
        # 3. ¡La Magia! Ordenar la lista
        # Usamos 'sort' para ordenar la lista en el sitio.
        # 'key=lambda actor: actor[1]' le dice que ordene usando el segundo ítem (la velocidad).
        # 'reverse=True' hace que el número MÁS ALTO (más rápido) vaya PRIMERO.
        lista_de_actores.sort(key=lambda actor: actor[1], reverse=True)
        
        # 4. Crear la cola de turnos final (solo con los nombres/objetos)
        self.cola_de_turnos = [actor[0] for actor in lista_de_actores]
        
        print("--- ¡Cola de Turnos Creada y Ordenada por Velocidad! ---")
        for i, actor in enumerate(self.cola_de_turnos):
            nombre = getattr(actor, "nombre_en_juego", getattr(actor, "nombre", "???"))
            print(f"  Turno {i+1}: {nombre} (Vel: {lista_de_actores[i][1]})")

    # --- 2. EL UPDATE (¡"RECABLEADO" (MODIFICADO)!) ---
    def update(self, teclas, tiempo_actual):
        
        #bucle de batalla de victoria
        if self.estado_batalla == "victoria":
            if self.pantalla_victoria_activa:
                self.pantalla_victoria_activa.update(teclas)
                return None 
        
        # 1. Actualizar textos flotantes (Sin cambios)
        for texto in self.textos_flotantes:
            texto.update()
        self.textos_flotantes = [t for t in self.textos_flotantes if not t.esta_muerto()]

        # 2. Revisar si hay un mensaje (victoria/derrota) (Sin cambios)
        if self.mensaje_batalla:
            if tiempo_actual - self.tiempo_mensaje > 1500: 
                if self.heroe_murio:
                    pygame.quit(); sys.exit()
                else:
                    return "mapa" 
            return None 

        # 3. Revisar condiciones de fin de batalla (Sin cambios)
        monstruos_vivos = [m for m in self.monstruos_en_batalla if not m.esta_muerto()]
        heroes_vivos = [h for h in self.grupo_heroes if not h.esta_muerto()]
        
        # --- ¡INICIO DE LA MODIFICACIÓN (Paso 4.4)! ---
        if not monstruos_vivos:
            # Si ya estamos en el estado VICTORIA, no hagas nada, solo espera.
            if self.estado_batalla == "VICTORIA":
                return None 
                
            if self.estado_batalla != "FIN_BATALLA":
                print("¡Batalla Ganada! Calculando recompensas...")
                
                # 1. Almacenar stats ANTIGUOS (para la pantalla de "Level Up")
                stats_heroes_antes = {}
                for heroe in heroes_vivos:
                    # Usamos copy.copy() para una copia superficial de las stats
                    stats_heroes_antes[heroe.nombre_en_juego] = {
                        "nivel": heroe.nivel,
                        "hp_max": heroe.HP_max,
                        "mp_max": heroe.MP_max,
                        "fuerza": heroe.fuerza,
                        "defensa": heroe.defensa,
                        "inteligencia": heroe.inteligencia,
                        "espiritu": heroe.espiritu
                    }

                # 2. Calcular recompensas totales
                total_xp_ganada = 0
                total_oro_ganado = 0
                for monstruo in self.monstruos_en_batalla:
                    total_xp_ganada += monstruo.xp_otorgada
                    total_oro_ganado += monstruo.oro_otorgado
                print(f"Recompensas Totales: {total_xp_ganada} XP, {total_oro_ganado} Oro!")

                # 3. Distribuir recompensas y detectar "Level Ups"
                heroes_que_subieron_stats = []
                
                if heroes_vivos: 
                    for heroe in heroes_vivos:
                        # heroe.ganar_experiencia ahora devuelve True si subió de nivel
                        subio_de_nivel = heroe.ganar_experiencia(total_xp_ganada)
                        
                        if subio_de_nivel:
                            print(f"¡{heroe.nombre_en_juego} ha subido de nivel y será mostrado!")
                            # Guardamos el objeto héroe (con stats NUEVAS)
                            # y el diccionario de stats ANTIGUAS
                            heroes_que_subieron_stats.append({
                                "heroe": heroe,
                                "stats_antes": stats_heroes_antes[heroe.nombre_en_juego]
                            })
                    
                    # Asignar el oro al líder
                    heroes_vivos[0].oro += total_oro_ganado
                    print(f"Oro añadido al líder! (Total: {heroes_vivos[0].oro})")
                
                # 4. Cambiar al estado de VICTORIA y crear la pantalla
                self.estado_batalla = "VICTORIA" # ¡NUEVO ESTADO!
                self.pantalla_victoria_activa = PantallaVictoria(
                    self.ANCHO, self.ALTO, self.cursor_img,
                    self.grupo_heroes, 
                    heroes_que_subieron_stats, # ¡Enviamos la lista de héroes que subieron!
                    total_xp_ganada,
                    total_oro_ganado
                )
                self.monstruos_ui_lista.clear() 
                
            return None 
        # --- FIN DE LA MODIFICACIÓN (Paso 4.4)! ---

        if not heroes_vivos: 
            if self.estado_batalla != "FIN_BATALLA":
                self.mensaje_batalla = "HAS MUERTO!"
                self.tiempo_mensaje = tiempo_actual
                self.heroe_murio = True 
                self.estado_batalla = "FIN_BATALLA" 
            return None 
        
        # --- 4. Lógica de Estados (Sin cambios) ---
        
        if self.estado_batalla == "INICIAR_RONDA":
            self.crear_cola_de_turnos()
            self.estado_batalla = "PROCESAR_TURNO"
        
        elif self.estado_batalla == "PROCESAR_TURNO":
            if not self.cola_de_turnos:
                self.estado_batalla = "INICIAR_RONDA"
            else:
                self.actor_actual = self.cola_de_turnos.pop(0)
                
                # Procesar efectos DOT/HOT al inicio del turno
                if hasattr(self.actor_actual, 'procesar_efectos_turno'):
                    # Guardar efectos antes de procesarlos
                    efectos_copia = []
                    for efecto in self.actor_actual.efectos_activos:
                        efectos_copia.append({
                            "tipo": efecto["tipo"],
                            "valor": efecto["valor"],
                            "es_mp": efecto.get("es_mp", False)
                        })
                    
                    # Procesar efectos
                    mensajes_efectos = self.actor_actual.procesar_efectos_turno()
                    
                    # Generar textos flotantes para cada efecto procesado
                    for efecto in efectos_copia:
                        tipo = efecto["tipo"]
                        valor = efecto["valor"]
                        
                        # Determinar posición y color
                        if isinstance(self.actor_actual, Heroe):
                            pos_x = self.actor_actual.pos_actual_x
                            pos_y = self.actor_actual.pos_actual_y - 50
                        else:  # Monstruo
                            pos_x = self.actor_actual.rect.centerx
                            pos_y = self.actor_actual.rect.top - 30
                        
                        # Determinar color según tipo de efecto
                        if "DOT" in tipo:
                            color = (255, 100, 100)  # Rojo para DOT
                            texto = f"-{valor}"
                        elif "HOT" in tipo:
                            if efecto.get("es_mp", False):
                                color = (100, 150, 255)  # Azul para MP
                                texto = f"+{valor} MP"
                            else:
                                color = (100, 255, 100)  # Verde para HP
                                texto = f"+{valor}"
                        else:
                            continue
                        
                        texto_flotante = TextoFlotante(texto, pos_x, pos_y, color)
                        self.textos_flotantes.append(texto_flotante)
                    
                    for mensaje in mensajes_efectos:
                        print(mensaje)
                
                if isinstance(self.actor_actual, Heroe):
                    if self.actor_actual.esta_muerto():
                        self.estado_batalla = "PROCESAR_TURNO" 
                    else:
                        print(f"¡Turno de {self.actor_actual.nombre_clase}!")
                        self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                        self.opcion_seleccionada = 0 
                
                elif isinstance(self.actor_actual, Monstruo):
                    if self.actor_actual.esta_muerto():
                        self.estado_batalla = "PROCESAR_TURNO" 
                    else:
                        self.ejecutar_ataque_monstruo(self.actor_actual, tiempo_actual)
                        self.estado_batalla = "RESOLVIENDO_ACCION"
        
        elif self.estado_batalla == "ESPERANDO_INPUT_HEROE":
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                if teclas[pygame.K_DOWN]: 
                    self.opcion_seleccionada = (self.opcion_seleccionada + 1 ) % len(self.opciones_menu)
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]: 
                    self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_menu)
                    self.tiempo_ultimo_input = tiempo_actual
        
        elif self.estado_batalla == "JUGADOR_ELIGE_MAGIA":
            if self.pantalla_magia_activa:
                self.pantalla_magia_activa.update(teclas)
        
        elif self.estado_batalla == "JUGADOR_ELIGE_ITEM":
            if self.pantalla_items_activa:
                self.pantalla_items_activa.update(teclas)
        
        elif self.estado_batalla == "JUGADOR_ELIGE_HABILIDAD":
            if self.pantalla_habilidades_activa:
                self.pantalla_habilidades_activa.update(teclas)

        elif self.estado_batalla == "HEROE_ELIGE_MONSTRUO":
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                num_monstruos_vivos = len(monstruos_vivos)
                if num_monstruos_vivos == 0:
                     self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                     return None
                
                if teclas[pygame.K_RIGHT] or teclas[pygame.K_DOWN]:
                    self.monstruo_seleccionado_idx = (self.monstruo_seleccionado_idx + 1) % num_monstruos_vivos
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_LEFT] or teclas[pygame.K_UP]:
                    self.monstruo_seleccionado_idx = (self.monstruo_seleccionado_idx - 1) % num_monstruos_vivos
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_ESCAPE]: 
                    # --- (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
                    if self.accion_magia_pendiente:
                        self.estado_batalla = "JUGADOR_ELIGE_MAGIA"
                        # ¡"Enchufado" (Agregado) el cursor BKN!
                        self.pantalla_magia_activa = PantallaMagia(self.ANCHO, self.ALTO, self.actor_actual, self.MAGIA_DB, self.cursor_img)
                        self.accion_magia_pendiente = None
                    elif self.accion_habilidad_pendiente:
                        self.estado_batalla = "JUGADOR_ELIGE_HABILIDAD"
                        self.pantalla_habilidades_activa = PantallaListaHabilidades(self.ANCHO, self.ALTO, self.actor_actual, self.HABILIDADES_DB, self.cursor_img)
                        self.accion_habilidad_pendiente = None
                    else:
                        self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    self.tiempo_ultimo_input = tiempo_actual

        elif self.estado_batalla == "JUGADOR_ELIGE_ALIADO":
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                num_heroes_vivos = len(heroes_vivos)
                if num_heroes_vivos == 0:
                     self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                     return None
                
                if teclas[pygame.K_DOWN]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx + 1) % num_heroes_vivos
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_UP]:
                    self.heroe_seleccionado_idx = (self.heroe_seleccionado_idx - 1) % num_heroes_vivos
                    self.tiempo_ultimo_input = tiempo_actual
                elif teclas[pygame.K_ESCAPE]: 
                    # --- (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
                    if self.accion_magia_pendiente:
                        self.estado_batalla = "JUGADOR_ELIGE_MAGIA"
                        # ¡"Enchufado" (Agregado) el cursor BKN!
                        self.pantalla_magia_activa = PantallaMagia(self.ANCHO, self.ALTO, self.actor_actual, self.MAGIA_DB, self.cursor_img)
                        self.accion_magia_pendiente = None
                    elif self.accion_item_pendiente:
                        self.estado_batalla = "JUGADOR_ELIGE_ITEM"
                        # ¡"Enchufado" (Agregado) el cursor BKN!
                        self.pantalla_items_activa = PantallaItems(self.ANCHO, self.ALTO, self.actor_actual, self.ITEMS_DB, self.cursor_img)
                        self.accion_item_pendiente = None
                    elif self.accion_habilidad_pendiente:
                        self.estado_batalla = "JUGADOR_ELIGE_HABILIDAD"
                        self.pantalla_habilidades_activa = PantallaListaHabilidades(self.ANCHO, self.ALTO, self.actor_actual, self.HABILIDADES_DB, self.cursor_img)
                        self.accion_habilidad_pendiente = None
                    else:
                        self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    self.tiempo_ultimo_input = tiempo_actual

        elif self.estado_batalla == "RESOLVIENDO_ACCION":
            if self.accion_item_pendiente:
                self.accion_item_pendiente = None 
                self.estado_batalla = "PROCESAR_TURNO" 
                return None 

            if self.actor_actual:
                animacion_terminada = self.actor_actual.update_animacion_ataque(tiempo_actual)
                if animacion_terminada:
                    self.actualizar_lista_ui_monstruos() 
                    heroes_vivos_check = [h for h in self.grupo_heroes if not h.esta_muerto()]
                    if not heroes_vivos_check:
                        self.estado_batalla = "FIN_BATALLA" 
                    else:
                        self.estado_batalla = "PROCESAR_TURNO" 
            else:
                self.estado_batalla = "PROCESAR_TURNO"
                
        return None 

    # --- 3. UPDATE_INPUT (¡"RECABLEADO" (MODIFICADO)!) ---
    def update_input(self, tecla, tiempo_actual):
        #canal input para la pantalla victoria
        
        if self.estado_batalla == "VICTORIA":
            if self.pantalla_victoria_activa:
                accion_victoria = self.pantalla_victoria_activa.update_input(tecla)
                
                # Si la pantalla de victoria nos dice que terminó...
                if accion_victoria == "cerrar_pantalla":
                    # Re-utilizamos la lógica antigua de "fin de batalla"
                    # para volver al mapa después de 1.5 seg.
                    self.mensaje_batalla = "¡Batalla terminada!" 
                    self.tiempo_mensaje = tiempo_actual
                    self.estado_batalla = "FIN_BATALLA"
                    self.pantalla_victoria_activa = None
                    return None
            return None # Detenemos la ejecución aquí
        # --- FIN Canal Victoria ---
                
        
        estados_permitidos = [
            "ESPERANDO_INPUT_HEROE", 
            "HEROE_ELIGE_MONSTRUO", 
            "JUGADOR_ELIGE_ALIADO",
            "JUGADOR_ELIGE_MAGIA",
            "JUGADOR_ELIGE_ITEM",
            "JUGADOR_ELIGE_HABILIDAD"  # ¡NUEVO!
        ]
        if self.estado_batalla not in estados_permitidos:
            return None

        # [CANAL 1: Input del Menú Principal (Atacar, Magia, etc)]
        if self.estado_batalla == "ESPERANDO_INPUT_HEROE" and tecla == pygame.K_RETURN:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                self.tiempo_ultimo_input = tiempo_actual
                
                opcion = self.opciones_menu[self.opcion_seleccionada]
                resultado_accion = self.seleccionar_opcion(opcion, self.actor_actual) 
                
                if resultado_accion == "mapa":
                    self.mensaje_batalla = "¡Escapaste a salvo!"
                    self.tiempo_mensaje = pygame.time.get_ticks()
                    self.estado_batalla = "FIN_BATALLA"
                
                if resultado_accion == "iniciar_targeting_monstruo":
                    monstruos_vivos = [m for m in self.monstruos_en_batalla if not m.esta_muerto()]
                    if not monstruos_vivos:
                         self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    else:
                        self.estado_batalla = "HEROE_ELIGE_MONSTRUO"
                        self.monstruo_seleccionado_idx = 0 
                
                # --- (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
                if resultado_accion == "iniciar_seleccion_magia":
                    print("¡Abriendo menú de Magia!")
                    # ¡"Enchufado" (Agregado) el cursor BKN!
                    self.pantalla_magia_activa = PantallaMagia(self.ANCHO, self.ALTO, self.actor_actual, self.MAGIA_DB, self.cursor_img)
                    self.estado_batalla = "JUGADOR_ELIGE_MAGIA"
                
                if resultado_accion == "iniciar_seleccion_item":
                    print("¡Abriendo menú de Items!")
                    # ¡"Enchufado" (Agregado) el cursor BKN!
                    self.pantalla_items_activa = PantallaItems(self.ANCHO, self.ALTO, self.actor_actual, self.ITEMS_DB, self.cursor_img)
                    self.estado_batalla = "JUGADOR_ELIGE_ITEM"
                
                if resultado_accion == "iniciar_seleccion_habilidad":
                    print(f"¡Abriendo menú de Habilidades para {self.actor_actual.nombre_en_juego}!")
                    # Solo mostrar habilidades del héroe actual
                    self.pantalla_habilidades_activa = PantallaListaHabilidades(self.ANCHO, self.ALTO, self.actor_actual, self.HABILIDADES_DB, self.cursor_img)
                    self.estado_batalla = "JUGADOR_ELIGE_HABILIDAD"
                    
        # [CANAL 2: Input del Menú de Magia (Cura, Piro, etc)]
        elif self.estado_batalla == "JUGADOR_ELIGE_MAGIA" and self.pantalla_magia_activa:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                resultado_magia = self.pantalla_magia_activa.update_input(tecla)
                
                if resultado_magia == "volver":
                    print("¡Cerrando menú de Magia!")
                    self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    self.pantalla_magia_activa = None
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif isinstance(resultado_magia, dict) and resultado_magia.get("accion") == "lanzar_magia":
                    magia_data = resultado_magia["magia_data"]
                    self.accion_magia_pendiente = magia_data 
                    self.pantalla_magia_activa = None
                    
                    if magia_data["target"] == "Aliado":
                        self.estado_batalla = "JUGADOR_ELIGE_ALIADO"
                        self.heroe_seleccionado_idx = 0 
                    elif magia_data["target"] == "Enemigo":
                        self.estado_batalla = "HEROE_ELIGE_MONSTRUO"
                        self.monstruo_seleccionado_idx = 0 
                    
                    self.tiempo_ultimo_input = tiempo_actual
        
        # [CANAL 3: Input del Menú de Items (Poción, Éter, etc)]
        elif self.estado_batalla == "JUGADOR_ELIGE_ITEM" and self.pantalla_items_activa:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                resultado_item = self.pantalla_items_activa.update_input(tecla)
                
                if resultado_item == "volver":
                    print("¡Cerrando menú de Items!")
                    self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    self.pantalla_items_activa = None
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif isinstance(resultado_item, dict) and resultado_item.get("accion") == "usar_item":
                    item_data = resultado_item["item_data"]
                    self.accion_item_pendiente = item_data 
                    self.pantalla_items_activa = None
                    
                    if item_data["target"] == "Aliado":
                        self.estado_batalla = "JUGADOR_ELIGE_ALIADO"
                        self.heroe_seleccionado_idx = 0 
                    
                    self.tiempo_ultimo_input = tiempo_actual
        
        # [CANAL 3.5: Input del Menú de Habilidades]
        elif self.estado_batalla == "JUGADOR_ELIGE_HABILIDAD" and self.pantalla_habilidades_activa:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                resultado_habilidad = self.pantalla_habilidades_activa.update_input(tecla)
                
                if resultado_habilidad == "cerrar":
                    print("¡Cerrando menú de Habilidades!")
                    self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    self.pantalla_habilidades_activa = None
                    self.tiempo_ultimo_input = tiempo_actual
                
                elif isinstance(resultado_habilidad, dict) and resultado_habilidad.get("accion") == "usar_habilidad":
                    habilidad_data = resultado_habilidad["habilidad"]
                    heroe_usuario = resultado_habilidad["heroe"]
                    
                    # Verificar que el héroe tenga suficiente MP
                    if heroe_usuario.MP_actual < habilidad_data["costo_mp"]:
                        print(f"¡{heroe_usuario.nombre_en_juego} no tiene suficiente MP!")
                        self.tiempo_ultimo_input = tiempo_actual
                        return None
                    
                    self.accion_habilidad_pendiente = habilidad_data
                    self.pantalla_habilidades_activa = None
                    
                    # Determinar target según el alcance de la habilidad
                    alcance = habilidad_data.get("alcance", "Un Enemigo")
                    
                    if "Enemigo" in alcance:
                        if "Todos" in alcance:
                            # AoE enemigos - ejecutar directamente
                            monstruos_vivos = [m for m in self.monstruos_en_batalla if not m.esta_muerto()]
                            self.ejecutar_habilidad_aoe(heroe_usuario, monstruos_vivos, habilidad_data, tiempo_actual)
                            self.accion_habilidad_pendiente = None
                            self.estado_batalla = "RESOLVIENDO_ACCION"
                        else:
                            # Un solo enemigo - ir a targeting
                            self.estado_batalla = "HEROE_ELIGE_MONSTRUO"
                            self.monstruo_seleccionado_idx = 0
                    
                    elif "Aliado" in alcance:
                        if "Todos" in alcance:
                            # AoE aliados - ejecutar directamente
                            heroes_vivos = [h for h in self.grupo_heroes if not h.esta_muerto()]
                            self.ejecutar_habilidad_aoe(heroe_usuario, heroes_vivos, habilidad_data, tiempo_actual)
                            self.accion_habilidad_pendiente = None
                            self.estado_batalla = "RESOLVIENDO_ACCION"
                        else:
                            # Un solo aliado - ir a targeting
                            self.estado_batalla = "JUGADOR_ELIGE_ALIADO"
                            self.heroe_seleccionado_idx = 0
                    
                    elif "Usuario" in alcance:
                        # Habilidad en sí mismo
                        self.ejecutar_habilidad_heroe(heroe_usuario, heroe_usuario, habilidad_data, tiempo_actual)
                        self.accion_habilidad_pendiente = None
                        self.estado_batalla = "RESOLVIENDO_ACCION"
                    
                    self.tiempo_ultimo_input = tiempo_actual
        
        # [CANAL 4: Input de Targeting de Monstruo]
        elif self.estado_batalla == "HEROE_ELIGE_MONSTRUO" and tecla == pygame.K_RETURN:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                self.tiempo_ultimo_input = tiempo_actual
                
                monstruos_vivos = [m for m in self.monstruos_en_batalla if not m.esta_muerto()]
                if monstruos_vivos and self.monstruo_seleccionado_idx < len(monstruos_vivos):
                    monstruo_objetivo = monstruos_vivos[self.monstruo_seleccionado_idx]
                    
                    if self.accion_magia_pendiente:
                        self.ejecutar_magia_heroe(self.actor_actual, monstruo_objetivo, self.accion_magia_pendiente, tiempo_actual)
                        self.accion_magia_pendiente = None 
                    elif self.accion_habilidad_pendiente:
                        self.ejecutar_habilidad_heroe(self.actor_actual, monstruo_objetivo, self.accion_habilidad_pendiente, tiempo_actual)
                        self.accion_habilidad_pendiente = None
                    else:
                        self.ejecutar_ataque_heroe(self.actor_actual, monstruo_objetivo, tiempo_actual)
                    
                    if monstruo_objetivo.esta_muerto():
                        nuevos_vivos = len([m for m in self.monstruos_en_batalla if not m.esta_muerto()])
                        self.monstruo_seleccionado_idx = max(0, min(self.monstruo_seleccionado_idx, nuevos_vivos - 1))
                        self.actualizar_lista_ui_monstruos()

                    self.estado_batalla = "RESOLVIENDO_ACCION" 
                else:
                    self.estado_batalla = "ESPERANDO_INPUT_HEROE"

        # [CANAL 5: Input de Targeting de Aliado]
        elif self.estado_batalla == "JUGADOR_ELIGE_ALIADO" and tecla == pygame.K_RETURN:
            if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
                self.tiempo_ultimo_input = tiempo_actual
                
                heroes_vivos = [h for h in self.grupo_heroes if not h.esta_muerto()]
                if heroes_vivos and self.heroe_seleccionado_idx < len(heroes_vivos):
                    heroe_objetivo = heroes_vivos[self.heroe_seleccionado_idx]
                    
                    if self.accion_magia_pendiente:
                        self.ejecutar_magia_heroe(self.actor_actual, heroe_objetivo, self.accion_magia_pendiente, tiempo_actual)
                        self.accion_magia_pendiente = None 
                        self.estado_batalla = "RESOLVIENDO_ACCION"
                        
                    elif self.accion_item_pendiente:
                        self.ejecutar_item_heroe(self.actor_actual, heroe_objetivo, self.accion_item_pendiente, tiempo_actual)
                        self.estado_batalla = "RESOLVIENDO_ACCION"
                    
                    elif self.accion_habilidad_pendiente:
                        self.ejecutar_habilidad_heroe(self.actor_actual, heroe_objetivo, self.accion_habilidad_pendiente, tiempo_actual)
                        self.accion_habilidad_pendiente = None
                        self.estado_batalla = "RESOLVIENDO_ACCION"
                    
                    else:
                        print("¡Palanqueo (Error)! JUGADOR_ELIGE_ALIADO sin acción pendiente.")
                        self.estado_batalla = "ESPERANDO_INPUT_HEROE"
                    
                else:
                    self.estado_batalla = "ESPERANDO_INPUT_HEROE"

        return None 

    # --- 5. seleccionar_opcion (¡ACTUALIZADO!) ---
    def seleccionar_opcion(self, opcion, heroe_atacante):
        print(f"¡{heroe_atacante.nombre_clase} seleccionó: {opcion}!")
        
        if opcion == "Atacar":
            return "iniciar_targeting_monstruo"
        
        elif opcion == "Habilidades":
            # Verificar si el héroe tiene habilidades equipadas
            if not heroe_atacante.habilidades_activas or not any(hab for hab in heroe_atacante.habilidades_activas if hab):
                print(f"¡{heroe_atacante.nombre_clase} no tiene habilidades equipadas!")
                return None 
            
            print("¡Iniciando selección de Habilidad!")
            return "iniciar_seleccion_habilidad"
        
        elif opcion == "Magia":
            if not heroe_atacante.magias:
                print(f"¡{heroe_atacante.nombre_clase} no 'cacha' (sabe) ninguna magia!")
                return None 
            
            print("¡Iniciando selección de Magia!")
            return "iniciar_seleccion_magia" 
            
        elif opcion == "Objeto":
            if not heroe_atacante.inventario or not any(v > 0 for v in heroe_atacante.inventario.values()):
                print(f"¡{heroe_atacante.nombre_clase} no tiene items!")
                return None 
            
            print("¡Iniciando selección de Item!")
            return "iniciar_seleccion_item"
            
        elif opcion == "Huir":
            print("¡Escapaste!")
            return "mapa"
            
    # --- 6. ejecutar_ataque_heroe (Sin cambios) ---
    def ejecutar_ataque_heroe(self, heroe_atacante, monstruo_objetivo, tiempo_actual):
        print(f"¡{heroe_atacante.nombre_clase} ataca a {monstruo_objetivo.nombre}!")
        
        heroe_atacante.animar_ataque(tiempo_actual)
        
        daño_base_heroe = heroe_atacante.fuerza
        daño = random.randint(daño_base_heroe - 1, daño_base_heroe + 3)
        
        color_daño_monstruo = (255, 255, 255) # Blanco por defecto
        texto_critico = ""

        # --- ¡NUEVA LÓGICA DE CRÍTICO! ---
        # Fórmula: 1 Suerte = 1% de probabilidad
        if random.randint(1, 100) <= heroe_atacante.suerte:
            print("¡GOLPE CRÍTICO DEL HÉROE!")
            daño = int(daño * 2) # Doble de daño
            color_daño_monstruo = (255, 255, 0) # Amarillo
            texto_critico = "¡CRÍTICO! "
        # --- Fin Lógica de Crítico ---
        
        monstruo_objetivo.recibir_daño(daño)
        
        pos_x = monstruo_objetivo.rect.centerx
        pos_y = monstruo_objetivo.rect.top - 30 
        
        texto_daño = TextoFlotante(f"{texto_critico}{daño}", pos_x, pos_y, color_daño_monstruo)
        self.textos_flotantes.append(texto_daño)
    # --- 7. ejecutar_ataque_monstruo (Sin cambios) ---
    def ejecutar_ataque_monstruo(self, monstruo_atacante, tiempo_actual):
        monstruo_atacante.animar_ataque(tiempo_actual)
        
        heroe_objetivo = random.choice([h for h in self.grupo_heroes if not h.esta_muerto()])
        print(f"¡{monstruo_atacante.nombre} ataca a {heroe_objetivo.nombre_clase}!")
        
        daño_base = monstruo_atacante.fuerza
        daño_monstruo = random.randint(daño_base - 2, daño_base + 2)
        
        color_daño_heroe = (255, 0, 0) # Rojo por defecto
        texto_critico = ""
        
        # --- ¡NUEVA LÓGICA DE CRÍTICO! ---
        # (Aquí es donde usamos la suerte del monstruo que acabamos de añadir)
        suerte_monstruo = getattr(monstruo_atacante, "suerte", 5)
        if random.randint(1, 100) <= suerte_monstruo:
            print("¡GOLPE CRÍTICO DEL MONSTRUO!")
            daño_monstruo = int(daño_monstruo * 2)
            color_daño_heroe = (255, 100, 0) # Naranja
            texto_critico = "¡CRÍTICO! "
        # --- Fin Lógica de Crítico ---

        heroe_objetivo.recibir_daño(daño_monstruo)
        
        pos_x = heroe_objetivo.pos_actual_x
        pos_y = heroe_objetivo.pos_actual_y - 50 
        
        texto_daño = TextoFlotante(f"{texto_critico}{daño_monstruo}", pos_x, pos_y, color_daño_heroe)
        self.textos_flotantes.append(texto_daño)
    # --- 8. ejecutar_magia_heroe (Sin cambios) ---
    def ejecutar_magia_heroe(self, heroe_actor, objetivo, magia_data, tiempo_actual):
        
        nombre_objetivo = getattr(objetivo, 'nombre_clase', getattr(objetivo, 'nombre', '???'))
        print(f"¡{heroe_actor.nombre_clase} usa {magia_data['nombre']} en {nombre_objetivo}!")
        
        heroe_actor.animar_ataque(tiempo_actual) 
        
        costo_mp = magia_data['costo_mp']
        heroe_actor.gastar_mp(costo_mp)
        
        poder_base = magia_data['poder']
        tipo_magia = magia_data['tipo']
        
        texto_flotante_valor = 0
        texto_flotante_color = (255, 255, 255)
        texto_flotante_pos = (0, 0)

        if tipo_magia == "Curacion":
            cantidad_curacion = poder_base + heroe_actor.inteligencia
            
            objetivo.recibir_curacion(cantidad_curacion)
            
            texto_flotante_valor = cantidad_curacion
            texto_flotante_color = (0, 255, 0) 
            texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)

        elif tipo_magia == "Ataque":
            daño_magico_base = poder_base + heroe_actor.inteligencia
            
            daño_final = random.randint(daño_magico_base - 2, daño_magico_base + 2)
            
            objetivo.recibir_daño(daño_final)
            
            texto_flotante_valor = daño_final
            texto_flotante_color = (255, 255, 255) 
            texto_flotante_pos = (objetivo.rect.centerx, objetivo.rect.top - 30)
            
        texto_flotante_obj = TextoFlotante(
            texto_flotante_valor, 
            texto_flotante_pos[0], 
            texto_flotante_pos[1], 
            texto_flotante_color
        )
        self.textos_flotantes.append(texto_flotante_obj)

    # --- 9. ejecutar_item_heroe (Sin cambios) ---
    def ejecutar_item_heroe(self, heroe_actor, objetivo, item_data, tiempo_actual):
        
        nombre_objetivo = getattr(objetivo, 'nombre_clase', getattr(objetivo, 'nombre', '???'))
        print(f"¡{heroe_actor.nombre_clase} usa {item_data['nombre']} en {nombre_objetivo}!")
        
        heroe_actor.usar_item(item_data['id_item'])
        
        poder_base = item_data['poder']
        efecto_item = item_data['efecto']
        
        texto_flotante_valor = 0
        texto_flotante_color = (255, 255, 255)
        texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)

        if efecto_item == "RESTAURA_HP":
            objetivo.recibir_curacion(poder_base)
            texto_flotante_valor = poder_base
            texto_flotante_color = (0, 255, 0) 

        elif efecto_item == "RESTAURA_MP":
            objetivo.recibir_curacion_mp(poder_base)
            texto_flotante_valor = poder_base
            texto_flotante_color = (150, 100, 255) 
            
        texto_flotante_obj = TextoFlotante(
            texto_flotante_valor, 
            texto_flotante_pos[0], 
            texto_flotante_pos[1], 
            texto_flotante_color
        )
        self.textos_flotantes.append(texto_flotante_obj)
    
    # --- 10. ejecutar_habilidad_heroe (¡NUEVO!) ---
    def ejecutar_habilidad_heroe(self, heroe_actor, objetivo, habilidad_data, tiempo_actual):
        """Ejecuta una habilidad de un héroe sobre un objetivo"""
        
        nombre_objetivo = getattr(objetivo, 'nombre_en_juego', getattr(objetivo, 'nombre', '???'))
        print(f"¡{heroe_actor.nombre_en_juego} usa {habilidad_data['nombre']} en {nombre_objetivo}!")
        
        heroe_actor.animar_ataque(tiempo_actual)
        
        # Gastar MP
        costo_mp = habilidad_data['costo_mp']
        heroe_actor.gastar_mp(costo_mp)
        
        poder_base = habilidad_data['poder']
        tipo_habilidad = habilidad_data['tipo']
        efecto = habilidad_data.get('efecto')
        
        texto_flotante_valor = 0
        texto_flotante_color = (255, 255, 255)
        texto_flotante_pos = (0, 0)
        
        # Determinar si es daño o curación
        if "Negra" in tipo_habilidad or "Fisica" in tipo_habilidad:
            # Es daño
            stat_multiplicador = heroe_actor.inteligencia if "Negra" in tipo_habilidad else heroe_actor.fuerza
            daño_base = poder_base + stat_multiplicador
            daño_final = random.randint(daño_base - 2, daño_base + 2)
            
            objetivo.recibir_daño(daño_final)
            
            texto_flotante_valor = daño_final
            texto_flotante_color = (255, 100, 100) if "Negra" in tipo_habilidad else (255, 255, 255)
            
            # Posición según si es héroe o monstruo
            if hasattr(objetivo, 'rect'):  # Es monstruo
                texto_flotante_pos = (objetivo.rect.centerx, objetivo.rect.top - 30)
            else:  # Es héroe
                texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)
            
            # Aplicar efectos DOT si corresponde
            if efecto:
                if "DOT" in efecto:
                    duracion = habilidad_data.get('dot_duracion', 3)
                    dano_dot = habilidad_data.get('dot_dano', 10)
                    objetivo.agregar_efecto(efecto, duracion, dano_dot)
                elif "APLICA_SANGRADO" in efecto:
                    # Sangrado: 8 de daño por 3 turnos
                    objetivo.agregar_efecto("DOT_SANGRADO", 3, 8)
                elif "APLICA_VENENO" in efecto:
                    # Veneno: 12 de daño por 4 turnos
                    objetivo.agregar_efecto("DOT_VENENO", 4, 12)
        
        elif "Blanca" in tipo_habilidad or "Defensa" in tipo_habilidad:
            # Es curación o buff
            if poder_base > 0:
                cantidad_curacion = poder_base + heroe_actor.inteligencia
                objetivo.recibir_curacion(cantidad_curacion)
                
                texto_flotante_valor = cantidad_curacion
                texto_flotante_color = (0, 255, 0)
            
            # Posición (siempre es héroe)
            texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)
            
            # Aplicar efectos HOT si corresponde
            if efecto:
                if "HOT" in efecto:
                    duracion = habilidad_data.get('hot_duracion', 3)
                    if "ETER" in efecto:
                        # Regeneración de MP
                        mp_hot = habilidad_data.get('hot_mp', 10)
                        objetivo.agregar_efecto(efecto, duracion, mp_hot, es_mp=True)
                    else:
                        # Regeneración de HP
                        curacion_hot = habilidad_data.get('hot_curacion', 20)
                        objetivo.agregar_efecto(efecto, duracion, curacion_hot, es_mp=False)
                elif "APLICA_RECUPERACION" in efecto:
                    # Recuperación: 15 HP por 3 turnos
                    objetivo.agregar_efecto("HOT_RECUPERACION", 3, 15)
        
        # Crear texto flotante si hay valor
        if texto_flotante_valor > 0:
            texto_flotante_obj = TextoFlotante(
                texto_flotante_valor, 
                texto_flotante_pos[0], 
                texto_flotante_pos[1], 
                texto_flotante_color
            )
            self.textos_flotantes.append(texto_flotante_obj)
    
    # --- 11. ejecutar_habilidad_aoe (¡NUEVO!) ---
    def ejecutar_habilidad_aoe(self, heroe_actor, lista_objetivos, habilidad_data, tiempo_actual):
        """Ejecuta una habilidad AoE sobre múltiples objetivos"""
        
        print(f"¡{heroe_actor.nombre_en_juego} usa {habilidad_data['nombre']} (AoE)!")
        
        heroe_actor.animar_ataque(tiempo_actual)
        
        # Gastar MP
        costo_mp = habilidad_data['costo_mp']
        heroe_actor.gastar_mp(costo_mp)
        
        poder_base = habilidad_data['poder']
        tipo_habilidad = habilidad_data['tipo']
        efecto = habilidad_data.get('efecto')
        
        # Aplicar la habilidad a cada objetivo
        for objetivo in lista_objetivos:
            texto_flotante_valor = 0
            texto_flotante_color = (255, 255, 255)
            texto_flotante_pos = (0, 0)
            
            if "Negra" in tipo_habilidad or "Fisica" in tipo_habilidad:
                # Es daño
                stat_multiplicador = heroe_actor.inteligencia if "Negra" in tipo_habilidad else heroe_actor.fuerza
                daño_base = poder_base + stat_multiplicador
                daño_final = random.randint(daño_base - 2, daño_base + 2)
                
                objetivo.recibir_daño(daño_final)
                
                texto_flotante_valor = daño_final
                texto_flotante_color = (255, 150, 0)  # Naranja para AoE
                
                # Posición según si es héroe o monstruo
                if hasattr(objetivo, 'rect'):  # Es monstruo
                    texto_flotante_pos = (objetivo.rect.centerx, objetivo.rect.top - 30)
                else:  # Es héroe
                    texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)
                
                # Aplicar efectos DOT si corresponde
                if efecto:
                    if "DOT" in efecto:
                        duracion = habilidad_data.get('dot_duracion', 3)
                        dano_dot = habilidad_data.get('dot_dano', 10)
                        objetivo.agregar_efecto(efecto, duracion, dano_dot)
                    elif "APLICA_SANGRADO" in efecto:
                        objetivo.agregar_efecto("DOT_SANGRADO", 3, 8)
            
            elif "Blanca" in tipo_habilidad:
                # Es curación
                cantidad_curacion = poder_base + heroe_actor.inteligencia
                objetivo.recibir_curacion(cantidad_curacion)
                
                texto_flotante_valor = cantidad_curacion
                texto_flotante_color = (100, 255, 100)  # Verde claro para AoE curación
                texto_flotante_pos = (objetivo.pos_actual_x, objetivo.pos_actual_y - 50)
                
                # Aplicar efectos HOT si corresponde
                if efecto:
                    if "HOT" in efecto:
                        duracion = habilidad_data.get('hot_duracion', 3)
                        curacion_hot = habilidad_data.get('hot_curacion', 20)
                        objetivo.agregar_efecto(efecto, duracion, curacion_hot, es_mp=False)
                    elif "APLICA_RECUPERACION" in efecto:
                        objetivo.agregar_efecto("HOT_RECUPERACION", 3, 15)
            
            # Crear texto flotante
            if texto_flotante_valor > 0:
                texto_flotante_obj = TextoFlotante(
                    texto_flotante_valor, 
                    texto_flotante_pos[0], 
                    texto_flotante_pos[1], 
                    texto_flotante_color
                )
                self.textos_flotantes.append(texto_flotante_obj)

    # --- 12. actualizar_lista_ui_monstruos (Sin cambios) ---
    def actualizar_lista_ui_monstruos(self):
        self.monstruos_ui_lista.clear()
        for monstruo in [m for m in self.monstruos_en_batalla if not m.esta_muerto()]:
            if monstruo.nombre in self.monstruos_ui_lista:
                self.monstruos_ui_lista[monstruo.nombre] += 1
            else:
                self.monstruos_ui_lista[monstruo.nombre] = 1 
            
    # --- 11. DRAW (¡"RECABLEADO" (MODIFICADO)!) ---
    def draw(self, pantalla):
        # 1. Dibujar el FONDO y los SPRITES
        pantalla.blit(self.fondo_img, (0, 0))
        
        monstruos_vivos = [m for m in self.monstruos_en_batalla if not m.esta_muerto()]
        heroes_vivos = [h for h in self.grupo_heroes if not h.esta_muerto()]
        
        for monstruo in monstruos_vivos:
            monstruo.draw(pantalla)
        
        for heroe in self.grupo_heroes:
            if not heroe.esta_muerto():
                heroe.draw_batalla(pantalla)

        # 2. Dibujar el Panel Principal Unificado
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.panel_principal_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_principal_rect, 4, border_radius=self.UI_BORDER_RADIUS)

        # 3. Dibujar Contenido de los 3 Paneles

        # --- Pane 1: Comandos (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
        if self.estado_batalla == "ESPERANDO_INPUT_HEROE":
            for i, opcion_texto in enumerate(self.opciones_menu):
                color = self.COLOR_TEXTO if i != self.opcion_seleccionada else self.COLOR_TEXTO_SEL
                texto_surf = self.fuente.render(opcion_texto, True, color)
                pos_x = self.pane_comandos_x
                pos_y = self.pane_comandos_y_base + (i * self.pane_comandos_y_salto)
                
                if i == self.opcion_seleccionada:
                    # ¡"Pega de Cirujano" (Precisión) BKN!
                    if self.cursor_img:
                        cursor_rect = self.cursor_img.get_rect(midright=(pos_x - 5, pos_y + 8))
                        pantalla.blit(self.cursor_img, cursor_rect)
                    else:
                        cursor_surf = self.fuente.render(">", True, self.COLOR_TEXTO_SEL) 
                        pantalla.blit(cursor_surf, (pos_x - 20, pos_y))
                
                pantalla.blit(texto_surf, (pos_x, pos_y))
        
        # Pane 2: Info Monstruo (Sin cambios)
        if self.mensaje_batalla:
            texto_surf = self.fuente.render(self.mensaje_batalla, True, self.COLOR_TEXTO_SEL)
            pantalla.blit(texto_surf, (self.pane_monstruo_x, self.pane_monstruo_y_base))
        
        elif self.estado_batalla == "HEROE_ELIGE_MONSTRUO":
            if monstruos_vivos and self.monstruo_seleccionado_idx < len(monstruos_vivos):
                monstruo_target = monstruos_vivos[self.monstruo_seleccionado_idx]
                nombre_surf = self.fuente_stats.render(monstruo_target.nombre, True, self.COLOR_TEXTO_SEL)
                pantalla.blit(nombre_surf, (self.pane_monstruo_x, self.pane_monstruo_y_base))
                hp_texto = f"HP: {monstruo_target.HP_actual} / {monstruo_target.HP_max}"
                hp_surf = self.fuente_stats.render(hp_texto, True, self.COLOR_TEXTO_SEL)
                pantalla.blit(hp_surf, (self.pane_monstruo_x, self.pane_monstruo_y_base + self.pane_monstruo_y_salto))

        elif self.estado_batalla != "FIN_BATALLA":
            y_offset = 0
            for nombre, cantidad in self.monstruos_ui_lista.items():
                texto_lista = f"{nombre} x{cantidad}"
                texto_surf = self.fuente_stats.render(texto_lista, True, self.COLOR_TEXTO)
                pantalla.blit(texto_surf, (self.pane_monstruo_x, self.pane_monstruo_y_base + y_offset))
                y_offset += self.pane_monstruo_y_salto

        # --- Pane 3: Stats Héroe (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
        y_pos_heroe = self.pane_heroe_y_base
        for i, heroe in enumerate(heroes_vivos): 
            
            color_texto_heroe = self.COLOR_TEXTO
            
            if self.actor_actual == heroe and self.estado_batalla != "RESOLVIENDO_ACCION":
                color_texto_heroe = self.COLOR_TEXTO_SEL 
            
            texto_stats_heroe = f"{heroe.nombre_clase}   HP: {heroe.HP_actual}/{heroe.HP_max}   MP: {heroe.MP_actual}/{heroe.MP_max}"
            stats_surf = self.fuente_stats.render(texto_stats_heroe, True, color_texto_heroe)
            pantalla.blit(stats_surf, (self.pane_heroe_x, y_pos_heroe))
            
            if self.estado_batalla == "JUGADOR_ELIGE_ALIADO" and i == self.heroe_seleccionado_idx:
                # ¡"Pega de Cirujano" (Precisión) BKN!
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(self.pane_heroe_x - 5, y_pos_heroe + 8))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    cursor_surf = self.fuente.render(">", True, self.COLOR_TEXTO_SEL)
                    pantalla.blit(cursor_surf, (self.pane_heroe_x - 20, y_pos_heroe))

            y_pos_heroe += self.pane_heroe_y_salto 
        
        # 4. Dibujar Textos Flotantes (Daño)
        for texto in self.textos_flotantes:
            texto.draw(pantalla)
            
        # --- 5. Dibujar Cursor de Targeting (¡"RECABLEADO" (MODIFICADO)!) (Paso 56.6) ---
        if self.estado_batalla == "HEROE_ELIGE_MONSTRUO":
            if monstruos_vivos and self.monstruo_seleccionado_idx < len(monstruos_vivos):
                monstruo_target = monstruos_vivos[self.monstruo_seleccionado_idx]
                
                # ¡"Pega de Cirujano" (Precisión) BKN!
                if self.cursor_img:
                    cursor_rect = self.cursor_img.get_rect(midright=(monstruo_target.rect.left - 5, monstruo_target.rect.centery))
                    pantalla.blit(self.cursor_img, cursor_rect)
                else:
                    # ¡"Fallback" (Alternativa) BKN!
                    cursor_rect = self.cursor_targeting_surf.get_rect()
                    cursor_rect.midright = (monstruo_target.rect.left - 5, monstruo_target.rect.centery)
                    pantalla.blit(self.cursor_targeting_surf, cursor_rect)
        
        # 6. Dibujar Sub-Menús (¡ACTUALIZADO!)
        if self.estado_batalla == "JUGADOR_ELIGE_MAGIA" and self.pantalla_magia_activa:
            self.pantalla_magia_activa.draw(pantalla)
        
        elif self.estado_batalla == "JUGADOR_ELIGE_ITEM" and self.pantalla_items_activa:
            self.pantalla_items_activa.draw(pantalla)
        
        elif self.estado_batalla == "JUGADOR_ELIGE_HABILIDAD" and self.pantalla_habilidades_activa:
            self.pantalla_habilidades_activa.draw(pantalla)
        
        # 7. Dibujar Pantalla de Victoria (ENCIMA de todo)
        if self.estado_batalla == "VICTORIA" and self.pantalla_victoria_activa:
            self.pantalla_victoria_activa.draw(pantalla)    