from database import obtener_conexion
from psycopg2.extras import RealDictCursor

def buscar_item(idusuario, id_producto):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id_carrito, cantidad
            FROM carrito
            WHERE id_usuario = %s AND id_producto = %s
        """,
            (idusuario, id_producto,)
        )
        producto =  cursor.fetchone()
        cursor.close()
        return producto
    except Exception as e:
        conexion.rollback()
        print(f"Error en la base de datos: {e}")
        raise e
    finally:
        conexion.close()


def insertar_en_carrito(idusuario, id_producto, cantidad):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
        INSERT INTO carrito (id_usuario, id_producto, cantidad)
        VALUES (%s, %s, %s)""",
        (idusuario, id_producto, cantidad)
        )
        conexion.commit()
        cursor.close()
    except Exception as e:
        conexion.rollback()
        print(f"Error en la base de datos: {e}")
        raise e
    finally:
        conexion.close()


def actualizar_item_en_carrito(id_carrito, nueva_cantidad):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
        UPDATE carrito
        SET cantidad = %s
        WHERE id_carrito = %s
        """,
        (nueva_cantidad, id_carrito)
        )
        conexion.commit()
        cursor.close()
    except Exception as e:
        conexion.rollback()
        print(f"Error en la base de datos: {e}")
        raise e
    finally:
        conexion.close()

def obtener_items_en_carrito (idusuario):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        cursor.execute("""
        SELECT
            c.id_carrito,
            c.id_usuario,
            c.id_producto,
            p.nombre,
            p.precio,
            p.imagen,
            c.cantidad,
            c.fecha_agregado
        FROM carrito c
        INNER JOIN producto p
            ON c.id_producto = p.id_producto
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_agregado DESC;
        """, (idusuario,))
        items = cursor.fetchall()
        cursor.close()
        return items
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        raise e
    finally:
        if conexion:
            conexion.close()

def buscar_item_por_id_carrito (id_carrito):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(cursor_factory = RealDictCursor)
        cursor.execute("""
        SELECT
            c.id_carrito, 
            c.id_usuario,
            c.id_producto,
            c.cantidad,
            p.stock
        FROM carrito c
        INNER JOIN producto p
            ON c.id_producto = p.id_producto
        WHERE c.id_carrito = %s
        """, (id_carrito,))
        item = cursor.fetchone()
        cursor.close()
        return item
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        raise e
    finally:
        if conexion:
            conexion.close()

def eliminar_item_del_carrito(id_carrito):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
        DELETE FROM carrito
        WHERE id_carrito = %s
        """, (id_carrito,))
        filas_eliminadas = cursor.rowcount
        conexion.commit()
        cursor.close()
        return filas_eliminadas > 0
    except Exception as e:
        conexion.rollback()
        print(f"Error en la base de datos {e}")
        raise e
    finally:
        if conexion:
            conexion.close()

def vaciar_carrito_usuario(id_usuario):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
        DELETE FROM carrito
        WHERE id_usuario = %s
        """, (id_usuario,))
        filas_eliminadas = cursor.rowcount
        conexion.commit()
        cursor.close()
        return filas_eliminadas
    except Exception as e:
        conexion.rollback()
        print(f"Error en la base de datos {e}")
        raise e
    finally:
        if conexion:
            conexion.close()