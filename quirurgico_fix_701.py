"""
Script Quirurgico FINAL: Arreglar linea 701
"""

def arreglar_linea_701():
    ruta = r"c:\Users\vicko\Documents\RPG\editor_batalla.py"
    
    print("Arreglando linea 701...")
    
    with open(ruta, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    
    # Arreglar linea 701 (indice 700)
    if len(lineas) > 700:
        linea_vieja = lineas[700]
        if "replace('\\\\'," in linea_vieja or "replace('\\'," in linea_vieja:
            # Reemplazar con la version correcta
            lineas[700] = "                        \"ruta\": str(archivo).replace('\\\\\\\\', '/'),\\r\\n"
            print("[OK] Linea 701 arreglada")
        else:
            print(f"[INFO] Linea 701 actual: {linea_vieja.strip()}")
    
    with open(ruta, 'w', encoding='utf-8') as f:
        f.writelines(lineas)
    
    print("[EXITO] Archivo guardado")

if __name__ == "__main__":
    arreglar_linea_701()
