#!/usr/bin/env python3
"""
Script para limpiar duplicados en main.py
"""

# Leer el archivo
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Eliminar líneas duplicadas consecutivas
cleaned_lines = []
prev_line = None
for line in lines:
    # Si la línea es diferente a la anterior, agregarla
    if line != prev_line or not line.strip().startswith(('from src.pantalla_cofre', 'mi_pantalla_cofre', 'cofre_cercano_actual')):
        cleaned_lines.append(line)
    prev_line = line

# Escribir el archivo limpio
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print(f"[OK] Limpieza completada")
print(f"  Líneas originales: {len(lines)}")
print(f"  Líneas después: {len(cleaned_lines)}")
print(f"  Duplicados eliminados: {len(lines) - len(cleaned_lines)}")
