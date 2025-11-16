# 🎮 Cómo Probar el Sistema de Habilidades

## 📋 Guía Rápida de Prueba

### Paso 1: Iniciar el Juego
```bash
cd c:\Users\vicko\Documents\RPG
python main.py
```

### Paso 2: Nuevo Juego o Cargar
- **Opción A:** Presiona Enter en "Juego Nuevo"
- **Opción B:** Cargar partida existente

### Paso 3: Abrir Menú de Pausa
- En el mapa, presiona **ESC**
- Verás el menú de pausa con varias opciones

### Paso 4: Seleccionar "Habilidades"
- Navega con ↑↓ hasta "Habilidades"
- Presiona **Enter**
- Aparece la lista de héroes

### Paso 5: Seleccionar Héroe
- Cloud (Guerrero) - Tiene habilidades físicas
- Terra (Mago) - Tiene habilidades mágicas
- Presiona **Enter** en el héroe que quieras

### Paso 6: Ver Pantalla de Habilidades
¡Ahora estás en la pantalla de gestión! Verás 4 paneles:

```
┌─────────────────────────────────────────────────┐
│ SPRITE │  INVENTARIO  │  DESCRIPCIÓN           │
├─────────────────────────────────────────────────┤
│         RANURAS ACTIVAS (1-4)                   │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Pruebas Básicas

### Test 1: Navegar por el Inventario
**Objetivo:** Ver todas las habilidades aprendidas

**Pasos:**
1. El cursor empieza en el panel de inventario (centro)
2. Presiona ↑↓ para navegar
3. Observa cómo cambia la descripción (panel derecho)

**Resultado esperado:**
- Cloud ve: Corte Cruzado, Golpe Fuerte, Embestida
- Terra ve: Bola de Fuego, Tormenta de Hielo, Rayo

---

### Test 2: Equipar Primera Habilidad
**Objetivo:** Equipar una habilidad en la ranura [1]

**Pasos:**
1. Selecciona "Corte Cruzado" (Cloud) o "Bola de Fuego" (Terra)
2. Presiona **Enter**
3. El cursor cambia al panel de ranuras (abajo)
4. La ranura [1] está resaltada en amarillo
5. Presiona **Enter**
6. ✅ ¡Habilidad equipada!

**Resultado esperado:**
- La ranura [1] ahora muestra el nombre de la habilidad
- En el inventario, aparece un punto • antes de la habilidad equipada
- El cursor vuelve al inventario

---

### Test 3: Equipar en Otra Ranura
**Objetivo:** Llenar las 4 ranuras

**Pasos:**
1. Selecciona otra habilidad en el inventario
2. Presiona **Enter**
3. Navega con ↑↓ a la ranura [2]
4. Presiona **Enter**
5. Repite para las ranuras [3] y [4]

**Resultado esperado:**
- Todas las ranuras muestran nombres
- Todos tienen marcador • en el inventario

---

### Test 4: Cambiar de Panel
**Objetivo:** Moverse entre paneles con las flechas

**Pasos:**
1. Desde el inventario, presiona **→** (flecha derecha)
2. El cursor va al panel de ranuras
3. Presiona **←** (flecha izquierda)
4. El cursor vuelve al inventario

**Resultado esperado:**
- El cursor se mueve suavemente entre paneles
- Cooldown de 200ms entre inputs

---

### Test 5: Ver Detalles (Pop-up Grande)
**Objetivo:** Ver información completa de una habilidad

**Pasos:**
1. Selecciona cualquier habilidad en el inventario
2. Presiona **D**
3. Aparece un pop-up grande en el centro

**Resultado esperado:**
```
┌─────────────────────────────────┐
│     CORTE CRUZADO               │
│                                 │
│ Tipo: Habilidad Física          │
│ Costo MP: 5                     │
│ Poder: 25                       │
│ Alcance: Un Enemigo             │
│                                 │
│ Descripción:                    │
│ Un ataque físico cruzado...     │
│                                 │
│ [Presiona D o ESC para cerrar]  │
└─────────────────────────────────┘
```

4. Presiona **D** o **ESC** para cerrar

---

### Test 6: Desequipar Habilidad
**Objetivo:** Quitar una habilidad de una ranura

**Pasos:**
1. Presiona **→** para ir al panel de ranuras
2. Navega con ↑↓ a la ranura [2] (o cualquiera con habilidad)
3. Presiona **X**
4. ✅ ¡Habilidad desequipada!

**Resultado esperado:**
- La ranura [2] ahora muestra "[Vacío]" en gris
- El marcador • desaparece del inventario
- La habilidad sigue en el inventario (no se borra)

---

### Test 7: Sobrescribir Habilidad
**Objetivo:** Reemplazar una habilidad ya equipada

**Pasos:**
1. La ranura [1] tiene "Corte Cruzado"
2. Selecciona "Golpe Fuerte" en el inventario
3. Presiona **Enter**
4. Selecciona ranura [1] (la misma)
5. Presiona **Enter**

**Resultado esperado:**
- "Golpe Fuerte" reemplaza "Corte Cruzado" en ranura [1]
- "Corte Cruzado" pierde su marcador •
- "Golpe Fuerte" gana marcador •
- Ambos siguen en el inventario

---

### Test 8: Scroll en Lista Larga
**Objetivo:** Ver que el scroll funciona (si hay >8 habilidades)

**Pasos:**
1. Si el héroe tiene más de 8 habilidades, navega con ↓
2. Al llegar al item 8, la lista hace scroll
3. Aparece indicador "▼" abajo

**Resultado esperado:**
- Solo se ven 8 items a la vez
- El scroll es automático
- Indicadores ▲ (arriba) y ▼ (abajo) aparecen

**Nota:** Por defecto, Cloud y Terra tienen 3 habilidades cada uno, así que este test requiere añadir más habilidades manualmente a `inventario_habilidades`.

---

### Test 9: Filtrado por Clase
**Objetivo:** Verificar que Cloud solo ve habilidades de Guerrero

**Pasos:**
1. Abre habilidades con Cloud
2. Verifica que solo ves: Corte Cruzado, Golpe Fuerte, Embestida
3. Cierra (ESC) y abre habilidades con Terra
4. Verifica que solo ves: Bola de Fuego, Tormenta de Hielo, Rayo

**Resultado esperado:**
- Cloud (Guerrero) NO ve habilidades mágicas
- Terra (Mago) NO ve habilidades físicas
- Cada clase ve solo sus habilidades compatibles

**Cómo romper el filtro (para probar):**
- En `database/habilidades_db.json`, cambia `"clase_requerida": null`
- Esa habilidad será visible para TODAS las clases

---

### Test 10: Salir de la Pantalla
**Objetivo:** Volver al menú de pausa

**Pasos:**
1. Desde cualquier panel, presiona **ESC**
2. Aparece el menú de pausa
3. Los cambios se guardaron automáticamente

**Resultado esperado:**
- La pantalla se cierra sin errores
- Vuelves al menú de pausa
- Si guardas la partida, las habilidades equipadas se guardan

---

## 🐛 Tests de Errores (Validaciones)

### Test Error 1: Equipar Sin Ranuras Disponibles
**Escenario:** Las 4 ranuras están llenas

**Pasos:**
1. Equipa 4 habilidades diferentes
2. Intenta equipar una 5ta habilidad
3. Debes sobrescribir una ranura existente

**Resultado esperado:**
- El sistema permite sobrescribir (no da error)
- La habilidad antigua vuelve al pool de inventario

---

### Test Error 2: Desequipar Ranura Vacía
**Escenario:** Presionar X en una ranura que ya está vacía

**Pasos:**
1. Ve al panel de ranuras
2. Selecciona una ranura con "[Vacío]"
3. Presiona **X**

**Resultado esperado:**
- No ocurre nada (no crash)
- La ranura sigue vacía
- No aparece error en consola

---

### Test Error 3: Navegación Extrema
**Escenario:** Presionar ↑ en el primer item o ↓ en el último

**Pasos:**
1. En el inventario, presiona ↑ en el primer item
2. El cursor no se mueve (queda en 0)
3. Presiona ↓ hasta el último item
4. Presiona ↓ de nuevo
5. El cursor no se mueve (queda en último)

**Resultado esperado:**
- No crash
- El cursor se queda en los límites
- No hay wrap-around (no va del final al inicio)

---

## 💾 Test de Guardado/Carga

### Test Persistencia
**Objetivo:** Verificar que las habilidades se guardan

**Pasos:**
1. Equipa 3 habilidades en Cloud
2. Presiona ESC → "Guardar" → Slot 1
3. Cierra el juego completamente
4. Reinicia el juego
5. Carga el Slot 1
6. Abre las habilidades de Cloud

**Resultado esperado:**
- Las 3 habilidades siguen equipadas
- El inventario tiene las mismas habilidades
- No se perdió nada

---

## 🎨 Test Visual

### Verificar Colores
- **Habilidades físicas:** Rojo claro (255, 100, 100)
- **Habilidades mágicas:** Azul claro (100, 150, 255)
- **Habilidad equipada:** Marcador • en verde (0, 255, 0)
- **Ranura vacía:** Texto "[Vacío]" en gris (100, 100, 100)
- **Selección actual:** Amarillo (255, 255, 0)

### Verificar Animación
- El sprite del héroe debe animarse (800ms por frame)
- Debe hacer loop: idle → idle → idle → ...

---

## 🔍 Test de Consola (Debugging)

### Mensajes Esperados
Al abrir la pantalla:
```
Abriendo pantalla de habilidades para Cloud
```

Al equipar:
```python
# (No hay mensaje, pero puedes añadir prints en _equipar_habilidad)
```

Al cerrar:
```
Cerrando pantalla de habilidades...
```

---

## 📊 Checklist de Pruebas

Marca cada test que completes:

**Básicos:**
- [ ] Navegar por inventario (↑↓)
- [ ] Equipar primera habilidad
- [ ] Equipar en las 4 ranuras
- [ ] Cambiar de panel (←→)
- [ ] Ver detalles (D)
- [ ] Desequipar (X)
- [ ] Sobrescribir habilidad
- [ ] Salir (ESC)

**Avanzados:**
- [ ] Filtrado por clase (Cloud/Terra)
- [ ] Scroll en lista larga
- [ ] Guardado y carga
- [ ] Validación de errores

**Visuales:**
- [ ] Colores correctos
- [ ] Animación del sprite
- [ ] Cursor visible
- [ ] Scroll indicators (▲▼)

---

## 🚨 Errores Comunes

### Error: "NameError: name 'PantallaHabilidades' is not defined"
**Solución:** Verifica que la línea 19 de `main.py` tiene:
```python
from src.pantalla_habilidades import PantallaHabilidades
```

### Error: No aparece el botón "Habilidades" activo
**Solución:** Verifica que `menu_pausa.py` tiene el código del Paso 7.16

### Error: Al seleccionar héroe, no pasa nada
**Solución:** Verifica que en `main.py` línea 327 está el código del Paso 7.18

### Error: Pantalla se ve mal (paneles deformados)
**Solución:** Verifica que tu pantalla es 800x600. Si usas otra resolución, ajusta las constantes en `pantalla_habilidades.py`

---

## 🎯 Escenario Completo (5 minutos)

**Objetivo:** Probar todas las funcionalidades en una sesión

1. ✅ Inicia el juego → Juego Nuevo
2. ✅ Camina un poco → Presiona ESC
3. ✅ Selecciona "Habilidades" → Elige Cloud
4. ✅ Navega por las 3 habilidades con ↑↓
5. ✅ Equipa "Corte Cruzado" en ranura [1]
6. ✅ Equipa "Golpe Fuerte" en ranura [2]
7. ✅ Equipa "Embestida" en ranura [3]
8. ✅ Presiona D para ver detalles de "Embestida"
9. ✅ Cierra detalles (ESC)
10. ✅ Ve al panel de ranuras (→)
11. ✅ Desequipa ranura [2] con X
12. ✅ Vuelve al inventario (←)
13. ✅ Cierra la pantalla (ESC)
14. ✅ Guarda la partida (Slot 1)
15. ✅ Sal al título → Carga Slot 1
16. ✅ Abre habilidades de Cloud
17. ✅ Verifica que ranuras [1] y [3] tienen habilidades
18. ✅ Verifica que ranura [2] está vacía
19. ✅ Cierra (ESC) → Abre habilidades de Terra
20. ✅ Verifica que ve habilidades mágicas (diferentes de Cloud)

---

## 🎉 ¡Prueba Exitosa!

Si completaste todos los tests, el sistema está 100% funcional.

**Características probadas:**
- ✅ Navegación
- ✅ Equipar/desequipar
- ✅ Filtrado por clase
- ✅ Persistencia (guardado/carga)
- ✅ Validaciones
- ✅ Visual/UX

---

**Fecha:** 2025-11-15  
**Sistema:** Habilidades Equipables  
**Estado:** ✅ PRODUCCIÓN
