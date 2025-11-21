from editor_portales import EditorPortales, MapaInfo
from pathlib import Path

# Llamar al método sin instanciar la ventana completa
maps = EditorPortales._buscar_mapas(None, Path('assets/maps/ciudades_y_pueblos'), 'ciudades_y_pueblos')
print('Total mapas detectados en categoría ciudades_y_pueblos:', len(maps))
for m in maps:
    print('-', m.nombre, '->', m.ruta, 'sub:', m.subcarpeta)
