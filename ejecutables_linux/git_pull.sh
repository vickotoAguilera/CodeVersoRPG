#!/bin/bash
echo "========================================"
echo "   DESCARGAR CAMBIOS DESDE GITHUB"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Descargando últimos cambios desde GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   DESCARGA EXITOSA!"
    echo "========================================"
    echo ""
    echo "Tu código está actualizado con GitHub"
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
