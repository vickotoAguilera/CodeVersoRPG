#!/bin/bash
echo "========================================"
echo "   PUSH COMPLETO A GITHUB"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

# Organizar documentación
echo "[1/5] Organizando documentación..."
python3 organizar_docs.py 2>/dev/null || echo "  (organizar_docs.py no encontrado, continuando...)"

# Mensaje automático
mensaje="update: Cambios del $(date '+%d-%m-%Y %H:%M')"

echo "[2/5] Agregando todos los archivos..."
git add .

echo "[3/5] Creando commit..."
git commit -m "$mensaje"
if [ $? -ne 0 ]; then
    echo "  No hay cambios para commitear"
fi

echo "[4/5] Descargando últimos cambios..."
git pull origin main --no-edit

echo "[5/5] Subiendo a GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   PUSH COMPLETO EXITOSO!"
    echo "========================================"
    echo ""
    echo "Mensaje: $mensaje"
    echo "Todos tus cambios están en GitHub!"
else
    echo ""
    echo "Hubo un problema al subir"
fi

echo ""
read -p "Presiona Enter para continuar..."
