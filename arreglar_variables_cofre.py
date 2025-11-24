"""
Script quirúrgico para arreglar el NameError en mapa.py
Problema: Variables 'ancho' y 'alto' no definidas en línea 424-425
Solución: Cambiar a 'ancho_deseado' y 'alto_deseado'
"""

import os

def arreglar_variables_cofre():
    ruta_mapa = r"c:\Users\vicko\Documents\RPG\src\mapa.py"
    
    print("=" * 60)
    print("ARREGLANDO VARIABLES DE COFRE EN MAPA.PY")
    print("=" * 60)
    
    # Leer el archivo
    with open(ruta_mapa, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    # Buscar y reemplazar las líneas problemáticas
    cambios_realizados = 0
    
    for i, linea in enumerate(lineas, start=1):
        # Línea 424: ancho=ancho,
        if i == 424 and "ancho=ancho," in linea:
            espacios = len(linea) - len(linea.lstrip())
            lineas[i-1] = " " * espacios + "ancho=ancho_deseado,\n"
            print(f"[OK] Linea {i}: ancho=ancho -> ancho=ancho_deseado")
            cambios_realizados += 1
        
        # Línea 425: alto=alto,
        elif i == 425 and "alto=alto," in linea:
            espacios = len(linea) - len(linea.lstrip())
            lineas[i-1] = " " * espacios + "alto=alto_deseado,\n"
            print(f"[OK] Linea {i}: alto=alto -> alto=alto_deseado")
            cambios_realizados += 1
    
    # Guardar el archivo modificado
    if cambios_realizados > 0:
        with open(ruta_mapa, 'w', encoding='utf-8') as f:
            f.writelines(lineas)
        print(f"\n[EXITO] Archivo guardado con {cambios_realizados} cambios")
    else:
        print("\n[ADVERTENCIA] No se encontraron las lineas a modificar")
    
    print("=" * 60)

if __name__ == "__main__":
    arreglar_variables_cofre()
    print("\n¡Listo! Ahora puedes ejecutar main.py")
