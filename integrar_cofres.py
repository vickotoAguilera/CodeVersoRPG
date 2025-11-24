#!/usr/bin/env python3
"""
Script para integrar el sistema de cofres en main.py de forma segura
"""

# Leer el archivo
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Agregar import (después de línea 19)
for i, line in enumerate(lines):
    if 'from src.pantalla_habilidades import PantallaHabilidades' in line:
        lines.insert(i + 1, 'from src.pantalla_cofre import PantallaCofre  # ¡NUEVO! Sistema de cofres\n')
        break

# 2. Agregar variables globales (después de línea 80)
for i, line in enumerate(lines):
    if 'mi_pantalla_habilidades = None  # ¡NUEVO! (Paso 7.18)' in line:
        lines.insert(i + 1, 'mi_pantalla_cofre = None  # ¡NUEVO! Sistema de cofres\n')
        lines.insert(i + 2, 'cofre_cercano_actual = None  # ¡NUEVO! Cofre detectado cerca del héroe\n')
        break

# 3. Agregar manejo de ESC para pantalla cofre (después del bloque de pantalla_habilidades)
for i, line in enumerate(lines):
    if '# --- FIN BLOQUE CORREGIDO ---' in line and i > 200 and i < 250:
        # Insertar antes del FIN BLOQUE CORREGIDO
        insert_lines = [
            '                \n',
            '                # ¡NUEVO! - Manejo de ESC en pantalla cofre\n',
            '                elif estado_juego == "pantalla_cofre" and mi_pantalla_cofre:\n',
            '                    accion_cofre = mi_pantalla_cofre.update_input(event.key)\n',
            '                    if accion_cofre == "cerrar":\n',
            '                        print("Cerrando pantalla de cofre")\n',
            '                        if cofre_cercano_actual:\n',
            '                            cofre_cercano_actual.abierto = True\n',
            '                            cofre_cercano_actual.actualizar_sprite()\n',
            '                        estado_juego = "mapa"\n',
            '                        mi_pantalla_cofre = None\n',
        ]
        for j, insert_line in enumerate(insert_lines):
            lines.insert(i + j, insert_line)
        break

# 4. Agregar manejo de tecla E (después del bloque de tecla X)
for i, line in enumerate(lines):
    if 'if event.key == pygame.K_x:' in line and 'pantalla_habilidades' in lines[i+1]:
        # Buscar el final de este bloque
        j = i + 1
        while j < len(lines) and (lines[j].startswith('                ') or lines[j].strip() == ''):
            j += 1
        # Insertar después
        insert_lines = [
            '\n',
            '            # ¡NUEVO! Tecla E para interactuar con cofres\n',
            '            if event.key == pygame.K_e:\n',
            '                if estado_juego == "mapa" and cofre_cercano_actual:\n',
            '                    if not cofre_cercano_actual.abierto:\n',
            '                        print(f"Abriendo cofre: {cofre_cercano_actual.id_cofre}")\n',
            '                        estado_juego = "pantalla_cofre"\n',
            '                        mi_pantalla_cofre = PantallaCofre(\n',
            '                            ANCHO, ALTO,\n',
            '                            cofre_cercano_actual,\n',
            '                            grupo_heroes,\n',
            '                            ITEMS_DB,\n',
            '                            CURSOR_IMG\n',
            '                        )\n',
        ]
        for k, insert_line in enumerate(insert_lines):
            lines.insert(j + k, insert_line)
        break

# 5. Agregar update loop para pantalla_cofre (después de pantalla_habilidades)
for i, line in enumerate(lines):
    if 'elif estado_juego == "pantalla_habilidades":' in line and 'mi_pantalla_habilidades.update(teclas)' in lines[i+1]:
        insert_lines = [
            '    # ¡NUEVO! Sistema de cofres\n',
            '    elif estado_juego == "pantalla_cofre":\n',
            '        if mi_pantalla_cofre: mi_pantalla_cofre.update(teclas)\n',
        ]
        for j, insert_line in enumerate(insert_lines):
            lines.insert(i + 2 + j, insert_line)
        break

# 6. Agregar detección de cofre cercano (después de chequear_zona)
for i, line in enumerate(lines):
    if 'zona_actual = mi_mapa.chequear_zona(heroe_lider.heroe_rect)' in line:
        lines.insert(i + 1, '            \n')
        lines.insert(i + 2, '            # ¡NUEVO! Detectar cofre cercano\n')
        lines.insert(i + 3, '            cofre_cercano_actual = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)\n')
        break

# 7. Agregar indicador visual en draw loop (después de dibujar coords)
for i, line in enumerate(lines):
    if 'PANTALLA.blit(texto_surf, (10, 10))' in line and i > 700:
        insert_lines = [
            '            \n',
            '            # ¡NUEVO! Indicador de proximidad al cofre\n',
            '            if cofre_cercano_actual and not cofre_cercano_actual.abierto:\n',
            '                fuente_indicador = pygame.font.Font(None, 24)\n',
            '                texto = fuente_indicador.render("Presiona E para abrir", True, (255, 255, 255))\n',
            '                # Posicionar sobre el cofre\n',
            '                cofre_screen_x = cofre_cercano_actual.rect.centerx - mi_mapa.camara_rect.x\n',
            '                cofre_screen_y = cofre_cercano_actual.rect.top - mi_mapa.camara_rect.y - 30\n',
            '                texto_rect = texto.get_rect(center=(cofre_screen_x, cofre_screen_y))\n',
            '                # Fondo semi-transparente\n',
            '                fondo = pygame.Surface((texto_rect.width + 10, texto_rect.height + 6))\n',
            '                fondo.set_alpha(180)\n',
            '                fondo.fill((0, 0, 0))\n',
            '                PANTALLA.blit(fondo, (texto_rect.x - 5, texto_rect.y - 3))\n',
            '                PANTALLA.blit(texto, texto_rect)\n',
        ]
        for j, insert_line in enumerate(insert_lines):
            lines.insert(i + 1 + j, insert_line)
        break

# 8. Agregar draw de pantalla cofre (después de FIN BLOQUE CORREGIDO en draw)
for i, line in enumerate(lines):
    if '# --- FIN BLOQUE CORREGIDO ---' in line and i > 750:
        insert_lines = [
            '    \n',
            '    # ¡NUEVO! Pantalla de cofre\n',
            '    elif estado_juego == "pantalla_cofre":\n',
            '        # Dibujar fondo (mapa pausado)\n',
            '        if mi_mapa and grupo_heroes:\n',
            '            heroe_lider = grupo_heroes[0]\n',
            '            mi_mapa.draw(PANTALLA)\n',
            '            heroe_lider.draw(PANTALLA, mi_mapa.camara_rect)\n',
            '        # Dibujar pantalla de cofre encima\n',
            '        if mi_pantalla_cofre:\n',
            '            mi_pantalla_cofre.draw(PANTALLA)\n',
        ]
        for j, insert_line in enumerate(insert_lines):
            lines.insert(i + 1 + j, insert_line)
        break

# Escribir el archivo modificado
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("[OK] Integración de sistema de cofres completada")
print("Cambios aplicados:")
print("  1. Import de PantallaCofre")
print("  2. Variables globales (mi_pantalla_cofre, cofre_cercano_actual)")
print("  3. Manejo de ESC en pantalla cofre")
print("  4. Manejo de tecla E para abrir cofres")
print("  5. Update loop para pantalla cofre")
print("  6. Detección de cofre cercano en game loop")
print("  7. Indicador visual de proximidad")
print("  8. Draw de pantalla cofre")
