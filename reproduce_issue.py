import json
import sys
from pathlib import Path

# Mock ElementoMapa
class ElementoMapa:
    def __init__(self, tipo, id, x, y, ancho, alto, datos=None, puntos=None):
        self.tipo = tipo
        self.id = id
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.datos = datos or {}
        self.puntos = puntos

def cargar_portales(data):
    elementos = []
    portales_data = data.get('portales', [])
    print(f"DEBUG: Claves en JSON: {list(data.keys())}")
    if portales_data:
        print(f"DEBUG: Encontrados {len(portales_data)} portales")
    else:
        print("DEBUG: No se encontró la clave 'portales' o está vacía")
    
    for i, portal in enumerate(portales_data):
        if portal.get('forma') == 'poly' or 'puntos' in portal:
            print(f"Portal {i} es poly")
            # Simulate poly loading
            puntos = portal.get('puntos', [])
            if puntos:
                xs = [p[0] for p in puntos]
                ys = [p[1] for p in puntos]
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
                elemento = ElementoMapa('portal', f'P{i+1}', x_min, y_min, x_max - x_min, y_max - y_min, portal, puntos)
                elementos.append(elemento)
                print(f"    ✓ Portal P{i+1} (poly) cargado en bbox ({x_min}, {y_min})")
            continue

        if 'caja' in portal:
            caja = portal['caja']
            x = caja.get('x', 0)
            y = caja.get('y', 0)
            ancho = caja.get('w', 64)
            alto = caja.get('h', 64)
        else:
            x = portal.get('x', 0)
            y = portal.get('y', 0)
            ancho = portal.get('w', portal.get('ancho', 64))
            alto = portal.get('h', portal.get('alto', 64))

        elemento = ElementoMapa('portal', f'P{i+1}', x, y, ancho, alto, portal)
        elementos.append(elemento)
        print(f"    ✓ Portal P{i+1} cargado en ({x}, {y})")
    return elementos

def test_map(path):
    print(f"Testing {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        portales = cargar_portales(data)
        print(f"Total portales loaded: {len(portales)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_map(sys.argv[1])
    else:
        print("Usage: python reproduce_issue.py <path_to_json>")
