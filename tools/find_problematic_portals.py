from pathlib import Path
import json
import sys


def analisar_map_file(path):
    problems = []
    try:
        data = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        return [f'ERROR-JSON: {e}']

    portales = data.get('portales', [])
    if portales:
        for i, p in enumerate(portales):
            # poly portals
            if p.get('forma') == 'poly' or 'puntos' in p:
                if not p.get('puntos'):
                    problems.append(f'portal[{i}]: forma=poly pero sin puntos')
            else:
                # not poly: expect caja or x/y
                if 'caja' not in p and not ('x' in p and 'y' in p):
                    problems.append(f'portal[{i}]: sin caja ni x/y')

            # suspicious sizes
            w = None
            if 'caja' in p:
                w = p['caja'].get('w')
            elif 'w' in p:
                w = p.get('w')
            if isinstance(w, (int, float)) and w and w > 2000:
                problems.append(f'portal[{i}]: ancho sospechoso={w}')

    # spawns check
    spawns = data.get('spawns', []) or data.get('zonas_batalla', [])
    if spawns:
        for i, s in enumerate(spawns):
            if 'caja' not in s and not ('x' in s and 'y' in s):
                problems.append(f'spawn[{i}]: sin caja ni x/y')

    return problems


def main():
    base = Path('src/database/mapas')
    if not base.exists():
        print('No se encontró carpeta de mapas en src/database/mapas')
        sys.exit(1)

    print('Buscando JSON problemáticos en mapas...')
    mismatches = []
    found_any = False

    for json_file in sorted(base.rglob('*.json')):
        probs = analisar_map_file(json_file)
        if probs:
            found_any = True
            print('\n' + str(json_file))
            for p in probs:
                print('  -', p)

        # Check for separate portales/spawns files used by hot-reload
        nombre = json_file.stem
        ruta_portales_separado = Path(f"src/database/portales/{nombre}_portales.json")
        ruta_spawns_separado = Path(f"src/database/spawns/{nombre}_spawns.json")

        # If main JSON has portales but the separate file exists and is empty, flag
        try:
            main_data = json.load(open(json_file, encoding='utf-8'))
            main_portales = len(main_data.get('portales', []))
        except:
            main_portales = 0

        if ruta_portales_separado.exists():
            try:
                sep = json.load(open(ruta_portales_separado, encoding='utf-8'))
                sep_count = len(sep.get('portales', [])) if isinstance(sep, dict) else 0
            except:
                sep_count = 0

            if main_portales > 0 and sep_count == 0:
                mismatches.append((json_file, ruta_portales_separado))

    if mismatches:
        print('\nArchivos con portales en el JSON principal pero archivo separado vacío (posible causa de hot-reload faltante):')
        for mainf, sep in mismatches:
            print(f'  - {mainf}  <--  {sep} (vacío)')

    if not found_any and not mismatches:
        print('No se detectaron problemas obvios.')


if __name__ == '__main__':
    main()
