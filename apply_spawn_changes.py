"""
Script mejorado para aplicar los cambios del sistema de enlazado de spawns
"""

# Leer el archivo original
with open('editor_portales.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Aplicar cambios usando replace (más seguro)
# Cambio 1: Actualizar clase Spawn
content = content.replace(
    '    tam: int = 12\n\n    def to_dict(self):',
    '    tam: int = 12\n    linked_portal_id: str = \'\'\n\n    def to_dict(self):'
)

# Cambio 2: Actualizar to_dict
content = content.replace(
    'return {"id": self.id, "x": int(self.x), "y": int(self.y), "direccion": self.direccion, "tam": int(self.tam)}',
    'return {"id": self.id, "x": int(self.x), "y": int(self.y), "direccion": self.direccion, "tam": int(self.tam), "linked_portal_id": self.linked_portal_id}'
)

# Cambio 3: Actualizar carga de spawns
content = content.replace(
    '''                spawns.append(Spawn(
                    s.get('id', ''),
                    s['x'], s['y'],
                    s.get('direccion', 'abajo'),
                    s.get('tam', 12)
                ))''',
    '''                spawns.append(Spawn(
                    s.get('id', ''),
                    s['x'], s['y'],
                    s.get('direccion', 'abajo'),
                    s.get('tam', 12),
                    s.get('linked_portal_id', '')
                ))'''
)

# Cambio 4 y 5: Actualizar creación de spawns en pair
content = content.replace(
    '        spawn_a = Spawn(id=spawn_a_id, x=cx_a, y=cy_a)',
    '        spawn_a = Spawn(id=spawn_a_id, x=cx_a, y=cy_a, linked_portal_id=a.id)'
)
content = content.replace(
    '        spawn_b = Spawn(id=spawn_b_id, x=cx_b, y=cy_b)',
    '        spawn_b = Spawn(id=spawn_b_id, x=cx_b, y=cy_b, linked_portal_id=b.id)'
)

# Cambio 6: Actualizar creación de nuevo_spawn
content = content.replace(
    '        nuevo_spawn = Spawn(id=nuevo_id, x=x, y=y)',
    '        nuevo_spawn = Spawn(id=nuevo_id, x=x, y=y, linked_portal_id=portal.id)'
)

# Cambio 7: Actualizar _confirm_unlink_spawn
old_unlink = '''    def _confirm_unlink_spawn(self, modal):
        portal = modal.get('portal')
        lado = modal.get('lado')
        spawn_id = modal.get('spawn_id')
        # Limpiar referencia en el portal
        portal.spawn_destino_id = ''
        # Intentar eliminar spawn si es huérfano en ese mapa
        spawns = self.izq_spawns if lado=='izq' else self.der_spawns'''

new_unlink = '''    def _confirm_unlink_spawn(self, modal):
        portal = modal.get('portal')
        lado = modal.get('lado')
        spawn_id = modal.get('spawn_id')
        # Limpiar referencia en el portal
        portal.spawn_destino_id = ''
        
        # Buscar el spawn y limpiar su linked_portal_id
        spawns = self.izq_spawns if lado=='izq' else self.der_spawns
        for s in spawns:
            if s.id == spawn_id:
                s.linked_portal_id = ''
                break
        
        # Intentar eliminar spawn si es huérfano en ese mapa'''

content = content.replace(old_unlink, new_unlink)

# Escribir el archivo modificado
with open('editor_portales.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Cambios aplicados exitosamente")
