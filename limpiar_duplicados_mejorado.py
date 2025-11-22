#!/usr/bin/env python3
"""
Script mejorado para eliminar bloques duplicados específicos en main.py
"""

# Leer el archivo
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Contar ocurrencias antes
original_length = len(content)

# Eliminar duplicados específicos manteniendo solo la primera ocurrencia

# 1. Eliminar segunda detección de cofre cercano (líneas ~732-733)
content = content.replace(
    """            
            # ¡NUEVO! Detectar cofre cercano
            cofre_cercano_actual = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
            
            # ¡NUEVO! Detectar cofre cercano
            cofre_cercano_actual = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
            """,
    """            
            # ¡NUEVO! Detectar cofre cercano
            cofre_cercano_actual = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
            """
)

# 2. Eliminar segunda tecla E para cofres (líneas ~604-616)
# Buscar el patrón duplicado
pattern_e_key = """            # ¡NUEVO! Tecla E para interactuar con cofres
            if event.key == pygame.K_e:
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
                        )"""

# Contar cuántas veces aparece
count = content.count(pattern_e_key)
if count > 1:
    # Encontrar la posición de la segunda ocurrencia y eliminarla
    first_pos = content.find(pattern_e_key)
    second_pos = content.find(pattern_e_key, first_pos + 1)
    if second_pos != -1:
        # Eliminar desde second_pos hasta el final del bloque
        end_pos = second_pos + len(pattern_e_key)
        content = content[:second_pos] + content[end_pos:]

# 3. Eliminar segundo bloque de pantalla_cofre update (líneas ~638-640)
content = content.replace(
    """    # ¡NUEVO! Sistema de cofres
    elif estado_juego == "pantalla_cofre":
        if mi_pantalla_cofre: mi_pantalla_cofre.update(teclas)
    # ¡NUEVO! Sistema de cofres
    elif estado_juego == "pantalla_cofre":
        if mi_pantalla_cofre: mi_pantalla_cofre.update(teclas)
    """,
    """    # ¡NUEVO! Sistema de cofres
    elif estado_juego == "pantalla_cofre":
        if mi_pantalla_cofre: mi_pantalla_cofre.update(teclas)
    """
)

# 4. Eliminar segundo indicador de proximidad (líneas ~790-803)
pattern_indicator = """            
            # ¡NUEVO! Indicador de proximidad al cofre
            if cofre_cercano_actual and not cofre_cercano_actual.abierto:
                fuente_indicador = pygame.font.Font(None, 24)
                texto = fuente_indicador.render("Presiona E para abrir", True, (255, 255, 255))
                # Posicionar sobre el cofre
                cofre_screen_x = cofre_cercano_actual.rect.centerx - mi_mapa.camara_rect.x
                cofre_screen_y = cofre_cercano_actual.rect.top - mi_mapa.camara_rect.y - 30
                texto_rect = texto.get_rect(center=(cofre_screen_x, cofre_screen_y))
                # Fondo semi-transparente
                fondo = pygame.Surface((texto_rect.width + 10, texto_rect.height + 6))
                fondo.set_alpha(180)
                fondo.fill((0, 0, 0))
                PANTALLA.blit(fondo, (texto_rect.x - 5, texto_rect.y - 3))
                PANTALLA.blit(texto, texto_rect)"""

count_indicator = content.count(pattern_indicator)
if count_indicator > 1:
    first_pos = content.find(pattern_indicator)
    second_pos = content.find(pattern_indicator, first_pos + 1)
    if second_pos != -1:
        end_pos = second_pos + len(pattern_indicator)
        content = content[:second_pos] + content[end_pos:]

# 5. Eliminar segundo bloque de dibujo de pantalla cofre (líneas ~853-862)
pattern_draw_chest = """    
    # ¡NUEVO! Pantalla de cofre
    elif estado_juego == "pantalla_cofre":
        # Dibujar fondo (mapa pausado)
        if mi_mapa and grupo_heroes:
            heroe_lider = grupo_heroes[0]
            mi_mapa.draw(PANTALLA)
            heroe_lider.draw(PANTALLA, mi_mapa.camara_rect)
        # Dibujar pantalla de cofre encima
        if mi_pantalla_cofre:
            mi_pantalla_cofre.draw(PANTALLA)"""

count_draw = content.count(pattern_draw_chest)
if count_draw > 1:
    first_pos = content.find(pattern_draw_chest)
    second_pos = content.find(pattern_draw_chest, first_pos + 1)
    if second_pos != -1:
        end_pos = second_pos + len(pattern_draw_chest)
        content = content[:second_pos] + content[end_pos:]

# Escribir el archivo limpio
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

new_length = len(content)
chars_removed = original_length - new_length

print(f"[OK] Limpieza completada")
print(f"  Caracteres originales: {original_length}")
print(f"  Caracteres después: {new_length}")
print(f"  Caracteres eliminados: {chars_removed}")
