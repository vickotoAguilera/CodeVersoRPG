"""
Script para aplicar el parche de sprites de cofres a mapa.py
Este script modifica SOLO las líneas necesarias sin corromper el archivo
"""
import os

# Leer el archivo
with open('src/mapa.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la línea que contiene "cofre_info = self.cofres_db.get(id_cofre)"
# y reemplazarla con la versión que busca en cofres_mapa también
for i, line in enumerate(lines):
    if 'cofre_info = self.cofres_db.get(id_cofre)' in line:
        # Reemplazar esta línea
        indent = '                '
        lines[i] = f'{indent}# Buscar datos del cofre en la base de datos\n'
        lines.insert(i+1, f'{indent}# Primero buscar en cofres_mapa, luego en la raíz\n')
        lines.insert(i+2, f'{indent}cofre_info = self.cofres_db.get("cofres_mapa", {{}}).get(id_cofre) or self.cofres_db.get(id_cofre)\n')
        break

# Encontrar la línea que contiene "nuevo_cofre = Cofre(" y agregar los sprites
for i, line in enumerate(lines):
    if 'nuevo_cofre = Cofre(' in line and i > 0:
        # Insertar las líneas de sprites ANTES de crear el cofre
        indent = '                    '
        # Buscar la línea anterior que dice "if cofre_info:"
        for j in range(i-1, max(0, i-10), -1):
            if 'if cofre_info:' in lines[j]:
                # Insertar después de "if cofre_info:"
                lines.insert(j+1, f'{indent}# ¡NUEVO! Obtener sprites desde la base de datos\n')
                lines.insert(j+2, f'{indent}sprite_cerrado = cofre_info.get("sprite_cerrado")\n')
                lines.insert(j+3, f'{indent}sprite_abierto = cofre_info.get("sprite_abierto")\n')
                lines.insert(j+4, f'{indent}\n')
                break
        
        # Ahora encontrar la línea "escala=escala" y agregar los sprites después
        for j in range(i, min(len(lines), i+15)):
            if 'escala=escala' in lines[j]:
                # Agregar las líneas de sprites después de escala
                lines[j] = lines[j].rstrip() + ',\n'
                indent2 = '                        '
                lines.insert(j+1, f'{indent2}sprite_cerrado=sprite_cerrado,  # ¡NUEVO!\n')
                lines.insert(j+2, f'{indent2}sprite_abierto=sprite_abierto   # ¡NUEVO!\n')
                break
        break

# Escribir el archivo modificado
with open('src/mapa.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ Parche aplicado exitosamente a src/mapa.py")
print("  - Agregada búsqueda en cofres_mapa")
print("  - Agregados parámetros sprite_cerrado y sprite_abierto")
