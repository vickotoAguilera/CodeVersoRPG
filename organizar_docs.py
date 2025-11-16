import os
import shutil

# Directorio base
BASE_DIR = r"c:\Users\vicko\Documents\RPG"
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Crear carpeta docs si no existe
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)
    print(f"Carpeta creada: {DOCS_DIR}")

# Archivos a NO mover (mantener en raíz)
ARCHIVOS_EXCLUIDOS = ["README.md", "requirements.txt"]

# Contador de archivos movidos
movidos = 0

# Mover archivos .md
print("\n📄 Moviendo archivos .md...")
for archivo in os.listdir(BASE_DIR):
    if archivo.endswith(".md") and archivo not in ARCHIVOS_EXCLUIDOS:
        origen = os.path.join(BASE_DIR, archivo)
        destino = os.path.join(DOCS_DIR, archivo)
        
        if os.path.isfile(origen):
            shutil.move(origen, destino)
            print(f"  ✅ {archivo}")
            movidos += 1

# Mover archivos .txt
print("\n📝 Moviendo archivos .txt...")
for archivo in os.listdir(BASE_DIR):
    if archivo.endswith(".txt") and archivo not in ARCHIVOS_EXCLUIDOS:
        origen = os.path.join(BASE_DIR, archivo)
        destino = os.path.join(DOCS_DIR, archivo)
        
        if os.path.isfile(origen):
            shutil.move(origen, destino)
            print(f"  ✅ {archivo}")
            movidos += 1

print(f"\n✨ Total de archivos movidos: {movidos}")
print(f"📁 Carpeta de documentación: {DOCS_DIR}")
print("\n✅ ¡Organización completada!")
