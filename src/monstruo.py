import pygame
import os
import sys
from src.config import MONSTRUOS_SPRITES_PATH

class Monstruo(pygame.sprite.Sprite):
    # --- __init__ (Sin cambios) ---
    def __init__(self, nombre, hp, fuerza, defensa, sprite_archivo, escala_sprite, xp_otorgada=0, oro_otorgado=0, velocidad=5, suerte=5):
        super().__init__()
        
        print(f"Creando Monstruo!: {nombre}!")
        
        self.nombre = nombre
        self.HP_max = hp
        self.HP_actual = hp
        self.fuerza = fuerza
        self.defensa = defensa
        self.xp_otorgada = xp_otorgada
        self.oro_otorgado = oro_otorgado
        self.velocidad = velocidad
        self.suerte = suerte
        
        try:
            ruta_monstruo = os.path.join (MONSTRUOS_SPRITES_PATH, sprite_archivo)
            img_origin = pygame.image.load(ruta_monstruo).convert_alpha()
            
            ancho_orig = img_origin.get_width()
            alto_orig = img_origin.get_height()
            nuevo_ancho = int(ancho_orig * escala_sprite)
            nuevo_alto = int(alto_orig * escala_sprite)
            
            self.image = pygame.transform.scale(img_origin, (nuevo_ancho, nuevo_alto))
            self.sprite = self.image 
            
            self.rect = self.image.get_rect()
        
        except FileNotFoundError:
            print(f" ERROR! no se encontro el elprite del monstruo: {ruta_monstruo}")
            pygame.quit()
            sys.exit()
            
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
    
    # --- Acciones (Sin cambios) ---
    def recibir_daño(self, cantidad_daño):
        daño_real = max(1, cantidad_daño)
        self.HP_actual -= daño_real
        print(f"{self.nombre} resive {daño_real} puntos de daño! HP restante: {self.HP_actual} ")
        if self.HP_actual < 0:
            self.HP_actual = 0
    
    def esta_muerto(self):
        return self.HP_actual <= 0
    
    def agregar_efecto(self, tipo_efecto, duracion, valor):
        """Agrega un efecto DOT/HOT al monstruo"""
        self.efectos_activos.append({
            "tipo": tipo_efecto,
            "duracion": duracion,
            "valor": valor
        })
        print(f"{self.nombre} ahora tiene el efecto: {tipo_efecto} por {duracion} turnos!")
    
    def procesar_efectos_turno(self):
        """Procesa los efectos DOT/HOT al inicio del turno del monstruo"""
        efectos_restantes = []
        mensajes = []
        
        for efecto in self.efectos_activos:
            tipo = efecto["tipo"]
            valor = efecto["valor"]
            
            # Aplicar el efecto
            if "DOT" in tipo:
                # Daño sobre tiempo
                self.HP_actual -= valor
                if self.HP_actual < 0:
                    self.HP_actual = 0
                mensajes.append(f"{self.nombre} recibe {valor} de daño por {tipo}!")
                print(f"{self.nombre} recibe {valor} de daño por {tipo}! HP: {self.HP_actual}/{self.HP_max}")
            elif "HOT" in tipo:
                # Curación sobre tiempo
                self.HP_actual += valor
                if self.HP_actual > self.HP_max:
                    self.HP_actual = self.HP_max
                mensajes.append(f"{self.nombre} se cura {valor} HP por {tipo}!")
                print(f"{self.nombre} se cura {valor} HP por {tipo}! HP: {self.HP_actual}/{self.HP_max}")
            
            # Reducir duración
            efecto["duracion"] -= 1
            
            # Si aún tiene duración, mantener el efecto
            if efecto["duracion"] > 0:
                efectos_restantes.append(efecto)
            else:
                mensajes.append(f"El efecto {tipo} en {self.nombre} ha terminado.")
                print(f"El efecto {tipo} en {self.nombre} ha terminado.")
        
        self.efectos_activos = efectos_restantes
        return mensajes
    
    # --- draw (Sin cambios) ---
    def draw(self, pantalla):
        self.rect.center = (int(self.pos_actual_x), int(self.pos_actual_y))
        pantalla.blit(self.sprite, self.rect)
        
    # --- Funciones de Batalla (Sin cambios) ---
    def establecer_posicion_batalla(self, x, y):
        self.pos_batalla_x = x
        self.pos_batalla_y = y
        self.pos_actual_x = x
        self.pos_actual_y = y
        self.rect.center = (int(self.pos_actual_x), int(self.pos_actual_y))

    def animar_ataque(self, tiempo_actual):
        if not self.anim_atacando:
            self.anim_atacando = True
            self.anim_fase = 1 
            self.anim_timer = tiempo_actual
            print(f"¡{self.nombre} inicia embestida!")

    # --- ¡MODIFICADO! (Paso 48.1) ---
    def update_animacion_ataque(self, tiempo_actual):
        if not self.anim_atacando:
            return True 

        tiempo_transcurrido = tiempo_actual - self.anim_timer
        
        # Fase 1: Moverse adelante
        if self.anim_fase == 1:
            self.pos_actual_x = self.pos_batalla_x + self.DISTANCIA_EMBESTIDA
            # --- ¡MODIFICADO! Más lento (300ms) ---
            if tiempo_transcurrido > 300:
                self.anim_fase = 2 
        
        # Fase 2: Pausa
        elif self.anim_fase == 2:
            # --- ¡MODIFICADO! Más lento (300ms + 300ms) ---
            if tiempo_transcurrido > (300 + 300):
                self.anim_fase = 3
        
        # Fase 3: Moverse atrás
        elif self.anim_fase == 3:
            self.pos_actual_x = self.pos_batalla_x 
            self.anim_fase = 0 
            self.anim_atacando = False
            print(f"¡{self.nombre} termina embestida!")
            return True 
            
        return False
            
    