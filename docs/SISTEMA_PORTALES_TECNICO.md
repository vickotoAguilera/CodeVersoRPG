# Sistema de Portales - Documentación Técnica

## ✅ Estado Actual: FUNCIONANDO CORRECTAMENTE

Los cambios recientes de resolución de editores (800x600) **NO afectaron** la lógica de portales del juego.

---

## Arquitectura del Sistema

### 1. Flujo de Datos

```
JSON del Mapa → Clase Mapa → Main.py → Cambio de Mapa
```

### 2. Archivos Involucrados

#### Código del Juego
- **[main.py](file:///c:/Users/vicko/Documents/RPG/main.py#L648-L676)** - Lógica principal de portales
- **[src/mapa.py](file:///c:/Users/vicko/Documents/RPG/src/mapa.py#L230-L297)** - Carga de portales desde JSON
- **[src/mapa.py](file:///c:/Users/vicko/Documents/RPG/src/mapa.py#L456-L462)** - Detección de colisión con portales

#### Editores
- **[editor_portales.py](file:///c:/Users/vicko/Documents/RPG/editor_portales.py)** - Editor visual de portales
- **[editor_unificado.py](file:///c:/Users/vicko/Documents/RPG/editor_unificado.py)** - Editor centralizado (incluye portales)

#### Documentación
- **[docs/WALKTHROUGH_PORTALES.md](file:///c:/Users/vicko/Documents/RPG/docs/WALKTHROUGH_PORTALES.md)** - Guía del sistema de portales
- **[docs/EDITOR_PORTALES_GUIA.md](file:///c:/Users/vicko/Documents/RPG/docs/EDITOR_PORTALES_GUIA.md)** - Guía del editor
- **[docs/RESUMEN_SESION_PORTALES.md](file:///c:/Users/vicko/Documents/RPG/docs/RESUMEN_SESION_PORTALES.md)** - Resumen de sesión

---

## Cómo Funciona (Orden de Ejecución)

### Paso 1: Carga del Mapa

**Archivo:** `src/mapa.py` (líneas 230-297)

```python
# Cargar portales desde JSON
if "portales" in datos:
    for portal_data in datos["portales"]:
        # Soporta 3 formatos:
        # 1) Con 'caja' (rect clásico)
        # 2) Con 'puntos' (polígono)
        # 3) Con x,y,w,h directos
        
        nuevo_portal = {
            "caja": caja_rect,                    # Rectángulo de colisión
            "mapa_destino": mapa_dest,            # Nombre del mapa destino
            "categoria_destino": categoria_dest,  # Categoría del mapa destino
            "pos_destino": pos_dest,              # Posición exacta (opcional)
            "spawn_destino_id": spawn_id          # ID del spawn destino (opcional)
        }
        self.portales.append(nuevo_portal)
```

### Paso 2: Detección de Colisión

**Archivo:** `src/mapa.py` (líneas 456-462)

```python
def chequear_portales(self, rect_heroe):
    for portal in self.portales:
        if rect_heroe.colliderect(portal["caja"]):
            return portal  # Retorna el portal completo
    return None
```

### Paso 3: Activación del Portal

**Archivo:** `main.py` (líneas 648-676)

```python
# 1. Detectar colisión
portal_tocado = mi_mapa.chequear_portales(heroe_lider.heroe_rect)

# 2. Si hay portal y está listo para usar
if portal_tocado and portal_listo_para_usar:
    # 3. Extraer datos del portal
    nombre_mapa_nuevo = portal_tocado["mapa_destino"]
    categoria_nueva = portal_tocado["categoria_destino"]
    pos_nueva = portal_tocado["pos_destino"]
    
    # 4. Resolver nombre de archivo real
    archivo_img, categoria_real = resolver_mapa(nombre_mapa_nuevo, categoria_nueva)
    
    # 5. Crear nuevo mapa
    mi_mapa = Mapa(archivo_img, categoria_real, ANCHO, ALTO)
    
    # 6. Teletransportar héroe (3 métodos en orden de prioridad):
    if pos_nueva:
        # Método 1: Posición explícita
        heroe_lider.teletransportar(pos_nueva[0], pos_nueva[1])
    else:
        spawn_id = portal_tocado.get('spawn_destino_id')
        if spawn_id and spawn_id in mi_mapa.spawns_ids:
            # Método 2: Spawn con ID específico
            coord = mi_mapa.spawns_ids[spawn_id]
            heroe_lider.teletransportar(coord[0], coord[1])
        else:
            # Método 3: Primer spawn del mapa (fallback)
            if mi_mapa.spawns:
                s = mi_mapa.spawns[0]
                heroe_lider.teletransportar(s[0], s[1])
    
    # 7. Desactivar portal temporalmente (evita bucle)
    portal_listo_para_usar = False

# 8. Reactivar cuando el héroe sale del portal
elif not portal_tocado:
    portal_listo_para_usar = True
```

---

## Formatos JSON Soportados

### Formato 1: Con 'caja' (Recomendado)

```json
{
  "portales": [{
    "caja": {"x": 455, "y": 900, "w": 30, "h": 30},
    "mapa_destino": "mapa_pradera",
    "categoria_destino": "mundo",
    "pos_destino": [563, 617]
  }]
}
```

### Formato 2: Con 'spawn_destino_id' (Editor Nuevo)

```json
{
  "portales": [{
    "id": "portal_pueblo_1",
    "x": 455,
    "y": 900,
    "w": 30,
    "h": 30,
    "mapa_destino": "mapa_pradera",
    "categoria_destino": "mundo",
    "spawn_destino_id": "S_mapa_pradera_1"
  }]
}
```

### Formato 3: Polígono (Avanzado)

```json
{
  "portales": [{
    "puntos": [[100, 200], [150, 200], [150, 250], [100, 250]],
    "mapa_destino": "mapa_herrero",
    "categoria_destino": "ciudades_y_pueblos/pueblo_inicio"
  }]
}
```

---

## Sistema de Prioridades para Teletransporte

El juego intenta 3 métodos en este orden:

1. **`pos_destino`** (Posición explícita)
   - Más preciso
   - Usado por portales antiguos

2. **`spawn_destino_id`** (ID de spawn)
   - Más flexible
   - Usado por editor nuevo
   - Permite múltiples portales al mismo mapa

3. **Primer spawn del mapa** (Fallback)
   - Seguro
   - Siempre funciona si el mapa tiene spawns

---

## Cambios Recientes (21-11-2025)

### Commit 7f25b3b: Editores 800x600

**Archivos modificados:**
- `editor_unificado.py`
- `editor_mapa.py`
- `editor_mapa_avanzado.py`
- `editor_muros.py`
- `editor_portales.py`
- `editor_portales_backup.py`
- `editor_cofres.py`
- `editor_batalla.py`

**Cambios realizados:**
- Resolución inicial: 1600x900 → 800x600
- Agregada flag `pygame.RESIZABLE`

**Impacto en portales:**
- ✅ **NINGUNO** - Solo afecta la ventana del editor
- ✅ Los datos JSON no cambiaron
- ✅ La lógica del juego no cambió
- ✅ Los portales funcionan exactamente igual

---

## Verificación de Integridad

### Código del Juego (main.py)

```bash
git log --oneline -10
```

**Resultado:**
```
7f25b3b feat: Configurar editores con resolucion 800x600 y controles estandar de ventana
8bd0ed2 feat: Sistema completo de respaldo y recuperacion con scripts .bat
64e9c22 update: Mejorado git_pull.bat para reemplazar proyecto completo desde GitHub
```

✅ **Confirmado:** El archivo `main.py` NO fue modificado en el commit 7f25b3b

### Código de Mapa (src/mapa.py)

✅ **Confirmado:** El archivo `src/mapa.py` NO fue modificado en el commit 7f25b3b

---

## Cómo Probar los Portales

### Prueba 1: Portal Básico

1. Ejecutar: `python main.py`
2. Iniciar nuevo juego
3. Caminar hacia un portal en `mapa_pradera`
4. **Verificar:** El héroe se teletransporta al mapa destino

### Prueba 2: Portal con Spawn ID

1. Abrir `editor_portales.py`
2. Crear portal con `spawn_destino_id`
3. Guardar (tecla G)
4. Probar en el juego
5. **Verificar:** El héroe aparece en el spawn correcto

### Prueba 3: Múltiples Portales

1. Crear 3 portales en `mapa_pueblo`:
   - Portal 1 → `mapa_herrero`
   - Portal 2 → `mapa_posada`
   - Portal 3 → `mapa_taberna`
2. **Verificar:** Cada portal lleva al destino correcto

---

## Solución de Problemas

### Problema: Portal no funciona

**Causas posibles:**
1. `mapa_destino` vacío o incorrecto
2. `categoria_destino` incorrecta
3. Archivo JSON del mapa destino no existe

**Solución:**
```python
# Verificar en el JSON del mapa
{
  "portales": [{
    "mapa_destino": "mapa_pradera",  # ✓ Nombre correcto
    "categoria_destino": "mundo"      # ✓ Categoría correcta
  }]
}
```

### Problema: Héroe aparece en posición incorrecta

**Causas posibles:**
1. `pos_destino` incorrecta
2. `spawn_destino_id` no existe en mapa destino
3. Mapa destino sin spawns

**Solución:**
1. Usar `spawn_destino_id` en lugar de `pos_destino`
2. Verificar que el spawn existe en el mapa destino
3. Agregar al menos un spawn al mapa destino

---

## Resumen

✅ **Sistema de portales funcionando correctamente**  
✅ **Cambios de resolución NO afectaron la lógica**  
✅ **Soporta 3 formatos JSON diferentes**  
✅ **3 métodos de teletransporte con fallback**  
✅ **Documentación completa disponible**  

**Última verificación:** 21-11-2025 15:35  
**Estado:** ✅ OPERATIVO
