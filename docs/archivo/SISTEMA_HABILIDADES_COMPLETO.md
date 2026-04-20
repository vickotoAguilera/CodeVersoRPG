# Sistema de Habilidades con DOT/HOT y AoE - Implementación Completa

## Resumen de Cambios

Se ha implementado un sistema completo de habilidades para el juego, incluyendo soporte para efectos de daño/curación sobre tiempo (DOT/HOT) y ataques de área (AoE).

## Archivos Modificados

### 1. `src/database/habilidades_db.json`
**Cambios:** Se agregaron nuevas habilidades con efectos DOT/HOT:
- **Quemadura (DOT)**: Causa 15 de daño por turno durante 3 turnos
- **Veneno (DOT)**: Causa 12 de daño por turno durante 4 turnos
- **Revitalizar (HOT)**: Regenera 20 HP por turno durante 3 turnos
- **Éter (HOT MP)**: Regenera 10 MP por turno durante 3 turnos
- **Llamas Infernales (AoE DOT)**: Daño en área que aplica quemadura a todos los enemigos

### 2. `src/monstruo.py`
**Cambios:** 
- Agregado atributo `efectos_activos = []` para rastrear efectos DOT/HOT
- Método `agregar_efecto(tipo_efecto, duracion, valor)`: Agrega un efecto al monstruo
- Método `procesar_efectos_turno()`: Procesa efectos al inicio del turno, aplicando daño/curación y reduciendo duración

### 3. `src/heroe.py`
**Cambios:**
- Agregado atributo `efectos_activos = []` para rastrear efectos DOT/HOT
- Método `agregar_efecto(tipo_efecto, duracion, valor, es_mp=False)`: Agrega un efecto al héroe
- Método `procesar_efectos_turno()`: Procesa efectos al inicio del turno, soportando:
  - DOT (Daño sobre tiempo)
  - HOT HP (Curación de HP sobre tiempo)
  - HOT MP (Regeneración de MP sobre tiempo)

### 4. `src/pantalla_lista_habilidades.py` (NUEVO)
**Archivo nuevo:** Pantalla de selección de habilidades en batalla
- Muestra héroes a la izquierda con HP/MP
- Muestra habilidades equipadas del héroe seleccionado a la derecha
- Panel de descripción en la parte superior
- Navegación con flechas y selección con ENTER
- Devuelve la habilidad seleccionada al presionar ENTER

### 5. `src/batalla.py`
**Cambios importantes:**

#### Menú actualizado:
- Agregado "Habilidades" entre "Atacar" y "Magia"
- Nuevo orden: `["Atacar", "Habilidades", "Magia", "Objeto", "Huir"]`

#### Nuevas importaciones:
- `from src.pantalla_lista_habilidades import PantallaListaHabilidades`

#### Carga de base de datos:
- Agregada carga de `habilidades_db.json` en el constructor

#### Nuevos atributos:
- `self.pantalla_habilidades_activa = None`
- `self.accion_habilidad_pendiente = None`

#### Nueva funcionalidad en `seleccionar_opcion()`:
```python
elif opcion == "Habilidades":
    # Verifica que el héroe tenga habilidades equipadas
    if not heroe_atacante.habilidades_activas or not any(hab for hab in heroe_atacante.habilidades_activas if hab):
        print(f"¡{heroe_atacante.nombre_clase} no tiene habilidades equipadas!")
        return None 
    
    print("¡Iniciando selección de Habilidad!")
    return "iniciar_seleccion_habilidad"
```

#### Nuevo estado: `"JUGADOR_ELIGE_HABILIDAD"`
- Agregado a `estados_permitidos`
- Maneja la navegación en la pantalla de habilidades
- Determina el targeting según el alcance de la habilidad:
  - "Un Enemigo": Va al estado de targeting de monstruos
  - "Todos Enemigos": Ejecuta AoE directamente
  - "Un Aliado": Va al estado de targeting de aliados
  - "Todos Aliados": Ejecuta AoE directamente
  - "Usuario": Se aplica al usuario directamente

#### Nuevas funciones:

**`ejecutar_habilidad_heroe(heroe_actor, objetivo, habilidad_data, tiempo_actual)`:**
- Ejecuta una habilidad sobre un objetivo único
- Calcula daño basándose en Inteligencia (magias) o Fuerza (físicas)
- Aplica efectos DOT/HOT según corresponda
- Muestra textos flotantes con colores apropiados
- Gasta MP del héroe

**`ejecutar_habilidad_aoe(heroe_actor, lista_objetivos, habilidad_data, tiempo_actual)`:**
- Ejecuta una habilidad sobre múltiples objetivos
- Aplica el efecto a cada objetivo en la lista
- Crea textos flotantes para cada objetivo
- Aplica efectos DOT/HOT a todos los afectados

#### Procesamiento de efectos:
- En `PROCESAR_TURNO`: Se agregó llamada a `procesar_efectos_turno()` al inicio del turno de cada actor
- Los efectos se procesan automáticamente antes de que el actor tome su turno
- Los mensajes de efectos se imprimen en la consola

#### Targeting actualizado:
- `HEROE_ELIGE_MONSTRUO`: Ahora también maneja habilidades con `self.accion_habilidad_pendiente`
- `JUGADOR_ELIGE_ALIADO`: Ahora también maneja habilidades con `self.accion_habilidad_pendiente`
- Escape devuelve a la pantalla de habilidades si hay una acción de habilidad pendiente

#### Update y Draw:
- Agregado update de `pantalla_habilidades_activa` en estado `JUGADOR_ELIGE_HABILIDAD`
- Agregado draw de `pantalla_habilidades_activa` en el método draw

## Cómo Usar el Sistema

### En Batalla:
1. Cuando sea el turno de un héroe, selecciona "Habilidades" en el menú
2. Se abrirá la pantalla de habilidades mostrando todos los héroes
3. Navega con ↑/↓ entre héroes
4. Presiona → para ver las habilidades del héroe seleccionado
5. Navega con ↑/↓ entre habilidades
6. Presiona ENTER para seleccionar una habilidad
7. Según el alcance de la habilidad:
   - **Un Enemigo**: Selecciona el enemigo objetivo
   - **Un Aliado**: Selecciona el aliado objetivo
   - **Todos Enemigos/Aliados**: Se ejecuta automáticamente
   - **Usuario**: Se aplica al héroe automáticamente
8. Los efectos DOT/HOT se procesan automáticamente al inicio de cada turno

### Tipos de Efectos:

**DOT (Damage Over Time)**:
- Se aplica daño automáticamente al inicio del turno del afectado
- Dura el número de turnos especificado en `dot_duracion`
- Causa el daño especificado en `dot_dano`
- Ejemplos: Quemadura, Veneno, Llamas Infernales

**HOT (Heal Over Time)**:
- Se aplica curación automáticamente al inicio del turno del afectado
- Dura el número de turnos especificado en `hot_duracion`
- Cura según el valor especificado:
  - `hot_curacion`: Para curación de HP
  - `hot_mp`: Para regeneración de MP
- Ejemplos: Revitalizar (HP), Éter (MP)

**AoE (Area of Effect)**:
- Afecta a todos los objetivos del tipo especificado
- Puede aplicar efectos DOT/HOT a todos los afectados
- Muestra textos flotantes en color naranja para daño AoE
- Muestra textos flotantes en verde claro para curación AoE

## Estructura de Habilidades en JSON

```json
{
    "ID_HABILIDAD": {
        "id_habilidad": "ID_HABILIDAD",
        "nombre": "Nombre de la Habilidad",
        "tipo": "Magia Negra | Magia Blanca | Habilidad Fisica",
        "descripcion": "Descripción de la habilidad",
        "costo_mp": 10,
        "poder": 15,
        "alcance": "Un Enemigo | Todos Enemigos | Un Aliado | Todos Aliados | Usuario",
        "efecto": "DOT_QUEMADURA | HOT_REGENERACION | HOT_ETER | etc.",
        "dot_duracion": 3,    // Solo para DOT
        "dot_dano": 15,       // Solo para DOT
        "hot_duracion": 3,    // Solo para HOT
        "hot_curacion": 20,   // Solo para HOT HP
        "hot_mp": 10          // Solo para HOT MP
    }
}
```

## Colores de Textos Flotantes

- **Blanco (255, 255, 255)**: Daño físico normal
- **Rojo claro (255, 100, 100)**: Daño mágico
- **Naranja (255, 150, 0)**: Daño AoE
- **Verde (0, 255, 0)**: Curación única
- **Verde claro (100, 255, 100)**: Curación AoE
- **Morado (150, 100, 255)**: Restauración de MP

## Próximas Mejoras Sugeridas

1. **Indicadores visuales de efectos**: Mostrar íconos sobre los personajes con efectos activos
2. **Contador de turnos**: Mostrar cuántos turnos quedan de cada efecto
3. **Efectos de estado adicionales**: Parálisis, Silencio, Confusión, etc.
4. **Resistencias**: Algunos enemigos podrían ser resistentes a ciertos efectos
5. **Stacking de efectos**: Permitir múltiples efectos del mismo tipo con diferente duración
6. **Efectos visuales**: Partículas o animaciones para DOT/HOT
7. **Sonidos**: Efectos de sonido al aplicar y procesar efectos

## Testing

Para probar el sistema:
1. Ejecuta el juego: `python main.py`
2. Inicia una batalla
3. En el turno de un héroe, selecciona "Habilidades"
4. Prueba diferentes habilidades:
   - Quemadura en un enemigo (verás daño cada turno)
   - Revitalizar en un aliado (verás curación cada turno)
   - Llamas Infernales para AoE (todos los enemigos reciben daño)
   - Éter para regenerar MP

## Notas Importantes

- Los efectos se procesan automáticamente al inicio de cada turno
- Si un personaje muere por un efecto DOT, se procesa normalmente
- Los efectos terminan automáticamente después del número de turnos especificado
- Los textos flotantes muestran el daño/curación de los efectos
- Los efectos persisten entre rondas de batalla
- Se puede tener múltiples efectos activos simultáneamente
