"""
Script quirurgico 2/3: Modificar src/cofre.py - _cargar_sprites
Eliminar logica de escalado y usar resize directo al tamano deseado
"""

import re

def aplicar_cambios():
    print("=" * 70)
    print("SCRIPT 2/3: Modificar _cargar_sprites - Sistema 1:1")
    print("=" * 70)
    
    with open('src/cofre.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # CAMBIO: Reemplazar toda la logica de escalado
    print("\n[1/1] Reemplazando logica de escalado...")
    
    # Buscar el bloque de escalado
    patron = r'# Escalar si es necesario\s+if self\.escala != 1\.0:.*?self\.sprite_vacio = sprite_abierto  # Usar mismo sprite para vacío'
    
    reemplazo = '''# Redimensionar al tamaño deseado
                sprite_cerrado = pygame.transform.scale(
                    sprite_cerrado,
                    (self.ancho_deseado, self.alto_deseado)
                )
                sprite_abierto = pygame.transform.scale(
                    sprite_abierto,
                    (self.ancho_deseado, self.alto_deseado)
                )
                
                self.sprite_cerrado = sprite_cerrado
                self.sprite_abierto = sprite_abierto
                self.sprite_vacio = sprite_abierto  # Usar mismo sprite para vacio'''
    
    contenido = re.sub(patron, reemplazo, contenido, flags=re.DOTALL)
    
    if contenido != contenido_original:
        print("   [OK] Logica de escalado reemplazada")
    else:
        print("   [ERROR] No se pudo reemplazar la logica")
        return False
    
    # Guardar
    with open('src/cofre.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[OK] Archivo guardado")
    print("\n" + "=" * 70)
    return True

if __name__ == "__main__":
    try:
        exito = aplicar_cambios()
        if not exito:
            print("[!] Revisa manualmente el archivo")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
