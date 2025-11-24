# Sistema de Habilidades Equipables - Progreso

## 📊 Estado Actual: Fase 7 - Sistema de Habilidades

---

## ✅ Completado

### Paso 7.11-7.13: Bases del Sistema ✅
**Archivos creados/modificados:**
- `database/habilidades_db.json` - Base de datos de habilidades
- `database/heroes_db.json` - Actualizado con campos de habilidades
- `main.py` (líneas 31, 49-50) - Carga de HABILIDADES_DB

**Qué hace:**
Define habilidades equipables como items. Cada héroe tiene:
- `clase`: "Guerrero", "Mago", etc.
- `ranuras_habilidad_max`: 4 (slots equipables)
- `habilidades_activas`: [hab1, hab2, null, null] (equipadas)
- `inventario_habilidades`: [hab1, hab2, hab3...] (todas las aprendidas)

### Paso 7.14: Actualizar heroe.py ✅
**Archivo modificado:**
- `src/heroe.py` (líneas 37-41)

**Qué hace:**
La clase Heroe ahora lee y almacena:
- `self.clase` - Tipo de héroe
- `self.ranuras_habilidad_max` - Cantidad de slots
- `self.habilidades_activas` - Habilidades equipadas
- `self.inventario_habilidades` - Todas las habilidades aprendidas

---

## 🔄 En Progreso

### Paso 7.15: Sistema de Guardado/Carga ✅
**Archivos modificados:**
- `main.py` (líneas 380-384) - Función de guardar
- `main.py` (líneas 282-286) - Función de cargar

**Qué hace:**
Agrega los nuevos campos al guardado/carga:
```python
"clase": heroe.clase,
"ranuras_habilidad_max": heroe.ranuras_habilidad_max,
"habilidades_activas": heroe.habilidades_activas,
"inventario_habilidades": heroe.inventario_habilidades
```

Ahora al guardar y cargar una partida, se preservan las habilidades equipadas y el inventario de habilidades.

**Estado:** COMPLETADO

---

## ✅ Completado (continuación 2)

### Paso 7.16: Botón "Habilidades" en Menú ✅
**Archivo modificado:**
- `src/menu_pausa.py` (líneas 159-165, 200-202)

**Qué hace:**
Conecta el botón "Habilidades" del menú de pausa:

1. **Al presionar Enter en "Habilidades":**
   - Cambia el modo a `"heroes"` (panel derecho)
   - Establece `proposito_foco_heroe = "habilidades"`
   - Permite seleccionar un héroe

2. **Al seleccionar un héroe:**
   - Devuelve: `{"accion": "abrir_habilidades_heroe", "indice_heroe": X}`
   - main.py recibirá esta acción para abrir la pantalla

**Funcionamiento:**
- Igual que el botón "Equipo"
- Primero seleccionas "Habilidades" → Luego seleccionas el héroe
- ESC vuelve al menú de opciones

**Estado:** COMPLETADO

---

## 🔄 En Progreso

### Paso 7.16: Botón "Habilidades" en Menú ✅
**Archivo modificado:**
- `src/menu_pausa.py`

**Estado:** ✅ Actualizado

### Paso 7.17: Crear Pantalla de Habilidades ✅
**Archivo nuevo:**
- `src/pantalla_habilidades.py` (~780 líneas)

**Estado:** ✅ Creado

### Paso 7.18: Conectar Pantalla al Juego ✅
**Archivo modificado:**
- `main.py`

**Cambios realizados:**
1. ✅ Importar `from src.pantalla_habilidades import PantallaHabilidades`
2. ✅ Crear variable `mi_pantalla_habilidades = None`
3. ✅ Agregar estado `"pantalla_habilidades"` al flujo
4. ✅ Manejar acción `"abrir_habilidades_heroe"` desde menu_pausa
5. ✅ Manejar entrada cuando pantalla_habilidades esté activa
6. ✅ Manejar salida con acción `"volver_al_menu"`
7. ✅ Agregar teclas D y X para detalles y desequipar
8. ✅ Agregar pantalla al loop de update()
9. ✅ Agregar pantalla al sistema de dibujo

**Estado:** ✅ COMPLETADO

```
┌─────────────────────────────────────────────────────┐
│ HABILIDADES: Cloud                                  │
├──────────┬──────────────────┬────────────────────────┤
│          │                  │                        │
│  Sprite  │   INVENTARIO     │   DESCRIPCIÓN          │
│  Héroe   │   Habilidades    │   Nombre: Corte X      │
│          │   (scroll)       │   Tipo: Física         │
│  [CLOUD] │                  │   Costo MP: 5          │
│          │   > Corte X      │   Poder: 25            │
│          │     Golpe Fuerte │   Alcance: 1 Enemigo   │
│          │     [Vacío]      │                        │
│          │                  │   Descripción:         │
│          │                  │   Un ataque cruzado... │
│          │                  │   (scroll)             │
├──────────┴──────────────────┴────────────────────────┤
│ RANURAS ACTIVAS (4 slots)                           │
│ [1: Corte X] [2: Vacío] [3: Vacío] [4: Vacío]      │
└─────────────────────────────────────────────────────┘
```

**4 Paneles:**
1. **Izquierdo:** Sprite del héroe
2. **Derecho:** Lista de habilidades (filtradas por clase)
3. **Central:** Descripción detallada
4. **Inferior:** Ranuras activas (equipar/desequipar)

### Paso 7.18: Conectar Pantalla al Juego
**Archivo a modificar:**
- `main.py`

**Qué hacer:**
1. Importar `pantalla_habilidades.py`
2. Crear estado `"pantalla_habilidades"`
3. Manejar entrada y salida

### Paso 7.19: Lógica de Equipar/Desequipar
**Archivo:**
- `src/pantalla_habilidades.py`

**Funcionalidad:**
1. Filtrar habilidades por clase del héroe
2. Equipar: Mover de inventario → ranura activa
3. Desequipar: Mover de ranura activa → inventario
4. Validar que no se excedan las ranuras
5. Validar que la habilidad sea de la clase correcta

---

## 📁 Archivos del Sistema de Habilidades

### Archivos de Base de Datos
| Archivo | Ubicación | Propósito | Estado |
|---------|-----------|-----------|--------|
| habilidades_db.json | database/ | Define todas las habilidades | ✅ Creado |
| heroes_db.json | database/ | Stats de héroes + habilidades | ✅ Actualizado |

### Archivos de Código
| Archivo | Ubicación | Propósito | Estado |
|---------|-----------|-----------|--------|
| heroe.py | src/ | Clase Heroe con habilidades | ✅ Actualizado |
| main.py | raíz | Carga DB y guardado/carga | ✅ Completado |
| menu_pausa.py | src/ | Botón habilidades | ✅ Actualizado |
| pantalla_habilidades.py | src/ | UI de habilidades | ✅ Creado |

---

## 🎯 Próximo Paso

**¡FASE 7 COMPLETADA! 🎉**

El sistema de habilidades está 100% implementado y funcional.

### ✅ Lo que ya funciona:
- Base de datos de habilidades (JSON)
- Héroe con inventario y ranuras de habilidades
- Guardado/carga de habilidades
- Botón "Habilidades" en menú de pausa
- Pantalla completa de gestión (equipar/desequipar)
- Filtrado por clase (Guerrero/Mago)

### 🚀 Próxima Fase: 8 - Gestión de Grupo

**Objetivos:**
1. Crear 3 nuevos héroes (actualizar heroes_db.json)
2. Implementar pantalla de "Gestión de Grupo"
3. Intercambiar miembros (grupo activo ↔ banca)
4. Función "Cambiar Líder" (ranura[0] es quien camina)

**Tiempo estimado:** 2-3 horas

---

## 📝 Notas Técnicas

### Estructura de habilidades_db.json
```json
{
    "ID_HABILIDAD": {
        "id_habilidad": "ID_HABILIDAD",
        "nombre": "Corte Cruzado",
        "tipo": "Habilidad Fisica",
        "descripcion": "Un ataque físico poderoso",
        "costo_mp": 5,
        "poder": 25,
        "alcance": "Un Enemigo",
        "efecto": null,
        "clase_requerida": "Guerrero"
    }
}
```

### Campos en heroes_db.json
```json
{
    "HEROE_1": {
        "clase": "Guerrero",
        "ranuras_habilidad_max": 4,
        "habilidades_activas": ["CORTE_X", null, null, null],
        "inventario_habilidades": ["CORTE_X", "GOLPE_FUERTE"]
    }
}
```

### Campos en Heroe
```python
self.clase = "Guerrero"
self.ranuras_habilidad_max = 4
self.habilidades_activas = ["CORTE_X", None, None, None]
self.inventario_habilidades = ["CORTE_X", "GOLPE_FUERTE", "EMBESTIDA"]
```

---

## 🔮 Visión Futura (Post Fase 7)

### Fase 8: Gestión de Grupo
- 3 nuevos héroes
- Pantalla de gestión de grupo (4 activos + banca)
- Cambiar líder

### Fase 9: NPCs y Mundo
- Sistema de diálogos
- Tiendas
- Misiones

### Fase 10: Game Over y Opciones
- Lógica de Game Over
- Menú de opciones (resolución, pantalla completa)

### Fase 11: Gamepad
- Soporte para controles

---

**Última actualización:** 2025-11-15  
**Fase actual:** ✅ FASE 7 COMPLETADA  
**Progreso Fase 7:** 100% (Sistema de Habilidades COMPLETO)
