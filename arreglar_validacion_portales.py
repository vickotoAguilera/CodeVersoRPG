"""
Script quirúrgico para arreglar validación de portales en editor_unificado.py
Cambia la validación para que solo advierta en lugar de bloquear el guardado
"""

import re

def aplicar_cambios():
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Arreglar Validación de Portales")
    print("=" * 60)
    
    # Leer el archivo
    with open('editor_unificado.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios_aplicados = 0
    
    # CAMBIO 1: Modificar la validación de portales para que solo advierta
    print("\n[1/2] Modificando validación de portales...")
    patron_validacion = r'# Validación: verificar que ningún portal tenga \'mapa_destino\' vacío \(cadena vacía\)\s+for portal in portales:\s+md = portal\.datos\.get\(\'mapa_destino\'\) if isinstance\(portal\.datos, dict\) else None\s+if md is not None and isinstance\(md, str\) and md\.strip\(\) == \'\':\s+print\(f"\[!\] Portal inválido: \{portal\.datos\} -> mapa_destino vacío"\)\s+return False'
    
    reemplazo_validacion = '''# Validación: advertir sobre portales con 'mapa_destino' vacío pero NO bloquear guardado
            for portal in portales:
                md = portal.datos.get('mapa_destino') if isinstance(portal.datos, dict) else None
                if md is not None and isinstance(md, str) and md.strip() == '':
                    print(f"[!] ADVERTENCIA: Portal con mapa_destino vacío: {portal.id} - Se guardará de todas formas")
                    # Opcional: establecer a None en lugar de cadena vacía
                    portal.datos['mapa_destino'] = None'''
    
    contenido = re.sub(patron_validacion, reemplazo_validacion, contenido, flags=re.MULTILINE)
    if contenido != contenido_original:
        cambios_aplicados += 1
        print("   [OK] Validación modificada")
    else:
        print("   [ERROR] No se pudo modificar validación")
    
    contenido_original = contenido
    
    # CAMBIO 2: Eliminar el check de ok_portales en guardar_cambios
    print("\n[2/2] Eliminando check de validación en guardar_cambios...")
    patron_check = r'# Guardar portales \(con validación\)\s+ok_portales = self\._guardar_portales\(nombre, elementos_por_tipo\[\'portal\'\]\)\s+if not ok_portales:\s+print\(\'\[X\] Guardado cancelado por validación de portales\'\)\s+return'
    
    reemplazo_check = '''# Guardar portales
        self._guardar_portales(nombre, elementos_por_tipo['portal'])'''
    
    contenido = re.sub(patron_check, reemplazo_check, contenido, flags=re.MULTILINE)
    if contenido != contenido_original:
        cambios_aplicados += 1
        print("   [OK] Check eliminado")
    else:
        print("   [ERROR] No se pudo eliminar check")
    
    # Guardar el archivo
    if cambios_aplicados > 0:
        with open('editor_unificado.py', 'w', encoding='utf-8') as f:
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
