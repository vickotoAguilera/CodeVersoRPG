import py_compile
import os
import sys

errors = []
files_to_check = [
    "sprite_sheet_editor.py"
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
