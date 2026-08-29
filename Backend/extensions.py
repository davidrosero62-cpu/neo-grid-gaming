# ==============================================================================
# CONFIGURACIÓN DE EXTENSIONES DE FLASK
# ==============================================================================

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Inicializamos la instancia de Limiter sin vincularla aún a ninguna app.
# Esto nos permite importarla en los Blueprints de forma segura

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)