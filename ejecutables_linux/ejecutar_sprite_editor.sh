#!/bin/bash
echo "========================================"
echo "   SPRITE SHEET EDITOR - CodeVersoRPG"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Iniciando Sprite Sheet Editor..."
echo ""

python3 sprite_sheet_editor.py

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
