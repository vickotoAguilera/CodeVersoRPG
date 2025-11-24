"""
Script quirúrgico para actualizar todas las llamadas a Mapa() en main.py
Agrega los parámetros estado_cofres y tiempo_juego
"""

import re

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Actualizar Llamadas a Mapa()")
    print("=" * 60)
    
    # Leer el archivo
    with open('main.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios_aplicados = 0
    
    # CAMBIO 1: Inicio de nueva partida (línea ~259)
    print("\n[1/3] Actualizando creación de mapa en nueva partida...")
    patron_nueva_partida = r'mi_mapa = Mapa\("mapa_pradera\.jpg", "mundo", ANCHO, ALTO\)'
    reemplazo_nueva_partida = 'mi_mapa = Mapa("mapa_pradera.jpg", "mundo", ANCHO, ALTO, cofres_estado_global, tiempo_juego_segundos)'
    
    if 'mi_mapa = Mapa("mapa_pradera.jpg", "mundo", ANCHO, ALTO, cofres_estado_global' not in contenido:
        contenido = re.sub(patron_nueva_partida, reemplazo_nueva_partida, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Nueva partida actualizada")
        else:
            print("   [ERROR] No se pudo actualizar nueva partida")
    else:
        print("   [SKIP] Nueva partida ya actualizada")
    
    contenido_original = contenido
    
    # CAMBIO 2: Carga de partida (línea ~344)
    print("\n[2/3] Actualizando creación de mapa en carga de partida...")
    # Este es más complejo porque está en múltiples líneas
    patron_carga = r'mi_mapa = Mapa\(\s+datos_cargados\["mapa"\]\["nombre_archivo"\],\s+datos_cargados\["mapa"\]\["categoria"\],\s+ANCHO, ALTO\s+\)'
    reemplazo_carga = '''mi_mapa = Mapa(
                                    datos_cargados["mapa"]["nombre_archivo"],
                                    datos_cargados["mapa"]["categoria"],
                                    ANCHO, ALTO,
                                    cofres_estado_global,
                                    tiempo_juego_segundos
                                )'''
    
    if 'datos_cargados["mapa"]["categoria"],\n                                    ANCHO, ALTO,\n                                    cofres_estado_global' not in contenido:
        contenido = re.sub(patron_carga, reemplazo_carga, contenido, flags=re.MULTILINE)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Carga de partida actualizada")
        else:
            print("   [ERROR] No se pudo actualizar carga de partida")
    else:
        print("   [SKIP] Carga de partida ya actualizada")
    
    contenido_original = contenido
    
    # CAMBIO 3: Cambio de mapa por portal (línea ~718)
    print("\n[3/3] Actualizando creación de mapa en cambio por portal...")
    patron_portal = r'mi_mapa = Mapa\(archivo_img, categoria_real, ANCHO, ALTO\)'
    reemplazo_portal = 'mi_mapa = Mapa(archivo_img, categoria_real, ANCHO, ALTO, cofres_estado_global, tiempo_juego_segundos)'
    
    if 'mi_mapa = Mapa(archivo_img, categoria_real, ANCHO, ALTO, cofres_estado_global' not in contenido:
        contenido = re.sub(patron_portal, reemplazo_portal, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Cambio por portal actualizado")
        else:
            print("   [ERROR] No se pudo actualizar cambio por portal")
    else:
        print("   [SKIP] Cambio por portal ya actualizado")
    
    # Guardar el archivo
    if cambios_aplicados > 0:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n[OK] Archivo guardado con {cambios_aplicados} cambios aplicados")
    else:
        print("\n[INFO] No se aplicaron cambios nuevos")
    
    print("\n" + "=" * 60)
    print(f"RESUMEN: {cambios_aplicados}/3 llamadas actualizadas")
    print("=" * 60)

if __name__ == "__main__":
    try:
        aplicar_cambios()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
