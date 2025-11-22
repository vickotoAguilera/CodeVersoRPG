"""
Script quirúrgico para agregar lógica de recuperación de cofres en src/mapa.py
Aplica el estado guardado de cofres con verificación de tiempo de recuperación
"""

import re

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Lógica de Recuperación de Cofres")
    print("=" * 60)
    
    # Leer el archivo
    with open('src/mapa.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # CAMBIO: Agregar lógica de recuperación después de crear cada cofre
    print("\n[1/1] Agregando lógica de recuperación de cofres...")
    
    # Buscar el bloque donde se crean los cofres y agregar la lógica después
    patron_cofre_append = r'(self\.cofres\.append\(nuevo_cofre\))'
    
    # Código a insertar después de append
    codigo_recuperacion = r'''\1
                    
                    # NUEVO: Aplicar estado guardado si existe, verificando recuperación
                    if self.nombre_archivo in self.estado_cofres_guardado:
                        estado_cofre = self.estado_cofres_guardado[self.nombre_archivo].get(id_cofre)
                        if estado_cofre:
                            tiempo_apertura = estado_cofre.get("tiempo_apertura", 0.0)
                            tiempo_transcurrido = self.tiempo_juego_actual - tiempo_apertura
                            
                            # Importar constante de recuperación desde main
                            TIEMPO_RECUPERACION = 3600  # 1 hora (debe coincidir con main.py)
                            
                            if tiempo_transcurrido >= TIEMPO_RECUPERACION:
                                # Cofre recuperado: NO aplicar estado guardado
                                print(f"[Cofre] '{id_cofre}' RECUPERADO (pasaron {tiempo_transcurrido:.1f}s)")
                                # Eliminar del estado guardado
                                del self.estado_cofres_guardado[self.nombre_archivo][id_cofre]
                            else:
                                # Cofre aún no se recupera: aplicar estado guardado
                                nuevo_cofre.cargar_desde_guardado(estado_cofre)
                                nuevo_cofre.actualizar_sprite()
                                tiempo_restante = TIEMPO_RECUPERACION - tiempo_transcurrido
                                print(f"[Cofre] '{id_cofre}' cargado (recupera en {tiempo_restante:.1f}s)")'''
    
    if 'Cofre recuperado: NO aplicar estado guardado' not in contenido:
        contenido = re.sub(patron_cofre_append, codigo_recuperacion, contenido)
        if contenido != contenido_original:
            print("   [OK] Lógica de recuperación agregada")
        else:
            print("   [ERROR] No se pudo agregar lógica de recuperación")
            print("   Buscando patrón alternativo...")
            return False
    else:
        print("   [SKIP] Lógica de recuperación ya existe")
        return True
    
    # Guardar el archivo
    with open('src/mapa.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    print("\n[OK] Archivo guardado exitosamente")
    
    print("\n" + "=" * 60)
    print("RESUMEN: Lógica de recuperación implementada")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("\n[ADVERTENCIA] Algunos cambios no se aplicaron correctamente")
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
