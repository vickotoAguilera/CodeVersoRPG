import py_compile
import os
import sys

errors = []
files_to_check = []

# Buscar todos los archivos .py en la raíz y src
for root, dirs, files in os.walk('.'):
    # Omitir carpetas de respaldo o temporales si es necesario
    if '_backup' in root or '.git' in root or '__pycache__' in root:
        continue
        
    for f in files:
        if f.endswith('.py'):
            files_to_check.append(os.path.join(root, f))

print(f"Verificando sintaxis de {len(files_to_check)} archivos Python...")
print("=" * 60)

for file_path in files_to_check:
    try:
        # Usar doraise=True para que lance excepción si hay error
        py_compile.compile(file_path, doraise=True)
        # print(f"✓ {file_path}")
    except py_compile.PyCompileError as e:
        print(f"✗ {file_path}")
        errors.append((file_path, str(e)))

print("=" * 60)

if errors:
    print(f"\n[X] Se encontraron {len(errors)} errores de sintaxis:\n")
    for file_path, error in errors:
        print(f"Archivo: {file_path}")
        # Limpiar un poco el mensaje de error para que sea más legible
        msg = str(error).split('\n')[-2] if '\n' in str(error) else str(error)
        print(f"Error: {msg}\n")
    sys.exit(1)
else:
    print(f"\n[OK] Todos los {len(files_to_check)} archivos tienen sintaxis correcta!")
    sys.exit(0)
