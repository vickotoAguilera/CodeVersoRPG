# Walkthrough: Sistema de Portales con IDs Únicos

## Cambios Implementados

### 1. Compatibilidad con Ambas Estructuras JSON

**Problema Original**: El editor esperaba una estructura JSON diferente a la que usa el juego.

**Solución**: Actualicé [`_cargar_mapa_data()`](file:///c:/Users/vicko/Documents/RPG/editor_portales.py#L394-L456) para detectar y manejar ambos formatos:

**JSON del Juego** (formato antiguo):
```json
{
  "portales": [{
    "caja": {"x": 455, "y": 900, "w": 30, "h": 30},
    "mapa_destino": "mapa_pradera.jpg",
    "pos_destino": [563, 617]
  }]
}
```

**JSON del Editor** (formato nuevo):
```json
{
  "portales": [{
    "id": "portal_mapa_pueblo_1",
    "x": 455,
    "y": 900,
    "w": 30,
    "h": 30,
    "mapa_destino": "mapa_pradera",
    "spawn_destino_id": "S_mapa_pueblo_mapa_pradera_1"
  }]
}
```

### 2. Generación Automática de IDs Únicos

Añadí [`_generar_portal_id_from_loaded()`](file:///c:/Users/vicko/Documents/RPG/editor_portales.py#L518-L539) que:
- Genera IDs únicos para portales sin ID al cargarlos
- Usa formato `portal_{mapa}_{n}` con contador auto-incremental
- Mantiene un diccionario de contadores por mapa para evitar duplicados

**Ejemplo**: Al cargar `mapa_pueblo_final.json` con 6 portales sin ID:
- `portal_mapa_pueblo_final_1`
- `portal_mapa_pueblo_final_2`
- `portal_mapa_pueblo_final_3`
- ... etc.

### 3. Mensajes de Error Mejorados

Actualicé los mensajes en [`_confirm_create_pair_spawns()`](file:///c:/Users/vicko/Documents/RPG/editor_portales.py#L541-L631) para ser más descriptivos:

**Antes**:
```
⚠ Portal origen ya tiene un spawn vinculado. Desvincula primero.
```

**Ahora**:
```
⚠ 'portal_mapa_pueblo_1' ya vinculado a 'mapa_herrero'. Click derecho en lista para desvincular.
```

### 4. Indicadores Visuales de Destino

Añadí texto debajo de cada portal vinculado mostrando su destino:

**Portales Rectangulares** (líneas 947-951):
```python
if linked and p.mapa_destino:
    dest_txt = self.font_small.render(f"→ {p.mapa_destino}", True, (180,180,180))
    self.screen.blit(dest_txt, (sx+6, sy+rh+2))
```

**Portales Poligonales** (líneas 941-944):
```python
if linked and p.mapa_destino:
    dest_txt = self.font_small.render(f"→ {p.mapa_destino}", True, (180,180,180))
    self.screen.blit(dest_txt, (cx-dest_txt.get_width()//2, cy+15))
```

## Cómo Funciona Ahora

### Sistema de Colores

- **VERDE** (0,200,80): Portal sin vínculo, disponible para enlazar
- **BLANCO** (255,255,255): Portal con vínculo activo

### Flujo de Trabajo

1. **Cargar Mapa del Juego**:
   - Los portales sin ID reciben IDs automáticos
   - Aparecen en VERDE (sin vínculo en el editor)

2. **Crear Portales Nuevos**:
   - Cada portal recibe un ID único con sufijo incremental
   - Ejemplo: `portal_pueblo_1`, `portal_pueblo_2`, `portal_pueblo_3`

3. **Vincular Portales**:
   - Click en portal del lado izquierdo → selecciona primer portal
   - Click en portal del lado derecho → abre modal de confirmación
   - ENTER → crea spawns y vincula ambos portales
   - Los portales cambian a BLANCO y muestran `→ {destino}`

4. **Múltiples Portales por Mapa**:
   - Puedes crear `portal_pueblo_1` → vinculado a `herrero`
   - Luego crear `portal_pueblo_2` → vinculado a `posada`
   - Luego crear `portal_pueblo_3` → vinculado a `taberna`
   - Cada uno es independiente y tiene su propio vínculo

5. **Desvincular**:
   - Click derecho en la lista "Portales Vinculados"
   - El portal vuelve a VERDE (disponible)

## Instrucciones de Prueba

### Prueba 1: Cargar Mapa Existente

1. Ejecutar: `python editor_portales.py`
2. Arrastrar `mapa_pueblo_final` al lado izquierdo
3. **Verificar**: Los 6 portales existentes tienen IDs únicos
4. **Verificar**: Todos aparecen en VERDE (sin vínculo)

### Prueba 2: Crear Múltiples Portales

1. Activar modo "Crear P." (botón o tecla P)
2. Crear portal rectangular en `mapa_pueblo_final`
3. **Verificar**: Recibe ID `portal_mapa_pueblo_final_7`
4. Crear otro portal
5. **Verificar**: Recibe ID `portal_mapa_pueblo_final_8`

### Prueba 3: Vincular Portales Independientemente

1. Cargar `mapa_herrero` en lado derecho
2. Activar modo "Enlazar" (botón)
3. Click en `portal_mapa_pueblo_final_7` (izq)
4. Click en un portal en `mapa_herrero` (der)
5. Presionar ENTER para confirmar
6. **Verificar**: Portal cambia a BLANCO
7. **Verificar**: Muestra `→ mapa_herrero` debajo del ID
8. Cargar `mapa_posada` en lado derecho
9. Click en `portal_mapa_pueblo_final_8` (izq)
10. Click en un portal en `mapa_posada` (der)
11. Presionar ENTER
12. **Verificar**: Segundo portal también en BLANCO con `→ mapa_posada`

### Prueba 4: Intentar Re-vincular

1. Intentar vincular `portal_mapa_pueblo_final_7` a otro destino
2. **Verificar mensaje**: `⚠ 'portal_mapa_pueblo_final_7' ya vinculado a 'mapa_herrero'. Click derecho en lista para desvincular.`

### Prueba 5: Persistencia

1. Guardar con tecla G
2. Cerrar editor
3. Reabrir y cargar ambos mapas
4. **Verificar**: Los IDs persisten
5. **Verificar**: Los vínculos se mantienen

## Archivos Modificados

- [`editor_portales.py`](file:///c:/Users/vicko/Documents/RPG/editor_portales.py)
  - Líneas 394-456: `_cargar_mapa_data()` actualizada
  - Líneas 518-539: Nueva función `_generar_portal_id_from_loaded()`
  - Líneas 566-591: Mensajes de error mejorados
  - Líneas 941-951: Indicadores visuales de destino

## Resultado Final

✅ **Problema resuelto**: Ahora puedes crear múltiples portales en el mismo mapa, cada uno con ID único, y vincularlos independientemente a diferentes destinos.

✅ **Compatibilidad**: El editor maneja tanto JSON antiguos del juego como nuevos del editor.

✅ **UX mejorada**: Indicadores visuales claros y mensajes de error descriptivos.
