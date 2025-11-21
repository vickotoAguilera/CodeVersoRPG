import sys, os
# Asegurar que el repo root está en sys.path
repo_root = os.path.abspath(os.getcwd())
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import pygame
from src.mapa import Mapa

pygame.init()
# Inicializar un modo de vídeo mínimo para permitir convert()/convert_alpha()
try:
    pygame.display.set_mode((1, 1))
except Exception:
    pass
print('PWD:', repo_root)
print('Cargando mapa usando categoria "ciudades_y_pueblos"')
try:
    m = Mapa('mapa_herrero.png', 'ciudades_y_pueblos', 800, 600)
    print('spawns:', len(m.spawns))
    print('spawns list:', m.spawns)
    print('muros:', len(m.muros))
    print('portales:', len(m.portales))
    for p in m.portales:
        print('portal caja:', p.get('caja'))
except Exception as e:
    print('Error:', e)

# --- Simular transición desde 'mapa_pueblo_final' hacia 'mapa_herrero' ---
print('\n--- Simulando portal desde mapa_pueblo_final -> mapa_herrero ---')
from src.mapa import Mapa as MapaClass
try:
    src_map = MapaClass('mapa_pueblo_final.png', 'ciudades_y_pueblos', 800, 600)
    # Buscar portal que apunte a 'mapa_herrero'
    portal_herrero = None
    for p in src_map.portales:
        if p.get('mapa_destino') == 'mapa_herrero':
            portal_herrero = p
            break
    print('Portal encontrado en pueblo_final:', bool(portal_herrero))
    if portal_herrero:
        # Crear mapa destino como hace main
        dest_map = MapaClass('mapa_herrero.png', 'ciudades_y_pueblos', 800, 600)
        # Intentar usar spawn_destino_id
        spawn_id = portal_herrero.get('spawn_destino_id')
        print('portal spawn_destino_id:', spawn_id)
        if spawn_id and hasattr(dest_map, 'spawns_ids') and spawn_id in dest_map.spawns_ids:
            print('Destino spawn coords:', dest_map.spawns_ids[spawn_id])
        else:
            print('No se encontró spawn por ID en destino; dest_map.spawns:', dest_map.spawns)
except Exception as e:
    print('Error simulacion:', e)

pygame.quit()
