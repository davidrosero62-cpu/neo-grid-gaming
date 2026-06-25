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
from flask import Flask, render_template, request, redirect, url_for, session, flash

# secure_filename: Asegura que los nombres de los archivos subidos no tengan caracteres peligrosos.
from werkzeug.utils import secure_filename

# load_dotenv: Carga las variables de entorno desde el archivo secreto .env (seguridad).
from dotenv import load_dotenv

# mysql.connector: Controlador oficial para conectar Python con la base de datos MySQL.
import mysql.connector

# os: Módulo del sistema operativo para manejar rutas de carpetas y archivos del servidor.
import os

# ------------------------------------------------------------------------------
# BLOQUE 2: CONFIGURACIÓN DE LA APLICACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------
# Activamos la carga del archivo oculto .env
load_dotenv()

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Configuramos la clave secreta indispensable para cifrar y proteger las sesiones de usuario
app.secret_key = os.getenv("SECRET_KEY", "clave_dev_temporal")

# Definimos la ruta física del servidor donde se guardarán las fotos de los productos subidos
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
# BLOQUE 4: CONTROLADORES Y RUTAS DE LA TIENDA (FRONTEND PRINCIPAL)
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
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        return render_template("index.html", productos=productos)
    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"


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
        cursor = conexion.cursor(dictionary=True)
        
        # Consulta SQL combinando el carrito del usuario con los datos reales del producto
        cursor.execute(
            """
            SELECT p.nombre, p.precio, p.imagen, c.cantidad 
            FROM carrito c 
            JOIN producto p ON c.producto_id_producto = p.id_producto 
            WHERE c.usuario_idusuario = %s
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
        
        # Comprobamos si el usuario ya tenía ese producto específico en su carrito
        cursor.execute(
            "SELECT * FROM carrito WHERE usuario_idusuario = %s AND producto_id_producto = %s",
            (id_usuario, id_producto)
        )
        existe = cursor.fetchone()
        
        if existe:
            # Si ya existe, le sumamos 1 a la cantidad acumulada
            nueva_cantidad = existe["cantidad"] + 1
            cursor.execute(
                "UPDATE carrito SET cantidad = %s WHERE usuario_idusuario = %s AND producto_id_producto = %s",
                (nueva_cantidad, id_usuario, id_producto)
            )
        else:
            # Si es nuevo en el carrito, se inserta con cantidad inicial de 1
            cursor.execute(
                "INSERT INTO carrito (usuario_idusuario, producto_id_producto, cantidad) VALUES (%s, %s, 1)",
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
# BLOQUE 5: RUTAS DE AUTENTICACIÓN (LOGIN, REGISTRO Y LOGOUT)
# ------------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Ruta para el ingreso seguro de usuarios.
    - GET: Muestra el formulario visual.
    - POST: Valida el email y contraseña contra la base de datos. Si coincide,
      crea las variables de sesión id_usuario, usuario y rol.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Buscamos al usuario por su correo único
            cursor.execute("SELECT * FROM usuario WHERE correo = %s", (email,))
            usuario = cursor.fetchone()
            
            cursor.close()
            conexion.close()

            # Validación de credenciales en texto plano (en producción aplicar hashing)
            if usuario and usuario["password"] == password:
                session["id_usuario"] = usuario["idusuario"]
                session["usuario"] = usuario["nombres"]
                session["rol"] = usuario["rol"]
                
                flash(f"¡Bienvenido de nuevo, {usuario['nombres']}!", "exito")
                return redirect(url_for("index"))
            else:
                flash("Correo o contraseña incorrectos", "error")
        except mysql.connector.Error as err:
            flash(f"Error en el servidor: {err}", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Ruta para el autoregistro de nuevos usuarios.
    Toma los datos del formulario de registro y los guarda en la base de datos.
    Aplica por defecto el rol de 'cliente'.
    """
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Inserta el nuevo registro, asignando por defecto el rol de cliente
            cursor.execute(
                "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
                (nombre, email, password),
            )
            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Registro exitoso. Ahora puedes iniciar sesión.", "exito")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"El correo ya se encuentra registrado o hubo un error: {err}", "error")

    return render_template("register.html")


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
# BLOQUE 6: RUTAS DEL PANEL DE ADMINISTRACIÓN (CRUD DE PRODUCTOS)
# ------------------------------------------------------------------------------

@app.route("/admin")
def admin():
    """
    Ruta del Panel Administrativo de Control.
    Verifica mediante seguridad por software que el rol del usuario logueado sea 'admin'.
    Muestra la tabla total con la lista de productos para su respectiva gestión.
    """
    if session.get("rol") != "admin":
        flash("Acceso denegado: No tienes permisos de administrador", "error")
        return redirect(url_for("index"))

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("admin.html", productos=productos)


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    """
    Ruta del CRUD: Crear Producto.
    Procesa la subida de la imagen seleccionada al servidor, captura los detalles del juego
    (nombre, precio, stock, categoría) y los guarda en la base de datos.
    """
    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    categoria = request.form["categoria"]
    imagen = request.files["imagen"]

    if imagen:
        # Renombramos el archivo de forma segura y lo guardamos en la carpeta de imágenes
        nombre_imagen = secure_filename(imagen.filename)
        imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))
    else:
        nombre_imagen = "default.png"

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        # Inserción en la base de datos mapeando las claves foráneas correspondientes
        cursor.execute(
            """INSERT INTO producto (nombre, precio, stock, imagen, categoria_id_categoria) 
               VALUES (%s, %s, %s, %s, %s)""",
            (nombre, precio, stock, nombre_imagen, categoria),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto agregado correctamente", "exito")
        return redirect(url_for("admin"))
    except mysql.connector.Error as err:
        return f"Error al agregar producto: {err}"


@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):
    """
    Ruta del CRUD: Eliminar Producto.
    Toma el ID único enviado a través de la URL de administración, ejecuta el borrado físico 
    del registro en la base de datos y actualiza la vista.
    """
    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto eliminado correctamente", "exito")
        return redirect(url_for("admin"))
    except mysql.connector.Error as err:
        return f"Error al eliminar producto: {err}"


@app.route("/modificar_producto/<int:id>", methods=["GET", "POST"])
def modificar_producto(id):
    """
    Ruta del CRUD: Actualizar/Modificar Producto.
    - GET: Obtiene la información actual del producto mediante su ID y llena el formulario de 'editar.html'.
    - POST: Captura los nuevos valores modificados por el administrador y actualiza el registro en la DB.
    """
    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]

        cursor.execute(
            "UPDATE producto SET nombre=%s, precio=%s, stock=%s WHERE id_producto=%s",
            (nombre, precio, stock, id),
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
# BLOQUE 7: ARRANQUE DE LA APLICACIÓN
# ------------------------------------------------------------------------------
# Este condicional asegura que el servidor web solo se encienda si el archivo se ejecuta
# directamente, activando el modo debug para detectar errores en tiempo de desarrollo.
if __name__ == "__main__":
    app.run(debug=True)
