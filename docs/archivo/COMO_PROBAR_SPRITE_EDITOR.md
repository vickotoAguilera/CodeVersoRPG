# ✅ CÓMO PROBAR EL SPRITE EDITOR ACTUALIZADO

## 🚀 Inicio Rápido

```bash
python sprite_sheet_editor.py
```

---

## 📋 CHECKLIST DE PRUEBAS

### ✓ Test 1: Cargar Spritesheet
- [ ] Arrastra una imagen PNG desde tu explorador a la ventana
- [ ] Verifica que se carga y se muestra en pantalla
- [ ] **Resultado esperado:** Imagen visible en panel central

---

### ✓ Test 2: Pan de Cámara (NUEVO)
- [ ] Mantén presionado el **botón derecho** del mouse
- [ ] Arrastra en cualquier dirección
- [ ] Suelta el botón
- [ ] **Resultado esperado:** La vista se mueve suavemente

---

### ✓ Test 3: Zoom
- [ ] Mueve el cursor sobre la imagen
- [ ] Gira la **rueda del mouse hacia arriba** (zoom in)
- [ ] Gira la **rueda del mouse hacia abajo** (zoom out)
- [ ] **Resultado esperado:** Zoom centrado en el cursor

---

### ✓ Test 4: Seleccionar Sprites
- [ ] Haz **click izquierdo** en un punto de la imagen
- [ ] Arrastra para crear un rectángulo
- [ ] Suelta
- [ ] Repite para seleccionar 3-4 sprites
- [ ] **Resultado esperado:** Rectángulos verdes/amarillos marcan las áreas

---

### ✓ Test 5: Checkboxes (NUEVO)
- [ ] Mira el **panel izquierdo** donde dice "Selecciones:"
- [ ] Verás cajitas □ al lado de cada sprite
- [ ] Haz **click en un checkbox**
- [ ] Observa que se marca/desmarca ☑/☐
- [ ] **Resultado esperado:** Checkbox cambia de estado

---

### ✓ Test 6: Nombrar Sprites
- [ ] Selecciona un sprite (click en él)
- [ ] Escribe un nombre en el input del panel derecho
- [ ] Ejemplo: "heroe_walk"
- [ ] Presiona Enter o haz click fuera
- [ ] **Resultado esperado:** Nombre aparece en el sprite

---

### ✓ Test 7: Numeración Automática (NUEVO)
- [ ] Selecciona 3 sprites diferentes
- [ ] Asigna el **mismo nombre** a los 3 (ej: "heroe_walk")
- [ ] Marca los 3 con checkboxes ☑
- [ ] Click en botón **"Exportar Todos (E)"**
- [ ] Ve a la carpeta `assets/sprites/heroes/batalla/`
- [ ] **Resultado esperado:** 
  - heroe_walk_1.png
  - heroe_walk_2.png
  - heroe_walk_3.png

---

### ✓ Test 8: Preview de Animación (NUEVO)
- [ ] Marca varios sprites con checkboxes (3-5 sprites)
- [ ] Click en botón **"Preview Animación"**
- [ ] Observa el panel izquierdo, abajo
- [ ] Verás una ventana con animación cíclica
- [ ] Muestra "Frame X/Y"
- [ ] **Resultado esperado:** Sprites se animan en secuencia

---

### ✓ Test 9: Desmarcar Checkbox
- [ ] En el panel izquierdo, click en un checkbox marcado ☑
- [ ] Debe cambiar a desmarcado ☐
- [ ] Click en "Exportar Todos"
- [ ] **Resultado esperado:** Solo exporta los marcados ☑

---

### ✓ Test 10: Guardar Sprite Individual
- [ ] Selecciona 1 sprite
- [ ] Nómbralo "test_sprite"
- [ ] Presiona **S** (o click "Guardar Sprite")
- [ ] Ve a la carpeta de categoría correspondiente
- [ ] **Resultado esperado:** test_sprite.png guardado

---

## 🎯 TEST COMPLETO DE FLUJO

### Escenario: Crear animación completa de caminar

#### Paso 1: Preparación
```
1. Abre el editor
2. Arrastra un spritesheet con sprites de caminar
3. Usa zoom para ver detalles
4. Usa pan (botón derecho) para navegar
```

#### Paso 2: Selección
```
5. Selecciona el primer frame de caminar
6. Selecciona el segundo frame
7. Selecciona el tercer frame
8. Selecciona el cuarto frame
```

#### Paso 3: Nombrar
```
9. Click en primer sprite
10. Escribe "heroe_walk" en el input
11. Click en segundo sprite
12. Escribe "heroe_walk" (mismo nombre)
13. Repite para el tercero y cuarto
```

#### Paso 4: Marcar
```
14. Verifica que los 4 sprites tengan checkbox marcado ☑
15. Si alguno está desmarcado, márcalo
```

#### Paso 5: Preview
```
16. Click en "Preview Animación"
17. Observa la animación en panel izquierdo
18. ¿Se ve bien? → Continúa
19. ¿Se ve mal? → Desmarca los malos, ajusta
```

#### Paso 6: Exportar
```
20. Click en "Exportar Todos (E)"
21. Ve a assets/sprites/heroes/batalla/
22. Verifica que existen:
    - heroe_walk_1.png
    - heroe_walk_2.png
    - heroe_walk_3.png
    - heroe_walk_4.png
```

#### Resultado Esperado:
✅ 4 archivos PNG numerados correctamente
✅ Cada uno contiene el frame correcto
✅ Están en la carpeta correcta

---

## 🐛 TROUBLESHOOTING

### Problema: No puedo hacer pan
**Solución:** Asegúrate de usar el **botón derecho**, no el izquierdo

### Problema: Los checkboxes no se ven
**Solución:** Primero debes seleccionar áreas. Los checkboxes aparecen en "Selecciones:"

### Problema: El preview no muestra nada
**Solución:** Marca al menos 1 sprite con checkbox antes de activar preview

### Problema: No se numera automáticamente
**Solución:** Verifica que:
- Múltiples sprites tengan el **mismo nombre exacto**
- Todos estén marcados con checkbox ☑
- Uses "Exportar Todos", no "Guardar Sprite"

### Problema: El zoom no funciona
**Solución:** Asegúrate de que el cursor esté sobre el panel central (área del spritesheet)

---

## 📊 VERIFICACIÓN FINAL

### Antes de reportar que todo funciona, verifica:
- [ ] Pan de cámara funciona con botón derecho
- [ ] Zoom funciona con rueda del mouse
- [ ] Checkboxes se pueden marcar/desmarcar
- [ ] Preview de animación se activa y muestra frames
- [ ] Exportar crea archivos numerados correctamente
- [ ] La barra de estado muestra "Marcados: X"
- [ ] Puedes seleccionar/deseleccionar sprites individuales

---

## ✨ CARACTERÍSTICAS EXTRA PARA PROBAR

### Grid de Referencia:
- Presiona **G** para mostrar/ocultar grid

### Deshacer/Rehacer:
- **Ctrl+Z** para deshacer
- **Ctrl+Y** para rehacer

### Eliminar Selección:
- Selecciona un sprite
- Presiona **DEL**

### Categorías:
- Cambia entre categorías en el panel derecho
- Prueba exportar a diferentes carpetas

---

## 📸 QUÉ DEBERÍAS VER

### Panel Izquierdo (Preview):
```
┌────────────────────┐
│ Preview            │
│                    │
│ [Imagen sprite]    │
│                    │
│ Selecciones:       │
│ ☑ ✓ sprite_1      │ ← Checkbox marcado, guardado
│ ☑ ○ sprite_2      │ ← Checkbox marcado, no guardado
│ ☐ ○ sprite_3      │ ← Checkbox desmarcado
│                    │
│ ┌────────────────┐ │
│ │ Animación      │ │ ← Solo si preview activo
│ │ [Frame]        │ │
│ │ Frame 2/3      │ │
│ └────────────────┘ │
└────────────────────┘
```

### Barra de Estado (Inferior):
```
Zoom: 1.50x | Selecciones: 4 | Guardados: 2 | Marcados: 3 | Sheet: 256x128
```

---

## 🎉 SI TODO FUNCIONA

**¡Felicidades! El editor está completamente funcional.**

Ahora puedes:
- Crear animaciones completas
- Exportar múltiples sprites rápidamente
- Previsualizar antes de guardar
- Navegar cómodamente con pan y zoom
- Seleccionar exactamente qué exportar con checkboxes

---

## 📞 SI ALGO NO FUNCIONA

1. **Cierra el editor**
2. **Verifica que usaste el archivo actualizado**
3. **Revisa la consola** por mensajes de error
4. **Prueba con una imagen PNG simple** primero
5. **Reporta el problema** con detalles

---

**Última actualización:** 17 de noviembre de 2025  
**Versión:** 2.0.0

*"Si todos los tests pasan, el editor está listo para producción."* ✅
