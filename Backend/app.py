# ==============================================================================
# PROYECTO: NEO GRID GAMING
# ==============================================================================

# ------------------------------------------------------------------------------
# BLOQUE 1: IMPORTACIÓN DE LIBRERÍAS Y MÓDULOS
# ------------------------------------------------------------------------------
# Flask: Framework principal para construir la API REST.
# request: Permite capturar datos en JSON (datos.get) o FormData (request.form) desde React.
# jsonify: Convierte diccionarios de Python en respuestas JSON válidas.
from flask import Flask, request, jsonify

# secure_filename: Asegura que los nombres de los archivos subidos no tengan caracteres peligrosos.
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Importaciones para crear y verificar JSON Web Tokens (JWT)
import jwt # Librería para firmar y validar tokens de autenticación segura
import datetime # Módulo para manejar tiempos de expiración de tokens

# load_dotenv: Carga las variables de entorno desde el archivo .env.
from dotenv import load_dotenv

# mysql.connector: Controlador oficial para conectar con MySQL.
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Importamos la librería flask-limiter para evitar ataques de fuerza bruta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importa la extensión para permitir peticiones CORS desde React
from flask_cors import CORS

# ------------------------------------------------------------------------------
# BLOQUE 2: CONFIGURACIÓN DE LA APLICACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app) # Permite que tu frontend de React (puerto 5173 / 3000) se comunique con Flask (puerto 5000)

# Configuración de Flask-Limiter para la IP del cliente
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[], # Sin límites globales, solo específicos por ruta (para desarrollo)
    storage_uri=os.getenv("REDIS_URL", "memory://")
)

# Clave secreta para firmar los JWTs
app.secret_key = os.getenv("SECRET_KEY", "clave_dev_temporal")

# Configuración de subida de imágenes para los productos
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 # Límite de 5 MB por archivo
EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "gif", "webp"}

# ------------------------------------------------------------------------------
# BLOQUE 3: FUNCIÓN AUXILIAR DE CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------------------------------
def obtener_conexion():
    try:
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432"),
        )
        return conexion
    except psycopg2.Error as err:
        print(f"Error detallado de conexión: {err}")
        raise err

# ------------------------------------------------------------------------------
# BLOQUE 4: FUNCIONES AUXILIARES DE SEGURIDAD
# ------------------------------------------------------------------------------

def extension_permitida(nombre_archivo):
    """
    Verifica que el archivo tenga una extensión permitida en la lista blanca.
    """
    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in EXTENSIONES_PERMITIDAS

def obtener_usuario_desde_token():
    """
    Lee la cabecera 'Authorization', extrae el token JWT y lo decodifica.
    Retorna un diccionario con los datos del usuario si el token es válido, 
    de lo contrario retorna None.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        # El header llega como: "Bearer eyJhbGci..."
        token = auth_header.split(" ")[1]
        datos = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return datos # Retorna {'idusuario': X, 'rol': 'admin', 'exp': ...}
    except Exception as e:
        print("Error al decodificar token:", e)
        return None

# ------------------------------------------------------------------------------
# BLOQUE 5: RUTAS DE AUTENTICACIÓN (LOGIN Y REGISTRO) - EXCLUSIVO API
# ------------------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    """
    API de Login: Valida credenciales, genera un token JWT y lo retorna junto al rol.
    """
    data = request.json
    correo = data.get("correo")
    password = data.get("password")

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    try:
        conexion = obtener_conexion()
        # Usamos RealDictCursor para obtener diccionarios.
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT idusuario, password, rol FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and check_password_hash(usuario["password"], password):
            # Creación del token JWT que expira en 24 horas
            token = jwt.encode({
                'idusuario': usuario['idusuario'],
                'rol': usuario['rol'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.secret_key, algorithm='HS256')

            return jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "rol": usuario["rol"],
                "idusuario": usuario["idusuario"],
                "token": token
            }), 200
        else:
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except psycopg2.Error as err:
        return jsonify({"error": f"Error en la base de datos: {err}"}), 500


@app.route("/api/register", methods=["POST"])
@limiter.limit("3 per minute")  # Máximo 3 registros por minuto por IP para evitar SPAM
def register():
    """
    API de registro: Recibe datos JSON y crea un usuario con rol 'cliente'.
    """
    datos = request.get_json()

    if not datos or not all(k in datos for k in ("nombre", "email", "password")):
        return jsonify({"error": "Faltan datos requeridos (nombre, email o password)"}), 400
    
    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        password_seguro = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, password_seguro),   
        )
        conexion.commit()

        # Éxito (Corregido 'status' y ortografía)
        return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada."
        }), 201
        
    except psycopg2.Error:
        # Error / Correo ya existente
        return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada."
        }), 201
    
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conexion' in locals() and conexion is not None:
            conexion.close()

# ------------------------------------------------------------------------------
# BLOQUE 6: RUTAS DE LA TIENDA (CATÁLOGO GENERAL DE PRODUCTOS)
# ------------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Ruta raíz de la API: Retorna todos los productos del catálogo en formato JSON puro.
    """
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        return jsonify(productos)
    except psycopg2.Error as err:
        return jsonify({"error": f"Error al conectar con la base de datos: {err}"}), 500

# ------------------------------------------------------------------------------
# BLOQUE 7: RUTAS DE API PÚBLICA (CATEGORÍAS Y PRODUCTOS)
# ------------------------------------------------------------------------------

@app.route("/api/categorias", methods=["GET"])
def api_categorias():
    """
    API que consulta las categorías para utilizarlas en selectores del frontend.
    """
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()

        cursor.close()
        conexion.close()
        return jsonify(categorias), 200
    except psycopg2.Error as err:
        return jsonify({"error": f"Error al consultar categorias: {err}"}), 500


@app.route("/api/productos", methods=["GET"])
def api_productos():
    """
    API que lista todos los productos con categorías detalladas para la tabla de administración.
    """
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        consulta_sql = """
            SELECT
                p.id_producto,
                p.nombre,
                p.precio,
                p.stock,
                p.imagen,
                p.descripcion,
                p.categoria_id_categoria,
                c.nombre_categoria
            FROM producto p
            INNER JOIN categoria c ON p.categoria_id_categoria = c.id_categoria
        """

        cursor.execute(consulta_sql)
        productos = cursor.fetchall()

        cursor.close()
        conexion.close()
        return jsonify(productos), 200
    except psycopg2.Error as err:
        return jsonify({"error": f"Error al consultar productos: {err}"}), 500

# ------------------------------------------------------------------------------
# BLOQUE 8: RUTAS DEL PANEL DE ADMINISTRACIÓN (CRUD EXCLUSIVO DE LA API)
# ------------------------------------------------------------------------------

@app.route("/api/productos", methods=["POST"])
def api_agregar_producto():
    """
    API para registrar un nuevo producto enviando FormData desde React.
    """
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403
    
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    stock = request.form.get("stock")
    categoria = request.form.get("categoria_id")
    imagen = request.files.get("imagen")
    descripcion = request.form.get("descripcion")

    nombre_imagen = "default.png"

    if imagen and imagen.filename != "":
        if not extension_permitida(imagen.filename):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400
        
        nombre_imagen = secure_filename(imagen.filename)
        if nombre_imagen == "":
            return jsonify({"error": "Nombre de archivo no valido"}), 400
        imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))
        
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO producto (nombre, precio, stock, imagen, categoria_id_categoria, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, precio, stock, nombre_imagen, categoria, descripcion)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Producto guardado correctamente"}), 201
    except psycopg2.Error as err:
        return jsonify({"error": f"Error al agregar producto: {err}"}), 500        


@app.route("/api/productos/<int:id>", methods=["DELETE"])
def api_eliminar_producto(id):
    """
    API para eliminar físicamente un producto del inventario mediante su ID.
    """
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Producto eliminado"}), 200
    except psycopg2.Error as err:
        return jsonify({"error": f"Error al eliminar producto: {err}"}), 500

# ------------------------------------------------------------------------------
# BLOQUE 9: ARRANQUE DE LA APLICACIÓN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)