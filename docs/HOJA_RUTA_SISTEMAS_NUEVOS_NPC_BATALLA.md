# Hoja de Ruta - Sistemas Nuevos (NPC -> Batalla/Magias)

## Documento puente entre PCs

Referencia oficial para traspaso de sesion:

- [docs/PUENTE_SESIONES_PC.md](PUENTE_SESIONES_PC.md)

Regla: antes de pasar de PC Trabajo a PC Casa (o viceversa), actualizar ese archivo con resumen de la sesion.

Fecha de actualizacion: 2026-04-20

Plan activo de implementacion (obligatorio en esta fase):

- `docs/PLAN_FASE_VENDEDOR_HERRERO_V2.md`
- `docs/PLAN_NPC_EVENTO_BATALLA_CANVAS_DOBLE.md`
- Orden: 1) Vendedor, 2) Herrero

Siguiente foco de implementacion (ya definido):

- NPC evento batalla con editor de canvas doble (mundo + preview batalla), layouts globales y override para boss centrado.

## 1) Archivos nuevos de esta semana (.bat y .py)

### .bat nuevos

- AUTO_SPLITTER_MAGICO.bat
- ejecutar_constructor_prefabs.bat
- ejecutar_gestor_interfaz_npc_v1.bat
- ejecutar_gestor_objetos_interaccion_v1.bat
- ejecutar_gestor_portales_interaccion_v2.bat
- ejecutar_gestor_portales_interaccion_v2_editor.bat
- ejecutar_interfaz_npc.bat
- iniciar_juego.bat
- visualizar_recursos.bat

### .py nuevos

- constructor_prefabs.py
- descargar_nes.py
- descargar_nes_v2.py
- gestor_interfaz_npc_v1.py
- gestor_objetos_interaccion_v1.py
- gestor_portales_interaccion_v2.py
- iniciar_interfaz_npc.py
- rpg_games_list.py
- scraper_spriters.py
- src/npc_comercio_herrero.py
- src/npc_eventos_batalla.py
- test_auto.py
- visualizador_recursos.py

Nota: existen archivos de respaldo/archivo historico movidos a "archivos viejos/" para no perder referencia.

## 2) Sistemas mejorados ya logrados

### Gestor NPC nuevo (v1)

NPC objetivo de pruebas iniciales:

- Vendedor: `mapa_tienda_items`, NPC id `2` (modo `venta`).
- Herrero (siguiente fase): `mapa_herrero`, NPC id `1` (modo `herrero`).

### Runtime base NPC

- Soporte de interaccion de dialogo en mapa con tecla E.
- Caja visual de dialogo en runtime.
- Fallback y lectura de varias claves de texto para NPC.
- Portal `pueblo_final <-> tienda_items` reparado con carga correcta de mapas especiales.
- Indicador de oro visible durante submenu de comercio.
- Selector de cantidad funcional en compra/venta (`+`, `-`, botones clickeables y `ESPACIO` para editar numero).
- Precio unitario y total dinamico visibles por item en submenu de comercio.
- Compra/venta por lote aplicada en logica real (oro e inventario por cantidad seleccionada).

### Orden y mantenimiento

- Archivado de respaldos y duplicados en carpeta "archivos viejos/".
- Recuperacion de lanzadores .bat recientes a la raiz para acceso rapido.
- Limpieza de carpeta CC0-1.0-Music del workspace.

## 3) Pendientes (lo que falta)

### Prioridad alta: cerrar fase NPC end-to-end

1. Completar UI grande de Vendedor (dos columnas, carrito, cantidad, total, confirmar/cancelar).
2. Completar UI grande de Herrero (mejorar/forjar/vender, comparador Antes vs Despues).
3. Validar integridad transaccional y persistencia (sin duplicados/perdidas).
4. Mantener control de estado limpio al abrir/cerrar paneles NPC.
5. Validar persistencia total por mapa con escenarios mixtos (aldeano + vendedor + herrero + evento).

### Prioridad media: pulido de UX y QA NPC

1. Nombres de slots auto por tipo (ej: Saludo, Oferta, Despedida).
2. Confirmacion opcional para borrar NPC (ademas de presets).
3. Mensajes de estado mas claros para cada accion clave.
4. Prueba manual guiada (casos felices + casos borde).
5. Redimension manual de ventanas (sin prompt de ancho/alto):

- Permitir redimensionar arrastrando bordes/esquinas de la caja de dialogo y panel de venta/herrero.
- Permitir mover la caja en pantalla para ajustar composicion.
- Guardar un tamano/posicion por defecto global para nuevas ventanas.
- Permitir excepciones por NPC (si se personaliza uno, mantener su config propia).
- Opcion rapida para "usar valores por defecto" y "restaurar por defecto".

### Siguiente gran fase (despues de NPC)

- Revisar y unificar combate/habilidades/magias:
  - efectos no aplicados (buff/debuff/elementales),
  - formula de dano/defensa,
  - duplicidad entre magia_db y habilidades_db,
  - orden y mantenimiento de flujo de batalla.

### Matriz de prioridad de esta fase

Critico:

- Integridad de transacciones.
- Persistencia de inventario/equipo/oro.
- Validaciones de oro/materiales/cantidad.

Alto:

- UI grande de Vendedor.
- UI grande de Herrero.
- Comparador de stats Antes vs Despues.

Medio:

- Filtros avanzados por categoria.
- Mensajeria contextual extendida.
- Balance base de precios/costos.

Bajo:

- Animaciones cosmeticas.
- Sonidos adicionales.
- Pulidos visuales no funcionales.

## 3.1) Especificacion futura: Evento de pelea contra NPC

Cuando iniciemos esta etapa, primero se debe confirmar contigo cual NPC se usara como caso de prueba.

Flujo funcional esperado:

- Interactuar con NPC abre dialogo normal.
- Al final del dialogo aparece decision con dos opciones: "Pelear" y "Aun no".
- Si el jugador elige "Aun no", se cierra la ventana y puede seguir en mapa (curarse, comprar, etc.).
- Si vuelve despues e interactua otra vez, debe poder elegir "Pelear" y recien ahi iniciar batalla.
- Si elige "Pelear", se transiciona a pantalla de batalla inmediatamente.

Regla de estado:

- Elegir "Aun no" no marca derrota ni victoria y no consume el evento.
- El evento queda pendiente hasta que el jugador acepte pelear.

Integracion editor (gestor NPC):

- Mantener la logica de enlace estilo objetos interactivos para disparar el evento.
- Agregar un bloque de sprites del NPC de pelea con 3 cajas:
  - Espera
  - Ataque
  - Muerte (opcional)
- Si no existe sprite de muerte, usar desvanecimiento como fallback, igual que monstruos actuales en batalla.

Uso runtime de sprites del NPC de pelea:

- El sistema debe saber que sprite usar por estado (espera/ataque/muerte).
- Si falta algun estado, aplicar fallback seguro sin romper batalla.

Pendiente de implementacion guiada:

- En cuanto entremos a esta fase, pedirte el NPC de prueba antes de escribir codigo.

## 4) Propuesta de creacion de archivos (uno a uno)

Orden recomendado para no romper nada y avanzar modular:

1. src/npc_runtime_actions.py

- Objetivo: resolver accion real segun modo_npc (npc/venta/herrero/evento) en runtime.

2. src/npc_shop_service.py

- Objetivo: logica de compra/venta (precios, stock, oro, inventario).

3. src/npc_blacksmith_service.py

- Objetivo: logica de mejora/forja (materiales, costos, resultado de mejora).

4. src/npc_event_service.py

- Objetivo: resolver eventos (iniciar batalla, entregar recompensa, flags).

5. src/npc_validation.py

- Objetivo: validar estructura JSON de NPC por mapa y detectar errores de datos.

6. scripts/test_npc_runtime_flow.py

- Objetivo: pruebas de flujo (interaccion, accion por modo, persistencia).

7. ejecutar_test_npc_runtime_flow.bat

- Objetivo: ejecutar test de flujo NPC de forma rapida.

8. docs/PLAN_FASE_BATALLA_MAGIAS_UNIFICACION.md

- Objetivo: plan detallado de unificacion de combate/magias post-NPC.

## 5) Checklist de cierre de fase NPC

- [ ] Interaccion NPC por modo funcionando en runtime.
- [ ] Venta real conectada a inventario/oro.
- [ ] Herrero real conectado a equipo/materiales.
- [ ] Evento real conectado a batalla/quest.
- [ ] Persistencia por mapa validada en escenarios mixtos.
- [ ] Sin errores de indice/estado al borrar NPC, cambiar modo o cargar mapa.
- [ ] Ventanas de dialogo y venta/herrero redimensionables por drag (sin input manual de dimensiones).
- [ ] Guardado de default global de ventana + override por NPC funcionando.

## 6) Resumen ejecutivo de avance hasta ahora

- Se construyo y estabilizo un gestor NPC nuevo separado.
- Se implemento base de dialogo robusta con modos y persistencia.
- Se completo una primera capa de UX (slots, checklist, presets, confirmaciones).
- Se ordeno parte del repo archivando respaldos y duplicados.
- En herrero runtime: compra/venta/mejorar/forjar operativos con validaciones, tope `+5`, recetas por materiales y panel de mejora con scroll/texto envuelto.
- En dialogos NPC runtime: tecla `Q` vuelve a retroceder lineas en conversacion y al cerrar panel retorna al dialogo base.
- Proximo foco: cerrar runtime NPC completo; luego pasar a batalla/magias.

## 7) Documento de referencia de contexto

Este archivo se considera referencia principal para continuar trabajo en sesiones siguientes:

- docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md
