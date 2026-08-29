# ==============================================================================
# RUTAS DE GESTIÓN DE PRODUCTOS Y CATÁLOGO
# ==============================================================================

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from database import obtener_conexion
from services.imagenes_service import es_imagen_valida, extension_permitida
from utils.auth_helpers import obtener_usuario_desde_token

# Instancia del Blueprint para Productos
productos_bp = Blueprint('productos', __name__)

@productos_bp.route("/", methods=["GET"])
def index():
    """Ruta del catálogo general público."""
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(productos), 200
    except psycopg2.Error as err:
        print("Error en base de datos al cargar el catálogo:", err)
        return jsonify({"error": "Error al conectar con la base de datos"}), 500


@productos_bp.route("/api/productos", methods= ["GET"])
def api_productos():
    """Obtiene la lista de productos con detalle de categoria (REQUIERE ROL ADMIN)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de admistrador"}), 403

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
        return jsonify(productos), 200
    except psycopg2.Error:
        return jsonify({"error": "Error al consultar productos"}), 500

@productos_bp.route("/apiu/productos", methods=["POST"])
def api_agregar_productos():
    """Registra un nuyevo producto en la base de datos y guarda su imagen (SOLO ADMIN)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    nombre = request.form.get("nombre")
    precio_raw = request.form.get("precio")
    stock_raw = request.form.get("stock")
    categoria = request.form.get("categoria_id")
    imagen = request.form.get("imagen")
    descripcion = request.form.get("descripcion")

    try:
        precio = float(precio_raw)
        stock = int(stock_raw)
        if precio < 0 or stock < 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Precio o stock invalido"}), 400

    nombre_imagen = "default.png"
    if imagen and imagen.filename != "":
        if not extension_permitida(imagen.filename):
            return jsonify({"error": "El archivo no es una imagen valida"}), 400
        if not es_imagen_valida(imagen):
            return jsonify({"error": "El archivo no es una imagen valida"}), 400
        nombre_imagen = secure_filename(imagen.filename)
        if nombre_imagen == "":
            return jsonify({"error": "Nombre de archivo no valido"}), 400

        # Guardado del archivo usando la carpeta UPLOAD_FOLDER configurada en la app
        imagen.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_imagen))


    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO producto (nombre, precio, stock, imagen, categori_id_categoria, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, precio, stock, nombre_imagen, categoria, descripcion)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Producto guardado correctamente"}), 201
    except psycopg2.Error:
        return jsonify({"error": "Error al agregar producto"}), 500


@productos_bp.route("/api/productos/<int:id>", methods=["DELETE"])
def api_eliminar_producto(id):
    """ Elimina productos mediante su ID (SOLO ADMIN)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Producto eliminado"}), 200
    except psycopg2.Error:
        return jsonify({"error": "Error al eliminar producto"}), 500