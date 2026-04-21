# Plan siguiente sesion: Objetos interactivos

## Documento puente entre PCs

Leer y actualizar siempre este archivo antes de cambiar de computador:
- [docs/PUENTE_SESIONES_PC.md](PUENTE_SESIONES_PC.md)

Uso recomendado:
1. Terminar sesion en este PC.
2. Actualizar [docs/PUENTE_SESIONES_PC.md](PUENTE_SESIONES_PC.md) con resumen claro.
3. Hacer push.
4. En el otro PC, hacer pull y abrir primero [docs/PUENTE_SESIONES_PC.md](PUENTE_SESIONES_PC.md).

## Objetivo

Crear una nueva herramienta para objetos seleccionables e interactivos del mapa, empezando por:

- cofres,
- puertas,
- mensajes de bloqueo por falta de llave,
- cambio visual de estado al abrir o desbloquear,
- y persistencia simple de estado.

## Base que se rescata del codigo actual

Lo que ya existe y conviene rescatar casi tal cual:

- [src/cofre.py](../src/cofre.py): ya resuelve cofres con `requiere_llave`, apertura y cambio de sprite.
- [src/heroe.py](../src/heroe.py): `inventario_especiales` ya guarda llaves y otros items persistentes.
- [src/pantalla_cofre.py](../src/pantalla_cofre.py): sirve como referencia de ventana/popup para feedback al jugador.
- [src/mapa.py](../src/mapa.py): ya carga cofres desde JSON y detecta cofres cercanos.
- [main.py](../main.py): ya existe la entrada de interacción con `E` para cofres.
- [src/database/items_db.json](../src/database/items_db.json): ya define llaves por tipo (`LLAVE_BRONCE`, `LLAVE_PLATA`, `LLAVE_ORO`).
- [src/database/items_especiales_db.json](../src/database/items_especiales_db.json): ya define llaves persistentes como items especiales.

## Lo que ya quedó confirmado

- Las llaves no se consumen al verificar un cofre.
- `inventario_especiales` es el lugar correcto para guardar llaves permanentes.
- Una llave puede abrir varias puertas o cofres del mismo tipo.
- El flujo actual de cofres ya separa "no tengo llave" de "sí tengo llave".
- El cambio de sprite al abrir ya existe en cofres y puede reutilizarse para puertas.

## Estado actual del editor V1

- El editor visual ya abre con canvas, panel derecho y fondo seleccionable.
- La lista de sprites muestra miniaturas y vista previa del sprite seleccionado.
- Las tres cajas superiores ya funcionan como contenedores reales de sprite.
- Un sprite no se duplica entre cajas: al asignarlo a una nueva, sale de la anterior.
- El modo `Enlazar` queda como flujo real: seleccionar fuente en el canvas y confirmar destino con click derecho.
- Los sprites del canvas llevan nombre visible para distinguir cuál se está moviendo o enlazando.
- Se agregó heroe de prueba en canvas con movimiento `WASD` e interaccion con `E`.
- Se corrigio que el click derecho no reasigna sprites en cajas: solo confirma enlaces.
- La asignacion de sprites en cajas queda solo con click izquierdo.
- Se incorporo logica boton->objeto: al interactuar con un boton enlazado, el cofre/puerta objetivo cambia automaticamente al sprite `ABIERTO`.
- Nuevo flujo de enlace para esta logica: click izquierdo objetivo, click izquierdo boton, click derecho en caja `ABIERTO`.
- Se agrego escalado de sprites del canvas: `+`/`-` y rueda del mouse (sobre canvas) para agrandar/achicar el sprite seleccionado.
- El boton `Eliminar` ahora borra el sprite seleccionado y limpia los enlaces dependientes para forzar un nuevo enlace manual.
- El sistema soporta multiples conexiones simultaneas en el mismo mapa (varios cofres enlazados a distintos botones) sin romper enlaces previos.
- Nuevo atajo de capa en editor: `Tab + clic derecho` sobre un objeto seleccionado cicla entre `colision`, `detras` y `adelante`.
- La capa `colision` bloquea el paso.
- `detras`: el jugador pasa por detras del objeto (el objeto se dibuja SOBRE el jugador).
- `adelante`: el jugador pasa por delante del objeto (el objeto se dibuja BAJO el jugador).

## Estado persistencia por mapa (implementado en editor)

La persistencia por mapa ya se implemento en el editor V1.

- Guardado por mapa desde el boton `Guardar`.
- Carga manual por JSON desde `Intercambiar`.
- Carga automatica al seleccionar fondo: si existe JSON del mapa, restaura estado; si no existe, limpia para mapa nuevo.
- Persistencia de: cajas superiores, objetos del canvas, tipo de objeto, sprite base/abierto, enlaces y trigger por boton.
- Carpeta de salida: `src/database/objetos_interactivos_mapas/`.

Pendiente de esta fase:

- Integrar esta misma lectura/escritura en el runtime principal del juego (`main.py`/`mapa.py`) para persistencia jugable completa.

## Registro de esta sesion

Se cerro y ajusto lo siguiente durante esta sesion:

- Se corrigio la carga runtime de objetos interactivos por mapa.
- Se agregaron logs de diagnostico para distinguir entre JSON ausente, JSON vacio y JSON cargado.
- Se alineo la semantica de capas con el constructor de prefabs: `detras` pasa por detras del jugador, `adelante` pasa por delante, `colision` bloquea.
- Se corrigio la coordenada editor -> juego usando `map_x`, `map_y`, `map_w`, `map_h`.
- Se desactivo el debug visual de rectangulos en juego normal.
- Se ajustaron hitboxes de objetos interactivos para que queden mas pegadas al sprite.
- Se mejoro la interaccion con `E` para que priorice objetos nuevos del editor V1 y siga usando los cofres antiguos como fallback.
- Se agrego un boton `Reiniciar` en el editor para volver todos los objetos del canvas a estado cerrado sin romper enlaces.
- Se hizo que en runtime el juego parta siempre desde `base_sprite` y no herede el estado visual abierto del editor.

**NUEVA SESION - IMPLEMENTACION DE HERRERO:**
- Se agrego opcion "Vender" al herrero para abrir el catalogo de materiales de forja y se mantiene el flujo de venta de inventario compartido.
- Se creo catalogo de materiales con 8 items: `POLVO_CRISTAL`, `FIBRA_CUERO`, `MINERAL_HIERRO`, `ESENCIA_FUEGO`, `ESENCIA_AGUA`, `FRAGMENTO_MADERA`, `PIEL_BESTIA`, `GEMA_ZAFIRO`.
- Se implemento logica de compra de materiales en `ejecutar_accion_submenu`.
- Se creo nueva pantalla visual `PantallaMejoraHerrero` en `src/pantalla_mejora_herrero.py` para que el heroe seleccione equipo equipado o de la mochila y lo mejore graficamente (navegacion con flechas, enter para confirmar).
- Las opciones del herrero ahora son: `["Comprar", "Vender", "Mejorar", "Forjar", "Hablar", "Salir"]`.
- Se corrigio crash de mejora por consumo de materiales en cantidad 0 (`KeyError` en `usar_item`) con validaciones defensivas.
- Se agrego limite explicito de mejora por equipo: maximo `+5`.
- Se actualizaron recetas de forja para usar materiales del herrero (sin uso de eter/pociones en recetas).
- Se mejoro UI de mejora: texto envuelto tipo chat y scroll para lista de equipos y panel de materiales/detalle.
- Se restauro comportamiento de dialogo con tecla `Q`: en dialogo retrocede linea, y en panel NPC vuelve al dialogo base.

## Nueva linea: biblioteca de dimensiones por sprite

La idea aqui es poder guardar un preset de tamaño por sprite para reutilizarlo despues sin tener que reescalar manualmente cada vez.

### Problema que resuelve

- Si un sprite de cofre, NPC o cualquier objeto se acomoda a un tamano especifico en un mapa, hoy ese tamano se pierde como preset reutilizable.
- Si luego se quiere usar el mismo sprite en otro mapa, hay que volver a redimensionarlo a mano.

### Solucion propuesta

- Agregar un boton en el editor: `Guardar dimensiones`.
- Cuando haya un sprite seleccionado en el canvas, el sistema guarda su ancho y alto actual como un preset reutilizable.
- Ese preset se muestra en una lista aparte, debajo o al lado de la lista normal de sprites.
- Al arrastrar o volver a usar ese sprite, se puede elegir el preset guardado para aplicarle automaticamente ese tamano.

### Estructura sugerida de datos

- `nombre_presets` o `presets_dimensiones` por tipo de sprite.
- Cada entrada podria guardar:
	- `nombre` del preset,
	- `sprite_base` o identificador del sprite,
	- `ancho`,
	- `alto`,
	- opcionalmente `categoria` como `cofre`, `npc`, `puerta`, `objeto`.

### Flujo minimo para probar

1. Seleccionar un sprite.
2. Ajustarlo a un tamano manualmente.
3. Pulsar `Guardar dimensiones`.
4. Verlo en una lista de presets.
5. Reutilizar ese preset en otro mapa o sobre el mismo sprite.

### Decision practica para empezar

- Para esta primera prueba conviene guardarlo en una lista simple dentro del JSON del editor, no en carpetas separadas por tipo.
- Luego, si funciona, se puede separar por categoria o por archivo dedicado.

## Bloqueo por interaccion (implementado en runtime)

Ya se conecto la parte principal del bloqueo en el juego:

- El mapa carga los objetos interactivos del JSON por mapa.
- Esos objetos se agregan a la colision del héroe mientras esten bloqueados.
- La tecla `E` ahora puede activar botones y abrir sus objetivos enlazados.
- Al activarse, el objeto cambia de estado y deja de bloquear el paso si corresponde.

Pendiente fino:

- Ajustar mensajes visuales por tipo de objeto cercano.
- Si hace falta, separar reglas mas estrictas para puertas, cofres y activadores por subtipos.

## Nota de bloqueo por interaccion

Tambien queda pendiente agregar la logica de bloqueo para objetos que no deben pasar sin activacion previa.

- Bloquear puertas, cofres, botones y otros objetos cuando corresponda.
- Un cofre cerrado no debe abrirse si no fue activado el boton enlazado.
- Una puerta debe respetar su estado bloqueado o desbloqueado segun el mapa cargado.
- El flujo debe quedar listo para que cada tipo de objeto tenga su propia regla de acceso.

Pendiente adicional:

- Definir reglas por tipo para bloqueo de colision real (paso/no paso) en mapa: `puerta`, `cofre`, `boton`, `palanca`, `activador`.

## Decisión de diseño para puertas

Para puertas conviene seguir esta lógica:

- Si el jugador interactúa y no tiene la llave necesaria, mostrar una ventana de aviso.
- Si el jugador sí tiene la llave, abrir la puerta y cambiar su sprite a la versión abierta.
- La llave no se consume.
- Todas las puertas del mismo nivel comparten la misma llave.
- El estado abierto debe persistir si la puerta ya fue desbloqueada.

## Flujo de trabajo propuesto

1. Crear una base nueva en un `.py` separado para objetos interactivos.
2. Crear su `.bat` de lanzamiento.
3. Reutilizar la lógica de cofres para el chequeo de llaves.
4. Agregar soporte para puertas con sprite cerrado y sprite abierto.
5. Mostrar popup cuando falte una llave.
6. Guardar estado de apertura por ID único.
7. Extender luego a otros objetos seleccionables si hace falta.

## Ruta siguiente sugerida: dialogos y NPC

Para no mezclar demasiado cosas distintas, conviene separar la linea de dialogos en dos etapas:

### Etapa 1: base de dialogo

- Definir un NPC sin colision dura, solo con rango de interaccion.
- Al presionar `E`, abrir una ventana de dialogo simple.
- Dibujar un cuadro de dialogo en una zona fija de la pantalla.
- Permitir mostrar una o varias lineas de texto.

### Etapa 2: NPC con funciones

- NPC vendedor.
- NPC herrero o mejora de armas.
- NPC con misiones o frases condicionales.
- NPC que cambie dialogo segun estado del juego.

### Recomendacion de orden

- Primero hacer el sistema base de dialogo.
- Despues agregar un NPC simple de prueba.
- Recién luego conectar compra, venta o mejora.
- Si compra/venta y herreria van a usar el mismo cuadro de dialogo, conviene hacer primero el cuadro y el motor de interaccion, y despues la logica de negocio.

## Guía para nuevos .py y .bat

Antes de crear un archivo nuevo conviene revisar si ya existe lógica que se pueda reutilizar o mejorar. La prioridad debería ser:

1. Buscar primero en el código actual si ya existe la mecánica equivalente.
2. Reutilizar la lógica antes de duplicarla en otro `.py`.
3. Si hace falta un nuevo `.bat`, usarlo solo como lanzador y no para repetir lógica de negocio.
4. Si la nueva funcionalidad es una variación de algo existente, mejorar el flujo actual en lugar de crear una rama paralela.

### Archivos que conviene revisar siempre primero

- [main.py](../main.py): entrada del juego, eventos, teclas, estado del mapa y render principal.
- [src/mapa.py](../src/mapa.py): carga del mapa, colisiones, cofres, objetos interactivos y capas.
- [src/cofre.py](../src/cofre.py): lógica de apertura, llaves y cambio visual de cofres.
- [gestor_objetos_interaccion_v1.py](../gestor_objetos_interaccion_v1.py): editor V1 de objetos, enlaces, guardado y presets.
- Cualquier `.bat` nuevo solo debería servir para abrir o ejecutar una herramienta ya existente.

### Regla practica

- Si la lógica ya existe, primero extenderla o refactorizarla.
- Si la lógica es nueva pero comparte estructura con otra, copiar la mínima parte necesaria y dejarla compatible con la anterior.
- Si el cambio afecta editor y runtime, revisar ambos lados antes de tocar nada.

## Datos mínimos para el nuevo flujo

Cada objeto interactivo debería tener:

- `id` único,
- `tipo` (`cofre`, `puerta`, `objeto`),
- `x`, `y`, `w`, `h`,
- `requiere_llave`,
- `sprite_cerrado`,
- `sprite_abierto`,
- `estado_abierto`,
- `mensaje_sin_llave`.

## Comportamiento esperado

- Si el jugador no tiene la llave: popup con mensaje claro.
- Si el jugador tiene la llave: se ejecuta la apertura y el sprite cambia.
- Si el objeto ya está abierto: no debe volver a bloquear el paso.
- Si el objeto es un cofre: puede seguir usando la pantalla de contenido existente como referencia.

## Nombre sugerido para la nueva base

- Python: `gestor_objetos_interaccion_v1.py`
- BAT: `ejecutar_gestor_objetos_interaccion_v1.bat`

## Siguiente paso

- Definir el formato exacto del preset de dimensiones y el boton `Guardar dimensiones` en el editor V1.
- Decidir si el preset se guarda junto al JSON del mapa o en un archivo global aparte.
- Luego crear la base de dialogos/NPC con un cuadro simple y un NPC de prueba.
- Revisar si el preset de dimensiones debe aplicarse automaticamente al arrastrar el sprite o si tambien debe poder elegirse manualmente desde la lista.

## Avance fase siguiente (dialogos NPC base)

Quedo implementada la base minima en runtime para dialogos de NPC:

- Los objetos interactivos tipo `npc` ahora pueden cargar lineas de dialogo desde el JSON por mapa.
- Se soportan claves: `dialogo_lineas`, `dialogo`, `dialogo_texto`, `texto_dialogo`, `texto`, `mensaje`.
- Si un NPC no trae texto, usa fallback simple para no romper la interaccion.
- La tecla `E` abre dialogo cuando el objeto cercano es NPC.
- Con `E` se avanza linea por linea y al final se cierra el dialogo.
- `ESC` cierra el dialogo activo sin abrir el menu pausa.
- Se agrega caja visual de dialogo en la parte baja de la pantalla.

Notas de comportamiento:

- NPC en esta fase base no bloquea paso (interaccion por proximidad).
- Se mantiene prioridad de objetos del editor V1 en la tecla `E` y fallback de cofres antiguos.

### Ejemplo de JSON para NPC

```json
{
	"id": 101,
	"tipo": "npc",
	"label": "Aldeano",
	"sprite": "assets/sprites/npcs/aldeano_1.png",
	"dialogo_lineas": [
		"Hola, viajero.",
		"La herreria abre al amanecer.",
		"Presiona E para seguir hablando."
	],
	"rect": { "map_x": 300, "map_y": 240, "map_w": 64, "map_h": 96 }
}
```

## Proximo bloque recomendado

1. Agregar edicion de dialogo en el editor V1 (campo multilinea por NPC).
2. Definir `rol_npc` (`vendedor`, `herrero`, `quest`) para enrutar acciones futuras.
3. Al cerrar dialogo, habilitar opcion de accion contextual segun rol.

## Delta actual: Gestor NPC nuevo (implementado)

Se implemento en el gestor NUEVO de NPC la base pedida para conversaciones y modos:

- Pool de 10 dialogos por NPC (`Dialogo 1` a `Dialogo 10`).
- Soporte por NPC independiente en el mismo mapa (cada NPC conserva su pool y slot activo).
- Menu contextual con click derecho estilo lista para elegir `Dialogo 1..10`.
- Opcion en menu contextual para editar el dialogo activo.
- Opcion en menu contextual para redimensionar ventana de dialogo.
- Tecla `E`: avanzar linea de dialogo.
- Tecla `Q`: retroceder linea de dialogo.
- Tecla `TAB`: cambiar modo del NPC seleccionado en ciclo `NPC -> VENTA -> HERRERO -> EVENTO`.
- Boton `Crear Ventana`: configurar ancho/alto de caja de dialogo del NPC seleccionado.
- Modo `VENTA`: al terminar dialogo abre panel lateral en canvas con `Comprar`, `Vender`, `Hablar`, `Salir`.
- Modo `HERRERO`: panel con `Comprar`, `Vender`, `Mejorar`, `Forjar`, `Hablar`, `Salir`.
- Modo `EVENTO`: hook base preparado para futura integracion de batalla por NPC.

Archivos nuevos de base modular:

- `src/npc_comercio_herrero.py`: acciones base para panel de venta/herrero.
- `src/npc_eventos_batalla.py`: hook base para eventos y futura batalla contra NPC.

## Pendiente siguiente (anotado)

- Paleta de colores para estilo de ventana de dialogo (postergado por ahora).
- Generador/guia de dialogos predeterminados por tipo de NPC.
- Ajustar la coherencia final entre el panel del herrero y sus submenus, y revisar balance de compra/venta/mejora/forja.
- Logica de evento que lance batalla contra NPC en archivo aparte.
- En modo batalla, mostrar dialogos en parte superior para no tapar opciones de combate.

## Delta actual 2: Persistencia, tamanos y panel derecho (implementado)

Se cerro la parte de tamanos y persistencia de NPC en el gestor nuevo:

- Se mantuvo separado el gestor nuevo de NPC para no mezclarlo con el gestor anterior de cofres/objetos.
- Se dejaron lanzadores dedicados para abrir directamente la interfaz nueva.
- La ventana del gestor nuevo arranca en `1280x720`, con marco normal de sistema y botones `-`, `[]`, `X`.

### Persistencia por mapa

- Al seleccionar fondo/mapa, el gestor busca automaticamente el JSON del mapa en `src/database/npc_interactivos_mapas/`.
- Si el mapa ya tenia datos, restaura NPC y configuracion.
- Si no hay datos para ese mapa, limpia el canvas para iniciar mapa nuevo.
- El boton `Guardar` persiste los NPC del mapa actual y conserva:
	- `rect` (posicion y tamano),
	- `modo_npc`,
	- `dialog_pool` y `dialogo_activo_idx`,
	- `ventana_dialogo` por NPC.

### Presets de tamano NPC

- Se agrego boton `Guardar Dim` en el gestor nuevo.
- Guarda presets globales de tamano por sprite en `src/database/npc_dimension_presets.json`.
- Al arrastrar un sprite al canvas, si existe preset guardado, se aplica automaticamente.
- Se puede redimensionar NPC seleccionado con:
	- `+` / `-`,
	- rueda del mouse sobre canvas.

### Panel derecho mejorado

- Se agrego lista de presets de tamano en el panel derecho.
- Click en preset:
	- lo selecciona,
	- y si hay NPC seleccionado, aplica tamano al instante.
- Se agrego un bloque pequeno de demo/preview de sprite debajo de la lista de presets.

### Atajos extra

- `Suprimir` sobre un preset seleccionado elimina ese preset de la lista.
- La eliminacion se guarda inmediatamente en el JSON de presets.

### Estabilidad

- Se corrigio un fallo de arranque por metodo faltante (`_load_thumb`) en el gestor nuevo.
- Se valido compilacion del script despues de cada ajuste (sin errores de sintaxis).

## Delta actual 3: UX y robustez del gestor NPC nuevo (implementado)

Se cerraron ajustes de uso diario y estabilidad del editor NPC:

### Suprimir sobre NPC seleccionado

- `Suprimir` ahora prioriza eliminar el NPC/sprite seleccionado en canvas.
- Si no hay NPC seleccionado, `Suprimir` mantiene la logica de borrar preset de tamano con confirmacion `SI`.
- Se ajustan indices internos de dialogo/panel tras borrar para no dejar referencias desfasadas.

### Dialogos predeterminados por tipo de NPC

- El pool por defecto ahora depende del modo del NPC:
	- `npc` (aldeano): 10 dialogos base de saludo/ambiente.
	- `venta`: 3 dialogos base de tienda.
	- `herrero`: 3 dialogos base de forja.
	- `evento`: 3 dialogos base de evento.
- El editor mantiene 10 slots por NPC; en `venta/herrero/evento` las 3 bases se ciclan para completar el pool.
- Al cambiar modo con `TAB`, el NPC recarga automaticamente los dialogos predeterminados del nuevo tipo.

### Fixes de crash en runtime del gestor

- Se corrigio `NameError` por `checklist_rect` no definido, integrando su rectangulo al bloque de layout del panel derecho.
- Se corrigio `IndexError` por `panel_npc_idx` fuera de rango:
	- validacion defensiva antes de usar indices persistentes del panel,
	- cierre automatico del panel si el NPC ya no existe,
	- reapertura segura de dialogo solo con indice valido.

## Nota para siguiente bloque: evento de pelea contra NPC

Queda anotado para implementacion futura el flujo de decision al final del dialogo:

- Opciones: `Pelear` y `Aun no`.
- Si el jugador elige `Aun no`, se cierra el dialogo y puede seguir en mapa.
- Si luego vuelve a interactuar y elige `Pelear`, recien ahi entra a batalla.

Tambien queda planificado para el gestor NPC:

- Enlace del NPC de evento usando logica estilo objetos interactivos.
- Bloque de sprites del NPC de pelea con 3 cajas:
	- `Espera`,
	- `Ataque`,
	- `Muerte` (opcional).
- Si no hay sprite de muerte, usar desvanecimiento como fallback (similar al comportamiento actual de monstruos en batalla).

Importante:

- Antes de implementar este bloque, confirmar contigo cual NPC vamos a usar de prueba.
- Esta especificacion tambien queda registrada en:
	- `docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md`.
