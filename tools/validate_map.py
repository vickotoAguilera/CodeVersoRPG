#!/usr/bin/env python3
"""
Validación básica de archivos de mapa según `docs/MAP_SCHEMA.md`.
Imprime advertencias y devuelve código 0 si todo está OK (solo chequeos básicos), 2 si hay errores graves.
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_MAPS = ROOT / 'src' / 'database' / 'mapas'


def validar_mapa(path: Path):
    errores = []
    advertencias = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        return [f'ERROR: No se pudo parsear {path}: {e}'], []

    mid = data.get('id')
    if not mid:
        errores.append('Falta campo "id"')
    if 'imagen' not in data:
        advertencias.append('Falta campo "imagen" (se intentará resolver por nombre)')

    def chequear_lista(lista, nombre):
        if not isinstance(lista, list):
            errores.append(f'Campo {nombre} debe ser lista si existe')
            return
        for i, it in enumerate(lista):
            if nombre == 'muros':
                if not (isinstance(it, dict) and (set(('x','y','w','h')).issubset(it.keys()) or 'puntos' in it)):
                    errores.append(f'Muros[{i}] formato inválido')
            if nombre == 'portales':
                if not isinstance(it, dict):
                    errores.append(f'Portales[{i}] debe ser objeto')
                else:
                    if not any(k in it for k in ('caja','puntos','x')):
                        errores.append(f'Portales[{i}] no tiene área activadora (caja/puntos/x)')

    if 'muros' in data:
        chequear_lista(data['muros'], 'muros')
    if 'portales' in data:
        chequear_lista(data['portales'], 'portales')

    return errores, advertencias


def main():
    mapas = list(DB_MAPS.rglob('*.json'))
    total_err = 0
    total_warn = 0
    for m in mapas:
        errs, warns = validar_mapa(m)
        if errs:
            print(f'[{m}] ERRORES:')
            for e in errs:
                print('  -', e)
            total_err += len(errs)
        if warns:
            print(f'[{m}] ADVERTENCIAS:')
            for w in warns:
                print('  -', w)
            total_warn += len(warns)

    print(f'Validación completada: {len(mapas)} mapas escaneados. Errores: {total_err}. Advertencias: {total_warn}.')
    if total_err > 0:
        sys.exit(2)


if __name__ == '__main__':
    main()
