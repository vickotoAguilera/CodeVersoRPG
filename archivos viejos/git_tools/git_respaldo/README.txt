========================================
  SISTEMA DE RESPALDO Y RECUPERACION
========================================

ORDEN DE USO:
=============

ANTES DE HACER CAMBIOS IMPORTANTES:
------------------------------------
1. Ejecuta: 1_CREAR_RESPALDO.bat
   - Crea un punto de restauracion automatico
   - Nombrado con fecha y hora
   - Ejemplo: respaldo-20251121-150230

2. Trabaja normalmente
   - Haz tus cambios
   - Haz commits
   - Haz push a GitHub

SI ALGO SALE MAL Y QUIERES VOLVER ATRAS:
-----------------------------------------
3. Ejecuta: 2_VER_RESPALDOS.bat
   - Muestra todos los respaldos disponibles
   - Anota el nombre del respaldo que quieres

4. Ejecuta: 3_RECUPERAR_RESPALDO.bat
   - Te pedira el nombre del respaldo
   - Confirmacion de seguridad
   - Restaura tu proyecto al estado anterior

MANTENIMIENTO (OPCIONAL):
-------------------------
5. Ejecuta: 4_LIMPIAR_RESPALDOS_VIEJOS.bat
   - Elimina respaldos antiguos que ya no necesites
   - Mantiene tu repositorio limpio

========================================
  CONSEJOS IMPORTANTES
========================================

✓ Crea un respaldo ANTES de hacer cambios grandes
✓ Los respaldos no ocupan mucho espacio
✓ Puedes tener multiples respaldos
✓ Los respaldos son locales (no se suben a GitHub automaticamente)
✓ Si quieres subir un respaldo a GitHub, usa git push origin nombre-rama

========================================
  EJEMPLOS DE USO
========================================

Ejemplo 1: Antes de agregar una nueva funcionalidad
1. Ejecuto: 1_CREAR_RESPALDO.bat
2. Agrego la nueva funcionalidad
3. Si funciona bien, sigo trabajando
4. Si no funciona, ejecuto 3_RECUPERAR_RESPALDO.bat

Ejemplo 2: Recuperar version de ayer
1. Ejecuto: 2_VER_RESPALDOS.bat
2. Busco el respaldo de ayer (ejemplo: respaldo-20251120-140000)
3. Ejecuto: 3_RECUPERAR_RESPALDO.bat
4. Ingreso: respaldo-20251120-140000
5. Confirmo con: SI

========================================
