# Sistema de Enlazado de Spawns - Plan de Implementación

## Objetivo

Implementar un sistema visual y funcional para enlazar portales con spawns, similar al sistema de portales:
- **Spawns sin enlazar**: VERDE
- **Spawns enlazados**: BLANCO con fondo NEGRO
- **Fusión de nombres**: Al enlazar, mostrar nombre fusionado (ej: `portal_pueblo_1_spawn`)
- **Flujo de enlazado**: Botón "Enlazar" → Click portal → Click spawn → Enlace creado

## Análisis del Sistema Actual

### Estructura de Spawn (Líneas 115-124)
```python
@dataclass
class Spawn:
    id: str
    x: int
    y: int
    direccion: str = 'abajo'
    tam: int = 12
```

**Problema**: No hay campo para rastrear si un spawn está enlazado a un portal.

### Renderizado Actual (Líneas 962-970)
```python
for s in spawns:
    sx, sy = self._map_to_screen(s.x, s.y, lado, offset_x, offset_y, zoom)
    half = max(6, int(s.tam * zoom / 2))
    pygame.draw.rect(self.screen, COLOR_SPAWN, (sx-half, sy-half, half*2, half*2), 1)
    # ... línea de dirección ...
    if s.id:
        self.screen.blit(self.font_small.render(s.id, True, COLOR_TEXTO), (sx+8, sy-18))
```

**Problema**: Color fijo (azul), no distingue estado de enlazado.

### Sistema de Enlazado Existente

Actualmente existe `portal.spawn_destino_id` que apunta a un spawn, pero **NO hay referencia inversa** (spawn → portal).

## Solución Propuesta

### Opción 1: Añadir Campo `linked_portal_id` a Spawn (RECOMENDADO)

Añadir campo opcional a la clase Spawn para rastrear el portal que lo usa:

```python
@dataclass
class Spawn:
    id: str
    x: int
    y: int
    direccion: str = 'abajo'
    tam: int = 12
    linked_portal_id: str = ''  # NUEVO: ID del portal que usa este spawn
```

**Ventajas**:
- Fácil verificar si spawn está enlazado
- Permite mostrar nombre fusionado
- Mantiene consistencia con sistema de portales

### Opción 2: Calcular Dinámicamente

Buscar en la lista de portales si alguno referencia este spawn.

**Desventajas**:
- Más lento (O(n) por cada spawn)
- Código más complejo

**Decisión**: Usar Opción 1.

## Proposed Changes

### [MODIFY] [editor_portales.py](file:///c:/Users/vicko/Documents/RPG/editor_portales.py)

#### Cambio 1: Actualizar Clase Spawn (Líneas 115-124)

Añadir campo `linked_portal_id` para rastrear el portal enlazado:

```python
@dataclass
class Spawn:
    id: str
    x: int
    y: int
    direccion: str = 'abajo'
    tam: int = 12
    linked_portal_id: str = ''  # ID del portal que usa este spawn
    
    def to_dict(self):
        return {
            "id": self.id,
            "x": int(self.x),
            "y": int(self.y),
            "direccion": self.direccion,
            "tam": int(self.tam),
            "linked_portal_id": self.linked_portal_id
        }
```

#### Cambio 2: Actualizar Renderizado de Spawns (Líneas 962-970)

Implementar sistema de colores verde/blanco según estado de enlazado:

```python
# Spawns
for s in spawns:
    sx, sy = self._map_to_screen(s.x, s.y, lado, offset_x, offset_y, zoom)
    half = max(6, int(s.tam * zoom / 2))
    
    # Determinar color según estado de enlazado
    is_linked = bool(getattr(s, 'linked_portal_id', ''))
    if is_linked:
        # Spawn enlazado: BLANCO con fondo NEGRO
        spawn_col = (255, 255, 255)
        text_col = (255, 255, 255)
        # Fondo negro
        bg_rect = pygame.Rect(sx-half-2, sy-half-2, half*2+4, half*2+4)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, spawn_col, bg_rect, 2)
    else:
        # Spawn sin enlazar: VERDE
        spawn_col = (0, 200, 80)
        text_col = (0, 200, 80)
        pygame.draw.rect(self.screen, spawn_col, (sx-half, sy-half, half*2, half*2), 2)
    
    # Línea de dirección
    vec = {"arriba":(0,-18),"abajo":(0,18),"izquierda":(-18,0),"derecha":(18,0)}.get(s.direccion, (0,18))
    pygame.draw.line(self.screen, spawn_col, (sx, sy), (sx+vec[0], sy+vec[1]), 2)
    
    # Nombre (fusionado si está enlazado)
    if s.id:
        if is_linked and s.linked_portal_id:
            # Nombre fusionado: portal_spawn
            display_name = f"{s.linked_portal_id}_{s.id}"
        else:
            display_name = s.id
        
        txt = self.font_small.render(display_name, True, text_col)
        # Fondo para el texto si está enlazado
        if is_linked:
            txt_rect = txt.get_rect(topleft=(sx+8, sy-20))
            txt_rect.inflate_ip(4, 2)
            pygame.draw.rect(self.screen, (0, 0, 0), txt_rect, border_radius=3)
            pygame.draw.rect(self.screen, spawn_col, txt_rect, 1, border_radius=3)
        self.screen.blit(txt, (sx+8, sy-18))
```

#### Cambio 3: Actualizar `_cargar_mapa_data()` (Líneas 394-456)

Cargar el nuevo campo `linked_portal_id` desde JSON:

```python
for s in data.get('spawns', []):
    spawns.append(Spawn(
        s.get('id', ''),
        s['x'], s['y'],
        s.get('direccion', 'abajo'),
        s.get('tam', 12),
        s.get('linked_portal_id', '')  # NUEVO
    ))
```

#### Cambio 4: Actualizar Lógica de Enlazado Portal→Spawn

Cuando se enlaza un portal a un spawn, actualizar ambas referencias:

**En `_confirm_create_pair_spawns()` (líneas 592-610)**:
```python
# Al crear spawns para vinculación
spawn_a = Spawn(id=spawn_a_id, x=cx_a, y=cy_a, linked_portal_id=a.id)
spawn_b = Spawn(id=spawn_b_id, x=cx_b, y=cy_b, linked_portal_id=b.id)
```

**En `_confirm_create_spawn()` (líneas 612-628)**:
```python
nuevo_spawn = Spawn(id=nuevo_id, x=x, y=y, linked_portal_id=portal.id)
```

#### Cambio 5: Implementar Modo "Enlazar Spawns"

Actualizar la lógica de click cuando el modo "Enlazar" está activo:

**En el event handler de MOUSEBUTTONDOWN (alrededor de línea 1300)**:

```python
# Si modo Enlazar está activo
if self.toggle_enlazar_spawns:
    if isinstance(obj, (PortalRect, PortalPoly)):
        # Primer click: seleccionar portal
        if not self.portal_para_spawn:
            self.portal_para_spawn = obj
            self.lado_portal_spawn = lado
            self._msg(f"✓ Portal '{obj.id}' seleccionado. Click en spawn para enlazar.")
    elif isinstance(obj, Spawn):
        # Segundo click: enlazar con spawn
        if self.portal_para_spawn:
            # Verificar que no estén ya enlazados
            if getattr(self.portal_para_spawn, 'spawn_destino_id', ''):
                self._msg(f"⚠ Portal '{self.portal_para_spawn.id}' ya tiene spawn enlazado.")
            elif getattr(obj, 'linked_portal_id', ''):
                self._msg(f"⚠ Spawn '{obj.id}' ya está enlazado a '{obj.linked_portal_id}'.")
            else:
                # Enlazar
                self.portal_para_spawn.spawn_destino_id = obj.id
                obj.linked_portal_id = self.portal_para_spawn.id
                self._msg(f"✓ Enlazados: {self.portal_para_spawn.id} ↔ {obj.id}")
                self.cambios_pendientes = True
            # Limpiar selección
            self.portal_para_spawn = None
            self.lado_portal_spawn = None
```

#### Cambio 6: Desvincular Spawn

Actualizar `_confirm_unlink_spawn()` para limpiar también `linked_portal_id`:

```python
def _confirm_unlink_spawn(self, modal):
    portal = modal.get('portal')
    lado = modal.get('lado')
    spawn_id = modal.get('spawn_id')
    
    # Limpiar referencia en el portal
    portal.spawn_destino_id = ''
    
    # Buscar el spawn y limpiar su linked_portal_id
    spawns = self.izq_spawns if lado=='izq' else self.der_spawns
    for s in spawns:
        if s.id == spawn_id:
            s.linked_portal_id = ''  # NUEVO
            break
    
    # ... resto del código ...
```

## Verification Plan

### Pruebas Manuales

1. **Crear Spawn Sin Enlazar**:
   - Activar modo "Crear S."
   - Click en mapa para crear spawn
   - **Verificar**: Spawn aparece en VERDE
   - **Verificar**: Nombre normal (sin fusión)

2. **Enlazar Portal con Spawn**:
   - Crear portal y spawn
   - Activar modo "Enlazar"
   - Click en portal
   - **Verificar**: Mensaje "Portal 'X' seleccionado"
   - Click en spawn
   - **Verificar**: Mensaje "✓ Enlazados: portal_X ↔ spawn_Y"
   - **Verificar**: Spawn cambia a BLANCO con fondo NEGRO
   - **Verificar**: Nombre fusionado: `portal_X_spawn_Y`

3. **Intentar Re-enlazar**:
   - Intentar enlazar portal ya enlazado
   - **Verificar**: Mensaje de error claro
   - Intentar enlazar spawn ya enlazado
   - **Verificar**: Mensaje de error claro

4. **Desvincular**:
   - Click derecho en lista "Portal → Spawn"
   - **Verificar**: Spawn vuelve a VERDE
   - **Verificar**: Nombre vuelve a normal (sin fusión)

5. **Persistencia**:
   - Guardar (tecla G)
   - Cerrar y reabrir editor
   - **Verificar**: Enlaces persisten
   - **Verificar**: Colores correctos al cargar
