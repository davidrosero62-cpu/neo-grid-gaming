# ==============================================================================
# SERVICIO DE LÓGICA DE NEGOCIO Y CONSULTAS DE PRODUCTOS
# ==============================================================================

import psycopg2
from psycopg2.extras import RealDictCursor
from database import obtener_conexion


def obtener_todos_los_productos():
    """Consulta todos los productos registrados (para catálogo general)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.close()
        return productos
    finally:
        conexion.close()


def obtener_productos_con_categoria():
    """Consulta la lista de productos unida a su categoría (para panel admin)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.stock, p.imagen, p.descripcion,
                   p.categoria_id_categoria, c.nombre_categoria
            FROM producto p
            INNER JOIN categoria c ON p.categoria_id_categoria = c.id_categoria
        """)
        productos = cursor.fetchall()
        cursor.close()
        return productos
    finally:
        conexion.close()


def crear_producto(nombre, precio, stock, nombre_imagen, categoria, descripcion):
    """Inserta un nuevo producto en la base de datos."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO producto (nombre, precio, stock, imagen, categoria_id_categoria, descripcion)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (nombre, precio, stock, nombre_imagen, categoria, descripcion)
        )
        conexion.commit()
        cursor.close()
    except Exception as err:
        conexion.rollback()
        raise err
    finally:
        conexion.close()


def eliminar_producto_por_id(id_producto):
    """Elimina un producto mediante su ID."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        cursor.close()
    except Exception as err:
        conexion.rollback()
        raise err
    finally:
        conexion.close()