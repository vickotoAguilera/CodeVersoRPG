"""
Script quirurgico para arreglar la creacion de cofres en mapa.py

PROBLEMA:
- El constructor Cofre() espera parametros ancho= y alto=
- El codigo actual solo pasa escala=
- Faltan las variables ancho_deseado y alto_deseado

SOLUCION:
1. Agregar calculo de ancho_deseado y alto_deseado desde el JSON
2. Cambiar escala=escala por ancho= y alto= en la llamada a Cofre()
"""

def arreglar_creacion_cofres():
    ruta_mapa = r"c:\Users\vicko\Documents\RPG\src\mapa.py"
    
    print("=" * 70)
    print("ARREGLANDO CREACION DE COFRES EN MAPA.PY")
    print("=" * 70)
    
    # Leer el archivo
    with open(ruta_mapa, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # CAMBIO 1: Reemplazar la linea de escala por el calculo completo
    viejo_codigo_escala = """                escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5"""
    
    nuevo_codigo_escala = """                # Obtener tamano deseado del JSON (si existe)
                ancho_deseado = cofre_data.get("ancho") or cofre_data.get("w")
                alto_deseado = cofre_data.get("alto") or cofre_data.get("h")
                
                # Calcular escala basada en el tamano deseado
                # Si no hay tamano especificado, usar escala por defecto
                if ancho_deseado and alto_deseado:
                    # Asumir que el sprite original es ~64x64 (tamano tipico)
                    # La escala sera el promedio de ancho/64 y alto/64
                    escala = (ancho_deseado / 64.0 + alto_deseado / 64.0) / 2.0
                else:
                    escala = cofre_data.get("escala", 0.5)  # Escala por defecto 0.5"""
    
    if viejo_codigo_escala in contenido:
        contenido = contenido.replace(viejo_codigo_escala, nuevo_codigo_escala)
        print("[OK] Paso 1: Agregado calculo de ancho_deseado y alto_deseado")
    else:
        print("[ADVERTENCIA] No se encontro la linea de escala para reemplazar")
    
    # CAMBIO 2: Reemplazar escala=escala por ancho= y alto=
    viejo_codigo_constructor = """                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        escala=escala,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )"""
    
    nuevo_codigo_constructor = """                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        ancho=ancho_deseado if ancho_deseado else 64,
                        alto=alto_deseado if alto_deseado else 64,
                        sprite_cerrado=cofre_info.get("sprite_cerrado"),
                        sprite_abierto=cofre_info.get("sprite_abierto")
                    )"""
    
    if viejo_codigo_constructor in contenido:
        contenido = contenido.replace(viejo_codigo_constructor, nuevo_codigo_constructor)
        print("[OK] Paso 2: Cambiado escala=escala por ancho= y alto=")
    else:
        print("[ADVERTENCIA] No se encontro el constructor de Cofre para reemplazar")
    
    # Guardar el archivo modificado
    with open(ruta_mapa, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Archivo guardado exitosamente")
    print("=" * 70)

if __name__ == "__main__":
    arreglar_creacion_cofres()
    print("\nListo! Ahora puedes ejecutar main.py")
