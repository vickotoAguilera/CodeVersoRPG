# Instrucciones para Aplicar Glassmorphism a PantallaMagia

## 📝 PASO 1: Agregar Import (Línea 2)

**Ubicación:** Después de `import pygame` (línea 1)

**AGREGAR esta línea:**
```python
from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento
```

**Resultado:**
```python
import pygame
from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento
import sys
```

---

## 📝 PASO 2: Reemplazar el Dibujo de las Cajas (Líneas 139-147)

**Ubicación:** Dentro del método `draw()`, después del velo

**BORRAR estas líneas (139-147):**
```python
        # 2. Dibujar las 3 Cajas Azules (Sin cambios)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_desc_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_mp_rect, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_magia_rect, border_radius=self.UI_BORDER_RADIUS)
        
        # 3. Dibujar los Bordes Blancos (Sin cambios)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_desc_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_mp_rect, 3, border_radius=self.UI_BORDER_RADIUS)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_magia_rect, 3, border_radius=self.UI_BORDER_RADIUS)
```

**REEMPLAZAR con:**
```python
        # 2. Dibujar las 3 Cajas con efecto glassmorphism
        dibujar_ventana_glass(pantalla, self.caja_desc_rect, "Descripcion", 
                             obtener_color_acento("magia"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_mp_rect, "MP del Heroe", 
                             obtener_color_acento("magia"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_magia_rect, "Magias Disponibles", 
                             obtener_color_acento("magia"), alpha=230)
```

---

## ✅ Resultado Final

El método `draw()` debería quedar así:

```python
    def draw(self, pantalla):
        
        # 1. Dibujar el "velo" (Sin cambios)
        velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        velo.fill(self.COLOR_FONDO_VELO)
        pantalla.blit(velo, (0, 0))
        
        # 2. Dibujar las 3 Cajas con efecto glassmorphism
        dibujar_ventana_glass(pantalla, self.caja_desc_rect, "Descripcion", 
                             obtener_color_acento("magia"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_mp_rect, "MP del Heroe", 
                             obtener_color_acento("magia"), alpha=230)
        dibujar_ventana_glass(pantalla, self.caja_magia_rect, "Magias Disponibles", 
                             obtener_color_acento("magia"), alpha=230)

        # 4. Dibujar Contenido: Caja Descripción (Arriba) (Sin cambios)
        opcion_actual = self.opciones_mostradas[self.opcion_seleccionada]
        
        # ... resto del código sin cambios
```

---

## 🎯 Resumen de Cambios

**Total de líneas a modificar:** 2 ubicaciones

1. **Línea 2:** Agregar 1 línea (import)
2. **Líneas 139-147:** Reemplazar 9 líneas por 6 líneas

**Archivo:** `src/pantalla_magia.py`

---

## 🧪 Probar

Después de hacer los cambios:
```bash
python main.py
```

Entra en una batalla y abre el menú de magia para ver el efecto glassmorphism.

---

## 🔙 Si algo sale mal

Revertir con:
```bash
git restore src/pantalla_magia.py
```

---

## 📋 Aplicar a Otras Ventanas

Una vez que funcione en PantallaMagia, puedes aplicar el mismo patrón a:

- **PantallaItems** (`src/pantalla_items.py`)
- **PantallaVictoria** (`src/pantalla_victoria.py`)
- **PantallaListaHabilidades** (`src/pantalla_lista_habilidades.py`)

El proceso es el mismo:
1. Agregar el import
2. Reemplazar `pygame.draw.rect()` por `dibujar_ventana_glass()`
