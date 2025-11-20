import os

# --- Definimos las rutas "A Prueba de Balas" ---

# __file__ es la ruta a este archivo (src/config.py)
# script_path es la ruta a la carpeta 'src'
script_path = os.path.dirname(os.path.abspath(__file__))

# subimos un nivel para llegar a la raíz del proyecto (RPG/)
ROOT_PATH = os.path.dirname(script_path)

# Creamos las rutas a las carpetas de assets
ASSETS_PATH = os.path.join(ROOT_PATH, "assets")
HEROES_SPRITES_PATH = os.path.join(ASSETS_PATH, "sprites", "heroes")
MONSTRUOS_SPRITES_PATH = os.path.join(ASSETS_PATH, "sprites", "monstruos")
MAPS_PATH = os.path.join(ASSETS_PATH, "maps")
BACKGROUNDS_PATH = os.path.join(ASSETS_PATH, "backgrounds")
# --- ¡NUEVA LÍNEA BKN! "Enchufamos" (Agregamos) la ruta del Cursor (Paso 56.2) ---
UI_PATH = os.path.join(ASSETS_PATH, "ui")
# --- FIN NUEVO ---

# --- ¡NUEVO! Ruta a la "Enciclopedia" del juego ---
DATABASE_PATH = os.path.join(ROOT_PATH, "src", "database")
# --- ¡NUEVO! Ruta a los archivos del Jugador ---
SAVES_PATH = os.path.join(ROOT_PATH, "saves")