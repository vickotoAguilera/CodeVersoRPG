#!/bin/bash
echo "========================================"
echo "   PUSH TOTAL - SUBE TODO A GITHUB"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

# Organizar documentación
echo "[1/6] Organizando documentación..."
python3 organizar_docs.py 2>/dev/null || echo "  (organizar_docs.py no encontrado, continuando...)"

# Mensaje automático
mensaje="update: Cambios del $(date '+%d-%m-%Y %H:%M')"

echo "[2/6] Agregando todos los archivos..."
git add .

echo "[3/6] Creando commit..."
git commit -m "$mensaje"
if [ $? -ne 0 ]; then
    echo "  No hay cambios para commitear"
fi

echo "[4/6] Asegurando que estamos en main..."
git checkout main 2>/dev/null || echo "  Ya estamos en main"

echo "[5/6] Haciendo merge de todas las ramas..."
# Hacer merge de fix/auto-map-fixes si existe
git merge fix/auto-map-fixes -m "Merge: $mensaje" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  Rama fix/auto-map-fixes ya está mergeada o no existe"
fi

echo "[6/6] Subiendo TODO a GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   TODO SUBIDO CON EXITO!"
    echo "========================================"
    echo "Rama: main"
    echo "Mensaje: $mensaje"
    echo ""
    echo "Todos tus cambios están en GitHub!"
else
    echo ""
    echo "Hubo un problema al subir"
fi

echo ""
read -p "Presiona Enter para continuar..."
