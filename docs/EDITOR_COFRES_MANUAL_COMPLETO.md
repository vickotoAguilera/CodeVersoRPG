# Editor de Cofres - Manual Completo

**CodeVerso RPG - Sistema de Cofres Visual**

Fecha: 19 de noviembre de 2025  
Versión: 1.0

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Inicio Rápido](#inicio-rápido)
3. [Interfaz del Editor](#interfaz-del-editor)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Controles y Atajos](#controles-y-atajos)
6. [Flujos de Trabajo](#flujos-de-trabajo)
7. [Sistema de Guardado](#sistema-de-guardado)
8. [Tips y Trucos](#tips-y-trucos)
9. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

El **Editor de Cofres** es una herramienta visual completa para crear, configurar y gestionar cofres en los mapas del juego. Permite colocar cofres con precisión, configurar su contenido, y duplicarlos rápidamente.

### Características Principales:

- ✅ Interfaz visual drag & drop
- ✅ 5 tipos de cofres (madera, bronce, plata, oro, especial)
- ✅ Sistema de contenido con items, equipo y especiales
- ✅ Generación de loot aleatorio
- ✅ Editor de cantidades con auto-guardado
- ✅ Copiar y pegar cofres (Ctrl+C / Ctrl+V)
- ✅ Zoom y paneo del mapa
- ✅ Auto-guardado cada 5 segundos
- ✅ Sistema de llaves automático

---

## 🚀 Inicio Rápido

### 1. Ejecutar el Editor

**Windows:**

```batch
ejecutar_cofres.bat
```

**Línea de comandos:**

```bash
python editor_cofres.py
```

### 2. Cargar un Mapa

**Opción A - Drag & Drop:**

1. En el panel izquierdo, expande una categoría de mapas (▶)
2. Arrastra un mapa al área del viewport (derecha)
3. Suelta para cargar

**Opción B - Click:**

1. Expande una categoría
2. Click en un mapa
3. Se carga automáticamente

### 3. Crear tu Primer Cofre

1. **Click izquierdo** en el viewport donde quieras el cofre
2. Se crea un cofre de madera por defecto
3. **Click derecho** en el cofre para abrir el modal de edición
4. Configura tipo, oro y contenido
5. Click en **"Cerrar"**

¡Listo! Tu cofre está guardado.

---

## 🖥️ Interfaz del Editor

### Distribución de Pantalla

```
┌─────────────┬──────────────────────────────────────────┐
│   PANEL     │           VIEWPORT                       │
│  LATERAL    │         (Mapa + Cofres)                  │
│             │                                          │
│  • Mapas    │  Info: Mapa | Cofres | Zoom             │
│    - Cat 1  │                                          │
│    - Cat 2  │  [Cofre 1]  [Cofre 2]                   │
│             │                                          │
│  [H] Ayuda  │            [Cofre 3]                     │
└─────────────┴──────────────────────────────────────────┘
```

### Panel Lateral (Izquierda)

**Elementos:**

- **Título**: "Editor de Cofres"
- **Instrucción**: Guía drag & drop
- **Secciones de Mapas**: Organizadas por categoría
  - Click en `▶` para expandir/colapsar
  - Muestra cantidad de mapas: `(5)`
- **Botón Ayuda**: `[H] Ayuda`

### Viewport (Derecha)

**Elementos:**

- **Barra de Info Superior**: Nombre del mapa, cantidad de cofres, zoom actual
- **Selección**: Muestra cofre seleccionado con dimensiones
- **Portapapeles**: `[Portapapeles: Cofre_Oro_C1] Ctrl+V para pegar`
- **Cofres**: Rectángulos con borde naranja
  - Sin seleccionar: Borde fino
  - Seleccionado: Borde grueso azul

---

## 🎮 Funcionalidades Principales

### 1. Gestión de Cofres

#### Crear Cofre

- **Click izquierdo** en el viewport
- Crea cofre de madera 64x64px
- ID auto-generado: C1, C2, C3...

#### Seleccionar Cofre

- **Click izquierdo** sobre un cofre existente
- Borde cambia a azul
- Muestra info en la parte superior

#### Mover Cofre

1. Selecciona el cofre (click)
2. Arrastra desde el centro
3. Suelta en nueva posición

#### Redimensionar Cofre

1. Selecciona el cofre
2. Coloca el cursor en un borde/esquina
3. El cursor cambia a indicador de resize
4. Arrastra para ajustar tamaño

**Puntos de Resize:**

- `n` = Norte (arriba)
- `s` = Sur (abajo)
- `e` = Este (derecha)
- `w` = Oeste (izquierda)
- `ne`, `nw`, `se`, `sw` = Esquinas

#### Eliminar Cofre

- Selecciona el cofre
- Presiona **DEL**
- Se elimina permanentemente

#### Copiar y Pegar Cofre

1. Selecciona un cofre
2. **Ctrl+C** → copia al portapapeles
3. Mueve el mouse a la nueva posición
4. **Ctrl+V** → pega con nuevo ID

**Lo que se copia:**

- Tipo de cofre
- Tamaño (ancho x alto)
- Oro
- Todos los items con cantidades
- Todo el equipo con cantidades
- Todos los especiales con cantidades
- Configuración de llaves
- Sprites asignados

---

### 2. Modal de Edición de Cofre

**Abrir:** Click derecho sobre un cofre

#### Estructura del Modal

```
┌─────────────────────────────────────────────────────┐
│  Editar: Cofre_Madera_C1                            │
│                                                     │
│  Tipo: MADERA                                       │
│  [Madera] [Bronce] [Plata] [Oro] [Especial]       │
│                                                     │
│  Oro: [1500▮]  [Random Oro]                        │
│                                                     │
│  ┌─────────────────────┬──────────────────────────┐│
│  │ Items Disponibles   │ Contenido del Cofre      ││
│  │                     │                          ││
│  │ ▼ Consumibles (12)  │ Items Consumibles:       ││
│  │   ☐ Poción HP       │   • Poción HP   [x 5] X  ││
│  │   ☑ Ether           │   • Ether       [x 3] X  ││
│  │   ☐ Antídoto        │                          ││
│  │                     │ Equipo:                  ││
│  │ ▶ Equipo (25)       │   • Espada      [x 1] X  ││
│  │                     │                          ││
│  │ ▶ Especiales (18)   │ Items Especiales:        ││
│  │                     │   (vacío)                ││
│  │                     │                          ││
│  │ [AGREGAR (2)]       │                          ││
│  └─────────────────────┴──────────────────────────┘│
│                                                     │
│  [Generar Loot Random]  [Limpiar Cofre]  [Cerrar] │
└─────────────────────────────────────────────────────┘
```

#### Sección: Tipo de Cofre

**5 Tipos Disponibles:**

| Tipo         | Color    | Llave           | Oro      | Descripción                   |
| ------------ | -------- | --------------- | -------- | ----------------------------- |
| **Madera**   | Marrón   | ❌ No           | 10-50    | Cofre básico, sin llave       |
| **Bronce**   | Cobre    | ✅ Llave Bronce | 50-150   | Cofre común con llave         |
| **Plata**    | Plateado | ✅ Llave Plata  | 150-400  | Cofre valioso                 |
| **Oro**      | Dorado   | ✅ Llave Oro    | 400-1000 | Cofre muy valioso             |
| **Especial** | Violeta  | ❌ No           | 0        | Cofre único, items especiales |

**Cambiar Tipo:**

- Click en botón del tipo deseado
- Actualiza automáticamente:
  - Color del cofre
  - Nombre (`Cofre_Oro_C3`)
  - Requisito de llave
  - Configuración de reapertura

#### Sección: Oro

**Input Editable:**

- Click en el cuadro de oro
- Escribe cualquier número ≥ 0
- **ENTER** para confirmar
- **ESC** para cancelar
- **Auto-guarda** al cambiar de campo

**Botón "Random Oro":**

- Genera oro aleatorio según tipo de cofre
- Rango depende del `cofres_db.json`
- Ejemplo Oro: 400-1000

#### Sección: Items Disponibles (Columna Izquierda)

**3 Categorías Desplegables:**

**▼ Consumibles (N)**

- Click en header para expandir/colapsar
- Muestra cantidad total disponible
- Máximo 8 items visibles por defecto
- Items: Pociones, Ethers, Antídotos, Elixires, etc.

**▼ Equipo (N)**

- Armas, armaduras, accesorios
- Espadas, Escudos, Botas, Anillos, etc.

**▼ Especiales (N)**

- Items únicos y quest items
- Llaves (Bronce, Plata, Oro, Maestra)
- Expansores de ranuras
- Orbes de experiencia
- Cristales de resurrección
- Bolsas de oro

**Selección con Checkboxes:**

- ☐ = No seleccionado
- ☑ = Seleccionado (verde)
- Click en checkbox para marcar/desmarcar
- Puedes seleccionar múltiples items de diferentes categorías

**Botón "AGREGAR (N)":**

- Verde brillante cuando hay selección
- Gris cuando no hay nada seleccionado
- Muestra cantidad de items seleccionados
- Click para agregar todos al cofre
- Agrega con cantidad inicial = 1
- Limpia automáticamente las selecciones

#### Sección: Contenido del Cofre (Columna Derecha)

**Organizado por Categoría:**

**Items Consumibles:**

- Lista de items en el cofre
- Formato: `• Nombre [x Cantidad] X`
- Muestra máximo 12 items

**Equipo:**

- Lista de equipamiento
- Mismo formato

**Items Especiales:**

- Lista de items especiales
- Mismo formato

**Funciones por Item:**

1. **Ver Nombre:** Truncado a 20 caracteres
2. **Editar Cantidad:** Click en `[x N]`
   - Activa input (fondo amarillo)
   - Escribe nuevo número
   - **ENTER** confirma
   - **ESC** cancela
   - **Auto-guarda** al cambiar campo
3. **Eliminar Item:** Click en `X` rojo
   - Elimina inmediatamente
   - No requiere confirmación

**Estados del Input:**

- Normal: `x 5` (gris)
- Editando: `5_` (amarillo con cursor)

#### Botones Inferiores

**[Generar Loot Random]**

- Verde oscuro
- Genera contenido aleatorio según tipo de cofre
- **IMPORTANTE**: Limpia contenido previo
- Usa configuración de `cofres_db.json`
- Incluye: oro, items, equipo, especiales

**[Limpiar Cofre]**

- Naranja
- Vacía completamente el cofre
- Pone oro en 0
- Elimina todos los items
- Útil para empezar de cero

**[Cerrar]**

- Rojo
- Guarda automáticamente cambios pendientes
- Cierra el modal
- Vuelve al viewport

---

### 3. Navegación del Mapa

#### Zoom

**Control:**

- **Rueda del mouse** arriba = Zoom in
- **Rueda del mouse** abajo = Zoom out

**Rango:** 0.25x - 2.0x (25% - 200%)

**Centrado:** Zoom mantiene el centro del viewport

#### Paneo (Mover Mapa)

**Control:**

- **Click derecho + Arrastrar** en área vacía
- Mueve el mapa en todas direcciones
- Útil con zoom para navegar mapas grandes

**Restricciones:**

- No pane si hay un cofre bajo el cursor
- Abre modal de cofre en su lugar

---

### 4. Sistema de Auto-Guardado

**Auto-guardado cada 5 segundos:**

- Guarda automáticamente el mapa actual
- Actualiza archivo JSON en `src/database/mapas/`
- Muestra mensaje en consola: `✓ Guardado: nombre_mapa.json`

**Guardado Manual:**

- Presiona **G** en cualquier momento
- Fuerza guardado inmediato

**Guardado al Salir:**

- Al presionar **ESC** o cerrar ventana
- Guarda automáticamente antes de salir

**Guardado de Cantidades:**

- Auto-guarda al cambiar de campo
- Auto-guarda al cerrar modal
- Auto-guarda al presionar ENTER

---

## ⌨️ Controles y Atajos

### Controles de Mouse

| Acción                  | Control                                  |
| ----------------------- | ---------------------------------------- |
| **Crear cofre**         | Click izquierdo en viewport vacío        |
| **Seleccionar cofre**   | Click izquierdo sobre cofre              |
| **Mover cofre**         | Click izq + arrastrar (centro del cofre) |
| **Redimensionar cofre** | Click izq + arrastrar (borde/esquina)    |
| **Abrir modal**         | Click derecho sobre cofre                |
| **Paneo del mapa**      | Click derecho + arrastrar (área vacía)   |
| **Zoom in/out**         | Rueda del mouse                          |
| **Expandir sección**    | Click en header (▶/▼)                    |
| **Marcar checkbox**     | Click en ☐                               |
| **Editar cantidad**     | Click en input [x N]                     |
| **Eliminar item**       | Click en X rojo                          |

### Atajos de Teclado

| Tecla         | Función                           |
| ------------- | --------------------------------- |
| **Click Izq** | Colocar/Seleccionar cofre         |
| **Click Der** | Abrir modal / Pan                 |
| **Ctrl+C**    | Copiar cofre seleccionado         |
| **Ctrl+V**    | Pegar cofre en posición del mouse |
| **DEL**       | Eliminar cofre seleccionado       |
| **G**         | Guardar mapa manualmente          |
| **H**         | Mostrar/Ocultar ayuda             |
| **ESC**       | Salir (guarda automáticamente)    |

### Atajos en Modal

| Tecla         | Función                         |
| ------------- | ------------------------------- |
| **ENTER**     | Confirmar cantidad editada      |
| **ESC**       | Cancelar edición / Cerrar modal |
| **BACKSPACE** | Borrar dígito                   |
| **0-9**       | Escribir cantidad               |

---

## 🔄 Flujos de Trabajo

### Flujo 1: Crear Cofre Simple

**Objetivo:** Crear un cofre de madera con pociones

1. Carga un mapa
2. Click izquierdo donde quieras el cofre
3. Click derecho en el cofre
4. En el modal:
   - Expande `▼ Consumibles`
   - Marca ☑ Poción HP
   - Marca ☑ Ether
   - Click `AGREGAR (2)`
   - Click en `[x 1]` de Poción HP
   - Escribe `5` + ENTER
   - Click en `[x 1]` de Ether
   - Escribe `3` + ENTER
5. Click `Cerrar`

✅ **Resultado:** Cofre con 5 Pociones HP y 3 Ethers

---

### Flujo 2: Cofre de Oro con Loot Random

**Objetivo:** Crear cofre valioso con contenido aleatorio

1. Crea cofre (click izquierdo)
2. Click derecho → abre modal
3. Click en botón `[Oro]` → cambia tipo
4. Click `Generar Loot Random`
5. Revisa el contenido generado:
   - Oro: 400-1000 (aleatorio)
   - Items: 2-5 consumibles
   - Equipo: 0-2 piezas
   - Especiales: posible llave
6. (Opcional) Ajusta cantidades manualmente
7. Click `Cerrar`

✅ **Resultado:** Cofre de oro con loot equilibrado

---

### Flujo 3: Duplicar Cofres Configurados

**Objetivo:** Crear 10 cofres idénticos en diferentes posiciones

1. Crea y configura el primer cofre:
   - Tipo: Plata
   - Oro: 300
   - 5 Pociones HP
   - 2 Ethers
   - 1 Espada de Hierro
2. Selecciona el cofre (click izquierdo)
3. **Ctrl+C** → copia al portapapeles
4. Mueve el mouse a otra posición
5. **Ctrl+V** → pega cofre idéntico (C2)
6. Repite pasos 4-5 para C3, C4, C5...

✅ **Resultado:** 10 cofres plata idénticos con contenido exacto

**Tiempo estimado:** 30 segundos vs 10 minutos manual

---

### Flujo 4: Ajuste de Oro en Cofres Existentes

**Objetivo:** Cambiar oro de múltiples cofres

1. Click derecho en Cofre_1
2. Click en input de oro
3. Escribe `500`
4. Click `Cerrar` (auto-guarda)
5. Click derecho en Cofre_2
6. Click en input de oro (guarda 500 del anterior)
7. Escribe `750`
8. Click `Cerrar`
9. Repite para más cofres

✅ **Resultado:** Oro actualizado sin usar Random

---

### Flujo 5: Limpiar y Reconfigurar Cofre

**Objetivo:** Cambiar completamente el contenido de un cofre

1. Click derecho en cofre existente
2. Click `Limpiar Cofre`
3. Oro = 0, items = vacío
4. Configura nuevo contenido:
   - Tipo diferente (ej: Bronce → Oro)
   - Nuevo oro (ej: 800)
   - Nuevos items
5. Click `Cerrar`

✅ **Resultado:** Cofre reconfigurado desde cero

---

## 💾 Sistema de Guardado

### Formato de Archivo JSON

**Ubicación:** `src/database/mapas/categoria/nombre_mapa.json`

**Estructura:**

```json
{
  "nombre": "mapa_pradera",
  "categoria": "exteriores",
  "subcarpeta": null,
  "archivo_imagen": "mapa_pradera.png",
  "ancho": 1600,
  "alto": 1200,
  "cofres": [
    {
      "id": "C1",
      "nombre": "Cofre_Oro_C1",
      "x": 450,
      "y": 320,
      "ancho": 64,
      "alto": 64,
      "tipo": "oro",
      "oro": 750,
      "items_contenido": {
        "POCION_BASICA": 5,
        "ETER_BASICO": 3
      },
      "equipo_contenido": {
        "ESPADA_HIERRO": 1
      },
      "especiales_contenido": {},
      "requiere_llave": "LLAVE_ORO",
      "puede_reabrir": false,
      "tiempo_reapertura": 0
    }
  ]
}
```

### Campos del Cofre

| Campo                  | Tipo        | Descripción               | Ejemplo                |
| ---------------------- | ----------- | ------------------------- | ---------------------- |
| `id`                   | string      | ID único auto-generado    | `"C1"`, `"C2"`         |
| `nombre`               | string      | Nombre descriptivo        | `"Cofre_Oro_C1"`       |
| `x`                    | int         | Posición X en el mapa     | `450`                  |
| `y`                    | int         | Posición Y en el mapa     | `320`                  |
| `ancho`                | int         | Ancho en píxeles          | `64`                   |
| `alto`                 | int         | Alto en píxeles           | `64`                   |
| `tipo`                 | string      | Tipo de cofre             | `"oro"`                |
| `oro`                  | int         | Cantidad de oro           | `750`                  |
| `items_contenido`      | dict        | Items con cantidades      | `{"POCION_BASICA": 5}` |
| `equipo_contenido`     | dict        | Equipo con cantidades     | `{"ESPADA_HIERRO": 1}` |
| `especiales_contenido` | dict        | Especiales con cantidades | `{}`                   |
| `requiere_llave`       | string/null | ID de llave requerida     | `"LLAVE_ORO"`          |
| `puede_reabrir`        | bool        | Permite reabrirse         | `false`                |
| `tiempo_reapertura`    | int         | Minutos para reabrir      | `0`                    |

### IDs de Items

**Formato:** `MAYUSCULAS_CON_GUION`

**Ejemplos:**

- Items: `POCION_BASICA`, `ETER_BASICO`, `ANTIDOTO`, `ELIXIR`
- Equipo: `ESPADA_HIERRO`, `ESCUDO_MADERA`, `BOTAS_CUERO`
- Especiales: `LLAVE_BRONCE`, `EXPANSOR_RANURAS`, `ORBE_EXPERIENCIA`

**Referencia completa:** Ver `src/database/items_db.json`, `equipo_db.json`, `items_especiales_db.json`

---

## 💡 Tips y Trucos

### Organización de Cofres

**Nomenclatura Consistente:**

- Los IDs se auto-generan: C1, C2, C3...
- Los nombres incluyen tipo: `Cofre_Oro_C1`
- No necesitas cambiar nombres manualmente

**Agrupación Visual:**

- Usa zoom para ver el mapa completo
- Coloca cofres similares cerca unos de otros
- Deja espacio entre cofres para facilitar selección

### Optimización de Tiempo

**Plantillas de Cofres:**

1. Crea un cofre "plantilla" bien configurado
2. Cópialo (Ctrl+C)
3. Pega en todas las posiciones (Ctrl+V)
4. Ajusta detalles específicos si es necesario

**Loot Random + Ajuste:**

1. Usa "Generar Loot Random" para base
2. Ajusta manualmente cantidades específicas
3. Más rápido que configurar desde cero

**Secciones Colapsadas:**

- Colapsa categorías no usadas (▶)
- Mantén expandida solo la que estás usando
- Botón AGREGAR siempre visible

### Precisión en Colocación

**Uso de Zoom:**

- Zoom in (1.5x - 2.0x) para colocación precisa
- Zoom out (0.5x - 0.75x) para vista general

**Paneo Efectivo:**

- Click derecho + arrastrar para navegar
- Combina con zoom para máxima precisión

**Grid Mental:**

- Los mapas suelen ser 1600x1200 o similares
- Divide mentalmente en cuadrantes
- Coloca cofres en posiciones redondeadas (ej: x=100, y=200)

### Edición Rápida de Cantidades

**Flujo Eficiente:**

1. Click en primera cantidad → escribe valor
2. Click en segunda cantidad (auto-guarda primera)
3. Click en tercera cantidad (auto-guarda segunda)
4. No uses ENTER entre campos
5. Solo usa ENTER o Cerrar al final

**Valores Comunes:**

- Pociones: 3-5 unidades
- Ethers: 2-3 unidades
- Equipo: 1 unidad
- Oro: múltiplos de 50 o 100

---

## 🔧 Solución de Problemas

### Problema: El mapa no carga

**Posibles Causas:**

1. Archivo JSON no tiene imagen asociada
2. Imagen en subcarpeta incorrecta
3. Extensión de imagen incorrecta

**Solución:**

- Solo se muestran mapas con imágenes encontradas
- Verifica que exista `.png`, `.jpg` o `.jpeg`
- Revisa `subcarpeta` en JSON

---

### Problema: No puedo crear cofres

**Verificaciones:**

1. ¿Hay un mapa cargado?
2. ¿Estás haciendo click en el viewport (derecha)?
3. ¿El modal está cerrado?

**Solución:**

- Carga un mapa primero
- Click izquierdo en área gris/verde (no en panel)
- Cierra modal si está abierto

---

### Problema: La cantidad no se guarda

**Causa:**

- Olvidaste presionar ENTER o cambiar de campo

**Solución:**

- Después de escribir el número:
  - Presiona **ENTER**, o
  - Click en otro campo, o
  - Click en **Cerrar**
- El auto-guardado funciona al cambiar foco

---

### Problema: Cofre copiado no pega

**Verificaciones:**

1. ¿Seleccionaste un cofre antes de Ctrl+C?
2. ¿El mouse está en el viewport al hacer Ctrl+V?
3. ¿Hay un mapa cargado?

**Solución:**

- Primero: Click en cofre para seleccionar
- Luego: Ctrl+C (verifica mensaje verde)
- Mueve mouse al viewport (no al panel)
- Luego: Ctrl+V

---

### Problema: Auto-guardado no funciona

**Verificaciones:**

- Los mensajes de guardado aparecen en consola
- No hay errores en consola

**Solución:**

- Espera 5 segundos para auto-guardado
- O presiona **G** para forzar guardado
- Verifica permisos de escritura en `src/database/mapas/`

---

### Problema: Modal no abre

**Causa:**

- Click derecho en área vacía (activa paneo)

**Solución:**

- Click derecho **exactamente sobre el cofre**
- Si el cursor está fuera del cofre, inicia paneo
- Usa zoom para hacer cofres más grandes y fáciles de clickear

---

### Problema: Checkboxes no responden

**Causa:**

- Clicks demasiado rápidos (debounce)
- Click fuera del área del checkbox

**Solución:**

- Click directamente en el cuadrado ☐
- Espera 150ms entre clicks
- No hagas doble-click

---

## 📚 Referencias Adicionales

### Archivos Relacionados

- **Editor:** `editor_cofres.py` (1550+ líneas)
- **Launcher:** `ejecutar_cofres.bat`
- **Bases de Datos:**
  - `src/database/items_db.json` - Items consumibles
  - `src/database/equipo_db.json` - Armas y armaduras
  - `src/database/items_especiales_db.json` - Items especiales (18)
  - `src/database/cofres_db.json` - Configuración de tipos de cofres
- **Mapas:** `src/database/mapas/categoria/*.json`
- **Imágenes:** `assets/maps/categoria/subcarpeta/*.png`

### Documentación

- **Guía Completa:** `docs/EDITOR_COFRES_GUIA.md` (600+ líneas)
- **Actualización:** `docs/ACTUALIZACION_EDITOR_COFRES.md`
- **Database:** `docs/DATABASE.md` - Esquema completo

### Configuración de Tipos de Cofres

**Archivo:** `src/database/cofres_db.json`

**Ejemplo Configuración:**

```json
{
  "tipos_cofre": {
    "oro": {
      "oro_min": 400,
      "oro_max": 1000,
      "requiere_llave": "LLAVE_ORO",
      "puede_reabrir": false,
      "tiempo_reapertura_minutos": 0,
      "items_random": {
        "min": 2,
        "max": 5,
        "pool_consumibles": ["POCION_BASICA", "ETER_BASICO", "ELIXIR"],
        "pool_equipo": ["ESPADA_ORO", "ESCUDO_ORO"],
        "pool_especiales": ["LLAVE_MAESTRA"]
      }
    }
  }
}
```

---

## 🎓 Mejores Prácticas

### Diseño de Cofres

1. **Balance de Recompensas:**

   - Cofres de madera: 1-2 pociones básicas, 10-50 oro
   - Cofres de bronce: 2-3 items variados, 50-150 oro
   - Cofres de plata: 3-5 items buenos, 150-400 oro
   - Cofres de oro: 5+ items valiosos, 400-1000 oro
   - Cofres especiales: Items únicos, sin oro

2. **Distribución en Mapas:**

   - No sobrecargues un área con cofres
   - Coloca cofres valiosos en lugares difíciles
   - Esconde cofres especiales

3. **Progresión:**
   - Mapas iniciales: más madera/bronce
   - Mapas intermedios: plata
   - Mapas finales: oro/especial

### Workflow Eficiente

1. **Planificación:**

   - Decide cuántos cofres necesitas
   - Define tipos y contenido general
   - Marca posiciones en el mapa

2. **Creación en Lote:**

   - Crea todos los cofres vacíos primero
   - Configura plantillas de cada tipo
   - Usa copiar/pegar para duplicar

3. **Refinamiento:**
   - Ajusta posiciones con paneo/zoom
   - Modifica cantidades específicas
   - Prueba en el juego

### Testing

1. **Verificación Visual:**

   - Zoom out completo
   - Revisa distribución general
   - Verifica que no se superpongan

2. **Verificación de Datos:**

   - Abre archivo JSON generado
   - Revisa que todos los cofres tengan:
     - IDs únicos
     - Posiciones válidas
     - Contenido correcto

3. **Prueba en Juego:**
   - Carga el mapa en el juego
   - Verifica que los cofres aparezcan
   - Prueba abrir cada cofre
   - Verifica llaves requeridas

---

## 📝 Changelog

### Versión 1.0 - 19 Nov 2025

**Características Implementadas:**

✅ **Editor Base:**

- Sistema de mapas con drag & drop
- Creación y colocación de cofres
- Selección y edición visual
- Redimensionamiento por bordes
- Zoom y paneo

✅ **Modal de Edición:**

- 5 tipos de cofres
- Sistema de checkboxes para items
- Secciones desplegables (Consumibles, Equipo, Especiales)
- Input editable de oro
- Inputs editables de cantidades con auto-guardado
- Botón "Agregar" con contador
- Generación de loot random
- Botón limpiar cofre

✅ **Copiar y Pegar:**

- Ctrl+C para copiar cofre
- Ctrl+V para pegar en posición del mouse
- Indicador visual de portapapeles
- Copia completa de contenido

✅ **Sistema de Guardado:**

- Auto-guardado cada 5 segundos
- Guardado manual con tecla G
- Guardado al cerrar
- Auto-guardado de cantidades

✅ **Bases de Datos:**

- items_db.json actualizado (7 items nuevos)
- items_especiales_db.json (18 items)
- cofres_db.json completo
- Configuración de tipos de cofres

---

## 🚀 Próximas Mejoras Sugeridas

### Funcionalidades Pendientes

- [ ] **Scroll en listas de items** (mostrar más de 8 items)
- [ ] **Búsqueda/filtro de items** por nombre
- [ ] **Presets de cofres** (guardar/cargar configuraciones)
- [ ] **Miniaturas de items** en las listas
- [ ] **Validación visual** (advertir si cofre vacío)
- [ ] **Deshacer/Rehacer** (Ctrl+Z / Ctrl+Y)
- [ ] **Selección múltiple** de cofres
- [ ] **Alineación automática** (grid snap)
- [ ] **Duplicación rápida** (Ctrl+D)
- [ ] **Vista previa de sprites** de cofres

---

## 📞 Soporte

Para problemas o sugerencias, consulta:

- Documentación completa en `docs/`
- Código fuente: `editor_cofres.py`
- Archivos de configuración en `src/database/`

---

**¡Disfruta creando cofres épicos para CodeVerso RPG!** 🎮✨
