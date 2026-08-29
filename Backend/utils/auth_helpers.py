# ==============================================================================
# HELPER DE EXTRACCIÓN Y DECODIFICACIÓN DE TOKENS DE SESIÓN
# ==============================================================================

import os
import jwt
from flask import request, current_app

def obtener_usuario_desde_token():
    """
    Lee la cookie httponly 'token' enviada desde la petición y la decodifica
    para validar la sesión del usuario y extraer su id y rol.

    Retorna:
        dict: Datos del usuario (idusuario, rol, exp) o None si el token es inválido.
    """
    token = request.cookies.get('token')
    if not token:
        return None
    try:
        secret_key = current_app.config.get('SECRET_KEY') or os.environ.get('SECRET_KEY')
        # CORRECCIÓN: Se usa jwt.decode para LEER el token
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except Exception as e:
        print("Error al decodificar token:", e)
        return None