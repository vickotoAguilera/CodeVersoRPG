from pathlib import Path
import json
import sys


def find_list_lengths(obj, key):
    """Recursively search for lists under `key` and return total length found."""
    total = 0
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], list):
            total += len(obj[key])
        for v in obj.values():
            total += find_list_lengths(v, key)
    elif isinstance(obj, list):
        for item in obj:
            total += find_list_lengths(item, key)
    return total


def main():
    base = Path('src/database')
    if not base.exists():
        base = Path('src')
    mapas = sorted(list(base.rglob('*.json')))
    if not mapas:
        print('No se encontraron archivos .json bajo', base)
        sys.exit(1)

    print('MAPA'.ljust(40), '| PORTALES | SPAWNS | MUROS | ZONAS_BATALLA')
    print('-' * 80)
    for m in mapas:
        try:
            data = json.load(open(m, encoding='utf-8'))
        except Exception as e:
            print(f'{m}: ERROR al leer JSON: {e}')
            continue

        portales = find_list_lengths(data, 'portales')
        spawns = find_list_lengths(data, 'spawns')
        muros = find_list_lengths(data, 'muros')
        zonas = find_list_lengths(data, 'zonas_batalla')

        print(f'{str(m).ljust(40)} | {str(portales).rjust(7)} | {str(spawns).rjust(6)} | {str(muros).rjust(5)} | {str(zonas).rjust(13)}')


if __name__ == '__main__':
    main()
