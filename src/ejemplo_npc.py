"""
EJEMPLO: Cómo usar el sistema centralizado de items especiales en NPCs
========================================================================

Este archivo muestra cómo un NPC (tienda, regalo, recompensa de quest)
debe agregar items especiales para que el efecto se aplique automáticamente.
"""

# EJEMPLO 1: NPC que VENDE un Expansor de Ranuras
def npc_vender_item(heroe_comprador, item_id, cantidad, precio, items_db, grupo_heroes):
    """
    Simula una compra en una tienda NPC.
    """
    # Verificar si tiene suficiente oro
    if heroe_comprador.oro_actual < precio:
        print("No tienes suficiente oro.")
        return False
    
    # Cobrar el oro
    heroe_comprador.oro_actual -= precio
    
    # Verificar si es item especial o normal
    if items_db and item_id in items_db:
        item_data = items_db[item_id]
        
        if item_data.get("tipo") == "Especial":
            # ✅ USAR EL MÉTODO CENTRALIZADO
            heroe_comprador.agregar_item_especial(item_id, cantidad, items_db, grupo_heroes)
        else:
            # Item normal
            if item_id in heroe_comprador.inventario:
                heroe_comprador.inventario[item_id] += cantidad
            else:
                heroe_comprador.inventario[item_id] = cantidad
            print(f"  → {item_id} x{cantidad} agregado al inventario")
    
    return True


# EJEMPLO 2: NPC que REGALA un item como recompensa de quest
def npc_dar_recompensa_quest(heroe_receptor, item_id, cantidad, items_db, grupo_heroes):
    """
    Simula un NPC que da un item como recompensa.
    """
    print(f"¡Recompensa obtenida!")
    
    # Verificar si es item especial o normal
    if items_db and item_id in items_db:
        item_data = items_db[item_id]
        
        if item_data.get("tipo") == "Especial":
            # ✅ USAR EL MÉTODO CENTRALIZADO
            heroe_receptor.agregar_item_especial(item_id, cantidad, items_db, grupo_heroes)
        else:
            # Item normal
            if item_id in heroe_receptor.inventario:
                heroe_receptor.inventario[item_id] += cantidad
            else:
                heroe_receptor.inventario[item_id] = cantidad
            print(f"  → {item_id} x{cantidad} agregado al inventario")


# EJEMPLO 3: Drop de batalla (monstruo que dropea item especial)
def monstruo_dropear_item(heroe_receptor, item_id, cantidad, items_db, grupo_heroes):
    """
    Simula un monstruo que dropea un item al ser derrotado.
    """
    print(f"¡El monstruo dejó caer un item!")
    
    # Verificar si es item especial o normal
    if items_db and item_id in items_db:
        item_data = items_db[item_id]
        
        if item_data.get("tipo") == "Especial":
            # ✅ USAR EL MÉTODO CENTRALIZADO
            heroe_receptor.agregar_item_especial(item_id, cantidad, items_db, grupo_heroes)
        else:
            # Item normal
            if item_id in heroe_receptor.inventario:
                heroe_receptor.inventario[item_id] += cantidad
            else:
                heroe_receptor.inventario[item_id] = cantidad
            print(f"  → {item_id} x{cantidad} agregado al inventario")


"""
RESUMEN:
=========
Siempre que agregues un item especial (Expansor de Ranuras, Llaves, etc.):

1. Verificar si es tipo "Especial" en items_db
2. SI ES ESPECIAL → Usar: heroe.agregar_item_especial(item_id, cantidad, items_db, grupo_heroes)
3. SI ES NORMAL → Agregar directamente a heroe.inventario[item_id]

El método agregar_item_especial() se encarga de:
- Agregarlo al inventario_especiales
- Verificar si tiene efecto automático
- Aplicar el efecto inmediatamente (como aumentar ranuras)

¡Ya está todo centralizado! 🎮✨
"""
