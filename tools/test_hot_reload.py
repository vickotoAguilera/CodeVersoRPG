import time
import os
from editor_unificado import EditorUnificado


def main():
    editor = EditorUnificado()
    # Buscar mapa_herrero
    mapa = None
    for m in editor.mapas_disponibles:
        if m.nombre == 'mapa_herrero':
            mapa = m
            break

    if not mapa:
        print('No se encontró mapa_herrero en la lista')
        return

    editor.cargar_mapa(mapa)
    print('\nEstado inicial: elementos=', len(editor.elementos))
    print('Timestamps:', editor.archivos_modificados)

    ruta = str(mapa.ruta_json)
    print('Tocando archivo:', ruta)
    os.utime(ruta, None)

    # Forzar chequeo
    editor.ultimo_check = 0
    editor._check_hot_reload()

    print('\nDespués de _check_hot_reload: elementos=', len(editor.elementos))


if __name__ == '__main__':
    main()
