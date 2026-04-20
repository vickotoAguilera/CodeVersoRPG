# Lógica del Editor de Muros

## 1. Lógica Poligonal

- **Modo polígono**: Al presionar `L`, el editor entra en modo poligonal.
- **Creación de vértices**: Cada click izquierdo agrega un punto (vértice) al polígono en construcción.
- **Visualización**: Se dibujan líneas entre los puntos y una línea de cierre (preview) entre el último y el primero si hay 3+ puntos. Cada vértice muestra su número.
- **Deshacer vértice**: Click derecho elimina el último punto agregado.
- **Finalizar polígono**: Enter crea el muro poligonal si hay al menos 3 puntos. ESC cancela el polígono.
- **Selección y arrastre**: Los muros poligonales se seleccionan igual que los rectangulares. Al arrastrar, se mueve todo el polígono usando el primer punto como referencia.
- **Colisión**: Para selección/borrado, se usa el algoritmo ray-casting para detectar si el mouse está dentro del polígono.
- **Serialización**: Los muros poligonales se guardan en JSON como `{ "tipo": "poly", "puntos": [[x1, y1], [x2, y2], ...] }`.

## 2. Lógica de Ventanas y Paneles

- **Panel lateral**: Muestra las categorías de mapas (carpetas principales). Cada sección es expandible/colapsable.
- **Scroll vertical**: Si hay muchos mapas, el panel permite desplazarse para ver todos los elementos.
- **Selección de mapa**: Al hacer click en un mapa del panel, se carga la imagen y los muros asociados.
- **Ventana de ayuda**: Botón `[?]` o tecla `H` abre una ventana modal con todos los atajos y funciones. Se puede cerrar con `ESC` o `H`.

## 3. Lógica de Scroll y Zoom

- **Zoom**: Se controla con la rueda del ratón. El zoom mínimo es 0.25x y el máximo 1.0x (escala real del juego). Tecla `0` resetea el zoom.
- **Scroll/Pan**: Se puede arrastrar el área del mapa con el botón derecho o el botón central del mouse. El desplazamiento se ajusta con `offset_x` y `offset_y`.
- **Ajuste de escala**: Al cargar un mapa, se calcula la escala para que quepa en el área visible sin agrandar la imagen.

## 4. Lógica de Multi-selección y Edición

- **Multi-selección**: Shift+Click permite seleccionar varios muros (rectangulares o poligonales).
- **Arrastre de grupo**: Al arrastrar, todos los muros seleccionados se mueven juntos, calculando el offset para cada uno.
- **Redimensionar**: Solo los muros rectangulares muestran handles en las esquinas para redimensionar.
- **Fusión**: Tecla `F` fusiona solo muros rectangulares en un bounding box.

## 5. Guardado y Exportación

- **Auto-guardado**: El editor guarda automáticamente los cambios cada cierto tiempo si hay modificaciones pendientes.
- **Guardar manual**: Tecla `G` guarda los muros en el archivo JSON correspondiente.
- **Exportar CSV**: Tecla `C` exporta los muros (rectangulares y poligonales) a un archivo CSV.

---

**Resumen:**
El editor permite crear, editar y gestionar muros de colisión de cualquier forma, con una interfaz flexible y controles intuitivos. La lógica poligonal es completamente adaptable y se integra con el resto de las funciones del editor.
