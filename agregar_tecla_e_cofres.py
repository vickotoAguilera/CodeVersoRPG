#!/usr/bin/env python3
"""
Script para agregar el manejo de la tecla E para cofres en main.py
"""

# Leer el archivo
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea donde está "# ¡NUEVO! (Paso 7.18) - Tecla X para desequipar habilidades"
insert_index = None
for i, line in enumerate(lines):
    if "# ¡NUEVO! (Paso 7.18) - Tecla X para desequipar habilidades" in line:
        # Encontrar el final del bloque de tecla X (4 líneas después)
        insert_index = i + 4
        break

if insert_index is None:
    print("[ERROR] No se encontró el bloque de tecla X")
    exit(1)

# Código a insertar
codigo_nuevo = """            
            # ¡NUEVO! - Tecla E para interactuar con cofres
            if event.key == pygame.K_e:
                # Abrir cofre desde el mapa
                if estado_juego == "mapa" and cofre_cercano_actual:
                    if not cofre_cercano_actual.abierto:
                        print(f"Abriendo cofre: {cofre_cercano_actual.id_cofre}")
                        estado_juego = "pantalla_cofre"
                        mi_pantalla_cofre = PantallaCofre(
                            ANCHO, ALTO,
                            cofre_cercano_actual,
                            grupo_heroes,
                            ITEMS_DB,
                            CURSOR_IMG
                        )
                # Tomar items o cerrar desde la pantalla de cofre
                elif estado_juego == "pantalla_cofre" and mi_pantalla_cofre:
                    accion_cofre = mi_pantalla_cofre.update_input(event.key)
                    if accion_cofre == "cerrar":
                        print("Cerrando pantalla de cofre")
                        if cofre_cercano_actual:
                            cofre_cercano_actual.abierto = True
                            cofre_cercano_actual.actualizar_sprite()
                        estado_juego = "mapa"
                        mi_pantalla_cofre = None
            
            # ¡NUEVO! - Navegación con flechas en pantalla de cofre
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                if estado_juego == "pantalla_cofre" and mi_pantalla_cofre:
                    mi_pantalla_cofre.update_input(event.key)

"""

# Insertar el código
lines.insert(insert_index, codigo_nuevo)

# Escribir el archivo
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"[OK] Código agregado en la línea {insert_index + 1}")
print("[OK] Sistema de cofres completado")
