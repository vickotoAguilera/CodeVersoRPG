# 📋 Editor Unificado - Manual Completo

## 🎯 Índice

1. [¿Qué es el Editor Unificado?](#qué-es)
2. [Características Principales](#características)
3. [Inicio Rápido](#inicio-rápido)
4. [Interfaz](#interfaz)
5. [Navegación](#navegación)
6. [Capas y Visibilidad](#capas)
7. [Selección de Elementos](#selección)
8. [Movimiento y Edición](#movimiento)
9. [Copiar y Pegar](#copiar-pegar)
10. [Grid y Snap](#grid-snap)
11. [Validación](#validación)
12. [Hot-Reload](#hot-reload)
13. [Exportación](#exportación)
14. [Controles Completos](#controles)
15. [Flujo de Trabajo](#flujo-trabajo)
16. [Relación con Editores Específicos](#relación-editores)
17. [Resolución de Problemas](#problemas)

---

## 🎯 ¿Qué es el Editor Unificado? {#qué-es}

El **Editor Unificado** es una herramienta visual que te permite ver y manipular **TODOS** los elementos de un mapa en una sola vista:

- 🧱 **Muros** (colisiones)
- 🌀 **Portales** (teleports)
- 👾 **Spawns** (zonas de monstruos)
- 📦 **Cofres** (tesoros)
- 🧍 **NPCs** (próximamente)
- 🎯 **Eventos** (próximamente)

### ¿Para qué sirve?

✅ **Ver todo junto** - Ya no necesitas abrir 4 editores diferentes  
✅ **Organizar espacialmente** - Mueve, alinea, redimensiona todo  
✅ **Detectar problemas** - Superposiciones, elementos fuera del mapa  
✅ **Trabajar más rápido** - Copia elementos entre distintos tipos  
✅ **Sincronización automática** - Los cambios se reflejan en todos los editores

---

## ✨ Características Principales {#características}

### FASE 1: Vista y Edición Básica ✅

- ✅ Vista multi-capa con colores por tipo
- ✅ Toggle de visibilidad por capa
- ✅ Movimiento de elementos (arrastrar)
- ✅ Redimensionamiento (arrastrar bordes)
- ✅ Zoom con rueda del mouse
- ✅ Pan con click derecho + arrastrar
- ✅ Auto-carga del primer mapa disponible
- ✅ Guardado manual (Ctrl+G) y automático (ESC)

### FASE 2: Productividad ✅

- ✅ Copiar/Pegar elementos (Ctrl+C/Ctrl+V)
- ✅ Selección múltiple (Ctrl+Click)
- ✅ Seleccionar todos (Ctrl+A)
- ✅ Movimiento en grupo
- ✅ Eliminación múltiple (DEL)
- ✅ Info en tiempo real (hover)

### FASE 3: Avanzado ✅

- ✅ Grid visual (toggle con G)
- ✅ Snap to grid (toggle con S)
- ✅ Hot-reload automático (cada 2 segundos)
- ✅ Validación de elementos (V)
- ✅ Exportación de screenshots (E)
- ✅ Detección de superposiciones
- ✅ Detección de elementos fuera del mapa

---

## 🚀 Inicio Rápido {#inicio-rápido}

### Ejecutar el Editor

```bash
# Método 1: Archivo .bat
ejecutar_editor_unificado.bat

# Método 2: Python directo
python editor_unificado.py
```

### Primeros Pasos

1. **El editor auto-carga el primer mapa** al iniciar
2. **Mueve la vista** con click derecho + arrastrar
3. **Haz zoom** con la rueda del mouse
4. **Click izquierdo** para seleccionar elementos
5. **Arrastra** para mover elementos
6. **Presiona H** para ver la ayuda completa

---

## 🖼️ Interfaz {#interfaz}

La interfaz se divide en **2 áreas**:

### 1. Panel Lateral Izquierdo (300px)

```
┌─────────────────────┐
│ Editor Unificado    │  ← Título
│ Mapa: ciudad_01     │  ← Mapa actual
├─────────────────────┤
│ CAPAS:              │
│ ☑ Muros (12)    🟥  │  ← Toggle + Color
│ ☑ Portales (3)  🟦  │
│ ☑ Spawns (5)    🟩  │
│ ☑ Cofres (8)    🟧  │
│ ☐ NPCs (0)      🟪  │
├─────────────────────┤
│ CONTROLES:          │
│ H: Ayuda            │
│ G: Grid/Guardar     │
│ S: Snap             │
│ I: Info             │
│ V: Validar          │
│ E: Exportar         │
└─────────────────────┘
```

### 2. Viewport (Resto de la pantalla)

- Muestra el mapa de fondo
- Dibuja todos los elementos visibles
- Permite interactuar con elementos

---

## 🎮 Navegación {#navegación}

### Mover la Vista (Pan)

```
Click Derecho + Arrastrar = Mover mapa
```

**Ejemplo:** Mantén presionado el botón derecho y arrastra para explorar el mapa.

### Zoom

```
Rueda Arriba   = Acercar (zoom in)
Rueda Abajo    = Alejar (zoom out)
```

**Rango:** 0.25x a 3.0x  
**Tip:** Zoom sobre el área que quieres ver con detalle.

### Reset Vista

Si pierdes el mapa de vista:

1. Presiona **ESC** para cerrar
2. Vuelve a abrir el editor (auto-centra)

---

## 📂 Capas y Visibilidad {#capas}

### Colores por Tipo

Cada tipo de elemento tiene un color distintivo:

| Tipo     | Color      | Hex     |
| -------- | ---------- | ------- |
| Muros    | 🟥 Rojo    | #FF6464 |
| Portales | 🟦 Azul    | #6496FF |
| Spawns   | 🟩 Verde   | #64FF96 |
| Cofres   | 🟧 Naranja | #FFA500 |
| NPCs     | 🟪 Morado  | #C864FF |

### Toggle de Capas

**Click en el checkbox** del panel lateral para mostrar/ocultar una capa completa.

```
☑ Muros (12)    → Visibles
☐ NPCs (0)      → Ocultos
```

**Beneficios:**

- Reducir clutter visual
- Enfocarte en un tipo específico
- Facilitar selección

---

## 🎯 Selección de Elementos {#selección}

### Selección Simple

```
Click Izquierdo = Seleccionar elemento bajo el mouse
```

- **Efecto:** El elemento anterior se deselecciona
- **Visual:** Borde azul brillante
- **Info:** Se muestra info del elemento arriba

### Selección Múltiple

```
Ctrl + Click Izquierdo = Agregar/Quitar de selección
```

**Ejemplo:** Selecciona 3 cofres para moverlos juntos.

### Seleccionar Todos

```
Ctrl + A = Seleccionar todos los elementos visibles
```

**Nota:** Solo selecciona elementos de capas visibles.

### Deseleccionar

```
Click en área vacía = Deseleccionar todo
```

---

## ✏️ Movimiento y Edición {#movimiento}

### Mover Elementos

1. **Selecciona** uno o más elementos
2. **Arrastra** desde el centro del elemento
3. **Suelta** para fijar posición

**Comportamiento:**

- Si hay varios seleccionados, se mueven todos juntos
- El offset relativo entre elementos se mantiene
- Con Snap activo, se ajusta al grid

### Redimensionar Elementos

1. **Selecciona** un elemento
2. **Coloca el mouse en un borde o esquina**
3. **Arrastra** para cambiar tamaño

**Bordes disponibles:**

- **N, S, E, W:** Lados (norte, sur, este, oeste)
- **NW, NE, SW, SE:** Esquinas

**Restricción:** Tamaño mínimo de 16x16 píxeles.

---

## 📋 Copiar y Pegar {#copiar-pegar}

### Copiar Elementos

```
Ctrl + C = Copiar elementos seleccionados
```

**Feedback:** Mensaje en consola: `✓ Copiados X elementos`

### Pegar Elementos

```
Ctrl + V = Pegar en posición del mouse
```

**Comportamiento:**

1. Los elementos se pegan donde está el mouse
2. Se mantiene el offset relativo entre elementos
3. Se generan nuevos IDs automáticamente
4. Los elementos pegados quedan seleccionados

**Ejemplo:**

```
1. Selecciona un cofre en (100, 100)
2. Ctrl+C para copiar
3. Mueve el mouse a (300, 200)
4. Ctrl+V para pegar
5. Aparece un nuevo cofre en (300, 200) con ID único
```

---

## 🔲 Grid y Snap {#grid-snap}

### Grid Visual

```
G = Toggle Grid (mostrar/ocultar líneas)
```

**Configuración:**

- Tamaño: 32x32 píxeles (configurable en código)
- Color: Gris oscuro sutil

**Uso:** Ayuda a alinear elementos visualmente.

### Snap to Grid

```
S = Toggle Snap (ajustar a grid)
```

**Cuando está activo:**

- Al mover elementos, se ajustan a la grid más cercana
- Al pegar elementos, se ajustan a la grid
- Facilita alineación perfecta

**Tip:** Combina Grid Visual + Snap para máxima precisión.

---

## ✅ Validación {#validación}

### Ejecutar Validación

```
V = Validar todos los elementos
```

### Problemas Detectados

1. **Superposiciones:** Dos elementos del mismo tipo que se solapan
2. **Fuera del mapa:** Elementos con coordenadas negativas o fuera de los límites
3. **Tamaños inválidos:** Elementos con ancho/alto menor a 16px

### Feedback

- **Consola:** Lista de problemas encontrados
- **Visual:** Elementos con error se marcan internamente

**Ejemplo de salida:**

```
🔍 Validando elementos...
⚠ Superposición: M3 y M5
⚠ C2 se sale del mapa
✗ Encontrados 2 problemas
```

---

## 🔄 Hot-Reload {#hot-reload}

### ¿Qué es?

El editor **detecta automáticamente** cuando otros editores guardan cambios y **recarga** los elementos.

### Funcionamiento

- Cada **2 segundos** verifica los timestamps de archivos
- Si detecta cambios, recarga **solo los archivos modificados**
- **No pierde tu progreso** actual

### Workflow con Editores Específicos

```
1. Abres Editor Unificado
2. Abres Editor de Cofres
3. Agregas un cofre en Editor de Cofres
4. Guardas (Ctrl+G)
5. [2 segundos después]
6. Editor Unificado muestra el nuevo cofre automáticamente
```

**Feedback:**

```
🔄 Cambios detectados en: cofres
✓ Recargando mapa...
```

---

## 📸 Exportación {#exportación}

### Exportar Screenshot

```
E = Exportar imagen del viewport
```

**Resultado:**

- Archivo PNG en carpeta `exports/`
- Nombre: `{mapa}_{timestamp}.png`
- Ejemplo: `ciudad_01_20251119_143052.png`

**Incluye:**

- Mapa de fondo
- Todos los elementos visibles
- Grid (si está activo)
- Elementos seleccionados (con borde azul)

**Uso:** Documentación, debugging, compartir diseños.

---

## ⌨️ Controles Completos {#controles}

### Tabla de Referencia

| Acción            | Control               | Descripción          |
| ----------------- | --------------------- | -------------------- |
| **NAVEGACIÓN**    |                       |                      |
| Mover vista       | Click Der + Arrastrar | Pan del mapa         |
| Zoom in           | Rueda Arriba          | Acercar              |
| Zoom out          | Rueda Abajo           | Alejar               |
| **SELECCIÓN**     |                       |                      |
| Seleccionar       | Click Izq             | Selecciona elemento  |
| Multi-selección   | Ctrl + Click          | Agregar/quitar       |
| Seleccionar todos | Ctrl + A              | Todos visibles       |
| Deseleccionar     | Click en vacío        | Limpia selección     |
| **EDICIÓN**       |                       |                      |
| Mover             | Arrastrar             | Mueve seleccionados  |
| Redimensionar     | Arrastrar borde       | Cambia tamaño        |
| Eliminar          | DEL                   | Borra seleccionados  |
| Copiar            | Ctrl + C              | Copia seleccionados  |
| Pegar             | Ctrl + V              | Pega en mouse        |
| **CAPAS**         |                       |                      |
| Toggle capa       | Click checkbox        | Mostrar/ocultar      |
| **UTILIDADES**    |                       |                      |
| Grid              | G                     | Toggle grid visual   |
| Snap              | S                     | Toggle snap to grid  |
| Info              | I                     | Toggle info overlay  |
| Ayuda             | H                     | Muestra/oculta ayuda |
| Validar           | V                     | Ejecuta validación   |
| Exportar          | E                     | Screenshot PNG       |
| Guardar           | Ctrl + G              | Guarda cambios       |
| Salir             | ESC                   | Guarda y cierra      |

---

## 🔄 Flujo de Trabajo {#flujo-trabajo}

### Workflow Típico

#### 1. Diseño General

```
1. Abre Editor Unificado
2. Carga el mapa que quieres editar
3. Activa Grid (G) y Snap (S)
4. Mueve y alinea elementos existentes
5. Valida (V) para detectar problemas
6. Guarda (Ctrl+G)
```

#### 2. Configuración Detallada

```
1. Desde Editor Unificado, identifica cofres a configurar
2. Abre Editor de Cofres
3. Selecciona el cofre y configura items/oro
4. Guarda en Editor de Cofres
5. Editor Unificado auto-recarga los cambios (2 segundos)
6. Verifica visualmente en Editor Unificado
```

#### 3. Organización Masiva

```
1. Selecciona múltiples elementos (Ctrl+Click)
2. Muévelos juntos a nueva posición
3. Copia (Ctrl+C)
4. Pega en varias posiciones (Ctrl+V)
5. Ajusta con Snap activo
6. Valida para asegurar no hay superposiciones
```

#### 4. Duplicación Rápida

```
1. Selecciona un spawn complejo
2. Ctrl+C para copiar
3. Ctrl+V en nueva zona
4. El nuevo spawn tiene ID único automático
5. Abre Editor de Spawns para ajustar monstruos
```

---

## 🔗 Relación con Editores Específicos {#relación-editores}

### Arquitectura Complementaria

El Editor Unificado **NO reemplaza** los editores específicos. Son **complementarios**:

| Editor                 | Función Principal                                            |
| ---------------------- | ------------------------------------------------------------ |
| **Unificado**          | Organización espacial, vista general, movimiento, alineación |
| **Editor de Muros**    | Dibujo de paredes, colisiones, atajos de teclado para líneas |
| **Editor de Portales** | Configuración de destinos, mapas objetivo, IDs de spawn      |
| **Editor de Spawns**   | Selección de monstruos, tasas de encuentro, nivel            |
| **Editor de Cofres**   | Items, cantidades, oro, tipo de cofre, apertura única        |

### Flujo Bidireccional

```
EDITOR UNIFICADO ↔ ARCHIVOS JSON ↔ EDITORES ESPECÍFICOS
```

**Sincronización:**

- Cambias posición en Unificado → Se guarda en JSON → Aparece en Editor Específico
- Agregas cofre en Editor de Cofres → Se guarda en JSON → Auto-recarga en Unificado

---

## 🛠️ Resolución de Problemas {#problemas}

### Problema: No veo el mapa

**Causa:** No se encontró la imagen del mapa.

**Solución:**

1. Verifica que existe `assets/maps/{categoria}/{nombre}.png`
2. Revisa la consola para ver errores de carga
3. Asegúrate que el nombre coincide con el JSON

### Problema: Los cambios no se guardan

**Causa:** No presionaste Ctrl+G o ESC antes de cerrar.

**Solución:**

- Siempre usa **Ctrl+G** para guardar manualmente
- O usa **ESC** que guarda automáticamente antes de cerrar

### Problema: Hot-reload no funciona

**Causa:** El archivo no cambió su timestamp.

**Solución:**

1. Asegúrate de GUARDAR en el otro editor
2. Espera 2 segundos para el check
3. Verifica que el archivo JSON cambió su fecha de modificación

### Problema: No puedo seleccionar un elemento

**Causa 1:** La capa está oculta.

**Solución:** Activa el checkbox de la capa en el panel lateral.

**Causa 2:** El elemento está detrás de otro.

**Solución:** Oculta la capa del elemento que está encima.

### Problema: Snap no funciona

**Causa:** Snap no está activo o el tamaño de grid no es el esperado.

**Solución:**

1. Presiona **S** para activar Snap
2. Verifica que dice `Snap to grid: ON` en consola
3. Ajusta `self.grid_size = 32` en código si necesitas otro tamaño

### Problema: Validación reporta errores falsos

**Causa:** La validación es estricta con superposiciones.

**Solución:**

- Si dos elementos del mismo tipo deben superponerse (raro), ignóralo
- O separa mínimamente los elementos

### Problema: Exportación no funciona

**Causa:** No existe la carpeta `exports/`.

**Solución:** El editor la crea automáticamente. Si falla, créala manualmente.

---

## 📚 Recursos Adicionales

### Archivos Relacionados

- `editor_cofres.py` - Editor específico de cofres
- `docs/DATABASE.md` - Esquema de JSON de elementos
- `docs/EDITOR_COFRES_MANUAL_COMPLETO.md` - Manual del editor de cofres

### Próximas Características

- [ ] Selector de mapa en el panel (cambiar sin reiniciar)
- [ ] Crear nuevos elementos desde el Editor Unificado
- [ ] Historial de cambios (undo/redo)
- [ ] Búsqueda de elementos por ID
- [ ] Filtros avanzados
- [ ] Modo comparación (antes/después)
- [ ] Exportación a JSON unificado

---

## 📝 Notas de Versión

### v1.0 - 19 Nov 2025

✅ **FASE 1:** Vista multi-capa, movimiento, redimensionamiento  
✅ **FASE 2:** Copiar/pegar, selección múltiple, eliminación  
✅ **FASE 3:** Grid/Snap, hot-reload, validación, exportación

**Elementos Soportados:** Muros, Portales, Spawns, Cofres  
**Pendientes:** NPCs, Eventos

---

## 🎓 Tips Profesionales

1. **Usa Snap para alineación perfecta** - Activa S antes de mover elementos críticos
2. **Oculta capas para trabajar limpio** - Desactiva Muros si estás organizando Cofres
3. **Valida frecuentemente** - Presiona V después de cambios importantes
4. **Copia en lugar de recrear** - Ctrl+C/Ctrl+V es más rápido que abrir otro editor
5. **Exporta antes de cambios grandes** - Usa E para tener backup visual
6. **Hot-reload es tu amigo** - Deja Unificado abierto mientras usas otros editores
7. **Grid de 32px = tiles estándar** - Alinea con la grid para mapas cuadriculados

---

**¡Disfruta del Editor Unificado!** 🚀

Si encuentras bugs o tienes sugerencias, reporta en el proyecto.
