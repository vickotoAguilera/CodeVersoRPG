#!/usr/bin/env python3
"""
Script para aplicar Fix #1 y #2 a mapa.py
"""
import re

# Leer el archivo original
with open('src/mapa.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix #1: Reemplazar la función cargar_datos_mapa para buscar primero en mapas_unificados
old_cargar_datos = '''    # --- ¡MODIFICADO! "EL MOTOR" PARA LEER JSON ---
    def cargar_datos_mapa(self):
        # 1. Averiguamos el nombre del archivo JSON (igual que antes)
        nombre_base = os.path.splitext(self.nombre_archivo)[0]
        nombre_json = f"{nombre_base}.json"
        
        # ¡MODIFICADO! ¡Ahora busca el JSON en la sub-carpeta correcta!
        ruta_json = os.path.join(DATABASE_PATH, "mapas", self.categoria, nombre_json)
        
        print(f"Buscando datos del mapa en: {ruta_json}")

        # 2. Abrimos y leemos el archivo JSON (igual que antes)
        try:
            # --- ¡MODIFICADO! Añadimos encoding='utf-8' ---
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except FileNotFoundError:
            # Intentar resolver mediante el índice maps_index.json si existe
            ruta_indice = os.path.join(DATABASE_PATH, 'maps_index.json')
            datos = None
            if os.path.exists(ruta_indice):
                try:
                    with open(ruta_indice, 'r', encoding='utf-8') as fi:
                        entradas = json.load(fi)
                    for e in entradas:
                        # buscar por id o por nombre base
                        if e.get('id') == nombre_base or os.path.splitext(os.path.basename(e.get('ruta_json','')))[0] == nombre_base:
                            posible = e.get('ruta_json')
                            if posible and os.path.exists(posible):
                                try:
                                    with open(posible, 'r', encoding='utf-8') as f:
                                        datos = json.load(f)
                                    print(f"Cargado JSON desde índice: {posible}")
                                    break
                                except Exception:
                                    datos = None
                except Exception:
                    datos = None

            if datos is None:
                print(f"¡ADVERTENCIA! No se encontró el archivo de datos: {ruta_json}")
                print("El mapa se cargará vacío (sin muros, portales, etc.)")
                return
        except json.JSONDecodeError:
            print(f"¡ERROR! El archivo JSON está mal escrito: {ruta_json}")
            pygame.quit(); sys.exit()'''

new_cargar_datos = '''    # --- ¡MODIFICADO! "EL MOTOR" PARA LEER JSON ---
    def cargar_datos_mapa(self):
        # 1. Averiguamos el nombre del archivo JSON
        nombre_base = os.path.splitext(self.nombre_archivo)[0]
        
        # ¡NUEVO! PRIORIDAD 1: Intentar cargar desde mapas_unificados/
        nombre_unificado = f"{nombre_base}_unificado.json"
        ruta_unificado = os.path.join(DATABASE_PATH, "mapas_unificados", nombre_unificado)
        
        datos = None
        ruta_cargada = None
        
        # Intentar cargar archivo unificado primero
        if os.path.exists(ruta_unificado):
            try:
                with open(ruta_unificado, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                ruta_cargada = ruta_unificado
                print(f"[UNIFICADO] Cargando desde: {ruta_unificado}")
            except json.JSONDecodeError as e:
                print(f"¡ERROR! Archivo unificado mal formado: {ruta_unificado}")
                print(f"  Error: {e}")
                datos = None
            except Exception as e:
                print(f"¡ERROR! No se pudo leer archivo unificado: {e}")
                datos = None
        
        # PRIORIDAD 2: Si no hay archivo unificado, buscar en mapas/{categoria}/
        if datos is None:
            nombre_json = f"{nombre_base}.json"
            ruta_json = os.path.join(DATABASE_PATH, "mapas", self.categoria, nombre_json)
            
            if os.path.exists(ruta_json):
                try:
                    with open(ruta_json, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    ruta_cargada = ruta_json
                    print(f"[PARCIAL] Cargando desde: {ruta_json}")
                except json.JSONDecodeError as e:
                    print(f"¡ERROR! El archivo JSON está mal escrito: {ruta_json}")
                    print(f"  Error: {e}")
                    pygame.quit(); sys.exit()
                except Exception as e:
                    print(f"¡ERROR! No se pudo leer: {e}")
                    datos = None
        
        # PRIORIDAD 3: Intentar resolver mediante el índice maps_index.json
        if datos is None:
            ruta_indice = os.path.join(DATABASE_PATH, 'maps_index.json')
            if os.path.exists(ruta_indice):
                try:
                    with open(ruta_indice, 'r', encoding='utf-8') as fi:
                        entradas = json.load(fi)
                    for e in entradas:
                        if e.get('id') == nombre_base or os.path.splitext(os.path.basename(e.get('ruta_json','')))[0] == nombre_base:
                            posible = e.get('ruta_json')
                            if posible and os.path.exists(posible):
                                try:
                                    with open(posible, 'r', encoding='utf-8') as f:
                                        datos = json.load(f)
                                    ruta_cargada = posible
                                    print(f"[INDICE] Cargado desde índice: {posible}")
                                    break
                                except Exception:
                                    datos = None
                except Exception as e:
                    print(f"[!] Error leyendo maps_index.json: {e}")
        
        # Si no se encontró ningún archivo, advertir y salir
        if datos is None:
            print(f"¡ADVERTENCIA! No se encontró archivo de datos para '{nombre_base}'")
            print(f"  Intentado:")
            print(f"    1. {ruta_unificado}")
            if 'ruta_json' in locals():
                print(f"    2. {ruta_json}")
            print(f"    3. Índice de mapas")
            print("El mapa se cargará vacío (sin muros, portales, etc.)")
            return'''

# Aplicar Fix #1
content = content.replace(old_cargar_datos, new_cargar_datos)

# Fix #2: Consolidar items de cofres
old_cofre_creation = '''                # Buscar datos del cofre en la base de datos
                cofre_info = self.cofres_db.get("cofres_mapa", {}).get(id_cofre) or self.cofres_db.get(id_cofre)
                if cofre_info:
                    # ¡NUEVO! Obtener sprites desde la base de datos
                    sprite_cerrado = cofre_info.get("sprite_cerrado")
                    sprite_abierto = cofre_info.get("sprite_abierto")
                    
                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=cofre_info.get("items_contenido", {}),
                        escala=escala,
                        sprite_cerrado=sprite_cerrado,  # ¡NUEVO!
                        sprite_abierto=sprite_abierto   # ¡NUEVO!
                    )
                    self.cofres.append(nuevo_cofre)
                else:
                    print(f"¡ADVERTENCIA! Cofre '{id_cofre}' no encontrado en cofres_db.json")'''

new_cofre_creation = '''                # Buscar datos del cofre en la base de datos
                cofre_info = self.cofres_db.get("cofres_mapa", {}).get(id_cofre) or self.cofres_db.get(id_cofre)
                if cofre_info:
                    # ¡NUEVO! Obtener sprites desde la base de datos
                    sprite_cerrado = cofre_info.get("sprite_cerrado")
                    sprite_abierto = cofre_info.get("sprite_abierto")
                    
                    # ¡FIX #2! Consolidar los 3 tipos de items en un solo diccionario
                    items_consolidados = {}
                    
                    # Agregar items consumibles
                    if "items_contenido" in cofre_info:
                        items_consolidados.update(cofre_info["items_contenido"])
                    
                    # Agregar items de equipo
                    if "equipo_contenido" in cofre_info:
                        items_consolidados.update(cofre_info["equipo_contenido"])
                    
                    # Agregar items especiales
                    if "especiales_contenido" in cofre_info:
                        items_consolidados.update(cofre_info["especiales_contenido"])
                    
                    print(f"  [OK] Cofre '{id_cofre}' cargado con {len(items_consolidados)} tipos de items")
                    
                    nuevo_cofre = Cofre(
                        sx(x), sy(y),
                        id_cofre,
                        requiere_llave=cofre_info.get("requiere_llave"),
                        items_contenido=items_consolidados,  # ¡FIX #2! Usar diccionario consolidado
                        escala=escala,
                        sprite_cerrado=sprite_cerrado,
                        sprite_abierto=sprite_abierto
                    )
                    self.cofres.append(nuevo_cofre)
                else:
                    print(f"¡ADVERTENCIA! Cofre '{id_cofre}' no encontrado en cofres_db.json")'''

# Aplicar Fix #2
content = content.replace(old_cofre_creation, new_cofre_creation)

# Fix #3: Arreglar el mensaje final
old_final_message = '''        print(f"¡Datos del mapa '{nombre_json}' cargados con éxito!")'''
new_final_message = '''        print(f"¡Datos del mapa cargados con éxito desde: {ruta_cargada}!")'''

content = content.replace(old_final_message, new_final_message)

# Guardar el archivo modificado
with open('src/mapa.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Cambios aplicados exitosamente a src/mapa.py")
print("  - Fix #1: Carga desde mapas_unificados/")
print("  - Fix #2: Consolidacion de items de cofres")
print("  - Fix #3: Mensaje de exito corregido")
