# 📋 TAREAS PENDIENTES - ACTUALIZADO
**Fecha:** 15 de Noviembre 2025
**Estado:** En Desarrollo Activo

---

## ✅ COMPLETADO RECIENTEMENTE

### Sistema de Habilidades
- [x] Pantalla de habilidades funcional con 4 paneles
- [x] Sistema de equipar/desequipar habilidades
- [x] Prevención de duplicados en ranuras activas
- [x] Scroll vertical en lista de habilidades (FUNCIONAL)
- [x] Navegación con flechas en todas las ventanas
- [x] Botón "Volver" para regresar al menú pausa
- [x] Mostrar descripción completa con scroll
- [x] Sistema de DOT y HOT básico implementado

### Interfaz de Batalla
- [x] Pantalla de selección de habilidades en batalla
- [x] Mostrar habilidades del héroe activo en turno
- [x] Descripción con scroll automático

---

## 🔴 PRIORIDAD ALTA - SIGUIENTE SESIÓN

### 1. Sistema de Scroll Completo (URGENTE)
**Problema:** No todas las ventanas scrolleables tienen el indicador visual y funcionalidad completa.

**Tareas:**
- [ ] Agregar scroll visual (barra lateral) a `pantalla_inventario.py` (Objetos en Menú Pausa)
- [ ] Agregar scroll visual a panel de habilidades en `pantalla_habilidades.py`
- [ ] Agregar scroll visual a `pantalla_equipo.py` si es necesario
- [ ] Agregar scroll visual a `pantalla_estado.py` si hay texto largo
- [ ] Verificar que TODAS las listas largas tengan scroll funcional

**Archivos a modificar:**
```
src/pantalla_inventario.py
src/pantalla_habilidades.py  (panel inventario)
src/pantalla_equipo.py
src/pantalla_estado.py
```

---

### 2. Sistema de Categorías en Inventario (URGENTE)
**Problema:** Los objetos no están organizados por categorías.

**Tareas:**
- [ ] Modificar `database/items_db.json` para agregar campo "categoria"
- [ ] Categorías: "Consumible", "Equipo", "Especial", "Misc"
- [ ] Modificar `pantalla_inventario.py` para mostrar pestañas/filtros
- [ ] Implementar navegación entre categorías (Tab o L/R)
- [ ] Marcar el "Expansor de Ranuras" como categoría "Especial"

**Archivos a modificar:**
```
src/database/items_db.json
src/pantalla_inventario.py
```

---

### 3. Lógica del Expansor de Ranuras (CRÍTICO)
**Problema:** El expansor de ranuras no funciona.

**Tareas:**
- [ ] Verificar que el objeto existe en `items_db.json`
- [ ] Crear función `usar_expansor_ranuras()` en `heroe.py`
- [ ] Agregar lógica de uso en `pantalla_inventario.py`
- [ ] Incremento: +2 ranuras por cada uso
- [ ] Acumulativo: Si usa 2 expansores = +4 ranuras total
- [ ] Actualizar `ranuras_habilidad_max` del héroe
- [ ] Guardar cambio en archivo de guardado
- [ ] Mostrar mensaje de confirmación

**Archivos a modificar:**
```
src/heroe.py
src/pantalla_inventario.py
src/database/items_db.json
```

---

### 4. Conectar Habilidades con Batalla (FUNCIONALIDAD CORE)
**Problema:** Las habilidades están equipadas pero no se ejecutan correctamente en batalla.

**Tareas:**
- [ ] Modificar `batalla.py` para leer habilidades de `heroe.habilidades_activas`
- [ ] Implementar ejecución de habilidades según tipo:
  - [ ] Daño simple
  - [ ] Curación
  - [ ] AoE (área de efecto)
  - [ ] DOT (daño sobre tiempo)
  - [ ] HOT (curación sobre tiempo)
- [ ] Agregar sistema de contadores de turnos para DOT/HOT
- [ ] Mostrar efectos activos en interfaz de batalla
- [ ] Calcular daño/curación según estadísticas del héroe

**Archivos a modificar:**
```
src/batalla.py
src/heroe.py
src/monstruo.py
```

---

## 📝 Prioridad de Implementación

### Alta Prioridad
1. **Sistema de Scroll Global** (necesario para usabilidad)
2. **Sistema de Expansor de Ranuras** (funcionalidad core)

### Media Prioridad
3. **Categorización de Objetos** (mejora UX)

### Baja Prioridad
4. **Testing completo** (verificación final)

---

## 🎯 Plan de Acción Inmediato

### Paso 1: Sistema de Scroll (30-45 min)
- Aplicar scroll a pantalla_items.py
- Aplicar scroll a pantalla_inventario.py (batalla)
- Aplicar scroll a pantalla_estado.py
- Mejorar scroll existente en pantalla_habilidades.py

### Paso 2: Expansor de Ranuras (20-30 min)
- Implementar lógica de detección
- Agregar ranuras dinámicas
- Actualizar sistema de guardado

### Paso 3: Categorización de Objetos (30-40 min)
- Modificar items_db.json
- Crear sistema de pestañas
- Implementar filtrado

### Paso 4: Testing Final (15-20 min)
- Probar todas las funcionalidades
- Verificar que no haya bugs
- Documentar cualquier issue

---

## 📌 Notas Importantes

- **Chilenismos:** Ya fueron convertidos a español neutro
- **Mouse:** No se implementará, todo es con teclado
- **Navegación:** Flechas para moverse, ENTER para seleccionar, ESC/Botón para volver
- **Arquitectura:** Estructura modular con src/, database/, assets/

---

## 🔄 Estado General del Proyecto

**Fase Actual:** Fase 7 - Sistema de Habilidades (90% completado)
**Siguiente Fase:** Fase 8 - Gestión de Grupo
**Progreso Total:** ~65% del proyecto completo

