# INSTRUCCIONES DE TESTING - RECUPERACIÓN DE COFRES

## Configuración Actual
- ⏱️ **Tiempo de recuperación: 10 SEGUNDOS** (configurado para testing rápido)
- 📍 Archivos modificados:
  - `main.py` línea 174: `TIEMPO_RECUPERACION_COFRE = 10`
  - `src/mapa.py` línea 425: `TIEMPO_RECUPERACION = 10`

## Cómo Probar la Recuperación

### Test 1: Verificar que el Cofre se Recupera Después de 10 Segundos

1. **Iniciar el juego** y crear una nueva partida
2. **Abrir un cofre** (presionar 'E' cerca del cofre)
   - Verás el mensaje: `[Cofre] Estado guardado: [id_cofre] abierto en t=X.Xs`
3. **Esperar 10 segundos de TIEMPO DE JUEGO**
   - ⚠️ IMPORTANTE: El tiempo debe transcurrir DENTRO del juego
   - Muévete por el mapa, camina, etc. (el tiempo de pausa NO cuenta)
   - Puedes ver el tiempo de juego en la consola
4. **Cambiar de mapa** usando un portal
5. **Regresar al mapa original**
6. **Verificar el cofre:**
   - ✅ **ESPERADO:** El cofre debe estar CERRADO y con ítems nuevamente
   - ✅ Deberías ver en consola: `[Cofre] '[id_cofre]' RECUPERADO (pasaron X.Xs)`

### Test 2: Verificar que el Cofre NO se Recupera Antes de 10 Segundos

1. **Abrir un cofre**
2. **Esperar solo 5 segundos** (menos de 10)
3. **Cambiar de mapa y regresar**
4. **Verificar el cofre:**
   - ✅ **ESPERADO:** El cofre debe seguir VACÍO
   - ✅ Deberías ver en consola: `[Cofre] '[id_cofre]' cargado (recupera en X.Xs)`

### Test 3: Recuperación con Guardado/Carga

1. **Abrir un cofre**
2. **Guardar la partida** (presionar 'G')
3. **Esperar 10 segundos de tiempo de juego**
4. **Guardar nuevamente** (para que el tiempo se guarde)
5. **Cargar la partida** (salir al menú y cargar)
6. **Verificar el cofre:**
   - ✅ **ESPERADO:** El cofre debe estar RECUPERADO (cerrado con ítems)

## Mensajes de Consola a Buscar

### Cuando abres un cofre:
```
[Cofre] Estado guardado: cofre_madera_01 abierto en t=123.4s
```

### Cuando cargas un mapa y el cofre AÚN NO se recupera:
```
[Cofre] 'cofre_madera_01' cargado (recupera en 7.3s)
```

### Cuando cargas un mapa y el cofre YA se recuperó:
```
[Cofre] 'cofre_madera_01' RECUPERADO (pasaron 12.5s)
```

## Troubleshooting

### El cofre no se recupera después de 10 segundos
- ✅ Verifica que estés esperando **tiempo de JUEGO**, no tiempo real
- ✅ El tiempo de pausa NO cuenta
- ✅ Debes **cambiar de mapa** para que se aplique la lógica de recuperación
- ✅ Verifica los mensajes en la consola

### El cofre se recupera inmediatamente
- ❌ Puede que el tiempo esté mal configurado
- Verifica que ambos archivos tengan `= 10` segundos

## Después del Testing

Una vez verificado que funciona correctamente, **RESTAURAR** el tiempo a 1 hora:

### En `main.py` línea 174:
```python
TIEMPO_RECUPERACION_COFRE = 3600  # 1 hora en segundos
```

### En `src/mapa.py` línea 425:
```python
TIEMPO_RECUPERACION = 3600  # 1 hora
```
