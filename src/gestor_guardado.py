import os
import json
import sys
import pygame # (Necesario para el sys.exit, aunque por ahora solo imprimimos)
from src.config import SAVES_PATH # (Necesitamos saber dónde guardar)

class GestorGuardado:

    # --- Función 1: GUARDAR ---
    # (Esta es una "static method", significa que la llamamos sin crear un "objeto")
    # Se llama así: GestorGuardado.guardar_partida(...)
    @staticmethod
    def guardar_partida(slot_id, datos_partida):
        """
        Agarra los datos de la partida y los "aplasta" (escribe) en un archivo JSON.
        'datos_partida' debe ser un diccionario (lo crearemos en main.py).
        """
        nombre_archivo = f"save_{slot_id}.json"
        ruta_archivo = os.path.join(SAVES_PATH, nombre_archivo)
        
        print(f"¡Guardando partida en '{ruta_archivo}'! ...")
        
        try:
            # 'w' significa "write" (escribir). Si el archivo ya existe, lo borra y lo re-escribe.
            # 'indent=4' es para que el JSON quede "bonito" y legible, no en una sola línea.
            
            # --- ¡MODIFICADO! Añadimos encoding='utf-8' ---
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_partida, f, indent=4)
            print("¡Partida guardada con éxito!")
            return True
        except Exception as e:
            print(f"¡ERROR CRÍTICO AL GUARDAR! No se pudo escribir el archivo: {e}")
            return False

    # --- Función 2: CARGAR ---
    @staticmethod
    def cargar_partida(slot_id):
        """
        Lee un archivo JSON del slot y devuelve los datos "descomprimidos".
        Devuelve el diccionario de datos si lo encuentra, o None si falla.
        """
        nombre_archivo = f"save_{slot_id}.json"
        ruta_archivo = os.path.join(SAVES_PATH, nombre_archivo)

        print(f"¡Cargando partida desde '{ruta_archivo}'! ...")

        # Primero, chequeamos si el archivo existe (por si acaso)
        if not os.path.exists(ruta_archivo):
            print(f"¡ERROR! No se encontró el archivo de guardado: {ruta_archivo}")
            return None
            
        try:
            # 'r' significa "read" (leer).
            # --- ¡MODIFICADO! Añadimos encoding='utf-8' ---
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_partida = json.load(f)
            print("¡Partida guardada con éxito!")
            return datos_partida
        except json.JSONDecodeError:
            print(f"¡ERROR CRÍTICO AL CARGAR! El archivo JSON está mal escrito o corrupto: {ruta_archivo}")
            return None
        except Exception as e:
            print(f"¡ERROR CRÍTICO AL CARGAR! Error desconocido: {e}")
            return None

    # --- Función 3: CHEQUEAR SI EXISTE (la usa pantalla_slots.py) ---
    @staticmethod
    def chequear_slot(slot_id):
        """
        Chequea rápido si un archivo de guardado existe.
        (Es la misma lógica que os.path.exists pero la ponemos aquí
        para tener todo lo de "guardado" en un solo lugar).
        """
        nombre_archivo = f"save_{slot_id}.json"
        ruta_archivo = os.path.join(SAVES_PATH, nombre_archivo)
        return os.path.exists(ruta_archivo)