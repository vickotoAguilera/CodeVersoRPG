#!/bin/bash
echo "========================================"
echo "   EDITOR UI UNIVERSAL - CodeVersoRPG"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Iniciando Editor UI Universal..."
echo ""

python3 editor_ui_universal.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error al ejecutar el editor"
    echo ""
fi

echo ""
read -p "Presiona Enter para continuar..."
