#!/usr/bin/env python3
"""
Script Quirúrgico - Implementar lógica de auto-incremento con relleno de huecos
"""

CAMBIOS = [
    {
        "archivo": "editor_unificado.py",
        "descripcion": "Implementar lógica de auto-incremento que rellena huecos en IDs de cofres",
        "linea_inicio": 1165,
        "linea_fin": 1184,
        "nuevo_contenido": """    def _generar_id(self, tipo):
        \"\"\"
        Genera un ID único para el tipo de elemento.
        
        LÓGICA DE AUTO-INCREMENTO CON RELLENO DE HUECOS:
        - Si hay huecos en la secuencia (ej: C1, C2, C4), usa el primer hueco (C3)
        - Si no hay huecos, incrementa al siguiente número (ej: C1, C2, C3 -> C4)
        
        Ejemplo:
        - IDs existentes: [C1, C3, C5] -> Nuevo ID: C2 (rellena hueco)
        - IDs existentes: [C1, C2, C3] -> Nuevo ID: C4 (incrementa)
        \"\"\"
        prefijos = {
            'muro': 'M',
            'portal': 'P',
            'spawn': 'S',
            'cofre': 'C',
            'npc': 'N'
        }
        
        prefijo = prefijos.get(tipo, 'X')
        
        # Obtener todos los números de IDs existentes del mismo tipo
        ids_existentes = [int(e.id[1:]) for e in self.elementos 
                         if e.tipo == tipo and e.id[1:].isdigit()]
        
        if not ids_existentes:
            # No hay elementos de este tipo, empezar en 1
            nuevo_num = 1
        else:
            # Ordenar los IDs existentes
            ids_existentes.sort()
            
            # Buscar el primer hueco en la secuencia
            nuevo_num = None
            for i in range(1, max(ids_existentes) + 1):
                if i not in ids_existentes:
                    nuevo_num = i
                    break
            
            # Si no hay huecos, incrementar al siguiente
            if nuevo_num is None:
                nuevo_num = max(ids_existentes) + 1
        
        return f"{prefijo}{nuevo_num}"
"""
    }
]

# ============================================
# MOTOR DEL SCRIPT (igual que antes)
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
    print(f"Descripcion: {descripcion}")
    print(f"Lineas: {linea_inicio} - {linea_fin}")
    print(f"{'='*60}")
    
    try:
        # Leer archivo completo
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        total_lineas = len(lineas)
        print(f"[INFO] Archivo tiene {total_lineas} lineas")
        
        # Validar rango
        if linea_inicio < 1 or linea_fin > total_lineas:
            print(f"[ERROR] Rango invalido: {linea_inicio}-{linea_fin} (archivo tiene {total_lineas} lineas)")
            return False
        
        # Mostrar líneas que se van a reemplazar
        print(f"\n[ANTES] Lineas {linea_inicio}-{linea_fin}:")
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
        print(f"[INFO] Archivo ahora tiene {len(nuevas_lineas)} lineas")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los cambios definidos"""
    print("\n" + "="*60)
    print("SCRIPT QUIRURGICO - Aplicando cambios")
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
