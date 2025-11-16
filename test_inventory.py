import json
import os

# Cargar datos
DATABASE_PATH = os.path.join("src", "database")
RUTA_ITEMS_DB = os.path.join(DATABASE_PATH, "items_db.json")
RUTA_GRUPO_INICIAL = os.path.join(DATABASE_PATH, "grupo_inicial.json")

with open(RUTA_ITEMS_DB, 'r', encoding='utf-8') as f:
    ITEMS_DB = json.load(f)

with open(RUTA_GRUPO_INICIAL, 'r', encoding='utf-8') as f:
    GRUPO_INICIAL = json.load(f)

print("=== ITEMS_DB ===")
for id_item, data in ITEMS_DB.items():
    print(f"{id_item}: tipo={data['tipo']}, nombre={data['nombre']}")

print("\n=== INVENTARIOS DE HÉROES ===")
for heroe_data in GRUPO_INICIAL:
    print(f"\n{heroe_data['nombre_en_juego']}:")
    print(f"  Inventario normal: {heroe_data['items_iniciales']}")
    print(f"  Inventario especial: {heroe_data.get('items_especiales', {})}")

# Simular lo que hace pantalla_inventario.py
print("\n=== SIMULACIÓN DE CONSTRUCCIÓN DE LISTA ===")

inventario_lider = GRUPO_INICIAL[0]['items_iniciales']
inventario_especiales = GRUPO_INICIAL[0].get('items_especiales', {})

print("\nCategoría: Consumibles")
lista_consumibles = []
for id_item, cantidad in inventario_lider.items():
    if cantidad > 0:
        item_data = ITEMS_DB.get(id_item)
        if item_data and item_data["tipo"] == "Consumible":
            lista_consumibles.append(item_data["nombre"])
            print(f"  - {item_data['nombre']} (x{cantidad})")

print("\nCategoría: Especiales")
lista_especiales = []
for id_item, cantidad in inventario_especiales.items():
    if cantidad > 0:
        item_data = ITEMS_DB.get(id_item)
        if item_data and item_data["tipo"] == "Especial":
            lista_especiales.append(item_data["nombre"])
            print(f"  - {item_data['nombre']} (x{cantidad})")

print("\n=== PROBLEMA DETECTADO ===")
print("Si EXPANSOR_RANURAS está en inventario_especiales pero items_db lo define como tipo 'Especial',")
print("debería aparecer en la categoría Especiales.")
print("\nVerificando si EXPANSOR_RANURAS existe:")
if "EXPANSOR_RANURAS" in inventario_especiales:
    print(f"  ✓ Está en inventario_especiales con cantidad: {inventario_especiales['EXPANSOR_RANURAS']}")
else:
    print("  ✗ NO está en inventario_especiales")

if "EXPANSOR_RANURAS" in inventario_lider:
    print(f"  ✓ Está en inventario normal con cantidad: {inventario_lider['EXPANSOR_RANURAS']}")
else:
    print("  ✗ NO está en inventario normal")
