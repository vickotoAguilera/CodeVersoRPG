#!/usr/bin/env python3
"""Script para agregar la lógica de interacción con cofres a main.py"""

import sys

def add_chest_interaction():
    # Leer el archivo
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 1. Agregar variables globales después de línea 163
    insert_pos_1 = 163
    variables_code = """
# Variables de interacción con cofres
mensaje_cofre_activo = False
mensaje_cofre_texto = ""
mensaje_cofre_inicio = 0
DURACION_MENSAJE_COFRE = 3000  # 3 segundos

"""
    lines.insert(insert_pos_1, variables_code)
    
    # 2. Agregar manejador de tecla E - buscar la línea con "if event.key == pygame.K_x:"
    for i, line in enumerate(lines):
        if "if event.key == pygame.K_x:" in line and i > 500:  # Asegurar que es la correcta
            # Insertar después del bloque de K_x
            insert_pos_2 = i + 3  # Después de las 3 líneas del bloque K_x
            key_e_code = """            
            # ¡NUEVO! - Tecla E para interactuar con cofres
            if event.key == pygame.K_e:
                if estado_juego == "mapa" and mi_mapa and grupo_heroes:
                    heroe_lider = grupo_heroes[0]
                    cofre_cercano = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
                    
                    if cofre_cercano:
                        # Interactuar con el cofre
                        resultado = cofre_cercano.interactuar(grupo_heroes, ITEMS_DB)
                        
                        # Construir mensaje para mostrar
                        if resultado["exito"]:
                            items_texto = ""
                            for item_id, cantidad in resultado["items_obtenidos"].items():
                                nombre_item = ITEMS_DB.get(item_id, {}).get("nombre", item_id)
                                items_texto += f"{nombre_item} x{cantidad}, "
                            items_texto = items_texto.rstrip(", ")
                            mensaje_cofre_texto = f"¡Cofre abierto! Obtenido: {items_texto}"
                        elif "nombre_llave_necesaria" in resultado:
                            mensaje_cofre_texto = f"Cofre cerrado. Necesitas: {resultado['nombre_llave_necesaria']}"
                        else:
                            mensaje_cofre_texto = resultado["mensaje"]
                        
                        # Activar mensaje
                        mensaje_cofre_activo = True
                        mensaje_cofre_inicio = tiempo_actual_ticks
                        print(f"[Cofre] {mensaje_cofre_texto}")

"""
            lines.insert(insert_pos_2, key_e_code)
            break
    
    # 3. Agregar indicador visual - buscar la línea con "PANTALLA.blit(texto_surf, (10, 10))"
    for i, line in enumerate(lines):
        if "PANTALLA.blit(texto_surf, (10, 10))" in line:
            insert_pos_3 = i + 1
            visual_indicator_code = """            
            # Indicador de cofre cercano
            cofre_cercano = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
            if cofre_cercano:
                texto_interaccion = "Presiona E para interactuar"
                texto_surf_interaccion = mi_fuente_debug.render(texto_interaccion, True, (255, 255, 0), (0, 0, 0))
                PANTALLA.blit(texto_surf_interaccion, (ANCHO // 2 - texto_surf_interaccion.get_width() // 2, ALTO - 50))

"""
            lines.insert(insert_pos_3, visual_indicator_code)
            break
    
    # 4. Agregar dibujo del mensaje - buscar "aviso_autoguardado_activo = False"
    for i, line in enumerate(lines):
        if "aviso_autoguardado_activo = False" in line and i > 700:
            insert_pos_4 = i + 1
            message_draw_code = """
    # --- Mensaje de interacción con cofre ---
    if mensaje_cofre_activo:
        tiempo_transcurrido = tiempo_actual_ticks - mensaje_cofre_inicio
        if tiempo_transcurrido < DURACION_MENSAJE_COFRE:
            mensaje_surf = mi_fuente_debug.render(mensaje_cofre_texto, True, (255, 255, 255), (0, 0, 0))
            mensaje_rect = mensaje_surf.get_rect(center=(ANCHO // 2, 100))
            fondo_mensaje = pygame.Surface((mensaje_rect.width + 20, mensaje_rect.height + 10))
            fondo_mensaje.set_alpha(200)
            fondo_mensaje.fill((0, 0, 0))
            PANTALLA.blit(fondo_mensaje, (mensaje_rect.x - 10, mensaje_rect.y - 5))
            PANTALLA.blit(mensaje_surf, mensaje_rect)
        else:
            mensaje_cofre_activo = False

"""
            lines.insert(insert_pos_4, message_draw_code)
            break
    
    # Escribir el archivo modificado
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("[OK] Logica de interaccion con cofres agregada exitosamente")

if __name__ == "__main__":
    try:
        add_chest_interaction()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
