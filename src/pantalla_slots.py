import pygame
import sys
import os
import json 
from src.gestor_guardado import GestorGuardado
from src.game_data import traducir_nombre_mapa

class PantallaSlots:
    
    # --- 1. EL CONSTRUCTOR (Sin cambios) ---
    def __init__(self, ancho_pantalla, alto_pantalla, ruta_saves, modo="cargar", origen="titulo", slot_autoguardado=None):
        print(f"¡Creando Pantalla de Slots! (Modo: {modo}, Origen: {origen})")
        self.ANCHO = ancho_pantalla
        self.ALTO = alto_pantalla
        self.RUTA_SAVES = ruta_saves
        self.modo = modo 
        self.origen = origen 
        self.SLOT_AUTOGUARDADO = slot_autoguardado
        
        try:
            pygame.font.init() 
            self.fuente_titulo = pygame.font.Font(None, 70) 
            self.fuente_slot_titulo = pygame.font.Font(None, 30)
            self.fuente_datos = pygame.font.Font(None, 28)
            self.fuente_empty = pygame.font.Font(None, 45)
        except pygame.error as e:
            print(f"Error al cargar la fuente: {e}"); pygame.quit(); sys.exit()

        # --- Opciones del Menú (Sin cambios) ---
        self.total_slots = 3
        self.opcion_seleccionada = 0
        self.opciones_slots_info = [] 
        
        # --- Cooldown (Sin cambios) ---
        self.tiempo_ultimo_input = pygame.time.get_ticks()
        self.COOLDOWN_INPUT = 200
        
        # --- Colores (Sin cambios) ---
        self.COLOR_FONDO = (0, 0, 20) 
        self.COLOR_CAJA = (0, 0, 139) 
        self.COLOR_BORDE = (255, 255, 255) 
        self.COLOR_BORDE_SEL = (255, 255, 0)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_TEXTO_SEL = (255, 255, 0)
        self.COLOR_VACIO = (100, 100, 100) 
        self.UI_BORDER_RADIUS = 10 
        
        # --- Título dinámico (Sin cambios) ---
        if self.modo == "cargar":
            self.titulo_pantalla = "Cargar Partida"
        else:
            self.titulo_pantalla = "Guardar Partida"

        self.actualizar_info_slots()
        
    # --- _formatear_tiempo (Sin cambios) ---
    def _formatear_tiempo(self, segundos_totales):
        """
        Toma un número de segundos (float o int) y
        lo devuelve como un string formateado HH:MM:SS.
        """
        segundos_int = int (segundos_totales)
        horas = segundos_int // 3600
        minutos = (segundos_int % 3600) // 60
        segundos = segundos_int % 60
        return f"{horas:02}:{minutos:02}:{segundos:02}"

    # --- ¡MODIFICADA! AHORA LEE LOS DATOS REALES ---
    def actualizar_info_slots(self):
        self.opciones_slots_info = [] 
        
        for i in range(self.total_slots):
            slot_num = i + 1
            if self.modo == "guardar" and slot_num == self.SLOT_AUTOGUARDADO:
                self.opciones_slots_info.append({
                    "accion": "autoguardado", 
                    "slot_id": slot_num,
                    "data": None 
                })
                continue 
            
            if GestorGuardado.chequear_slot(slot_num):
                datos_partida = GestorGuardado.cargar_partida(slot_num)
                
                if datos_partida:
                    try:
                        # --- ¡"RECABLEADO" (REFACTOR) BKN! (Paso 51.3) ---
                        
                        # 1. "Pillamos" (Obtenemos) al Héroe Líder (el [0]) del grupo
                        heroe_lider_data = datos_partida["grupo"][0]
                        
                        # 2. "Pillamos" (Extraemos) los datos del Líder
                        level = heroe_lider_data["nivel"]
                        oro = heroe_lider_data["oro"]
                        
                        # 3. "Pillamos" (Extraemos) los datos del Juego
                        #    ¡ESTA LÍNEA FALTABA BKN!
                        mapa_archivo = datos_partida["mapa"]["nombre_archivo"]
                        tiempo_seg = datos_partida["juego"]["tiempo_juego_segundos"]
                        
                        # --- FIN DEL "RECABLEO" (REFACTOR) ---
                        
                        # 4. Usamos el traductor y el formateador
                        datos_para_mostrar = {
                            "level": level,
                            "mapa": traducir_nombre_mapa(mapa_archivo),
                            "oro": oro,
                            "tiempo": self._formatear_tiempo(tiempo_seg)
                        }
                        self.opciones_slots_info.append({
                            "accion": "ocupado",
                            "slot_id": slot_num,
                            "data": datos_para_mostrar 
                        })
                    except (KeyError, TypeError, IndexError): # (¡Añadido IndexError por si "grupo" está vacío!)
                        # El JSON fue leído pero le faltan datos o el formato es antiguo
                        self.opciones_slots_info.append({
                            "accion": "corrupto",
                            "slot_id": slot_num,
                            "data": None
                        })
                else:
                    # El archivo existe pero GestorGuardado no pudo leerlo (JSON malformado)
                    self.opciones_slots_info.append({
                        "accion": "corrupto",
                        "slot_id": slot_num,
                        "data": None
                    })
            else:
                # El archivo no existe
                self.opciones_slots_info.append({"accion": "vacio", "data": None, "slot_id": slot_num})
        
        # Añadir la opción de "Volver" al final
        self.opciones_slots_info.append({"accion": "volver", "data": None})

    # --- 2. EL UPDATE (Sin cambios) ---
    def update(self, teclas):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_ultimo_input > self.COOLDOWN_INPUT:
            if teclas[pygame.K_DOWN]:
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones_slots_info)
                self.tiempo_ultimo_input = tiempo_actual
            elif teclas[pygame.K_UP]:
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_slots_info)
                self.tiempo_ultimo_input = tiempo_actual
        return None

    # --- 3. EL UPDATE_INPUT (Sin cambios) ---
    def update_input(self, tecla):
        if tecla == pygame.K_RETURN: # Tecla ENTER
            
            opcion = self.opciones_slots_info[self.opcion_seleccionada]
            accion = opcion["accion"]

            if accion == "autoguardado":
                print("¡Este slot es solo para autoguardado!")
                return None
            
            if accion == "volver":
                print(f"¡Volviendo! (Origen: {self.origen})")
                return {"accion": "volver", "origen": self.origen}
            
            slot_num = opcion["slot_id"]

            if self.modo == "cargar":
                if accion == "ocupado":
                    print(f"¡Seleccionado 'Cargar Slot {slot_num}'!")
                    return {"accion": "cargar_slot", "slot_id": slot_num}
                else: 
                    print("¡Este slot está vacío!")
                    return None

            elif self.modo == "guardar":
                print(f"¡Seleccionado 'Guardar en Slot {slot_num}'!")
                return {"accion": "confirmar_guardado", "slot_id": slot_num}
                
        return None

    # --- 4. EL DRAW (Sin cambios) ---
    def draw(self, pantalla):
        
        pantalla.fill(self.COLOR_FONDO)
        
        # 1. Título
        texto_titulo_surf = self.fuente_titulo.render(self.titulo_pantalla, True, self.COLOR_TEXTO)
        titulo_rect = texto_titulo_surf.get_rect(center=(self.ANCHO // 2, 60))
        pantalla.blit(texto_titulo_surf, titulo_rect)
        
        # 2. Geometría (Corregida)
        box_ancho = self.ANCHO - 80 
        box_alto = 110 
        padding_y = 15 
        start_y = 100 
        
        # 3. Dibujar Opciones
        for i, opcion in enumerate(self.opciones_slots_info):
            
            box_y = start_y + (i * (box_alto + padding_y))
            caja_rect = pygame.Rect(40, box_y, box_ancho, box_alto)
            
            if i == self.opcion_seleccionada:
                color_borde = self.COLOR_BORDE_SEL
                color_texto = self.COLOR_TEXTO_SEL
            else:
                color_borde = self.COLOR_BORDE
                color_texto = self.COLOR_TEXTO

            pygame.draw.rect(pantalla, self.COLOR_CAJA, caja_rect, border_radius=self.UI_BORDER_RADIUS)
            
            if opcion["accion"] == "volver":
                texto_volver_surf = self.fuente_empty.render("Volver", True, color_texto)
                texto_rect = texto_volver_surf.get_rect(center=caja_rect.center)
                pantalla.blit(texto_volver_surf, texto_rect)
            elif opcion["accion"] == "autoguardado":
                color_auto = (70, 70, 70) 
                if i == self.opcion_seleccionada:
                    color_auto = (100, 100, 100) 
                    
                texto_vacio_surf = self.fuente_empty.render("SLOT DE AUTOGUARDADO", True, color_auto)
                texto_rect = texto_vacio_surf.get_rect(center=caja_rect.center)
                pantalla.blit(texto_vacio_surf, texto_rect)
            
            elif opcion["accion"] == "corrupto":
                color_corrupto = (255, 50, 50)
                if i == self.opcion_seleccionada:
                    color_corrupto = (255, 150, 150)
                
                texto_vacio_surf = self.fuente_empty.render("DATOS CORRUPTOS",True, color_corrupto)
                texto_rect = texto_vacio_surf.get_rect(center=caja_rect.center)
                pantalla.blit(texto_vacio_surf, texto_rect)
                            
            elif opcion["accion"] == "vacio":
                color_vacio = self.COLOR_VACIO
                if self.modo == "guardar" and i == self.opcion_seleccionada:
                    color_vacio = self.COLOR_TEXTO_SEL
                
                texto_vacio_surf = self.fuente_empty.render("VACÍO", True, color_vacio)
                texto_rect = texto_vacio_surf.get_rect(center=caja_rect.center)
                pantalla.blit(texto_vacio_surf, texto_rect)

            elif opcion["accion"] == "ocupado":
                datos = opcion["data"]
                
                titulo_slot_surf = self.fuente_slot_titulo.render(f"SLOT {opcion['slot_id']}", True, color_texto)
                pantalla.blit(titulo_slot_surf, (caja_rect.x + 20, caja_rect.y + 15))
                
                level_text = f"Nivel: {datos['level']}"
                level_surf = self.fuente_datos.render(level_text, True, self.COLOR_TEXTO)
                pantalla.blit(level_surf, (caja_rect.x + 200, caja_rect.y + 30))
                
                mapa_text = f"Lugar: {datos['mapa']}"
                mapa_surf = self.fuente_datos.render(mapa_text, True, self.COLOR_TEXTO)
                pantalla.blit(mapa_surf, (caja_rect.x + 200, caja_rect.y + 60))

                oro_text = f"Oro: {datos['oro']}"
                oro_surf = self.fuente_datos.render(oro_text, True, self.COLOR_TEXTO)
                pantalla.blit(oro_surf, (caja_rect.right - 200, caja_rect.y + 30))
                
                tiempo_text = f"Tiempo: {datos['tiempo']}"
                tiempo_surf = self.fuente_datos.render(tiempo_text, True, self.COLOR_TEXTO)
                pantalla.blit(tiempo_surf, (caja_rect.right - 200, caja_rect.y + 60))

            pygame.draw.rect(pantalla, color_borde, caja_rect, 4, border_radius=self.UI_BORDER_RADIUS)