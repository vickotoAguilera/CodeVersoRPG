import editor_portales

print('TEST SUITE: VINCULACION VARIOS CASOS')
ep = editor_portales.EditorPortales()
left = editor_portales.MapaInfo('mapa_pueblo','file','assets/maps/whatever.png','ciudades')
right = editor_portales.MapaInfo('mapa_herrero','file','assets/maps/whatever2.png','ciudades')
ep.mapa_izq = left
ep.mapa_der = right

# Caso A: portales ya tienen id
pA1 = editor_portales.PortalRect('portal_pueblo', 10, 10, 20, 20)
pA2 = editor_portales.PortalRect('portal_herrero', 50, 60, 20, 20)
ep.izq_portales.append(pA1)
ep.der_portales.append(pA2)
print('\nCaso A: IDs preexistentes')
print('antes:', pA1.id, pA2.id, 'spawns:', pA1.spawn_destino_id, pA2.spawn_destino_id)
ep._confirm_create_pair_spawns({'portal_a':pA1,'lado_a':'izq','portal_b':pA2,'lado_b':'der','mapa_origen':left.nombre,'mapa_dest':right.nombre})
print('despues:', pA1.id, pA2.id, 'spawns:', pA1.spawn_destino_id, pA2.spawn_destino_id)

# Caso B: múltiples pares
pB1 = editor_portales.PortalRect('', 120, 10, 18, 18)
pB2 = editor_portales.PortalRect('', 160, 60, 18, 18)
pB3 = editor_portales.PortalRect('', 220, 80, 18, 18)
pB4 = editor_portales.PortalRect('', 260, 110, 18, 18)
ep.izq_portales.append(pB1); ep.der_portales.append(pB2); ep.izq_portales.append(pB3); ep.der_portales.append(pB4)
print('\nCaso B: crear dos vinculos independientes')
print('Antes IDs:', [p.id for p in (pB1,pB2,pB3,pB4)])
# vincular pB1 <-> pB2
ep._confirm_create_pair_spawns({'portal_a':pB1,'lado_a':'izq','portal_b':pB2,'lado_b':'der','mapa_origen':left.nombre,'mapa_dest':right.nombre})
# vincular pB3 <-> pB4
ep._confirm_create_pair_spawns({'portal_a':pB3,'lado_a':'izq','portal_b':pB4,'lado_b':'der','mapa_origen':left.nombre,'mapa_dest':right.nombre})
print('Despues IDs:', [p.id for p in (pB1,pB2,pB3,pB4)])
print('Spawns izq:', [(s.id,s.x,s.y) for s in ep.izq_spawns])
print('Spawns der:', [(s.id,s.x,s.y) for s in ep.der_spawns])

# Caso C: intentar vincular cuando origen ya tiene spawn
pC1 = editor_portales.PortalRect('', 300,300,20,20)
pC2 = editor_portales.PortalRect('', 400,400,22,22)
ep.izq_portales.append(pC1); ep.der_portales.append(pC2)
# Forzar spawn existente en pC1
pC1.spawn_destino_id = 'S_dummy_1'
print('\nCaso C: origen ya tiene spawn (debería abortar con mensaje)')
print('pC1.spawn antes:', pC1.spawn_destino_id)
# Try linking
ep._confirm_create_pair_spawns({'portal_a':pC1,'lado_a':'izq','portal_b':pC2,'lado_b':'der','mapa_origen':left.nombre,'mapa_dest':right.nombre})
print('pC1.spawn despues:', pC1.spawn_destino_id, 'pC2.spawn:', pC2.spawn_destino_id)

# Caso D: renombrar y propagar
pD1 = editor_portales.PortalRect('', 10,200,15,15)
pD2 = editor_portales.PortalRect('', 50,220,15,15)
ep.izq_portales.append(pD1); ep.der_portales.append(pD2)
ep._confirm_create_pair_spawns({'portal_a':pD1,'lado_a':'izq','portal_b':pD2,'lado_b':'der','mapa_origen':left.nombre,'mapa_dest':right.nombre})
print('\nCaso D: renombrar portal y verificar propagacion')
print('Antes:', pD1.id, pD2.id)
# Simular editar nombre y ENTER behavior
new_name = 'portal_prueba_rename'
pD1.id = new_name
if getattr(pD1,'linked_portal',None):
    pD1.linked_portal.id = new_name
print('Despues:', pD1.id, pD2.id)

print('\nResumen final:')
print('Total spawns izq:', len(ep.izq_spawns), 'der:', len(ep.der_spawns))
print('contador_spawns:', ep.contador_spawns)
print('FIN SUITE')
