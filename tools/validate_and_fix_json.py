from pathlib import Path
import json
import shutil

ROOT = Path('.')

def is_blank(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return False
    return s.strip() == ''

def backup(path: Path):
    bak = path.with_suffix(path.suffix + '.bak')
    shutil.copy2(path, bak)
    return bak

def main():
    print('Validando archivos .json...')
    bad = []
    fixed = []
    for p in sorted(ROOT.rglob('*.json')):
        # skip node_modules or hidden folders if any
        try:
            with p.open('r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            # If file is empty or whitespace-only, fix by writing {}
            if is_blank(p):
                print(f'  VACÍO: {p} — creando backup y escribiendo {{}}')
                bak = backup(p)
                p.write_text('{}\n', encoding='utf-8')
                fixed.append(p)
            else:
                print(f'  ERROR: {p} — {e}')
                bad.append((p, str(e)))
        except Exception as e:
            print(f'  SKIP/ERR: {p} — {e}')

    print('\nResumen:')
    print(f'  Archivos corregidos (vacíos -> {{}}): {len(fixed)}')
    for f in fixed:
        print('   -', f)
    print(f'  Archivos con error no corregidos: {len(bad)}')
    for p, e in bad:
        print('   -', p, '->', e)

if __name__ == "__main__":
    main()
