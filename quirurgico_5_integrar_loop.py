"""
Script Quirúrgico 5 (FINAL): Integrar Renderizado en Loop Principal

OBJETIVO:
Agregar la llamada a dibujar_pantallas_preview() en el loop principal
justo después de dibujar el área de batalla

CAMBIOS:
- Insertar llamada en el método ejecutar()
"""

def integrar_renderizado_final():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("INTEGRANDO RENDERIZADO EN LOOP PRINCIPAL")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar e insertar después de dibujar_area_batalla
    codigo_viejo = """            # Área de batalla
            area_batalla = self.pantalla.subsurface((PANEL_ANCHO, 0, AREA_BATALLA_ANCHO, ALTO))
            self.dibujar_area_batalla(area_batalla)
            
            # Sprite fantasma durante drag"""
    
    codigo_nuevo = """            # Área de batalla
            area_batalla = self.pantalla.subsurface((PANEL_ANCHO, 0, AREA_BATALLA_ANCHO, ALTO))
            self.dibujar_area_batalla(area_batalla)
            
            # Pantallas preview (sobre el área de batalla)
            self.dibujar_pantallas_preview(self.pantalla)
            
            # Sprite fantasma durante drag"""
    
    if codigo_viejo in contenido:
        contenido = contenido.replace(codigo_viejo, codigo_nuevo)
        print("[OK] Llamada a dibujar_pantallas_preview agregada en loop principal")
    else:
        print("[ADVERTENCIA] No se encontró el patrón exacto")
    
    # Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n[EXITO] Integración completada")
    print("=" * 70)
    print("\n✓ El editor ahora debería mostrar las pantallas preview")
    print("✓ Falta: Agregar manejo de clicks en toggles para activar/desactivar")

if __name__ == "__main__":
    integrar_renderizado_final()
