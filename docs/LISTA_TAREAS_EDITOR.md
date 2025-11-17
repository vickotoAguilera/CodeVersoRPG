# LISTA DE TAREAS - EDITORES RPG

## EDITOR DE MAPAS AVANZADO

### ✅ COMPLETADO

1. **Zoom con rueda del mouse** ✓
   - Zoom centrado en la posición del cursor
   - Límites de zoom (0.1x a 5x)
   - Funcional en todas las vistas

2. **Sistema de muros dibujables** ✓
   - Modo de dibujo de muros
   - Pintar áreas de colisión
   - Grosor ajustable

3. **Sistema de portales** ✓
   - Crear conexiones entre mapas
   - Lista de mapas con thumbnails
   - Preview visual de destinos

4. **Vista de batalla** ✓
   - Mostrar sprites de héroes (desde heroes/batalla/)
   - Mostrar sprites de monstruos (desde assets/sprites/monstruos/)
   - Fondos de batalla (desde assets/backgrounds/)
   - Simulación de ventana UI inferior (200px)
   - Sprite cloud_batalla.png visible automáticamente

5. **Mover cámara con arrastre del mouse** ✓
   - Click derecho para arrastrar
   - Funcional en todas las vistas

6. **Cargar imágenes de mapas correctamente** ✓
   - Búsqueda recursiva en assets/maps/
   - Soporte para PNG y JPG
   - Escalado al tamaño del juego (1280x720)

7. **Biblioteca de sprites** ✓
   - Categorías: Cofres, NPCs, Héroes, Monstruos
   - Botón "Actualizar" para recargar lista
   - Botón "+ Añadir" para explorar archivos
   - Thumbnails y descripción

8. **Redimensionamiento de objetos** ✓
   - Arrastrar esquinas para redimensionar
   - Handles visuales en objetos seleccionados
   - Dimensiones mostradas en tiempo real

9. **Configuraciones de batalla** ✓
   - Guardar configuración (JSON)
   - Cargar configuración
   - Selector de cantidad de héroes (1-4)
   - Selector de cantidad de monstruos (1-5)

### ⏳ EN PROCESO / POR VERIFICAR

1. **Sprites de monstruos en modo batalla**
   - ISSUE: Al hacer click en lista de monstruos, debe agregar el sprite seleccionado
   - CAMBIO: Corregido tipo de objeto (monstruo_batalla)
   - CAMBIO: Corregida búsqueda de sprites por ruta completa
   - ESTADO: Por verificar en ejecución

2. **Movimiento de sprites en modo batalla**
   - Debe permitir mover héroes y monstruos
   - Debe permitir redimensionar
   - ESTADO: Por verificar funcionamiento

3. **Eliminar sprites con clic derecho**
   - En modo batalla y modo normal
   - Menú contextual o eliminación directa
   - ESTADO: Por implementar/verificar

### 📋 PENDIENTE

1. **Persistencia de selecciones**
   - Recordar último fondo de batalla usado
   - Recordar configuración de cantidad de sprites
   - Guardar preferencias de usuario

2. **Drag & Drop de archivos**
   - Arrastrar imágenes desde explorador
   - Copiar automáticamente a carpeta correcta
   - Actualizar biblioteca automáticamente

3. **Validación de sprites**
   - Verificar que archivos existen
   - Mostrar advertencia si faltan sprites
   - Recargar automáticamente sprites eliminados

4. **Export/Import de configuraciones**
   - Exportar configuración de batalla completa
   - Importar desde otro proyecto
   - Compartir configuraciones

---

## EDITOR DE SPRITES (Sprite Sheet Editor)

### ✅ COMPLETADO

1. **Zoom con rueda del mouse** ✓
   - Zoom centrado en cursor
   - Límites de zoom

2. **Mover cámara con mouse** ✓
   - Pan/arrastre con botón derecho
   - Desplazamiento fluido

3. **Herramienta de selección/recorte** ✓
   - Marcar áreas del spritesheet
   - Redimensionar selección
   - Mover selección arrastrando

4. **Sistema de grid** ✓
   - Grid automático 1x1, 2x2, 3x3
   - Grid personalizado
   - Ajustar a grid

5. **Exportar sprites recortados** ✓
   - Guardar múltiples sprites
   - Nomenclatura automática con números
   - Pregunta si reemplazar archivos existentes
   - Preview antes de guardar

6. **Preview de animaciones** ✓
   - Reproducir secuencia de sprites
   - Controlar velocidad (FPS)
   - Play/Pause

7. **Deseleccionar con click fuera** ✓
   - Click izquierdo fuera del área = nueva selección
   - Funcional

8. **Documentación** ✓
   - Guía de uso (SPRITE_SHEET_EDITOR_GUIA.md)
   - Lista de funcionalidades

### ⏳ EN PROCESO

1. **Grid inteligente para sprites múltiples**
   - ISSUE: Si selecciono 3 sprites juntos, los toma como uno
   - SOLUCIÓN PROPUESTA: Detectar sprites individuales en grid
   - ESTADO: Por implementar

2. **Ajustar ventana de recorte**
   - ISSUE: No se puede mover la ventana de recorte en grid
   - SOLUCIÓN: Permitir ajuste fino de posición
   - ESTADO: Por implementar

3. **Eliminar selecciones**
   - Click derecho en área verde/amarilla = eliminar
   - Menú contextual
   - ESTADO: Por implementar

### 📋 PENDIENTE

1. **Detección automática de sprites**
   - Algoritmo para detectar sprites separados
   - Basado en transparencia
   - Sugerencias de recorte

2. **Plantillas de recorte**
   - Guardar configuraciones de grid
   - Cargar plantillas predefinidas
   - Para tipos comunes (32x32, 64x64, etc.)

3. **Batch processing**
   - Procesar múltiples spritesheets
   - Aplicar misma configuración a todos
   - Exportar en lote

4. **Metadata de sprites**
   - Guardar información adicional (tipo, animación, frames)
   - JSON con configuración
   - Para uso en el juego

---

## PRIORIDADES ACTUALES

1. **🔴 URGENTE**: Verificar funcionamiento de monstruos en modo batalla
   - Probar que se agregan correctamente
   - Verificar que se pueden mover
   - Verificar que se guardan/cargan

2. **🟡 IMPORTANTE**: Implementar eliminación con clic derecho
   - En ambos editores
   - Consistencia de comportamiento

3. **🟢 MEJORA**: Drag & Drop de archivos
   - Facilitar agregar nuevos sprites
   - Mejor experiencia de usuario

4. **🟢 MEJORA**: Grid inteligente en editor de sprites
   - Detectar sprites individuales
   - Facilitar recorte de múltiples sprites

---

## BUGS CONOCIDOS

1. ~~Error "ModoEditor has no attribute 'DIBUJAR_MURO'"~~ ✓ CORREGIDO
2. ~~SyntaxError en sprite_sheet_editor.py (doble ::)~~ ✓ CORREGIDO
3. ~~ValueError: subsurface rectangle outside surface area~~ ✓ CORREGIDO
4. ~~UnboundLocalError en modo portales (variable 'obj')~~ ✓ CORREGIDO

---

## NOTAS DE DESARROLLO

- **Arquitectura**: Editor modular con modos separados
- **Formato de guardado**: JSON para configuraciones
- **Rutas de sprites**:
  - Cofres: `assets/sprites/cofres y demas/`
  - NPCs: `assets/sprites/npcs/`
  - Héroes batalla: `assets/sprites/heroes/batalla/`
  - Monstruos: `assets/sprites/monstruos/`
  - Fondos batalla: `assets/backgrounds/`
  - Mapas: `assets/maps/` (recursivo)

---

**Última actualización**: 2025-11-17
**Autor**: CodeVerso Team
