# 🧪 TEST - Sistema de Items Especiales

## ✅ SISTEMA COMPLETO IMPLEMENTADO

### 📋 Características Implementadas:

#### 1. **Inventario Separado**
- ✅ `inventario_especiales` en cada héroe
- ✅ Se guarda y carga correctamente
- ✅ Compatible con partidas antiguas

#### 2. **Categorías en Pantalla de Inventario**
- ✅ **Consumibles**: Pociones, Éteres
- ✅ **Especiales**: Llaves, Expansores usados, Amuletos
- ✅ **Equipos**: Armas, Armaduras, Accesorios
- ✅ Navegación con TAB o flechas ←→

#### 3. **Items Especiales Disponibles**
```json
- EXPANSOR_RANURAS: Se mueve automáticamente a especiales al usarse
- LLAVE_BRONCE: Llave para puertas de bronce
- LLAVE_PLATA: Llave para puertas de plata  
- LLAVE_ORO: Llave para puertas de oro
```

#### 4. **Funciones en heroe.py**
```python
# Verificar si tiene un item especial
heroe.tiene_item_especial("LLAVE_BRONCE")  # → True/False

# Agregar item especial
heroe.agregar_item_especial("LLAVE_ORO", 1)

# Obtener lista de items especiales
heroe.obtener_items_especiales()  # → [{"id": "LLAVE_BRONCE", "cantidad": 1}, ...]
```

#### 5. **Indicadores Visuales**
- ★ Items especiales marcados con estrella
- Descripción indica: "(No se consume - permanece en inventario)"
- Cantidad mostrada correctamente desde `inventario_especiales`

---

## 🎮 CÓMO PROBAR:

### 1. **Probar Expansor de Ranuras**
```
1. Ejecutar el juego
2. Ir al menú → Inventario
3. Seleccionar categoría "Consumibles"
4. Usar "Expansor de Ranuras" en un héroe
5. Cambiar a categoría "Especiales"
6. Verificar que el expansor aparece con ★
7. Ir al menú → Habilidades
8. Verificar que ahora hay 6 ranuras (era 4)
```

### 2. **Probar Llaves**
```
1. Agregar llave manualmente (si aún no está implementado el sistema de puertas):
   - En main.py, después de cargar héroes:
     grupo_heroes[0].agregar_item_especial("LLAVE_BRONCE", 1)

2. Ir al menú → Inventario
3. Seleccionar categoría "Especiales"
4. Verificar que la llave aparece con ★
5. La llave NO se puede usar (dice "no se puede usar directamente")
6. Cuando implementes puertas, usar:
   if heroe.tiene_item_especial("LLAVE_BRONCE"):
       # Abrir puerta
```

### 3. **Probar Guardado/Carga**
```
1. Usar expansor de ranuras
2. Guardar partida
3. Cargar partida
4. Verificar que:
   - El expansor sigue en "Especiales"
   - Las ranuras extra se mantienen (6 en lugar de 4)
   - Los items especiales se cargan correctamente
```

---

## 🔧 SISTEMA TÉCNICO:

### **Flujo de Items Especiales:**

```
CONSUMIBLES (se eliminan al usar):
Inventario Normal → Usar Item → Desaparece
Ejemplo: Poción

ESPECIALES (permanecen):
Inventario Normal → Usar Item → Inventario Especiales
Ejemplo: Expansor de Ranuras

LLAVES (no se usan, solo se verifican):
Obtener → Inventario Especiales → Verificar cuando se necesita
Ejemplo: Llave de Bronce para abrir puerta
```

### **Guardado:**
```python
# En main.py, al guardar:
"inventario": heroe.inventario,  # Items consumibles y equipos
"inventario_especiales": heroe.inventario_especiales,  # Llaves, expansores

# En main.py, al cargar:
heroe.inventario_especiales = data_heroe.get("inventario_especiales", {}).copy()
```

---

## 📊 VERIFICACIÓN RÁPIDA:

Ejecuta en la consola de Python:
```python
# Después de cargar un héroe
print("Items normales:", grupo_heroes[0].inventario)
print("Items especiales:", grupo_heroes[0].inventario_especiales)
print("Ranuras de habilidad:", grupo_heroes[0].ranuras_habilidad_max)
```

---

## ✅ TODO COMPLETADO:

- ✅ Items especiales no se consumen
- ✅ Se mueven a inventario_especiales automáticamente
- ✅ Categorías funcionando (Consumibles/Especiales/Equipos)
- ✅ Indicadores visuales (★)
- ✅ Sistema de guardado/carga actualizado
- ✅ Expansor funciona correctamente
- ✅ Llaves agregadas a la base de datos
- ✅ Funciones de verificación implementadas

---

## 🎯 PRÓXIMO PASO:

**Implementar Sistema de Puertas:**
```python
# En mapa.py o donde manejes interacciones:
def intentar_abrir_puerta(heroe, tipo_llave):
    if heroe.tiene_item_especial(tipo_llave):
        print(f"¡Puerta abierta con {tipo_llave}!")
        return True
    else:
        print(f"Necesitas {tipo_llave} para abrir esta puerta.")
        return False

# Ejemplo de uso:
if intentar_abrir_puerta(grupo_heroes[0], "LLAVE_BRONCE"):
    # Permitir paso
    pass
```

---

**Fecha de implementación:** 16 de Noviembre 2025  
**Estado:** ✅ COMPLETO Y FUNCIONAL
