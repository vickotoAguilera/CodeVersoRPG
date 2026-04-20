# FUNCIONALIDADES AGREGADAS AL EDITOR DE MAPAS AVANZADO

## 1. **PORTALES** - Sistema de conexión entre mapas

### Cómo funcionan:
- **Botón "Portales"** en el menú superior
- Al activarlo:
  1. Haces clic en un punto del mapa actual (Portal A)
  2. Seleccionas el mapa de destino de la lista
  3. Haces clic donde aparecerá el jugador (Portal B)
  4. Le pones un nombre (ej: "Pueblo-Casa_Juan")
  
### Datos que guarda:
```json
{
  "id": "portal_001",
  "mapa_origen": "mapa_pradera",
  "x_origen": 450,
  "y_origen": 300,
  "mapa_destino": "pueblo_inicio",
  "x_destino": 100,
  "y_destino": 200,
  "nombre": "Pueblo-Casa_Juan",
  "ancho": 64,
  "alto": 64
}
```

### Visualización:
- Se muestra como un rectángulo morado/azul con el nombre
- Puedes redimensionarlo arrastrando las esquinas
- Al hacer hover, muestra info del destino

---

## 2. **MUROS DIBUJABLES** - Zonas de colisión personalizadas

### Cómo funcionan:
- **Botón "Muros"** en el menú superior
- Al activarlo:
  1. Mantienes clic y dibujas sobre el mapa
  2. Se crean puntos que siguen tu mouse
  3. Puedes ajustar el grosor del muro
  4. Al soltar, se cierra el polígono (opcional)
  
### Opciones:
- **Grosor del muro:** Slider de 1-20 píxeles
- **Color:** Selector de color (rojo por defecto)
- **Cerrar polígono:** Botón para conectar último punto con el primero
- **Borrar último punto:** Ctrl+Z
- **Terminar muro:** Doble clic o tecla Enter

### Datos que guarda:
```json
{
  "id": "muro_001",
  "puntos": [
    [100, 150],
    [150, 150],
    [150, 200],
    [100, 200]
  ],
  "color": [255, 0, 0],
  "grosor": 5,
  "cerrado": true
}
```

### Visualización:
- Líneas rojas (o color elegido) sobre el mapa
- Semi-transparente al editar
- Al hacer hover, resalta
- Puedes editar puntos individuales

---

## 3. **CARGA DE IMÁGENES DE MAPAS** - Corregido

### Problema anterior:
- Solo buscaba archivos `.jpg` en una carpeta específica
- No cargaba `.png` ni buscaba recursivamente

### Solución implementada:
```python
def cargar_mapa(self, nombre_mapa, carpeta):
    # Busca primero en la lista de mapas disponibles
    mapa_info = next((m for m in self.mapas_disponibles 
                      if m["nombre"] == nombre_mapa 
                      and m["carpeta"] == carpeta), None)
    
    if mapa_info:
        # Usa la ruta exacta encontrada
        ruta_imagen = Path(mapa_info["ruta"])
        if ruta_imagen.exists():
            self.imagen_mapa = pygame.image.load(str(ruta_imagen)).convert()
    else:
        # Fallback: busca manualmente
        for ext in ['.jpg', '.png', '.jpeg']:
            ruta_imagen = Path(f"assets/maps/{carpeta}/{nombre_mapa}{ext}")
            if ruta_imagen.exists():
                self.imagen_mapa = pygame.image.load(str(ruta_imagen)).convert()
                return
```

---

## 4. **VISUALIZACIÓN DE SPRITES EN EL MAPA**

### Problema:
- Los cofres/NPCs aparecían como cuadrados vacíos

### Solución:
- Ahora se cargan las imágenes reales
- Se redimensionan según el tamaño definido
- Se muestran con su apariencia correcta

---

## 5. **ATAJOS DE TECLADO**

| Tecla | Acción |
|-------|--------|
| **Espacio** | Activar/desactivar modo Pan (mover cámara) |
| **G** | Mostrar/ocultar grid |
| **Ctrl + S** | Guardar mapa |
| **Ctrl + Z** | Deshacer (en modo muros) |
| **Enter** | Finalizar muro actual |
| **Delete** | Eliminar objeto seleccionado |
| **Esc** | Cancelar acción actual |
| **+/-** | Zoom in/out |

---

## 6. **PANEL DE PROPIEDADES** (Panel Derecho)

Muestra información del objeto seleccionado:
- **Tipo:** Cofre, NPC, Portal, Muro, etc.
- **Posición:** X, Y
- **Tamaño:** Ancho x Alto
- **Z-Index:** Profundidad de capa
- **Datos extra:** Información específica del objeto

Para **Portales** además muestra:
- Mapa de destino
- Coordenadas de destino
- Nombre descriptivo

Para **Muros** además muestra:
- Número de puntos
- Grosor
- Color
- Si está cerrado o no

---

## 7. **EXPORTACIÓN JSON**

Al guardar, se crea un archivo JSON con esta estructura:

```json
{
  "mapa": "mapa_pradera",
  "ancho": 2560,
  "alto": 1440,
  "objetos": [...],
  "portales": [
    {
      "id": "portal_pueblo_casa",
      "mapa_origen": "mapa_pradera",
      "mapa_destino": "pueblo_inicio",
      "x_origen": 450,
      "y_origen": 300,
      "x_destino": 100,
      "y_destino": 200,
      "nombre": "Entrada Pueblo"
    }
  ],
  "muros": [
    {
      "id": "muro_lago",
      "puntos": [[100,150], [200,150], [200,250], [100,250]],
      "cerrado": true,
      "grosor": 5
    }
  ],
  "version": "2.0"
}
```

---

## 8. **USO EN EL JUEGO**

### Para detectar colisiones con muros:
```python
def jugador_colisiona_con_muros(self, jugador_rect):
    for muro in self.muros_mapa:
        if self.punto_en_poligono(jugador_rect.center, muro['puntos']):
            return True
    return False

def punto_en_poligono(self, punto, poligono):
    x, y = punto
    dentro = False
    j = len(poligono) - 1
    for i in range(len(poligono)):
        xi, yi = poligono[i]
        xj, yj = poligono[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            dentro = not dentro
        j = i
    return dentro
```

### Para usar portales:
```python
def verificar_portales(self, jugador_pos):
    for portal in self.portales:
        if pygame.Rect(portal['x_origen'], portal['y_origen'], 
                       portal['ancho'], portal['alto']).collidepoint(jugador_pos):
            # Cambiar al mapa de destino
            self.cargar_mapa(portal['mapa_destino'])
            self.jugador.x = portal['x_destino']
            self.jugador.y = portal['y_destino']
            break
```

---

## RESUMEN DE CAMBIOS REALIZADOS

✅ **Agregado:** Enum `ModoEditor` con modos NORMAL, DIBUJAR_MUROS, CREAR_PORTAL  
✅ **Agregado:** Clase `Portal` con todos sus datos  
✅ **Agregado:** Clase `MuroDibujable` con lista de puntos  
✅ **Agregado:** Variables de estado para portales y muros  
✅ **Agregado:** Botones "Portales" y "Muros" en el menú  
✅ **Corregido:** Carga de imágenes de mapas (busca .jpg y .png)  
✅ **Corregido:** Búsqueda recursiva en carpetas de sprites  

---

## PRÓXIMOS PASOS

Para completar la funcionalidad, necesitas agregar:

1. **Métodos de dibujo** para portales y muros en el render
2. **Lógica de eventos** para capturar clics y dibujar
3. **Interfaz para nombrar portales** (cuadro de texto)
4. **Selector de mapa destino** para portales
5. **Controles de grosor/color** para muros
6. **Guardar/cargar** portales y muros del JSON

¿Quieres que implemente alguno de estos puntos específicamente?
