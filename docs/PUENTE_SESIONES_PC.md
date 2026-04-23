# Puente de Sesiones entre PCs (Trabajo <-> Casa)

Fecha de ultima actualizacion: 2026-04-22 (PC Trabajo)

Estado de sesion: Avance activo en fase NPC evento batalla

Objetivo de este archivo:

- Este es el documento oficial para traspasar contexto entre computadores.
- Antes de cambiar de PC, actualizar este archivo con resumen claro de la sesion.
- Al abrir en el otro PC, leer primero este archivo y continuar desde aqui.

Regla de uso obligatorio:

1. Al cerrar sesion en un PC: actualizar secciones 1, 2, 3, 4 y 5.
2. Guardar cambios y subir al repo.
3. En el otro PC: bajar cambios y abrir este archivo antes de seguir.

---

## 1) ALERTA CRITICA DE TRASPASO (leer primero)

1. Estamos trabajando en paralelo entre PC Trabajo y PC Casa.
2. Ambos agentes deben usar ESTE archivo como fuente oficial de estado antes de tocar codigo.
3. No asumir estado sin leer este archivo: comercio/herrero ya tiene primera version funcional con submenu.
4. Si un agente implementa algo nuevo, debe dejar:

- archivos tocados,
- que hace cada cambio,
- que falta,
- como validarlo rapido.

5. Si no se actualiza este puente, se rompe sincronizacion entre sesiones y se corre riesgo de regresiones.
6. Si se agrega una libreria/dependencia nueva, hay que actualizar tambien la seccion 8 de este archivo y `requirements.txt`.

---

## 2) Estado tecnico real verificado en codigo

- Fase activa: **NPC evento batalla con canvas doble** (recién iniciada 2026-04-22).
- Archivos nuevos creados:
  - `gestor_npc_evento_batalla_v1.py` → Editor canvas doble con carga de sprites.
  - `ejecutar_gestor_npc_evento_batalla_v1.bat` → Lanzador.
  - `src/database/npc_evento_batalla_layouts.json` → Layouts globales por cantidad (1-5).
  - `src/database/npc_evento_batalla_por_mapa/` → Directorio para overrides por mapa.
  - `src/database/npc_evento_batalla_por_mapa/TEMPLATE_EJEMPLO.json` → Template de referencia.
- Paso 1 completado: marco UI, carga de mapas, carga de sprites de monstruos/heroes, dibujo de slots, guardado de config por mapa.
- Paso 3 funcional: slots 1..5, asignacion de enemigos a slots y reacomodo por drag de cajas en canvas batalla.
- Mejora UX aplicada: modo `Canvas Batalla XL` para ampliar area de posicionamiento y evitar vista comprimida.
- Flujo completo habilitado: seleccion en listas inferiores -> spawn en canvas mundo -> enlace por click derecho a slots del canvas batalla.
- Soporte dual de asignacion: flujo completo mundo->batalla y flujo rapido por teclas (`Space` enemigo, `H` heroe).
- Fix aplicado: corregido `ImportError` por constantes de pantalla no presentes en `src/config.py` (definicion local en el editor).
- Fix aplicado: corregidas rutas de carga de mapas (uso de `src/database/mapas_unificados` con fallback).
- Fase anterior (Vendedor/Herrero): cerrada y validada en sesion previa.

Decision de arquitectura para fondos de pelea:

- Batallas normales: fondo determinado por mapa/zona.
- Batallas de evento NPC: fondo especial desacoplado del mapa.
- Prioridad objetivo en runtime: `fondo_evento_npc -> fondo_por_mapa -> fallback global`.

Arreglo reciente (2026-04-20):

- **Portal a tienda_items reparado**: JSONs de mapas especiales movidos de `ciudades_y_pueblos/pueblo_inicio/` a `ciudades_y_pueblos/`.
- Todos los mapas afectados: tienda_items, tienda_magia, herrero, posada, pueblo_final, taberna.
- Verificacion: portal bidireccional pueblo_final <-> tienda_items carga correctamente.
- Runtime ahora encuentra portal cuando se carga el mapa.

Validacion manual final (2026-04-21):

- Vendedor verificado en runtime: cantidad, botones, tecla `ESPACIO`, total dinamico y compra/venta por lote funcionando.
- Herrero verificado en runtime: mejorar y forjar aplican costos, materiales y mensajes correctos.
- Persistencia de seleccion verificada: no se pierde el foco al confirmar transaccion.
- Portal y regreso al mapa verificados sin errores visibles.

Nuevo plan aprobado (2026-04-22):

- Se crea fase de NPC evento batalla con editor de canvas doble.
- Documento oficial de esta fase: `docs/PLAN_NPC_EVENTO_BATALLA_CANVAS_DOBLE.md`.
- Regla nueva: heroes usan distribucion espejo por cantidad (1..5), con cajas reacomodables y guardado global.
- Se agrega soporte de override por encuentro para boss centrado.

Avance reciente adicional (2026-04-20, UI comercio):

- Oro inicial de heroes ajustado a 100000 para pruebas de flujo de compra/venta.
- Se agrego visual de oro disponible durante submenu de comercio/herrero en runtime.
- Submenu de compra/venta ahora soporta cantidad por item (`cantidad_seleccionada`).
- Controles de cantidad habilitados con teclado `+` y `-`.
- Controles de cantidad habilitados tambien con botones visuales clickeables `[-] [xN] [+]`.
- Tecla `ESPACIO` habilitada para editar el numero directamente (confirmar con Enter, cancelar con ESC).
- Se muestra precio unitario y total dinamico por fila (`U:xxG T:yyG`).
- Transaccion aplica cantidad real en compra/venta (oro e inventario se actualizan por lote).
- Persistencia de seleccion: despues de comprar/vender se mantiene el item seleccionado en submenu.

Avance adicional Critico (UI Herrero Mejorada V2):

- **Tienda Herrero Arreglada**: Ahora el Herrero vende `MATERIALES_HERRERO` en lugar de pociones en la pestaña "Comprar".
- **Herrero y materiales**: La opción "Vender" del herrero abre el catálogo de materiales de forja para comprarlos, y la venta de inventario sigue disponible en el flujo compartido.
- **Mochila+Equipo en Herrero**: La UI de "Mejorar" (en `src/pantalla_mejora_herrero.py`) lista tanto el equipo en la **Mochila** como el **Equipado**.
- **Pop-Up Details Herrero**: Seleccionar un arma a mejorar abre un panel lateral con _Glassmorphism_ que compara stats e indica costo real en Oro y Materiales (resta inventario).
- **Adiós Pantalla Negra**: Se engancharon correctamente las subfunciones de la Pantalla de Mejora a `main.py`, eliminando loops o returns sin procesar que resultaban en crasheos al darle ESC/Mejorar.
- **Estabilidad de mejora**: Corregido `KeyError` en consumo de materiales al mejorar (cantidades 0 ignoradas de forma segura).
- **Limite de mejora**: Se fijo tope de mejora por equipo en `+5` y se informa cuando un equipo llega a maximo.
- **Recetas de forja ajustadas**: Las recetas del herrero ahora usan materiales de herreria en lugar de consumibles (eter/pociones).
- **UI de mejora con scroll**: Lista de equipos y detalle de materiales ahora soportan scroll y texto envuelto para no cortar lineas largas.
- **Tecla Q en dialogo NPC**: Se restauro retroceso de linea en conversaciones y retorno al dialogo base al salir del panel.

Integracion confirmada:

- `main.py`: importa `opciones_panel_por_modo`, `ejecutar_accion_panel`, `construir_submenu`, `ejecutar_accion_submenu`.
- `main.py`: gestiona `dialogo_npc_activo` y `panel_npc_activo`.
- `main.py`: en tecla E llama `mi_mapa.interactuar_objetos_interactivos(...)`.
- `main.py`: si hay panel activo llama `ejecutar_accion_panel(...)` y en submenu usa `ejecutar_accion_submenu(...)`.
- `src/mapa.py`: mantiene `chequear_portales`, `interactuar_objetos_interactivos`, `chequear_objeto_interactivo_cercano`.

---

## 3) Inventario explicito de archivos clave (que hace cada uno)

### Runtime principal

- `main.py`
  - Bucle principal, estados del juego, input global.
  - Maneja interaccion `E` con objetos/NPC/cofres.
  - Dibuja y controla panel/dialogo NPC en mapa.
- `src/mapa.py`
  - Carga mapa y capas de colision.
  - Carga objetos interactivos del editor y evalua objeto cercano.
  - Resuelve portales y chequeo de cofres cercanos.

### NPC runtime

- `src/npc_comercio_herrero.py`
  - Define opciones de panel por modo NPC.
  - Expone `construir_submenu()` y `ejecutar_accion_submenu()`.
  - Implementa compra/venta (oro + inventario), mejora de equipo equipado y forja por recetas/materiales.
- `src/npc_eventos_batalla.py`
  - Hook de evento NPC.
  - Para modo `evento` devuelve estructura para disparar batalla futura.

### Editores/herramientas separadas (standalone)

- `gestor_interfaz_npc_v1.py`
  - Editor visual de NPC por mapa (dialogos, modos, presets de ventana).
  - Guarda configuraciones para uso futuro.
- `gestor_objetos_interaccion_v1.py`
  - Herramienta de objetos interactivos (cofres/puertas/botones/NPC base), validacion/flujo editor.
- `gestor_portales_interaccion_v2.py`
  - Auditor + editor de portales/interaccion v2, separado del runtime principal.
- `constructor_prefabs.py`
  - Constructor visual de prefabs (componer piezas, capa visual, export png/json).
- `visualizador_recursos.py`
  - Herramienta de recursos/sprites (recortes, atlas, organizacion).

---

## 4) Que se creo y que se toco en la linea de trabajo actual

Archivos tocados en la fase actual (segun docs + integracion verificada):

- `main.py`
- `src/mapa.py`
- `src/npc_comercio_herrero.py`
- `src/npc_eventos_batalla.py`
- `gestor_interfaz_npc_v1.py`
- `gestor_npc_evento_batalla_v1.py`
- `ejecutar_gestor_npc_evento_batalla_v1.bat`
- `src/database/npc_evento_batalla_layouts.json`
- `src/database/npc_evento_batalla_por_mapa/TEMPLATE_EJEMPLO.json`
- `docs/PLAN_CERRADO_OBJETOS_INTERACCION.md`
- `docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md`
- `docs/PLAN_NPC_EVENTO_BATALLA_CANVAS_DOBLE.md`
- `docs/PUENTE_SESIONES_PC.md`

Archivos tocados en el ultimo ajuste de comercio (2026-04-20):

- `main.py`
- `src/npc_comercio_herrero.py`
- `src/database/heroes_db.json`
- `docs/PUENTE_SESIONES_PC.md`
- `docs/PLAN_FASE_VENDEDOR_HERRERO_V2.md`
- `docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md`

Archivos tocados en el ultimo ajuste de estabilidad/UI de herrero (2026-04-20):

- `main.py`
- `src/heroe.py`
- `src/npc_comercio_herrero.py`
- `src/pantalla_mejora_herrero.py`
- `src/database/items_db.json`
- `docs/PLAN_CERRADO_OBJETOS_INTERACCION.md`
- `docs/PUENTE_SESIONES_PC.md`
- `docs/PLAN_FASE_VENDEDOR_HERRERO_V2.md`
- `docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md`

Archivos creados/modulares en esta etapa (herramientas nuevas separadas):

- `gestor_portales_interaccion_v2.py`
- `constructor_prefabs.py`
- `visualizador_recursos.py`
- lanzadores `.bat` asociados (segun hoja de ruta en docs)

Nota importante:

- Estos modulos de herramienta NO reemplazan automaticamente el flujo runtime de `main.py`; son bases de trabajo separadas.

---

## 5) Lista de tareas heredadas (del otro agente + docs vigentes)

### Prioridad inmediata (hacer primero)

1. Ejecutar Plan V2 de Vendedor/Herrero (documento oficial):

- `docs/PLAN_FASE_VENDEDOR_HERRERO_V2.md`
- Orden obligatorio: primero Vendedor, luego Herrero.

2. Cerrar puntos CRITICOS de flujo transaccional:

- Integridad de compra/venta/mejora/forja (sin duplicados/perdidas).
- Persistencia de inventario/equipo/oro al confirmar.
- Validacion de oro/materiales/cantidad + cancelacion segura.

3. Mantener coherencia de control runtime:

- Con panel/dialogo NPC activo, el heroe no debe moverse.
- Cerrar/reabrir panel/dialogo sin estados colgados.

### Prioridad media

4. Filtros avanzados por categoria en comercio.
5. Mejoras de mensajeria contextual.
6. Ajuste de balance inicial de precios/costos.

### Siguiente fase

7. Conectar `src/npc_eventos_batalla.py` a batalla real contra NPC.
8. Iniciar fase de unificacion combate/magias tras cierre Vendedor/Herrero.

---

## 6) Proximo paso exacto al retomar en cualquier PC

1. Hacer pull.
2. Abrir este archivo (`docs/PUENTE_SESIONES_PC.md`) antes de tocar codigo.
3. Abrir y seguir `docs/PLAN_NPC_EVENTO_BATALLA_CANVAS_DOBLE.md`.
4. Continuar por orden:

- Paso 2 mundo: arrastre NPC en canvas izquierdo y guardado de posicion/sprite.
- Paso 4 layout: reforzar guardado/carga override con prioridad `override -> global -> default`.
- Paso 5 enlace: guardar decision final `Pelear ahora / Aun no`.

6. Dejar en este puente:

- archivos tocados,
- que quedo funcionando,
- que falta,
- validacion realizada.

7. Estado actual tras validacion:

- Comercio vendedor: cerrado y validado.
- Herrero: cerrado y validado.
- NPC evento batalla: Paso 1 completado + Paso 3 funcional + modo Canvas Batalla XL aplicado.
- Flujo de enlace operativo: mundo (izq) a batalla (der) con validacion por tipo (`enemigo->E`, `heroe->H`).
- Siguiente foco sugerido: completar Paso 2 y cierre de Paso 4.

8. Orden sugerido de arranque para la nueva fase:

- Paso critico 1: crear `gestor_npc_evento_batalla_v1.py` y su `.bat`.
- Paso critico 2: habilitar canvas doble (mundo + preview batalla) con grilla alineada al juego.
- Paso critico 3: guardar/cargar layouts globales por cantidad (1..5).
- Paso alto 1: drag de cajas y override de boss centrado.
- Paso alto 2: enlace NPC evento (mundo) con NPC evento batalla (preview derecho).

9. Regla de seguimiento cruzado (OBLIGATORIA):

- Si se avanza algo en la otra PC, registrar ese avance aqui mismo en seccion 2 (resumen tecnico) y seccion 4 (archivos tocados).
- Marcar el progreso del plan en `docs/PLAN_NPC_EVENTO_BATALLA_CANVAS_DOBLE.md` usando casillas `[x]` para lo completado.
- Antes de cerrar cada PC: commit + push + nota corta de validacion.

---

## 7) Plantilla corta para proxima transferencia

Copiar y reemplazar al final de cada sesion:

---

Fecha:
PC origen: Trabajo o Casa

## Hecho hoy:

-
-

## Archivos tocados:

-

Validado:

- py_compile:
- prueba manual:

## Pendiente siguiente:

-

## Bloqueos o riesgos:

---

---

## 8) Dependencias del proyecto (instalacion obligatoria)

Estado del entorno validado en esta sesion (PC Casa):

- Entorno Python: `.venv` del proyecto.
- Version Python: 3.12.4
- Archivo fuente de dependencias: `requirements.txt`

Dependencias activas del proyecto:

- `pygame>=2.0.0` (motor del juego)
- `requests>=2.33.0` (descarga/consumo HTTP en scripts de apoyo)
- `beautifulsoup4>=4.14.0` (parseo HTML en scripts de scraping)
- `pytest>=7.0.0` (testing)
- `pytest-cov>=4.0.0` (cobertura)
- `pytest-mock>=3.10.0` (mocks para pruebas)

Instalacion recomendada (siempre dentro de la carpeta del proyecto):

1. Crear entorno virtual (si no existe):

- Windows PowerShell:
  - `py -3.12 -m venv .venv`

2. Activar entorno:

- Windows PowerShell:
  - `.\.venv\Scripts\Activate.ps1`

3. Instalar dependencias:

- `python -m pip install --upgrade pip`
- `python -m pip install -r requirements.txt`

Verificacion minima rapida:

- `python -m py_compile main.py src/mapa.py src/npc_comercio_herrero.py src/npc_eventos_batalla.py`

Regla de documentacion de nuevas dependencias (OBLIGATORIA):

1. Si se agrega una libreria nueva, actualizar `requirements.txt` en el mismo commit.
2. Agregar en esta seccion 8:

- nombre del paquete,
- version minima,
- para que se usa.

3. En el cierre de sesion, anotar en "Hecho hoy" que se agrego dependencia nueva.

Nota de escaneo tecnico:

- Si aparece `mapa` como "missing" en algun escaneo de imports, no es paquete de pip; es un import local y se corrige en codigo/rutas, no con instalacion de libreria.

---

## 9) Prioridades vigentes (resumen rapido)

Critico:

- Integridad transaccional y persistencia correcta.
- Validaciones de oro/materiales/cantidad.

Alto:

- UI grande de Vendedor (dos columnas + carrito + total dinamico).
- UI grande de Herrero (mejorar/forjar + comparador Antes vs Despues).

Medio:

- Filtros por categoria, mensajeria contextual, balance fino.

Bajo:

- Animaciones, sonidos extra, pulidos visuales no funcionales.
