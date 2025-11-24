#!/bin/bash
echo "========================================"
echo "   PUSH RAPIDO A GITHUB"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

# Mensaje automático con fecha y hora
mensaje="update: Cambios del $(date '+%d-%m-%Y %H:%M')"

echo "Agregando archivos..."
git add .

echo "Creando commit..."
git commit -m "$mensaje"

echo "Subiendo a GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   SUBIDA EXITOSA!"
    echo "========================================"
    echo ""
    echo "Mensaje: $mensaje"
else
    echo ""
    echo "Hubo un problema al subir"
fi

echo ""
read -p "Presiona Enter para continuar..."
