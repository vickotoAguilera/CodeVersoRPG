# ESTADO ACTUAL DE LOS EDITORES - 17 NOV 2025

## 🎮 EDITOR DE MAPAS AVANZADO

### ✅ FUNCIONANDO
1. **Zoom con rueda del mouse** ✓
   - Zoom centrado en cursor
   - Límites 0.1x - 5x

2. **Sistema de muros** ✓
   - Modo dibujo de muros
   - Áreas de colisión

3. **Biblioteca de sprites** ✓
   - Cofres, NPCs, Héroes, Monstruos
   - Botones Actualizar/Añadir

4. **Redimensionamiento** ✓
   - Arrastrar esquinas

5. **Pan/Arrastre con mouse** ✓

### ⚠️ PROBLEMAS ACTUALES

#### 1. **MODO BATALLA - Monstruos NO se agregan**
**Síntomas:**
- Al hacer click en lista de monstruos no aparecen en pantalla
- Solo aparece sprite "cloud_batalla.png"
- Mensaje: "No hay monstruos disponibles"
- Carpeta correcta: `assets/sprites/monstruos/` (ej: dragon_prueba.png)

**Causa probable:**
- Búsqueda de archivos incorrecta
- Ruta de sprites mal configurada
- Filtrado incorrecto en biblioteca_sprites

#### 2. **NO se pueden mover sprites en modo batalla**
- Héroes y monstruos deben ser movibles
- Deben ser redimensionables
- Actualmente se quedan fijos

#### 3. **Falta eliminar con clic derecho**
- No hay opción para eliminar sprites colocados
- Necesario en modo batalla y modo normal

#### 4. **Lista de monstruos vacía**
- La carpeta `assets/sprites/monstruos/` SÍ tiene archivos
- Pero no se cargan/muestran en panel izquierdo

### 📋 PENDIENTE DE IMPLEMENTAR

1. **Botones cantidad de sprites**
   - Selector 1-4 héroes
   - Selector 1-5 monstruos
   - Opciones visuales para configurar

2. **Guardar/Cargar configuraciones**
   - Implementado pero necesita testing
   - Archivo: `src/database/batalla_config.json`

3. **Preview de fondos de batalla**
   - Cargar desde `assets/backgrounds/`
   - Thumbnails en panel

4. **Simulación ventana UI**
   - Mostrar zona de 200px inferior
   - Ver espacio real disponible

---

## 🖼️ EDITOR DE SPRITES

### ✅ FUNCIONANDO

1. **Zoom con rueda** ✓
2. **Pan con botón derecho** ✓ (ANTES TENÍA PROBLEMA)
3. **Selección de áreas** ✓
4. **Sistema de grid** ✓ (1x1, 2x2, 3x3)
5. **Guardar múltiples sprites** ✓
6. **Nomenclatura automática** ✓ (nombre_1, nombre_2, etc.)
7. **Reemplazar archivos** ✓ (pregunta antes)
8. **Preview de animaciones** ✓
9. **Deseleccionar con click fuera** ✓

### ⚠️ PROBLEMAS RECIENTES (RESUELTOS?)

1. ~~Error: "subsurface rectangle outside surface area"~~ ✓
2. ~~No se puede mover en pantalla con click derecho~~ ✓
3. ~~No reconoce grid de 3 sprites~~ - PENDIENTE VERIFICAR

### 📋 PENDIENTE

1. **Grid inteligente**
   - Si selecciono 3 sprites juntos, separarlos automáticamente
   - Actualmente los toma como uno solo

2. **Mover ventana de recorte en grid**
   - Ajustar posición fina del grid
   - Actualmente "pesca" imagen siguiente

3. **Eliminar selecciones con clic derecho**
   - En áreas verdes/amarillas
   - Menú contextual

---

## 🔴 PRIORIDAD CRÍTICA

### 1. ARREGLAR MODO BATALLA - MONSTRUOS
**Objetivo:** Que al hacer click en un monstruo de la lista, aparezca en pantalla

**Pasos necesarios:**
1. Verificar que `cargar_biblioteca_sprites()` encuentra archivos en `assets/sprites/monstruos/`
2. Verificar que `crear_objeto_batalla()` usa la ruta correcta
3. Agregar logs de debug para ver qué está pasando
4. Confirmar que la imagen se carga con `cache_imagen()`

### 2. PERMITIR MOVER/REDIMENSIONAR EN BATALLA
**Objetivo:** Poder arrastrar y redimensionar héroes y monstruos colocados

**Necesario:**
- Detectar clicks en sprites de batalla
- Permitir arrastre
- Mostrar handles de redimensionamiento
- Funcione igual que en modo normal

### 3. ELIMINAR SPRITES CON CLIC DERECHO
**Objetivo:** Menú contextual o eliminación directa

**Implementación:**
- Click derecho en sprite → mostrar opción "Eliminar"
- O eliminación directa (más simple)
- Aplicar en ambos editores

---

## 📊 ANÁLISIS DEL CÓDIGO

### Archivos principales:
- `editor_mapa_avanzado.py` (1723 líneas)
- `sprite_sheet_editor.py` (1171 líneas)

### Estructura del editor de mapas:
```
Clase EditorMapas:
  - modo_actual: str (mapas/cofres/npcs/héroes/monstruos/batalla)
  - modo_editor: ModoEditor (NORMAL/DIBUJAR_MUROS/CREAR_PORTAL/VISTA_BATALLA)
  - biblioteca_sprites: Dict[str, List[SpriteInfo]]
  - objetos: List[ObjetoMapa]
  - cache_imagenes: Dict[str, pygame.Surface]
```

### Flujo de agregar monstruo:
1. Usuario hace click en panel izquierdo (lista monstruos)
2. `manejar_clicks_panel_izquierdo()` detecta click
3. Llama a `crear_objeto_batalla(sprite_info, "monstruo")`
4. Crea `ObjetoMapa` tipo "monstruo_batalla"
5. Agrega a `self.objetos`
6. Debe dibujarse en `dibujar()` → `dibujar_mapa()`

### Problema identificado:
- En línea 1617-1627: El código SÍ maneja clicks en monstruos
- Llama a `crear_objeto_batalla(sprite, "monstruo")`
- PERO: Puede que `biblioteca_sprites["monstruos"]` esté vacía
- VERIFICAR: `cargar_biblioteca_sprites()` método

---

## 🛠️ ACCIONES INMEDIATAS

1. **Agregar logging extensivo**
   - Ver qué archivos encuentra en carpeta monstruos
   - Ver si se agregan a biblioteca_sprites
   - Ver si se crean objetos correctamente
   - Ver si se dibujan en pantalla

2. **Verificar rutas**
   - Confirmar que `assets/sprites/monstruos/` es la ruta correcta
   - Ver si usa ruta absoluta o relativa
   - Confirmar que dragon_prueba.png existe

3. **Testing paso a paso**
   - Ejecutar editor
   - Ir a modo batalla
   - Ver console para mensajes debug
   - Hacer click en botón "Actualizar" monstruos
   - Ver si aparecen en lista
   - Hacer click en uno
   - Ver si aparece en pantalla

---

## 📝 NOTAS

- Los errores 404 mencionados pueden ser de conectividad, no del código
- El sprite_sheet_editor.py está funcional según última actualización
- La mayoría de funcionalidades básicas están implementadas
- Falta testing y depuración en modo batalla

**Última actualización:** 17 NOV 2025 18:50
