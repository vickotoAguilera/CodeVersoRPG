"""
Script para organizar la documentación en su propia carpeta.
Ejecuta esto SOLO UNA VEZ para limpiar la raíz del proyecto.
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("="*70)
print("ORGANIZANDO DOCUMENTACIÓN EN CARPETA docs/")
print("="*70)

# Crear carpeta docs si no existe
docs_dir = os.path.join(BASE_DIR, "docs")
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)
    print("\n✓ Carpeta docs/ creada")
else:
    print("\n✓ Carpeta docs/ ya existe")

# Lista de archivos de documentación a mover
archivos_docs = [
    "LEEME_PRIMERO.txt",
    "INICIO_RAPIDO.md",
    "README.md",
    "ARQUITECTURA.md",
    "DATABASE.md",
    "REFACTORIZACION.md",
    "RESUMEN_CAMBIOS.md",
    "INDICE_PROYECTO.md"
]

print("\nMoviendo archivos de documentación...")
movidos = 0
for archivo in archivos_docs:
    origen = os.path.join(BASE_DIR, archivo)
    destino = os.path.join(docs_dir, archivo)
    
    if os.path.exists(origen):
        # Si ya existe en destino, eliminarlo primero
        if os.path.exists(destino):
            os.remove(destino)
        
        shutil.move(origen, destino)
        print(f"  ✓ Movido: {archivo}")
        movidos += 1
    else:
        print(f"  ⚠ No encontrado: {archivo}")

print(f"\n✓ {movidos} archivos movidos a docs/")

# Crear un README simple en la raíz
readme_raiz = os.path.join(BASE_DIR, "README.md")
with open(readme_raiz, 'w', encoding='utf-8') as f:
    f.write("""# Code Verso RPG

Un juego de rol (RPG) 2D desarrollado en Python con Pygame.

## 🎮 Para Jugar

```bash
python main.py
```

## 📚 Documentación

Toda la documentación está en la carpeta `docs/`:

- **docs/LEEME_PRIMERO.txt** - Empieza aquí
- **docs/GUIA_RAPIDA_VSCODE.md** - Para usar con VS Code
- **docs/INICIO_RAPIDO.md** - Guía rápida
- **docs/DATABASE.md** - Modificar datos del juego
- **docs/ARQUITECTURA.md** - Diseño técnico

## 🔧 Instalación

Si no tienes pygame:

```bash
pip install pygame
```

## 🎯 Controles

- **Flechas:** Movimiento / Navegación
- **Enter:** Confirmar / Interactuar
- **ESC:** Menú de pausa
- **D:** Ver detalles

## 📖 Más Información

Lee `docs/LEEME_PRIMERO.txt` para información completa.
""")

print("\n✓ README.md creado en la raíz")

# Crear archivo de inicio rápido
inicio_rapido = os.path.join(BASE_DIR, "INICIO.txt")
with open(inicio_rapido, 'w', encoding='utf-8') as f:
    f.write("""================================================================================
                        CODE VERSO RPG - INICIO RÁPIDO
================================================================================

PARA JUGAR:

    1. Abre VS Code en esta carpeta
    2. Presiona F5 o escribe en terminal:
       
       python main.py

    3. ¡Juega!


SI DA ERROR "No module named pygame":

    En la terminal de VS Code escribe:
    
    pip install pygame
    
    Luego ejecuta de nuevo: python main.py


DOCUMENTACIÓN:

    Toda la documentación está en la carpeta docs/
    
    Lee primero: docs/LEEME_PRIMERO.txt


ESTRUCTURA:

    RPG/
    ├── main.py              ← ¡EJECUTA ESTE!
    ├── settings.json        ← Configuración
    ├── INICIO.txt          ← Este archivo
    │
    ├── docs/                ← Documentación completa
    │   ├── LEEME_PRIMERO.txt
    │   ├── GUIA_RAPIDA_VSCODE.md
    │   └── ... más guías
    │
    ├── src/                 ← Código del juego
    ├── database/            ← Datos (JSON)
    ├── assets/              ← Gráficos
    ├── saves/               ← Partidas guardadas
    └── logs/                ← Archivos de log


CONTROLES:

    Flechas = Movimiento / Navegación
    Enter   = Confirmar / Interactuar
    ESC     = Menú de pausa
    D       = Ver detalles


¿PREGUNTAS?

    Lee docs/GUIA_RAPIDA_VSCODE.md para más ayuda

================================================================================
""")

print("✓ INICIO.txt creado en la raíz")

print("\n" + "="*70)
print("¡LISTO! PROYECTO ORGANIZADO")
print("="*70)

print("""
AHORA TU PROYECTO SE VE ASÍ:

RPG/
├── main.py              ← Ejecuta esto para jugar
├── INICIO.txt           ← Instrucciones rápidas
├── README.md            ← Info básica
├── settings.json        ← Configuración
├── requirements.txt     ← Dependencias
│
├── docs/                ← TODA la documentación aquí
│   ├── LEEME_PRIMERO.txt
│   ├── GUIA_RAPIDA_VSCODE.md
│   ├── INICIO_RAPIDO.md
│   ├── ARQUITECTURA.md
│   ├── DATABASE.md
│   ├── REFACTORIZACION.md
│   ├── RESUMEN_CAMBIOS.md
│   └── INDICE_PROYECTO.md
│
├── src/                 ← Código fuente
├── database/            ← Datos del juego
├── assets/              ← Recursos gráficos
├── saves/               ← Partidas guardadas
└── logs/                ← Logs del juego

PARA JUGAR:
    python main.py

PARA MÁS INFO:
    Lee docs/LEEME_PRIMERO.txt o docs/GUIA_RAPIDA_VSCODE.md
""")
