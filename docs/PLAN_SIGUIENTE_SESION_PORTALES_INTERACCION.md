# Plan siguiente sesion: Portales + Interaccion

## Objetivo de la siguiente sesion

Crear una nueva etapa de trabajo enfocada en:

- logica de portales,
- logica de interaccion,
- rescatar lo util de lo existente,
- y construir una version mejor (mas limpia y estable) en un nuevo `.py` y su `.bat`.

## Estado inicial para arrancar

- El plan de prefabs queda cerrado en [docs/RESUMEN_PLAN_PREFABS.md](RESUMEN_PLAN_PREFABS.md).
- Esta nueva etapa tomara como base ese resultado.
- Hay una base previa de portales que se va a evaluar primero (antes de rehacer).

## Registro completo de avances

Esta seccion resume todo lo que se fue construyendo y corrigiendo durante la etapa de portales + interaccion:

- Se planteo primero una base de prueba en vivo para colisiones y paso por delante / por detras antes de integrar portales al juego.
- Se exploro la idea de usar `constructor_prefabs.py` como lugar de demo visual para probar un personaje ejemplo en tiempo real.
- Luego se tomo la decision de no mezclar esa base con la logica de portales y de crear una herramienta separada para portales e interaccion.
- Se rescato la idea de una base nueva y se consolidaron dos modos de trabajo en `gestor_portales_interaccion_v2.py`: `audit` y `editor`.
- Se creo el lanzador `ejecutar_gestor_portales_interaccion_v2.bat` para abrir el flujo nuevo de forma directa.
- Se implemento el auditor de mapas para revisar `portales`, `spawns`, `interacciones`, `mapa_destino`, IDs duplicados y formas invalidas.
- Se agrego el modo `--fix` para correcciones seguras iniciales, como IDs faltantes y sincronizacion de `caja` en portales rectangulares.
- Se ajusto la validacion de `spawn_destino_id` para que compare contra el mapa destino real y no contra el mismo archivo.
- Se corrigieron enlaces invalidos entre mapas de prueba y mapas reales hasta dejar el audit estable.
- Se agrego el editor visual minimo con creacion, seleccion, movimiento, cambio de destino, cambio de spawn y guardado.
- Se paso luego a un editor mas completo con doble canvas: izquierda para origen y derecha para destino.
- Se incorporaron botones de ventana y acciones rapidas para crear, enlazar, eliminar, guardar e intercambiar mapas.
- Se sumaron buscadores y controles para navegar mapas de forma mas comoda.
- Se implemento la creacion de portales por arrastre y luego la edicion por seleccion directa.
- Se agrego el enlace ida / vuelta entre portales y la generacion automatica de `spawn_destino_id` en ambos sentidos.
- Se trabajo la visualizacion clara de portales enlazados con nombres y colores distintos para identificar parejas.
- Se incorporo la logica para separar enlaces con `Ctrl + click` y seleccionar ambos portales de una pareja con `Alt + click` para redimensionarlos juntos.
- Se agrego soporte para redimensionamiento individual y en pareja, manteniendo la coherencia visual y de datos.
- Se sincronizo el respawn con la caja del portal para que el punto de llegada coincida con el portal dibujado.
- Se ajusto el respawn para que el PJ reaparezca centrado dentro del portal solo al teletransportarse / respawnear.
- Se integro un personaje demo para probar teletransportes en vivo y verificar que el cruce funcione como se espera.
- Se corrigieron bucles de teletransporte y problemas de respawn mientras se iba refinando la experiencia de prueba.
- Se fue limpiando la experiencia de edicion hasta dejar una base mucho mas clara para seguir creciendo en sesiones futuras.

Estado actual de esa ruta:

- La base nueva quedo separada de la vieja.
- El audit quedo operativo y fue validado varias veces.
- El editor v2 quedo en un punto util para seguir iterando sobre portales, enlace y pruebas en vivo.

## Actualizacion de criterio (revision realizada)

Revision rapida de archivos existentes (sin cambios aplicados):

- `editor_portales.py` tiene logica funcional de crear/guardar/cargar portales y spawns.
- `ejecutar_portales.bat` ya ejecuta directo el editor de portales actual.
- Existen scripts de soporte/parche: `arreglar_validacion_portales.py`, `clean_portal_links.py`, `tools/find_problematic_portals.py`, `tools/test_portal_id_seq.py`.

Diagnostico:

- Si hay logica ya util, pero esta mezclada con parches historicos y utilidades quirurgicas.
- El flujo de validacion/guardado ya tuvo friccion (hay scripts para ajustar validaciones), senal de deuda tecnica.
- La base sirve para rescatar funciones, pero no conviene meter esta capa dentro de `constructor_prefabs.py`.

Decision recomendada para la siguiente etapa:

- Mantener `constructor_prefabs.py` enfocado en prefabs + demo visual de colision/sobreposicion.
- Implementar portales/interaccion en archivo separado (`gestor_portales_interaccion_v2.py`) y su lanzador (`ejecutar_gestor_portales_interaccion_v2.bat`).
- Reutilizar piezas de `editor_portales.py` por extraccion, no por copia completa del flujo actual.

Estado de accion:

- No aplicar cambios aun en codigo de portales.
- Primera tarea al retomar: auditoria dirigida de funciones de IO/validacion/enlace para decidir que se rescata y que se reescribe.

## Avance aplicado en esta sesion

Se creo la base separada `v2` (sin tocar el editor antiguo):

- `gestor_portales_interaccion_v2.py`
- `ejecutar_gestor_portales_interaccion_v2.bat`

Alcance actual de `v2`:

- Comando `audit` para revisar todos los JSON en `src/database/mapas`.
- Validacion de estructura de `portales`, `spawns` e `interacciones` (si existe).
- Chequeo de `mapa_destino` y formato de forma `rect/poly`.
- Chequeo de IDs duplicados o faltantes.
- Modo `--fix` para correcciones seguras iniciales:
	- asignar IDs faltantes en `spawn`/`portal`,
	- sincronizar `caja` con `x/y/w/h` en portales rectangulares.

Uso rapido:

- `python gestor_portales_interaccion_v2.py audit`
- `python gestor_portales_interaccion_v2.py audit --strict`
- `python gestor_portales_interaccion_v2.py audit --fix`

Nota:

- Esta base es de auditoria/normalizacion para estabilizar datos antes de construir la capa visual nueva de portales + interaccion.

## Estado actual validado

- Se ajustaron enlaces `spawn_destino_id` invalidos entre `mapa_pradera` y `mapa_pueblo_final`.
- Se mejoro `gestor_portales_interaccion_v2.py` para validar `spawn_destino_id` contra el mapa destino real (no contra el mismo archivo).
- Resultado de auditoria actual: `0 issues`, `0 warnings`, `0 errores`.

## Avance nuevo: editor visual minimo v2

Se agrego capa visual inicial en `gestor_portales_interaccion_v2.py` con subcomando `editor`.

Funciones incluidas:

- Crear portales rectangulares por arrastre (`N` + drag).
- Seleccionar portal con click.
- Mover portal arrastrando o con flechas (ajuste fino).
- Definir `mapa_destino` ciclando opciones (`M`).
- Definir `spawn_destino_id` del mapa destino (`P`).
- Eliminar portal seleccionado (`Del`).
- Guardar cambios al JSON actual (`S`).

Lanzador agregado:

- `ejecutar_gestor_portales_interaccion_v2_editor.bat`

Uso CLI:

- `python gestor_portales_interaccion_v2.py editor`
- `python gestor_portales_interaccion_v2.py editor --map mapa_pradera`

## Avance nuevo: doble canvas + botones

Se actualizo el editor para trabajar en dos mitades del canvas:

- Mitad izquierda: mapa de entrada (origen).
- Mitad derecha: mapa de llegada (destino).

Botones agregados en la barra superior:

- `Nuevo IZQ`
- `Nuevo DER`
- `Enlazar par ida/vuelta`
- `Eliminar`
- `Guardar`
- `Intercambiar`
- `<` y `>` para cambiar el mapa derecho

Flujo de portales interconectados:

- Se crea un portal en izquierda y otro en derecha.
- Con `Enlazar par ida/vuelta` ambos quedan conectados entre si.
- Se generan `spawn_destino_id` automaticamente en ambos mapas.
- Resultado: al cruzar desde A llegas a B y para volver usas el portal espejo en B.

## Archivos objetivo de esta nueva etapa

### Nuevo Python (propuesto)

- `gestor_portales_interaccion_v2.py`

### Nuevo BAT (propuesto)

- `ejecutar_gestor_portales_interaccion_v2.bat`

## Estrategia de trabajo

1. Revisar lo que ya existe
- Auditar archivos actuales de portales/interaccion para detectar que sirve y que no.
- Confirmar si la logica actual de portales funciona en casos reales.
- Identificar problemas de flujo, validacion y persistencia.

2. Definir contrato de datos
- Establecer formato JSON de portal (entrada/salida, destino, condiciones, flags).
- Establecer formato JSON de interaccion (accion, texto, evento, requisito, recompensa).
- Alinear estos datos con el mapa y con el flujo del juego.

3. Implementar nueva logica de portales
- Crear/editar portal.
- Validar conexiones (sin enlaces rotos).
- Resolver destino de forma robusta.
- Proveer mensajes de error claros para portales invalidos.

4. Implementar nueva logica de interaccion
- Detectar interaccion por proximidad o tecla.
- Definir acciones base reutilizables.
- Integrar eventos condicionales.
- Permitir mejora incremental sin romper mapas viejos.

5. Integrar con flujo del editor
- Cargar y guardar sin perder datos.
- Mantener compatibilidad con contenidos anteriores cuando sea posible.
- Dejar comandos claros para pruebas manuales.

6. Crear lanzador `.bat`
- Ejecutar el nuevo Python.
- Mostrar errores de forma legible.
- Dejar listo para uso rapido en siguientes sesiones.

## Criterios de terminado para esta etapa

- Se puede crear y editar portales de forma estable.
- Se puede configurar interaccion por objeto/NPC/evento de forma clara.
- Guardado y carga funcionan sin perder configuracion.
- Se valida la consistencia de enlaces de portales.
- Existe `.bat` funcional para lanzar el nuevo flujo.
- Queda documentado el uso minimo (teclas/acciones/guardado).

## Notas de diseño

- Se prioriza robustez y claridad por sobre agregar demasiadas features al inicio.
- Se rescata codigo util de implementaciones antiguas, pero se rehace lo que este fragil.
- Se busca que la nueva base quede lista para crecer en sesiones futuras.

## Siguiente paso al retomar

Al iniciar la proxima sesion:

1. Abrir este archivo como contexto principal.
2. Auditar archivos existentes de portales/interaccion.
3. Confirmar nombre final del nuevo `.py` y del `.bat`.
4. Empezar implementacion con una primera version funcional minima.
