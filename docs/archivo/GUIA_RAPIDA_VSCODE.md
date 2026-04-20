# Guía Rápida para Visual Studio Code

## ✅ Tu Juego FUNCIONA Ahora

Los errores ya están corregidos. Puedes jugar directamente:

### 🎮 Para Jugar:

1. Abre VS Code en la carpeta `RPG`
2. Presiona `F5` o haz clic en el botón ▶️ "Run"
3. O en la terminal de VS Code escribe:
   ```
   python main.py
   ```

¡Y listo! El juego funcionará.

---

## 📁 ¿Qué Son Estos Archivos?

### Archivos de Documentación (carpeta `docs/`)
- **LEEME_PRIMERO.txt** - Resumen general
- **INICIO_RAPIDO.md** - Guía rápida
- **README.md** - Manual del usuario
- **ARQUITECTURA.md** - Diseño técnico (para programadores)
- **DATABASE.md** - Cómo modificar datos del juego
- **REFACTORIZACION.md** - Plan de mejoras futuras
- **RESUMEN_CAMBIOS.md** - Qué se cambió
- **INDICE_PROYECTO.md** - Lista de todos los archivos

**¿Necesitas leerlos?** NO si solo quieres jugar. SÍ si quieres modificar el juego.

### Archivos de Configuración (raíz)
- **main.py** - ¡El juego! Ejecuta este
- **requirements.txt** - Lista de programas necesarios
- **settings.json** - Configuración del juego
- **.gitignore** - Para control de versiones (Git)

### Scripts (solo si quieres mejorar el código)
- **crear_estructura_completa.py** - Crea carpetas nuevas
- **setup_structure.py** - Igual, crea carpetas

---

## 🤔 ¿Qué Significan Esos Comandos?

### `python crear_estructura_completa.py`
**¿Qué hace?** Crea carpetas vacías para código futuro.

**¿Necesitas ejecutarlo?** NO si solo quieres jugar. SÍ si vas a programar mejoras.

### `pip install -r requirements.txt`
**¿Qué hace?** Instala pygame (el motor del juego).

**¿Necesitas ejecutarlo?** SOLO SI el juego dice "No module named 'pygame'".

**Cómo ejecutarlo en VS Code:**
1. Terminal → New Terminal (Ctrl+Shift+`)
2. Escribe: `pip install pygame`
3. Espera que termine

### `python main.py`
**¿Qué hace?** ¡Inicia el juego!

**¿Cómo?** En VS Code:
- Opción 1: Presiona `F5`
- Opción 2: Click en ▶️ arriba a la derecha
- Opción 3: Terminal → `python main.py`

---

## 🎯 Para Ti: Solo 2 Pasos

### Paso 1: ¿Tienes Pygame?
Prueba ejecutar el juego:
```
python main.py
```

Si dice "No module named 'pygame'", instálalo:
```
pip install pygame
```

### Paso 2: ¡Juega!
```
python main.py
```

---

## 📚 ¿Y Toda Esa Documentación?

Es para el FUTURO. Te hice:

**Si solo quieres JUGAR:**
- Ignora todo menos `main.py`
- Solo ejecuta el juego

**Si quieres MODIFICAR el juego:**
- Lee `docs/DATABASE.md` para cambiar stats, items, etc.
- No necesitas tocar código

**Si quieres PROGRAMAR mejoras:**
- Lee `docs/ARQUITECTURA.md` para entender el código
- Lee `docs/REFACTORIZACION.md` para mejorarlo

---

## ⚙️ Configuración de VS Code (Opcional)

Para que VS Code ejecute el juego con F5:

1. Crea carpeta `.vscode/` en RPG
2. Dentro crea archivo `launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Juego RPG",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal"
        }
    ]
}
```

Ahora presionando F5 iniciará el juego.

---

## 🆘 Problemas Comunes

### "No module named 'pygame'"
**Solución:**
```
pip install pygame
```

### "python no se reconoce como comando"
**Solución:** Python no está instalado o no está en el PATH.
- Descarga Python desde python.org
- Durante instalación marca "Add to PATH"

### El juego va lento
**Solución:** Edita `settings.json`, cambia:
```json
"fps": 30
```

---

## ✅ Resumen Ultra Rápido

```bash
# ¿Funciona el juego?
python main.py

# ¿Da error de pygame?
pip install pygame

# ¿Funciona ahora?
python main.py

# ¡Listo! 🎮
```

---

**¿Más preguntas?** Pregúntame lo que necesites.
