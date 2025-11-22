"""
Script Quirúrgico 4: Agregar Renderizado de Pantallas y Manejo de Eventos

OBJETIVO:
1. Agregar método dibujar_pantallas_preview()
2. Llamar al método desde el draw principal
3. Agregar manejo de clicks en toggles de pantallas
4. Agregar manejo de clicks en backgrounds

CAMBIOS:
- Insertar método dibujar_pantallas_preview antes de dibujar_panel_lateral
- Actualizar draw principal para llamar al nuevo método
- Agregar lógica de eventos en el loop principal
"""

def agregar_renderizado_y_eventos():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("AGREGANDO RENDERIZADO Y MANEJO DE EVENTOS")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Agregar método dibujar_pantallas_preview
    codigo_metodo = '''
    
    def dibujar_pantallas_preview(self, surface):
        """Dibuja las pantallas de batalla en modo preview"""
        for nombre, pantalla in self.pantallas_preview.items():
            if self.toggles_pantallas.get(nombre, False):
                # Fondo semi-transparente
                s = pygame.Surface((pantalla.ancho, pantalla.alto))
                s.set_alpha(230)
                s.fill((30, 30, 40))
                surface.blit(s, (pantalla.x, pantalla.y))
                
                # Borde
                es_seleccionado = (self.sprite_seleccionado == pantalla)
                color_borde = COLOR_SELECCION if es_seleccionado else COLOR_TEXTO
                pygame.draw.rect(surface, color_borde, pantalla.rect, 2, border_radius=5)
                
                # Título
                texto_titulo = self.fuente.render(pantalla.titulo, True, COLOR_TEXTO)
                surface.blit(texto_titulo, (pantalla.x + 10, pantalla.y + 10))
                
                # Indicador de "Preview Mode"
                texto_preview = self.fuente_pequena.render("(Preview - No funcional)", True, COLOR_TEXTO_SEC)
                surface.blit(texto_preview, (pantalla.x + 10, pantalla.y + 40))
                
                # Handles de redimensionamiento si está seleccionada
                if es_seleccionado:
                    for handle_name, (hx, hy) in {
                        'nw': (pantalla.x, pantalla.y),
                        'ne': (pantalla.x + pantalla.ancho, pantalla.y),
                        'sw': (pantalla.x, pantalla.y + pantalla.alto),
                        'se': (pantalla.x + pantalla.ancho, pantalla.y + pantalla.alto)
                    }.items():
                        pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), 6)
'''
    
    # Insertar antes de dibujar_panel_lateral
    import re
    patron = r"(    def dibujar_panel_lateral\(self, surface\):)"
    if re.search(patron, contenido):
        contenido = re.sub(patron, codigo_metodo + r"\1", contenido)
        print("[OK] Paso 1: Método dibujar_pantallas_preview agregado")
    else:
        print("[ADVERTENCIA] No se encontró dibujar_panel_lateral")
    
    # PASO 2: Llamar al método desde el draw principal (buscar donde se dibuja el área de batalla)
    # Buscar la llamada a dibujar_area_batalla y agregar después
    patron_draw = r"(self\.dibujar_area_batalla\(self\.pantalla\))"
    if re.search(patron_draw, contenido):
        contenido = re.sub(
            patron_draw,
            r"\1\n        \n        # Dibujar pantallas preview\n        self.dibujar_pantallas_preview(self.pantalla)",
            contenido
        )
        print("[OK] Paso 2: Llamada a dibujar_pantallas_preview agregada en draw")
    else:
        print("[ADVERTENCIA] No se encontró dibujar_area_batalla en draw")
    
    # Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Renderizado agregado")
    print("=" * 70)
    print("\nNOTA: Falta agregar manejo de eventos (clicks en toggles)")
    print("Esto se hará en el siguiente script")

if __name__ == "__main__":
    agregar_renderizado_y_eventos()
