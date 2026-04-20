# 🌍 SISTEMA DE ITEMS ESPECIALES GLOBALES

**Fecha:** 16 Noviembre 2025 - 23:30 UTC  
**Versión:** 1.0

---

## 📋 DESCRIPCIÓN GENERAL

Los **Items Especiales** son items que tienen efecto **GLOBAL** y **AUTOMÁTICO** en todo el grupo de héroes. No se consumen al usarse y su efecto es permanente mientras estén en el inventario.

### Características principales:

1. **NO consumibles** - Permanecen en el inventario siempre
2. **Efecto automático** - Se aplican al iniciar/cargar partida
3. **Efecto global** - Afectan a TODOS los héroes del grupo
4. **Acumulativos** - Múltiples items del mismo tipo multiplican el efecto
5. **Solo visualización** - NO se pueden usar manualmente con Enter
6. **Verificación por ID** - Solo se verifica si existen en el inventario

---

## 🔧 TIPOS DE ITEMS ESPECIALES

### 1. Expansor de Ranuras 📦
**ID:** `EXPANSOR_RANURAS`  
**Efecto:** Aumenta las ranuras de habilidades de TODOS los héroes  
**Poder base:** +2 ranuras por expansor  
**Acumulativo:** Sí

**Ejemplo:**
- 0 Expansores: 4 ranuras (base)
- 1 Expansor: 6 ranuras (4 + 2)
- 2 Expansores: 8 ranuras (4 + 4)
- 3 Expansores: 10 ranuras (4 + 6)

**Fórmula:**
```
Ranuras totales = Ranuras base + (Cantidad de expansores × 2)
```

---

### 2. Llaves 🔑
**IDs:** `LLAVE_BRONCE`, `LLAVE_PLATA`, `LLAVE_ORO`  
**Efecto:** Permite abrir puertas/cofres cerrados  
**Poder:** 0 (solo verificación de ID)  
**Acumulativo:** No (solo necesita existir)

**Uso:**
- Al interactuar con una puerta cerrada de plata
- El sistema verifica si existe `LLAVE_PLATA` en inventario_especiales
- Si existe → Abrir puerta
- Si no existe → Mostrar mensaje "Necesitas una Llave de Plata"

---

## ⚙️ IMPLEMENTACIÓN TÉCNICA

### Función Principal: `aplicar_efectos_items_especiales_globales()`

**Ubicación:** `main.py` (líneas 72-140)

**Se ejecuta en:**
1. Al iniciar nueva partida (después de crear el grupo)
2. Al cargar partida guardada (después de cargar héroes)
3. (Futuro) Al obtener nuevos items especiales

**Lógica:**
```python
def aplicar_efectos_items_especiales_globales(grupo_heroes):
    """
    1. Obtener inventario especial del líder
    2. Para cada item especial:
       a. Obtener cantidad del item
       b. Calcular poder total (poder_base × cantidad)
       c. Aplicar efecto a TODOS los héroes
    """
```

---

### Función Auxiliar: `_aplicar_efecto_especial()`

**Lógica por tipo de efecto:**

```python
if efecto == "AUMENTA_RANURAS_HABILIDAD":
    poder_total = poder_base × cantidad
    Para cada héroe:
        heroe.ranuras_habilidad_max = 4 + poder_total

elif efecto == "LLAVE":
    # No hacer nada, solo verificar existencia en inventario
    pass
```

---

## 🎮 COMPORTAMIENTO EN EL JUEGO

### En Pantalla de Inventario (Pestaña "Especiales")

**Navegación permitida:**
- ✅ Mover cursor con ↑↓ para ver items
- ✅ Presionar 'd' para ver descripción completa
- ❌ Presionar Enter NO hace nada (mensaje informativo)

**Mensaje al intentar usar con Enter:**
```
[INFO] Items especiales no se usan manualmente.
[INFO] Su efecto es automático y global.
[INFO] Presiona 'd' para ver la descripción del item.
```

### Visualización

**Items especiales muestran:**
- Nombre del item
- Cantidad total (suma de inventario normal + especial)
- Descripción que explica el efecto automático
- Icono especial `[*]` en la pestaña

---

## 📊 EJEMPLO PRÁCTICO

### Escenario: Jugador tiene 2 Expansores de Ranuras

**Al iniciar partida:**
```
=== Aplicando Efectos de Items Especiales Globales ===
  Item: Expansor de Ranuras x2
    → Cloud: 8 ranuras (+4)
    → Terra: 8 ranuras (+4)
    → Aeris: 8 ranuras (+4)
    → Barret: 8 ranuras (+4)
=== Efectos Aplicados ===
```

**Resultado:**
- Todos los héroes ahora tienen 8 ranuras de habilidades
- No se consumieron los expansores
- El efecto persiste mientras los items estén en el inventario
- Si se guardan ranuras extras manualmente, se respetan

---

## 🔄 FLUJO DE DATOS

### Nueva Partida
```
1. Crear grupo de héroes
2. Aplicar efectos globales automáticamente
3. Jugador puede ver items en pestaña "Especiales"
4. Efectos ya están aplicados (no necesita hacer nada)
```

### Cargar Partida
```
1. Cargar datos de héroes
2. Cargar inventarios (normal + especial)
3. Aplicar efectos globales automáticamente
4. Si guardado tiene ranuras_habilidad_max guardadas:
   - Respetar valor guardado (ya incluye efectos)
   - Recalcular con items actuales
```

### Obtener Nuevo Item Especial (Futuro)
```
1. Agregar item a inventario_especiales
2. Llamar a aplicar_efectos_items_especiales_globales()
3. Mostrar mensaje: "¡Efecto aplicado a todos los héroes!"
```

---

## 📝 ARCHIVOS MODIFICADOS

### 1. `main.py`
- Agregada función `aplicar_efectos_items_especiales_globales()`
- Agregada función auxiliar `_aplicar_efecto_especial()`
- Llamada al iniciar nueva partida (línea ~283)
- Llamada al cargar partida guardada (línea ~395)

### 2. `src/pantalla_inventario.py`
- Modificado comportamiento de Enter en pestaña "Especiales"
- Agregados mensajes informativos
- Items especiales NO son seleccionables con Enter

### 3. `src/database/items_db.json`
- Actualizada descripción de `EXPANSOR_RANURAS`
- Cambiado target de "Heroe" a "Global"

### 4. `src/heroe.py`
- Cambiado `ranuras_habilidad_max_base` a `ranuras_habilidad_max` (línea 40)
- Permitir modificación dinámica de ranuras

---

## 🎯 VENTAJAS DEL SISTEMA

1. **Simplicidad:** El jugador no necesita hacer nada manualmente
2. **Claridad:** Efecto visible inmediatamente en todas las pantallas
3. **Persistencia:** Los efectos se guardan correctamente
4. **Escalabilidad:** Fácil agregar nuevos tipos de items especiales
5. **Flexibilidad:** Funciona con items acumulativos y no acumulativos
6. **Usabilidad:** No hay confusión sobre cómo "usar" items especiales

---

## 🔮 ITEMS ESPECIALES FUTUROS (Propuestos)

### Amuletos Permanentes
- **Amuleto de Fuerza:** +5 Fuerza a todos los héroes (global)
- **Amuleto de Velocidad:** +3 Velocidad a todos los héroes (global)

### Libros de Conocimiento
- **Libro de Fuego:** Desbloquea habilidades de fuego para todos los magos
- **Libro de Hielo:** Desbloquea habilidades de hielo para todos los magos

### Reliquias
- **Reliquia de Experiencia:** +50% XP ganado en batallas (global)
- **Reliquia de Oro:** +30% Oro ganado en batallas (global)

---

## ⚠️ NOTAS IMPORTANTES

1. **Items especiales NUNCA se consumen**
2. **No es posible "desequipar" items especiales**
3. **Los efectos son permanentes mientras estén en inventario**
4. **Si se pierde un item especial (vender/tirar), el efecto desaparece**
5. **Al cargar partida, los efectos se recalculan automáticamente**

---

## 🐛 DEBUGGING

### Verificar Items Especiales
```python
# En consola Python
lider = grupo_heroes[0]
print(lider.inventario_especiales)
# Output: {'EXPANSOR_RANURAS': 2, 'LLAVE_PLATA': 1}
```

### Verificar Ranuras Aplicadas
```python
for heroe in grupo_heroes:
    print(f"{heroe.nombre_en_juego}: {heroe.ranuras_habilidad_max} ranuras")
# Output:
# Cloud: 8 ranuras
# Terra: 8 ranuras
```

### Ver Log de Aplicación
Al iniciar/cargar partida, la consola muestra:
```
=== Aplicando Efectos de Items Especiales Globales ===
  Item: Expansor de Ranuras x2
    → Cloud: 8 ranuras (+4)
    → Terra: 8 ranuras (+4)
=== Efectos Aplicados ===
```

---

**Última Actualización:** 16 Noviembre 2025 - 23:30 UTC  
**Autor:** CodeVerso RPG Development Team  
**Versión del Sistema:** 1.0
