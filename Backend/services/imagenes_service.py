# ==============================================================================
# SERVICIO DE GESTIÓN Y VALIDACIÓN DE IMÁGENES
# ==============================================================================

import os
from PIL import Image

# Formatos de archivo de imagen autorizados

EXTESIONES_PERMITIDAS = {"jpg", "jpge", "png", "gif", "webp"}


def extension_permitida(nombre_archivo):
    """
    Verifica si la extensión del archivo está dentro del conjunto permitido.

    Parámetros:
        nombre_archivo (str): Nombre del archivo subido.
    Retorna:
        bool: True si la extensión es valida, False en caso contrario.
    """
    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in  EXTESIONES_PERMITIDAS


def es_imagen_valida(archivo):
    """
    Inspecciona el CONTENIDO binario del archivo usando Pillow para grantizar que sea una
    imagen real y no un archivo malicioso renombrado.

    Párametros:
        archivo: Objeto FileStorage de Flask.
    Retorna:
        bool: True si la imagen se puede decodificar, False si esta corrupta o alterada
    """
    try:
        archivo.stream.seek(0)
        Image.open(archivo.stream).verify()
        archivo.stream.seek(0)
        return True
    except Exception:
        return False


