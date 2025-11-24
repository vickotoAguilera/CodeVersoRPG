import pygame
from src.mapa import Mapa

pygame.init()
print('--- Cargando con categoria: ciudades_y_pueblos/pueblo_inicio ---')
try:
    m = Mapa('mapa_herrero.png', 'ciudades_y_pueblos/pueblo_inicio', 800, 600)
    print('spawns:', len(m.spawns))
    print('muros:', len(m.muros))
    print('portales:', len(m.portales))
except Exception as e:
    print('Error:', e)

print('\n--- Cargando con categoria: ciudades_y_pueblos ---')
try:
    m2 = Mapa('mapa_herrero.png', 'ciudades_y_pueblos', 800, 600)
    print('spawns:', len(m2.spawns))
    print('muros:', len(m2.muros))
    print('portales:', len(m2.portales))
except Exception as e:
    print('Error:', e)

pygame.quit()
