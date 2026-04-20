# 📁 Organización del Proyecto

**Fecha:** 16 Noviembre 2025

---

## 📂 Estructura de Carpetas

```
RPG/
├── main.py                    # Punto de entrada del juego
├── README.md                  # Documentación principal
├── requirements.txt           # Dependencias de Python
├── settings.json              # Configuración del juego
├── organizar_docs.py          # Script de organización
├── organizar_docs.bat         # Acceso directo al script
│
├── src/                       # Código fuente del juego
│   ├── batalla.py
│   ├── heroe.py
│   ├── monstruo.py
│   ├── database/             # Bases de datos JSON
│   └── ...
│
├── docs/                      # 📚 DOCUMENTACIÓN (todos los .md y .txt)
│   ├── GUIA_COMPLETA_PROYECTO.md
│   ├── ESTADO_COMPLETO_PROYECTO.md
│   ├── SISTEMA_DOT_HOT_COMPLETO.md
│   ├── TAREAS_PENDIENTES_FINAL.md
│   └── ... (todos los demás .md y .txt)
│
├── assets/                    # Recursos gráficos
│   ├── sprites/
│   ├── backgrounds/
│   └── ui/
│
└── saves/                     # Partidas guardadas
    ├── save_slot_1.json
    ├── save_slot_2.json
    └── save_slot_3.json
```

---

## 🔄 Sistema de Organización Automática

### ¿Qué hace `organizar_docs.py`?

El script mueve automáticamente todos los archivos de documentación a la carpeta `docs/`:

**Archivos que MUEVE:**
- ✅ Todos los archivos `.md` (excepto README.md)
- ✅ Todos los archivos `.txt` (excepto requirements.txt)

**Archivos que MANTIENE en raíz:**
- ✅ `README.md` - Documentación principal visible en GitHub
- ✅ `requirements.txt` - Necesario para pip install
- ✅ `main.py` - Punto de entrada
- ✅ Scripts de utilidad (.py, .bat)

---

## 🚀 Cómo Usar

### Opción 1: Doble Clic (Más Fácil)
```
1. Hacer doble clic en: organizar_docs.bat
2. Ver la lista de archivos movidos
3. Presionar cualquier tecla para cerrar
```

### Opción 2: Terminal
```bash
# Desde la carpeta raíz del proyecto
python organizar_docs.py
```

### Opción 3: Desde cualquier lugar
```bash
python "c:\Users\vicko\Documents\RPG\organizar_docs.py"
```

---

## 📅 ¿Cuándo Ejecutarlo?

**Ejecuta el script cuando:**
- ✅ Acabas de crear nuevos archivos `.md` de documentación
- ✅ Has generado reportes o resúmenes en la raíz
- ✅ Notas que hay muchos archivos `.txt` o `.md` en la raíz
- ✅ Al inicio de cada sesión de desarrollo (mantenimiento)
- ✅ Antes de hacer un commit a Git

**NO es necesario ejecutarlo:**
- ❌ Después de modificar archivos existentes en `docs/`
- ❌ Si solo trabajas con código en `src/`
- ❌ Si solo modificas `README.md` o `requirements.txt`

---

## 📋 Reglas de Organización

### Archivos en RAÍZ (directorio principal)
Solo deben estar archivos esenciales para el proyecto:
```
✅ main.py
✅ README.md
✅ requirements.txt
✅ settings.json
✅ .gitignore
✅ Scripts de utilidad (organizar_docs.py, setup_structure.py, etc.)
```

### Archivos en DOCS/ (documentación)
Toda la documentación del proyecto:
```
✅ Guías (GUIA_*.md)
✅ Resúmenes (RESUMEN_*.md)
✅ Sistemas (SISTEMA_*.md)
✅ Estados (ESTADO_*.md)
✅ Tareas (TAREAS_*.md)
✅ Notas de sesión (INICIO_*.md, SESION_*.md)
✅ Documentos de texto (*.txt)
```

### Archivos en SRC/ (código)
Todo el código fuente del juego:
```
✅ Archivos .py del juego
✅ Carpeta database/ (JSON)
✅ Carpeta ui/ (interfaces)
```

### Archivos en ASSETS/ (recursos)
Recursos gráficos y multimedia:
```
✅ sprites/
✅ backgrounds/
✅ ui/
✅ sounds/ (futuro)
```

---

## 🎯 Ejemplo de Uso

### Escenario: Acabo de crear 3 nuevos documentos

```
RPG/
├── main.py
├── NUEVO_SISTEMA_BUFFS.md        ← Nuevo documento
├── RESUMEN_SESION_2025_11_17.md  ← Nuevo documento
├── NOTAS_IMPLEMENTACION.txt      ← Nuevo documento
└── docs/
    └── ... (otros documentos)
```

**Paso 1:** Ejecutar organización
```bash
python organizar_docs.py
```

**Resultado:**
```
📄 Moviendo archivos .md...
  ✅ NUEVO_SISTEMA_BUFFS.md
  ✅ RESUMEN_SESION_2025_11_17.md

📝 Moviendo archivos .txt...
  ✅ NOTAS_IMPLEMENTACION.txt

✨ Total de archivos movidos: 3
📁 Carpeta de documentación: c:\Users\vicko\Documents\RPG\docs
✅ ¡Organización completada!
```

**Estado Final:**
```
RPG/
├── main.py
└── docs/
    ├── NUEVO_SISTEMA_BUFFS.md
    ├── RESUMEN_SESION_2025_11_17.md
    ├── NOTAS_IMPLEMENTACION.txt
    └── ... (otros documentos)
```

---

## 💡 Buenas Prácticas

### Durante Desarrollo
1. **Trabaja libremente** - Crea documentos donde sea conveniente
2. **Al finalizar sesión** - Ejecuta `organizar_docs.bat`
3. **Antes de commit** - Verifica que la raíz esté limpia

### Nombres de Documentos
Usa nombres descriptivos en MAYÚSCULAS:
```
✅ SISTEMA_NUEVAS_FUNCIONALIDADES.md
✅ RESUMEN_SESION_2025_11_XX.md
✅ GUIA_IMPLEMENTACION_FEATURE.md
✅ ESTADO_ACTUAL_PROYECTO.md
✅ TAREAS_PENDIENTES.md
```

### Documentos Importantes
Mantén actualizados estos documentos clave (en `docs/`):
- `TAREAS_PENDIENTES_FINAL.md` - Lista de tareas actual
- `ESTADO_COMPLETO_PROYECTO.md` - Estado general del proyecto
- `RESUMEN_SESION_YYYY_MM_DD.md` - Resumen de cada sesión

---

## 🔧 Personalización

### Agregar Más Extensiones

Si quieres mover también archivos `.log` o `.bak`, edita `organizar_docs.py`:

```python
# Buscar esta línea:
if archivo.endswith(".md") and archivo not in ARCHIVOS_EXCLUIDOS:

# Cambiar a:
if archivo.endswith((".md", ".log", ".bak")) and archivo not in ARCHIVOS_EXCLUIDOS:
```

### Excluir Más Archivos

Para mantener más archivos en la raíz:

```python
# Buscar esta línea:
ARCHIVOS_EXCLUIDOS = ["README.md", "requirements.txt"]

# Agregar más:
ARCHIVOS_EXCLUIDOS = ["README.md", "requirements.txt", "MI_ARCHIVO_ESPECIAL.md"]
```

---

## 📊 Beneficios

### Antes (Desorganizado)
```
❌ 30+ archivos .md en la raíz
❌ Difícil encontrar documentos específicos
❌ Confusión entre código y documentación
❌ Repositorio se ve desordenado
```

### Después (Organizado)
```
✅ Solo archivos esenciales en raíz (5-6 archivos)
✅ Toda la documentación en docs/
✅ Fácil navegación
✅ Proyecto profesional y limpio
✅ Git diffs más claros
```

---

## 🤖 Automatización Futura (Opcional)

### Opción 1: Git Hook
Crear un pre-commit hook que ejecute automáticamente el script:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python organizar_docs.py
git add docs/
```

### Opción 2: Tarea Programada
Configurar Windows Task Scheduler para ejecutar semanalmente.

### Opción 3: Script de Inicio
Agregar al inicio del `main.py`:

```python
import subprocess
import os

if os.path.exists("organizar_docs.py"):
    subprocess.run(["python", "organizar_docs.py"])
```

---

## ❓ FAQ

**P: ¿Qué pasa si ejecuto el script dos veces?**
R: No hay problema. El script solo mueve archivos que están en la raíz. Los que ya están en `docs/` no se tocan.

**P: ¿Puedo recuperar un archivo que moví por error?**
R: Sí, simplemente muévelo manualmente de `docs/` a la raíz.

**P: ¿El script borra archivos?**
R: No, solo MUEVE archivos de un lugar a otro. No borra nada.

**P: ¿Funciona en Linux/Mac?**
R: Sí, el script Python funciona en todas las plataformas. Solo el `.bat` es específico de Windows.

**P: ¿Puedo agregar el script a Git?**
R: Sí, es recomendable incluir `organizar_docs.py` en el repositorio.

---

**Última actualización:** 16 Nov 2025 - 14:30 UTC
