"""
Script quirúrgico para modificar src/mapa.py
Agrega soporte para persistencia de cofres con recuperación temporal
"""

import re

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Modificar Mapa para Cofres")
    print("=" * 60)
    
    # Leer el archivo
    with open('src/mapa.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios_aplicados = 0
    
    # CAMBIO 1: Modificar constructor para aceptar estado_cofres y tiempo_juego
    print("\n[1/2] Modificando constructor __init__...")
    patron_constructor = r'def __init__\(self, archivo_mapa, categoria_mapa, ancho_pantalla, alto_pantalla\):'
    reemplazo_constructor = 'def __init__(self, archivo_mapa, categoria_mapa, ancho_pantalla, alto_pantalla, estado_cofres=None, tiempo_juego=0.0):'
    
    if 'estado_cofres=None, tiempo_juego=0.0' not in contenido:
        contenido = re.sub(patron_constructor, reemplazo_constructor, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Constructor modificado")
        else:
            print("   [ERROR] No se pudo modificar constructor")
    else:
        print("   [SKIP] Constructor ya modificado")
    
    contenido_original = contenido
    
    # CAMBIO 2: Agregar atributos de instancia después de self.categoria
    print("\n[2/2] Agregando atributos de instancia...")
    patron_categoria = r'(self\.categoria = categoria_mapa # ¡NUEVO! Guardamos la categoría)\s+'
    reemplazo_categoria = r'''\1
        
        # NUEVO: Sistema de persistencia de cofres con recuperación
        self.estado_cofres_guardado = estado_cofres if estado_cofres is not None else {}
        self.tiempo_juego_actual = tiempo_juego
        '''
    
    if 'self.estado_cofres_guardado' not in contenido:
        contenido = re.sub(patron_categoria, reemplazo_categoria, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Atributos agregados")
        else:
            print("   [ERROR] No se pudo agregar atributos")
    else:
        print("   [SKIP] Atributos ya existen")
    
    contenido_original = contenido
    
    # Guardar el archivo
    if cambios_aplicados > 0:
        with open('src/mapa.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n[OK] Archivo guardado con {cambios_aplicados} cambios aplicados")
    else:
        print("\n[INFO] No se aplicaron cambios nuevos")
    
    print("\n" + "=" * 60)
    print(f"RESUMEN: {cambios_aplicados}/2 cambios aplicados")
    print("=" * 60)

if __name__ == "__main__":
    try:
        aplicar_cambios()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
