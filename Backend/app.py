# ==============================================================================
# PROYECTO: NEO GRID GAMING
# ==============================================================================

# ------------------------------------------------------------------------------
# BLOQUE 1: IMPORTACIÓN DE LIBRERÍAS Y MÓDULOS
# ------------------------------------------------------------------------------
# Flask: Framework principal para construir la aplicación web.
# render_template: Permite cargar y mostrar las páginas HTML (plantillas).
# request: Permite capturar los datos enviados por el usuario desde los formularios.
# redirect y url_for: Permiten redirigir al usuario de una página a otra de forma dinámica.
# session: Permite almacenar variables globales del usuario en el navegador (control de login).
# flash: Permite mostrar mensajes de alerta temporales en la pantalla (ej: "Usuario registrado").
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# secure_filename: Asegura que los nombres de los archivos subidos no tengan caracteres peligrosos.
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Librería de Flask permite almacenar información específica de cada usuario a medida que navega por la app
from flask import session
from werkzeug.security import check_password_hash

# Importaciones para crear y verificar JSON Web Tokens (JWT) 
import jwt # Trae la libreria que contiene las funciones para cifrar datos en un token y descifrar el mismo para validar quien es el usuario
import datetime # Trae el modulo para manejar fechas y horas.

# load_dotenv: Carga las variables de entorno desde el archivo secreto .env (seguridad).
from dotenv import load_dotenv

# mysql.connector: Controlador oficial para conectar Python con la base de datos MySQL.
import mysql.connector

# os: Módulo del sistema operativo para manejar rutas de carpetas y archivos del servidor.
import os

#Importamos wraps, utilidad de Python que preserva el nombre y la documentacion de la funcion original cuando se usa un decorador
from functools import wraps

# Importamos la libreria flask-limiter para evitar ataques de fuerza bruta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Importa la extensión para permitir peticiones desde el frontend (CORS)
from flask_cors import CORS

# ------------------------------------------------------------------------------
# BLOQUE 2: CONFIGURACIÓN DE LA APLICACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------
# Activamos la carga del archivo oculto .env
load_dotenv()

# Inicializamos la aplicación Flask
app = Flask(__name__)
# Habilita CORS para permitir peticiones desde aplicaciones frontend en otros dominios
CORS(app)




#Configuramos la libreria Flask-Limiter
#El key_func le dice al limiter que identifique a cada visitante por su IP

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[] #sin limite global; solo limites especificos por ruta
)

# Configuramos la clave secreta indispensable para cifrar y proteger las sesiones de usuario
app.secret_key = os.getenv("SECRET_KEY", "clave_dev_temporal")

# Definimos la ruta física del servidor donde se guardarán las fotos de los productos subidos
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Agregamos configuración de tamaño maximo
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 *1024 # Limite de 5 MB por archivo subido
EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "gif", "webp"}



# ------------------------------------------------------------------------------
# BLOQUE 3: FUNCIÓN AUXILIAR DE CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------------------------------
def obtener_conexion():
    """
    Establece y retorna un puente de comunicación con el servidor MySQL.
    Utiliza los datos definidos de forma segura en el archivo .env.
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
# BLOQUE 4: FUNCIONES AUXILIARES Y DECORADORES DE SEGURIDAD
# ------------------------------------------------------------------------------

# Creamos una función validadora para el tipo de archivo subido
def extension_permitida(nombre_archivo):
    """
    Verifica que el achivo tenga una extensión en la lista blanca.
    'foto.producto.JPG'  → extrae 'jpg'  → verifica en el conjunto  → True
    'malware.php'        → extrae 'php'  → no esta en el conjuto  → False
    """
    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in EXTENSIONES_PERMITIDAS

#Creamos el decorador requiere_admin para revalidación de datos
def requiere_admin(f): 
    """
    Decorador de seguridad que verifica en la base de datos que el usuario
    actualmente en sesión todavia tiene el rol 'admin'.
    Uso: @requiere_admin encima de cualquier ruta protegida.
    """

    @wraps(f)
    def function_decorada(*args, **kwargs):
        # Primero verificar que hay sesión activa
        if not session.get("id_usuario"):
            flash("Debes iniciar sesión", "error")
            return redirect(url_for("login"))
        
        #Luego consultar la DB para verificar el rol actual (no confiar solo en la cookie)
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT rol FROM usuario WHERE idusuario = %s",
                (session["id_usuario"],)
            )

            usuario_db = cursor.fetchone ()
            cursor.close()
            conexion.close()

            if not usuario_db or usuario_db["rol"] != "admin":
                session.clear() #Limpiar sesión desactualizada
                flash("Acceso denegado: permisos insuficientes", "error")
                return redirect(url_for("index"))
            
        except mysql.connector.Error:
            flash("Error de servidor al verificar permisos", "error")
            return redirect(url_for("index"))
        return f (*args, **kwargs) # Todo bien: ejecutar la funcion original
    return function_decorada

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
        # Decodificamos el token usando la clave secreta de tu app
        datos = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return datos # Retorna {'idusuario': X, 'rol': 'admin', 'exp': ...}
    except Exception as e:
        print("Error al decodificar token:", e)
        return None



# Funcion global que inyexta variables automáticamente en todas las plantillas del proyecto
@app.context_processor
def contar_carrito_global():

    """
    Calcula la cantidad toal de articulos en el carrito del usuario logueado
    y la hace disponible automaticamente en todas las plantillas HTML.
    """
    if not session.get("id_usuario"):
        return{"cart_count": 0}
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Sumamos la columna 'cantidad' para saber el total de articulos acumulados
        cursor.execute(
            "SELECT SUM(cantidad) AS total FROM carrito WHERE id_usuario =%s",
            [session["id_usuario"]]
        )
        resultado = cursor.fetchone()

        cursor.close()
        conexion.close()

        # Si el resultado es None o la suma da None, devolvemos 0
        if resultado and resultado["total"]:
            return{"cart_count": resultado["total"]}
    except Exception:
        pass
        
    return {"cart_count": 0}


# ------------------------------------------------------------------------------
# BLOQUE 5: RUTAS DE AUTENTICACIÓN (LOGIN, REGISTRO Y LOGOUT)
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
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT idusuario, password, rol FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario and check_password_hash(usuario["password"], password):
            # --- CREACIÓN DEL TOKEN JWT ---
            token = jwt.encode({
                'idusuario': usuario['idusuario'],
                'rol': usuario['rol'],
                # El token caducará automáticamente en 24 horas
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.secret_key, algorithm='HS256')

            return jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "rol": usuario["rol"],
                "idusuario": usuario["idusuario"],
                "token": token # <-- ¡Aquí enviamos el token a React!
            }), 200
        else:
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except mysql.connector.Error as err:
        return jsonify({"error": f"Error en la base de datos: {err}"}), 500


@app.route("/api/register", methods=["POST"])
@limiter.limit("3 per minute")  # Maximo 3 registros por minuto por IP
def register():
    """
   API de registro: recibe los datos del nuevo usauri en formato JSON 
   y los guarda en la base de datos. Aplica por defecto el rol de 'cliente'
    """

    datos = request.get_json()

    # Validacion basica de seguridad para evitar errores si faltan campos.
    if not datos or not all(k in datos for k in ("nombre", "email", "password")):
        return jsonify({"error": "Faltan datos requeridos (nombre, email o password)"}), 400
    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Usamos werkzeug para convertir la contraseña en un hash
        password_seguro = generate_password_hash(password)

        cursor.execute(
        "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s,'cliente')",
         (nombre,email, password_seguro),   
        )

        conexion.commit()
        # Camino A: Registro exitoso
        # Devolvemos un JSON y un codigo HTTP 201 (Created)
        return jsonify({
            "status": "succces",
            "mensaje": "Si el correo no estaba registrado, tu cuenta a sido creada."
        }), 201
    except mysql.connector.Error as e:
        # Camino B: El correo ya existia o hubo un error en la BD
        # Mensaje identico para reducir ciber-ataques de enumeracion de correos
        return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba regisrado, tu cuenta a sido creada."
        }), 201
    
    finally:
        # Buena practica: asegurar que la conexion se cierre siempre, falle o no
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'cursor' in locals() and conexion.is_connected:
            conexion.close()

@app.route("/logout")
def logout():
    """
    Ruta para cerrar la sesión actual.
    Limpia por completo el diccionario de sesión del navegador del cliente
    y lo redirige a la página principal de la tienda.
    """
    session.clear()
    flash("Has cerrado sesión correctamente", "exito")
    return redirect(url_for("index"))


# ------------------------------------------------------------------------------
# BLOQUE 6: RUTAS DE LA TIENDA Y EL CARRITO
# ------------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Ruta raíz o Página de Inicio.
    Consulta todos los artículos registrados en la tabla 'producto' de la base
    de datos y los envía al archivo 'index.html' para renderizar el catálogo comercial.
    """
    try:
        conexion = obtener_conexion()
        # dictionary=True convierte los resultados de la DB en diccionarios de Python
        cursor = conexion.cursor(dictionary=True,)
        
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        # Devolvemos JSON puro
        return jsonify(productos)
    except mysql.connector.Error as err:
        # Si hay error en la base de datos, tambien responde en formato JSON
        return jsonify({"error": f"Error al conectar con la base de datos: {err}"}), 500



@app.route("/carrito")
def carrito():
    """
    Ruta para visualizar el Carrito de Compras.
    Verifica que el usuario esté logueado, consulta los artículos que ha agregado
    enlazando la tabla 'carrito' con 'producto' y calcula el subtotal y total.
    """
    if not session.get("id_usuario"):
        flash("Debes iniciar sesión para ver tu carrito", "error")
        return redirect(url_for("login"))
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True, buffered=True)
        
        # Consulta SQL combinando el carrito del usuario con los datos reales del producto
        cursor.execute(
            """
            SELECT c.id_producto, p.nombre, p.precio, p.imagen, c.cantidad 
            FROM carrito c 
            JOIN producto p ON c.id_producto = p.id_producto 
            WHERE c.id_usuario = %s
            """,
            (session["id_usuario"],),
        )
        productos_carrito = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        # Renderiza la vista del carrito pasando los productos encontrados
        return render_template("carrito.html", carrito=productos_carrito)
    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"


@app.route("/agregar_al_carrito", methods=["POST"])
def agregar_al_carrito():
    """
    Ruta para añadir artículos al carrito de compras desde el catálogo.
    Recibe el ID del producto enviado por formulario, valida la sesión del cliente
    e inserta o actualiza el registro correspondiente en la tabla 'carrito'.
    """
    if not session.get("id_usuario"):
        flash("Debes iniciar sesión para agregar productos al carrito", "error")
        return redirect(url_for("login"))
        
    id_producto = request.form.get("id_producto")
    id_usuario = session["id_usuario"]
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        # Consultar stock disponible del producto
        cursor.execute(
            "SELECT stock FROM producto WHERE id_producto = %s",
            (id_producto,)
        )
        producto_db = cursor.fetchone()

        # Verificar que el producto exista
        if not producto_db:
            flash("El producto no existe", "error")
            return redirect(url_for("index"))
        
        stock_disponible = producto_db["stock"]

        #Ver cuántos productos tiene el usuario en el carrito

        cursor.execute(
            "SELECT cantidad FROM carrito WHERE id_usuario = %s AND id_producto = %s",
            (id_usuario, id_producto)
        )
        existe = cursor.fetchone()

        cantidad_actual_en_carrito = existe["cantidad"] if existe else 0

        #Verificar que agregar 1 más no supere el stock
        if cantidad_actual_en_carrito + 1 > stock_disponible:
            flash(f"No hay suficiente stock, Solo quedan {stock_disponible} unidades disponibles", "error")
            return redirect(url_for("index"))
        
        if existe:
            cursor.execute(
                "UPDATE carrito SET cantidad = %s WHERE id_usuario = %s AND id_producto = %s",
                (cantidad_actual_en_carrito + 1, id_usuario, id_producto)
            )
        else:
            # Si es nuevo en el carrito, se inserta con cantidad inicial de 1
            cursor.execute(
                "INSERT INTO carrito (id_usuario, id_producto, cantidad) VALUES (%s, %s, 1)",
                (id_usuario, id_producto)
            )
            
        conexion.commit()
        cursor.close()
        conexion.close()
        
        flash("Producto agregado al carrito con éxito", "exito")
        return redirect(url_for("index"))
    except mysql.connector.Error as err:
        return f"Error al gestionar el carrito: {err}"



# ------------------------------------------------------------------------------
# BLOQUE 7: RUTAS DE API PÚBLICA (CATEGORÍAS, PRODUCTOS Y COMPONENTES)
# ------------------------------------------------------------------------------

# Ruta para consultar en la Base de Datos y retornar los datos en JSON

@app.route("/api/categorias", methods=["GET"])
def api_categorias():
    """
    API que consulta las categorias en la base de datos
    y las retorna en formato JSON para el select de React.
    """

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Consultamos las categorias en la base de datos
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()

        cursor.close()
        conexion.close()

        # Retornamos los datos puros en JSON con codigo de estado 200 (Éxito)
        return jsonify(categorias), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al consultar categorias: {err}"}), 500

#Ruta para la API de productos

@app.route("/api/productos", methods=["GET"])
def api_productos():

    # Validamos usando nuestro validador de tokens
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
# BLOQUE 8: RUTAS DEL PANEL DE ADMINISTRACIÓN (CRUD DE PRODUCTOS)
# ------------------------------------------------------------------------------

@app.route("/admin")
@requiere_admin #Activamos la funcion para verificar que el usuario sea "admin"
def admin():
   
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto")
    productos = cursor.fetchall()


    cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
    categorias = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("admin.html", productos=productos, categorias=categorias)


# Ruta API para crear productos
@app.route("/api/productos", methods =["POST"])
def api_agregar_producto():
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denagado: Se requieren permisos de administrador"}), 403
    #Capturamos datos multimedia (FormData) enviados desde REACT
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
        if nombre_imagen =="":
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
    except Exception as err:
        return jsonify({"error": f"Error interno del servidor: {err}"}), 500     


@app.route("/api/productos/<int:id>", methods =["DELETE"])
def api_eliminar_producto(id):
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


@app.route("/modificar_producto/<int:id>", methods=["GET", "POST"])
@requiere_admin #Activamos la funcion para verificar que el usuario sea "admin"
def modificar_producto(id):
   
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        descripcion = request.form["descripcion"]

        cursor.execute(
            "UPDATE producto SET nombre=%s, precio=%s, stock=%s, descripcion=%s WHERE id_producto=%s",
            (nombre, precio, stock, descripcion, id),
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        flash("Producto actualizado correctamente", "exito")
        return redirect(url_for("admin"))

    # Operación GET: Recupera los datos iniciales para mostrarlos dentro del formulario de edición
    cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template("editar.html", producto=producto)

# ------------------------------------------------------------------------------
# BLOQUE 9: ARRANQUE DE LA APLICACIÓN
# ------------------------------------------------------------------------------
# Este condicional asegura que el servidor web solo se encienda si el archivo se ejecuta
# directamente, activando el modo debug para detectar errores en tiempo de desarrollo.
# Este condicional asegura que el servidor web solo se encienda si el archivo se ejecuta
# directamente, activando el modo debug para detectar errores en tiempo de desarrollo.
if __name__ == "__main__":
    app.run(debug=True)