# Sistema DOT/HOT Completamente Implementado

**Fecha:** 16 Noviembre 2025
**Estado:** ✅ COMPLETADO Y FUNCIONAL

---

## 📋 Resumen

El sistema de efectos DOT (Damage Over Time) y HOT (Heal Over Time) está completamente implementado y conectado con el sistema de batalla.

---

## ✅ Componentes Implementados

### 1. Estructura de Efectos en Héroe y Monstruo

**Archivos:** `heroe.py`, `monstruo.py`

Ambas clases tienen:
- `efectos_activos = []` - Lista que almacena efectos activos
- `agregar_efecto(tipo, duracion, valor, es_mp=False)` - Agrega nuevos efectos
- `procesar_efectos_turno()` - Procesa efectos al inicio del turno

### 2. Procesamiento en Batalla

**Archivo:** `batalla.py` (líneas 420-465)

Al inicio de cada turno:
1. Se procesan los efectos del actor actual
2. Se genera texto flotante para cada efecto
3. Se verifica si el actor muere por DOT
4. Los efectos con duración 0 se eliminan automáticamente

### 3. Aplicación de Efectos

**Archivo:** `batalla.py`

Las funciones `ejecutar_habilidad_heroe()` y `ejecutar_habilidad_aoe()` aplican efectos cuando corresponde según el tipo de habilidad.

---

## 🎯 Tipos de Efectos Soportados

### DOT (Damage Over Time)
- **DOT_QUEMADURA**: Daño de fuego por turno
- **DOT_SANGRADO**: Daño de sangrado por turno
- **DOT_VENENO**: Daño de veneno por turno
- **DOT_QUEMADURA_AOE**: Quemadura aplicada en área

### HOT (Heal Over Time)
- **HOT_RECUPERACION**: Regeneración de HP por turno
- **HOT_REGENERACION**: Regeneración de HP por turno
- **HOT_ETER**: Regeneración de MP por turno

---

## 🔥 Habilidades con Efectos DOT/HOT

### Habilidades DOT

1. **Quemadura** (ID_QUEMADURA)
   - Tipo: Magia Negra
   - Costo: 10 MP
   - Daño inicial: 10
   - DOT: 15 de daño x 3 turnos
   - Alcance: Un Enemigo

2. **Sangrado** (ID_SANGRADO)
   - Tipo: Habilidad Física
   - Costo: 6 MP
   - Daño inicial: 5
   - DOT: 8 de daño x 3 turnos
   - Alcance: Un Enemigo

3. **Veneno** (ID_VENENO)
   - Tipo: Habilidad Física
   - Costo: 8 MP
   - Daño inicial: 5
   - DOT: 12 de daño x 4 turnos
   - Alcance: Un Enemigo

4. **Llamas Infernales** (ID_LLAMAS_INFERNALES)
   - Tipo: Magia Negra
   - Costo: 20 MP
   - Daño inicial: 15
   - DOT: 10 de daño x 3 turnos
   - Alcance: Todos los Enemigos (AoE)

### Habilidades HOT

1. **Recuperación** (ID_RECUPERACION)
   - Tipo: Habilidad Defensa
   - Costo: 8 MP
   - Curación inicial: 10
   - HOT: +15 HP x 3 turnos
   - Alcance: Usuario

2. **Revitalizar** (ID_REVITALIZAR)
   - Tipo: Magia Blanca
   - Costo: 10 MP
   - Curación inicial: 0
   - HOT: +20 HP x 3 turnos
   - Alcance: Un Aliado

3. **Éter** (ID_ETER)
   - Tipo: Magia Blanca
   - Costo: 5 MP
   - Regeneración: 0
   - HOT: +10 MP x 3 turnos
   - Alcance: Un Aliado

---

## 🎨 Indicadores Visuales

### Colores de Texto Flotante

- **DOT (Daño)**: Rojo (255, 100, 100) - Muestra `-valor`
- **HOT (Curación HP)**: Verde (100, 255, 100) - Muestra `+valor`
- **HOT (Regeneración MP)**: Azul (100, 150, 255) - Muestra `+valor MP`

### Posicionamiento

- **Héroes**: Texto aparece en `pos_actual_y - 50`
- **Monstruos**: Texto aparece en `rect.top - 30`

---

## 🔄 Flujo de Procesamiento

### Al Usar Habilidad con Efecto

1. Se ejecuta el efecto inmediato (daño o curación)
2. Se llama a `objetivo.agregar_efecto(tipo, duracion, valor, es_mp)`
3. El efecto se añade a la lista `efectos_activos` del objetivo
4. Se muestra mensaje en consola: "X ahora tiene el efecto: Y por Z turnos"

### Al Inicio de Cada Turno

1. El actor actual llama a `procesar_efectos_turno()`
2. Para cada efecto en `efectos_activos`:
   - Se aplica el daño/curación correspondiente
   - Se genera un texto flotante con el valor
   - Se reduce la duración en 1
   - Si duración llega a 0, el efecto se elimina
3. Se retorna lista de mensajes para mostrar

### Ejemplos de Mensajes

```
Cloud recibe 15 de daño por DOT_QUEMADURA! HP: 85/100
Terra recupera 10 MP por HOT_ETER! MP: 45/100
Goblin recibe 8 de daño por DOT_SANGRADO! HP: 22/50
El efecto DOT_QUEMADURA en Cloud ha terminado.
```

---

## 🧪 Cómo Probar el Sistema

### Probar DOT

1. Iniciar batalla
2. Seleccionar "Habilidades"
3. Elegir "Quemadura", "Sangrado" o "Veneno"
4. Aplicar en enemigo
5. Observar:
   - Daño inicial inmediato
   - En cada turno del enemigo, aparece texto flotante rojo con daño adicional
   - Después de 3-4 turnos, el efecto desaparece

### Probar HOT

1. Iniciar batalla
2. Seleccionar "Habilidades"
3. Elegir "Recuperación" (en sí mismo) o "Revitalizar" (en aliado)
4. Observar:
   - Curación inicial (si corresponde)
   - En cada turno del héroe afectado, texto flotante verde con curación
   - Después de 3 turnos, el efecto desaparece

### Probar HOT de MP

1. Gastar MP en habilidades
2. Usar "Éter" en héroe con bajo MP
3. Observar texto flotante azul "+10 MP" cada turno

### Probar AoE DOT

1. Usar "Llamas Infernales" (si hay múltiples enemigos)
2. Todos los enemigos recibirán el efecto de quemadura
3. Cada enemigo mostrará daño DOT en su turno

---

## 📊 Estadísticas de Efectos

### Tabla Comparativa

| Efecto | Tipo | Duración | Valor/Turno | Total |
|--------|------|----------|-------------|-------|
| Quemadura | DOT | 3 turnos | 15 HP | 45 HP |
| Sangrado | DOT | 3 turnos | 8 HP | 24 HP |
| Veneno | DOT | 4 turnos | 12 HP | 48 HP |
| Recuperación | HOT | 3 turnos | 15 HP | 45 HP |
| Revitalizar | HOT | 3 turnos | 20 HP | 60 HP |
| Éter | HOT MP | 3 turnos | 10 MP | 30 MP |

---

## 🛠️ Mantenimiento y Extensión

### Agregar Nuevo Efecto DOT

```json
{
    "id_habilidad": "ID_NUEVA_DOT",
    "nombre": "Nueva DoT",
    "tipo": "Magia Negra",
    "descripcion": "Causa X de daño por turno durante Y turnos",
    "costo_mp": 10,
    "poder": 5,
    "alcance": "Un Enemigo",
    "efecto": "DOT_NUEVO_EFECTO",
    "dot_duracion": 3,
    "dot_dano": 20
}
```

### Agregar Nuevo Efecto HOT

```json
{
    "id_habilidad": "ID_NUEVA_HOT",
    "nombre": "Nueva HoT",
    "tipo": "Magia Blanca",
    "descripcion": "Regenera X HP por turno durante Y turnos",
    "costo_mp": 8,
    "poder": 0,
    "alcance": "Un Aliado",
    "efecto": "HOT_NUEVO_EFECTO",
    "hot_duracion": 3,
    "hot_curacion": 25
}
```

No se requiere modificar código, el sistema detecta automáticamente cualquier efecto que contenga "DOT" o "HOT" en su nombre.

---

## ⚠️ Consideraciones Importantes

### Stack de Efectos
- **Múltiples efectos del mismo tipo NO se stackean**, se sobrescriben
- Si se aplica DOT_QUEMADURA mientras ya existe, se reinicia la duración
- Diferentes tipos de DOT (Quemadura, Veneno, Sangrado) SÍ se acumulan

### Orden de Procesamiento
1. Efectos se procesan al **inicio** del turno del actor
2. El actor recibe daño/curación ANTES de realizar su acción
3. Si un actor muere por DOT, su turno se salta automáticamente

### Performance
- Sistema optimizado para hasta 10 efectos simultáneos por actor
- Los efectos se almacenan en listas simples (búsqueda O(n))
- Limpieza automática de efectos expirados

---

## 🎯 Estado del Sistema

✅ **Completamente funcional**
✅ **Probado con múltiples habilidades**
✅ **Visualización correcta con textos flotantes**
✅ **Integrado con sistema de batalla**
✅ **Documentado completamente**

---

## 📝 Archivos Modificados

1. `src/batalla.py` - Ejecución y procesamiento de efectos
2. `src/heroe.py` - Métodos de efectos para héroes
3. `src/monstruo.py` - Métodos de efectos para monstruos
4. `src/database/habilidades_db.json` - Definiciones actualizadas

---

**Última actualización:** 16 Nov 2025 - 14:10 UTC
