import json
import editor_portales
from pathlib import Path

print('END-TO-END TEST: crear->vincular->renombrar->guardar')
ep = editor_portales.EditorPortales()
# Mapas de prueba (categoria existente 'ciudades')
map_a = editor_portales.MapaInfo('test_mapa_a','file','assets/maps/whatever.png','ciudades')
map_b = editor_portales.MapaInfo('test_mapa_b','file','assets/maps/whatever2.png','ciudades')
ep.mapa_izq = map_a
ep.mapa_der = map_b

# Crear un portal en cada lado (simulando creación por rect)
p_left = editor_portales.PortalRect('', 30, 40, 24, 32)
p_right = editor_portales.PortalRect('', 120, 140, 24, 32)
ep.izq_portales.append(p_left)
ep.der_portales.append(p_right)
print('IDs antes:', p_left.id, p_right.id)
# Vincular
modal = {'portal_a': p_left, 'lado_a': 'izq', 'portal_b': p_right, 'lado_b': 'der', 'mapa_origen': map_a.nombre, 'mapa_dest': map_b.nombre}
ep._confirm_create_pair_spawns(modal)
print('IDs despues vinculo:', p_left.id, p_right.id)
print('spawn left->', p_left.spawn_destino_id, 'spawn right->', p_right.spawn_destino_id)
# Renombrar y propagar
p_left.id = 'portal_test_final'
if getattr(p_left, 'linked_portal', None):
    p_left.linked_portal.id = 'portal_test_final'
print('IDs despues rename:', p_left.id, p_right.id)
# Guardar
ep.guardar()
# Leer los JSON escritos
ruta_a = Path('src/database/mapas')/map_a.categoria/(map_a.nombre + '.json')
ruta_b = Path('src/database/mapas')/map_b.categoria/(map_b.nombre + '.json')
print('\nJSON guardado mapa A:', ruta_a)
if ruta_a.exists():
    print(json.dumps(json.loads(ruta_a.read_text(encoding='utf-8')), indent=2, ensure_ascii=False))
else:
    print('No existe', ruta_a)
print('\nJSON guardado mapa B:', ruta_b)
if ruta_b.exists():
    print(json.dumps(json.loads(ruta_b.read_text(encoding='utf-8')), indent=2, ensure_ascii=False))
else:
    print('No existe', ruta_b)

print('\nEND-TO-END DONE')
