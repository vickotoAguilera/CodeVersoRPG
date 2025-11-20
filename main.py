import pygame
import sys
import os 
import random
import json # Necesario para cargar el grupo inicial
from src.pantalla_titulo import PantallaTitulo
from src.pantalla_slots import PantallaSlots 
from src.menu_pausa import MenuPausa 
from src.gestor_guardado import GestorGuardado
from src.game_data import traducir_nombre_mapa
# --- (REFRACTORIZADO) ---
from src.config import SAVES_PATH, UI_PATH, DATABASE_PATH 
from src.heroe import Heroe
from src.mapa import Mapa
from src.batalla import Batalla
from src.pantalla_estado import PantallaEstado
from src.pantalla_equipo import PantallaEquipo
from src.pantalla_inventario import PantallaInventario
from src.pantalla_habilidades import PantallaHabilidades  # ¡NUEVO! (Paso 7.18)
# --- NUEVAS IMPORTACIONES (Paso 53.6) ---
from src.asset_coords_db import pillar_coords, COORDS_TERRA as COORDS_TERRA_FALLBACK
 

# 1. Inicializar Pygame
pygame.init()

# --- NUEVAS CONSTANTES DE LA BASE DE DATOS (Paso 53.6) ---
RUTA_HEROES_DB = os.path.join(DATABASE_PATH, "heroes_db.json")
RUTA_GRUPO_INICIAL = os.path.join(DATABASE_PATH, "grupo_inicial.json")
RUTA_EQUIPO_DB = os.path.join(DATABASE_PATH, "equipo_db.json")
RUTA_ITEMS_DB = os.path.join(DATABASE_PATH, "items_db.json")
RUTA_HABILIDADES_DB = os.path.join(DATABASE_PATH, "habilidades_db.json")
# --------------------------------------------------------

# 2. Definir el tamaño de la ventana
ANCHO = 800
ALTO = 600
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Code Verso RPG")
mi_fuente_debug = pygame.font.Font(None, 30)
reloj = pygame.time.Clock() #El reloj que controla los FPS
# --- Cargar Bases de Datos Globales ---
try:
    with open(RUTA_HEROES_DB, 'r', encoding='utf-8') as f:
        HEROES_DB = json.load(f)
    with open(RUTA_EQUIPO_DB, 'r', encoding='utf-8') as f:
        EQUIPO_DB = json.load(f)
    with open(RUTA_ITEMS_DB, 'r', encoding='utf-8') as f:
        ITEMS_DB = json.load(f)
    with open(RUTA_HABILIDADES_DB, 'r', encoding='utf-8') as f:
        HABILIDADES_DB = json.load(f)
except FileNotFoundError as e:
    print(f"¡ERROR CRÍTICO! No se pudo cargar una base de datos: {e}")
    pygame.quit(); sys.exit()
except json.JSONDecodeError as e:
    print(f"¡ERROR CRÍTICO! Una base de datos JSON está malformada: {e}")
    pygame.quit(); sys.exit()
# --- FIN Carga Global ---

# --- Carga del Cursor "Mano" (Sin cambios) ---
try:
    ruta_cursor = os.path.join(UI_PATH, "cursor_mano.png")
    CURSOR_IMG = pygame.image.load(ruta_cursor).convert_alpha()
    CURSOR_IMG = pygame.transform.scale(CURSOR_IMG, (17*2, 16*2))
except FileNotFoundError:
    print(f"¡ADVERTENCIA! No se encontró el cursor en {ruta_cursor}")
    print("Usando 'fallback' de texto '>'")
    CURSOR_IMG = None 
# --- FIN CARGA CURSOR ---

# 3. ¡CREAMOS LOS OBJETOS!
mi_pantalla_titulo = PantallaTitulo(ANCHO, ALTO, CURSOR_IMG)
mi_pantalla_slots = None 
mi_menu_pausa = None 
mi_mapa = None
grupo_heroes = []
mi_pantalla_estado = None 
mi_pantalla_equipo = None
mi_pantalla_inventario = None
mi_pantalla_habilidades = None  # ¡NUEVO! (Paso 7.18)


def resolver_mapa(nombre_mapa, categoria_guess):
    """Resolver el nombre de archivo y categoría reales del mapa. Devuelve (nombre_archivo, categoria).
    Si no encuentra en la categoría indicada, busca en todas las subcarpetas de `src/database/mapas` por nombre base.
    """
    # Normalizar base
    base = os.path.splitext(nombre_mapa)[0]

    # 0) Si existe un índice de mapas, intentar resolver por id/nombre/imagen
    try:
        ruta_indice = os.path.join(DATABASE_PATH, 'maps_index.json')
        if os.path.exists(ruta_indice):
            with open(ruta_indice, 'r', encoding='utf-8') as f:
                entradas = json.load(f)
            for e in entradas:
                # Match por id, nombre legible, nombre de imagen (con o sin extensión)
                if e.get('id') == nombre_mapa or e.get('id') == base:
                    return e.get('imagen') or e.get('imagen_ruta') or (base + '.png'), e.get('categoria')
                if e.get('nombre') == nombre_mapa:
                    return e.get('imagen') or e.get('imagen_ruta') or (base + '.png'), e.get('categoria')
                imagen_nom = e.get('imagen') or ''
                if imagen_nom:
                    if os.path.splitext(imagen_nom)[0] == base or imagen_nom == nombre_mapa:
                        return imagen_nom, e.get('categoria')
    except Exception:
        # No hacer fallar la resolución si el índice está corrupto
        pass

    # 1) Buscar imagen en la categoría propuesta (assets/maps)
    mapas_assets_cat = os.path.join('assets', 'maps', categoria_guess)
    for ext in ('.png', '.jpg', '.jpeg'):
        cand = os.path.join(mapas_assets_cat, base + ext)
        if os.path.exists(cand):
            return base + ext, categoria_guess

    # 2) Buscar JSON en la base de datos para descubrir la categoría
    mapas_root = os.path.join(DATABASE_PATH, 'mapas')
    encontrado_categoria = None
    for root, dirs, files in os.walk(mapas_root):
        for f in files:
            if os.path.splitext(f)[0] == base and f.lower().endswith('.json'):
                encontrado_categoria = os.path.relpath(root, mapas_root).replace('\\', '/')
                break
        if encontrado_categoria:
            break

    # 3) Si encontramos categoría por el JSON, buscar la imagen ahí
    if encontrado_categoria:
        mapas_assets_cat = os.path.join('assets', 'maps', encontrado_categoria)
        # Buscar recursivamente dentro de la carpeta de la categoría
        for root, dirs, files in os.walk(mapas_assets_cat):
            for f in files:
                if os.path.splitext(f)[0] == base and os.path.splitext(f)[1].lower() in ('.png', '.jpg', '.jpeg'):
                    # devolver ruta relativa dentro de la carpeta de assets (solo el nombre de archivo, Mapa añadirá la categoría)
                    relpath = os.path.relpath(os.path.join(root, f), os.path.join('assets', 'maps', encontrado_categoria))
                    # si está en subcarpeta, incluirla en el nombre de archivo para que Mapa lo encuentre correctamente
                    return os.path.join(relpath).replace('\\', '/'), encontrado_categoria
        # Si no hay imagen, devolver nombre base con .png por facilidad
        return base + '.png', encontrado_categoria

    # 4) Fallback: si no se encuentra, devolver lo original
    # Añadir extensión .png si no tenía
    if not os.path.splitext(nombre_mapa)[1]:
        return base + '.png', categoria_guess
    return nombre_mapa, categoria_guess
# --- FIN OBJETOS ---

# --- Variables de estado del juego (Sin cambios) ---
estado_juego = "titulo" 
batalla_actual = None 
pasos_desde_batalla = 0
pasos_para_batalla = random.randint(50, 200) 
portal_listo_para_usar = True
tiempo_inicio_partida_ticks = None
tiempo_juego_segundos = 0.0

#variables auto guardado (Sin cambios)
INTERVALO_AUTOGUARDADO= 10 * 60 * 1000 
SLOT_AUTOGUARDADO = 3 
tiempo_ultimo_autoguardado = None 
aviso_autoguardado_activo = False
aviso_autoguardado_inicio = 0

# 4. Bucle principal del juego
while True:
    
    tiempo_actual_ticks = pygame.time.get_ticks()
    
    if tiempo_inicio_partida_ticks is not None:
        if estado_juego == "mapa":
            tiempo_juego_segundos = (tiempo_actual_ticks - tiempo_inicio_partida_ticks) / 1000.0
        
    
    # 5. Manejar eventos
    teclas = pygame.key.get_pressed() 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # --- MANEJO DE CLICS DEL MOUSE ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic izquierdo
            if estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
                accion_hab = mi_pantalla_habilidades.update_input("MOUSE_CLICK")
                if accion_hab and accion_hab.get("accion") == "volver_menu_pausa":
                    print("¡Regresando a Menú de Pausa desde botón!")
                    estado_juego = "menu_pausa"
                    mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                    mi_pantalla_habilidades = None
            
        if event.type == pygame.KEYDOWN:
            
            # --- MANEJO DE TECLA ESCAPE (Global) ---
            if event.key == pygame.K_ESCAPE:
                if estado_juego == "mapa":
                    print("¡Abriendo Menú de Pausa!")
                    estado_juego = "menu_pausa"
                    mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                
                elif estado_juego == "menu_pausa" and mi_menu_pausa:
                    accion_pausa = mi_menu_pausa.update_input(event.key)
                    if accion_pausa == "cerrar_menu":
                        print("¡Cerrando Menú de Pausa!")
                        estado_juego = "mapa"
                        mi_menu_pausa = None
                
                # --- ¡BLOQUE CORREGIDO! (Desanidado) ---
                elif estado_juego == "pantalla_estado" and mi_pantalla_estado:
                    accion_estado = mi_pantalla_estado.update_input(event.key)
                    if accion_estado == "volver_al_menu":
                        estado_juego = "menu_pausa"
                        mi_pantalla_estado = None 

                elif estado_juego == "pantalla_equipo" and mi_pantalla_equipo:
                    accion_equipo = mi_pantalla_equipo.update_input(event.key)
                    if accion_equipo == "volver_al_menu":
                        estado_juego = "menu_pausa"
                        mi_pantalla_equipo = None 

                elif estado_juego == "pantalla_inventario" and mi_pantalla_inventario:
                    accion_inventario = mi_pantalla_inventario.update_input(event.key)
                    if accion_inventario == "volver_al_menu":
                        estado_juego = "menu_pausa"
                        mi_pantalla_inventario = None
                
                # ¡NUEVO! - Manejo de ESC en pantalla habilidades
                elif estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
                    accion_hab = mi_pantalla_habilidades.update_input(event.key)
                    if accion_hab and accion_hab.get("accion") == "volver_menu_pausa":
                        print("¡Regresando a Menú de Pausa desde ESC!")
                        estado_juego = "menu_pausa"
                        mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                        mi_pantalla_habilidades = None
                # --- FIN BLOQUE CORREGIDO ---

            # --- MANEJO DE TECLA ENTER (Por Estado) ---
            if event.key == pygame.K_RETURN: 
                
                # [CANAL 1: TÍTULO]
                if estado_juego == "titulo" and mi_pantalla_titulo:
                    accion_titulo = mi_pantalla_titulo.update_input(event.key)
                    
                    if accion_titulo == "juego_nuevo":
                        print("¡Iniciando Nuevo Juego!")
                        mi_mapa = Mapa("mapa_pradera.jpg", "mundo", ANCHO, ALTO) 
                        grupo_heroes = [] 
                        
                        try:
                            with open(RUTA_GRUPO_INICIAL, 'r', encoding='utf-8') as f:
                                datos_grupo = json.load(f)
                        except FileNotFoundError:
                            print("¡ERROR CRÍTICO! Archivo de grupo inicial no encontrado.")
                            pygame.quit(); sys.exit()

                        for miembro in datos_grupo["miembros"]:
                            id_clase = miembro["id_clase_db"]
                            id_coords = miembro["id_coords_db"]
                            
                            clase_data = HEROES_DB.get(id_clase)
                            coords_data = pillar_coords(id_coords)
                            
                            if clase_data and coords_data:
                                nuevo_heroe = Heroe(
                                    miembro["nombre_en_juego"],
                                    clase_data,
                                    coords_data,
                                    EQUIPO_DB,
                                    HABILIDADES_DB # ¡NUEVO!
                                )
                                nuevo_heroe.HP_actual = nuevo_heroe.HP_max
                                nuevo_heroe.MP_actual = nuevo_heroe.MP_max
                                grupo_heroes.append(nuevo_heroe)
                            else:
                                print(f"¡ADVERTENCIA! Datos incompletos para {miembro['nombre_en_juego']}")

                        # Posicionar héroes en el spawn principal del mapa (si existe)
                        # Activar debug_draw temporal para visualizar muros/portales/spawns
                        try:
                            mi_mapa.debug_draw = True
                            spawn = None
                            if hasattr(mi_mapa, 'spawns') and mi_mapa.spawns:
                                spawn = mi_mapa.spawns[0]
                            if spawn:
                                for i, heroe in enumerate(grupo_heroes):
                                    # desplazar ligeramente para evitar solapamiento
                                    heroe.teletransportar(spawn[0] + (i*16), spawn[1])
                            else:
                                # fallback: centrar grupo en el mapa
                                for i, heroe in enumerate(grupo_heroes):
                                    heroe.teletransportar(mi_mapa.mapa_rect.centerx + (i*16), mi_mapa.mapa_rect.centery)
                        except Exception as e:
                            print(f"¡ADVERTENCIA! No se pudieron posicionar los héroes automáticamente: {e}")

                        estado_juego = "mapa"
                        mi_pantalla_titulo = None 
                        tiempo_inicio_partida_ticks = tiempo_actual_ticks
                        tiempo_ultimo_autoguardado = tiempo_actual_ticks
                        
                    elif accion_titulo == "cargar_juego":
                        print("¡Cambiando a Pantalla de Slots (Modo Cargar)!")
                        estado_juego = "slots_carga"
                        mi_pantalla_slots = PantallaSlots(ANCHO, ALTO, SAVES_PATH, modo="cargar", slot_autoguardado=SLOT_AUTOGUARDADO)
                        mi_pantalla_titulo = None 
                        
                    elif accion_titulo == "salir":
                        pygame.quit()
                        sys.exit()
                
                # [CANAL 2: SLOTS DE CARGA]
                elif estado_juego == "slots_carga" and mi_pantalla_slots:
                    accion_slots = mi_pantalla_slots.update_input(event.key)
                    
                    if accion_slots: 
                        if accion_slots["accion"] == "volver":
                            if accion_slots["origen"] == "titulo":
                                estado_juego = "titulo"
                                mi_pantalla_titulo = PantallaTitulo(ANCHO, ALTO, CURSOR_IMG)
                                mi_pantalla_slots = None
                            elif accion_slots["origen"] == "pausa":
                                estado_juego = "menu_pausa"
                                mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                                mi_pantalla_slots = None 
                        
                        elif accion_slots["accion"] == "cargar_slot":
                            print(f"¡Cargando Slot {accion_slots['slot_id']}!")
                            slot_id = accion_slots['slot_id']
                            datos_cargados = GestorGuardado.cargar_partida(slot_id)
                            
                            if datos_cargados:
                                mi_mapa = Mapa(
                                    datos_cargados["mapa"]["nombre_archivo"],
                                    datos_cargados["mapa"]["categoria"],
                                    ANCHO, ALTO
                                )
                                
                                grupo_heroes = [] 
                                
                                for data_heroe in datos_cargados["grupo"]:
                                    nombre_clase_guardado = data_heroe["nombre_clase"] 
                                    
                                    id_clase_real = ""
                                    id_coords = ""
                                    
                                    if nombre_clase_guardado == "Héroe 1":
                                        id_clase_real = "HEROE_1"
                                        id_coords = "COORDS_CLOUD"
                                    elif nombre_clase_guardado == "Héroe 2":
                                        id_clase_real = "HEROE_2"
                                        id_coords = "COORDS_TERRA"
                                    else:
                                        id_clase_real = "HEROE_2" 
                                        id_coords = "COORDS_TERRA"
                                    
                                    clase_data_base = HEROES_DB.get(id_clase_real, {})
                                    coords_data = pillar_coords(id_coords)
                                    
                                    if not coords_data:
                                        coords_data = COORDS_TERRA_FALLBACK
                                        
                                    nombre_en_juego = data_heroe.get("nombre_en_juego", data_heroe["nombre_clase"])

                                    heroe_cargado = Heroe(
                                        nombre_en_juego, 
                                        clase_data_base, 
                                        coords_data,
                                        EQUIPO_DB, # ¡NUEVO!
                                        HABILIDADES_DB # ¡NUEVO!
                                    )
                                    
                                    heroe_cargado.HP_actual = data_heroe["hp_actual"]
                                    heroe_cargado.HP_max_base = data_heroe.get("hp_max_base", data_heroe.get("hp_max", 100))
                                    heroe_cargado.MP_actual = data_heroe["mp_actual"]
                                    heroe_cargado.MP_max_base = data_heroe.get("mp_max_base", data_heroe.get("mp_max", 20))
                                    heroe_cargado.fuerza_base = data_heroe.get("fuerza_base", data_heroe.get("fuerza", 10))
                                    heroe_cargado.defensa_base = data_heroe.get("defensa_base", data_heroe.get("defensa", 5))
                                    heroe_cargado.inteligencia_base = data_heroe.get("inteligencia_base", data_heroe.get("inteligencia", 8))
                                    heroe_cargado.espiritu_base = data_heroe.get("espiritu_base", data_heroe.get("espiritu", 6))
                                    heroe_cargado.velocidad_base = data_heroe.get("velocidad_base", data_heroe.get("velocidad", 5))
                                    heroe_cargado.suerte_base = data_heroe.get("suerte_base", data_heroe.get("suerte", 5))
                                    heroe_cargado.magias = data_heroe.get("magias", heroe_cargado.magias).copy() 
                                    heroe_cargado.inventario = data_heroe.get("inventario", heroe_cargado.inventario).copy()
                                    heroe_cargado.inventario_especiales = data_heroe.get("inventario_especiales", heroe_cargado.inventario_especiales).copy()
                                    heroe_cargado.equipo = data_heroe.get("equipo", heroe_cargado.equipo).copy()
                                    # --- ¡NUEVO! Sistema de Habilidades (Paso 7.15) ---
                                    heroe_cargado.clase = data_heroe.get("clase", heroe_cargado.clase)
                                    heroe_cargado.ranuras_habilidad_max = data_heroe.get("ranuras_habilidad_max", heroe_cargado.ranuras_habilidad_max)
                                    heroe_cargado.habilidades_activas = data_heroe.get("habilidades_activas", heroe_cargado.habilidades_activas).copy()
                                    heroe_cargado.inventario_habilidades = data_heroe.get("inventario_habilidades", heroe_cargado.inventario_habilidades).copy()
                                    # --------------------------------------------------------
                                    heroe_cargado.oro = data_heroe["oro"]
                                    heroe_cargado.nivel = data_heroe["nivel"]
                                    
                                    heroe_cargado.teletransportar(
                                        data_heroe["pos_x"],
                                        data_heroe["pos_y"]
                                    )
                                    
                                    grupo_heroes.append(heroe_cargado)
                                    
                                tiempo_guardado_seg = datos_cargados["juego"]["tiempo_juego_segundos"]
                                tiempo_guardado_ms = tiempo_guardado_seg * 1000
                                tiempo_inicio_partida_ticks = tiempo_actual_ticks - tiempo_guardado_ms
                                tiempo_ultimo_autoguardado = tiempo_actual_ticks

                                estado_juego = "mapa"
                                mi_pantalla_slots = None
                                
                            else:
                                print(f"¡ERROR! El Slot {slot_id} está corrupto o no se pudo leer.")

                # [CANAL 3: MENÚ PAUSA]
                elif estado_juego == "menu_pausa" and mi_menu_pausa:
                    accion_pausa = mi_menu_pausa.update_input(event.key)
                    
                    if isinstance(accion_pausa, dict):
                        if accion_pausa["accion"] == "ver_estado_heroe":
                            indice = accion_pausa["indice_heroe"]
                            if indice < len(grupo_heroes):
                                heroe_seleccionado = grupo_heroes[indice]
                                print(f"Abriendo pantalla de estado para {heroe_seleccionado.nombre_en_juego}")
                                mi_pantalla_estado = PantallaEstado(ANCHO, ALTO, heroe_seleccionado, CURSOR_IMG)
                                estado_juego = "pantalla_estado"
                        
                        elif accion_pausa["accion"] == "abrir_equipo_heroe":
                            indice = accion_pausa["indice_heroe"]
                            if indice < len(grupo_heroes):
                                heroe_seleccionado = grupo_heroes[indice]
                                print(f"Abriendo pantalla de equipo para {heroe_seleccionado.nombre_en_juego}")
                                mi_pantalla_equipo = PantallaEquipo(ANCHO, ALTO, heroe_seleccionado, EQUIPO_DB, CURSOR_IMG)
                                estado_juego = "pantalla_equipo"
                        
                        # ¡NUEVO! (Paso 7.18) - Abrir Pantalla de Habilidades
                        elif accion_pausa["accion"] == "abrir_habilidades_heroe":
                            indice = accion_pausa["indice_heroe"]
                            if indice < len(grupo_heroes):
                                heroe_seleccionado = grupo_heroes[indice]
                                print(f"Abriendo pantalla de habilidades para {heroe_seleccionado.nombre_en_juego}")
                                mi_pantalla_habilidades = PantallaHabilidades(ANCHO, ALTO, heroe_seleccionado, HABILIDADES_DB, CURSOR_IMG)
                                estado_juego = "pantalla_habilidades"

                    elif isinstance(accion_pausa, str):
                        if accion_pausa == "abrir_items":
                            print("¡Abriendo Pantalla de Inventario!")
                            estado_juego = "pantalla_inventario"
                            mi_pantalla_inventario = PantallaInventario(ANCHO, ALTO, grupo_heroes, ITEMS_DB, CURSOR_IMG)

                        elif accion_pausa == "salir_titulo":
                            estado_juego = "titulo"
                            mi_pantalla_titulo = PantallaTitulo(ANCHO, ALTO, CURSOR_IMG)
                            mi_menu_pausa = None
                            mi_pantalla_slots = None
                            grupo_heroes = [] 
                            mi_mapa = None
                            tiempo_inicio_partida_ticks = None
                            tiempo_juego_segundos = 0.0
                        
                        elif accion_pausa == "abrir_guardar":
                            estado_juego = "slots_guardar"
                            mi_pantalla_slots = PantallaSlots(ANCHO, ALTO, SAVES_PATH, modo="guardar", slot_autoguardado=SLOT_AUTOGUARDADO)
                            mi_menu_pausa = None
                        
                        elif accion_pausa == "abrir_cargar":
                            estado_juego = "slots_carga"
                            mi_pantalla_slots = PantallaSlots(ANCHO, ALTO, SAVES_PATH, modo="cargar", origen="pausa", slot_autoguardado=SLOT_AUTOGUARDADO)
                            mi_menu_pausa = None 
                
                # [CANAL 4: SLOTS DE GUARDADO]
                elif estado_juego == "slots_guardar" and mi_pantalla_slots:
                    accion_slots = mi_pantalla_slots.update_input(event.key)
                    
                    if accion_slots:
                        if accion_slots["accion"] == "volver":
                            estado_juego = "menu_pausa"
                            mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                            mi_pantalla_slots = None
                        
                        elif accion_slots["accion"] == "confirmar_guardado":
                            print("¡Confirmado! ¡Guardando datos!")
                            slot_id = accion_slots["slot_id"]
                            grupo_guardado = []
                            for heroe in grupo_heroes:
                                nombre_en_juego = getattr(heroe, "nombre_en_juego", heroe.nombre_clase)
                                
                                datos_heroe = {
                                    "nombre_en_juego": nombre_en_juego, 
                                    "nombre_clase": heroe.nombre_clase,
                                    "hp_actual": heroe.HP_actual,
                                    "hp_max_base": heroe.HP_max_base,
                                    "mp_actual": heroe.MP_actual,
                                    "mp_max_base": heroe.MP_max_base,
                                    "fuerza_base": heroe.fuerza_base,
                                    "defensa_base": heroe.defensa_base,
                                    "inteligencia_base": heroe.inteligencia_base,
                                    "espiritu_base": heroe.espiritu_base,
                                    "velocidad_base": heroe.velocidad_base,
                                    "suerte_base": heroe.suerte_base,
                                    "magias": heroe.magias,
                                    "inventario": heroe.inventario,
                                    "inventario_especiales": heroe.inventario_especiales,
                                    "equipo": heroe.equipo,
                                    # --- \u00a1NUEVO! Sistema de Habilidades (Paso 7.15) ---
                                    "clase": heroe.clase,
                                    "ranuras_habilidad_max": heroe.ranuras_habilidad_max,
                                    "habilidades_activas": heroe.habilidades_activas,
                                    "inventario_habilidades": heroe.inventario_habilidades,
                                    # --------------------------------------------------------
                                    "oro": heroe.oro,
                                    "nivel": heroe.nivel,
                                    "pos_x": heroe.heroe_rect.x, 
                                    "pos_y": heroe.heroe_rect.y
                                }
                                grupo_guardado.append(datos_heroe)
                            
                            datos_partida = {
                                "grupo": grupo_guardado, 
                                "mapa": {
                                    "nombre_archivo": mi_mapa.nombre_archivo,
                                    "categoria": mi_mapa.categoria
                                },
                                "juego": {
                                    "tiempo_juego_segundos": tiempo_juego_segundos
                                }
                            }
                            
                            exito = GestorGuardado.guardar_partida(slot_id, datos_partida)
                            
                            if exito:
                                estado_juego = "menu_pausa"
                                mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                                mi_pantalla_slots = None
                            else:
                                print("¡ERROR! No se pudo guardar.")
                
                # [CANAL 5: BATALLA]
                elif estado_juego == "batalla" and batalla_actual:
                    batalla_actual.update_input(event.key, tiempo_actual_ticks)
                
                # [CANAL 6: PANTALLA EQUIPO]
                elif estado_juego == "pantalla_equipo" and mi_pantalla_equipo:
                    mi_pantalla_equipo.update_input(event.key)
                
                # [CANAL 7: PANTALLA INVENTARIO]
                elif estado_juego == "pantalla_inventario" and mi_pantalla_inventario:
                    mi_pantalla_inventario.update_input(event.key)
                
                # ¡NUEVO! (Paso 7.18)
                # [CANAL 8: PANTALLA HABILIDADES]
                elif estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
                    accion_habilidades = mi_pantalla_habilidades.update_input(event.key)
                    if accion_habilidades and accion_habilidades.get("accion") == "volver_menu_pausa":
                        print("Cerrando pantalla de habilidades...")
                        estado_juego = "menu_pausa"
                        mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
                        mi_pantalla_habilidades = None
            
            # --- MANEJO DE TECLA 'D' (Detalles) ---
            if event.key == pygame.K_d:
                if estado_juego == "pantalla_equipo" and mi_pantalla_equipo:
                    mi_pantalla_equipo.update_input(event.key)
                elif estado_juego == "pantalla_inventario" and mi_pantalla_inventario:
                    pass  # (Futuro: detalles de ítems)
                # ¡NUEVO! (Paso 7.18) - Tecla D en pantalla habilidades
                elif estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
                    mi_pantalla_habilidades.update_input(event.key)
            
            # ¡NUEVO! (Paso 7.18) - Tecla X para desequipar habilidades
            if event.key == pygame.K_x:
                if estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
                    mi_pantalla_habilidades.update_input(event.key)

    # 6. Actualizar lógica
    if estado_juego == "titulo":
        if mi_pantalla_titulo: mi_pantalla_titulo.update(teclas)
    elif estado_juego == "slots_carga":
        if mi_pantalla_slots: mi_pantalla_slots.update(teclas)
    elif estado_juego == "slots_guardar":
        if mi_pantalla_slots: mi_pantalla_slots.update(teclas)
    elif estado_juego == "menu_pausa":
        if mi_menu_pausa: mi_menu_pausa.update(teclas,  grupo_heroes)
    elif estado_juego == "pantalla_estado":
        if mi_pantalla_estado: mi_pantalla_estado.update(teclas)
    elif estado_juego == "pantalla_equipo":
        if mi_pantalla_equipo: mi_pantalla_equipo.update(teclas) 
    elif estado_juego == "pantalla_inventario":
        if mi_pantalla_inventario: mi_pantalla_inventario.update(teclas)
    # ¡NUEVO! (Paso 7.18)
    elif estado_juego == "pantalla_habilidades":
        if mi_pantalla_habilidades: mi_pantalla_habilidades.update(teclas)
    
    # --- Lógica del MAPA ---
    elif estado_juego == "mapa":
        if grupo_heroes and mi_mapa and tiempo_ultimo_autoguardado: 
            tiempo_actual = tiempo_actual_ticks
            
            if tiempo_actual - tiempo_ultimo_autoguardado > INTERVALO_AUTOGUARDADO:
                print(f"¡Disparando Autoguardado en Slot {SLOT_AUTOGUARDADO}!")
                
                grupo_guardado = []
                for heroe in grupo_heroes:
                    nombre_en_juego = getattr(heroe, "nombre_en_juego", heroe.nombre_clase)
                    
                    datos_heroe = {
                        "nombre_en_juego": nombre_en_juego, 
                        "nombre_clase": heroe.nombre_clase,
                        "hp_actual": heroe.HP_actual,
                        "hp_max_base": heroe.HP_max_base,
                        "mp_actual": heroe.MP_actual,
                        "mp_max_base": heroe.MP_max_base,
                        "fuerza_base": heroe.fuerza_base,
                        "defensa_base": heroe.defensa_base,
                        "inteligencia_base": heroe.inteligencia_base,
                        "espiritu_base": heroe.espiritu_base,
                        "velocidad_base": heroe.velocidad_base,
                        "suerte_base": heroe.suerte_base,
                        "magias": heroe.magias,
                        "inventario": heroe.inventario,
                        "equipo": heroe.equipo,
                        "oro": heroe.oro,
                        "nivel": heroe.nivel,
                        "pos_x": heroe.heroe_rect.x,
                        "pos_y": heroe.heroe_rect.y
                    }
                    grupo_guardado.append(datos_heroe)
                
                datos_partida = {
                    "grupo": grupo_guardado, 
                    "mapa": {
                        "nombre_archivo": mi_mapa.nombre_archivo,
                        "categoria": mi_mapa.categoria
                    },
                    "juego": {
                        "tiempo_juego_segundos": tiempo_juego_segundos
                    }
                }
                
                GestorGuardado.guardar_partida(SLOT_AUTOGUARDADO, datos_partida)
                aviso_autoguardado_activo = True
                aviso_autoguardado_inicio = tiempo_actual
                tiempo_ultimo_autoguardado = tiempo_actual
        
        if grupo_heroes and mi_mapa: 
            heroe_lider = grupo_heroes[0] 
            
            heroe_lider.update(teclas, mi_mapa.mapa_img, mi_mapa.muros)
            
            mi_mapa.update_camara(heroe_lider)
            portal_tocado = mi_mapa.chequear_portales(heroe_lider.heroe_rect)
            
            if portal_tocado and portal_listo_para_usar:
                nombre_mapa_nuevo = portal_tocado["mapa_destino"]
                categoria_nueva = portal_tocado["categoria_destino"]
                pos_nueva = portal_tocado["pos_destino"]
                # Resolver nombre de archivo y categoría reales antes de crear Mapa
                archivo_img, categoria_real = resolver_mapa(nombre_mapa_nuevo, categoria_nueva)
                mi_mapa = Mapa(archivo_img, categoria_real, ANCHO, ALTO)
                if pos_nueva:
                    heroe_lider.teletransportar(pos_nueva[0], pos_nueva[1])
                portal_listo_para_usar = False
                pasos_desde_batalla = 0
            elif not portal_tocado:
                portal_listo_para_usar = True
            
            zona_actual = mi_mapa.chequear_zona(heroe_lider.heroe_rect)
            
            if heroe_lider.heroe_esta_caminando and zona_actual != "segura": 
                pasos_desde_batalla += 1
                if pasos_desde_batalla >= pasos_para_batalla:
                    estado_juego = "batalla" 
                    batalla_actual = Batalla(ANCHO, ALTO, grupo_heroes, zona_actual, CURSOR_IMG) 
                    pasos_desde_batalla = 0
                    pasos_para_batalla = random.randint(50, 200 )
            elif not heroe_lider.heroe_esta_caminando or zona_actual == "segura":
                 pasos_desde_batalla = 0 
    
    # --- Lógica de Batalla ---
    elif estado_juego == "batalla":
        if batalla_actual:
            resultado_batalla = batalla_actual.update(teclas, tiempo_actual_ticks)
            if resultado_batalla == "mapa":
                estado_juego = "mapa"; batalla_actual = None
                for heroe in grupo_heroes:
                    if not heroe.esta_muerto(): # Solo curar a los vivos
                        heroe.HP_actual = heroe.HP_max
                        heroe.MP_actual = heroe.MP_max
                portal_listo_para_usar = True 
    
    # --- 7. Dibujar en la pantalla ---
    PANTALLA.fill((0, 0, 0)) 

    if estado_juego == "titulo":
        if mi_pantalla_titulo: mi_pantalla_titulo.draw(PANTALLA)
    
    elif estado_juego == "slots_carga":
        if mi_pantalla_slots: mi_pantalla_slots.draw(PANTALLA)

    elif estado_juego == "mapa":
        if mi_mapa and grupo_heroes: 
            heroe_lider = grupo_heroes[0] 
            mi_mapa.draw(PANTALLA)
            heroe_lider.draw(PANTALLA, mi_mapa.camara_rect) 
            texto_coords = f"X: {heroe_lider.heroe_rect.x}  Y: {heroe_lider.heroe_rect.y}"
            texto_surf = mi_fuente_debug.render(texto_coords, True, (255, 255, 255), (0, 0, 0))
            PANTALLA.blit(texto_surf, (10, 10))

    elif estado_juego == "batalla":
        if batalla_actual: batalla_actual.draw(PANTALLA) 

    # --- ¡BLOQUE CORREGIDO! (Desanidado) ---
    elif estado_juego == "menu_pausa" or estado_juego == "slots_guardar" or estado_juego == "pantalla_estado" or estado_juego == "pantalla_equipo" or estado_juego == "pantalla_inventario" or estado_juego == "pantalla_habilidades":
        # 1. Dibujar el fondo del mapa (pausado)
        if mi_mapa and grupo_heroes: 
            heroe_lider = grupo_heroes[0] 
            mi_mapa.draw(PANTALLA)
            heroe_lider.draw(PANTALLA, mi_mapa.camara_rect) 
        
        # 2. Dibujar el menú de pausa (siempre de fondo si está en submenú)
        if (estado_juego == "menu_pausa" or estado_juego == "pantalla_estado" or estado_juego == "pantalla_equipo" or estado_juego == "pantalla_inventario" or estado_juego == "pantalla_habilidades") and mi_menu_pausa:
            mi_menu_pausa.draw(PANTALLA, grupo_heroes, tiempo_juego_segundos, mi_mapa.nombre_archivo) 
        
        # 3. Dibujar slots (si está activo)
        elif estado_juego == "slots_guardar" and mi_pantalla_slots:
            mi_pantalla_slots.draw(PANTALLA)

        # 4. Dibujar pantalla de estado (ENCIMA del menú de pausa)
        if estado_juego == "pantalla_estado" and mi_pantalla_estado:
            mi_pantalla_estado.draw(PANTALLA)

        # 5. Dibujar pantalla de equipo (ENCIMA del menú de pausa)
        if estado_juego == "pantalla_equipo" and mi_pantalla_equipo:
            mi_pantalla_equipo.draw(PANTALLA)
            
        # 6. Dibujar pantalla de inventario (ENCIMA del menú de pausa)
        if estado_juego == "pantalla_inventario" and mi_pantalla_inventario:
            mi_pantalla_inventario.draw(PANTALLA)
        
        # ¡NUEVO! (Paso 7.18)
        # 7. Dibujar pantalla de habilidades (ENCIMA del menú de pausa)
        if estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
            mi_pantalla_habilidades.draw(PANTALLA)
    # --- FIN BLOQUE CORREGIDO ---
            
    # --- (Aviso de Autoguardado - Sin cambios) ---
    if aviso_autoguardado_activo:
        tiempo_transcurrido = tiempo_actual_ticks - aviso_autoguardado_inicio
        if tiempo_transcurrido < 3000:
            num_puntos = int(tiempo_transcurrido / 500) % 4
            puntos_str = "." * num_puntos
            texto_aviso = f"Autoguardando{puntos_str}"
            aviso_surf = mi_fuente_debug.render(texto_aviso, True, (255, 255, 255), (0, 0, 0))
            aviso_rect = aviso_surf.get_rect(bottomright=(ANCHO - 15, ALTO - 15))
            fondo_aviso = pygame.Surface((aviso_rect.width + 10, aviso_rect.height + 10))
            fondo_aviso.set_alpha(180) 
            fondo_aviso.fill((0, 0, 0))
            PANTALLA.blit(fondo_aviso, (aviso_rect.x - 5, aviso_rect.y - 5))
            PANTALLA.blit(aviso_surf, aviso_rect)
        else:
            aviso_autoguardado_activo = False

    
    # 8. Actualizar la pantalla
    reloj.tick(60) #Limita el juego a 60 FPS
    pygame.display.update()