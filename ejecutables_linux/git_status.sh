#!/bin/bash
echo "========================================"
echo "   ESTADO DEL REPOSITORIO GIT"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

echo "Estado actual:"
git status

echo ""
echo "Últimos 5 commits:"
git log --oneline -5

echo ""
echo "Ramas:"
git branch -a

echo ""
echo "========================================"
echo "   VERIFICACION COMPLETADA"
echo "========================================"
echo ""
read -p "Presiona Enter para continuar..."
