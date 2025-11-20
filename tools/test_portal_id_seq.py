import sys
sys.path.insert(0, r'c:/Users/vicko/Documents/RPG')
import editor_portales

print('TEST SEQUENCE: generar múltiples portal IDs en mismo mapa')
ep = editor_portales.EditorPortales()
mi_mapa = editor_portales.MapaInfo('pueblo','file','assets/maps/whatever.png','ciudades')
ep.mapa_izq = mi_mapa

for i in range(1,8):
    new_id = ep._generar_portal_id(mi_mapa.nombre)
    ep.izq_portales.append(editor_portales.PortalRect(new_id, 10*i, 10*i, 20,20))
    print(f'creado {i}: {new_id}')

print('\nIDs en izq_portales:')
print([p.id for p in ep.izq_portales])
