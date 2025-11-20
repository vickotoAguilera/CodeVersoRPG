from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
src_dir = ROOT / 'assets' / 'maps' / 'ciudades_y_pueblos' / 'pueblo_inicio'
dst_dir = ROOT / 'assets' / 'maps' / 'ciudades_y_pueblos'
dst_dir.mkdir(parents=True, exist_ok=True)
files = ['mapa_herrero.png','mapa_posada.png','mapa_pueblo_final.png','mapa_taberna.png','mapa_tienda_items.png','mapa_tienda_magia.png']
for f in files:
    s = src_dir / f
    d = dst_dir / f
    if s.exists():
        shutil.copy2(s, d)
        print('copied', s.relative_to(ROOT), '->', d.relative_to(ROOT))
    else:
        print('missing', s.relative_to(ROOT))
