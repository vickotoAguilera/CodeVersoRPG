# README de trabajo de hoy

Este documento resume los 2 scripts Python y los 2 lanzadores BAT que se trabajaron hoy para el flujo de prefabs y el flujo unificado de mapas/sprites.

## Archivos incluidos

- [constructor_prefabs.py](../constructor_prefabs.py)
- [visualizador_recursos.py](../visualizador_recursos.py)
- [ejecutar_constructor_prefabs.bat](../ejecutar_constructor_prefabs.bat)
- [ejecutar_editor_unificado.bat](../ejecutar_editor_unificado.bat)

## Respuesta tecnica sobre superposicion y colision

Si, se puede hacer.

La idea correcta es separar dos conceptos:

- Colision real: si el jugador choca o no con el objeto.
- Orden visual / profundidad: si el jugador se dibuja delante o detras del objeto.

Con eso se puede lograr:

- que un NPC o un objeto bloquee el paso normalmente,
- que otro objeto tenga una capa de sobreposicion,
- que el jugador pase "por atras" de una casa o arbol,
- que cofres, estatuas o decoracion queden escondidos detras de estructuras,
- y que una tecla como Tab cambie el estado de profundidad o capa.

La forma mas practica es guardar una bandera como:

- `bloquea_jugador`
- `sobrepuesto`
- `capa_visual`

Y al renderizar:

- dibujar primero la capa de fondo,
- luego al jugador,
- luego los elementos sobrepuestos.

## constructor_prefabs.py

### Proposito

Constructor visual para armar prefabs compuestos a partir de sprites, tiles o piezas ya existentes. Permite mover, redimensionar, pegar, despegar, cambiar profundidad y guardar el resultado como PNG + JSON.

### Clases

- `PiezaPrefab`
- `ConstructorPrefabs`

### Funciones de `PiezaPrefab`

- `__init__`: crea la pieza con posicion, rotacion, espejo, escala, grupo y capa visual.
- `get_surface`: devuelve la superficie procesada con escala, flip y rotacion.
- `get_rect`: devuelve el rectangulo actual visible de la pieza.
- `to_dict`: serializa la pieza a JSON incluyendo posicion, capa, grupo, escala y flags.

### Funciones de `ConstructorPrefabs`

- `__init__`: inicializa Pygame, paneles, estados, recursos y seleccion.
- `_aplicar_modo`: activa modo agregar, mover, rotar, espejo, borrar o pegar.
- `_actualizar_preview_recurso`: actualiza la vista previa del recurso seleccionado.
- `_alternar_fullscreen`: alterna entre pantalla normal y fullscreen.
- `_rect_barra_superior`: devuelve el rectangulo de la barra superior.
- `_set_mensaje`: muestra mensajes temporales en pantalla.
- `_cargar_carpetas`: carga las carpetas de recursos disponibles dentro de `assets`.
- `_cargar_recursos`: escanea sprites e imagenes desde las carpetas activas.
- `_elegir_carpeta`: abre el selector de carpeta dentro de `assets`.
- `_elegir_archivo_imagen`: abre un selector de imagen para cargar mapa de fondo.
- `_elegir_archivo_json`: abre un selector de JSON para cargar prefabs guardados.
- `_cargar_mapa_fondo`: carga una imagen de fondo para el lienzo.
- `_resolver_ruta_recurso`: resuelve rutas guardadas en JSON a una ruta real del proyecto.
- `_cargar_prefab_desde_json`: importa un prefab guardado y lo selecciona completo en la escena actual.
- `_buscar_pieza_por_pos`: detecta la pieza bajo el mouse.
- `_cargar_pieza_desde_recurso`: agrega una pieza nueva al lienzo desde un recurso.
- `_snap`: alinea valores a la grilla si el snap esta activo.
- `_seleccion_multiple_rects`: construye una seleccion por rectangulo.
- `_mover_piezas_seleccionadas`: mueve todas las piezas seleccionadas a la vez.
- `_escalar_seleccion`: escala la seleccion con la rueda del mouse.
- `_tiradores_para_rect`: genera los 8 tiradores de redimensionado.
- `_rect_seleccion_canvas`: calcula el rectangulo envolvente de la seleccion multiple.
- `_iniciar_redimension`: inicia el redimensionado de una pieza o de un grupo.
- `_actualizar_redimension`: aplica el cambio real de tamanio mientras arrastras.
- `_actualizar_indices_seleccion`: recalcula indices despues de reordenar piezas.
- `_enviar_seleccion_a_fondo`: manda la seleccion al fondo visual.
- `_traer_seleccion_al_frente`: trae la seleccion al frente visual.
- `_alternar_profundidad_seleccion`: alterna entre fondo y frente con Shift.
- `_pegar_seleccion`: agrupa la seleccion como bloque.
- `_despegar_seleccion`: separa las piezas del bloque seleccionado.
- `_copiar_seleccion`: copia la seleccion al portapapeles interno.
- `_pegar_portapapeles_en`: pega el bloque copiado en una posicion concreta.
- `_pegar_portapapeles_con_offset`: pega con desplazamiento automatico.
- `_guardar_prefab`: exporta PNG + JSON del prefab actual.
- `_max_scroll_lista`: calcula el limite maximo del scroll del panel izquierdo.
- `_max_scroll_panel`: calcula el limite maximo del scroll del panel derecho.
- `_dibujar_panel_izquierdo`: dibuja recursos, preview y lista scrolleable.
- `_dibujar_panel_derecho`: dibuja opciones, acciones y texto de ayuda.
- `_dibujar_barra_superior`: dibuja botones de ventana y titulo.
- `_dibujar_canvas`: renderiza fondo, grilla, piezas, capas y tiradores.
- `manejar_eventos`: procesa clicks, rueda, teclado, arrastre, pegado y redimensionado.
- `dibujar`: refresca toda la interfaz.
- `ejecutar`: arranca el bucle principal.

### Funciones clave ya resueltas hoy

- Multi-seleccion con Ctrl + click izquierdo.
- Pegar / Despegar seleccion para unir o separar piezas.
- Profundidad con Shift para mandar fondo/frente.
- Escalado con rueda del mouse.
- Redimensionado con tiradores en lados y esquinas.
- Redimensionado proporcional con Alt en tiradores de esquina.
- Carga de prefab JSON sobre la escena actual, dejando todo seleccionado.
- Scroll con limites para que no se salga el contenido de los paneles.

## visualizador_recursos.py

### Proposito

Editor maestro de sprites y recursos. Sirve para cortar, organizar, seleccionar, previsualizar y generar atlas o fragmentos a partir de sheets o imagenes grandes.

### Clases

- `FrameData`
- `Fragmento`
- `EditorMaestroSprites`

### Funciones de `FrameData`

- `__init__`: crea un frame con posicion, tamanio y estado usado.
- `get_rect`: devuelve el rect del frame.

### Funciones de `Fragmento`

- `__init__`: guarda el rect original y la posicion virtual en el canvas.

### Funciones de `EditorMaestroSprites`

- `__init__`: prepara UI, paneles, carpetas, acciones, grid y estado general.
- `reordenar_ui`: recalcula las zonas del editor segun el tamano de ventana.
- `_ruta_relativa_assets`: devuelve la ruta relativa dentro de `assets`.
- `_texto_ruta_assets`: convierte una ruta a texto legible para UI.
- `_elegir_carpeta_assets`: abre selector de carpeta restringido a `assets`.
- `_actualizar_barra_carpetas`: limpia, valida y ordena la barra de carpetas.
- `_guardar_preferencias_ui`: guarda configuracion visual y rutas.
- `_cargar_preferencias_ui`: restaura configuracion visual y rutas guardadas.
- `_agregar_carpeta_barra`: agrega una carpeta a la barra persistente.
- `_quitar_carpeta_barra`: elimina una carpeta de la barra persistente.
- `_selector_guardado_actual`: devuelve el destino actual de guardado.
- `_escanear_recursos`: busca recursos en carpetas activas.
- `actualizar_lista_categoria`: filtra recursos segun categoria activa.
- `_actualizar_carpetas_destino`: actualiza la lista de carpetas disponibles como destino.
- `_ruta_destino_actual`: devuelve la carpeta de salida activa.
- `_nombre_limpio`: limpia nombres para guardar archivos.
- `_accion_actual`: devuelve la accion seleccionada.
- `_rects_acciones`: construye las zonas clicables de acciones.
- `cargar_sheet`: carga una imagen/sheet en memoria.
- `_get_canvas_coords`: convierte coordenadas de pantalla a canvas.
- `_get_image_coords`: convierte coordenadas virtuales a coordenadas de imagen.
- `_get_screen_coords`: convierte coordenadas virtuales a pantalla.
- `_generar_grid_completo`: crea la grilla completa de frames.
- `manejar_eventos`: procesa clicks, drag, scroll, seleccion y cortes manuales.
- `_get_frame_por_punto`: obtiene el frame bajo un punto.
- `_update_caja_seleccion`: actualiza la caja de seleccion activa.
- `_aplicar_corte_manual`: aplica el recorte manual del area seleccionada.
- `auto_detectar_sprites`: detecta sprites automaticamente en la imagen.
  - `is_background`: funcion interna para detectar fondo.
  - `merge_sprites`: funcion interna para fusionar detecciones cercanas.
- `_set_mensaje`: muestra mensajes temporales en la UI.
- `generar_atlas`: construye el atlas de salida.
- `toggle_animacion`: activa o desactiva la previsualizacion animada.
- `_tick_animacion`: avanza la animacion segun FPS.
- `toggle_grid`: activa o desactiva la grilla.
- `_guardar_seleccion`: guarda la seleccion actual.
- `dibujar`: renderiza toda la interfaz del editor.
- `ejecutar`: arranca el bucle principal.

### Funciones clave ya resueltas en este flujo

- Barra de carpetas persistente.
- Guardado y carga de preferencias.
- Seleccion y corte manual.
- Auto-deteccion de sprites.
- Generacion de atlas.
- Vista de animacion.
- UI para seleccionar carpeta destino dentro de `assets`.

## ejecutar_constructor_prefabs.bat

### Proposito

Lanzador del constructor de prefabs.

### Flujo

- Cambia al directorio actual del proyecto.
- Limpia pantalla.
- Muestra resumen de funciones.
- Ejecuta `python constructor_prefabs.py`.
- Informa si termino con error o correctamente.

### Funcion real

Este BAT no tiene funciones internas de Python; solo hace de lanzador del script principal.

## ejecutar_editor_unificado.bat

### Proposito

Lanzador del editor unificado de mapas.

### Flujo

- Limpia pantalla.
- Muestra el objetivo del editor.
- Ejecuta `python editor_unificado.py`.
- Informa si el archivo unificado se genero correctamente o si hubo error.

### Funcion real

Tampoco tiene funciones internas propias; su trabajo es iniciar el editor unificado y mostrar estados basicos.

## Notas de uso

- Si quieres mover un prefab cargado, queda seleccionado al importar.
- Si quieres borrar o reubicar elementos importados, puedes hacerlo antes de guardar de nuevo.
- Si quieres pasar un objeto o NPC por detras de una casa, la solucion correcta es manejar una capa de profundidad y una bandera de colision separadas.
- Si quieres, Tab puede usarse como atajo para alternar el estado de sobreposicion o profundidad visual.

## Siguiente paso recomendado

- Unificar la logica de colision y capas para objetos, NPCs, cofres y casas.
- Definir una bandera por elemento para indicar si bloquea al jugador o si solo va en capa de fondo.
- Crear un editor visual de capas para alternar rapidamente entre frente y fondo.
