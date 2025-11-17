# EDITOR DE MAPAS AVANZADO - Funcionalidades Completas

## 🎮 Editor de Mapas CodeVerso RPG

### ✅ FUNCIONALIDADES IMPLEMENTADAS

#### 1. **Zoom con Rueda del Mouse** ✓

- Zoom centrado en la posición del cursor
- Rango: 0.1x hasta 5.0x
- Ajuste suave de la cámara durante el zoom
- Control preciso para trabajar cómodamente

#### 2. **Sistema de Muros Dibujables** ✓

- Modo especial para dibujar áreas de colisión
- Pintar muros arrastrando el mouse
- Visualización clara de zonas no transitables
- Exportación automática a JSON

#### 3. **Sistema de Portales** ✓

- Crear conexiones entre mapas
- **Lista de mapas con thumbnails visuales** (70x40px)
- Preview del mapa destino
- Indica carpeta de origen
- Click para seleccionar origen y destino del portal

#### 4. **Vista de Batalla** ✓

- **Carga automática de fondos** desde `assets/backgrounds/`
- **Thumbnails de fondos** (60x35px)
- **Separación clara: Héroes vs Monstruos**
- **Simulación de ventana UI inferior** (200px de altura)
- **Sprite cloud_batalla.png visible automáticamente**
- Indicadores "← Héroes aquí" y "Monstruos aquí →"
- Líneas de referencia y medidas

#### 5. **Mover Cámara con Arrastre** ✓

- Click izquierdo sin objeto = arrastra el mapa
- Click derecho o central = pan de cámara
- Movimiento fluido con teclado (WASD o flechas)
- Zoom se mantiene durante el movimiento

#### 6. **Carga Correcta de Mapas** ✓

- Búsqueda recursiva en subcarpetas
- Soporta JPG y PNG
- Escala automática al tamaño del juego (1000x600)
- Preview en lista de selección

---

## 📋 CARACTERÍSTICAS ADICIONALES

### **Biblioteca de Sprites Completa**

- ✓ Cofres (redimensionables)
- ✓ NPCs
- ✓ Héroes de mapa
- ✓ Héroes de batalla (separados)
- ✓ Monstruos (separados)
- ✓ Decoraciones

### **Sistema de Edición**

- ✓ Redimensionamiento arrastrando esquinas
- ✓ Selección y movimiento de objetos
- ✓ Duplicación rápida (tecla D)
- ✓ Eliminación (tecla DEL)
- ✓ Sistema de capas (z-index)
- ✓ Historial de uso de sprites

### **Interfaz Visual**

- ✓ Panel izquierdo: Selector de mapas y sprites
- ✓ Panel central: Área de edición con zoom
- ✓ Panel derecho: Propiedades del objeto seleccionado
- ✓ Barra de estado con información en tiempo real
- ✓ Grid con coordenadas
- ✓ Cambios sin guardar indicados

### **Exportación**

- ✓ Guardado automático en JSON
- ✓ Estructura compatible con el juego
- ✓ Preserva todas las propiedades de objetos
- ✓ Ubicación: `src/database/mapas/{carpeta}/{mapa}.json`

---

## 🎯 MODOS DE EDICIÓN

### 1. **Modo Normal** (predeterminado)

- Colocar, mover y editar sprites
- Redimensionar objetos
- Gestión de capas

### 2. **Modo Dibujar Muros**

- Pintar áreas de colisión
- Definir zonas no transitables
- Visualización en tiempo real

### 3. **Modo Portales**

- **Lista visual de todos los mapas**
- **Thumbnails para identificar rápido**
- Crear conexiones entre mapas
- Define origen y destino

### 4. **Modo Vista de Batalla**

- **Preview de fondos de batalla**
- **Visualización de héroes y monstruos**
- **Simulación exacta del espacio UI**
- **cloud_batalla.png visible**
- Posicionamiento preciso de enemigos y aliados

---

## 🔧 CONTROLES

### Ratón

- **Rueda**: Zoom in/out
- **Click izquierdo**: Seleccionar/Mover objeto
- **Click derecho**: Mover cámara (pan)
- **Arrastrar esquinas**: Redimensionar objeto

### Teclado

- **WASD / Flechas**: Mover cámara
- **D**: Duplicar objeto seleccionado
- **DEL**: Eliminar objeto seleccionado
- **Ctrl+S**: Guardar mapa
- **ESC**: Salir

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
RPG/
├── assets/
│   ├── maps/           # Mapas organizados por carpeta
│   ├── sprites/
│   │   ├── cofres/
│   │   ├── npcs/
│   │   ├── heroes/
│   │   │   └── batalla/    # Sprites de héroes para batalla
│   │   │       └── cloud_batalla.png  ← Enlazado automáticamente
│   │   └── monstruos/
│   └── backgrounds/    # Fondos de batalla
│
└── src/database/mapas/ # JSONs exportados
```

---

## 🚀 PRÓXIMAS MEJORAS SUGERIDAS

### Aún pendientes:

- [ ] Sistema de capas visuales (toggle on/off)
- [ ] Atajos de teclado personalizables
- [ ] Copiar/Pegar múltiples objetos
- [ ] Deshacer/Rehacer (Ctrl+Z / Ctrl+Y)
- [ ] Snap to grid opcional
- [ ] Búsqueda de sprites por nombre

---

## 💡 TIPS DE USO

1. **Usa el zoom** para trabajar con precisión en detalles pequeños
2. **Modo batalla** es perfecto para ver cómo se verán los encuentros
3. **Los thumbnails de mapas** ayudan a crear portales rápido
4. **Redimensiona cofres/objetos** arrastrando las esquinas naranjas
5. **Click derecho** para mover la cámara sin seleccionar objetos

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### El editor no inicia

- Verifica que tengas Python 3.8+ instalado
- Instala dependencias: `pip install pygame`

### No veo los sprites

- Verifica que las carpetas `assets/sprites/` existan
- Comprueba que las imágenes sean PNG o JPG

### Los thumbnails no aparecen

- Asegúrate que las rutas sean correctas
- Verifica permisos de lectura en las carpetas

### cloud_batalla.png no aparece

- Debe estar en: `assets/sprites/heroes/batalla/cloud_batalla.png`
- Verifica que sea un PNG válido

---

**Versión**: 2.0 - Editor Profesional
**Última actualización**: 2025-01-17
**Estado**: ⚠️ FUNCIONALIDADES PARCIALMENTE IMPLEMENTADAS

## ❌ PROBLEMAS ACTUALES

### Modo Batalla

- ❌ **No se pueden agregar héroes/monstruos** a la escena
- ❌ **No se pueden mover** los objetos de batalla
- ❌ **No se pueden redimensionar**
- ❌ **Faltan opciones** de cantidad (1-4 héroes, 1-5 monstruos)
- ✅ Vista visual funciona correctamente
- ✅ cloud_batalla.png se muestra

### Modo Portales

- ❌ **No se pueden crear portales** con clicks
- ❌ **No se guardan** en JSON
- ✅ Lista de mapas con thumbnails funciona

### Modo Muros

- ❌ **No se pueden dibujar muros** con clicks
- ❌ **No se guardan** en JSON
- ✅ Modo activado correctamente
