# 📦 SISTEMA DE COFRES - CodeVerso RPG

**Fecha de Implementación:** 17 Noviembre 2025  
**Versión:** 1.0

---

## 📋 DESCRIPCIÓN GENERAL

Sistema completo de cofres interactivos en el mapa que permite al jugador obtener items, con soporte para cofres cerrados con llave.

---

## 🎨 SPRITES DEL COFRE

### Archivo: `assets/sprites/cofres y demas/cofre.png`

**Dimensiones totales:** 700x350 píxeles  
**Estados:** 3 (dispuestos horizontalmente)

| Estado | Posición X | Ancho | Descripción |
|--------|-----------|-------|-------------|
| Abierto con items | 0 | 203px | Cofre abierto mostrando contenido |
| Cerrado | 233 | 203px | Cofre cerrado (sin interactuar) |
| Vacío | 466 | 203px | Cofre abierto sin contenido |

**Alto de cada estado:** 275 píxeles

---

## 🏗️ ARQUITECTURA

### Archivos Nuevos

```
src/cofre.py                           # Clase Cofre
src/pantalla_recompensa_cofre.py       # Pantalla de items obtenidos
src/database/cofres_db.json            # Base de datos de cofres
```

### Archivos Modificados

```
src/mapa.py                            # Carga y dibuja cofres
main.py                                # Manejo de interacción con cofres
```

---

## 📦 CLASE COFRE

### Constructor

```python
Cofre(x, y, id_cofre, requiere_llave=None, items_contenido=None, escala=1.0)
```

**Parámetros:**
- `x, y`: Posición en el mapa
- `id_cofre`: ID único del cofre
- `requiere_llave`: ID de la llave necesaria (None si no requiere)
- `items_contenido`: Dict de items `{"item_id": cantidad}`
- `escala`: Escala del sprite (1.0 = tamaño original)

### Atributos

```python
self.id_cofre          # ID único
self.requiere_llave    # ID de llave o None
self.items_contenido   # Dict de items
self.abierto           # Bool: ¿ya se abrió?
self.vacio             # Bool: ¿ya se recogieron items?
self.rect              # Rectángulo de colisión
self.sprite_actual     # Sprite visible actual
```

### Métodos Principales

#### `interactuar(grupo_heroes)`
Intenta abrir el cofre.

**Returns:**
```python
{
    "exito": bool,
    "mensaje": str,
    "items_obtenidos": dict
}
```

**Lógica:**
1. Si está vacío → Retorna mensaje "vacío"
2. Si requiere llave → Verifica que el jugador la tenga
3. Si todo OK → Abre, da items, cambia a sprite vacío

#### `actualizar_sprite()`
Actualiza el sprite según el estado actual (cerrado/abierto/vacío).

#### `draw(pantalla, camara_rect)`
Dibuja el cofre en pantalla con offset de cámara.

#### `obtener_datos_guardado()` / `cargar_desde_guardado(datos)`
Serialización para sistema de guardado.

---

## 🗄️ BASE DE DATOS DE COFRES

### Archivo: `src/database/cofres_db.json`

```json
{
  "COFRE_PRADERA_01": {
    "nombre": "Cofre Pradera 1",
    "requiere_llave": null,
    "items_contenido": {
      "POCION": 3,
      "ETER": 1
    },
    "descripcion": "Un cofre simple sin cerradura"
  },
  
  "COFRE_PRADERA_SECRETO": {
    "nombre": "Cofre Secreto",
    "requiere_llave": "LLAVE_BRONCE",
    "items_contenido": {
      "POCION": 5,
      "ETER": 3,
      "EXPANSOR_RANURAS": 1
    },
    "descripcion": "Un cofre cerrado con llave de bronce"
  }
}
```

### Estructura de Entrada

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | string | Nombre descriptivo |
| `requiere_llave` | string\|null | ID de llave necesaria |
| `items_contenido` | object | Dict de items y cantidades |
| `descripcion` | string | Descripción del cofre |

---

## 🗺️ CONFIGURACIÓN EN MAPAS

### Agregar Cofres a un Mapa

En el archivo JSON del mapa (ej. `mapa_pradera.json`):

```json
{
  "muros": [...],
  "zonas_batalla": [...],
  "portales": [...],
  "cofres": [
    {
      "id_cofre": "COFRE_PRADERA_01",
      "x": 300,
      "y": 400,
      "escala": 0.3
    },
    {
      "id_cofre": "COFRE_PRADERA_SECRETO",
      "x": 800,
      "y": 300,
      "escala": 0.3
    }
  ]
}
```

### Parámetros de Cofre en Mapa

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_cofre` | string | Debe existir en cofres_db.json |
| `x` | int | Posición X en el mapa |
| `y` | int | Posición Y en el mapa |
| `escala` | float | Escala del sprite (0.3 recomendado) |

---

## 🎮 INTERACCIÓN DEL JUGADOR

### Flujo de Interacción

1. **Jugador presiona "I" cerca de un cofre**
2. **Sistema verifica:**
   - ¿Está vacío? → Mensaje "vacío"
   - ¿Requiere llave? → Verifica inventario
   - ¿No tiene llave? → Mensaje "cerrado con llave"
3. **Si todo OK:**
   - Abre el cofre (sprite → abierto)
   - Agrega items al inventario del líder
   - Muestra pantalla de recompensa
   - Cambia sprite a vacío
4. **Pantalla de recompensa se cierra automáticamente en 3s**

### Controles

| Tecla | Acción |
|-------|--------|
| `I` | Interactuar con cofre cercano (en mapa) |
| `ENTER` | Cerrar pantalla de recompensa |
| `ESC` | Cerrar pantalla de recompensa |

---

## 🔧 MÉTODOS EN MAPA.PY

### `cargar_cofres_db()`
Carga la base de datos de cofres desde JSON.

### `chequear_cofre_cercano(rect_heroe, distancia=50)`
Verifica si hay un cofre cerca del héroe.

**Returns:** `Cofre` si hay uno cerca, `None` si no.

**Uso:**
```python
cofre_cercano = mi_mapa.chequear_cofre_cercano(heroe.heroe_rect)
if cofre_cercano:
    resultado = cofre_cercano.interactuar(grupo_heroes)
```

---

## 💾 SISTEMA DE GUARDADO

### Datos a Guardar

Para cada cofre en el mapa:

```python
{
    "id_cofre": "COFRE_PRADERA_01",
    "abierto": true,
    "vacio": true,
    "x": 300,
    "y": 400
}
```

### Implementación (Futuro)

En `gestor_guardado.py`:

```python
# Guardar
"cofres": [cofre.obtener_datos_guardado() for cofre in mi_mapa.cofres]

# Cargar
for cofre_data in datos["cofres"]:
    cofre = encontrar_cofre_por_id(cofre_data["id_cofre"])
    if cofre:
        cofre.cargar_desde_guardado(cofre_data)
```

---

## 🎨 PANTALLA DE RECOMPENSA

### Clase: `PantallaRecompensaCofre`

**Características:**
- Fondo semi-transparente negro
- Cuadro central con borde dorado
- Título "¡Cofre Abierto!"
- Lista de items obtenidos con colores:
  - Verde: Consumibles
  - Dorado: Items especiales
  - Blanco: Otros
- Auto-cierre en 3 segundos
- Contador regresivo visible

### Uso

```python
# En main.py
if tecla_i_presionada:
    cofre = mi_mapa.chequear_cofre_cercano(heroe.heroe_rect)
    if cofre:
        resultado = cofre.interactuar(grupo_heroes)
        if resultado["exito"]:
            pantalla_recompensa = PantallaRecompensaCofre(
                ANCHO, ALTO,
                resultado["items_obtenidos"],
                ITEMS_DB
            )
            estado_juego = "recompensa_cofre"
```

---

## 🔄 INTEGRACIÓN CON MAIN.PY

### Estado de Juego Nuevo

```python
estado_juego = "recompensa_cofre"
```

### Event Loop

```python
# Tecla I para interactuar
if event.key == pygame.K_i:
    if estado_juego == "mapa":
        cofre_cercano = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
        if cofre_cercano:
            resultado = cofre_cercano.interactuar(grupo_heroes)
            if resultado["exito"]:
                mi_pantalla_recompensa = PantallaRecompensaCofre(
                    ANCHO, ALTO,
                    resultado["items_obtenidos"],
                    ITEMS_DB
                )
                estado_juego = "recompensa_cofre"
            else:
                # Mostrar mensaje en pantalla
                print(resultado["mensaje"])
```

### Update Loop

```python
elif estado_juego == "recompensa_cofre":
    if mi_pantalla_recompensa:
        mi_pantalla_recompensa.update(teclas)
        if mi_pantalla_recompensa.cerrar:
            estado_juego = "mapa"
            mi_pantalla_recompensa = None
```

### Draw Loop

```python
elif estado_juego == "recompensa_cofre":
    # Dibujar mapa de fondo
    if mi_mapa:
        mi_mapa.draw(PANTALLA)
    if grupo_heroes:
        grupo_heroes[0].draw(PANTALLA, mi_mapa.camara_rect)
    
    # Dibujar pantalla de recompensa encima
    if mi_pantalla_recompensa:
        mi_pantalla_recompensa.draw(PANTALLA)
```

---

## ✅ PRUEBAS DE SISTEMA

### Checklist de Testing

- [ ] Cofre sin llave se abre correctamente
- [ ] Cofre con llave requiere la llave correcta
- [ ] Items se agregan al inventario del líder
- [ ] Sprite cambia de cerrado → abierto → vacío
- [ ] Pantalla de recompensa muestra items correctos
- [ ] Colores de items correctos (verde/dorado)
- [ ] Auto-cierre funciona después de 3s
- [ ] ENTER cierra inmediatamente
- [ ] Cofre vacío muestra mensaje correcto
- [ ] Interacción sin llave muestra mensaje correcto
- [ ] Sistema de guardado preserva estado de cofres

---

## 🔮 MEJORAS FUTURAS

### Versión 1.1
- [ ] Sonido de apertura de cofre
- [ ] Animación de apertura (transición entre sprites)
- [ ] Partículas doradas al abrir
- [ ] Cofres trampa (batalla al abrir)

### Versión 1.2
- [ ] Cofres con múltiples llaves (AND/OR)
- [ ] Cofres con acertijos
- [ ] Cofres con temporizador
- [ ] Cofres mimic (se transforman en monstruo)

### Versión 1.3
- [ ] Sistema de logro "Cofres encontrados"
- [ ] Mapa de tesoros (muestra ubicación de cofres)
- [ ] Cofres legendarios con efectos especiales
- [ ] Sistema de probabilidad de items (loot table)

---

## 📝 EJEMPLOS DE USO

### Ejemplo 1: Cofre Simple

```json
"COFRE_TUTORIAL": {
  "nombre": "Cofre de Tutorial",
  "requiere_llave": null,
  "items_contenido": {
    "POCION": 2
  },
  "descripcion": "Tu primer cofre"
}
```

### Ejemplo 2: Cofre con Llave

```json
"COFRE_TESORO": {
  "nombre": "Cofre de Tesoro",
  "requiere_llave": "LLAVE_ORO",
  "items_contenido": {
    "POCION": 10,
    "ETER": 5,
    "EXPANSOR_RANURAS": 1
  },
  "descripcion": "Un cofre dorado muy valioso"
}
```

### Ejemplo 3: Cofre Secreto

```json
"COFRE_OCULTO": {
  "nombre": "Cofre Oculto",
  "requiere_llave": "LLAVE_MAESTRA",
  "items_contenido": {
    "EXPANSOR_RANURAS": 3,
    "POCION": 99
  },
  "descripcion": "Solo para los más curiosos"
}
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: Sprite no se carga

**Causa:** Ruta incorrecta o archivo no encontrado  
**Solución:** Verificar que `cofre.png` esté en `assets/sprites/cofres y demas/`

### Problema: Cofre no aparece en mapa

**Causa:** ID de cofre no existe en `cofres_db.json`  
**Solución:** Agregar entrada en la base de datos

### Problema: Llave no funciona

**Causa:** ID de llave no coincide  
**Solución:** Verificar que el ID en `cofres_db.json` coincida con `items_db.json`

### Problema: Items no se agregan

**Causa:** Items no existen en `items_db.json`  
**Solución:** Agregar items a la base de datos primero

---

## 📚 REFERENCIAS

**Archivos relacionados:**
- `src/cofre.py`
- `src/pantalla_recompensa_cofre.py`
- `src/mapa.py`
- `src/database/cofres_db.json`
- `src/database/items_db.json`

**Documentación relacionada:**
- `SISTEMA_ITEMS_ESPECIALES.md`
- `DATABASE.md`
- `ARQUITECTURA.md`

---

**Última Actualización:** 17 Noviembre 2025  
**Autor:** CodeVerso RPG Development Team  
**Versión del Documento:** 1.0
