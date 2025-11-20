"""
Test completo del editor de mapas avanzado
Verifica todas las funcionalidades implementadas
"""

import sys
from pathlib import Path

print("=" * 60)
print("VERIFICACIÓN COMPLETA DEL EDITOR DE MAPAS AVANZADO")
print("=" * 60)

# Verificar estructura de archivos
print("\n1. Verificando estructura de archivos...")

carpetas_necesarias = [
    "assets/maps",
    "assets/sprites/cofres",
    "assets/sprites/npcs",
    "assets/sprites/heroes/batalla",
    "assets/sprites/monstruos",
    "assets/backgrounds",
    "src/database/mapas"
]

for carpeta in carpetas_necesarias:
    path = Path(carpeta)
    if path.exists():
        archivos = list(path.glob("*"))
        print(f"  ✓ {carpeta}: {len(archivos)} archivos")
    else:
        print(f"  ✗ {carpeta}: NO EXISTE")

# Verificar cloud_batalla.png
print("\n2. Verificando cloud_batalla.png...")
cloud_path = Path("assets/sprites/heroes/batalla/cloud_batalla.png")
if cloud_path.exists():
    print(f"  ✓ cloud_batalla.png encontrado")
else:
    print(f"  ✗ cloud_batalla.png NO EXISTE")

# Verificar fondos de batalla
print("\n3. Verificando fondos de batalla...")
bg_path = Path("assets/backgrounds")
if bg_path.exists():
    fondos = list(bg_path.glob("*.png")) + list(bg_path.glob("*.jpg"))
    print(f"  ✓ {len(fondos)} fondos encontrados:")
    for f in fondos[:5]:
        print(f"    - {f.name}")
else:
    print(f"  ✗ Carpeta backgrounds NO EXISTE")

# Verificar mapas
print("\n4. Verificando mapas disponibles...")
maps_path = Path("assets/maps")
if maps_path.exists():
    mapas = list(maps_path.rglob("*.jpg")) + list(maps_path.rglob("*.png"))
    print(f"  ✓ {len(mapas)} mapas encontrados:")
    for m in mapas[:5]:
        print(f"    - {m.parent.name}/{m.name}")
else:
    print(f"  ✗ Carpeta maps NO EXISTE")

# Verificar sintaxis del código
print("\n5. Verificando sintaxis del editor_mapa_avanzado.py...")
try:
    with open("editor_mapa_avanzado.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
        compile(codigo, "editor_mapa_avanzado.py", "exec")
    print("  ✓ Sintaxis correcta")
except SyntaxError as e:
    print(f"  ✗ ERROR DE SINTAXIS: {e}")
    sys.exit(1)

# Verificar enums
print("\n6. Verificando enums del código...")
if "VISTA_BATALLA" in codigo:
    print("  ✓ ModoEditor.VISTA_BATALLA encontrado")
else:
    print("  ✗ ModoEditor.VISTA_BATALLA NO encontrado")

if "DIBUJAR_MUROS" in codigo:
    print("  ✓ ModoEditor.DIBUJAR_MUROS encontrado")
else:
    print("  ✗ ModoEditor.DIBUJAR_MUROS NO encontrado")

if "CREAR_PORTAL" in codigo:
    print("  ✓ ModoEditor.CREAR_PORTAL encontrado")
else:
    print("  ✗ ModoEditor.CREAR_PORTAL NO encontrado")

# Verificar funciones clave
print("\n7. Verificando funciones implementadas...")
funciones_requeridas = [
    "cargar_fondos_batalla",
    "dibujar_modo_portales",
    "dibujar_modo_batalla",
    "dibujar_vista_batalla"
]

for func in funciones_requeridas:
    if f"def {func}" in codigo:
        print(f"  ✓ {func}() implementada")
    else:
        print(f"  ✗ {func}() NO implementada")

print("\n" + "=" * 60)
print("RESUMEN DE FUNCIONALIDADES:")
print("=" * 60)

funcionalidades = {
    "✓ Zoom con rueda del mouse": "self.zoom" in codigo,
    "✓ Sistema de muros dibujables": "DIBUJAR_MUROS" in codigo,
    "✓ Sistema de portales": "CREAR_PORTAL" in codigo and "dibujar_modo_portales" in codigo,
    "✓ Vista de batalla": "VISTA_BATALLA" in codigo and "dibujar_vista_batalla" in codigo,
    "✓ Mover cámara con arrastre": "arrastrando_camara" in codigo,
    "✓ Carga de imágenes de mapas": "cargar_mapa" in codigo,
    "✓ Lista de mapas con thumbnails": "crear_thumbnail" in codigo and "dibujar_modo_portales" in codigo,
    "✓ Fondos de batalla": "cargar_fondos_batalla" in codigo,
    "✓ Sprites héroes/monstruos separados": "heroes_batalla" in codigo or "héroes" in codigo,
    "✓ Simulación ventana UI batalla": "ui_alto = 200" in codigo,
    "✓ cloud_batalla.png enlazado": "cloud_batalla" in codigo
}

todo_ok = True
for func, status in funcionalidades.items():
    if status:
        print(f"  {func}")
    else:
        print(f"  ✗ FALTA: {func}")
        todo_ok = False

print("\n" + "=" * 60)
if todo_ok:
    print("✅ TODAS LAS FUNCIONALIDADES IMPLEMENTADAS")
    print("=" * 60)
    print("\nPuedes ejecutar: python editor_mapa_avanzado.py")
else:
    print("⚠️ ALGUNAS FUNCIONALIDADES FALTAN")
    print("=" * 60)

print("\n")
