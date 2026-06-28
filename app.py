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

# ------------------------------------------------------------------------------
# BLOQUE 2: CONFIGURACIÓN DE LA APLICACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------
# Activamos la carga del archivo oculto .env
load_dotenv()

# Inicializamos la aplicación Flask
app = Flask(__name__)




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
# BLOQUE 4: CONTROLADORES Y RUTAS DE LA TIENDA (FRONTEND PRINCIPAL)
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
    actualmente en sesi;on todavia tiene el rol 'admin'.
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
    
    #Ruta para elimiar productos del carrito
@app.route("/eliminar_del_carrito", methods=["POST"])
def eliminar_del_carrito():
    if not session.get("id_usuario"):
        flash("Debes iniciar sesión para gestionar tu carrito", "error")
        return redirect(url_for("login"))
    id_producto = request.form.get("id_producto")
    id_usuario = session["id_usuario"]

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #Eliminamos el registro exacto que coincide con el usuario y el producto
        cursor.execute(
            "DELETE FROM carrito WHERE id_usuario = %s AND id_producto = %s",
            (id_usuario, id_producto)
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto eliminado del carrito correctamente", "exito")
    except mysql.connector.Error as err:
        flash(f"Error al eliminar el producto: {err}", "error")
    return redirect(url_for("carrito"))


# ------------------------------------------------------------------------------
# BLOQUE 5: RUTAS DE AUTENTICACIÓN (LOGIN, REGISTRO Y LOGOUT)
# ------------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute") # Maximo 5 intentos por minuto por IP
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

            # Validación de credenciales en hash
            if usuario and check_password_hash(usuario["password"], password):
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
@limiter.limit("3 per minute")  # Maximo 3 registros por minuto por IP
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

            #Usamos werkzeug para convertir contraseñas en un hash
            password_seguro = generate_password_hash(password)
            
            # Inserta el nuevo registro, asignando por defecto el rol de cliente
            cursor.execute(
                "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
                (nombre, email, password_seguro),
            )
            conexion.commit()
            cursor.close()
            conexion.close()

# Camino A: Registro exitoso (mismo mensaje por seguridad)
            flash("Si el correo no estaba registrado, tu cuenta ha sido creada. Intenta inciar sesión", "exito")
            return redirect(url_for("login"))
        except mysql.connector.Error:
# Camino B: El correo ya existia o hubo un error (Mensaje identico para reducir ciber-ataques)
            flash("Si el correo no estaba registrado, tu cuenta ha sido creada. Intenta inciar sesión", "exito")
            return redirect(url_for("login"))

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


@app.route("/agregar_producto", methods=["POST"])
@requiere_admin #Activamos la funcion para verificar que el usuario sea "admin"
def agregar_producto():
  
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    stock = request.form["stock"]
    categoria = request.form["categoria"]
    imagen = request.files["imagen"]
    descripcion = request.form["descripcion"]


    #Aplicamos la validacion de la extension de los archivos subidos
    nombre_imagen = "default.png" #Valor por defecto siempre inicializado

    if imagen and imagen.filename !="":
        #verificar que la extension este en la lista blanca
        if not extension_permitida(imagen.filename):
            flash("Tipo de archivo no permitido.")
            return redirect(url_for("admin"))
        
        nombre_imagen = secure_filename(imagen.filename)
        #Verificar que secure_filename no devolvio un string vacio
        if nombre_imagen == "":
            flash("El nombre del archivo no es valido.", "error")
            return redirect(url_for("admin"))
        imagen.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))


    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        # Inserción en la base de datos mapeando las claves foráneas correspondientes
        cursor.execute(
            """INSERT INTO producto (nombre, precio, stock, imagen, categoria_id_categoria, descripcion) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, precio, stock, nombre_imagen, categoria, descripcion),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto agregado correctamente", "exito")
        return redirect(url_for("admin"))
    except mysql.connector.Error as err:
        return f"Error al agregar producto: {err}"


@app.route("/eliminar_producto/<int:id>", methods=["POST"])
@requiere_admin ##Activamos la funcion para verificar que el usuario sea "admin"
def eliminar_producto(id):

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

@app.route("/api/componentes", methods=["GET"])
def obtener_componentes_api():
    """
    API que devuelve un listado de hardware en formato JSON para que React lo consuma.
    """
    # En un proyecto real, esto vendría con un "SELECT * FROM producto WHERE..."
    componentes = [
        {"id": 1, "nombre": "Tarjeta de Video RTX 4060", "precio": 1600000, "categoria": "GPU"},
        {"id": 2, "nombre": "Procesador Intel Core i5-12400F", "precio": 750000, "categoria": "CPU"},
        {"id": 3, "nombre": "Memoria RAM Corsair 16GB DDR4", "precio": 280000, "categoria": "RAM"},
        {"id": 4, "nombre": "Disco Estado Sólido SSD 1TB NVMe", "precio": 320000, "categoria": "Almacenamiento"}
    ]
    # jsonify transforma la lista de Python en un formato que JavaScript entiende perfectamente
    return jsonify(componentes)
# ------------------------------------------------------------------------------
# BLOQUE 7: ARRANQUE DE LA APLICACIÓN
# ------------------------------------------------------------------------------
# Este condicional asegura que el servidor web solo se encienda si el archivo se ejecuta
# directamente, activando el modo debug para detectar errores en tiempo de desarrollo.
if __name__ == "__main__":
    app.run(debug=True)
