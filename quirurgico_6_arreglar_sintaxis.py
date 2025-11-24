"""
Script Quirúrgico 6: Arreglar Errores de Sintaxis y Eliminar Emojis

OBJETIVO:
1. Arreglar error de sintaxis en línea 701 (barras invertidas)
2. Eliminar TODOS los emojis del archivo
3. Reemplazar con texto ASCII simple

CAMBIOS:
- Arreglar replace('\\', '/') -> replace('\\\\', '/')
- Reemplazar ✓ con [OK]
- Reemplazar ⚠️ con [ADVERTENCIA]
- Reemplazar ❌ con [ERROR]
"""

import re

def arreglar_sintaxis_y_emojis():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("ARREGLANDO SINTAXIS Y ELIMINANDO EMOJIS")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Arreglar error de sintaxis en línea 701
    contenido = contenido.replace(
        "\"ruta\": str(archivo).replace('\\', '/'),",
        "\"ruta\": str(archivo).replace('\\\\', '/'),"
    )
    print("[OK] Paso 1: Error de sintaxis arreglado")
    
    # PASO 2: Eliminar emojis
    emojis_a_reemplazar = {
        "✓": "[OK]",
        "⚠️": "[ADVERTENCIA]",
        "⚠": "[ADVERTENCIA]",
        "❌": "[ERROR]",
        "✅": "[OK]",
        "🎯": "[*]",
        "📋": "",
        "🔗": "",
        "🎨": "",
        "🎮": "",
        "💡": "",
        "⭐": "",
        "⏳": "",
        "▼": "v",
        "▶": ">",
        "⋮": ":",
    }
    
    for emoji, reemplazo in emojis_a_reemplazar.items():
        if emoji in contenido:
            contenido = contenido.replace(emoji, reemplazo)
            print(f"[OK] Reemplazado: {repr(emoji)} -> {repr(reemplazo)}")
    
    # PASO 3: Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Sintaxis arreglada y emojis eliminados")
    print("=" * 70)

if __name__ == "__main__":
    arreglar_sintaxis_y_emojis()
    print("\nAhora el editor deberia ejecutarse sin errores")
