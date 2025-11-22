"""
Script Quirurgico 6b: Eliminar Emojis (sin prints problematicos)
"""

def eliminar_emojis():
    ruta_editor = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("=" * 70)
    print("ELIMINANDO EMOJIS")
    print("=" * 70)
    
    with open(ruta_editor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Eliminar emojis
    emojis_a_reemplazar = {
        "✓": "[OK]",
        "⚠️": "[ADVERTENCIA]",
        "⚠": "[ADVERTENCIA]",
        "❌": "[ERROR]",
        "✅": "[OK]",
        "▼": "v",
        "▶": ">",
        "⋮": ":",
    }
    
    contador = 0
    for emoji, reemplazo in emojis_a_reemplazar.items():
        if emoji in contenido:
            contenido = contenido.replace(emoji, reemplazo)
            contador += 1
    
    print(f"[OK] {contador} tipos de emojis reemplazados")
    
    # Guardar
    with open(ruta_editor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("[EXITO] Emojis eliminados")
    print("=" * 70)

if __name__ == "__main__":
    eliminar_emojis()
