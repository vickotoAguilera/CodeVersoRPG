#!/usr/bin/env python3
"""
Script Quirúrgico - Reemplaza líneas específicas sin tocar el resto del código
Uso: Define los cambios en la lista CAMBIOS y ejecuta
"""

# ============================================
# CONFIGURACIÓN DE CAMBIOS
# ============================================

CAMBIOS = [
    {
        "archivo": "src/mapa.py",
        "descripcion": "Arreglar mensaje final - usar ruta_cargada en lugar de nombre_json",
        "linea_inicio": 416,
        "linea_fin": 416,
        "nuevo_contenido": """        print(f"¡Datos del mapa cargados con éxito desde: {ruta_cargada}!")
"""
    }
]

# ============================================
# MOTOR DEL SCRIPT
# ============================================

def aplicar_cambio(cambio):
    """Aplica un cambio quirúrgico a un archivo"""
    archivo = cambio["archivo"]
    descripcion = cambio["descripcion"]
    linea_inicio = cambio["linea_inicio"]
    linea_fin = cambio["linea_fin"]
    nuevo_contenido = cambio["nuevo_contenido"]
    
    print(f"\n{'='*60}")
    print(f"Archivo: {archivo}")
    print(f"Descripción: {descripcion}")
    print(f"Líneas: {linea_inicio} - {linea_fin}")
    print(f"{'='*60}")
    
    try:
        # Leer archivo completo
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        total_lineas = len(lineas)
        print(f"[INFO] Archivo tiene {total_lineas} líneas")
        
        # Validar rango
        if linea_inicio < 1 or linea_fin > total_lineas:
            print(f"[ERROR] Rango inválido: {linea_inicio}-{linea_fin} (archivo tiene {total_lineas} líneas)")
            return False
        
        # Mostrar líneas que se van a reemplazar
        print(f"\n[ANTES] Líneas {linea_inicio}-{linea_fin}:")
        print("-" * 60)
        for i in range(linea_inicio - 1, min(linea_fin, total_lineas)):
            print(f"{i+1:4d}: {lineas[i]}", end='')
        print("-" * 60)
        
        # Preparar nuevo contenido (asegurar que termine con \n)
        if not nuevo_contenido.endswith('\n'):
            nuevo_contenido += '\n'
        
        # Construir nuevo archivo
        nuevas_lineas = (
            lineas[:linea_inicio - 1] +  # Líneas antes del cambio
            [nuevo_contenido] +           # Nuevo contenido
            lineas[linea_fin:]            # Líneas después del cambio
        )
        
        # Guardar archivo
        with open(archivo, 'w', encoding='utf-8') as f:
            f.writelines(nuevas_lineas)
        
        print(f"\n[OK] Cambio aplicado exitosamente")
        print(f"[INFO] Archivo ahora tiene {len(nuevas_lineas)} líneas")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los cambios definidos"""
    print("\n" + "="*60)
    print("SCRIPT QUIRÚRGICO - Aplicando cambios")
    print("="*60)
    
    exitosos = 0
    fallidos = 0
    
    for i, cambio in enumerate(CAMBIOS, 1):
        print(f"\n[{i}/{len(CAMBIOS)}] Procesando cambio...")
        if aplicar_cambio(cambio):
            exitosos += 1
        else:
            fallidos += 1
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Total de cambios: {len(CAMBIOS)}")
    print(f"Exitosos: {exitosos}")
    print(f"Fallidos: {fallidos}")
    print("="*60 + "\n")
    
    if fallidos == 0:
        print("[OK] Todos los cambios se aplicaron correctamente!")
    else:
        print(f"[ADVERTENCIA] {fallidos} cambio(s) fallaron")

if __name__ == "__main__":
    main()
