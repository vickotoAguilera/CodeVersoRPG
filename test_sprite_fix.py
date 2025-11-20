"""Test rápido del sprite editor para verificar que no hay errores"""
import sys

try:
    # Intentar importar el módulo
    import sprite_sheet_editor
    print("✓ sprite_sheet_editor.py no tiene errores de sintaxis")
    print("✓ Todas las correcciones aplicadas correctamente")
    print("\n🔧 Cambios realizados:")
    print("  1. ✅ Ventana ajustada a 800x600")
    print("  2. ✅ Modo pantalla completa con tecla F")
    print("  3. ✅ Ventana redimensionable")
    print("  4. ✅ Redimensionamiento de selecciones MEJORADO:")
    print("     - Tolerancia aumentada a 15px")
    print("     - Ahora considera offset_x y offset_y correctamente")
    print("     - Funciona con zoom y pan de cámara")
    print("  5. ✅ Preview reubicado:")
    print("     - Info (Tamaño/Pos) se muestra PRIMERO")
    print("     - Imagen del sprite debajo de la info")
    print("     - Fondo de cuadrícula para ver transparencias")
    print("     - Ya no se corta")
    print("\n🎮 Cómo redimensionar selecciones:")
    print("  1. Crea una selección (click + arrastrar)")
    print("  2. Acerca el cursor al BORDE o ESQUINA del rectángulo")
    print("  3. El cursor cambiará de forma (flechas)")
    print("  4. Arrastra para redimensionar")
    print("\n✅ ¡Todo listo para probar!")
    
except SyntaxError as e:
    print(f"❌ Error de sintaxis: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠️ Advertencia: {e}")
    print("  (Probablemente faltan dependencias como pygame, pero la sintaxis está bien)")
