"""
Test rápido para verificar el editor con zoom
"""
import subprocess
import sys

print("=" * 60)
print("TEST EDITOR DE MAPAS CON ZOOM")
print("=" * 60)
print()
print("Instrucciones:")
print("1. El editor se abrirá")
print("2. Selecciona un mapa desde el panel izquierdo")
print("3. Usa la RUEDA DEL MOUSE para hacer ZOOM")
print("4. Selecciona 'Cofres' o 'Monstruos' en los botones")
print("5. Haz click en un sprite para añadirlo al mapa")
print("6. Arrastra el objeto para moverlo")
print("7. Arrastra las ESQUINAS (círculos rojos) para cambiar tamaño")
print()
print("CONTROLES:")
print("  - Rueda Mouse = Zoom in/out")
print("  - Click Medio/Derecho = Arrastrar cámara")
print("  - H = Mostrar/ocultar grid")
print("  - G = Guardar")
print("  - D = Duplicar objeto seleccionado")
print("  - DEL = Eliminar objeto seleccionado")
print("  - ESC = Salir")
print()
print("=" * 60)
print()

try:
    subprocess.run([sys.executable, "editor_mapa_avanzado.py"])
except KeyboardInterrupt:
    print("\n✓ Editor cerrado por el usuario")
except Exception as e:
    print(f"\n❌ Error: {e}")
