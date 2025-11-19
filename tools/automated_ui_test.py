import importlib.util
from pathlib import Path
import time

# Cargar módulo por ruta para evitar problemas de import
spec = importlib.util.spec_from_file_location('editor_unificado_mod', str(Path('editor_unificado.py').resolve()))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

EditorUnificado = mod.EditorUnificado

def center(rect):
    return rect.left + rect.width//2, rect.top + rect.height//2

def main():
    print('Iniciando prueba UI automatizada...')
    editor = EditorUnificado()

    # Seleccionar mapa conocido con elementos
    target = None
    for m in editor.mapas_disponibles:
        # Preferir la versión dentro de 'pueblo_inicio' si existe
        if 'pueblo_inicio' in str(m.ruta_json):
            if m.nombre == 'mapa_herrero':
                target = m
                break
    if not target:
        target = editor.mapas_disponibles[0]

    print('Cargando mapa de prueba:', target.ruta_json)
    editor.cargar_mapa(target)

    # Dibujar panel para generar hitboxes
    editor._draw_panel()
    time.sleep(0.1)

    resultados = {'toggles': [], 'categorias': [], 'map_click': None}

    # Probar toggles (capas)
    for capa, rect in editor.capas_hitboxes.items():
        before = editor.capas_visibles.get(capa)
        cx, cy = center(rect)
        editor._handle_click_panel(cx, cy)
        after = editor.capas_visibles.get(capa)
        resultados['toggles'].append((capa, before, after))

    # Abrir selector y dibujarlo
    editor.mostrar_selector_mapas = True
    # Forzar scroll a 0 para mostrar inicio de la lista
    editor.scroll_mapas = 0
    editor._draw_panel()
    editor._draw_selector_mapas()
    time.sleep(0.1)

    # Probar clic en la primera categoría disponible
    categorias = list(editor.selector_hitboxes['categorias'].items())
    if categorias:
        cat_name, cat_rect = categorias[0]
        before = editor.categorias_expandidas.get(cat_name, False)
        cx, cy = center(cat_rect)
        editor._handle_click_selector_mapas(cx, cy)
        after = editor.categorias_expandidas.get(cat_name, False)
        resultados['categorias'].append((cat_name, before, after))

        # Si se expandió, intentar click en el primer mapa listado
        if after:
            # Si no hay mapas visibles por el scroll, forzar scroll=0 y redibujar
            if not editor.selector_hitboxes.get('mapas'):
                editor.scroll_mapas = 0
                editor._draw_panel()
                editor._draw_selector_mapas()

            if editor.selector_hitboxes.get('mapas'):
                mapa, mapa_rect = editor.selector_hitboxes['mapas'][0]
                cx, cy = center(mapa_rect)
                prev_mapa = editor.mapa_actual
                editor._handle_click_selector_mapas(cx, cy)
                resultados['map_click'] = (str(prev_mapa.ruta_json) if prev_mapa else None, str(editor.mapa_actual.ruta_json) if editor.mapa_actual else None)
            else:
                resultados['map_click'] = ('no_map_hitboxes', None)
    else:
        print('No se encontraron categorías en selector_hitboxes')

    # Cerrar selector
    if editor.selector_hitboxes.get('cerrar'):
        cx, cy = center(editor.selector_hitboxes['cerrar'])
        editor._handle_click_selector_mapas(cx, cy)

    # Mostrar resultados
    print('\nResultados de la prueba automatizada:')
    for t in resultados['toggles']:
        print(f"Toggle {t[0]}: {t[1]} -> {t[2]}")
    for c in resultados['categorias']:
        print(f"Categoria {c[0]}: {c[1]} -> {c[2]}")
    print('Map click cambio:', resultados['map_click'])

    # Cerrar pygame
    try:
        import pygame
        pygame.quit()
    except Exception:
        pass

if __name__ == '__main__':
    main()
