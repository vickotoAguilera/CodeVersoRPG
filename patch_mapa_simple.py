"""
Script simple para modificar src/mapa.py - Enfoque línea por línea
"""

# Leer todas las líneas
with open('src/mapa.py', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

# Encontrar la línea que contiene 'nombre_json = f"{nombre_base}.json"'
indice_insercion = None
for i, linea in enumerate(lineas):
    if 'nombre_json = f"{nombre_base}.json"' in linea:
        indice_insercion = i + 1  # Insertar después de esta línea
        break

if indice_insercion is None:
    print("[!] No se encontro la linea de referencia")
    exit(1)

# Verificar si ya está modificado
ya_modificado = False
for linea in lineas[indice_insercion:indice_insercion+5]:
    if 'mapas_unificados' in linea:
        ya_modificado = True
        break

if ya_modificado:
    print("[OK] El archivo ya esta modificado")
    exit(0)

# Crear las nuevas líneas a insertar
nuevas_lineas = [
    "        \n",
    "        # NUEVO! Primero intentar cargar archivo UNIFICADO\n",
    "        ruta_unificado = os.path.join(DATABASE_PATH, \"mapas_unificados\", f\"{nombre_base}_unificado.json\")\n",
    "        datos = None\n",
    "        \n",
    "        if os.path.exists(ruta_unificado):\n",
    "            try:\n",
    "                with open(ruta_unificado, 'r', encoding='utf-8') as f:\n",
    "                    datos = json.load(f)\n",
    "                print(f\"[UNIFICADO] Cargando desde: {ruta_unificado}\")\n",
    "            except Exception as e:\n",
    "                print(f\"[!] Error leyendo archivo unificado: {e}\")\n",
    "                print(f\"[!] Intentando con archivos parciales...\")\n",
    "                datos = None\n",
    "        \n",
    "        # Si no hay archivo unificado, usar metodo original\n",
    "        if datos is None:\n",
]

# Insertar las nuevas líneas
lineas[indice_insercion:indice_insercion] = nuevas_lineas

# Guardar el archivo modificado
with open('src/mapa.py', 'w', encoding='utf-8') as f:
    f.writelines(lineas)

print("[OK] Archivo src/mapa.py modificado exitosamente!")
print("[OK] El juego ahora cargara archivos unificados primero")
