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

---

# ACTUALIZACIÓN: Efecto Global Automático para Items Especiales

## Problema Detectado (Nueva Sesión)

Los items especiales (como EXPANSOR_RANURAS) actualmente requieren:
1. Seleccionar el item
2. Seleccionar un héroe específico
3. Aplicar efecto solo a ESE héroe
4. El item se consume/desaparece

**Esto está MAL** porque los items especiales deben:
- ✅ Tener efecto automático global (a TODOS los héroes)
- ✅ NO consumirse del inventario
- ✅ NO requerir selección de héroe
- ✅ Permanecer en el apartado "Especiales" como items permanentes

## Solución: Sistema de Efecto Global Automático

### Concepto

Los items especiales actúan como "mejoras pasivas permanentes" simplemente por estar en el inventario.

**Ejemplo**:
```
- Tienes 2 "Expansor de Ranuras" en inventario especial
- Cada uno da +1 ranura
- TODOS los héroes automáticamente tienen +2 ranuras extra
- Los items NO desaparecen, permanecen en el inventario
```

### Cambios Necesarios

#### 1. Modificar heroe.py

Cambiar `ranuras_habilidad_max` de variable fija a propiedad calculada:

```python
class Heroe:
    def __init__(self, ...):
        # Antes: self.ranuras_habilidad_max = clase_data['ranuras_habilidad_max']
        # Ahora: guardar como base
        self.ranuras_habilidad_base = clase_data['ranuras_habilidad_max']
        self.items_db = items_db  # Necesitamos acceso a la DB
    
    @property
    def ranuras_habilidad_max(self):
        """Calcula ranuras dinámicamente: base + expansores en inventario"""
        ranuras = self.ranuras_habilidad_base
        
        # Sumar bonus de expansores en inventario especial
        for id_item, cantidad in self.inventario_especiales.items():
            item_data = self.items_db.get(id_item)
            if item_data and item_data.get('efecto') == "AUMENTA_RANURAS_HABILIDAD":
                bonus_por_expansor = item_data.get('poder', 1)
                ranuras += (cantidad * bonus_por_expansor)
        
        return ranuras
```

#### 2. Modificar pantalla_inventario.py

Cambiar comportamiento del Enter para items especiales:

```python
if tecla == pygame.K_RETURN:
    if self.modo == "seleccion_item":
        if self.lista_items_mostrados:
            item_data = self.lista_items_mostrados[self.item_seleccionado_idx]
            categoria_nombre = self.categorias[self.categoria_actual]["nombre"]
            
            # ITEMS ESPECIALES: Solo mostrar info, NO usar
            if categoria_nombre == "Especiales":
                print(f"╔══════════════════════════════════════╗")
                print(f"║ ITEM ESPECIAL: {item_data['nombre']}")
                print(f"║ EFECTO: Actúa automáticamente")
                print(f"║ DESCRIPCIÓN: {item_data['descripcion']}")
                print(f"╚══════════════════════════════════════╝")
                return None
            
            # ITEMS CONSUMIBLES: funcionamiento normal
            elif item_data["target"] in ["Aliado", "Heroe"]:
                self.item_seleccionado_data = item_data
                self.modo = "seleccion_heroe"
                ...
```

#### 3. Modificar game_data.py

Asegurar que items especiales tienen target="Ninguno":

```python
"expansor_ranuras_1": {
    "id_item": "expansor_ranuras_1",
    "nombre": "Expansor de Ranuras",
    "tipo": "Especial",
    "efecto": "AUMENTA_RANURAS_HABILIDAD",
    "poder": 1,  # +1 ranura por expansor
    "target": "Ninguno",  # NO se usa directamente
    "descripcion": "Aumenta ranuras de habilidad de todos los héroes (efecto automático)",
    "precio": 500
}
```

### Flujo Correcto

1. **Jugador compra/encuentra Expansor de Ranuras**
   - Se añade a inventario_especiales: `{"expansor_ranuras_1": 1}`

2. **Efecto automático inmediato**
   - Al abrir menú de habilidades
   - Sistema calcula: `ranuras = base (3) + expansores (1) = 4`
   - Muestra 4 ranuras disponibles para TODOS los héroes

3. **Visualización en inventario**
   - Categoría "Especiales" muestra: "Expansor de Ranuras x1"
   - Al presionar Enter: solo info, no se puede "usar"
   - El item permanece en inventario

### Beneficios

- ✅ Lógica simple y clara
- ✅ Efecto global automático
- ✅ No requiere micro-gestión
- ✅ Items especiales permanentes como deben ser
- ✅ Escalable para otros items especiales futuros

### Archivos a Modificar

1. `src/heroe.py` - Convertir ranuras_habilidad_max en @property
2. `src/pantalla_inventario.py` - Bloquear "uso" de items especiales
3. `src/game_data.py` - Verificar target="Ninguno" en items especiales
4. Todas las pantallas que usan ranuras_habilidad_max (ya funcionarán automáticamente)

### Testing

- [ ] Con 0 expansores: héroe tiene 3 ranuras
- [ ] Con 1 expansor: héroe tiene 4 ranuras
- [ ] Con 2 expansores: héroe tiene 5 ranuras
- [ ] Efecto es para TODOS los héroes
- [ ] Items NO desaparecen del inventario
- [ ] Enter en item especial: solo muestra info, no permite usar
