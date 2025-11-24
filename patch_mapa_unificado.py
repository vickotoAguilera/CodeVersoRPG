"""
Script para modificar src/mapa.py y agregar soporte para archivos unificados
"""
import re

# Leer el archivo original
with open('src/mapa.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar la función cargar_datos_mapa y modificarla
# Patrón: encontrar desde "def cargar_datos_mapa" hasta el primer "try:"
patron = r'(    def cargar_datos_mapa\(self\):.*?nombre_json = f"\{nombre_base\}\.json"\s+)(.*?)(        # 2\. Abrimos y leemos el archivo JSON)'

reemplazo = r'''\1        # ¡NUEVO! Primero intentar cargar archivo UNIFICADO
        ruta_unificado = os.path.join(DATABASE_PATH, "mapas_unificados", f"{nombre_base}_unificado.json")
        datos = None
        
        if os.path.exists(ruta_unificado):
            try:
                with open(ruta_unificado, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                print(f"[UNIFICADO] ✓ Cargando desde: {ruta_unificado}")
            except Exception as e:
                print(f"[!] Error leyendo archivo unificado: {e}")
                print(f"[!] Intentando con archivos parciales...")
                datos = None
        
        # Si no hay archivo unificado, usar método original
        if datos is None:
\3'''

# Aplicar el reemplazo
contenido_modificado = re.sub(patron, reemplazo, contenido, flags=re.DOTALL)

# Verificar que se hizo el cambio
if contenido != contenido_modificado:
    # Guardar el archivo modificado
    with open('src/mapa.py', 'w', encoding='utf-8') as f:
        f.write(contenido_modificado)
    print("[OK] Archivo src/mapa.py modificado exitosamente")
    print("[OK] Ahora el juego cargara archivos unificados primero")
else:
    print("[!] No se pudo aplicar la modificacion")
    print("El patron no coincidio con el contenido del archivo")
