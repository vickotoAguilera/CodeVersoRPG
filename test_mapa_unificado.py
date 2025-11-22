#!/usr/bin/env python3
"""Test para verificar que el mapa carga correctamente desde el archivo unificado"""
import pygame
import sys
sys.path.insert(0, 'src')

# Inicializar pygame con ventana
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Importar y crear mapa
from mapa import Mapa

print("\n" + "="*60)
print("TEST: Cargando mapa desde archivo unificado")
print("="*60 + "\n")

try:
    mi_mapa = Mapa("mapa_pradera.jpg", "mundo", 1280, 720)
    
    print("\n" + "="*60)
    print("RESULTADOS DEL TEST")
    print("="*60)
    print(f"✓ Portales cargados: {len(mi_mapa.portales)}")
    print(f"✓ Cofres cargados: {len(mi_mapa.cofres)}")
    print(f"✓ Muros cargados: {len(mi_mapa.muros)}")
    print(f"✓ Spawns cargados: {len(mi_mapa.spawns)}")
    print("="*60)
    
    # Verificar que los portales tienen datos
    if len(mi_mapa.portales) > 0:
        print(f"\n[OK] Portal 1: destino = {mi_mapa.portales[0].get('mapa_destino')}")
    
    # Verificar que los cofres tienen datos
    if len(mi_mapa.cofres) > 0:
        print(f"[OK] Cofre 1: ID = {mi_mapa.cofres[0].id_cofre}")
    
    print("\n[EXITO] El mapa se cargó correctamente desde el archivo unificado!\n")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
