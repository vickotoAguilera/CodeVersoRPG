# Esquema JSON para mapas (Editor Unificado)

Este documento define el esquema canónico que debe exportar el `editor_unificado` para que el juego cargue mapas completos.

Ruta recomendada:

- Imagen: `assets/maps/<categoria>/<archivo_imagen>`
- JSON datos: `src/database/mapas/<categoria>/<id>.json`

Campos principales (top-level)

- `id` (string) — Identificador único del mapa (ej. `mapa_pradera`). Recomendado usar minúsculas y guiones bajos.
- `nombre` (string) — Nombre legible mostrado en selectores.
- `categoria` (string) — Carpeta/agrupación (ej. `mundo`, `ciudades_y_pueblos`).
- `imagen` (string) — Nombre de la imagen relativa a `assets/maps/<categoria>/` (ej. `mapa_pradera.png`).
- `meta` (object, opcional) — Metadatos: `autor`, `version`, `creado`, `modificado`, `notas`.

Elementos del mapa

- `muros` (array, opcional) — Lista de muros. Cada elemento puede ser:

  - Rectángulo: `{ "x": int, "y": int, "w": int, "h": int }`
  - Polígono: `{ "puntos": [[x,y],[x,y],...] }` (se calcula bbox para colisión si es necesario)

- `zonas_batalla` (array, opcional) — Igual formato que `muros` (rect o polígono).

- `portales` (array, opcional) — Cada portal:

  - `id` (string, opcional)
  - `caja` (obj) o `puntos` (array) o `x`/`y`: area activadora
    - `caja`: `{ "x":int, "y":int, "w":int, "h":int }`
    - `puntos`: `[[x,y],...]`
  - `mapa_destino`: string — puede ser `id` conocido o nombre de archivo (`mapa_pueblo_final.png`).
  - `categoria_destino`: string (opcional)
  - `pos_destino`: `[x,y]` (opcional) — posición en el mapa destino donde aparecerá el héroe.
  - `meta` (opcional)

- `spawns` (array, opcional) — Posiciones de aparición de héroes. Elementos aceptados:

  - Punto simple: `[x,y]` o `{ "x":int,"y":int, "id": "spawn1" }`
  - Polígono: `{ "puntos": [[x,y],...] }` → editor usa centro del bbox como spawn.

- `cofres` (array, opcional) — Cada cofre:

  - `id_cofre` (string) — debe existir en `src/database/cofres_db.json` (si no, se carga con advertencia).
  - `x`,`y` o `pos` — posición.
  - `escala` (float, opcional)
  - `caja` (opcional) — área de interacción.

- `extras` (object, opcional) — Para triggers, NPCs u otros datos específicos del editor.

Reglas y recomendaciones

- Coordenadas en píxeles (enteros).
- Polígonos deben tener al menos 3 puntos.
- Evitar nombres duplicados de `id` entre mapas.
- Si `imagen` no existe, el loader intentará buscar por nombre base en la carpeta de assets.

Ejemplo mínimo

```
{
  "id": "mapa_pradera",
  "nombre": "Pradera",
  "categoria": "mundo",
  "imagen": "mapa_pradera.png",
  "spawns": [[200,150]],
  "muros": [{"x":0,"y":300,"w":800,"h":32}],
  "portales": [
    {
      "id": "P_A",
      "caja": {"x":760,"y":280,"w":40,"h":40},
      "mapa_destino": "mapa_pueblo_final.png",
      "categoria_destino": "ciudades_y_pueblos",
      "pos_destino": [120,200]
    }
  ]
}
```

Este esquema facilita que el juego aplique la lógica existente (muros → colisión; portales → teletransporte; cofres → lookup en `cofres_db.json`; spawns → posicionamiento inicial).

Próximo: crear ejemplos concretos y un script para generar `src/database/maps_index.json` automáticamente.
