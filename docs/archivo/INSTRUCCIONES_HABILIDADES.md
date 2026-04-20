# Instrucciones para Aplicar Glassmorphism a PantallaListaHabilidades

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

## 📝 PASO 2: Reemplazar el Dibujo de la Caja Principal (Líneas 224-227)

**Ubicación:** Dentro del método `draw()`, después del velo

**BUSCAR estas líneas (aproximadamente líneas 224-227):**
```python
    pygame.draw.rect(pantalla, self.COLOR_CAJA, self.caja_principal_rect, border_radius=self.UI_BORDER_RADIUS)
    pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_principal_rect, 3, border_radius=self.UI_BORDER_RADIUS)
    
    pygame.draw.rect(pantalla, self.COLOR_BORDE, self.panel_habilidades_rect, 1, border_radius=self.UI_BORDER_RADIUS)
    pygame.draw.rect(pantalla, self.COLOR_BORDE, self.caja_titulo_rect, 1, border_radius=self.UI_BORDER_RADIUS)
```

**REEMPLAZAR con:**
```python
    # Dibujar caja principal con efecto glassmorphism
    dibujar_ventana_glass(pantalla, self.caja_principal_rect, "Habilidades", 
                         obtener_color_acento("habilidades"), alpha=230)
    
    # Bordes internos (más sutiles)
    pygame.draw.rect(pantalla, (100, 100, 150), self.panel_habilidades_rect, 1, border_radius=self.UI_BORDER_RADIUS)
    pygame.draw.rect(pantalla, (100, 100, 150), self.caja_titulo_rect, 1, border_radius=self.UI_BORDER_RADIUS)
```

---

## ✅ Resultado Final

El inicio del método `draw()` debería quedar así:

```python
def draw(self, pantalla):
    
    # 1. Dibujar el "velo" y la Caja Principal
    velo = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
    velo.fill(self.COLOR_FONDO_VELO)
    pantalla.blit(velo, (0, 0))
    
    # Dibujar caja principal con efecto glassmorphism
    dibujar_ventana_glass(pantalla, self.caja_principal_rect, "Habilidades", 
                         obtener_color_acento("habilidades"), alpha=230)
    
    # Bordes internos (más sutiles)
    pygame.draw.rect(pantalla, (100, 100, 150), self.panel_habilidades_rect, 1, border_radius=self.UI_BORDER_RADIUS)
    pygame.draw.rect(pantalla, (100, 100, 150), self.caja_titulo_rect, 1, border_radius=self.UI_BORDER_RADIUS)

    # 2. Dibujar Título con nombre del héroe
    titulo_texto = f"Habilidades - {self.heroe.nombre_en_juego}"
    # ... resto del código sin cambios
```

---

## 🎯 Resumen de Cambios

**Total de líneas a modificar:** 2 ubicaciones

1. **Línea 2:** Agregar 1 línea (import)
2. **Líneas 224-227:** Reemplazar 5 líneas por 6 líneas

**Archivo:** `src/pantalla_lista_habilidades.py`

---

## 🧪 Probar

Después de hacer los cambios:
```bash
python main.py
```

Entra en una batalla y abre el menú de habilidades para ver el efecto glassmorphism.

---

## 🔙 Si algo sale mal

Revertir con:
```bash
git restore src/pantalla_lista_habilidades.py
```

---

## 🎨 Color de Acento

La ventana de habilidades usa el color **azul** (`obtener_color_acento("habilidades")`).

Si quieres cambiar el color, puedes usar:
- `"magia"` → Púrpura
- `"items"` → Verde
- `"victoria"` → Dorado
- `"habilidades"` → Azul (actual)
