# 📋 TAREAS PENDIENTES - Sistema RPG

## ✅ COMPLETADO

### Fase 7 - Sistema de Habilidades
- ✅ Creado `habilidades_db.json` con pool de habilidades
- ✅ Actualizado sistema de héroes con clases y ranuras
- ✅ Creada `pantalla_habilidades.py` con 4 paneles
- ✅ Implementado sistema de equipar/desequipar habilidades
- ✅ Navegación por teclado entre paneles (↑↓←→)
- ✅ Sistema de scroll visual en descripción de habilidades
- ✅ Botón "Volver" para regresar al menú de pausa
- ✅ Prevención de habilidades duplicadas en ranuras
- ✅ Actualización visual del inventario al equipar/desequipar
- ✅ Integración con sistema de batalla
- ✅ Menú de habilidades en batalla (panel pequeño scrolleable)
- ✅ Navegación entre menús de batalla (Atacar/Habilidades/Objetos)
- ✅ Eliminado menú obsoleto de "Magia"
- ✅ Sistema de scroll visual implementado en batalla

---

## 🔧 TAREAS PENDIENTES

### 1. **SISTEMA DE EXPANSOR DE RANURAS** (CRÍTICO)
**Estado:** ✅ IMPLEMENTADO - ⏳ PENDIENTE DE PRUEBAS

**Completado:**
- ✅ Función `usar_expansor_ranuras(cantidad)` creada en `heroe.py`
- ✅ Lógica integrada en `pantalla_inventario.py`
- ✅ Expansor añadido al inventario inicial de héroes
- ✅ Sistema apilable (+2, +4, +6... según cantidad usada)

**Tareas pendientes:**
- [ ] Probar que el expansor aumenta correctamente las ranuras
- [ ] Verificar que el scroll se adapta a las nuevas ranuras
- [ ] Verificar que las nuevas ranuras se guardan correctamente
- [ ] Probar con múltiples expansores consecutivos

---

### 2. **ORGANIZAR INVENTARIO POR CATEGORÍAS**
**Estado:** ⚠️ NECESITA MEJORA

**Problema actual:**
- Todos los objetos aparecen mezclados en una sola lista
- Difícil de navegar con muchos ítems

**Tareas:**
- [ ] Modificar `pantalla_objetos.py` para mostrar pestañas/categorías:
  - **Consumibles** (Pociones, Elixires, etc.)
  - **Equipo** (Armas, Armaduras, Accesorios)
  - **Especiales** (Expansor de Ranuras, ítems de misión)
  - **Varios** (Otros ítems)
- [ ] Añadir campo `categoria` en `items_db.json`
- [ ] Implementar navegación entre categorías (← → o teclas L/R)
- [ ] Implementar scroll en cada categoría
- [ ] Mostrar contador de ítems por categoría (ej: "Consumibles [12]")

---

### 3. **IMPLEMENTAR SCROLL EN TODAS LAS PANTALLAS**
**Estado:** ⚠️ PARCIALMENTE IMPLEMENTADO

**Pantallas que necesitan scroll visual:**
- [ ] `pantalla_objetos.py` → Inventario (Ya tiene scroll básico, mejorar visual)
- [ ] `pantalla_equipo.py` → Lista de equipo disponible
- [ ] `pantalla_heroes.py` → Lista de héroes (si hay +4)
- [ ] `menu_batalla.py` → Lista de enemigos (si hay +4)
- [ ] Cualquier lista que pueda tener >6 elementos

**Implementar:**
- [ ] Barra de scroll visual (como en `pantalla_habilidades.py`)
- [ ] Indicadores de "más contenido" (▲ arriba, ▼ abajo)
- [ ] Scroll suave con animación

---

### 4. **SISTEMA DOT/HOT EN BATALLA**
**Estado:** ✅ CREADO EN DB, ⚠️ FALTA IMPLEMENTAR LÓGICA

**Habilidades creadas:**
- ✅ "Quemadura" (DOT: daño por turno)
- ✅ "Revitalizar" (HOT: cura HP por turno)
- ✅ "Regeneración de Maná" (HOT: recupera MP por turno)

**Tareas pendientes:**
- [ ] Crear clase `EstadoAlterado` en `heroe.py`:
  - Atributos: tipo, duracion_turnos, potencia, origen
- [ ] Añadir lista `self.estados_alterados = []` en Heroe
- [ ] Crear función `aplicar_dot_hot()` en `pantalla_batalla.py`
- [ ] Procesar estados al inicio/fin de cada turno
- [ ] Mostrar iconos de estados sobre sprites (🔥💚💙)
- [ ] Implementar resistencias/inmunidades
- [ ] Crear animaciones de DOT/HOT
- [ ] Mensajes en batalla: "Cloud recibe 15 de daño por Quemadura"

---

### 5. **SISTEMA AOE (ÁREA DE EFECTO)**
**Estado:** ✅ DEFINIDO EN DB, ⚠️ FALTA IMPLEMENTAR

**Habilidades AOE creadas:**
- ✅ "Fuego en Cadena" (daño a todos los enemigos)
- ✅ "Tormenta de Hielo" (daño AoE + slow)

**Tareas:**
- [ ] Modificar `menu_batalla.py` para detectar habilidades AoE
- [ ] Al usar AoE → NO pedir seleccionar objetivo individual
- [ ] Aplicar efecto a TODOS los enemigos vivos
- [ ] Crear animación de impacto múltiple
- [ ] Mostrar daño individual en cada enemigo
- [ ] Implementar resistencias elementales

---

### 6. **MEJORAS EN BATALLA**
**Estado:** ⚠️ PENDIENTE

**Tareas:**
- [ ] Mostrar iconos de estados alterados sobre sprites
- [ ] Añadir barra de turno visual (quién ataca siguiente)
- [ ] Implementar sistema de velocidad (AGI determina orden)
- [ ] Animaciones de habilidades especiales
- [ ] Efectos de partículas (fuego, hielo, etc.)
- [ ] Sonidos de habilidades (si añadimos audio)

---

### 7. **SISTEMA DE GUARDADO/CARGA**
**Estado:** ⚠️ VERIFICAR

**Tareas:**
- [ ] Verificar que `ranuras_habilidad_max` se guarda correctamente
- [ ] Verificar que `habilidades_activas` se guarda correctamente
- [ ] Verificar que `inventario_habilidades` se guarda correctamente
- [ ] Verificar que expansores usados persisten entre sesiones
- [ ] Probar cargar partidas antiguas (compatibilidad)

---

### 8. **OPTIMIZACIONES Y BUGS**
**Estado:** ⚠️ REVISAR

**Bugs conocidos:**
- [ ] Verificar que ESC funciona en todas las pantallas
- [ ] Revisar colisiones de texto en pantallas pequeñas
- [ ] Optimizar renderizado de scroll (lag con muchos ítems)
- [ ] Verificar navegación con gamepad (si se implementa)

---

## 🎯 FASES FUTURAS (POST-FASE 7)

### Fase 8: Gestión de Grupo
- [ ] Crear 3 héroes adicionales (total: 6 héroes)
- [ ] Pantalla de "Gestión de Grupo"
- [ ] Sistema de grupo activo (4) vs banco (2)
- [ ] Función "Cambiar Líder" (quien camina en el mapa)

### Fase 9: Mundo y NPCs
- [ ] Sistema de NPCs (diálogos)
- [ ] Tiendas (comprar/vender)
- [ ] Misiones secundarias
- [ ] Sistema de ciudades/pueblos

### Fase 10: Opciones y Game Over
- [ ] Menú de Opciones (Resolución, Pantalla completa)
- [ ] Sistema de Game Over (teletransporte a último pueblo)
- [ ] Ajustes de audio (si se añade)

### Fase 11: Soporte Adicional
- [ ] Soporte para gamepad/mando
- [ ] Sistema de logros
- [ ] Modo difícil/fácil
- [ ] New Game+

---

## 📊 PRIORIDADES

### 🔴 ALTA PRIORIDAD (Hacer YA)
1. Arreglar Expansor de Ranuras
2. Organizar Inventario por categorías
3. Implementar scroll visual en todas las pantallas

### 🟡 MEDIA PRIORIDAD (Esta semana)
4. Sistema DOT/HOT en batalla
5. Sistema AOE funcional
6. Verificar guardado/carga

### 🟢 BAJA PRIORIDAD (Cuando se pueda)
7. Mejoras visuales en batalla
8. Optimizaciones de rendimiento

---

## 📝 NOTAS

- El sistema de habilidades base está COMPLETO y funcional
- La navegación por teclado funciona bien
- El scroll visual es elegante y profesional
- Falta pulir detalles de usabilidad
- El código está bien estructurado para expansiones futuras

---

**Última actualización:** 2025-11-15
**Fase actual:** 7 (Sistema de Habilidades) - 90% completo
