# Instrucciones Manuales para PantallaMagia - Glassmorphism

## 🎯 Objetivo
Aplicar efecto glassmorphism a `PantallaMagia` y ajustar la posición del contenido para que no se solape con los títulos.

---

## 📝 PASO 1: Agregar Import (Línea 2)

**Archivo:** `src/pantalla_magia.py`

**Ubicación:** Después de `import pygame` (línea 1), antes de `import sys` (línea 2)

**AGREGAR esta línea:**
```python
from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento
```

**Resultado esperado (líneas 1-3):**
```python
import pygame
from src.ui_glassmorphism import dibujar_ventana_glass, obtener_color_acento
import sys
```

---

## 📝 PASO 2: Reemplazar Dibujo de Cajas (Líneas 139-147)

**Ubicación:** Dentro del método `draw()`, después del velo

**BUSCAR estas 9 líneas (139-147):**
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

**REEMPLAZAR con estas 6 líneas:**
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

## 📝 PASO 3: Ajustar Posición Y de Magias (Línea 170)

**Ubicación:** Dentro del método `draw()`, sección de lista de magias

**BUSCAR esta línea (170):**
```python
        start_y_opciones = self.caja_magia_rect.y + 25
```

**REEMPLAZAR con:**
```python
        start_y_opciones = self.caja_magia_rect.y + 60  # Ajustado para glassmorphism
```

---

## ✅ Verificación

Después de hacer los cambios, el archivo debería:

1. **Línea 2:** Tener el import de glassmorphism
2. **Líneas 139-145:** Tener 3 llamadas a `dibujar_ventana_glass()` en lugar de 9 `pygame.draw.rect()`
3. **Línea 170:** Tener `+ 60` en lugar de `+ 25`

---

## 🧪 Probar

```bash
python main.py
```

Entra en batalla y abre el menú de magia. Deberías ver:
- ✨ Efecto de vidrio púrpura transparente
- 📝 Títulos en las barras superiores de cada caja
- 🎯 Las magias no se solapan con el título "Magias Disponibles"

---

## 🔙 Si algo sale mal

Revertir con:
```bash
git restore src/pantalla_magia.py
```

Y volver a intentar siguiendo los pasos cuidadosamente.

---

## 📊 Resumen de Cambios

| Ubicación | Cambio | Líneas |
|-----------|--------|--------|
| Línea 2 | Agregar import | +1 línea |
| Líneas 139-147 | Glassmorphism | -9 líneas, +6 líneas |
| Línea 170 | Ajustar posición Y | Cambiar valor |

**Total:** 3 ubicaciones para modificar
