# ==============================================================================
# PROYECTO: NEO GRID GAMING - ARCHIVO PRINCIPAL (app.py)
# ==============================================================================

import os
from dotenv import load_dotenv

from flask import Flask
from flask_cors import CORS

# Importación de extensiones
from extensions import limiter

# Importación de Blueprints (Rutas del sistema)
from routes.auth_routes import auth_bp
from routes.categorias_routes import categorias_bp
from routes.productos_routes import productos_bp

# Carga de variables de entorno (.env)
load_dotenv()

# Inicialización del servidor Flask
app = Flask(__name__)

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE EXTENSIONES Y SEGURIDAD
# ------------------------------------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS(app, supports_credentials=True, origins=[FRONTEND_URL], resources={r"/*": {"origins": FRONTEND_URL}})
# Asignar limitador de peticiones
limiter.init_app(app)

# Clave secreta para JWT y sesión
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError(
        "ERROR CRÍTICO: La variable de entorno SECRET_KEY no está configurada. "
        "La aplicación no puede iniciar de manera segura."
    )

# Configuración de subida de imágenes
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB máximo

# ------------------------------------------------------------------------------
# REGISTRO DE BLUEPRINTS (RUTAS MIGRADAS)
# ------------------------------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(productos_bp)


if __name__ == "__main__":
    app.run(debug=True)