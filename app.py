from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_dev_temporal")  # Clave secreta para la sesión, se recomienda usar una clave segura en producción
UPLOAD_FOLDER = os.path.join("static", "img", "productos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def obtener_conexion():
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


@app.route("/")
def index():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("index.html", productos=productos)
    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombres = request.form["nombre"]
        correo = request.form["email"]
        password = request.form["password"]
        try:
            connexion = obtener_conexion()
            cursor = connexion.cursor()
            # Verificar si el correo ya existe
            cursor.execute("SELECT idusuario FROM usuario WHERE correo = %s", [correo])
            if cursor.fetchone():
                flash("El corrreo ya esta registrado", "error")
                return redirect(url_for("register"))
            # insertar nuevo usuario
            cursor.execute(
                "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, %s)",
                (nombres, correo, password, "cliente"),
            )
            connexion.commit()
            cursor.close()
            connexion.close()
            flash("Registro exitoso, ahora puedes iniciar sesion", "exito")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            return f"Error al conectar a la base de datos: {err}"
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["email"]
        password = request.form["password"]

        try:
            connexion = obtener_conexion()
            cursor = connexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT idusuario, nombres, rol FROM usuario WHERE correo = %s AND password = %s",
                (correo, password),
            )
            usuario = cursor.fetchone()
            cursor.close()
            connexion.close()

            # si el usuario existe, guardar su id en la session(memoria temporal del navegador)
            if usuario:
                session["id_usuario"] = usuario["idusuario"]
                session["nombres"] = usuario["nombres"]
                session["rol"] = usuario["rol"]
                flash("Bienvenido, " + usuario["nombres"], "exito")
                return redirect(url_for("index"))
            else:
                flash("correo o contraseña incorrectos", "error")
                return redirect(url_for("login"))
        except mysql.connector.Error as err:
            return f"Error al conectar a la base de datos: {err}"
    return render_template("login.html")


# ruta del logout, que elimina la session del usuario
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "exito")
    return redirect(url_for("index"))


# Ruta del carrito de compras
@app.route("/carrito")
def carrito():
    if not session.get("id_usuario"):
        flash("Debes iniciar sesión para ver tu carrito", "error")
        return redirect(url_for("login"))
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.nombre, p.precio, p.imagen, p.cantidad FROM carrito c JOIN producto p ON c.id_producto = p.id_producto 
            WHERE c.id_usuario = %s""",
            (session["id_usuario"],),
        )
        productos_carrito = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("carrito.html", carrito=productos_carrito)

    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"


# Ruta para agregar productos al carrito
@app.route("/agregar_al_carrito", methods=["POST"])
def agregar_al_carrito():
    if not session.get("id_usuario"):
        flash("Debes iniciar sesion para agregar productos", "error")
        return redirect(url_for("login"))

    id_producto = request.form["id_producto"]

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        # verificar si el producto ya existe en el carrito del usuario
        cursor.execute(
            "SELECT id_carrito, cantidad FROM carrito WHERE id_usuario = %s AND id_producto = %s",
            (session["id_usuario"], id_producto),
        )
        producto_existente = cursor.fetchone()

        if producto_existente:
            # si ya existe este producto aumentamos la cantidad
            cursor.execute(
                "UPDATE carrito SET cantidad = cantidad + 1  WHERE id_carrito = %s",
                (producto_existente["id_carrito"],),
            )

        else:
            # si no exsite lo insertamos
            cursor.execute(
                "INSERT INTO carrito (id_usuario, id_producto, cantidad) VALUES (%s, %s, %s)",
                (session["id_usuario"], id_producto, 1),
            )

            conexion.commit()
            cursor.close()
            conexion.close()
            flash("Producto agregado al carrito", "exito")

    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"


# Ruta panel de administracion
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("rol") != "admin":
        flash("Acceso denegado.", "error")
        return redirect(url_for("index"))
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "POST":
            nombre = request.form["nombre"]
            precio = request.form["precio"]
            descripcion = request.form["descripcion"]
            categoria = request.form["categoria"]
            stock = request.form["stock"]
            imagen = "default.png"  # Imagen por defecto, en caso de que no se suba ninguna imagen

            if "imagen" in request.files:
                file = request.files["imagen"]
                if file and file.filename:
                    nombre_seguro = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro))
                    imagen = nombre_seguro

                cursor.execute(
                    """
                    INSERT INTO producto (nombre, precio, stock, categoria_id_categoria, descripcion, imagen ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (nombre, precio, stock, categoria, descripcion, imagen),
                )
                conexion.commit()
                cursor.close()
                conexion.close()
                flash("producto agregado correctamente", "exito")
                return redirect(url_for("admin"))
        # Obtener categorias para el formulario
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template("admin.html", productos=productos, categorias=categorias)

    except mysql.connector.Error as err:
        return f"Error al conectar a la base de datos: {err}"
    
@app.route("/eliminar_producto/<int:id>")
def eliminar_producto(id):
    if session.get("rol") != "admin":
        flash("Acceso denegado.", "error")
        return redirect(url_for("index"))
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto eliminado correctamente", "exito")
        return redirect (url_for("admin"))
    except mysql.connector.Error as err:
        return f"Error al eliminar producto: {err}"



if __name__ == "__main__":
    app.run(
        debug=True
    )  # Ejecutar la aplicación en modo de depuración para facilitar el desarrollo. Nunca se debe usar debug=True en producción, ya que puede exponer información sensible.