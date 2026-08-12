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


from PIL import Image
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# Importaciones para crear y verificar JSON Web Tokens (JWT)
import jwt # Librería para firmar y validar tokens de autenticación segura
import datetime # Módulo para manejar tiempos de expiración de tokens

# load_dotenv: Carga las variables de entorno desde el archivo .env.
from dotenv import load_dotenv

# mysql.connector: Controlador oficial para conectar con MySQL.
import mysql.connector
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
CORS(app, supports_credentials=True, origins=["http://localhost:5173"]) # Permite que tu frontend de React (puerto 5173 / 3000) se comunique con Flask (puerto 5000)

# Configuración de Flask-Limiter para la IP del cliente
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[], # Sin límites globales, solo específicos por ruta (para desarrollo)
    storage_uri=os.getenv("REDIS_URL", "memory://")
)

# Intentamos obtener la clave secreta del entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Si no esta configurada, detenemos la ejecucion inmediatamente
if not app.config['SECRET_KEY']:
    raise RuntimeError(
        "ERROR CRITICO: La variable de entorno SECRET_KEY no esta configurada. "
        "La aplicación no puede iniciar de manera segura"
    )
# Configuración de subida de imágenes para los productos
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 # Límite de 5 MB por archivo
EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "gif", "webp"}

# ------------------------------------------------------------------------------
# BLOQUE 3: FUNCIÓN AUXILIAR DE CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------------------------------
def obtener_conexion():
    """
    Establece y retorna un puente de comunicación con el servidor MySQL.
    """
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT", 3306),
    )
    return conn

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

def es_imagen_valida(archivo):
    """
    Verifica que el contenido del archivo sea realmente una imagen decodificable,
    no solo que su nombre termine en una extension permitida
    """
    try:
        archivo.stream.seek(0) # nos aseguramos de leer desde el inicio
        Image.open(archivo.stream).verify()
        archivo.stream.seek(0) #devolvemos el cursor al inicio para poder guardalo despues
        return True
    except Exception:
        return False

def obtener_usuario_desde_token():
    """
    Lee la cookie 'token' enviada automáticamente por el navegador y la decodifica.
    Retorna un diccionario con los datos del usuario si es válida, o None si no.
    """
    token = request.cookies.get('token')
    if not token:
        return None
    
    try:
        datos = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return datos
    except Exception as e:
        print("Error al decodificar token desde cookie:", e)
        return None

# ------------------------------------------------------------------------------
# BLOQUE 5: RUTAS DE AUTENTICACIÓN (LOGIN Y REGISTRO) - EXCLUSIVO API
# ------------------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
@limiter.limit("3 per minute") 
def login():
    data = request.json
    correo = data.get("correo")
    password = data.get("password")

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute ("SELECT idusuario, password, rol FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and check_password_hash(usuario["password"], password):
            token = jwt.encode({
                'idusuario': usuario['idusuario'],
                'rol': usuario ['rol'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.secret_key, algorithm='HS256')

            # Creamos la respuesta Json con los datos no sensibles (rol e id)
            response = jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "rol": usuario["rol"],
                "idusuario": usuario["idusuario"]
            })

            # Inyectamos el token en una cookie HttpOnly segura
            response.set_cookie(
                key="token",
                value=token,
                httponly=True, # Bloquea lectura por JavaScript (Proteccion contra XSS)
                secure=False,  # Cambiarlo a True cuando se use HTTPS en producción
                samesite="Lax",  # Proteccion contra ataques CSRF
                max_age=86400  # 24 horas de expiración
            )

            return response, 200
        else:
            return jsonify({"error": "Correo o contreaseña incorrectos"}), 401

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erorr en la base de datos: {err}"}), 500
    
# Ruta para el cierre de sesión (Logout)

@app.route("/api/logout", methods=["POST"])
def logout():
    """
    Cierra la sesión eliminando la cookie httpOnly del navegador
    """
    response = jsonify({"mensaje": "Sesión cerrada correctamente"})
    response.set_cookie(
        key="token",
        value="",
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=0,
        expires=0
    )

    return response, 200

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

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "El formato del correo no es válido"}), 400

    if len(password) <8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        password_seguro = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, password_seguro),   
        )
        conexion.commit()

        # Éxito 
        return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada."
        }), 201
        
    except mysql.connector.Error as err:
        if err.errno == 1062:
        # Error / Correo ya regsitrado
            return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada."
        }), 201

        else: 
        # Cualquier otro error (Conexion, esquema, etc.) Sí debe reportarse como error real
            print("Error inesperado en registro:", err)
            return jsonify({"error": "Ocurrió un error al procesar el registro"}), 500
    
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conexion' in locals() and conexion.is_connected():
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
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        return jsonify(productos)
    except mysql.connector.Error as err:
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
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()

        cursor.close()
        conexion.close()
        return jsonify(categorias), 200
    except mysql.connector.Error as err:
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
        cursor = conexion.cursor(dictionary=True)

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
    except mysql.connector.Error as err:
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

        if not es_imagen_valida(imagen):
            return jsonify({"error": "El archivo no es una imagen valida"}), 400
        
        nombre_imagen = secure_filename(imagen.filename)
        if nombre_imagen == "":
            return jsonify({"error": "Nombre de archivo no valido"}), 400
        imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))

    try:
        precio = float(precio)
        stock = int(stock)
        if precio < 0 or stock < 0:
            raise ValueError("Precio o stock negativo")
    except (TypeError, ValueError):
        return jsonify({"error": "Precio o stock invalido"}), 400
        
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
    except mysql.connector.Error as err:
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
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al eliminar producto: {err}"}), 500

# ------------------------------------------------------------------------------
# BLOQUE 9: ARRANQUE DE LA APLICACIÓN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)