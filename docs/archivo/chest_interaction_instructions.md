# Instrucciones para agregar interacción con cofres a main.py

## 1. Agregar variables globales (después de la línea 163):

```python
# Variables de interacción con cofres
mensaje_cofre_activo = False
mensaje_cofre_texto = ""
mensaje_cofre_inicio = 0
DURACION_MENSAJE_COFRE = 3000  # 3 segundos
```

## 2. Agregar manejador de tecla E (después de la línea 571, dentro del bloque `if event.type == pygame.KEYDOWN:`):

```python
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
```

## 3. Agregar indicador visual de cofre cercano (en la sección de dibujo del mapa, después de la línea 717):

```python
            # Indicador de cofre cercano
            cofre_cercano = mi_mapa.chequear_cofre_cercano(heroe_lider.heroe_rect)
            if cofre_cercano:
                texto_interaccion = "Presiona E para interactuar"
                texto_surf_interaccion = mi_fuente_debug.render(texto_interaccion, True, (255, 255, 0), (0, 0, 0))
                PANTALLA.blit(texto_surf_interaccion, (ANCHO // 2 - texto_surf_interaccion.get_width() // 2, ALTO - 50))
```

## 4. Agregar dibujo del mensaje de cofre (después del bloque de autoguardado, línea 771):

```python
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
```
