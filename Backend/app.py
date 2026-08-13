# ==============================================================================
# PROYECTO: NEO GRID GAMING
# ==============================================================================

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errorcodes
import os
from PIL import Image

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

# ------------------------------------------------------------------------------
# CORS: restringido al dominio real del frontend en Vercel.
# supports_credentials=True es OBLIGATORIO para que la cookie httpOnly viaje.
# ------------------------------------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

Limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=os.getenv("REDIS_URL", "memory://")
)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError(
        "ERROR CRITICO: La variable de entorno SECRET_KEY no esta configurada. "
        "La aplicación no puede iniciar de manera segura"
    )

# ¿Estamos en producción (Render)? Controla si la cookie exige HTTPS.
ES_PRODUCCION = os.getenv("FLASK_ENV") == "production"

UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5* 1024 * 1024
EXTENSIONES_PERMITIDAS = { "jpg", "jpeg", "png", "gif", "web"}
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def obtener_conexion():
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conexion = psycopg2.connect(database_url)
        else:
            conexion = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT", "5432")
            )
        return conexion
    except psycopg2.Error as err:
        print(f"Error detallado de conexión: {err}")
        raise err

def extension_permitida(nombre_archivo):
    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1) [1].lower()
    return extension in EXTENSIONES_PERMITIDAS

def es_imagen_valida(archivo):
    """ Verifica que el CONTENIDO del archivo sea realmente una imagen decodificable."""
    try:
        archivo.stream.seek(0)
        Image.open(archivo.stream).verify()
        archivo.stream.seek(0)
        return True
    except Exception:
        return False

def obtener_usuario_desde_token():
    """ Lee la cookie httpOnly 'token' y la decodifica."""
    token = request.cookies.get('token')
    if not token:
        return None
    try:
        return jwt.decode(token, app.secret_key, algorithms=['HS256'])
    except Exception as e:
        print("Error al decodificar token", e)
        return None

def set_cookie_token(response, token):
    """Centraliza la configuración de la cookie para no repetirla en cada ruta."""
    response.set_cookie(
        key="token",
        value=token,
        httpOnly=True,
        secure=ES_PRODUCCION, #True en Render (HTTPS), False en local.
        samesite="None" if ES_PRODUCCION else "Lax", # None es obligatorio para cross-site
    )
    return response


# ------------------------------------------------------------------------------
# AUTENTICACIÓN
# ------------------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
@Limiter.limit("5 per minute")
def login():
    data = request.json
    correo = data.get("correo")
    password = data.get("password")

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT idsuario, password, rol FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario and check_password_hash(usuario["password"], password):
            token = jwt.encode({
                'idusuario': usuario['idusuario'],
                'rol': usuario['rol'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.secret_key, algorithm=['HS256'])

            response = jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "rol": usuario["rol"],
                "idusuario": usuario["idusuario"]
            })
            return set_cookie_token(response, token), 200
        else:
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except psycopg2.Error as err:
        return jsonify({"error": "Error en la base de datos"}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"mensaje": "Sesión cerrada correctamente"})
    response.set_cookie(
        key="token",
        value="",
        httponly=True,
        secure=ES_PRODUCCION,
        samesite="None" if ES_PRODUCCION else "lax",
        max_age=0,
        expires=0
    )
    return response, 200

@app.route("/api/register", methods=["POST"])
@Limiter.limit("3 per minute")
def register():
    datos = request.get_json()

    if not datos or not all(k in datos for k in ("nombre", "email", "password")):
        return jsonify({"error": "Faltan datos requeridos (nombre, email o password)"}), 400

    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        password_seguro = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, password_seguro)
        )
        conexion.commit()

        return jsonify({
            "status": "succes",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada."
        }), 201

    except psycopg2.Error as err:
        if conexion:
            conexion.rollback()
        # En Postgre, "correo duplicado" es el codigo SQLSTATE 23505,
        if err.pgcode == errorcodes.UNIQUE_VIOLATION:
            return jsonify({
                "status": "succes",
                "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada"
            }), 201
        else:
            print("Error inesperado en registro:", err)
            return jsonify({"error": "Ocurrió un error al procesar el registrp"}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


# ------------------------------------------------------------------------------
# CATÁLOGO PÚBLICO
# ------------------------------------------------------------------------------

@app.route("/")
def index():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(productos)
    except psycopg2.Error:
        return jsonify({"error": "Error al conectar con la base de datos"}), 500

@app.route("/api/categorias", methods=["GET"])
def api_categorias():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(categorias), 200
    except psycopg2.Error:
        return jsonify({"error": "Error al consultar categorias"}), 500


@app.route("/api/productos", methods=["GET"])
def api_productos():
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
        SELECT p.id_producto, p.nombre, p.precio, p.stock, p.imagen, p.descripcion,
                p.categoria_id_categoria, c.nombre_categoria

        FROM producto p
        INNER JOIN categoria c ON p.categoria_id_categoria = c.id_categoria
        """)
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify (productos), 200
    except psycopg2.Error:
        return jsonify ({"error": "Error al consultar productos"}), 500


    # ------------------------------------------------------------------------------
# PANEL DE ADMINISTRACIÓN
# ------------------------------------------------------------------------------

@app.route("/api/productos", methods=["POST"])
def api_agregar_productos():
    usuario = obtener_usuario_desde_token()
    if not usuario or not usuario.get("rol") != "admin":
        return jsonify ({"error": "Acceso denegado: Se requieren permisos de administrados"}), 403

    nombre = request.form.get("nombre")
    precio_raw = request.form.get("precio")
    stock_raw = request.form.get("stock")
    categoria = request.form.get("categoria_id")
    imagen = request.files.get("imagen")
    descripcion = request.form.get("descripcion")

    try:
        precio = float(precio_raw)
        stock = int(stock_raw)
        if precio < 0 or stock < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify ({"error": "Precio o Stock invalido"}), 400

    nombre_imagen = "default.png"
    if imagen and imagen.filename != "":
        if not extension_permitida(imagen.filename):
            return jsonify ({"error": "El archivo no es una imagen valida"}), 400
        if not es_imagen_valida(imagen):
            return jsonify ({"error": "El archivo no es una imagen valida"}), 400
        nombre_imagen = secure_filename(imagen.filename)
        if nombre_imagen == "":
            return jsonify ({"error": "Nombre de archivo no valido"}), 400
        imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO producto (nombre, precio, stock, imagen, categori_id_categoria, descripcion)
                VALUES (%s, %s, %s, %s, %s)""",
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Producto guardado correctamente"}), 201
    except psycopg2.Error:
        return jsonify({"error": "Error al agregar producto"}), 500

@app.route("/api/productos/<int:id>", methods=["DELETE"])
def api_eliminar_producto(id):
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify ({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify ({"mensaje": "Producto eliminado"}), 200
    except psycopg2.Error:
        return jsonify ({"error": "Error al eliminar el producto"}), 500

if __name__ == "__main__":
    app.run(debug=True)