"""
Descargador de Sprites para NES - Versión 2
Usa el subdominio sprites.spriters-resource.com
"""
import requests
from pathlib import Path
import time
import re

BASE_URL = "https://sprites.spriters-resource.com"
DOWNLOAD_DIR = Path(r"c:\Users\vicko\Documents\RPG\assets\sprites\NES")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Juegos NES - slug en sprites.spriters-resource.com
NES_GAMES = [
    ("finalfantasy", "Final Fantasy"),
    ("finalfantasy2", "Final Fantasy II"),
    ("finalfantasy3", "Final Fantasy III"),
    ("dragonwarrior", "Dragon Warrior"),
    ("dragonwarrior2", "Dragon Warrior II"),
    ("dragonwarrior3", "Dragon Warrior III"),
    ("dragonwarrior4", "Dragon Warrior IV"),
    ("earthboundzero", "Earthbound Zero"),
    ("mother", "Mother"),
    ("shinsekai", "Shinsekai"),
    ("seikendensetsu3", "Seiken Densetsu III"),
    ("herakles", "Herakles"),
    ("lagrange", "Lagrange"),
    ("cristiano", "Cristiano"),
    ("fireemblem", "Fire Emblem"),
    ("fireemblem2", "Fire Emblem II"),
    ("willow", "Willow"),
    ("wizardsandwarriors", "Wizards & Warriors"),
]

def try_download(url, filepath):
    """Intenta descargar un archivo"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def process_game(slug, game_name, game_num, total):
    """Procesa un juego"""
    print(f"\n[{game_num}/{total}] {game_name}")

    game_dir = DOWNLOAD_DIR / game_name.replace(' ', '_')
    game_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = 0

    # Probar varias estructuras de URL
    url_variants = [
        f"{BASE_URL}/nes/{slug}/",
        f"{BASE_URL}/nes/{slug.lower()}/",
        f"{BASE_URL}/nes/{slug.replace('_', '')}/",
    ]

    found_urls = set()

    for variant in url_variants:
        print(f"  Probando: {variant}")
        try:
            r = requests.get(variant, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                # Buscar todos los enlaces a assets
                links = re.findall(r'href="(/nes/[^"]+/\d+/)"', r.text)
                for link in links:
                    if '/full/' not in link and '/sheet/' in link:
                        found_urls.add(BASE_URL + link)
                if found_urls:
                    break
        except Exception as e:
            print(f"    Error: {e}")
        time.sleep(0.5)

    print(f"  Encontrados {len(found_urls)} sheets")

    for i, url in enumerate(found_urls, 1):
        # Extraer nombre del archivo
        parts = url.split('/')
        filename = parts[-2] if parts else f"sprite_{i}.png"
        filename = re.sub(r'[^\w\-]', '', filename) + '.png'
        filepath = game_dir / filename

        if filepath.exists():
            filename = f"{parts[-2]}_{i}.png"
            filepath = game_dir / filename

        print(f"  [{i}/{len(found_urls)}] {filename[:40]}...", end=" ")
        if try_download(url, filepath):
            print("OK")
            downloaded += 1
        else:
            print("FAIL")
            failed += 1
        time.sleep(0.2)

    print(f"  Descargados: {downloaded}, Fallidos: {failed}")
    return downloaded

def main():
    print("="*60)
    print("DESCARGADOR NES v2 - Sprites Subdomain")
    print("="*60)

    total = 0
    start = time.time()

    for i, (slug, name) in enumerate(NES_GAMES, 1):
        count = process_game(slug, name, i, len(NES_GAMES))
        total += count
        time.sleep(1)

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"COMPLETADO: {total} sprites en {elapsed/60:.1f} min")
    print(f"Directorio: {DOWNLOAD_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()