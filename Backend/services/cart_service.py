from services.productos_service import obtener_producto_por_id
from services.cart_repository import (
    buscar_item,
    insertar_en_carrito,
    actualizar_item_en_carrito,
    obtener_items_en_carrito
)

# Validar cantidad, que sea mayor a cero
def agregar_producto_al_carrito (idusuario, id_producto, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0.")
#  Buscar producto y validar que exista

    producto = obtener_producto_por_id(id_producto)
    if not producto:
        raise KeyError("El producto no existe")
#  Validar si hay stock disponible
    if producto['stock'] < cantidad:
        raise ValueError("No hay suficiente stock disponible.")

    # Buscar si ya existe en el carrito 

    item = buscar_item(idusuario, id_producto)
    if not item:
        insertar_en_carrito(idusuario, id_producto, cantidad)

    else:
        nueva_cantidad = item['cantidad'] + cantidad

        if nueva_cantidad > producto['stock']:
            raise ValueError("La cantidad total supera el stock disponible")

        actualizar_item_en_carrito(item['id_carrito'], nueva_cantidad)

def obtener_carrito_usuario(id_usuario):
    if not id_usuario or id_usuario <= 0:
        raise ValueError("El ID de usuario no es válido")

    items_en_carrito = obtener_items_en_carrito(id_usuario)

    items_procesados = []
    total_carrito = 0.0
    cantidad_total = 0

    for item in items_en_carrito:
        precio = float(item["precio"])
        cantidad = int(item["cantidad"])
        subtotal = round(precio * cantidad, 2)

        total_carrito += subtotal
        cantidad_total += cantidad

        items_procesados.append({
            "id_carrito": item["id_carrito"],
            "id_producto": item["id_producto"],
            "nombre": item["nombre"],
            "precio": precio,
            "imagen": item["imagen"],
            "cantidad": cantidad,
            "subtotal": subtotal
        })

    return {
        "id_usuario": id_usuario,
        "items": items_procesados,
        "cantidad_total": cantidad_total,
        "total": round(total_carrito, 2)
        }