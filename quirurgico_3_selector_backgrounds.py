"""
Script Quirúrgico 3: Agregar Selector de Backgrounds y Renderizado

OBJETIVO:
1. Escanear carpeta backgrounds/ y listar todos los fondos disponibles
2. Crear sección desplegable para seleccionar backgrounds
3. Agregar lógica para renderizar las pantallas preview
4. Agregar manejo de clicks en toggles

CAMBIOS:
- Agregar método cargar_backgrounds()
- Agregar sección de backgrounds en panel
- Agregar método dibujar_pantallas_preview()
- Actualizar manejo de eventos para toggles
"""

def agregar_selector_backgrounds():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("AGREGANDO SELECTOR DE BACKGROUNDS Y RENDERIZADO")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Agregar método cargar_backgrounds después de cargar_sprites
    codigo_cargar_backgrounds = '''
    
    def cargar_backgrounds(self):
        """Escanea y carga todos los backgrounds disponibles"""
        self.backgrounds_disponibles = []
        
        path_backgrounds = Path("assets/backgrounds")
        if path_backgrounds.exists():
            for archivo in sorted(path_backgrounds.glob("*.png")):
                # Solo incluir los que empiezan con "pelea_"
                if archivo.stem.startswith("pelea_"):
                    self.backgrounds_disponibles.append({
                        "nombre": archivo.stem,
                        "ruta": str(archivo).replace('\\\\', '/'),
                        "archivo": archivo.name
                    })
        
        print(f"✓ Backgrounds encontrados: {len(self.backgrounds_disponibles)}")
        
        # Crear sección de backgrounds
        self.seccion_backgrounds = SeccionDesplegable(10, 210, PANEL_ANCHO - 20, "Backgrounds", (150, 100, 50))
        self.seccion_backgrounds.items = [
            SpriteInfo(bg["nombre"], bg["ruta"], "background") 
            for bg in self.backgrounds_disponibles
        ]
'''
    
    # Buscar después del método cargar_sprites
    patron_insercion = r"(print\(f\"✓ Sprites cargados: \{len\(self\.seccion_heroes\.items\)\} héroes, \{len\(self\.seccion_monstruos\.items\)\} monstruos\"\))"
    
    import re
    if re.search(patron_insercion, contenido):
        contenido = re.sub(
            patron_insercion,
            r"\1" + codigo_cargar_backgrounds,
            contenido
        )
        print("[OK] Paso 1: Método cargar_backgrounds agregado")
    else:
        print("[ADVERTENCIA] No se encontró el patrón para cargar_backgrounds")
    
    # PASO 2: Llamar a cargar_backgrounds en __init__
    codigo_viejo_init = """        # Cargar sprites
        self.cargar_sprites()"""
    
    codigo_nuevo_init = """        # Cargar sprites
        self.cargar_sprites()
        
        # Cargar backgrounds disponibles
        self.cargar_backgrounds()"""
    
    if codigo_viejo_init in contenido:
        contenido = contenido.replace(codigo_viejo_init, codigo_nuevo_init)
        print("[OK] Paso 2: Llamada a cargar_backgrounds agregada en __init__")
    else:
        print("[ADVERTENCIA] No se encontró el código de cargar sprites en __init__")
    
    # PASO 3: Agregar método para dibujar pantallas preview
    codigo_dibujar_pantallas = '''
    
    def dibujar_pantallas_preview(self, surface):
        """Dibuja las pantallas de batalla en modo preview"""
        for nombre, pantalla in self.pantallas_preview.items():
            if self.toggles_pantallas[nombre] and pantalla.visible:
                # Fondo semi-transparente
                s = pygame.Surface((pantalla.ancho, pantalla.alto))
                s.set_alpha(230)
                s.fill((30, 30, 40))
                surface.blit(s, (pantalla.x, pantalla.y))
                
                # Borde
                color_borde = COLOR_SELECCION if pantalla == self.sprite_seleccionado else COLOR_TEXTO
                pygame.draw.rect(surface, color_borde, pantalla.rect, 2, border_radius=5)
                
                # Título
                texto_titulo = self.fuente.render(pantalla.titulo, True, COLOR_TEXTO)
                surface.blit(texto_titulo, (pantalla.x + 10, pantalla.y + 10))
                
                # Indicador de "Preview Mode"
                texto_preview = self.fuente_pequena.render("(Preview - No funcional)", True, COLOR_TEXTO_SEC)
                surface.blit(texto_preview, (pantalla.x + 10, pantalla.y + 40))
                
                # Handles de redimensionamiento si está seleccionada
                if pantalla == self.sprite_seleccionado:
                    for handle_name, (hx, hy) in {
                        'nw': (pantalla.x, pantalla.y),
                        'ne': (pantalla.x + pantalla.ancho, pantalla.y),
                        'sw': (pantalla.x, pantalla.y + pantalla.alto),
                        'se': (pantalla.x + pantalla.ancho, pantalla.y + pantalla.alto)
                    }.items():
                        pygame.draw.circle(surface, COLOR_HANDLE, (int(hx), int(hy)), 6)
'''
    
    # Insertar antes del método run (al final de la clase)
    patron_run = r"(    def run\(self\):)"
    if re.search(patron_run, contenido):
        contenido = re.sub(
            patron_run,
            codigo_dibujar_pantallas + r"\1",
            contenido
        )
        print("[OK] Paso 3: Método dibujar_pantallas_preview agregado")
    else:
        print("[ADVERTENCIA] No se encontró el método run")
    
    # Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Selector de backgrounds y renderizado agregados")
    print("=" * 70)

if __name__ == "__main__":
    agregar_selector_backgrounds()
    print("\nSiguiente: Agregar manejo de eventos para toggles y backgrounds")
