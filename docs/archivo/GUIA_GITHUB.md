# 🐙 Guía de GitHub para el Proyecto RPG

**Fecha:** 16 Noviembre 2025

---

## 🚀 Configuración Inicial

### Paso 1: Verificar Git

Abre una terminal y verifica que tienes Git instalado:

```bash
git --version
```

Si no lo tienes, descarga Git desde: https://git-scm.com/

### Paso 2: Configurar Git (primera vez)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_email@ejemplo.com"
```

### Paso 3: Inicializar Repositorio

Desde la carpeta del proyecto:

```bash
cd c:\Users\vicko\Documents\RPG
git init
```

### Paso 4: Agregar Archivos

```bash
# Agregar todos los archivos
git add .

# O agregar selectivamente
git add main.py
git add src/
git add docs/
git add assets/
git add README.md
git add requirements.txt
```

### Paso 5: Primer Commit

```bash
git commit -m "Initial commit: RPG game base structure"
```

---

## 🌐 Subir a GitHub

### Opción A: Crear Repositorio desde GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `code-verso-rpg` (o el que prefieras)
3. Descripción: "Un juego RPG 2D desarrollado en Python con Pygame"
4. **NO** marques "Initialize with README" (ya lo tenemos)
5. Click en "Create repository"

### Opción B: Desde la terminal

Después de crear el repo en GitHub:

```bash
# Agregar el remoto
git remote add origin https://github.com/TU_USUARIO/code-verso-rpg.git

# Subir código
git branch -M main
git push -u origin main
```

---

## 📝 Workflow Diario

### Al Empezar a Trabajar

```bash
# Actualizar tu copia local (si trabajas en varios lugares)
git pull origin main
```

### Durante el Desarrollo

```bash
# Ver cambios
git status

# Ver diferencias
git diff
```

### Al Terminar una Sesión

```bash
# 1. Organizar documentación
python organizar_docs.py

# 2. Ver qué cambió
git status

# 3. Agregar cambios
git add .

# 4. Hacer commit descriptivo
git commit -m "feat: Implementar sistema DOT/HOT completo"

# 5. Subir a GitHub
git push origin main
```

---

## 💬 Mensajes de Commit Recomendados

### Formato Estándar

```
tipo(scope): descripción corta

Descripción más detallada (opcional)
```

### Tipos de Commit

```bash
# Nueva funcionalidad
git commit -m "feat: Agregar sistema de buffs/debuffs"

# Corrección de bug
git commit -m "fix: Corregir items especiales invisibles"

# Documentación
git commit -m "docs: Actualizar guía de habilidades"

# Refactorización
git commit -m "refactor: Mejorar sistema de scroll"

# Mejora de rendimiento
git commit -m "perf: Optimizar carga de sprites"

# Testing
git commit -m "test: Agregar tests para sistema de batalla"

# Estilo/formato
git commit -m "style: Formatear código con black"

# Tareas de mantenimiento
git commit -m "chore: Actualizar dependencias"
```

### Ejemplos del Proyecto

```bash
git commit -m "feat: Implementar 7 habilidades DOT/HOT"
git commit -m "fix: Hacer visibles items especiales en inventario"
git commit -m "docs: Crear documentación completa de sistema DOT/HOT"
git commit -m "refactor: Organizar archivos MD en carpeta docs/"
git commit -m "feat: Agregar scroll visual a todas las pantallas"
```

---

## 🌿 Branches (Ramas)

### Trabajar con Ramas

```bash
# Crear rama para nueva feature
git checkout -b feature/sistema-buffs

# Trabajar normalmente...
git add .
git commit -m "feat: Implementar sistema de buffs básico"

# Volver a main
git checkout main

# Mergear cambios
git merge feature/sistema-buffs

# Subir todo
git push origin main
```

### Estrategia Recomendada

```
main (rama principal - siempre funcional)
├── feature/nuevas-habilidades
├── feature/sistema-buffs
├── fix/correccion-batalla
└── docs/actualizar-guias
```

---

## 📦 Qué Subir y Qué No

### ✅ SÍ Subir (tracked)

```
✅ Código fuente (src/*.py)
✅ Archivos principales (main.py, README.md)
✅ Documentación (docs/*.md)
✅ Bases de datos (src/database/*.json)
✅ Assets (sprites, backgrounds)
✅ Configuración de ejemplo (settings.json)
✅ Scripts de utilidad (organizar_docs.py, etc.)
✅ .gitignore
✅ requirements.txt
```

### ❌ NO Subir (ignored)

```
❌ Partidas guardadas personales (saves/*.json)
❌ Cache de Python (__pycache__/)
❌ Virtual environments (venv/, .venv/)
❌ Archivos de IDE (.vscode/, .idea/)
❌ Logs (*.log)
❌ Archivos temporales (*.tmp, *.bak)
❌ Configuración personal (settings_local.json)
```

**Nota:** El archivo `.gitignore` ya está configurado para esto.

---

## 🔄 Comandos Útiles

### Ver Historial

```bash
# Ver commits recientes
git log --oneline --graph --decorate -10

# Ver cambios en un archivo
git log -p src/batalla.py

# Ver quién cambió qué
git blame src/batalla.py
```

### Deshacer Cambios

```bash
# Descartar cambios no guardados en un archivo
git checkout -- archivo.py

# Descartar TODOS los cambios no guardados
git checkout -- .

# Deshacer el último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer el último commit (descartar cambios)
git reset --hard HEAD~1
```

### Revisar Diferencias

```bash
# Ver cambios no guardados
git diff

# Ver cambios en staging
git diff --staged

# Comparar con commit anterior
git diff HEAD~1
```

---

## 🏷️ Tags (Versiones)

### Crear Tags

```bash
# Tag simple
git tag v0.1.0

# Tag con mensaje
git tag -a v0.1.0 -m "Primera versión jugable"

# Ver tags
git tag

# Subir tags
git push origin v0.1.0

# Subir todos los tags
git push origin --tags
```

### Estrategia de Versionado

```
v0.1.0 - Sistema básico de batalla
v0.2.0 - Sistema de habilidades completo
v0.3.0 - Sistema DOT/HOT implementado
v0.4.0 - Sistema de inventario completo
v1.0.0 - Primera versión pública
```

---

## 🚨 Problemas Comunes

### Problema 1: Archivos Grandes

```bash
# Error: archivo muy grande para GitHub (>100MB)
# Solución: Usar Git LFS o excluir del repo

# Instalar Git LFS
git lfs install

# Trackear archivos grandes
git lfs track "*.psd"
git lfs track "assets/videos/*"
```

### Problema 2: Conflictos de Merge

```bash
# Cuando hay conflicto
git pull origin main  # Error: conflict

# Ver archivos en conflicto
git status

# Abrir archivo y resolver manualmente
# Buscar marcas: <<<<<<< HEAD, =======, >>>>>>>

# Después de resolver
git add archivo_resuelto.py
git commit -m "fix: Resolver conflicto en batalla.py"
```

### Problema 3: Olvidé Agregar .gitignore

```bash
# Si ya subiste archivos que no querías
git rm --cached archivo_no_deseado.py
git commit -m "chore: Remover archivo no deseado"
git push
```

---

## 📊 README.md del Repositorio

Tu README.md actual está bien, pero considera agregar:

```markdown
## 📸 Screenshots
![Batalla](docs/images/screenshot_batalla.png)
![Menú](docs/images/screenshot_menu.png)

## ⭐ Características
- Sistema de batalla por turnos
- 23+ habilidades con efectos DOT/HOT
- Sistema de inventario y equipo
- Guardado/Carga de partidas
- Interfaz estilo Blue Dragon

## 🎮 Estado del Proyecto
- ✅ Sistema de batalla: 100%
- ✅ Sistema de habilidades: 100%
- ✅ Inventario y equipo: 100%
- 🔄 Sistema de buffs: En desarrollo
- ⏳ NPCs y tiendas: Pendiente

## 🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor lee CONTRIBUTING.md

## 📄 Licencia
MIT License - ver LICENSE file
```

---

## 🔐 Seguridad

### NO subir contraseñas o secretos

```python
# ❌ MAL
API_KEY = "sk_live_123456789"

# ✅ BIEN
import os
API_KEY = os.environ.get('API_KEY')
```

### Usar variables de entorno

```bash
# Crear .env (agregar a .gitignore)
API_KEY=tu_clave_secreta
DATABASE_PASSWORD=password123

# En Python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🎯 Checklist Pre-Push

Antes de hacer `git push`:

- [ ] Código funciona correctamente
- [ ] Ejecutar `python organizar_docs.py`
- [ ] Revisar `git status`
- [ ] Revisar `git diff`
- [ ] Commit con mensaje descriptivo
- [ ] No hay contraseñas o secretos
- [ ] `.gitignore` actualizado
- [ ] Tests pasan (si existen)

---

## 📚 Recursos

### Documentación Oficial
- Git: https://git-scm.com/doc
- GitHub: https://docs.github.com

### Tutoriales
- Git básico: https://www.atlassian.com/git/tutorials
- GitHub Flow: https://guides.github.com/introduction/flow/

### Comandos Cheat Sheet
- https://education.github.com/git-cheat-sheet-education.pdf

---

## 🎓 Comandos Rápidos (Resumen)

```bash
# Setup inicial
git init
git add .
git commit -m "Initial commit"
git remote add origin URL
git push -u origin main

# Workflow diario
python organizar_docs.py
git status
git add .
git commit -m "feat: descripción"
git push

# Ver historial
git log --oneline
git diff

# Deshacer cambios
git checkout -- archivo.py
git reset --soft HEAD~1
```

---

**Última actualización:** 16 Nov 2025 - 14:35 UTC
