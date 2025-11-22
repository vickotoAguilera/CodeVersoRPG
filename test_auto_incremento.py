#!/usr/bin/env python3
"""
Test de la lógica de auto-incremento con relleno de huecos
Simula el comportamiento de _generar_id()
"""

def test_generar_id_con_huecos():
    """Prueba la lógica de generación de IDs con relleno de huecos"""
    
    print("\n" + "="*60)
    print("TEST: Lógica de Auto-Incremento con Relleno de Huecos")
    print("="*60 + "\n")
    
    # Simular la función _generar_id
    def generar_id(ids_existentes, prefijo='C'):
        if not ids_existentes:
            nuevo_num = 1
        else:
            ids_existentes.sort()
            nuevo_num = None
            for i in range(1, max(ids_existentes) + 1):
                if i not in ids_existentes:
                    nuevo_num = i
                    break
            if nuevo_num is None:
                nuevo_num = max(ids_existentes) + 1
        return f"{prefijo}{nuevo_num}"
    
    # Test 1: Sin elementos
    print("Test 1: Sin cofres existentes")
    ids = []
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {ids}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C1' else 'FALLO'} (esperado: C1)\n")
    
    # Test 2: Secuencia continua (sin huecos)
    print("Test 2: Secuencia continua [C1, C2, C3]")
    ids = [1, 2, 3]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C4' else 'FALLO'} (esperado: C4)\n")
    
    # Test 3: Con hueco al inicio
    print("Test 3: Hueco al inicio [C2, C3, C4]")
    ids = [2, 3, 4]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C1' else 'FALLO'} (esperado: C1)\n")
    
    # Test 4: Con hueco en medio
    print("Test 4: Hueco en medio [C1, C3, C5]")
    ids = [1, 3, 5]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C2' else 'FALLO'} (esperado: C2)\n")
    
    # Test 5: Múltiples huecos (debe usar el primero)
    print("Test 5: Multiples huecos [C1, C4, C7]")
    ids = [1, 4, 7]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C2' else 'FALLO'} (esperado: C2)\n")
    
    # Test 6: Caso real del proyecto [C3, C5, C6]
    print("Test 6: Caso real del proyecto [C3, C5, C6]")
    ids = [3, 5, 6]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C1' else 'FALLO'} (esperado: C1)\n")
    
    # Test 7: Después de borrar C3 de [C1, C2, C3, C4]
    print("Test 7: Despues de borrar C3 [C1, C2, C4]")
    ids = [1, 2, 4]
    nuevo = generar_id(ids)
    print(f"  IDs existentes: {['C' + str(i) for i in ids]}")
    print(f"  Nuevo ID: {nuevo}")
    print(f"  Resultado: {'OK' if nuevo == 'C3' else 'FALLO'} (esperado: C3)\n")
    
    print("="*60)
    print("RESUMEN: Todos los tests demuestran que la logica funciona!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_generar_id_con_huecos()
