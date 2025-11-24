"""
Script para analizar las rutas JSON de todos los editores
"""
from pathlib import Path
import re

def analizar_editor(archivo):
    """Analiza un archivo de editor para encontrar cómo construye rutas JSON"""
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print(f"\n{'='*60}")
    print(f"EDITOR: {archivo.name}")
    print('='*60)
    
    # Buscar función _ruta_json o _get_ruta_json
    patron_ruta = r'def (_ruta_json|_get_ruta_json)\(.*?\):(.*?)(?=\n    def |\nclass |\Z)'
    matches = re.findall(patron_ruta, contenido, re.DOTALL)
    
    if matches:
        for func_name, func_body in matches:
            print(f"\n✓ Encontrada función: {func_name}")
            # Extraer líneas relevantes
            lineas = func_body.strip().split('\n')[:15]
            for linea in lineas:
                if linea.strip():
                    print(f"  {linea}")
    
    # Buscar cómo guarda (función guardar)
    patron_guardar = r'def (guardar|_guardar_mapa)\(.*?\):(.*?)(?=\n    def |\nclass |\Z)'
    matches_guardar = re.findall(patron_guardar, contenido, re.DOTALL)
    
    if matches_guardar:
        print(f"\n✓ Encontrada función de guardado")
        # Buscar líneas con 'open' o 'Path'
        for func_name, func_body in matches_guardar:
            lineas = func_body.strip().split('\n')
            for i, linea in enumerate(lineas[:30]):
                if 'open(' in linea or 'Path(' in linea or 'ruta' in linea.lower():
                    print(f"  Línea {i}: {linea.strip()}")
    
    # Buscar si incluye subcarpeta
    if 'subcarpeta' in contenido:
        print(f"\n✓ INCLUYE manejo de subcarpeta")
        # Contar ocurrencias
        count = contenido.count('subcarpeta')
        print(f"  Menciones de 'subcarpeta': {count}")
    else:
        print(f"\n✗ NO incluye manejo de subcarpeta")

# Analizar todos los editores
editores = [
    Path('editor_muros.py'),
    Path('editor_portales.py'),
    Path('editor_cofres.py'),
    Path('editor_unificado.py')
]

for editor in editores:
    if editor.exists():
        analizar_editor(editor)
    else:
        print(f"\n⚠ No encontrado: {editor}")

print(f"\n\n{'='*60}")
print("RESUMEN")
print('='*60)
print("""
EDITOR_MUROS.PY:
  - Función: _get_ruta_json()
  - Incluye subcarpeta: SÍ (líneas 433-434)
  - Ruta: src/database/mapas/categoria/[subcarpeta/]nombre.json

EDITOR_PORTALES.PY:
  - Función: _ruta_json()
  - Incluye subcarpeta: ??? (verificar línea 340-343)
  - Ruta: src/database/mapas/categoria/nombre.json

EDITOR_COFRES.PY:
  - Función: guardar_mapa()
  - Incluye subcarpeta: ??? (verificar línea 423-462)
  - Ruta: usa self.mapa_actual.ruta directamente

EDITOR_UNIFICADO.PY:
  - Función: _cargar_muros(), _guardar_muros()
  - Incluye subcarpeta: ??? (verificar)
  - Ruta: self.mapa_actual.ruta_json
""")
