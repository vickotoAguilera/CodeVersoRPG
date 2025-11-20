# Cambios automáticos en mapas

Fecha: 2025-11-20

Se aplicaron correcciones automáticas para normalizar JSON de mapas y mejorar la compatibilidad con el loader y el editor.

Resumen de acciones:

- Se rellenaron campos `id` e `imagen` en mapas que los tenían ausentes. Backups creados con extensión `.bak` en los mismos directorios.
- Se añadió `categoria_destino` por defecto en portales que no lo contenían (valor: categoría del mapa origen).
- Se aseguraron dimensiones `w`/`h` en `portales[].caja`, `muros` y `zonas_batalla` cuando faltaban (valores por defecto razonables).
- Se generó/actualizó `src/database/maps_index.json`.

Archivos afectados (lista parcial):

- `src/database/mapas/ciudades_y_pueblos/*.json`
- `src/database/mapas/mundo/mapa_pradera.json`

Backups:

- Todos los JSON modificados tienen un archivo `.bak` al lado con el contenido original.

Recomendaciones:

- Revisar los JSON modificados antes de mergear a `main` si necesitas conservar campos personalizados.
- Ejecutar `tools/validate_map.py` para detectar problemas adicionales.
