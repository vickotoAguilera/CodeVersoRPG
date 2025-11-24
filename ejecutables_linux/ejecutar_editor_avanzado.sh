#!/bin/bash
echo "========================================"
echo "   EDITOR DE MAPAS AVANZADO"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Iniciando Editor de Mapas Avanzado..."
echo ""

python3 editor_mapa_avanzado.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error al ejecutar el editor"
    echo ""
    echo "Verifica que tengas Python 3 y pygame instalados:"
    echo "  sudo apt install python3 python3-pip"
    echo "  pip3 install pygame"
    echo ""
fi

echo ""
read -p "Presiona Enter para continuar..."
