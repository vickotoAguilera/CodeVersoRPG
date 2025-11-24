"""Script de prueba para el editor unificado"""
import sys
from pathlib import Path

# Importar el editor
from editor_unificado import EditorUnificado, MapaInfo

# Crear instancia del editor
editor = EditorUnificado()

# Cargar mapa de prueba con múltiples elementos
mapa_test = MapaInfo(
    nombre="mapa_pueblo_final",
    categoria="ciudades_y_pueblos/pueblo_inicio",
    ruta_json=Path("src/database/mapas/ciudades_y_pueblos/pueblo_inicio/mapa_pueblo_final.json"),
    ruta_imagen=Path("assets/maps/ciudades_y_pueblos/pueblo_inicio/mapa_pueblo_final.png")
)

editor.cargar_mapa(mapa_test)

# Ejecutar
editor.run()
