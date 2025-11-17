import py_compile
import os
import sys

errors = []
files_to_check = [
    "main.py",
    "src/batalla.py",
    "src/heroe.py",
    "src/mapa.py",
    "src/cofre.py",
    "src/pantalla_recompensa_cofre.py",
    "src/pantalla_habilidades.py",
    "src/pantalla_inventario.py",
    "src/pantalla_equipo.py",
    "src/pantalla_estado.py",
    "src/pantalla_titulo.py",
    "src/pantalla_slots.py",
    "src/menu_pausa.py"
]

print("Verificando sintaxis de archivos Python...")
print("=" * 50)

for file_path in files_to_check:
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✓ {file_path}")
    except py_compile.PyCompileError as e:
        print(f"✗ {file_path}")
        errors.append((file_path, str(e)))

print("=" * 50)

if errors:
    print(f"\n❌ Se encontraron {len(errors)} errores:\n")
    for file_path, error in errors:
        print(f"Archivo: {file_path}")
        print(f"Error: {error}\n")
    sys.exit(1)
else:
    print("\n✅ Todos los archivos tienen sintaxis correcta!")
    sys.exit(0)
