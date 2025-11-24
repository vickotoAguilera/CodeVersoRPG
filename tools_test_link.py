import editor_portales

print('INICIANDO TEST DE VINCULACION')
ep = editor_portales.EditorPortales()
# Crear mapas ficticios (no cargamos imágenes)
left = editor_portales.MapaInfo('mapa_pueblo','file','assets/maps/whatever.png','ciudades')
right = editor_portales.MapaInfo('mapa_herrero','file','assets/maps/whatever2.png','ciudades')
ep.mapa_izq = left
ep.mapa_der = right
# Añadir portales sin id para forzar generación
p1 = editor_portales.PortalRect('', 10, 10, 20, 30)
p2 = editor_portales.PortalRect('', 50, 50, 20, 30)
ep.izq_portales.append(p1)
ep.der_portales.append(p2)
print('before:', 'p1.id=', p1.id, 'p2.id=', p2.id, 'p1.spawn=', p1.spawn_destino_id, 'p2.spawn=', p2.spawn_destino_id)
modal = {'portal_a': p1, 'lado_a': 'izq', 'portal_b': p2, 'lado_b': 'der', 'mapa_origen': left.nombre, 'mapa_dest': right.nombre}
# Llamar a la función que crea los spawns y enlaces
ep._confirm_create_pair_spawns(modal)
print('after:', 'p1.id=', p1.id, 'p2.id=', p2.id, 'p1.spawn=', p1.spawn_destino_id, 'p2.spawn=', p2.spawn_destino_id)
print('linked_refs:', p1.linked_portal is p2, p2.linked_portal is p1)
print('izq_spawns:', [(s.id,s.x,s.y) for s in ep.izq_spawns])
print('der_spawns:', [(s.id,s.x,s.y) for s in ep.der_spawns])
print('contador_spawns:', ep.contador_spawns)
print('FIN TEST')
