#!/bin/bash
echo "========================================"
echo "   VERIFICAR CONFIGURACION DE GIT"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Verificando Git..."
git --version

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Git no está instalado"
    echo ""
    echo "Instala Git con:"
    echo "  sudo apt install git"
    echo ""
    read -p "Presiona Enter para continuar..."
    exit 1
fi

echo ""
echo "Configuración de usuario:"
echo "  Nombre: $(git config user.name)"
echo "  Email: $(git config user.email)"

echo ""
echo "Repositorio remoto:"
git remote -v

echo ""
echo "Rama actual:"
git branch --show-current

echo ""
echo "Estado:"
git status --short

echo ""
echo "========================================"
echo "   VERIFICACION COMPLETADA"
echo "========================================"
echo ""
read -p "Presiona Enter para continuar..."
