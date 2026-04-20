# Sistema de Items Especiales

## Descripción General
Los items especiales son objetos únicos que proporcionan efectos globales permanentes al inventario. Estos items NO son consumibles ni equipables, y su efecto se aplica automáticamente a todos los héroes.

## Características de los Items Especiales

### 1. No Consumibles
- Los items especiales permanecen SIEMPRE en el inventario
- No desaparecen al usarse
- No se pueden dar/transferir a héroes individuales

### 2. Efecto Global Automático
- El sistema verifica automáticamente la existencia de estos items
- Los efectos se aplican a TODOS los héroes simultáneamente
- No requiere selección manual de héroe

### 3. Acumulación de Efectos
- Si tienes múltiples items del mismo tipo (ej: Expansor de Ranuras x2)
- El efecto se MULTIPLICA por la cantidad
- Ejemplo: 
  - Item: "Expansor de Ranuras" (+2 ranuras)
  - Cantidad: x2
  - Efecto total: 2 ranuras × 2 items = 4 ranuras adicionales para TODOS los héroes

## Tipos de Items Especiales

### A. Expansores de Ranuras
- **Función**: Aumentan el espacio de inventario
- **Efecto**: Se aplica automáticamente a todos los héroes
- **Cálculo**: efecto_base × cantidad_items = ranuras_totales_añadidas

### B. Llaves Especiales
- **Función**: Permiten abrir cofres específicos
- **Efecto**: El sistema verifica el ID de la llave al interactuar con cofres
- **Tipos**: Llave de Plata, Llave de Oro, Llave de Diamante, etc.

### C. Objetos de Acceso
- **Función**: Permiten acceder a áreas o eventos especiales
- **Efecto**: Desbloquean opciones en el mapa o diálogos

## Comportamiento en el Inventario

### Visualización
- Categoría: "Especiales"
- Muestra cantidad si hay múltiples del mismo tipo (ej: x2, x3)
- El cursor puede navegar sobre ellos para ver información
- Muestra descripción y efecto al seleccionarlos

### Interacción
- **Enter**: NO hace nada (no son seleccionables para uso)
- **D**: Muestra detalles del item (descripción y efecto)
- Los efectos numéricos se muestran automáticamente en la descripción

## Sistema de Verificación

### Para Expansores de Ranuras
```python
# El sistema ejecuta automáticamente:
1. Detectar items en categoría "especiales"
2. Contar cantidad de cada item único
3. Calcular efecto total: efecto_base × cantidad
4. Aplicar a todos los héroes
5. Actualizar interfaz de inventario
```

### Para Llaves
```python
# Al interactuar con un cofre:
1. Sistema verifica tipo de cofre (ID)
2. Busca en items especiales si existe llave correspondiente
3. Si existe: Abre el cofre
4. Si no existe: Muestra mensaje "Necesitas: [Nombre de Llave]"
```

## Implementación Técnica

### Estructura de Item Especial
```python
{
    "id": "exp_ranuras_1",
    "nombre": "Expansor de Ranuras",
    "tipo": "especial",
    "efecto": "aumentar_ranuras",
    "valor": 2,  # Número de ranuras que añade
    "descripcion": "Aumenta permanentemente las ranuras de inventario de todos los héroes"
}
```

### Verificación Automática
El sistema debe ejecutar la verificación:
- Al cargar una partida guardada
- Al obtener un nuevo item especial
- Al entrar al menú de inventario

## Ventajas del Sistema

1. **Simplicidad**: El jugador no necesita administrar manualmente estos efectos
2. **Equidad**: Todos los héroes reciben los beneficios
3. **Claridad**: Es fácil ver qué mejoras globales tiene el jugador
4. **Escalabilidad**: Fácil añadir nuevos tipos de items especiales

## Notas Importantes

- Los items especiales NUNCA deben poder darse a un héroe específico
- Los efectos son permanentes mientras el item esté en el inventario
- No ocupan espacio en el inventario normal de los héroes
- Son ideales para mecánicas de progresión y desbloqueo de contenido
