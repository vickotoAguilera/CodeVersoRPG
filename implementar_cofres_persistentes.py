"""
Script quirúrgico para implementar persistencia de cofres con recuperación temporal
Aplica cambios específicos a main.py de forma segura
"""

import re
import sys

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Persistencia de Cofres")
    print("=" * 60)
    
    # Leer el archivo
    with open('main.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios_aplicados = 0
    
    # CAMBIO 1: Agregar variables globales después de las variables de cofres
    print("\n[1/6] Agregando variables globales de estado de cofres...")
    patron_variables_cofre = r'(DURACION_MENSAJE_COFRE = 3000  # 3 segundos)'
    reemplazo_variables = r'''\1

# Sistema de persistencia de cofres con recuperación temporal
# Formato: {"mapa_nombre": {"id_cofre": {"abierto": bool, "vacio": bool, "tiempo_apertura": float}}}
cofres_estado_global = {}
TIEMPO_RECUPERACION_COFRE = 3600  # 1 hora en segundos (cambiar a 10 para testing rápido)'''
    
    if 'cofres_estado_global' not in contenido:
        contenido = re.sub(patron_variables_cofre, reemplazo_variables, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Variables globales agregadas")
        else:
            print("   [ERROR] No se pudo agregar variables globales")
    else:
        print("   [SKIP] Variables globales ya existen")
    
    contenido_original = contenido
    
    # CAMBIO 2: Modificar interacción con cofres para guardar timestamp
    print("\n[2/6] Modificando interacción con cofres...")
    patron_interaccion = r'(if cofre_cercano:\s+# Interactuar con el cofre\s+resultado = cofre_cercano\.interactuar\(grupo_heroes, ITEMS_DB\))\s+'
    reemplazo_interaccion = r'''\1
                        
                        # NUEVO: Si se abrió exitosamente, guardar estado CON TIMESTAMP
                        if resultado["exito"]:
                            if mi_mapa.nombre_archivo not in cofres_estado_global:
                                cofres_estado_global[mi_mapa.nombre_archivo] = {}
                            
                            cofres_estado_global[mi_mapa.nombre_archivo][cofre_cercano.id_cofre] = {
                                "abierto": cofre_cercano.abierto,
                                "vacio": cofre_cercano.vacio,
                                "tiempo_apertura": tiempo_juego_segundos
                            }
                            print(f"[Cofre] Estado guardado: {cofre_cercano.id_cofre} abierto en t={tiempo_juego_segundos:.1f}s")
                        
'''
    
    if 'tiempo_apertura": tiempo_juego_segundos' not in contenido:
        contenido = re.sub(patron_interaccion, reemplazo_interaccion, contenido, flags=re.DOTALL)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Interacción con cofres modificada")
        else:
            print("   [SKIP] No se pudo modificar interacción (puede que ya esté modificada)")
    else:
        print("   [SKIP] Interacción ya modificada")
    
    contenido_original = contenido
    
    # CAMBIO 3: Agregar cofres al guardado manual
    print("\n[3/6] Modificando guardado manual...")
    patron_guardado_manual = r'("juego": \{\s+"tiempo_juego_segundos": tiempo_juego_segundos\s+\})\s+(\})'
    reemplazo_guardado_manual = r'''\1,
                                "cofres": cofres_estado_global  # NUEVO: Estado de cofres
                            \2'''
    
    # Buscar la primera ocurrencia (guardado manual)
    if contenido.count('"tiempo_juego_segundos": tiempo_juego_segundos') >= 1:
        partes = contenido.split('"tiempo_juego_segundos": tiempo_juego_segundos', 1)
        if '"cofres": cofres_estado_global' not in partes[1].split('"tiempo_juego_segundos": tiempo_juego_segundos')[0]:
            contenido = re.sub(patron_guardado_manual, reemplazo_guardado_manual, contenido, count=1)
            if contenido != contenido_original:
                cambios_aplicados += 1
                print("   [OK] Guardado manual modificado")
            else:
                print("   [ERROR] No se pudo modificar guardado manual")
        else:
            print("   [SKIP] Guardado manual ya modificado")
    
    contenido_original = contenido
    
    # CAMBIO 4: Agregar cofres al autoguardado
    print("\n[4/6] Modificando autoguardado...")
    # Buscar la segunda ocurrencia (autoguardado)
    partes = contenido.split('"tiempo_juego_segundos": tiempo_juego_segundos')
    if len(partes) >= 3:
        if '"cofres": cofres_estado_global' not in partes[2]:
            # Reconstruir con el cambio en la segunda ocurrencia
            contenido = partes[0] + '"tiempo_juego_segundos": tiempo_juego_segundos' + partes[1] + '"tiempo_juego_segundos": tiempo_juego_segundos'
            # Aplicar el cambio a la parte restante
            partes[2] = re.sub(r'(\})\s+(\})', r''',
                    "cofres": cofres_estado_global  # NUEVO: Estado de cofres
                \1
                \2''', partes[2], count=1)
            contenido += partes[2]
            if contenido != contenido_original:
                cambios_aplicados += 1
                print("   [OK] Autoguardado modificado")
            else:
                print("   [ERROR] No se pudo modificar autoguardado")
        else:
            print("   [SKIP] Autoguardado ya modificado")
    
    contenido_original = contenido
    
    # CAMBIO 5: Restaurar estado de cofres al cargar
    print("\n[5/6] Modificando carga de partida...")
    patron_carga = r'(tiempo_ultimo_autoguardado = tiempo_actual_ticks)\s+(estado_juego = "mapa")'
    reemplazo_carga = r'''\1

                                # NUEVO: Restaurar estado de cofres
                                cofres_estado_global.clear()
                                cofres_estado_global.update(datos_cargados.get("cofres", {}))
                                print(f"[Cofres] Estado restaurado: {len(cofres_estado_global)} mapas con cofres abiertos")

                                \2'''
    
    if 'cofres_estado_global.clear()' not in contenido:
        contenido = re.sub(patron_carga, reemplazo_carga, contenido)
        if contenido != contenido_original:
            cambios_aplicados += 1
            print("   [OK] Carga de partida modificada")
        else:
            print("   [ERROR] No se pudo modificar carga de partida")
    else:
        print("   [SKIP] Carga de partida ya modificada")
    
    contenido_original = contenido
    
    # CAMBIO 6: Nota sobre modificaciones pendientes en mapa.py
    print("\n[6/6] Verificando cambios...")
    
    # Guardar el archivo
    if cambios_aplicados > 0:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n[OK] Archivo guardado con {cambios_aplicados} cambios aplicados")
    else:
        print("\n[INFO] No se aplicaron cambios nuevos")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print(f"  - Cambios aplicados: {cambios_aplicados}/5")
    print("\nPROXIMOS PASOS:")
    print("  1. Modificar src/mapa.py para aceptar estado_cofres y tiempo_juego")
    print("  2. Actualizar todas las creaciones de Mapa() en main.py")
    print("  3. Testing manual")
    print("=" * 60)

if __name__ == "__main__":
    try:
        aplicar_cambios()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
