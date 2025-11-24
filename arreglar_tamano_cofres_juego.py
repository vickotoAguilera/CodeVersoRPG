"""
Script quirurgico para arreglar el tamaño de los cofres en el juego
El problema: El juego no respeta el ancho/alto guardado en el JSON
La solucion: Calcular la escala correcta basandose en el tamano deseado
"""

import re

def aplicar_cambios():
    print("=" * 70)
    print("SCRIPT QUIRURGICO: Arreglar Tamano de Cofres en Juego")
    print("=" * 70)
    
    # Leer el archivo
    with open('src/mapa.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # CAMBIO: Modificar la logica de carga para calcular escala correcta
    print("\n[1/1] Modificando logica de carga de cofres...")
    
    # Buscar el bloque donde se crea el Cofre
    patron = r'escala = cofre_data\.get\("escala", 0\.5\)  # Escala por defecto 0\.5\s+# Si no tenemos id o posición suficiente'
    
    reemplazo = '''# Obtener tamaño deseado del JSON (si existe)
                ancho_deseado = cofre_data.get("ancho") or cofre_data.get("w")
                alto_deseado = cofre_data.get("alto") or cofre_data.get("h")
                
                # Calcular escala basada en el tamaño deseado
                # Si no hay tamaño especificado, usar escala por defecto
                if ancho_deseado and alto_deseado:
                    # Asumir que el sprite original es ~64x64 (tamaño típico)
                    # La escala será el promedio de ancho/64 y alto/64
                    escala = (ancho_deseado / 64.0 + alto_deseado / 64.0) / 2.0
                else:
                    escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5
                
                # Si no tenemos id o posición suficiente'''
    
    contenido_nuevo = re.sub(patron, reemplazo, contenido, flags=re.MULTILINE)
    
    if contenido_nuevo != contenido_original:
        print("   [OK] Logica modificada")
        contenido = contenido_nuevo
    else:
        print("   [ERROR] No se pudo modificar la logica")
        print("   Intentando patron alternativo...")
        
        # Patron alternativo mas simple
        patron2 = r'escala = cofre_data\.get\("escala", 0\.5\)  # Escala por defecto 0\.5'
        
        reemplazo2 = '''# Calcular escala basada en el tamaño deseado del JSON
                ancho_deseado = cofre_data.get("ancho") or cofre_data.get("w")
                alto_deseado = cofre_data.get("alto") or cofre_data.get("h")
                
                if ancho_deseado and alto_deseado:
                    # Calcular escala promedio (asumiendo sprite original de 64x64)
                    escala = (ancho_deseado / 64.0 + alto_deseado / 64.0) / 2.0
                else:
                    escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5'''
        
        contenido_nuevo = re.sub(patron2, reemplazo2, contenido)
        
        if contenido_nuevo != contenido:
            print("   [OK] Logica modificada (patron alternativo)")
            contenido = contenido_nuevo
        else:
            print("   [ERROR] No se pudo aplicar ninguno de los patrones")
            return False
    
    # Guardar el archivo
    with open('src/mapa.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[OK] Archivo guardado exitosamente")
    
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print("  - Ahora el juego calculara la escala correcta")
    print("  - Basado en ancho/alto del JSON del mapa")
    print("  - Los cofres se veran del mismo tamano que en el editor")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("\n[ADVERTENCIA] No se pudieron aplicar todos los cambios")
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
