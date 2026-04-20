"""
Descargador de Sprites para NES
Descarga todos los RPGs de NES de The Spriters Resource
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re
import json

BASE_URL = "https://www.spriters-resource.com"
DOWNLOAD_DIR = Path(r"c:\Users\vicko\Documents\RPG\assets\sprites\NES")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.spriters-resource.com/'
}

# Juegos NES de la lista
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

def get_page(url, retry=3):
    """Descarga una página con reintentos"""
    for i in range(retry):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return BeautifulSoup(r.text, 'html.parser')
            elif r.status_code == 404:
                print(f"  [404] Pagina no encontrada")
                return None
            else:
                print(f"  Intento {i+1}/{retry} - Status {r.status_code}")
        except Exception as e:
            print(f"  Error: {e}, reintento {i+1}/{retry}")
        time.sleep(1)
    return None

def extract_sprite_sheets(soup, game_name):
    """Extrae los enlaces a sprite sheets de una página de juego"""
    sheets = []
    if not soup:
        return sheets

    # Buscar todos los enlaces que apunten a sheets
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)

        # Los sheets tienen formato: /nes/game/sheet/NUMERO/
        if f'/sheet/' in href and '/full/' not in href:
            # Verificar que no sea un enlace genérico
            if 'source=' not in href:  # Evita enlaces de búsqueda
                full_url = BASE_URL + href if href.startswith('/') else href
                name = text if text else f"sprite_{len(sheets)+1}"
                # Limpiar nombre
                name = re.sub(r'[^\w\s\-]', '', name)
                name = name.strip() or f"sprite_{len(sheets)+1}"
                sheets.append({'name': name, 'url': full_url})

    return sheets

def download_sprite(url, save_path):
    """Descarga un sprite sheet"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  ⚠ Error descargando {url}: {e}")
    return False

def process_game(slug, game_name, game_num, total):
    """Procesa un juego: busca sheets y descarga"""
    print(f"\n[{game_num}/{total}] {game_name}")
    print(f"  URL: {BASE_URL}/nes/{slug}/")

    game_dir = DOWNLOAD_DIR / game_name.replace(' ', '_')
    game_dir.mkdir(parents=True, exist_ok=True)

    # Intentar varias variantes de URL
    variants = [
        f"/nes/{slug}/sheet/",
        f"/nes/{slug.lower().replace(' ','')}/sheet/",
    ]

    all_sheets = []
    for variant in variants:
        url = BASE_URL + variant
        print(f"  Intentando: {url}")
        soup = get_page(url)
        if soup:
            sheets = extract_sprite_sheets(soup, game_name)
            if sheets:
                all_sheets.extend(sheets)
                break  # Si encontramos sheets, paramos
        time.sleep(0.5)

    # Eliminar duplicados
    seen = set()
    unique_sheets = []
    for s in all_sheets:
        if s['url'] not in seen:
            seen.add(s['url'])
            unique_sheets.append(s)

    print(f"  Encontrados {len(unique_sheets)} sprite sheets")

    # Descargar cada sheet
    for i, sheet in enumerate(unique_sheets, 1):
        filename = f"{sheet['name'][:50]}.png"
        filepath = game_dir / filename

        # Evitar sobreescribir
        if filepath.exists():
            filename = f"{sheet['name'][:40]}_{i}.png"
            filepath = game_dir / filename

        print(f"  [{i}/{len(unique_sheets)}] {filename}")
        if download_sprite(sheet['url'], filepath):
            print(f"    ✓ Guardado")
        else:
            print(f"    ✗ Error")

        time.sleep(0.3)  # Ser respetuoso con el servidor

    return len(unique_sheets)

def main():
    print("="*60)
    print("DESCARGADOR DE SPRITES - NES RPGs")
    print("="*60)
    print(f"Directorio: {DOWNLOAD_DIR}")
    print(f"Juegos a procesar: {len(NES_GAMES)}")
    print("="*60)

    total_sheets = 0
    start_time = time.time()

    for i, (slug, name) in enumerate(NES_GAMES, 1):
        count = process_game(slug, name, i, len(NES_GAMES))
        total_sheets += count
        time.sleep(1)  # Pausa entre juegos

    elapsed = time.time() - start_time

    print("\n" + "="*60)
    print("DESCARGA COMPLETADA")
    print("="*60)
    print(f"Juegos procesados: {len(NES_GAMES)}")
    print(f"Total sprite sheets: {total_sheets}")
    print(f"Tiempo: {elapsed/60:.1f} minutos")
    print(f"Directorio: {DOWNLOAD_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()