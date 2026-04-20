# Resumen del plan de prefabs y siguiente etapa

## Estado de etapa

- Etapa actual: **CERRADA (completada en esta sesion)**.
- Resultado: el flujo base de prefabs ya quedo operativo (armado, importacion, edicion y guardado).
- Traspaso de contexto: la siguiente etapa queda documentada en [docs/PLAN_SIGUIENTE_SESION_PORTALES_INTERACCION.md](PLAN_SIGUIENTE_SESION_PORTALES_INTERACCION.md).

## Lo que hicimos hasta ahora

- Organizamos la documentación antigua dentro de [docs/archivo/](archivo/).
- Dejamos un archivo principal de organización en [docs/ORGANIZACION_DOCUMENTACION.md](ORGANIZACION_DOCUMENTACION.md).
- Dejamos [visualizador_recursos.py](../visualizador_recursos.py) como herramienta aparte, sin centrar ahí el trabajo actual.
- Empezamos a construir [constructor_prefabs.py](../constructor_prefabs.py) como base del nuevo sistema de prefabs.
- Definimos que el flujo nuevo debe guardar prefabs en `.png` + `.json`.
- Agregamos multi-seleccion con Ctrl+Click izquierdo y botones de Pegar/Despegar seleccion para unir o separar piezas elegidas.
- Mantenemos tambien el flujo de copiar/pegar bloque (Ctrl+C / Ctrl+V) para acelerar la construccion en el lienzo.
- Agregamos profundidad por capas con Shift: la seleccion alterna entre fondo/frente y se marca con borde celeste (fondo) o amarillo (frente).
- Agregamos redimensionado de sprites en lienzo con rueda y tiradores visuales (lados/esquinas) para alargar o contraer piezas.
- Cuando hay varias piezas seleccionadas, ahora comparten una sola caja con tiradores para redimensionar el bloque completo.
- Agregamos carga real de prefabs desde JSON para continuar una sesion guardada.
- La carga ahora importa el prefab sobre la escena actual y selecciona todo el bloque para moverlo, borrarlo o reguardarlo con otro nombre.
- Agregamos limites de scroll en paneles para que no se pase del contenido.
- Agregamos redimensionado proporcional con Alt al usar tiradores de esquina.
- Agregamos logica editable por pieza para colision y sobreposicion desde el prefab.
- Atajos actuales: `B` alterna colision, `Tab` alterna pasar por detras (sobrepuesto).
- Confirmamos que la lógica del editor unificado puede servir como referencia para validación, colocación y manejo de elementos.

## Qué queremos hacer después

- Crear un nuevo editor visual para construir prefabs o estructuras compuestas.
- Seguir puliendo [constructor_prefabs.py](../constructor_prefabs.py) para flujo completo y mas estable en sesiones largas.
- Permitir montar casas, castillos, estatuas y otras estructuras a partir de piezas o tiles.
- Guardar cada prefab como:
  - una imagen previa (`.png`),
  - un archivo de datos (`.json`) con posiciones, tamaño, rotación, espejo y colisiones.
- Permitir luego colocar esos prefabs en un mapa como si fueran objetos prearmados.
- Soportar redimensionado, espejo y rotación.
- Mantener y pulir el sistema dual: pegar/despegar seleccion + copiar/pegar bloque para construccion rapida.
- Mantener colisión o bloqueo por celdas para que el personaje no atraviese las partes ocupadas.
- Pulir la experiencia de cajas redimensionables (tiradores, limites y colision) para igualar el nivel de visualizador_recursos.

## Estructura propuesta del nuevo archivo `.py`

Nombre sugerido:

- `constructor_prefabs.py`

Bloques principales:

1. Configuración general
   - tamaño de ventana
   - colores
   - rutas base
   - carpeta de salida

2. Carga de recursos
   - cargar tiles o sprites base
   - cargar prefabs existentes
   - cargar mapa de fondo opcional

3. Modelo de datos
   - clase `Prefab`
   - clase `TilePrefab`
   - clase `CeldaBloqueada` o similar

4. Editor principal
   - seleccionar pieza
   - mover
   - rotar
   - espejo horizontal / vertical
   - escalar
   - borrar
   - deshacer / rehacer

5. Vista previa
   - render del prefab completo
   - overlay de grilla
   - indicadores de colisión

6. Guardado
   - exportar PNG
   - exportar JSON
   - guardar en carpeta destino elegida dentro de `assets`

7. Carga para reutilización
   - volver a abrir el prefab
   - editarlo de nuevo
   - colocarlo en otros mapas

## Estructura propuesta del nuevo `.bat`

Nombre sugerido:

- `ejecutar_constructor_prefabs.bat`

Contenido lógico:

1. Limpiar pantalla y mostrar título.
2. Ir a la carpeta del script.
3. Verificar dependencias.
4. Ejecutar el Python principal.
5. Mostrar error si algo falla.

Flujo esperado:

- `cd /d "%~dp0"`
- verificar `pygame`
- ejecutar `python constructor_prefabs.py`
- pausar si hay error

## Próximos pasos técnicos

1. Definir el formato exacto del JSON del prefab.
2. Crear el nuevo `.py` del constructor.
3. Crear su `.bat` de ejecución.
4. Conectar el nuevo prefab con el editor de mapas.
5. Añadir soporte visual para rotación, espejo y colisión.
6. Completar flujo de pegar/despegar y copiar/pegar con carga/guardado para reconstruir bloques en nuevas sesiones.
7. Pulir edicion de cajas con tiradores (lados/esquinas), incluyendo limites min/max y ajuste fino de colision.

## Regla general

- El prefabricador debe guardar la estructura editable.
- El mapa final debe poder usar ese prefab como un objeto prearmado.
- La lógica de bloqueo debe funcionar por casillas, no solo por imagen.
