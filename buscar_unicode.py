import os
import re

# Caracteres Unicode problemáticos que queremos encontrar
unicode_chars = ['►', '◄', '↵', '⏎', '↹', '←', '→', '↓', '↑', 'TAB']

def buscar_unicode_en_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            for num_linea, linea in enumerate(lineas, 1):
                for char in unicode_chars:
                    if char in linea:
                        print(f"{ruta_archivo}:{num_linea} -> {linea.strip()}")
                        break
    except Exception as e:
        print(f"Error leyendo {ruta_archivo}: {e}")

def buscar_en_directorio(directorio):
    for root, dirs, files in os.walk(directorio):
        for file in files:
            if file.endswith('.py'):
                ruta_completa = os.path.join(root, file)
                buscar_unicode_en_archivo(ruta_completa)

if __name__ == "__main__":
    print("Buscando caracteres Unicode en archivos .py...")
    buscar_en_directorio('src')
    print("\nBúsqueda completada.")
