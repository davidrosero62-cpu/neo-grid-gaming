# ==============================================================================
# RUTAS DE GESTIÓN DE PRODUCTOS Y CATÁLOGO (Solo HTTP)
# ==============================================================================

import os
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

# Servicios y Helpers
from services.imagenes_service import es_imagen_valida, extension_permitida
from services.productos_service import (
    obtener_todos_los_productos,
    obtener_productos_con_categoria,
    crear_producto,
    eliminar_producto_por_id
)
from utils.auth_helpers import obtener_usuario_desde_token

productos_bp = Blueprint('productos', __name__)


@productos_bp.route("/", methods=["GET"])
def index():
    """Ruta del catálogo general público."""
    try:
        productos = obtener_todos_los_productos()
        return jsonify(productos), 200
    except Exception:
        return jsonify({"error": "Error al conectar con la base de datos"}), 500


@productos_bp.route("/api/productos", methods=["GET"])
def api_productos():
    """Obtiene la lista de productos con detalle de categoría (Requiere rol Admin)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    try:
        productos = obtener_productos_con_categoria()
        return jsonify(productos), 200
    except Exception:
        return jsonify({"error": "Error al consultar productos"}), 500


@productos_bp.route("/api/productos", methods=["POST"])
def api_agregar_productos():
    """Registra un nuevo producto en la base de datos y guarda su imagen (Solo Admin)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

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
        return jsonify({"error": "Precio o Stock invalido"}), 400

    nombre_imagen = "default.png"
    if imagen and imagen.filename != "":
        if not extension_permitida(imagen.filename):
            return jsonify({"error": "El archivo no es una imagen valida"}), 400
        if not es_imagen_valida(imagen):
            return jsonify({"error": "El archivo no es una imagen valida"}), 400
        nombre_imagen = secure_filename(imagen.filename)
        if nombre_imagen == "":
            return jsonify({"error": "Nombre de archivo no valido"}), 400
        imagen.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_imagen))

    try:
        crear_producto(nombre, precio, stock, nombre_imagen, categoria, descripcion)
        return jsonify({"mensaje": "Producto guardado correctamente"}), 201
    except Exception as err:
        print("Error al agregar producto:", err)
        return jsonify({"error": "Error al agregar producto"}), 500


@productos_bp.route("/api/productos/<int:id>", methods=["DELETE"])
def api_eliminar_producto(id):
    """Elimina un producto mediante su ID (Solo Admin)."""
    usuario = obtener_usuario_desde_token()
    if not usuario or usuario.get("rol") != "admin":
        return jsonify({"error": "Acceso denegado: Se requieren permisos de administrador"}), 403

    try:
        eliminar_producto_por_id(id)
        return jsonify({"mensaje": "Producto eliminado"}), 200
    except Exception:
        return jsonify({"error": "Error al eliminar el producto"}), 500