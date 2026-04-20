# 🎮 CÓMO PROBAR EL SISTEMA DE COFRES

**Fecha:** 17 Noviembre 2025

---

## 📍 UBICACIÓN DE COFRES DE PRUEBA

En el **Mapa Pradera** (`mapa_pradera.jpg`) hay 2 cofres:

### Cofre 1: Sin Llave
- **ID:** `COFRE_PRADERA_01`
- **Posición:** X: 300, Y: 400
- **Requiere llave:** NO
- **Contenido:** 
  - Poción x3
  - Éter x1

### Cofre 2: Con Llave de Bronce
- **ID:** `COFRE_PRADERA_SECRETO`
- **Posición:** X: 800, Y: 300
- **Requiere llave:** LLAVE_BRONCE
- **Contenido:**
  - Poción x5
  - Éter x3
  - Expansor de Ranuras x1

---

## 🎮 CONTROLES

| Tecla | Acción |
|-------|--------|
| **ENTER** | Interactuar con cofre cercano |
| **Flechas** | Moverse por el mapa |
| **ESC** | Menú de pausa |

---

## 🧪 PASOS PARA PROBAR

### Test 1: Cofre Simple (Sin Llave)

1. **Iniciar nuevo juego** o **cargar partida**
2. **Ir a la posición** X:300, Y:400 (aparece en esquina superior izquierda)
3. **Acercarse al cofre** (debe estar a menos de 50 píxeles)
4. **Presionar ENTER**
5. **Verificar:**
   - ✓ Aparece pantalla "¡Cofre Abierto!"
   - ✓ Muestra "Poción x3" y "Éter x1" en verde
   - ✓ Cuenta regresiva de 3 segundos
   - ✓ Se cierra automáticamente o con ENTER
   - ✓ Sprite del cofre cambia a "vacío"
6. **Presionar ESC** y revisar inventario
7. **Verificar que los items se agregaron**

### Test 2: Cofre con Llave (Sin la Llave)

1. **Ir a la posición** X:800, Y:300
2. **Acercarse al cofre**
3. **Presionar ENTER**
4. **Verificar:**
   - ✓ Aparece mensaje en consola: "Este cofre está cerrado con llave."
   - ✓ Cofre permanece cerrado
   - ✓ No se obtienen items

### Test 3: Cofre con Llave (Con la Llave)

1. **Agregar llave al inventario** (temporal, para testing):
   - Editar `database/grupo_inicial.json`
   - Agregar `"LLAVE_BRONCE": 1` en `items_especiales`
   - O agregar en `items_iniciales`
2. **Reiniciar juego** o cargar partida con la llave
3. **Ir a la posición** X:800, Y:300
4. **Acercarse al cofre**
5. **Presionar ENTER**
6. **Verificar:**
   - ✓ Cofre se abre
   - ✓ Aparece pantalla de recompensa
   - ✓ Muestra 3 items (pociones, éteres, expansor)
   - ✓ Expansor aparece en **dorado** (item especial)
   - ✓ Sprite cambia a vacío
7. **Revisar inventario**
8. **Verificar que el Expansor de Ranuras se agregó**

### Test 4: Cofre Vacío

1. **Abrir cualquier cofre** (Test 1 o Test 3)
2. **Alejarse del cofre**
3. **Volver a acercarse**
4. **Presionar ENTER**
5. **Verificar:**
   - ✓ Mensaje en consola: "El cofre está vacío..."
   - ✓ No aparece pantalla de recompensa
   - ✓ Sprite permanece en estado "vacío"

---

## 🐛 PROBLEMAS COMUNES

### El cofre no aparece en el mapa

**Solución:**
1. Verificar que `cofre.png` esté en `assets/sprites/cofres y demas/`
2. Revisar la consola al iniciar - debe decir "✓ Sprites del cofre cargados"

### No se puede interactuar con el cofre

**Posibles causas:**
1. **Muy lejos:** Acércate más (menos de 50 píxeles)
2. **Posición incorrecta:** Verifica coordenadas en pantalla
3. **Error de carga:** Revisa consola por errores

### La llave no funciona

**Verificar:**
1. ID de llave en `cofres_db.json` coincide con `items_db.json`
2. Llave está en inventario (normal o especial)
3. Revisar consola por mensajes de error

### Items no se agregan al inventario

**Verificar:**
1. Items existen en `items_db.json`
2. Abrir menú de pausa → Items → verificar categorías
3. Items especiales están en categoría "Especiales"

---

## 📊 CHECKLIST DE TESTING COMPLETO

- [ ] Cofre sin llave se abre
- [ ] Items se agregan correctamente
- [ ] Sprite cambia de cerrado → abierto → vacío
- [ ] Pantalla de recompensa muestra items correctos
- [ ] Colores: Verde (consumibles), Dorado (especiales)
- [ ] Auto-cierre en 3 segundos funciona
- [ ] ENTER cierra pantalla inmediatamente
- [ ] ESC cierra pantalla inmediatamente
- [ ] Cofre con llave sin tenerla muestra mensaje
- [ ] Cofre con llave teniendo llave se abre
- [ ] Cofre vacío muestra mensaje correcto
- [ ] No se puede abrir cofre vacío múltiples veces
- [ ] Expansor de Ranuras aparece en inventario especial
- [ ] Coordenadas del héroe se muestran correctamente

---

## 🔧 AGREGAR LLAVE TEMPORAL (Testing)

### Opción 1: Editar grupo_inicial.json

```json
{
  "miembros": [
    {
      "nombre_en_juego": "Cloud",
      "id_clase_db": "HEROE_1",
      "id_coords_db": "COORDS_CLOUD",
      "items_especiales": {
        "LLAVE_BRONCE": 1,
        "LLAVE_PLATA": 1,
        "LLAVE_ORO": 1
      }
    }
  ]
}
```

### Opción 2: Consola de Python (Durante el juego)

Si tienes acceso a consola de debugging:
```python
grupo_heroes[0].inventario_especiales["LLAVE_BRONCE"] = 1
```

---

## 📝 NOTAS IMPORTANTES

1. **Los cofres se resetean** cada vez que inicias nuevo juego
2. **Sistema de guardado de cofres** aún no implementado
3. **Sprites fallback:** Si no se carga imagen, verás cuadrados de colores
4. **Distancia de interacción:** 50 píxeles por defecto

---

## 🎯 PRÓXIMOS PASOS

Después de probar el sistema básico:

1. Implementar guardado de estado de cofres
2. Agregar más cofres en otros mapas
3. Crear llaves obtenibles en juego (no solo iniciales)
4. Agregar cofres con items raros/únicos
5. Implementar animación de apertura

---

**¡Disfruta probando el sistema de cofres!** 📦✨
