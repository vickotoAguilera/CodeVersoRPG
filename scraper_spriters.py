import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
import time

BASE_URL = "https://www.spriters-resource.com"
OUTPUT_FILE = Path(__file__).parent / "rpg_games_found.json"

def get_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        r = requests.get(url, headers=headers, timeout=30)
        print(f"  Status: {r.status_code} | Bytes: {len(r.text)}")
        return BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"  Error: {e}")
        return None

def extract_game_links_from_page(soup, section_filter=None):
    """Extrae enlaces de juegos de una página"""
    games = []
    if not soup:
        return games
    
    # Buscar todos los enlaces
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Solo nos interesa игры que tenga sheets
        # Los enlaces de juegos suelen tener formato: /[platform]/[game_name]/sheet/
        if '/sheet/' in href or '/sheetinfo/' in href:
            # Evitar duplicados y enlaces genéricos
            if 'full/' in href or 'search' in href or 'browser' in href:
                continue
            
            # Palabras clave de RPGs (Expandido)
            rpg_keywords = [
                # Final Fantasy (todas las versiones)
                'final fantasy', 'finalfantasy', 'ffvii', 'ffviii', 'ffix', 'ffx', 'ffxi', 'ffxii',
                'ffiv', 'ffv', 'ffvi', 'ffiii', 'ffii', 'ffi', 'ff7', 'ff8', 'ff9', 'ff10', 'ff12',
                'dissidia', 'crizz', 'crystal chronicle', 'chocobo', 'mobius',
                # Chrono
                'chrono trigger', 'chrono cross', 'chrono', 'chronotrigger',
                # Breath of Fire
                'breath of fire', 'breathoffire', 'bof', 'dragon quarter',
                # Dragon Quest
                'dragon quest', 'dragonquest', 'dq', 'slime', 'endentaru',
                # Earthbound / Mother
                'earthbound', 'mother', 'eb', 'mother2', 'mother3',
                # Mario RPG series
                'super mario rpg', 'marioparty', 'papermario', 'paper mario', 'mario', 'luigi',
                # Zelda (RPG-ish)
                'zelda', 'hyrule', 'ocarina', 'majora', 'alink',
                # Square RPGs
                'seiken densetsu', 'secret of mana', 'soe', 'gemfire', 'robotrek',
                'гонзо', 'mahjong', 'sim', 'board',
                # Persona / SMT
                'persona', 'shin megami', 'smt', 'devil survivor', 'etrian',
                'megami tensei', 'demon crest', 'soul hack', ' DDS', 'dcini',
                # Tales
                'tales of', 'talesof', 'tales symphonia', 'tales vesperia', 'tales of the Abyss',
                # Fire Emblem
                'fire emblem', 'fireemblem', 'advance wars', 'fe', 'binding blade', 'sacred stones',
                # Golden Sun
                'golden sun', 'goldensun',
                # Star Ocean
                'star ocean', 'starocean', 'so1', 'so2', 'so3', 'so4',
                # Xenogears / Xenosaga
                'xenogears', 'xenosaga', 'xenoblade', 'monolith', 'xenogears',
                # Suikoden
                'suikoden', 'suikoden2', 't suikoden', ' Genshin',
                # Parasite Eve
                'parasite eve', 'parasiteeve', 'pe',
                # Front Mission
                'front mission', 'frontmission', 'fm', 'ouzen',
                # Valkyrie Profile
                'valkyrie profile', 'valkyrieprofile', 'vp',
                # FFT / Tactics
                'final fantasy tactics', 'fft', 'tactics ogre', 'ogre tactics', 'fft',
                'front mission', 'tactics',
                # Lunar
                'lunar', 'lunar2', 'lunarsilver', 'blue dragon',
                # Pokémon
                'pokemon', 'pokémon', 'pokedex', 'pokemon1', 'pokemon2', 'pokemon3',
                # Digimon
                'digimon', 'digimon2', 'digimon3', 'digimon4',
                # Dragon Ball Z / Anime RPGs
                'dragon ball', 'dbz', 'dbz saga', 'dbgt', 'dokkan', 'fighters',
                'naruto', 'naru', 'bleach', 'ble',
                # One Piece
                'one piece', 'piece', 'op', 'gorosei',
                # JRPGs conocida
                'ys', 'yso', ' adventures', 'iro', 'lagrange',
                'starfy', 'kirby', 'mega man', 'megaman', 'roll',
                'metroid', 'kid icarus', 'icarus',
                'castlevania', 'konami', 'wizardry', 'rogue',
                'quest', 'quest64', 'hard', 'rpgsx',
                'baten', "kaito's", 'sirens', 'time soldier',
                'drakengard', 'nier', 'drakengard', 'yo', 'nino',
                'blazblue', 'blaz', 'calam', 'phantom', 'breath',
                'trails', 'kiseki', 'ao', 'zero', 'sen', 'cold steel', 'hajimari',
                'honkai', 'star rail', ' Genshin Impact',
                'sao', 'sword art', ' Hollow', ' Hollow_fragment',
                're:zero', 'rezero', 'konosuba', 'that time',
                'overlord', 'masquerade', 'disgaea', 'phantasy star', 'ps0', 'ps2', 'ps4',
                'sakura wars', 'sengoku', 'basilica', 'ront', 'rouk',
                'saga', 'sagau', 'scions', 'omake',
                'paladin', 'crest', 'baku', 'shinobi', 'strike',
                'fate', 'stay night', 'fsn', 'fz', 'gba',
                'zatch', 'shaman king', 'shaman', 'gintama',
                'messiah', 'shibuya', 'chaos;head', 'steins;gate', 'robot;',
                'chaos', 'da', 'danganronpa', 'ultra',
                'greninja', 'zoro', 'sanji', 'luffy', 'nami',
                'fairy tail', 'natsu', 'lucy', 'fairy',
                'gintama', 'silver', 'soul eater', 'bleach', 'ichigo',
                'inazuma', 'eleven', 'attel', 'kum', 'rum', 'horo',
                'valkyria', 'valkyrie', 'chronicles',
                'edelweiss', 'eden', 'ungi', 'wing', 'alf', 'rose',
                'yo', 'kaiji', 'akagi', 'gambler', 'kaiji',
                'sen', ' Meadows', 'evermore', 'oak', 'san',
                'monster hunter', 'hunter', 'ginsboro', 'gins',
                'tales of the Abyss', 'symphia', 'phantasy', 'vers',
                'kingdom hearts', 'kh', 'birth', 're:', 'chain',
                'megaera', 'vampire', 'sang', 'mundus', 'devil',
                'zettai', 'mugen', 'rinne', 'tenchi', 'ryo',
                'sprr', 'sprite', 'ffxiv', 'ffxv', 'ff16', 'ff7r', 'ff7 ',
                'kait', 'strider', 'strider2', 'hips', 'marion',
                'collection', 'anthology', 'remix', 'collection',
                'sd', 'super deformed',
            ]
            
            text_lower = text.lower()
            href_lower = href.lower()
            
            # Verificar si coincide con alguna keyword
            es_rpg = False
            for kw in rpg_keywords:
                if kw in text_lower or kw in href_lower:
                    es_rpg = True
                    break
            
            if es_rpg or (section_filter and any(x in href_lower for x in ['finalfantasy', 'dragonquest', 'pokemon', 'tales', 'chrono', 'persona', 'smt', 'breath', 'xeno', 'star', 'suikoden', 'lunar', 'fft', 'fire', 'golden', 'shin ', 'valkyrie', 'vagrant', 'front'])):
                full_url = href if href.startswith('http') else BASE_URL + href
                
                # Evitar duplicados
                if not any(g['url'] == full_url for g in games):
                    games.append({
                        'name': text if text else href.split('/')[-1].replace('_', ' ').title(),
                        'url': full_url,
                        'type': 'rpg'
                    })
    
    return games

def scan_platform(platform_url, platform_name, game_type):
    print(f"\n{'='*60}")
    print(f"ESCANEANDO: {platform_name}")
    print(f"URL: {platform_url}")
    print(f"{'='*60}")
    
    soup = get_page(platform_url)
    if not soup:
        return []
    
    games = extract_game_links_from_page(soup, platform_name)
    print(f"Encontrados: {len(games)} potential RPGs")
    
    return games

def main():
    print("="*60)
    print("SCRAPER DE RPGs - The Spriters Resource")
    print("="*60)
    
    # Plataformas a escanear
    platforms = [
        ("https://www.spriters-resource.com/nes/", "NES (8-bits)", "8bits"),
        ("https://www.spriters-resource.com/snes/", "SNES (16-bits)", "16bits"),
        ("https://www.spriters-resource.com/gameboy/", "Game Boy", "8bits"),
        ("https://www.spriters-resource.com/gba/", "Game Boy Advance", "portable"),
        ("https://www.spriters-resource.com/psx/", "PlayStation 1 (Anime)", "anime_psx"),
        ("https://www.spriters-resource.com/ps2/", "PlayStation 2 (Anime)", "anime_ps2"),
        ("https://www.spriters-resource.com/n64/", "Nintendo 64", "64bits"),
        ("https://www.spriters-resource.com/gamecube/", "GameCube", "64bits"),
        ("https://www.spriters-resource.com/wii/", "Wii", "wii"),
        ("https://www.spriters-resource.com/switch/", "Switch", "switch"),
    ]
    
    all_games = []
    
    for url, name, ptype in platforms:
        games = scan_platform(url, name, ptype)
        all_games.extend(games)
        time.sleep(1)  # Ser respetuoso con el servidor
    
    # Eliminar duplicados por URL
    seen_urls = set()
    unique_games = []
    for g in all_games:
        if g['url'] not in seen_urls:
            seen_urls.add(g['url'])
            unique_games.append(g)
    
    # Guardar resultados
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_games, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN: {len(unique_games)} RPGs únicos encontrados")
    print(f"Guardado en: {OUTPUT_FILE}")
    print(f"{'='*60}")
    
    # Mostrar lista ordenada
    print("\n" + "="*60)
    print("LISTA DE JUEGOS RPG ENCONTRADOS:")
    print("="*60)
    
    # Agrupar por tipo
    by_type = {}
    for g in unique_games:
        t = g.get('type', 'unknown')
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(g)
    
    idx = 1
    for gtype, g_list in sorted(by_type.items()):
        print(f"\n--- {gtype.upper()} ---")
        for g in sorted(g_list, key=lambda x: x['name']):
            print(f"  {idx}. {g['name']}")
            print(f"     {g['url']}")
            idx += 1

if __name__ == "__main__":
    main()