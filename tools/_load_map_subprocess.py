#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    if len(sys.argv) < 3:
        print('Uso: _load_map_subprocess.py <imagen_o_nombre> <categoria>')
        sys.exit(2)
    nombre = sys.argv[1]
    categoria = sys.argv[2]

    # Intentar usar display dummy
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    try:
        import pygame
        pygame.init()
        try:
            pygame.display.set_mode((1,1))
        except Exception:
            pass
    except Exception as e:
        print('WARN: pygame no disponible o fallo al inicializar:', e)

    try:
        from src.mapa import Mapa
        m = Mapa(nombre, categoria, 800, 600)
        print('OK')
        sys.exit(0)
    except SystemExit as se:
        # Propagar el código de salida si se llamó intencionalmente
        raise
    except Exception as e:
        print('ERROR', e)
        sys.exit(3)

if __name__ == '__main__':
    main()
