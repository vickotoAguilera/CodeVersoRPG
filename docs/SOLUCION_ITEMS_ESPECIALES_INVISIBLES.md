# Solución: Items Especiales No Visibles en Inventario

## Problema Identificado

Los items que dan ranuras (EXPANSOR_RANURAS) no se veían en la pantalla del inventario.

### Causa Raíz

1. **Definición en DB**: El EXPANSOR_RANURAS está definido en `items_db.json` con tipo "Especial"
2. **Ubicación inicial**: Los héroes comienzan con EXPANSOR_RANURAS en su inventario normal (`items_iniciales`)
3. **Lógica de visualización defectuosa**: 
   - La categoría "Especiales" en `pantalla_inventario.py` solo buscaba items en `inventario_especiales`
   - Los items tipo "Especial" en el inventario normal NO se mostraban en ninguna categoría
   - Los items tipo "Consumible" en la categoría "Consumibles" se mostraban correctamente

### Resultado
- EXPANSOR_RANURAS (tipo "Especial") en inventario normal → **INVISIBLE** ✗
- Después de usarse, se movía a inventario especial → **VISIBLE** ✓
- Pero la lógica de uso tenía problemas al consumir desde inventario especial

## Solución Aplicada

### Cambio 1: Construcción de lista de items especiales
**Archivo**: `src/pantalla_inventario.py`
**Líneas**: 98-138

```python
elif categoria_nombre == "Especiales":
    # Mostrar items especiales de AMBOS inventarios (normal y especial)
    # Primero del inventario normal
    for id_item, cantidad in inventario_lider.items():
        if cantidad > 0:
            item_data = self.items_db.get(id_item)
            if item_data and item_data["tipo"] == "Especial":
                self.lista_items_mostrados.append(item_data)
    
    # Luego del inventario especial
    for id_item, cantidad in inventario_especiales.items():
        if cantidad > 0:
            item_data = self.items_db.get(id_item)
            if item_data and item_data["tipo"] == "Especial":
                # Verificar que no se haya agregado ya del inventario normal
                if item_data not in self.lista_items_mostrados:
                    self.lista_items_mostrados.append(item_data)
```

### Cambio 2: Cálculo de cantidad total
**Archivo**: `src/pantalla_inventario.py`
**Líneas**: 492-501

Ahora suma las cantidades de ambos inventarios para items especiales:

```python
if categoria_actual_nombre == "Especiales":
    # Para items especiales, buscar en ambos inventarios y sumar
    cantidad_normal = self.grupo_heroes[0].inventario.get(id_item_actual, 0)
    cantidad_especial = self.grupo_heroes[0].inventario_especiales.get(id_item_actual, 0)
    cantidad = cantidad_normal + cantidad_especial
```

### Cambio 3: Lógica de consumo mejorada
**Archivo**: `src/pantalla_inventario.py`
**Líneas**: 319-334

Ahora consume desde el inventario correcto (normal o especial):

```python
elif item_data['efecto'] == "AUMENTA_RANURAS_HABILIDAD":
    # Consumir desde el inventario correcto (puede estar en normal o especial)
    id_item = item_data['id_item']
    lider = self.grupo_heroes[0]
    
    # Intentar consumir del inventario normal primero
    if lider.tiene_item(id_item):
        lider.usar_item(id_item)
    # Si no está en el normal, consumir del especial
    elif lider.tiene_item_especial(id_item):
        # Reducir cantidad en inventario especial
        lider.inventario_especiales[id_item] -= 1
        if lider.inventario_especiales[id_item] <= 0:
            del lider.inventario_especiales[id_item]
    
    # Aplicar el efecto
    heroe_objetivo.usar_expansor_ranuras(item_data['poder'])
```

## Resultado Final

✅ Los EXPANSOR_RANURAS ahora son visibles en la categoría "Especiales" desde el inicio
✅ La cantidad mostrada es la suma de ambos inventarios
✅ Se pueden usar correctamente sin importar en qué inventario estén
✅ El indicador visual "★" aparece para todos los items especiales

## Consideraciones

- Los items tipo "Especial" pueden estar en cualquier inventario
- El sistema es flexible para futuros items especiales
- La visualización es correcta y consistente
- No se requieren cambios en otros archivos del sistema
