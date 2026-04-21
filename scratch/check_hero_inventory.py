import json, sys, os
# Add project root to path so 'src' package can be imported
sys.path.append('c:/Users/Usuario/Desktop/RPG')
from src.heroe import Heroe
# Load hero data
with open('c:/Users/Usuario/Desktop/RPG/src/database/heroes_db.json', 'r', encoding='utf-8') as f:
    heroes_db = json.load(f)
hero_data = heroes_db['HEROE_1']
# Minimal coords data required for Heroe init (sprite sheet placeholders)
coords_data = {
    'VELOCIDAD': 5,
    'HOJA_SPRITES': 'hero_sprites.png',
    'ESCALA': 1,
    'PARADO_ABAJO': (0,0,32,32),
    'PARADO_ARRIBA': (0,0,32,32),
    'PARADO_IZQUIERDA': (0,0,32,32),
    'PARADO_DERECHA': (0,0,32,32),
    'CAMINAR_ABAJO_1': (0,0,32,32),
    'CAMINAR_ABAJO_2': (0,0,32,32),
    'CAMINAR_ARRIBA_1': (0,0,32,32),
    'CAMINAR_ARRIBA_2': (0,0,32,32),
    'CAMINAR_IZQUIERDA_1': (0,0,32,32),
    'CAMINAR_IZQUIERDA_2': (0,0,32,32),
    'CAMINAR_DERECHA_1': (0,0,32,32),
    'CAMINAR_DERECHA_2': (0,0,32,32),
}
# Dummy equipment DB (only needed for init)
equipment_db = {}
hero = Heroe('TestHero', hero_data, coords_data, equipment_db, {})
print('=== Inventario del héroe ===')
for item_id, qty in hero.inventario.items():
    print(f"{item_id}: {qty}")
print('Oro inicial:', hero.oro)
