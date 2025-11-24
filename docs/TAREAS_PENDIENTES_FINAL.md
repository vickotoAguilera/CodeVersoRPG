# 📋 TAREAS PENDIENTES - Sistema RPG

**Última Actualización:** 16 Noviembre 2025 - 14:10 UTC

---

## ✅ RECIÉN COMPLETADO

### Sistema de Efectos DOT/HOT ✅ COMPLETADO
- ✅ Efectos DOT (Damage Over Time) funcionando
- ✅ Efectos HOT (Heal Over Time) funcionando
- ✅ Regeneración de MP funcionando
- ✅ Textos flotantes con colores por tipo
- ✅ Procesamiento automático cada turno
- ✅ Habilidades DOT: Quemadura, Sangrado, Veneno, Llamas Infernales
- ✅ Habilidades HOT: Recuperación, Revitalizar, Éter
- ✅ Documentación completa en SISTEMA_DOT_HOT_COMPLETO.md

### Items Especiales Visibles ✅ COMPLETADO
- ✅ Expansor de Ranuras ahora visible en inventario
- ✅ Items especiales muestran en categoría correcta
- ✅ Cantidad suma de ambos inventarios (normal + especial)
- ✅ Sistema de consumo flexible

---

## 🔴 PRIORIDAD ALTA (Completar Ahora)

### 1. Sistema de Scroll Global ✅ COMPLETADO
**Tareas:**
- ✅ Implementado en pantalla_habilidades_batalla.py
- ✅ Aplicado a pantalla_items.py (Batalla - Objetos)
- ✅ Aplicado a pantalla_inventario.py (Menú Pausa)
- ✅ Aplicado a pantalla_equipo.py (Menú Pausa)
- ✅ pantalla_estado.py no requiere scroll (diseño fijo)
- ✅ Todas las pantallas que necesitan scroll lo tienen

**Estado:** ✅ 100% completado
**Documentación:** RESUMEN_SCROLL_COMPLETO.md

---

### 2. Sistema de Expansor de Ranuras ✅ COMPLETADO
**Tareas:**
- ✅ Detectar "Expansor de Ranuras" en inventario
- ✅ Aplicar efecto: +2 ranuras por cada expansor
- ✅ Hacer stackeable (múltiples expansores = más ranuras)
- ✅ Actualizar pantalla_habilidades.py para mostrar ranuras dinámicas
- ✅ Guardar ranuras expandidas en sistema de guardado
- ✅ Items visibles en categoría "Especiales"

**Estado:** ✅ 100% completado

---

### 3. Categorización de Objetos en Inventario ✅ COMPLETADO (Menú Pausa)
**Tareas:**
- ✅ Sistema de categorías en pantalla_inventario.py (Menú Pausa)
- ✅ 3 Categorías: Consumibles, Especiales, Equipos
- ✅ Pestañas visuales con indicador de selección
- ✅ Navegación con ← → entre categorías
- ✅ Filtrado automático por categoría
- ✅ Scroll horizontal de pestañas
- ✅ Transición fluida entre modos

**Estado:** ✅ 100% completado para menú pausa
**Pendiente:** Aplicar a pantalla_items.py (batalla) si es necesario

**Categorías implementadas:**
- **Consumibles:** Pociones, Éteres (items con efecto inmediato)
- **Especiales:** Expansor de Ranuras, Llaves (items no consumibles)
- **Equipos:** Armas, Armaduras, Accesorios (solo visualización)

---

### 4. Conectar Habilidades con Sistema de Batalla ✅ COMPLETADO
**Tareas:**
- ✅ Verificar que las habilidades equipadas se ejecuten en batalla
- ✅ Aplicar daño/curación según tipo de habilidad
- ✅ Implementar efectos DOT (Damage Over Time)
- ✅ Implementar efectos HOT (Heal Over Time)
- ✅ Implementar efectos AoE (Area of Effect - todos los enemigos)
- ✅ Calcular consumo de MP por habilidad
- ✅ Mostrar mensajes de error si no hay MP suficiente
- ✅ Actualizar turno después de usar habilidad
- ✅ Textos flotantes con colores por tipo de efecto

**Estado:** ✅ 100% completado

**Habilidades funcionando:**
- ✓ Ataque simple
- ✓ Magia de área
- ✓ DOT: Quemadura (15 daño x 3 turnos)
- ✓ DOT: Sangrado (8 daño x 3 turnos)
- ✓ DOT: Veneno (12 daño x 4 turnos)
- ✓ HOT: Recuperación (15 HP x 3 turnos)
- ✓ HOT: Revitalizar (20 HP x 3 turnos)
- ✓ HOT: Éter (10 MP x 3 turnos)

---

## 🟡 PRIORIDAD MEDIA

### 5. Pantalla de Objetos en Batalla ✅ COMPLETADO
**Tareas:**
- ✅ Implementado pantalla similar a habilidades
- ✅ Mostrar objetos consumibles del inventario
- ✅ Seleccionar objetivo con cursor (héroe)
- ✅ Aplicar efectos del objeto (RESTAURA_HP, RESTAURA_MP)
- ✅ Remover objeto del inventario al usarse
- ✅ Botón volver funcional
- ✅ Scroll visual implementado
- ✅ Textos flotantes con colores

**Estado:** ✅ 100% completado (ya estaba implementado)
**Documentación:** SISTEMA_OBJETOS_BATALLA.md

**Objetos funcionando:**
- Poción: +50 HP (texto verde)
- Éter: +20 MP (texto morado)

---

### 6. Pulir Interfaz de Batalla
**Tareas:**
- [ ] Verificar que todos los menús tengan botón "Volver"
- [ ] Asegurar navegación fluida entre todas las ventanas
- [ ] Verificar que ESC funcione consistentemente
- [ ] Agregar indicadores visuales de turno actual
- [ ] Mostrar efectos activos (DOT/HOT) en cada personaje

**Archivos a modificar:**
```
src/batalla.py
src/pantalla_habilidades_batalla.py
```

---

### 7. Sistema de Guardado Mejorado
**Tareas:**
- [ ] Guardar ranuras de habilidad expandidas
- [ ] Guardar efectos DOT/HOT activos si es necesario
- [ ] Verificar que todo se cargue correctamente
- [ ] Agregar validación de datos al cargar

**Archivos a modificar:**
```
src/gestor_guardado.py
main.py (funciones guardar/cargar)
```

---

## 🟢 MEJORAS FUTURAS (No Urgente)

### 8. Pool de Habilidades Expandido
**Estado:** ⏳ Futuro
- Crear 10+ habilidades variadas por clase
- Guerrero: habilidades físicas, buffs
- Mago: habilidades mágicas, debuffs
- Arquero: habilidades de precisión
- Clérigo: habilidades de soporte

### 9. Animaciones de Habilidades
**Estado:** ⏳ Futuro
- Agregar efectos visuales para cada habilidad
- Animaciones de daño/curación
- Partículas de efectos especiales

### 10. Sistema de Combo
**Estado:** ⏳ Futuro
- Permitir combinar habilidades
- Bonificaciones por sinergias
- Sistema de cadenas

---

<<<<<<< HEAD
## 🗺️ HOJA DE RUTA FUTURA (Visión General)

### Fase 8: Gestión de Grupo
**Estado:** ⏳ Próxima fase después de completar Fase 7

**Tareas:**
- [ ] Crear 3 nuevos héroes adicionales (total: 6 héroes en el juego)
- [ ] Actualizar `heroes_db.json` con los nuevos héroes
- [ ] Actualizar `asset_coords_db.py` con las coordenadas de sprites
- [ ] Implementar pantalla "Gestión de Grupo"
  - Grupo activo (4 héroes en batalla)
  - Banca/Reserva (2 héroes adicionales)
  - Sistema de intercambio entre activo y reserva
- [ ] Implementar función "Cambiar Líder"
  - El héroe en ranura[0] es quien camina en el mapa
  - Permitir intercambiar posición del líder

**Archivos a crear/modificar:**
```
database/heroes_db.json
database/asset_coords_db.py
src/pantalla_gestion_grupo.py (NUEVO)
src/heroe.py (actualizar si es necesario)
main.py (agregar entrada al menú)
```

---

### Fase 9: Lógica del Mundo (NPCs)
**Estado:** ⏳ Después de Fase 8

**Tareas:**
- [ ] Implementar sistema de NPCs (Non-Player Characters)
- [ ] Sistema de diálogos interactivos
- [ ] Sistema de tiendas:
  - Comprar items/equipo
  - Vender items del inventario
  - Sistema de precios dinámicos
- [ ] Sistema de misiones/quests de NPCs
- [ ] Crear base de datos de NPCs (`npcs_db.json`)

**Archivos a crear/modificar:**
```
database/npcs_db.json (NUEVO)
database/tiendas_db.json (NUEVO)
src/npc.py (NUEVO)
src/pantalla_dialogo.py (NUEVO)
src/pantalla_tienda.py (NUEVO)
src/mapa.py (agregar NPCs al mapa)
```

---

### Fase 10: Opciones y Game Over
**Estado:** ⏳ Después de Fase 9

**Tareas:**
- [ ] Implementar lógica de "Game Over"
  - Si el grupo muere en batalla
  - Teletransporte al último pueblo visitado
  - Penalización (perder 50% del oro, etc.)
- [ ] Crear Menú de Opciones:
  - Resolución de pantalla (800x600, 1024x768, 1280x720)
  - Modo pantalla completa
  - Volumen de música/efectos (si se implementa audio)
  - Controles personalizables
- [ ] Sistema de "último pueblo visitado"
- [ ] Pantalla de Game Over con opción de cargar partida

**Archivos a crear/modificar:**
```
src/pantalla_opciones.py (NUEVO)
src/pantalla_game_over.py (NUEVO)
main.py (detectar game over, agregar menú opciones)
settings.json (guardar configuraciones)
```

---

### Fase 11: Soporte Adicional
**Estado:** ⏳ Después de Fase 10

**Tareas:**
- [ ] Implementar soporte para Gamepad/Mando:
  - Detectar gamepad conectado (pygame.joystick)
  - Mapear botones a teclas existentes:
    - D-Pad → Flechas (↑↓←→)
    - A/B → Enter/ESC
    - X/Y → Teclas adicionales (D, I, etc.)
  - Configuración personalizable de controles
- [ ] Sistema de logros/achievements (opcional)
- [ ] Modo de dificultad (Fácil/Normal/Difícil)
- [ ] New Game+ (opcional)

**Archivos a crear/modificar:**
```
src/input_manager.py (NUEVO - gestionar teclado + gamepad)
src/pantalla_controles.py (NUEVO - configurar controles)
main.py (integrar input_manager)
settings.json (guardar configuración de controles)
```

---

## 📊 PROGRESO POR FASES

| Fase | Nombre | Estado | Progreso |
|------|--------|--------|----------|
| 1-6 | Sistemas Base | ✅ Completado | 100% |
| 7 | Sistema de Habilidades | ✅ Completado | 100% |
| 8 | Gestión de Grupo | ⏳ Pendiente | 0% |
| 9 | NPCs y Mundo | ⏳ Pendiente | 0% |
| 10 | Opciones y Game Over | ⏳ Pendiente | 0% |
| 11 | Soporte Adicional | ⏳ Pendiente | 0% |

**Progreso Total del Proyecto:** ~58% completado (7 de 12 fases totales)

---

=======
>>>>>>> 2b327ff69cadaac90f9843e6d11438e4f982c9ee
## 📝 NOTAS IMPORTANTES

### Chilenismos Eliminados
- ✓ Todo el texto está en español neutro
- ✓ Diálogos profesionales
- ✓ Descripciones claras

### Sistema de Scroll
- ✓ Implementado en batalla (habilidades)
- 🔄 Pendiente en otras ventanas (ver prioridad alta)

### Navegación
- ✓ Flechas izquierda/derecha para ranuras
- ✓ Flechas arriba/abajo para listas
- ✓ Enter para seleccionar
- ✓ ESC o botón "Volver" para regresar

---

## 🎯 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

**Sesión Actual (1-2 horas):**
1. Sistema de scroll completo en todas las pantallas
2. Categorías en inventario
3. Lógica del expansor de ranuras

**Próxima Sesión (2-3 horas):**
4. Conectar habilidades con batalla (ejecución completa)
5. Pantalla de objetos en batalla
6. Testing completo de DOT/HOT

**Sesión Final (1-2 horas):**
7. Pulir interfaz y navegación
8. Sistema de guardado mejorado
9. Testing general del sistema completo

---

## 🔄 ESTADO GENERAL DEL PROYECTO

**Fase Actual:** Fase 7 - Sistema de Habilidades (✅ 100% completado)
**Siguiente Fase:** Fase 8 - Gestión de Grupo
**Progreso Total:** ~75% del proyecto completo

**Arquitectura Actual:**
- ✓ Estructura modular (src/, database/, assets/)
- ✓ Sistema de guardado funcional
- ✓ Batalla con habilidades completas y efectos DOT/HOT
- ✓ Menú de pausa completo
- ✓ Sistema de equipo funcional
- ✓ Sistema de expansor de ranuras funcional
- ✓ Items especiales visibles y funcionales

**Sistemas Completados Hoy:**
1. ✅ Sistema DOT/HOT completamente funcional
2. ✅ Items especiales (expansor) visibles en inventario
3. ✅ 7 habilidades con efectos sobre tiempo funcionando

---

## 📞 REFERENCIA RÁPIDA

**Documentación:**
- `GUIA_COMPLETA_PROYECTO.md` - Documentación completa del proyecto
- `ESTADO_ACTUAL_SISTEMA.md` - Estado actual detallado del código
- `CAMBIOS_SISTEMA_HABILIDADES.md` - Log de cambios del sistema de habilidades
- `SISTEMA_DOT_HOT_COMPLETO.md` - ✨ NUEVO: Documentación completa de efectos DOT/HOT
- `SOLUCION_ITEMS_ESPECIALES_INVISIBLES.md` - ✨ NUEVO: Solución items especiales

**Última actualización:** 16 Nov 2025 - 14:10 UTC
