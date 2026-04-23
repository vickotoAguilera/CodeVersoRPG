# Plan NPC Evento Batalla - Canvas Doble

Fecha: 2026-04-22
Estado: En implementacion (Paso 1 completado, Paso 3 funcional)

Seguimiento: Este plan se actualiza desde cualquier PC. Lo completado se marca con `[x]` y se refleja tambien en `docs/PUENTE_SESIONES_PC.md`.

## 1) Objetivo

Crear un editor nuevo (py + bat) para configurar NPC de evento de batalla usando dos canvas en una sola pantalla:

- Canvas izquierdo: mapa del mundo (NPC fisico en mapa real).
- Canvas derecho: preview de batalla (enemigos vs heroes).

La batalla real se ejecuta en runtime del juego; este editor solo prepara datos y enlaces.

## 2) Decisiones cerradas

1. El nuevo py sera editor, no runtime completo de batalla.
2. Se usara formato compatible con NPC interactivo, con campos extra de batalla.
3. El canvas derecho sera preview/configuracion visual (no combate real dentro del editor).

## 3) Reglas de posicionamiento (nueva solicitud)

### 3.1 Heroes en espejo de logica de enemigos

- Los heroes tomaran distribucion equivalente por cantidad, igual que la logica de enemigos:
  - 1 unidad: centrado vertical.
  - 2 unidades: uno arriba y uno abajo.
  - 3/4/5 unidades: distribucion automatica por slots.

### 3.2 Cajas reacomodables y persistencia global

- El editor mostrara cajas de slots (1..5) para lado enemigo y lado heroe.
- Se podran reacomodar por drag and drop.
- Las posiciones ajustadas quedaran guardadas como layout global por cantidad (1..5).
- Habra override por encuentro (ejemplo boss centrado especial).

### 3.3 Boss centrado

- Se habilita posicion personalizada para boss (slot unico o principal) sin perder layout global.
- Prioridad de uso:
  1. Override del encuentro actual.
  2. Layout global por cantidad.
  3. Layout por defecto del sistema.

## 4) Flujo de edicion en el nuevo editor

1. Cargar mapa/base para canvas izquierdo.
2. Arrastrar sprite NPC al mapa real.
3. Definir sprite normal y sprite espejo del NPC.
4. Configurar dialogo basico + botones finales:
   - Pelear ahora
   - Aun no
5. En canvas derecho:
   - elegir cantidad de enemigos (1..5)
   - colocar sprites enemigos en slots
   - preview de heroes auto-posicionados
   - permitir reacomodo manual de cajas (si se quiere)
6. Guardar enlace de NPC mundo <-> NPC batalla.

## 5) Controles clave

- W/S o flechas para navegar.
- Click izquierdo para seleccionar/arrastrar.
- Click derecho para menu contextual de enlace.
- Ctrl + Alt + Click derecho sobre sprite NPC batalla: alternar espejo horizontal.
- Q para retroceder dialogo/pantalla previa cuando aplique.

Controles implementados en esta iteracion:

- `F`: alterna modo Canvas Batalla XL (agranda area de ajuste de cajas).
- `+` / `-`: cambia cantidad de enemigos (1..5).
- `Left/Right`: cambia monstruo actual del catalogo.
- `Space`: asigna monstruo actual a un slot libre.
- `Drag` con mouse: mueve cajas de enemigos y heroes en el canvas de batalla.
- `G`: guarda layout global de la cantidad actual.
- `Enter`: guarda override por mapa actual.

Flujo operativo actual (mundo -> batalla):

1. Elegir mapa desde la lista inferior (`W/S` o click).
2. Elegir enemigo o heroe desde buscadores inferiores.
3. Click en canvas izquierdo para crear objeto en mundo (spawn).
4. Arrastrar objeto en canvas izquierdo para ajustar posicion.
5. Seleccionar objeto del mundo y hacer click derecho sobre slot del canvas derecho para enlazar.
6. Guardar con `G` (layout global) o `Enter` (override por mapa).

Flujo rapido (sin pasar por mundo):

- `Space`: asigna enemigo actual al primer slot enemigo libre.
- `H`: asigna heroe actual al primer slot heroe libre.

Reglas de enlace:

- Objeto tipo enemigo solo enlaza a slots `E`.
- Objeto tipo heroe solo enlaza a slots `H`.
- Si el tipo no coincide, no se aplica enlace.

Estrategia de fondos de pelea (acordada):

1. Fondo por mapa para batallas normales.
2. Fondo por evento NPC para peleas especiales no ligadas al mapa.
3. Prioridad recomendada en runtime: `fondo_evento_npc -> fondo_por_mapa -> fallback`.

## 6) Archivos a crear

1. gestor_npc_evento_batalla_v1.py
   - Editor canvas doble.

2. ejecutar_gestor_npc_evento_batalla_v1.bat
   - Lanzador del editor.

3. src/database/npc_evento_batalla_layouts.json
   - Layouts globales por cantidad (1..5) y por lado.

4. src/database/npc_evento_batalla_por_mapa/<mapa>.json
   - Overrides por NPC/encuentro (incluye boss centrado si corresponde).

## 7) Prioridades

### Critico

1. Canvas doble funcional con coordenadas reales de mapa.
2. Guardado/carga de layouts globales por cantidad.
3. Enlace NPC mundo con NPC batalla sin romper runtime actual.
4. Opcion Pelear ahora / Aun no persistente y estable.

### Alto

1. Drag and drop de sprites y de cajas de slots.
2. Soporte de espejo del sprite con atajo pedido.
3. Preview claro de heroes y enemigos con nombres enlazados.
4. Override de boss centrado por encuentro.

### Medio

1. Buscador/listado de sprites mejorado.
2. Mensajeria contextual de errores/guardado.
3. Previews secundarios de sprite (zoom simple).

### Bajo

1. Animaciones cosmeticas del editor.
2. Temas visuales alternativos.
3. Atajos extra no criticos.

## 8) Plan de implementacion por pasos

Checklist rapido de ejecucion (tachar al completar):

- [x] Paso 1 base completado (py + bat + marco UI + carga mapa izquierdo)
- [ ] Paso 2 mundo completado (arrastre NPC + guardado posicion/sprite)
- [x] Paso 3 batalla preview completado (slots 1..5 + auto-layout heroes)
- [ ] Paso 4 layout global/override completado (global + boss centrado)
- [ ] Paso 5 enlace/dialogo completado (Pelear ahora / Aun no)
- [ ] Paso 6 integracion runtime completado (hook evento -> batalla)

Avance implementado hoy:

- Creado `gestor_npc_evento_batalla_v1.py` y `ejecutar_gestor_npc_evento_batalla_v1.bat`.
- Carga de mapas disponibles y selector navegable.
- Carga de monstruos desde DB y asignacion a slots.
- Cajas de enemigos y heroes reacomodables por drag en canvas de batalla.
- Modo Canvas Batalla XL para ajuste fino de posiciones sin comprimir vista.
- Guardado global por cantidad y guardado por mapa para override base.

### Paso 1 (base)

- Crear py + bat del editor.
- Dibujar marco UI con dos canvas y barra inferior.
- Cargar mapa en canvas izquierdo.

### Paso 2 (mundo)

- Arrastre de NPC en mapa izquierdo.
- Guardar posicion y sprite base.

### Paso 3 (batalla preview)

- Canvas derecho con slots 1..5 lado enemigo.
- Auto-layout de heroes por cantidad.
- Selector de cantidad de enemigos (1..5).

### Paso 4 (layout global + override)

- Guardar layouts globales por cantidad.
- Guardar override por encuentro para boss.
- Cargar prioridad override -> global -> default.

### Paso 5 (enlace y dialogo final)

- Configurar texto final y botones Pelear ahora / Aun no.
- Guardar enlace NPC evento (izq) y NPC evento batalla (der).

### Paso 6 (integracion runtime)

- Consumir JSON desde hook de evento batalla existente.
- Validar transicion estable desde dialogo a batalla real.

## 9) Criterios de aceptacion

1. Se puede crear un NPC evento en mapa y enlazar su version de batalla.
2. Con 1/2/3/4/5 enemigos, cajas y posiciones se ven correctas.
3. Heroes se acomodan automaticamente en espejo logico de enemigos.
4. Layout global se guarda y se reutiliza en nuevos encuentros.
5. Override de boss centrado funciona sin romper el global.
6. Runtime reconoce Pelear ahora / Aun no correctamente.
