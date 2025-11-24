#!/bin/bash
echo "========================================"
echo "   SUBIR CAMBIOS A GITHUB"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

# Pedir mensaje de commit
read -p "Mensaje del commit: " mensaje

if [ -z "$mensaje" ]; then
    mensaje="update: Cambios del $(date '+%d-%m-%Y %H:%M')"
fi

echo ""
echo "Agregando archivos..."
git add .

echo "Creando commit..."
git commit -m "$mensaje"

if [ $? -ne 0 ]; then
    echo "No hay cambios para commitear"
fi

echo ""
echo "Subiendo a GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   SUBIDA EXITOSA!"
    echo "========================================"
    echo ""
    echo "Tus cambios están en GitHub"
    echo "Mensaje: $mensaje"
else
    echo ""
    echo "========================================"
    echo "   HUBO UN PROBLEMA"
    echo "========================================"
    echo ""
    echo "Revisa los mensajes de error arriba"
fi

echo ""
read -p "Presiona Enter para continuar..."
