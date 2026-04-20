# Cambios en Sprite Sheet Editor

## ✅ Cambios Realizados (ACTUALIZADOS)

### 1. **Ventana más pequeña (800x600)**
   - Cambiada resolución de 1400x900 a 800x600
   - La ventana ya no ocupará toda la pantalla al iniciar
   - Más cómodo para trabajar en laptops y monitores pequeños

### 2. **Modo Pantalla Completa**
   - Presiona **F** para entrar/salir de pantalla completa
   - Nuevo botón "Fullscreen (F)" en el panel de controles
   - Los paneles se ajustan automáticamente al cambiar de modo

### 3. **Ventana Redimensionable**
   - Ahora puedes ajustar el tamaño de la ventana arrastrando los bordes
   - Los paneles se adaptan automáticamente al nuevo tamaño
   - La interfaz es responsive y se reorganiza correctamente

### 4. **Redimensionamiento de Selecciones MEJORADO** ⭐
   - **AHORA SÍ FUNCIONA CORRECTAMENTE**
   - Tolerancia aumentada de 8px a 15px para detectar bordes más fácilmente
   - Corregido: ahora toma en cuenta el offset_x y offset_y (pan de cámara)
   - Funciona correctamente con zoom y pan
   - Acerca el cursor a los bordes o esquinas de un rectángulo
   - El cursor cambiará para indicar que puedes redimensionar:
     - ↔ Izquierda/Derecha: Bordes laterales
     - ↕ Arriba/Abajo: Bordes superior/inferior
     - ↖↘ Esquinas diagonal
     - ↗↙ Esquinas diagonal inversa
   - Arrastra para cambiar el tamaño
   - Validación para que no salga de los límites del spritesheet

### 5. **Preview Reubicado** ⭐
   - **La imagen ya no se corta**
   - Orden cambiado: primero muestra la info (Tamaño, Pos)
   - Luego debajo muestra la imagen del sprite
   - Agregado fondo de cuadrícula para ver transparencias
   - El preview se ajusta al espacio disponible
   - Escalado inteligente hasta 3x si el sprite es muy pequeño

### 6. **Paneles más compactos**
   - Panel de control reducido de 300px a 200px
   - Panel de preview reducido de 300px a 200px
   - Botones más pequeños pero funcionales
   - Mejor uso del espacio en pantalla

### 7. **Corrección del error "subsurface rectangle outside"**
   - Agregado método `get_rect_valido()` para validar límites
   - Todas las operaciones de subsurface ahora validan límites
   - Ya no habrá crashes al seleccionar áreas fuera del spritesheet

## 🎮 Controles Actualizados

| Tecla/Acción | Función |
|--------------|---------|
| **Arrastrar imagen** | Cargar spritesheet |
| **Click + Arrastrar (canvas)** | Crear nueva selección |
| **Arrastrar bordes/esquinas** | ⭐ Redimensionar selección (15px tolerancia) |
| **Click derecho en selección** | Eliminar selección |
| **Click derecho + arrastrar** | Pan de cámara |
| **Scroll (en canvas)** | Zoom in/out |
| **Scroll (en lista)** | Desplazar lista de sprites |
| **F** | Pantalla completa |
| **S** | Guardar sprite actual |
| **E** | Exportar todos marcados |
| **G** | Toggle grid |
| **DEL** | Eliminar selección |
| **CTRL+Z** | Deshacer |
| **CTRL+Y** | Rehacer |
| **ESC** | Salir |

## 📝 Notas Técnicas

- La ventana detecta automáticamente eventos de redimensionamiento (VIDEORESIZE)
- Los botones y controles se reposicionan dinámicamente
- El área del spritesheet calcula su ancho basado en el tamaño de ventana
- Todas las referencias a ANCHO y ALTO fijas fueron reemplazadas por valores dinámicos
- **get_borde_cercano()** ahora recibe offset_x, offset_y, zoom para calcular correctamente

## 🧪 Para Probar

1. Ejecuta `ejecutar_sprite_editor_simple.bat`
2. La ventana debe iniciar en 800x600
3. Carga un spritesheet (arrastra o botón Cargar)
4. Crea una selección (click + arrastrar)
5. **Acerca el cursor a los bordes del rectángulo** - debería cambiar de forma
6. **Arrastra el borde** para redimensionar
7. Verifica que el preview muestra primero la info y luego la imagen completa
8. Prueba zoom y pan, y redimensiona de nuevo
9. Prueba F para pantalla completa
10. Prueba redimensionar la ventana

## ❗ Solución a Problemas Comunes

**"No puedo redimensionar"**
- Acércate MÁS a los bordes (15px de tolerancia)
- El cursor debe cambiar de forma antes de arrastrar
- Asegúrate de no estar en modo pan (no tengas click derecho presionado)

**"El preview se corta"**
- Esto ya está solucionado en esta versión
- La info aparece primero, luego la imagen debajo
- Si la ventana es muy pequeña, agrándala o usa pantalla completa (F)
