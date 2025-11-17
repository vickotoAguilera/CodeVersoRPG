import pygame
import os
import sys 
from src.config import HEROES_SPRITES_PATH

class Heroe:
    
    # --- 1. EL CONSTRUCTOR (¡"PARCHADO" (FIXED) EL CENTRADO!) ---
    def __init__(self, nombre_en_juego, clase_data, coords_data, equipo_db, habilidades_db):
        
        # Asignación de Nombres
        self.nombre_clase = clase_data['nombre_clase'] 
        self.nombre_en_juego = nombre_en_juego  
        self.equipo_db = equipo_db
        self.habilidades_db = habilidades_db     
        
        # Asignación de Stats (ahora son "base")
        self.HP_max_base = clase_data['hp_max']
        self.HP_actual = self.HP_max_base # (HP_actual se basa en el max inicial)
        self.MP_max_base = clase_data['mp_max']
        self.MP_actual = self.MP_max_base # (MP_actual se basa en el max inicial)
        self.fuerza_base = clase_data['fuerza']
        self.defensa_base = clase_data['defensa']
        self.inteligencia_base = clase_data['inteligencia']
        self.espiritu_base = clase_data['espiritu']
        self.velocidad_base = clase_data['velocidad_base']
        self.suerte_base = clase_data['suerte_base']
        # Stats de progresión
        self.oro = clase_data['oro_inicial']
        self.nivel = clase_data['nivel']
        self.experiencia_actual = clase_data['experiencia_actual']
        self.experiencia_siguiente_nivel = clase_data['experiencia_siguiente_nivel']
        # Asignación de Inventarios
        self.inventario = clase_data['items_iniciales'].copy()
        self.inventario_especiales = clase_data.get('items_especiales', {}).copy()  # Items que no se consumen (llaves, amuletos, etc.)
        self.magias = clase_data['magias_iniciales'].copy()
        
        # --- ¡NUEVO! Sistema de Habilidades (Paso 7.14) ---
        self.clase = clase_data['clase']
        self.ranuras_habilidad_max = clase_data['ranuras_habilidad_max']
        self.habilidades_activas = clase_data['habilidades_activas'].copy()
        self.inventario_habilidades = clase_data['inventario_habilidades'].copy()

        # --- ¡NUEVO! Ranuras de Equipo (11 Slots) ---
        self.equipo = {
            "cabeza": None,       # Gorro
            "pecho": None,        # Armadura de Pecho
            "piernas": None,      # Pantalon
            "pies": None,         # Botas
            "manos": None,        # Guantes
            "espalda": None,      # Capa
            "mano_principal": None, # Arma
            "mano_secundaria": None, # Escudo
            "accesorio1": None,   # Aro 1
            "accesorio2": None,   # Aro 2
            "accesorio3": None    # Collar
        }

        # Velocidad y Carga de Sprites
        self.velocidad_movimiento = coords_data['VELOCIDAD']
        self._cargar_sprites(coords_data) # ¡"Tira" (Llama) al "motor" (engine) BKN!
        
        # --- "PEGA DE CIRUJANO" (FIX) BKN: LÓGICA DE CENTRADO ---
        # (¡"Pilla" (Define) la pos BKN *después* de "cargar" (leer) los sprites!)
        pos_centro_anterior = (677, 540) 
        self.heroe_rect = self.img_parado_abajo.get_rect() 
        self.heroe_rect.center = pos_centro_anterior
        # --- FIN "PEGA DE CIRUJANO" (FIX) ---
        
        self.heroe_x_float = float(self.heroe_rect.x)
        self.heroe_y_float = float(self.heroe_rect.y)
        
        # Animación del MAPA
        self.ultimo_update_anim = pygame.time.get_ticks()
        self.velocidad_anim = 200 
        self.frame_actual = 0
        self.heroe_esta_caminando = False
        self.direccion = "abajo"
        
        # Variables de Posición y Animación de BATALLA
        self.pos_batalla_x = 0     
        self.pos_batalla_y = 0     
        self.pos_actual_x = 0      
        self.pos_actual_y = 0      
        self.anim_atacando = False 
        self.anim_fase = 0         
        self.anim_timer = 0        
        self.DISTANCIA_EMBESTIDA = 30
        
        # Sistema de Efectos de Estado (DOT/HOT)
        self.efectos_activos = []  # Lista de efectos: [{"tipo": "DOT_QUEMADURA", "duracion": 3, "valor": 15}, ...]
        
    # --- 2. CARGAR SPRITES (¡"RECABLEADO" (REFACTOR) MAESTRO BKN!) ---
    # (¡"Parcha" (Arregla) el KeyError BKN!)
    def _cargar_sprites(self, coords_data):
        
        hoja_sprites_archivo = coords_data['HOJA_SPRITES']
        escala = coords_data['ESCALA']
        
        try:
            ruta_heroe = os.path.join(HEROES_SPRITES_PATH, hoja_sprites_archivo)
            # ¡"Pega Pro" (Profesional) BKN! "Usamos" (Llamamos) convert_alpha() "al tiro" (inmediatamente)
            hoja_img_orig = pygame.image.load(ruta_heroe).convert_alpha() 
            
        except FileNotFoundError:
            print(f"¡ERROR CRÍTICO! No se (encontró) la hoja de sprites: {ruta_heroe}")
            pygame.quit(); sys.exit()
            
        self.ESCALA_HEROE = escala

        self.animaciones = {
            "caminar_abajo": [],
            "caminar_arriba": [],
            "caminar_izquierda": [],
            "caminar_derecha": [],
        }
        
        # --- ¡LÓGICA "INTELIGENTE" (ADAPTATIVA) BKN! ---
        # "Pilla" (Define) las direcciones BKN
        direcciones_base = ["ABAJO", "ARRIBA", "IZQUIERDA"]
        # "Chequea" (Verifica) si el "molde" (coords) "cacha" (tiene) "DERECHA"
        if "PARADO_DERECHA" in coords_data:
            print(f"¡'Pillado' (Detectado) Sprite Sheet de 12 frames (Cloud) BKN!")
            direcciones_base.append("DERECHA")
        else:
            print(f"¡'Pillado' (Detectado) Sprite Sheet de 8 frames (Terra) BKN! 'Usando' (Aplicando) Flip...")

        for dir_base in direcciones_base:
            dir_min = dir_base.lower() 
            
            # --- 1. "Pillar" (Cargar) Sprite Parado BKN ---
            recorte_parado_key = f"PARADO_{dir_base}"
            recorte_parado = coords_data[recorte_parado_key] 
            img_recortada_orig = hoja_img_orig.subsurface(recorte_parado)
            
            # "Pillamos" (Calculamos) el tamaño "nuevo" (escalado) BKN
            nuevo_ancho = int(img_recortada_orig.get_width() * escala)
            nuevo_alto = int(img_recortada_orig.get_height() * escala)
            img_escalada = pygame.transform.scale(img_recortada_orig, (nuevo_ancho, nuevo_alto))

            # "Seteamos" (Guardamos) la variable BKN (ej: self.img_parado_abajo)
            setattr(self, f"img_parado_{dir_min}", img_escalada)

            # --- 2. "Pillar" (Cargar) Frames de Caminata BKN ---
            # ("Pillamos" (Buscamos) los frames 1 y 2. ¡El 3 "palanqueaba" (fallaba)!)
            for i in range(1, 3): 
                recorte_caminar_key = f"CAMINAR_{dir_base}_{i}"
                
                # "Chequeamos" (Verificamos) si "existe" (está) el "filete" (frame) BKN
                if recorte_caminar_key in coords_data:
                    recorte = coords_data[recorte_caminar_key]
                    img_recortada_orig = hoja_img_orig.subsurface(recorte)
                    img_escalada = pygame.transform.scale(img_recortada_orig, (nuevo_ancho, nuevo_alto))
                    self.animaciones[f"caminar_{dir_min}"].append(img_escalada)
                else:
                    # ¡"Palanqueo" (Error) BKN! "Falta" (No está) el frame 1 o 2
                    print(f"¡ADVERTENCIA! 'Falta' (No está) el frame {recorte_caminar_key} en la DB BKN.")
                    break 

        # --- 3. "Pillar" (Crear) Sprites "Flipeados" (Invertidos) BKN (¡Solo si "falta" (no está) DERECHA!) ---
        if "PARADO_DERECHA" not in coords_data:
            self.img_parado_derecha = pygame.transform.flip(self.img_parado_izquierda, True, False)
            for frame_izq in self.animaciones["caminar_izquierda"]:
                self.animaciones["caminar_derecha"].append(pygame.transform.flip(frame_izq, True, False))

        # --- 4. "Setear" (Definir) Sprites de Batalla y Desmayo BKN ---
        # (¡"Parchado" (Arreglado) BKN! "Usa" (Asigna) el "parado" (idle) BKN)
        self.img_batalla_izquierda = self.img_parado_izquierda
        self.img_batalla_derecha = self.img_parado_derecha
        # (¡"Fileteado" (Eliminado) el Desmayo BKN, "tal como" (según) "pediste" (solicitaste)!)
        self.img_desmayo = self.img_parado_abajo # "Fallback" (Alternativa) BKN


    # --- 3. DIBUJAR (MAPA) ---
    def draw(self, pantalla, camara_rect):
        
        # Seleccionar el sprite actual
        if self.heroe_esta_caminando:
            lista_frames = self.animaciones[f"caminar_{self.direccion}"]
            # "Parchamos" (Arreglamos) un "palanqueo" (error) BKN si el frame "pasa" (supera) el límite
            if self.frame_actual >= len(lista_frames):
                self.frame_actual = 0 
            sprite_actual = lista_frames[self.frame_actual]
        else:
            # "Seteamos" (Definimos) el "parado" (idle) BKN
            sprite_actual = getattr(self, f"img_parado_{self.direccion}", self.img_parado_abajo)

        pos_en_pantalla_x = self.heroe_rect.x - camara_rect.x
        pos_en_pantalla_y = self.heroe_rect.y - camara_rect.y
        
        # "Usamos" (Obtenemos) el rect "real" (actual) del sprite BKN
        sprite_rect_temp = sprite_actual.get_rect(x=pos_en_pantalla_x, y=pos_en_pantalla_y)
        pantalla.blit(sprite_actual, sprite_rect_temp)


    # --- 4. UPDATE DEL MAPA (¡"PARCHADO" (FIXED) EL ATTRIBUTEERROR BKN!) ---
    # (¡"Recableado" (Renombrado) a "update" BKN!)
    def update(self, teclas, mapa_img, muros): # ¡"Parámetros" (Argumentos) "parchados" (corregidos) BKN!
        # 1. Variables de movimiento
        delta_x = 0.0
        delta_y = 0.0
        self.heroe_esta_caminando = False
        
        # 2. Manejo de Input (Dirección)
        if teclas[pygame.K_UP]:
            delta_y = -self.velocidad_movimiento
            self.direccion = "arriba"
            self.heroe_esta_caminando = True
        elif teclas[pygame.K_DOWN]:
            delta_y = self.velocidad_movimiento
            self.direccion = "abajo"
            self.heroe_esta_caminando = True
        elif teclas[pygame.K_LEFT]:
            delta_x = -self.velocidad_movimiento
            self.direccion = "izquierda"
            self.heroe_esta_caminando = True
        elif teclas[pygame.K_RIGHT]:
            delta_x = self.velocidad_movimiento
            self.direccion = "derecha"
            self.heroe_esta_caminando = True

        # 3. Aplicar movimiento con colisiones
        if self.heroe_esta_caminando:
            self._mover_con_colisiones(delta_x, delta_y, muros) # ¡"Usa" (Pasa) "muros" BKN!
            self._update_animacion()

    # --- 5. LÓGICA DE COLISIONES ---
    def _mover_con_colisiones(self, delta_x, delta_y, paredes_mapa):
        
        # --- MOVIMIENTO EN X ---
        self.heroe_x_float += delta_x
        self.heroe_rect.x = int(self.heroe_x_float)
        
        for muro in paredes_mapa:
            if self.heroe_rect.colliderect(muro):
                if delta_x > 0:
                    self.heroe_rect.right = muro.left
                elif delta_x < 0:
                    self.heroe_rect.left = muro.right
                self.heroe_x_float = float(self.heroe_rect.x)

        # --- MOVIMIENTO EN Y ---
        self.heroe_y_float += delta_y
        self.heroe_rect.y = int(self.heroe_y_float)
        
        for muro in paredes_mapa:
            if self.heroe_rect.colliderect(muro):
                if delta_y > 0:
                    self.heroe_rect.bottom = muro.top
                elif delta_y < 0:
                    self.heroe_rect.top = muro.bottom
                self.heroe_y_float = float(self.heroe_rect.y)


    # --- 6. UPDATE DE ANIMACIÓN ---
    def _update_animacion(self):
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - self.ultimo_update_anim > self.velocidad_anim:
            self.ultimo_update_anim = tiempo_actual
            
            lista_frames = self.animaciones[f"caminar_{self.direccion}"]
            self.frame_actual = (self.frame_actual + 1) % len(lista_frames)

    #7 logica de experiencia y nivel
    def ganar_experiencia(self, cantidad):
        """
        Añade experiencia al héroe y chequea si sube de nivel.
        Utiliza un 'while' por si el héroe gana suficiente XP
        para subir varios niveles a la vez.
        
        Devuelve:
            True: si el héroe subió de nivel.
            False: si no subió de nivel.
        """
        
        if self.esta_muerto():
            print(f"{self.nombre_en_juego} esta muerto y no puede ganar exp!")
            return False # No ganó XP, no subió de nivel
            
        # --- ¡LÍNEA CRÍTICA FALTANTE (AÑADIDA)! ---
        self.experiencia_actual += cantidad
        print(f"¡{self.nombre_en_juego} gana {cantidad} XP! (Total: {self.experiencia_actual})")
        # ----------------------------------------------

        # --- ¡NUEVO! Variable de retorno ---
        subio_de_nivel = False
        
        # Bucle si sube multiples niveles
        while self.experiencia_actual >= self.experiencia_siguiente_nivel:
            self._subir_nivel()
            subio_de_nivel = True # Marcamos que sí subió

        return subio_de_nivel
    def _subir_nivel(self):
        """
        Función interna para manejar la subida de nivel.
        (Esta es una versión simple, la podemos hacer más compleja después)
        """
        
        self.nivel +=1
        print(f"{self.nombre_en_juego} ha subido al nivel {self.nivel}!")
        
        #1. aca se calcula la exp restante y nueva meta 
        xp_restante = self.experiencia_actual - self.experiencia_siguiente_nivel
        self.experiencia_actual = xp_restante
        
        #Formula simple de incremento de xp ej: 100,150...
        self.experiencia_siguiente_nivel = int(self.experiencia_siguiente_nivel * 1.5)
        
        #2.- aumentar estadisticas (valores de ejemplo)
        aumento_hp = 10
        aumento_mp = 2
        
        self.HP_max_base += aumento_hp
        self.MP_max_base += aumento_mp
        self.fuerza_base += 1
        self.defensa_base += 1
        self.inteligencia_base += 1
        self.espiritu_base += 1
        self.velocidad_base += 1
        self.suerte_base += 1
        
        #curar al heroe cuando sube de nivel
        self.HP_actual = self.HP_max
        self.MP_actual = self.MP_max
        
        print(f"¡HP Máx: {self.HP_max} (+{aumento_hp}), MP Máx: {self.MP_max} (+{aumento_mp})!")
        print(f"XP para Nivel {self.nivel + 1}: {self.experiencia_siguiente_nivel}")
        # --- 7.5 CÁLCULO DE STATS CON EQUIPO (¡NUEVO!) ---
    # Usamos @property para que parezca una variable normal,
    # pero en realidad es una función que calcula el total.

    def _get_stat_equipo(self, stat_nombre):
        """Función interna para sumar la stat de todo el equipo equipado."""
        total_bonus = 0
        ids_ya_sumados = [] # ¡NUEVO! Lista para evitar sumar 2H dos veces
        
        for slot, id_equipo in self.equipo.items():
            
            # ¡NUEVO! Si hay un ítem Y no lo hemos sumado ya
            if id_equipo and id_equipo not in ids_ya_sumados:
                
                # Buscamos el item en la DB que guardamos
                item_data = self.equipo_db.get(id_equipo)
                if item_data:
                    # Sumamos el bonus de esa stat
                    total_bonus += item_data["stats"].get(stat_nombre, 0)
                    # Añadimos el ID a la lista para no volver a sumarlo
                    ids_ya_sumados.append(id_equipo)
                    
        return total_bonus

    @property
    def HP_max(self):
        # (Por ahora el equipo no da HP, pero está listo para el futuro)
        bonus_equipo = 0 
        return self.HP_max_base + bonus_equipo

    @property
    def MP_max(self):
        # (Por ahora el equipo no da MP, pero está listo para el futuro)
        bonus_equipo = 0 
        return self.MP_max_base + bonus_equipo

    @property
    def fuerza(self):
        bonus_equipo = self._get_stat_equipo("fuerza")
        return self.fuerza_base + bonus_equipo

    @property
    def defensa(self):
        bonus_equipo = self._get_stat_equipo("defensa")
        return self.defensa_base + bonus_equipo

    @property
    def inteligencia(self):
        bonus_equipo = self._get_stat_equipo("inteligencia")
        return self.inteligencia_base + bonus_equipo

    @property
    def espiritu(self):
        bonus_equipo = self._get_stat_equipo("espiritu")
        return self.espiritu_base + bonus_equipo
    @property
    def velocidad(self):
        bonus_equipo = self._get_stat_equipo("velocidad")
        return self.velocidad_base + bonus_equipo

    @property
    def suerte(self):
        bonus_equipo = self._get_stat_equipo("suerte")
        return self.suerte_base + bonus_equipo
    
    # --- 8. LÓGICA DE COMBATE (¡"PARCHADA" (RESTAURADA) BKN!) ---
    
    def recibir_daño(self, cantidad):
        self.HP_actual -= cantidad
        if self.HP_actual < 0:
            self.HP_actual = 0
        print(f"¡{self.nombre_clase} recibió {cantidad} de daño! HP: {self.HP_actual}")
        return cantidad
    
    # --- ¡"Enchufada" (Restaurada) la función BKN! ---
    def esta_muerto(self):
        """Retorna True si el héroe está muerto (HP <= 0)"""
        return self.HP_actual <= 0
        
    # --- ¡"Enchufada" (Restaurada) la función BKN! ---
    def recibir_curacion(self, curacion):
        """Cura HP (usado por magias y pociones)"""
        curacion_real = min(curacion, self.HP_max - self.HP_actual)
        self.HP_actual += curacion_real
        print(f"¡{self.nombre_clase} recupera {curacion_real} HP! HP: {self.HP_actual}")
        return curacion_real

    # --- ¡"Enchufada" (Restaurada) la función BKN! ---
    def recibir_curacion_mp(self, curacion):
        """Cura MP (usado por éteres)"""
        curacion_real = min(curacion, self.MP_max - self.MP_actual)
        self.MP_actual += curacion_real
        print(f"¡{self.nombre_clase} recupera {curacion_real} MP! MP: {self.MP_actual}")
        return curacion_real

    def gastar_mp(self, costo):
        if self.MP_actual >= costo:
            self.MP_actual -= costo
            print(f"¡{self.nombre_clase} gasta {costo} MP! (Quedan: {self.MP_actual})")
            return True
        else:
            print(f"¡{self.nombre_clase} no tiene suficiente MP! (Necesita: {costo})")
            return False
    
    def usar_expansor_ranuras(self, cantidad=2):
        """
        Expande las ranuras de habilidades del héroe.
        El expansor es acumulativo: +2, +4, +6...
        Este método se llama cuando se selecciona el item EXPANSOR_RANURAS.
        El expansor NO se consume porque está en items especiales.
        """
        self.ranuras_habilidad_max += cantidad
        print(f"¡{self.nombre_en_juego} ahora tiene {self.ranuras_habilidad_max} ranuras de habilidades!")
        
        # Los items especiales NO se consumen, permanecen en el inventario
        # No se debe agregar ni quitar nada del inventario especial aquí
        
        return True
    
    def agregar_efecto(self, tipo_efecto, duracion, valor, es_mp=False):
        """Agrega un efecto DOT/HOT al héroe"""
        self.efectos_activos.append({
            "tipo": tipo_efecto,
            "duracion": duracion,
            "valor": valor,
            "es_mp": es_mp
        })
        print(f"{self.nombre_en_juego} ahora tiene el efecto: {tipo_efecto} por {duracion} turnos!")
    
    def procesar_efectos_turno(self):
        """Procesa los efectos DOT/HOT al inicio del turno del héroe"""
        efectos_restantes = []
        mensajes = []
        
        for efecto in self.efectos_activos:
            tipo = efecto["tipo"]
            valor = efecto["valor"]
            es_mp = efecto.get("es_mp", False)
            
            # Aplicar el efecto
            if "DOT" in tipo:
                # Daño sobre tiempo
                self.HP_actual -= valor
                if self.HP_actual < 0:
                    self.HP_actual = 0
                mensajes.append(f"{self.nombre_en_juego} recibe {valor} de daño por {tipo}!")
                print(f"{self.nombre_en_juego} recibe {valor} de daño por {tipo}! HP: {self.HP_actual}/{self.HP_max}")
            elif "HOT" in tipo:
                # Curación sobre tiempo
                if es_mp:
                    # Regeneración de MP
                    self.MP_actual += valor
                    if self.MP_actual > self.MP_max:
                        self.MP_actual = self.MP_max
                    mensajes.append(f"{self.nombre_en_juego} recupera {valor} MP por {tipo}!")
                    print(f"{self.nombre_en_juego} recupera {valor} MP por {tipo}! MP: {self.MP_actual}/{self.MP_max}")
                else:
                    # Regeneración de HP
                    self.HP_actual += valor
                    if self.HP_actual > self.HP_max:
                        self.HP_actual = self.HP_max
                    mensajes.append(f"{self.nombre_en_juego} se cura {valor} HP por {tipo}!")
                    print(f"{self.nombre_en_juego} se cura {valor} HP por {tipo}! HP: {self.HP_actual}/{self.HP_max}")
            
            # Reducir duración
            efecto["duracion"] -= 1
            
            # Si aún tiene duración, mantener el efecto
            if efecto["duracion"] > 0:
                efectos_restantes.append(efecto)
            else:
                mensajes.append(f"El efecto {tipo} en {self.nombre_en_juego} ha terminado.")
                print(f"El efecto {tipo} en {self.nombre_en_juego} ha terminado.")
        
        self.efectos_activos = efectos_restantes
        return mensajes

    

    # --- GESTIÓN DE INVENTARIO ---
    def tiene_item(self, id_item, cantidad=1):
        cantidad_actual = self.inventario.get(id_item, 0)
        return cantidad_actual >= cantidad

    def usar_item(self, id_item, cantidad=1):
        if self.tiene_item(id_item, cantidad):
            self.inventario[id_item] -= cantidad
            if self.inventario[id_item] <= 0:
                del self.inventario[id_item]
            print(f"¡{self.nombre_clase} usó {id_item} x{cantidad}!")
            return True
        return False
        
    def agregar_item(self, id_item, cantidad=1):
        self.inventario[id_item] = self.inventario.get(id_item, 0) + cantidad
        print(f"¡{self.nombre_clase} agregó {id_item} x{cantidad}!")
    
    def aplicar_efectos_especiales(self):
        """Aplica efectos pasivos de los items especiales en el inventario."""
        # Los items especiales actúan como pasivos mientras están en el inventario
        # Por ejemplo: llaves, amuletos, expansores, etc.
        # Los expansores ya se aplican automáticamente cuando se usan
        # Las llaves y otros items especiales se verifican cuando se necesitan
        
        if self.inventario_especiales:
            print(f"Items especiales activos de {self.nombre_en_juego}:")
            for id_item, cantidad in self.inventario_especiales.items():
                if cantidad > 0:
                    print(f"  - {id_item} x{cantidad}")
    
    def tiene_item_especial(self, id_item):
        """Verifica si el héroe tiene un item especial (llave, amuleto, etc.)"""
        return id_item in self.inventario_especiales and self.inventario_especiales[id_item] > 0
    
    def agregar_item_especial(self, id_item, cantidad=1, items_db=None, grupo_heroes=None):
        """
        Agrega un item especial (no consumible) al inventario.
        Si el item tiene efecto global (como expansores de ranuras),
        aplica el efecto automáticamente a todos los héroes.
        """
        self.inventario_especiales[id_item] = self.inventario_especiales.get(id_item, 0) + cantidad
        print(f"¡{self.nombre_clase} obtuvo {id_item} (Especial) x{cantidad}!")
        
        # Si tenemos la DB de items y el grupo de héroes, aplicar efectos automáticos
        if items_db and grupo_heroes and id_item in items_db:
            item_data = items_db[id_item]
            self._aplicar_efecto_global_especial(item_data, grupo_heroes)
        
        self.aplicar_efectos_especiales()
    
    def _aplicar_efecto_global_especial(self, item_data, grupo_heroes):
        """Aplica efectos de items especiales a todos los héroes del grupo."""
        efecto = item_data.get("efecto")
        
        if efecto == "AUMENTA_RANURAS_HABILIDAD":
            # Calcular el total de ranuras según la cantidad de items
            cantidad_item = self.inventario_especiales.get(item_data['id_item'], 0)
            ranuras_totales = item_data['poder'] * cantidad_item
            
            print(f"\n=== EFECTO GLOBAL ACTIVADO ===")
            print(f"Item: {item_data['nombre']} x{cantidad_item}")
            print(f"Ranuras otorgadas: {item_data['poder']} x {cantidad_item} = {ranuras_totales}")
            
            # Aplicar a todos los héroes
            for heroe in grupo_heroes:
                ranuras_anteriores = heroe.ranuras_habilidad_max
                heroe.usar_expansor_ranuras(ranuras_totales)
                print(f"  -> {heroe.nombre_en_juego}: {ranuras_anteriores} -> {heroe.ranuras_habilidad_max} ranuras")
            
            print("=== FIN EFECTO GLOBAL ===\n")
    
    def obtener_items_especiales(self):
        """Retorna lista de items especiales activos"""
        items = []
        for id_item, cantidad in self.inventario_especiales.items():
            if cantidad > 0:
                items.append({"id": id_item, "cantidad": cantidad})
        return items
        
    # --- ¡NUEVO! LÓGICA DE EQUIPAMIENTO ---
    
    def equipar_item_en_ranura(self, id_item_nuevo, ranura_seleccionada):
        """
        Gestiona la lógica de equipar un ítem nuevo y 
        desequipar el antiguo.
        'id_item_nuevo' puede ser un ID o "NINGUNO" (para desequipar).
        """
        print(f"Intentando equipar '{id_item_nuevo}' en la ranura '{ranura_seleccionada}'")

        # 1. DESEQUIPAR EL ÍTEM ANTIGUO (si existe)
        id_item_viejo = self.equipo.get(ranura_seleccionada)
        if id_item_viejo:
            item_viejo_data = self.equipo_db.get(id_item_viejo)
            if item_viejo_data:
                # Si era un ítem de 2 manos, limpiamos ambas ranuras
                if "mano_secundaria" in item_viejo_data.get("ranuras_que_ocupa", []):
                    self.equipo["mano_principal"] = None
                    self.equipo["mano_secundaria"] = None
                    print(f"Desequipando (2H): {item_viejo_data['nombre']}")
                else:
                    # Si era normal, solo limpiamos su ranura
                    self.equipo[ranura_seleccionada] = None
                    print(f"Desequipando: {item_viejo_data['nombre']}")
                
                # Devolver el ítem viejo al inventario
                self.agregar_item(id_item_viejo)

        # 2. EQUIPAR EL ÍTEM NUEVO (si no es "NINGUNO")
        if id_item_nuevo != "NINGUNO":
            item_nuevo_data = self.equipo_db.get(id_item_nuevo)
            if not item_nuevo_data:
                print(f"¡ERROR! No se encontró el ítem {id_item_nuevo} en la DB.")
                return

            # Quitar el ítem nuevo del inventario
            if not self.usar_item(id_item_nuevo):
                print(f"¡ERROR! El héroe no tenía el ítem {id_item_nuevo} para equipar.")
                return # Detenemos si el ítem no estaba en el inventario

            # Obtenemos las ranuras que ocupa
            ranuras_a_ocupar = item_nuevo_data.get("ranuras_que_ocupa", [])
            
            # --- Lógica de 2 Manos ---
            # Si el ítem nuevo es de 2 manos...
            if "mano_principal" in ranuras_a_ocupar and "mano_secundaria" in ranuras_a_ocupar:
                print(f"Equipando (2H): {item_nuevo_data['nombre']}")
                
                # ...desequipamos lo que haya en la mano secundaria (un escudo)
                id_item_secundario = self.equipo.get("mano_secundaria")
                if id_item_secundario:
                    self.agregar_item(id_item_secundario)
                    print(f"¡El arma de 2H quitó el {id_item_secundario}!")
                
                # Ocupamos ambas ranuras
                self.equipo["mano_principal"] = id_item_nuevo
                self.equipo["mano_secundaria"] = id_item_nuevo
            
            # --- Lógica de 1 Mano / Escudo / Armadura ---
            else:
                # Si es un escudo y tenemos un arma de 2H, no se puede
                if ranura_seleccionada == "mano_secundaria" and self.equipo.get("mano_principal"):
                    id_arma_ppal = self.equipo.get("mano_principal")
                    arma_ppal_data = self.equipo_db.get(id_arma_ppal)
                    if arma_ppal_data and "mano_secundaria" in arma_ppal_data.get("ranuras_que_ocupa", []):
                        print("¡No se puede equipar un escudo con un arma de 2 manos!")
                        # Devolvemos el ítem al inventario
                        self.agregar_item(id_item_nuevo) 
                        return # Detenemos la acción
                
                # Equipamiento normal
                print(f"Equipando: {item_nuevo_data['nombre']} en {ranura_seleccionada}")
                # --- ¡CORREGIDO! Solo equipamos en la ranura específica ---
                self.equipo[ranura_seleccionada] = id_item_nuevo    

    # --- LÓGICA DE TELETRANSPORTE ---
    def teletransportar(self, x, y):
        """Mueve al héroe a una posición específica del mapa"""
        self.heroe_rect.x = x
        self.heroe_rect.y = y
        self.heroe_x_float = float(x)
        self.heroe_y_float = float(y)

    # --- LÓGICA DE ANIMACIÓN DE BATALLA ---
    def establecer_posicion_batalla(self, x, y):
        self.pos_batalla_x = x
        self.pos_batalla_y = y
        self.pos_actual_x = x
        self.pos_actual_y = y

    def draw_batalla(self, pantalla):
        if self.HP_actual <= 0:
            img_heroe = self.img_desmayo # (Usando el "fallback" (alternativa) BKN)
        else:
            img_heroe = self.img_batalla_izquierda 
            
        heroe_rect = img_heroe.get_rect()
        heroe_rect.center = (int(self.pos_actual_x), int(self.pos_actual_y))
        pantalla.blit(img_heroe, heroe_rect)

    def animar_ataque(self, tiempo_actual):
        if not self.anim_atacando:
            self.anim_atacando = True
            self.anim_fase = 1 
            self.anim_timer = tiempo_actual
            print(f"¡{self.nombre_clase} inicia embestida!")

    def update_animacion_ataque(self, tiempo_actual):
        if not self.anim_atacando:
            return True
        
        tiempo_transcurrido = tiempo_actual - self.anim_timer
        
        if self.anim_fase == 1:
            self.pos_actual_x = self.pos_batalla_x - self.DISTANCIA_EMBESTIDA
            if tiempo_transcurrido > 300:
                self.anim_fase = 2
                self.anim_timer = tiempo_actual
        
        elif self.anim_fase == 2:
            if tiempo_transcurrido > 300:
                self.anim_fase = 3
                self.anim_timer = tiempo_actual
        
        elif self.anim_fase == 3:
            self.pos_actual_x = self.pos_batalla_x 
            if tiempo_transcurrido > 300:
                self.anim_fase = 0
                self.anim_atacando = False
                print(f"¡{self.nombre_clase} termina ataque!")
                return True

        return False
    
    # --- SISTEMA DE EXPANSIÓN DE RANURAS ---
    def usar_expansor_ranuras(self, cantidad_ranuras):
        """
        Aumenta permanentemente las ranuras de habilidad del héroe.
        Esta función NO acumula, sino que ESTABLECE el valor total.
        """
        # Establecer el nuevo máximo de ranuras
        self.ranuras_habilidad_max = cantidad_ranuras
        print(f"{self.nombre_en_juego} ahora tiene {self.ranuras_habilidad_max} ranuras de habilidad.")
    
    # --- SISTEMA CENTRALIZADO DE ITEMS ESPECIALES ---
    def agregar_item_especial(self, item_id, cantidad, items_db, grupo_heroes=None):
        """
        Agrega un item especial al inventario y aplica su efecto automático.
        
        Args:
            item_id: ID del item especial
            cantidad: Cantidad a agregar
            items_db: Base de datos de items
            grupo_heroes: Lista de héroes (para efectos globales como expansor)
        
        Returns:
            bool: True si se aplicó un efecto, False si solo se agregó al inventario
        """
        # Agregar al inventario especial
        if item_id in self.inventario_especiales:
            self.inventario_especiales[item_id] += cantidad
        else:
            self.inventario_especiales[item_id] = cantidad
        
        print(f"  → {item_id} x{cantidad} agregado a items especiales")
        
        # Verificar si tiene efecto automático
        if items_db and item_id in items_db:
            item_data = items_db[item_id]
            efecto = item_data.get("efecto")
            
            # EXPANSOR DE RANURAS - Efecto Global
            if efecto == "AUMENTA_RANURAS_HABILIDAD":
                incremento = item_data.get("poder", 2) * cantidad
                
                # Si hay grupo, aplicar a todos
                if grupo_heroes:
                    for heroe in grupo_heroes:
                        heroe.ranuras_habilidad_max += incremento
                        print(f"  ✨ {heroe.nombre_en_juego}: Ranuras aumentadas a {heroe.ranuras_habilidad_max}")
                else:
                    # Solo a este héroe
                    self.ranuras_habilidad_max += incremento
                    print(f"  ✨ {self.nombre_en_juego}: Ranuras aumentadas a {self.ranuras_habilidad_max}")
                
                return True
            
            # LLAVES - No tienen efecto automático, solo se verifican
            elif efecto == "LLAVE":
                print(f"  🔑 Llave obtenida: {item_data.get('nombre', item_id)}")
                return False
        
        return False
