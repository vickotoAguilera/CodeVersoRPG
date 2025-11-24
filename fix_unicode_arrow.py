"""
Script quirúrgico para reemplazar el carácter Unicode → (U+2192) por '->' en archivos Python.
Esto soluciona el UnicodeEncodeError en consolas Windows con codificación CP1252.
"""

import os
import sys

def fix_unicode_arrows(file_path):
    """
    Reemplaza el carácter → por -> en un archivo.
    
    Args:
        file_path: Ruta al archivo a procesar
        
    Returns:
        bool: True si se hicieron cambios, False si no
    """
    try:
        # Leer el archivo con codificación UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si contiene el carácter problemático
        if '→' not in contenido:
            return False
        
        # Contar ocurrencias
        ocurrencias = contenido.count('→')
        
        # Reemplazar → por ->
        contenido_nuevo = contenido.replace('→', '->')
        
        # Guardar el archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print(f"[OK] {file_path}: {ocurrencias} reemplazos")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error procesando {file_path}: {e}")
        return False

def main():
    """Procesa todos los archivos Python en el directorio src/"""
    
    # Directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    
    print("=" * 60)
    print("SCRIPT QUIRURGICO: Reemplazo de caracteres Unicode -> por ->")
    print("=" * 60)
    print(f"Directorio base: {base_dir}")
    print(f"Directorio src: {src_dir}")
    print()
    
    archivos_modificados = 0
    archivos_procesados = 0
    
    # Procesar archivos en src/
    if os.path.exists(src_dir):
        for archivo in os.listdir(src_dir):
            if archivo.endswith('.py'):
                ruta_completa = os.path.join(src_dir, archivo)
                archivos_procesados += 1
                
                if fix_unicode_arrows(ruta_completa):
                    archivos_modificados += 1
    
    # Procesar main.py en la raiz
    main_py = os.path.join(base_dir, 'main.py')
    if os.path.exists(main_py):
        archivos_procesados += 1
        if fix_unicode_arrows(main_py):
            archivos_modificados += 1
    
    print()
    print("=" * 60)
    print(f"RESUMEN:")
    print(f"  Archivos procesados: {archivos_procesados}")
    print(f"  Archivos modificados: {archivos_modificados}")
    print("=" * 60)
    
    if archivos_modificados > 0:
        print("\nListo! Ahora puedes ejecutar main.py sin errores de Unicode.")
    else:
        print("\nNo se encontraron caracteres para reemplazar.")

if __name__ == "__main__":
    main()
