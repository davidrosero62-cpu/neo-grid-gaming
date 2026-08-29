# ==============================================================================
# RUTAS DE GESTIÓN DE CATEGORÍAS
# ==============================================================================

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Blueprint, jsonify

from database import obtener_conexion

# Instancia del Blueprint para Categorías
categorias_bp = Blueprint('categorias', __name__)

@categorias_bp.route("/api/categorias", methods=["GET"])
def api_categorias():
    """Obtiene el listado completo de categorías registradas."""
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(categorias), 200
    except psycopg2.Error:
        return jsonify({"error": "Error al consultar categorias"}),500