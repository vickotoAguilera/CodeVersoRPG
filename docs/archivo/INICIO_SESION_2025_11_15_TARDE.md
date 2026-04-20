# 🎮 INICIO DE SESIÓN - 15 Noviembre 2025 (Tarde)

## 📍 Estado Actual

### ✅ Lo que ya funciona:
1. Sistema de habilidades funcionando
2. Pantalla de habilidades con navegación
3. Botón de volver funcional
4. Scroll en batalla (descripción de habilidades)
5. DOTs/HOTs implementados
6. Habilidades enlazadas a batalla

### 🔧 Lo que vamos a hacer AHORA:

#### **TAREA 1: Sistema de Scroll Mejorado** (EN PROCESO)
Vamos a implementar scroll visual con scrollbar en:
- ✓ `pantalla_lista_habilidades.py` (batalla) - YA TIENE
- ❌ `pantalla_inventario.py` (menú pausa) - MEJORAR
- ❌ `pantalla_habilidades.py` (menú pausa) - MEJORAR  
- ❌ `pantalla_estado.py` (menú pausa) - AGREGAR

#### **TAREA 2: Expansor de Ranuras**
- Detectar ítem en inventario
- Incrementar ranuras (+2, +4, +6...)
- Hacer scroll en ranuras si hay muchas

#### **TAREA 3: Categorización de Objetos**
- Consumibles
- Equipo
- Varios
- Especiales

---

## 🎯 Plan Inmediato

### Paso 1: Agregar Scrollbar Visual a `pantalla_inventario.py`
**Tiempo estimado:** 15 min

**Cambios:**
- Agregar dibujo de scrollbar en panel de ítems
- Agregar indicador de posición (thumb)
- Mantener lógica de scroll existente

**Archivos:**
- `src/pantalla_inventario.py`

---

### Paso 2: Agregar Scrollbar Visual a `pantalla_habilidades.py`
**Tiempo estimado:** 15 min

**Cambios:**
- Agregar scrollbar en panel de inventario de habilidades
- Agregar scrollbar en panel de ranuras activas (si hay muchas)

**Archivos:**
- `src/pantalla_habilidades.py`

---

### Paso 3: Agregar Scroll a `pantalla_estado.py`
**Tiempo estimado:** 15 min

**Cambios:**
- Revisar si necesita scroll
- Agregar si la lista de héroes es larga

**Archivos:**
- `src/pantalla_estado.py`

---

### Paso 4: Implementar Sistema de Expansor de Ranuras
**Tiempo estimado:** 25 min

**Cambios:**
1. Verificar que existe el ítem en `items_db.json`
2. Agregar lógica en `heroe.py` para `ranuras_extra`
3. Modificar `pantalla_habilidades.py` para:
   - Detectar ítem en inventario
   - Calcular ranuras totales = base + extras
   - Hacer scroll si hay muchas ranuras
4. Actualizar `gestor_guardado.py` para guardar/cargar

**Archivos:**
- `src/database/items_db.json`
- `src/heroe.py`
- `src/pantalla_habilidades.py`
- `src/gestor_guardado.py`

---

### Paso 5: Categorización de Objetos
**Tiempo estimado:** 30 min

**Cambios:**
1. Agregar campo "categoria" a todos los ítems en `items_db.json`
2. Modificar `pantalla_inventario.py` para:
   - Crear sistema de pestañas (Consumibles/Equipo/Varios/Especiales)
   - Filtrar ítems según categoría
   - Permitir navegación entre pestañas
3. Agregar scroll independiente por categoría

**Archivos:**
- `src/database/items_db.json`
- `src/pantalla_inventario.py`

---

## 🚀 EMPEZAMOS

### ➡️ Siguiente: Paso 1 - Scrollbar en pantalla_inventario.py

