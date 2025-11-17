# 🎮 GUÍA DE USO - EDITORES RPG

## 📋 TABLA DE CONTENIDOS
1. [Editor de Mapas Avanzado](#editor-de-mapas-avanzado)
2. [Sprite Sheet Editor](#sprite-sheet-editor)
3. [Atajos de Teclado](#atajos-de-teclado)

---

## 🗺️ EDITOR DE MAPAS AVANZADO

### Ejecutar
```bash
python editor_mapa_avanzado.py
```
o doble click en `ejecutar_editor_avanzado.bat`

### Funcionalidades

#### 1. **Navegación**
- **Zoom**: Rueda del mouse (zoom centrado en cursor)
- **Pan**: Click medio o derecho + arrastrar
- **Grid**: Tecla `H` para mostrar/ocultar

#### 2. **Cargar y Editar Mapas**
- Panel izquierdo: Click en un mapa para cargarlo
- Los mapas se cargan desde `assets/maps/`
- Se escalan automáticamente a 1280x720

#### 3. **Añadir Objetos**
- **Botones superiores**: Cofres, NPCs, Héroes, Monstruos
- Click en un sprite del panel izquierdo para añadirlo
- El objeto aparece en el centro de la vista
- Arrastra para mover, arrastra esquinas rojas para redimensionar

#### 4. **Sistema de Muros** 🆕
1. Click en botón **"Muros"**
2. Click en el mapa para añadir puntos
3. Continúa haciendo click para crear el camino
4. **ENTER**: Terminar muro abierto
5. **C**: Cerrar muro (polígono cerrado)
6. **ESC**: Cancelar

**Uso**: Definir áreas de colisión para el juego

#### 5. **Sistema de Portales** 🆕
1. Click en botón **"Portales"**
2. Click para marcar el **origen** del portal
3. Click para marcar el **destino** del portal
4. **ENTER**: Completar portal
5. **ESC**: Cancelar

**Uso**: Crear conexiones entre diferentes áreas del mapa

#### 6. **Guardar y Cargar**
- **G**: Guardar mapa actual
- Los datos se guardan en `src/database/mapas/{carpeta}/{mapa}.json`
- Incluye: objetos, muros, portales

### Controles Completos

| Tecla/Mouse | Acción |
|-------------|--------|
| Rueda Mouse | Zoom in/out |
| Click Medio/Derecho | Mover cámara |
| Click Izquierdo | Seleccionar/Arrastrar objeto |
| G | Guardar mapa |
| H | Toggle grid |
| D | Duplicar objeto seleccionado |
| DELETE | Eliminar objeto seleccionado |
| ENTER | Terminar muro/portal |
| C | Cerrar muro (polígono) |
| ESC | Salir o cancelar acción |

---

## 🎨 SPRITE SHEET EDITOR

### Ejecutar
```bash
python sprite_sheet_editor.py
```
o doble click en `ejecutar_sprite_editor.bat`

### Funcionalidades

#### 1. **Cargar Spritesheet**
- **Arrastra** un archivo de imagen (.png, .jpg, .bmp, .gif) desde tu explorador
- El spritesheet se carga automáticamente

#### 2. **Navegación** 🆕
- **Zoom**: Rueda del mouse (zoom centrado en cursor)
- **Pan**: Click medio o derecho + arrastrar
- **Grid**: Tecla `G` para mostrar/ocultar

#### 3. **Seleccionar Sprites**
- **Click Izquierdo + Arrastrar**: Seleccionar área rectangular
- **CTRL + Click**: Hacer múltiples selecciones
- Las selecciones se muestran en el panel de preview

#### 4. **Nombrar y Guardar**
1. Selecciona un área del spritesheet
2. Presiona **N** o click en el campo de nombre
3. Escribe el nombre del sprite
4. Selecciona la categoría (Héroes, Monstruos, Cofres, NPCs)
5. Presiona **S** para guardar el sprite actual
6. Presiona **E** para exportar todos los sprites seleccionados

**Carpetas de salida**:
- Héroes Batalla: `assets/sprites/heroes/batalla/`
- Héroes Mapa: `assets/sprites/heroes/mapa/`
- Monstruos: `assets/sprites/monstruos/`
- Cofres: `assets/sprites/cofres y demas/`
- NPCs: `assets/sprites/npcs/`

#### 5. **Historial**
- **CTRL+Z**: Deshacer última acción
- **CTRL+Y**: Rehacer acción deshecha

### Controles Completos

| Tecla/Mouse | Acción |
|-------------|--------|
| Arrastra imagen | Cargar spritesheet |
| Rueda Mouse | Zoom in/out |
| Click Medio/Derecho | Mover cámara |
| Click Izquierdo + Arrastrar | Seleccionar área |
| CTRL + Click | Múltiples selecciones |
| N | Nombrar sprite seleccionado |
| S | Guardar sprite actual |
| E | Exportar todos |
| G | Toggle Grid |
| CTRL+Z | Deshacer |
| CTRL+Y | Rehacer |
| DELETE | Eliminar selección |
| ESC | Salir |

---

## ⌨️ ATAJOS DE TECLADO

### Editor de Mapas

```
NAVEGACIÓN:
  Rueda Mouse    Zoom in/out
  Click Medio    Mover cámara
  Click Derecho  Mover cámara
  H              Toggle grid

EDICIÓN:
  Click Izq      Seleccionar objeto
  Arrastrar      Mover objeto
  Esquinas       Redimensionar objeto
  D              Duplicar seleccionado
  DELETE         Eliminar seleccionado

MUROS:
  Click          Añadir punto
  ENTER          Terminar muro
  C              Cerrar muro (polígono)
  ESC            Cancelar

PORTALES:
  Click          Origen/Destino
  ENTER          Completar portal
  ESC            Cancelar

ARCHIVO:
  G              Guardar mapa
  ESC            Salir
```

### Sprite Sheet Editor

```
NAVEGACIÓN:
  Rueda Mouse    Zoom in/out
  Click Medio    Mover cámara
  Click Derecho  Mover cámara
  G              Toggle grid

SELECCIÓN:
  Click + Drag   Seleccionar área
  CTRL + Click   Múltiples selecciones
  DELETE         Eliminar selección

EDICIÓN:
  N              Nombrar sprite
  S              Guardar sprite actual
  E              Exportar todos
  CTRL+Z         Deshacer
  CTRL+Y         Rehacer

ARCHIVO:
  Drag & Drop    Cargar spritesheet
  ESC            Salir
```

---

## 📝 CONSEJOS Y TRUCOS

### Editor de Mapas

1. **Zoom preciso**: Coloca el cursor sobre el objeto que quieres ver de cerca antes de hacer zoom
2. **Muros eficientes**: Usa pocos puntos para muros simples, más puntos para formas complejas
3. **Portales**: El origen y destino pueden estar en el mismo mapa
4. **Organización**: Usa nombres descriptivos para portales (ej: "Entrada Castillo")

### Sprite Sheet Editor

1. **Grid alineado**: Activa el grid (G) para alinear selecciones
2. **Zoom primero**: Haz zoom antes de seleccionar sprites pequeños
3. **Múltiples sprites**: Usa CTRL+Click para cortar varios sprites de una vez
4. **Nombres únicos**: Usa nombres descriptivos (ej: "dragon_rojo_ataque_1")

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### "No se carga el mapa"
- Verifica que la imagen esté en `assets/maps/`
- Formatos soportados: JPG, PNG
- Haz click en "↻ Actualizar Lista"

### "No se ven los sprites"
- Verifica que los sprites estén en las carpetas correctas
- Haz click en "↻ Actualizar Lista" en el panel
- Revisa la consola para errores

### "El zoom no funciona"
- Asegúrate de que el cursor esté dentro del área del mapa/spritesheet
- No funciona si el cursor está sobre los paneles laterales

### "Los muros no se guardan"
- Presiona ENTER o C para terminar el muro antes de guardar
- Muros sin terminar (en progreso) no se guardan

---

## 📚 ESTRUCTURA DE ARCHIVOS

```
RPG/
├── assets/
│   ├── maps/           # Imágenes de mapas
│   │   ├── mundo/
│   │   ├── castillo/
│   │   └── ...
│   └── sprites/        # Sprites organizados
│       ├── heroes/
│       ├── monstruos/
│       ├── cofres y demas/
│       └── npcs/
├── src/
│   └── database/
│       └── mapas/      # JSONs de mapas
│           ├── mundo/
│           ├── castillo/
│           └── ...
├── editor_mapa_avanzado.py
├── sprite_sheet_editor.py
└── GUIA_USO_EDITORES.md (este archivo)
```

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### Para Crear un Mapa Completo:

1. **Preparar assets**
   - Imagen del mapa en `assets/maps/`
   - Sprites necesarios en `assets/sprites/`

2. **Cargar y editar**
   - Abrir Editor de Mapas
   - Cargar el mapa
   - Añadir NPCs, cofres, etc.

3. **Definir colisiones**
   - Activar modo "Muros"
   - Dibujar muros alrededor de obstáculos
   - Cerrar muros con C

4. **Crear conexiones**
   - Activar modo "Portales"
   - Crear portales entre áreas
   - Nombrar portales descriptivamente

5. **Guardar**
   - Presionar G para guardar
   - Verificar JSON en `src/database/mapas/`

### Para Organizar Sprites:

1. **Obtener spritesheet**
   - Descargar o crear spritesheet

2. **Abrir en editor**
   - Arrastrar imagen al Sprite Sheet Editor
   - Hacer zoom si es necesario

3. **Cortar sprites**
   - Seleccionar cada sprite individualmente
   - O usar CTRL+Click para múltiples

4. **Nombrar y categorizar**
   - Nombrar cada sprite (N)
   - Seleccionar categoría correcta
   - Guardar (S) o exportar todos (E)

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de finalizar un mapa:

- [ ] Todos los objetos están en su posición correcta
- [ ] Los muros cubren todas las áreas de colisión
- [ ] Los portales están conectados correctamente
- [ ] El mapa se guardó (G)
- [ ] Se probó en el juego

Antes de cerrar el Sprite Editor:

- [ ] Todos los sprites están nombrados
- [ ] Las categorías son correctas
- [ ] Los sprites se exportaron (E)
- [ ] Los archivos están en las carpetas correctas

---

**¡Listo para crear tu RPG! 🎮✨**
