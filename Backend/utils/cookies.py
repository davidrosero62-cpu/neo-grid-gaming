# ======================================================================================
# MÓDULO DE UTILIDADES PARA COOKIES DE SESIÓN
#=======================================================================================

import os

# Determina si el entorno es de producción (RENDER) para exigir HTTPS en la cookie
ES_PRODUCCION = os.getenv("FLASK_ENV") == "production"

def set_cookie_token(response, token):
    """

    Configura de forma centralizada la cookie HTTP-only segura con el JWT.

    Parámetros:
        response: Objeto de respuesta HTTP de Flask.
        token (str): Tokenn JWT generado.

        Retorna:
            response: Objeto de respuesta con la cookie adjunta.
    """
    response.set_cookie(
        key="token",
        value=token,
        httponly=True, #Impide acceso a la cookie mediante JavaScript en el navegador
        secure=ES_PRODUCCION, # Exige HTTPS en producción
        samesite="None" if ES_PRODUCCION else "Lax", # Permite cookies cross-site en prod
        max_age=86400 # Duración de 24 horas en segundos.
    )
    return response