# Sistema de Habilidades - Documentación de Cambios

## Fecha: 2025-11-15

## Resumen de Cambios

Se ha implementado un sistema completo de habilidades equipables con ranuras dinámicas y scroll horizontal.

---

## 1. Nuevo Ítem: Expansor de Ranuras

### Archivo: `src/database/items_db.json`

Se agregó un nuevo ítem especial que aumenta permanentemente las ranuras de habilidades:

```json
"EXPANSOR_RANURAS": {
    "id_item": "EXPANSOR_RANURAS",
    "nombre": "Expansor de Ranuras",
    "descripcion": "Aumenta permanentemente las ranuras de habilidades de un héroe en +2. Acumulable.",
    "tipo": "Especial",
    "efecto": "AUMENTA_RANURAS_HABILIDAD",
    "poder": 2,
    "target": "Heroe"
}
```

**Funcionamiento:**
- Cada Expansor de Ranuras aumenta `ranuras_habilidad_max` del héroe en +2
- Es acumulable: si usas 2 expansores, obtienes +4 ranuras (de 4 inicial a 8 total)
- Es permanente: una vez usado, el aumento se mantiene en las partidas guardadas

---

## 2. Pool de 10 Nuevas Habilidades

### Archivo: `src/database/habilidades_db.json`

Se agregaron 10 nuevas habilidades para probar el sistema de ranuras:

1. **ID_GOLPE_FEROZ** - Habilidad Física (40 poder, 15 MP)
2. **ID_TERREMOTO** - Magia Negra AoE de Tierra (25 poder, 18 MP)
3. **ID_RAYO** - Magia Negra de Rayo (30 poder, 8 MP)
4. **ID_ESCUDO_MAGICO** - Magia Blanca (Buff Def. Mágica, 10 MP)
5. **ID_HIELO** - Magia Negra de Hielo (28 poder, 7 MP)
6. **ID_CURA_PLUS** - Magia Blanca (100 HP, 12 MP)
7. **ID_VIENTO** - Magia Negra de Viento (22 poder, 6 MP)
8. **ID_BERSERKER** - Habilidad Física (Buff ATK / Debuff DEF, 20 MP)
9. **ID_CURAGA** - Magia Blanca AoE (60 HP a todos, 25 MP)
10. **ID_METEORO** - Magia Negra AoE (35 poder a todos, 30 MP)

**Distribución por héroe:**

- **Héroe 1 (Guerrero)**: 7 habilidades físicas/defensivas
  - ID_CORTE_CRUZADO, ID_GUARDIA, ID_SANGRADO, ID_GOLPE_FEROZ, ID_TIRO_PENETRANTE, ID_RECUPERACION, ID_BERSERKER

- **Héroe 2 (Mago)**: 11 habilidades mágicas
  - ID_PIRO, ID_CURA, ID_PIRO_PLUS, ID_TERREMOTO, ID_RAYO, ID_HIELO, ID_VIENTO, ID_ESCUDO_MAGICO, ID_CURA_PLUS, ID_CURAGA, ID_METEORO

---

## 3. Inventario Inicial Actualizado

### Archivo: `src/database/heroes_db.json`

Ambos héroes ahora tienen:
- **2 Expansores de Ranuras** en su inventario inicial
- Pool completo de habilidades disponibles para equipar

**Resultado:** Al usar los 2 expansores, cada héroe tendrá 8 ranuras de habilidades (4 base + 4 extra).

---

## 4. Sistema de Scroll Horizontal en Ranuras

### Archivo: `src/pantalla_habilidades.py`

**Nuevas características:**

### 4.1. Variables de Scroll
```python
self.scroll_ranuras = 0  # Offset de scroll para ranuras activas
self.max_items_visibles_ranuras = 4  # Cuántas ranuras se ven a la vez
```

### 4.2. Navegación Mejorada
- **Flecha Izquierda (←)**: Mueve selección a ranura anterior
- **Flecha Derecha (→)**: Mueve selección a siguiente ranura
- **Scroll automático**: Cuando seleccionas una ranura fuera del área visible, el scroll se ajusta automáticamente

### 4.3. Indicadores Visuales
- **◀ (Izquierda)**: Aparece cuando hay ranuras ocultas a la izquierda
- **▶ (Derecha)**: Aparece cuando hay ranuras ocultas a la derecha

### 4.4. Lógica de Actualización de Listas
```python
def _actualizar_listas(self):
    # Ahora soporta cualquier número de ranuras dinámicamente
    for i in range(self.heroe.ranuras_habilidad_max):
        # Crea ranuras vacías o llenas según corresponda
```

### 4.5. Renderizado con Scroll
```python
def _draw_panel_ranuras(self, pantalla):
    # Calcula ranuras visibles según scroll
    inicio = self.scroll_ranuras
    fin = min(inicio + self.max_items_visibles_ranuras, num_ranuras)
    ranuras_visibles = self.lista_ranuras_activas[inicio:fin]
    # Solo dibuja las ranuras visibles
```

---

## 5. Tecla ESC para Regresar

### Archivo: `src/pantalla_habilidades.py`

**Flujo de navegación mejorado:**

```python
def update_input(self, tecla):
    if tecla == pygame.K_ESCAPE:
        if self.modo == "ver_detalles":
            self.modo = "seleccion_inventario"  # Cerrar detalles
            return None
        elif self.modo == "seleccion_ranura":
            self.modo = "seleccion_inventario"  # Volver a inventario
            return None
        elif self.modo == "seleccion_inventario":
            return "volver_al_menu"  # Cerrar pantalla completa
```

**Estados de ESC:**
1. Desde "ver_detalles" → Cierra el popup de detalles
2. Desde "seleccion_ranura" → Vuelve al modo de inventario
3. Desde "seleccion_inventario" → Cierra la pantalla y vuelve al menú pausa

### Archivo: `main.py`

Ya estaba conectado correctamente:
```python
elif estado_juego == "pantalla_habilidades" and mi_pantalla_habilidades:
    accion_habilidades = mi_pantalla_habilidades.update_input(event.key)
    if accion_habilidades == "volver_al_menu":
        estado_juego = "menu_pausa"
        mi_menu_pausa = MenuPausa(ANCHO, ALTO, CURSOR_IMG)
        mi_pantalla_habilidades = None
```

---

## 6. Controles Completos

### En Inventario de Habilidades:
- **↑ / ↓**: Navegar por habilidades
- **ENTER**: Seleccionar habilidad para equipar
- **D**: Ver detalles completos
- **ESC**: Salir a menú pausa

### En Ranuras Activas:
- **← / →**: Navegar entre ranuras (scroll automático)
- **↑**: Volver al inventario
- **ENTER**: Equipar habilidad seleccionada en la ranura actual
- **X**: Desequipar habilidad de la ranura actual
- **ESC**: Volver al inventario

### En Popup de Detalles:
- **D o ESC**: Cerrar detalles

---

## 7. Sistema de Guardado

Los nuevos campos se guardan automáticamente:
- `clase`: "Guerrero" o "Mago"
- `ranuras_habilidad_max`: Número dinámico de ranuras
- `habilidades_activas`: Array con IDs de habilidades equipadas
- `inventario_habilidades`: Array con IDs de todas las habilidades disponibles

---

## 8. Colores y Estilo

### Código de Colores:
- **Rojo Claro (255, 100, 100)**: Habilidades físicas
- **Azul Claro (100, 150, 255)**: Habilidades mágicas
- **Amarillo (255, 255, 0)**: Elemento seleccionado
- **Verde (0, 255, 0)**: Habilidad equipada
- **Gris (100, 100, 100)**: Ranura vacía

### Indicadores Visuales:
- **Bullet "•"**: Marca habilidades que están equipadas en el inventario
- **Borde Amarillo Grueso**: Panel actualmente seleccionado
- **Flechas de Scroll**: Indican dirección de navegación disponible

---

## 9. Próximos Pasos (Futuro)

### Lógica de Uso del Expansor:
- Implementar función `usar_expansor_ranuras(heroe)` en inventario
- Aumentar `heroe.ranuras_habilidad_max += 2`
- Actualizar UI para reflejar nuevas ranuras inmediatamente

### Efectos en Batalla:
- Integrar las nuevas habilidades en el sistema de combate
- Implementar los efectos especiales (ELEMENTO_FUEGO, BUFF_ATK, etc.)
- Agregar animaciones para cada tipo de habilidad

### Clases y Restricciones:
- Agregar campo `clase_requerida` a habilidades específicas
- Implementar sistema de aprendizaje de habilidades por nivel
- Crear árboles de habilidades por clase

---

## Archivos Modificados

1. **src/database/items_db.json** - Nuevo ítem "EXPANSOR_RANURAS"
2. **src/database/habilidades_db.json** - 10 nuevas habilidades
3. **src/database/heroes_db.json** - Inventarios actualizados con expansores y habilidades
4. **src/pantalla_habilidades.py** - Sistema de scroll horizontal y ESC
5. **main.py** - Ya tenía la conexión ESC correcta

---

## Pruebas Realizadas

✅ Navegación con flechas en inventario
✅ Navegación horizontal (← →) en ranuras
✅ Scroll automático cuando hay más de 4 ranuras
✅ Indicadores visuales de scroll (◀ ▶)
✅ Tecla ESC funciona en todos los modos
✅ Guardado y carga de nuevos campos
✅ Colores diferenciados por tipo de habilidad

---

## Notas Técnicas

### Rendimiento:
- El scroll horizontal se calcula dinámicamente basado en `ranuras_habilidad_max`
- Solo se renderizan las ranuras visibles (máximo 4 a la vez)
- El sistema soporta cualquier número de ranuras sin límite hardcodeado

### Compatibilidad:
- Los archivos de guardado antiguos se cargarán correctamente (valores por defecto)
- El sistema es retrocompatible con héroes que tengan solo 4 ranuras

---

**Fin del Documento**
