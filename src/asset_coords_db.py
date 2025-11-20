import pygame
import os
import sys 

# --- 1. COORDENADAS DE CLOUD (¡"RECABLEADO" (REFACTOR) BKN!) ---
# (Basado en el nuevo 'heroe_cloud.png' 2x6 BKN)
CLOUD_W = 16 # Ancho del frame
CLOUD_H = 25 # Alto del frame
CLOUD_X_OFFSET = 1 # (¡"Pilla" (Usa) el Left: 1 BKN!)
CLOUD_Y_OFFSET = 0 # (¡"Pilla" (Usa) el Top: 0 BKN!)

# "Pillamos" (Calculamos) el "Pitch" (espacio) BKN:
# 109px (ancho total) - 1px (offset) = 108px para 6 frames
# 108 / 6 = 18px (¡"Pitch X" BKN!)
PITCH_X = 18 
# 51px (alto total) / 2 filas = 25.5px (¡"Pitch Y" BKN! "Usamos" (Redondeamos) 25)
PITCH_Y = 25 

COORDS_CLOUD = {
    "HOJA_SPRITES": "heroe_cloud.png",
    "ESCALA": 1.8, # (¡Lo "hacemos" (ponemos) más grande BKN!)
    "VELOCIDAD": 3,
    
    # --- FILA 1 (Y=0) ---
    # Walk Down (Frames 1-3)
    "PARADO_ABAJO":       (CLOUD_X_OFFSET + (PITCH_X*0), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    "CAMINAR_ABAJO_1":    (CLOUD_X_OFFSET + (PITCH_X*1), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    "CAMINAR_ABAJO_2":    (CLOUD_X_OFFSET + (PITCH_X*2), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    # Walk Left (Frames 4-6)
    "PARADO_IZQUIERDA":   (CLOUD_X_OFFSET + (PITCH_X*3), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    "CAMINAR_IZQUIERDA_1":(CLOUD_X_OFFSET + (PITCH_X*4), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    "CAMINAR_IZQUIERDA_2":(CLOUD_X_OFFSET + (PITCH_X*5), CLOUD_Y_OFFSET + (PITCH_Y*0), CLOUD_W, CLOUD_H),
    
    # --- FILA 2 (Y=25) ---
    # Walk Up (Frames 7-9)
    "PARADO_ARRIBA":      (CLOUD_X_OFFSET + (PITCH_X*0), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    "CAMINAR_ARRIBA_1":   (CLOUD_X_OFFSET + (PITCH_X*1), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    "CAMINAR_ARRIBA_2":   (CLOUD_X_OFFSET + (PITCH_X*2), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    # Walk Right (Frames 10-12)
    "PARADO_DERECHA":     (CLOUD_X_OFFSET + (PITCH_X*3), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    "CAMINAR_DERECHA_1":  (CLOUD_X_OFFSET + (PITCH_X*4), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    "CAMINAR_DERECHA_2":  (CLOUD_X_OFFSET + (PITCH_X*5), CLOUD_Y_OFFSET + (PITCH_Y*1), CLOUD_W, CLOUD_H),
    
    # (¡"Fileteado" (Eliminado) el DESMAYO BKN, "tal como" (según) "pediste" (solicitaste)!)
}

# --- 2. COORDENADAS DE TERRA (El "Fallback" (Alternativa) BKN) ---
TERRA_ANCHO = 32
TERRA_ALTO = 48
TERRA_Y1 = 45 
TERRA_Y2 = 93
COORDS_TERRA = {
    "HOJA_SPRITES": "heroe_sheet.png", 
    "ESCALA": 1.0,
    "VELOCIDAD": 3,
    "PARADO_ABAJO": (0, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_ABAJO_1": (32, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_ABAJO_2": (64, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "PARADO_ARRIBA": (96, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_ARRIBA_1": (128, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_ARRIBA_2": (160, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "PARADO_IZQUIERDA": (192, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_IZQUIERDA_1": (224, TERRA_Y1, TERRA_ANCHO, TERRA_ALTO),
    "CAMINAR_IZQUIERDA_2": (0, TERRA_Y2, TERRA_ANCHO, TERRA_ALTO),
    # (¡"Pega" (Trabajo) futura BKN! "Enchufar" (Agregar) coords de Batalla)
}


# --- 3. EL "CEREBRO" (Motor) BKN ---
ASSET_COORDS_DB = {
    "COORDS_TERRA": COORDS_TERRA,
    "COORDS_CLOUD": COORDS_CLOUD,
}

def pillar_coords(coords_id_bkn):
    """
    "Pilla" (Obtiene) el diccionario de coordenadas BKN 
    desde la "Enciclopedia" (DB) Maestra BKN.
    """
    print(f"¡'Pillando' (Buscando) Coords ID: {coords_id_bkn}!")
    return ASSET_COORDS_DB.get(coords_id_bkn)