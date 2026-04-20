# Plan Fase Vendedor/Herrero V2

Fecha inicio plan: 2026-04-20
Estado: En planificacion activa
Orden de ejecucion: 1) Vendedor, 2) Herrero

NPCs objetivo para pruebas iniciales:

- Vendedor: map_id `mapa_tienda_items`, NPC id `2`, modo `venta`.
- Herrero: map_id `mapa_herrero`, NPC id `1`, modo `herrero`.

## 1) Objetivo de esta fase

Reforzar la logica de comercio y herreria con interfaz grande, transacciones claras y persistencia correcta, manteniendo el estilo visual actual del juego.

## 2) Reglas de diseno acordadas

1. Implementar primero Vendedor (compra/venta).
2. Implementar despues Herrero (mejorar/forjar + venta al herrero).
3. Mantener colorimetria y estilo de paneles ya existentes en runtime.
4. Si una accion no puede completarse, mostrar mensaje claro y no alterar inventario/oro.
5. Toda operacion debe poder cancelarse sin efectos secundarios.

## 3) Fase 1 - Vendedor (prioridad inmediata)

### 3.1 Alcance funcional

- Panel grande de comercio con dos columnas.
- Columna izquierda: inventario del jugador.
- Columna derecha: stock del vendedor.
- Filtros por categoria (consumibles, equipo, especiales, etc.).
- Control de cantidad con + y -.
- Total de compra/venta en tiempo real.
- Confirmar/Cancelar transaccion.

### 3.2 Reglas de negocio

1. El vendedor puede comprar todo lo vendible del jugador (dinero NPC interno infinito).
2. El jugador solo puede comprar si tiene oro suficiente.
3. Cantidades nunca negativas.
4. Nunca duplicar ni perder items por error de UI.
5. Solo aplicar cambios al confirmar.

### 3.3 Checklist Vendedor

- [ ] Definir modelo de datos de transaccion temporal (carrito).
- [ ] Crear UI grande de vendedor con dos paneles.
- [ ] Integrar filtros de categoria.
- [x] Integrar selector de cantidad con + y -.
- [x] Mostrar total dinamico (compra/venta).
- [ ] Implementar Confirmar/Cancelar.
- [ ] Aplicar cambios a inventario/oro del jugador al confirmar.
- [ ] Mensajes de error y exito claros.
- [ ] Prueba manual completa del flujo vendedor.

Avance implementado en runtime actual (sin UI grande de dos columnas aun):

- Selector de cantidad por item con `+`/`-` teclado y botones clickeables.
- Edicion directa de cantidad con `ESPACIO` sobre item seleccionado.
- Precio unitario y total dinamico visible por item.
- Aplicacion de compra/venta por lote segun cantidad elegida.

## 4) Fase 2 - Herrero (despues de vendedor)

### 4.1 Alcance funcional

- Pantalla grande de herrero con secciones Mejorar, Forjar y Vender.
- Vista comparativa Antes vs Despues por stat.
- Nivel de mejora visible por pieza (ej: +1, +2, +3...).
- Costo en oro + materiales por accion.

### 4.2 Reglas de negocio

1. Si no hay materiales/oro, bloquear accion y explicar causa.
2. Al mejorar, mostrar stat que sube y resultado final.
3. Al forjar, mostrar receta, costo y resultado esperado.
4. Cambios reflejados en inventario/equipo inmediatamente al confirmar.

### 4.3 Checklist Herrero

- [ ] Definir estructura de niveles de mejora por equipo.
- [ ] Definir estructura de recetas de forja.
- [ ] Crear UI grande de herrero (mejorar/forjar/vender).
- [ ] Integrar comparador de stats Antes vs Despues.
- [ ] Implementar consumo de oro/materiales.
- [ ] Reflejar resultado en inventario/equipo.
- [ ] Prueba manual completa del flujo herrero.

## 5) Mejora UX transversal

- [ ] Boton de pantalla completa en runtime del juego.
- [ ] Mantener atajos consistentes en paneles (mover, elegir, volver).
- [ ] Mantener formato de mensajes y paneles visuales coherente.

## 6) Priorizacion por impacto

### Critico

- Integridad de transacciones (sin duplicados/perdidas).
- Persistencia de inventario/equipo tras confirmar.
- Validaciones de oro, materiales y cantidad.
- Cierre/retorno de UI sin estados colgados.

### Alto

- UI grande de vendedor con dos columnas.
- Carrito temporal + total dinamico.
- Herrero con comparador Antes vs Despues.
- Niveles de mejora visibles por equipo.

### Medio

- Filtros por categoria avanzados.
- Mensajeria de ayuda/contexto mas rica.
- Ajustes finos de balance base de precios.

### Bajo

- Animaciones cosmeticas de compra/forja.
- Sonidos extra por accion.
- Micro-pulidos visuales no funcionales.

## 7) Regla de actualizacion entre PCs

Cada vez que se complete un item de checklist:

1. Marcarlo en este archivo.
2. Actualizar resumen de sesion en `docs/PUENTE_SESIONES_PC.md`.
3. Indicar que item quedo listo y que prueba manual se realizo.
