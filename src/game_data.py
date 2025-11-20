# Este archivo funciona como una base de datos estática para el juego.
# Contiene diccionarios de traducción y otros datos constantes.
# ---------------------------------------------------------------------

# Diccionario de traducción de nombres de mapas
# Mapea los nombres de archivo (usados en saves) a nombres legibles

MAPA_NOMBRES_LEGIBLES = {
    #MUNDO
    "mapa_pradera.jpg": "Pradera de Inicio",
    
    #Pueblo de inicio
    "mapa_pueblo_final.png": "Pueblo Inicial",
    "mapa_posada.png": "Posada 'El Pixel'",
    "mapa_tienda_items.png": "Tienda de items",
    "mapa_tienda_magia.png": "Tienda de Magia",
    "mapa_herrero.png": "Herrería 'El Yunque'",
    "mapa_taberna.png": "Taberna 'El Dragón'"
    
    # (Se pueden agregar más mapas aquí después)
}

# Función de consulta segura 
def traducir_nombre_mapa(nombre_archivo_guardado):
    """
    Busca el nombre legible en el diccionario.
    Si no lo encuentra, devuelve el nombre de archivo original
    para evitar un error y asegurar que siempre se muestre algo.
    """
    # .get() es el método seguro:
    # Intenta obtener 'nombre_archivo_guardado', si falla,
    # devuelve 'nombre_archivo_guardado' (el valor por defecto).
    return MAPA_NOMBRES_LEGIBLES.get(nombre_archivo_guardado, nombre_archivo_guardado)
    