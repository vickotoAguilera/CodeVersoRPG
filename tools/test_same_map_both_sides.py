import editor_portales

print('TEST: mis-detection when both viewports have same map name')
ep = editor_portales.EditorPortales()
map_same = editor_portales.MapaInfo('mapa_igual','file','assets/maps/whatever.png','ciudades')
# load same info into both sides
ep.mapa_izq = map_same
ep.mapa_der = map_same
p1 = editor_portales.PortalRect('',10,10,20,20)
p2 = editor_portales.PortalRect('',50,50,20,20)
ep.izq_portales.append(p1)
ep.der_portales.append(p2)
# try linking
modal = {'portal_a':p1,'lado_a':'izq','portal_b':p2,'lado_b':'der','mapa_origen':map_same.nombre,'mapa_dest':map_same.nombre}
print('map names:', ep.mapa_izq.nombre, ep.mapa_der.nombre)
ep._confirm_create_pair_spawns(modal)
print('After:', p1.id, p2.id, p1.spawn_destino_id, p2.spawn_destino_id)
print('linked?', p1.linked_portal is p2, p2.linked_portal is p1)
print('izq_spawns', ep.izq_spawns)
print('der_spawns', ep.der_spawns)
