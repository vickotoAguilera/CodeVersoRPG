"""
Script Quirúrgico 2: Agregar Instancias de Pantallas y Toggles

OBJETIVO:
Agregar en el __init__ del EditorBatalla las instancias de las pantallas reales
y crear toggles (checkboxes) para mostrar/ocultar cada pantalla

CAMBIOS:
1. Agregar variables de control para cada pantalla
2. Crear instancias preview de las pantallas
3. Agregar checkboxes en el panel lateral
4. Actualizar método draw para renderizar pantallas
"""

def agregar_instancias_pantallas():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("AGREGANDO INSTANCIAS DE PANTALLAS Y TOGGLES")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # PASO 1: Agregar variables de control en __init__ (después de ventana_emulador)
    codigo_viejo = """        # Ventanas adicionales
        self.ventana_magia = VentanaMagia()
        self.ventana_emulador = VentanaEmuladorBatalla()
        self.mostrar_ventana_magia = False
        self.mostrar_ventana_emulador = False"""
    
    codigo_nuevo = """        # Ventanas adicionales (LEGACY - mantener por compatibilidad)
        self.ventana_magia = VentanaMagia()
        self.ventana_emulador = VentanaEmuladorBatalla()
        self.mostrar_ventana_magia = False
        self.mostrar_ventana_emulador = False
        
        # Pantallas reales de batalla (NUEVO)
        self.pantallas_preview = {
            "magia": PantallaPreview(100, 100, 400, 300, "Pantalla Magia"),
            "items": PantallaPreview(520, 100, 400, 300, "Pantalla Items"),
            "victoria": PantallaPreview(100, 420, 600, 350, "Pantalla Victoria"),
            "habilidades": PantallaPreview(720, 420, 400, 300, "Pantalla Habilidades")
        }
        
        # Toggles para mostrar/ocultar pantallas
        self.toggles_pantallas = {
            "magia": False,
            "items": False,
            "victoria": False,
            "habilidades": False
        }"""
    
    if codigo_viejo in contenido:
        contenido = contenido.replace(codigo_viejo, codigo_nuevo)
        print("[OK] Paso 1: Variables de control agregadas")
    else:
        print("[ADVERTENCIA] No se encontró el código de ventanas adicionales")
    
    # PASO 2: Agregar sección de toggles en el panel lateral
    # Buscar donde agregar (después de la sección de monstruos)
    codigo_seccion_toggles = """
        
        # Sección de pantallas (toggles)
        self.seccion_pantallas = SeccionDesplegable(10, 160, PANEL_ANCHO - 20, "Pantallas", (100, 50, 150))
        self.seccion_pantallas.items = [
            SpriteInfo("Pantalla Magia", "toggle_magia", "toggle"),
            SpriteInfo("Pantalla Items", "toggle_items", "toggle"),
            SpriteInfo("Pantalla Victoria", "toggle_victoria", "toggle"),
            SpriteInfo("Pantalla Habilidades", "toggle_habilidades", "toggle")
        ]"""
    
    # Buscar después de self.seccion_monstruos
    patron_insercion = r"(self\.seccion_monstruos = SeccionDesplegable\(10, 110, PANEL_ANCHO - 20, \"Monstruos\", \(200, 50, 50\)\))"
    
    import re
    if re.search(patron_insercion, contenido):
        contenido = re.sub(
            patron_insercion,
            r"\1" + codigo_seccion_toggles,
            contenido
        )
        print("[OK] Paso 2: Sección de pantallas agregada")
    else:
        print("[ADVERTENCIA] No se encontró el patrón de inserción")
    
    # Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Instancias y toggles agregados")
    print("=" * 70)

if __name__ == "__main__":
    agregar_instancias_pantallas()
    print("\nSiguiente: Agregar lógica de renderizado de pantallas")
