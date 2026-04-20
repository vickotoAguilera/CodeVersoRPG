# Puente de Sesiones entre PCs (Trabajo <-> Casa)

Fecha de ultima actualizacion: 2026-04-20

Objetivo de este archivo:
- Este es el documento oficial para traspasar contexto entre computadores.
- Antes de cambiar de PC, actualizar este archivo con resumen claro de la sesion.
- Al abrir en el otro PC, leer primero este archivo y continuar desde aqui.

Regla de uso obligatorio:
1. Al cerrar sesion en un PC: actualizar secciones 1, 2, 3 y 4.
2. Guardar cambios y subir al repo.
3. En el otro PC: bajar cambios y abrir este archivo antes de seguir.

---

## 1) Estado actual rapido

- Fase activa: cierre NPC runtime (venta/herrero) y preparacion de evento/batalla.
- Editor NPC v1: estable, con dialogos por slot, modos npc/venta/herrero/evento y persistencia por mapa.
- Ventanas UI editor NPC: drag/resize implementado para dialogo y panel, con defaults globales y override por NPC.
- Runtime mapa: panel de vendedor/herrero integrado y navegable con teclas de movimiento, bloqueando movimiento del heroe mientras panel/dialogo esta activo.

## 2) Lo ultimo implementado en este PC (Trabajo)

Cambios recientes importantes:

1. Runtime vendedor/herrero en mapa
- Se agrego panel de opciones sobre el mapa.
- Navegacion del panel con W/S y flechas arriba/abajo.
- Confirmacion con E o Enter.
- Cierre con Q o ESC.

2. Bloqueo de movimiento del heroe
- Mientras panel NPC o dialogo NPC esta activo, el heroe no se mueve.
- Permite reutilizar las mismas teclas para navegar opciones del panel.

3. Conexion de modo/id NPC desde mapa
- La interaccion NPC ahora devuelve npc_id y npc_modo para abrir panel correcto segun tipo (vendedor/herrero).

4. Validacion tecnica
- main.py y src/mapa.py compilan sin errores.

## 3) Pendiente inmediato (primer trabajo al abrir en el otro PC)

1. Dar logica real a opciones de vendedor:
- Comprar (descontar oro, agregar item)
- Vender (quitar item, sumar oro)

2. Dar logica real a opciones de herrero:
- Mejorar (costos + materiales + incremento stats)
- Forjar (crear equipo nuevo con receta)

3. Mantener coherencia UI/flujo:
- Mensajes claros de exito/error en cada accion.
- Mantener bloqueo de movimiento hasta cerrar panel/submenu.

## 4) Lista de archivos tocados recientemente

- main.py
- src/mapa.py
- gestor_interfaz_npc_v1.py
- src/npc_comercio_herrero.py
- src/npc_eventos_batalla.py
- docs/PLAN_SIGUIENTE_SESION_OBJETOS_INTERACCION.md
- docs/HOJA_RUTA_SISTEMAS_NUEVOS_NPC_BATALLA.md

## 5) Plantilla corta para proxima transferencia

Copiar y reemplazar al final de cada sesion:

---
Fecha:
PC origen: Trabajo o Casa

Hecho hoy:
- 
- 
- 

Validado:
- py_compile:
- prueba manual:

Pendiente siguiente:
- 
- 

Bloqueos o riesgos:
- 
---
