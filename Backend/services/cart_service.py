from services.productos_service import obtener_producto_por_id
from services.cart_repository import (
    buscar_item,
    insertar_en_carrito,
    actualizar_item_en_carrito,
    obtener_items_en_carrito,
    buscar_item_por_id_carrito,
    eliminar_item_del_carrito,
    vaciar_carrito_usuario,
)

# Validar cantidad, que sea mayor a cero
def agregar_producto_al_carrito (idusuario, id_producto, cantidad):
    if not isinstance(cantidad, int) or isinstance(cantidad, bool):
        raise ValueError("la cantidad debe ser un entero.")
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

        actualizar_item_en_carrito(item['id_carrito'], nueva_cantidad, idusuario)

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

def actualizar_cantidad_en_carrito(id_carrito, nueva_cantidad, id_usuario):
    if not id_carrito or id_carrito <= 0:
        raise ValueError ("El ID del carrito no es válido")
    if isinstance(nueva_cantidad, bool) or not isinstance(nueva_cantidad, int) or nueva_cantidad <= 0:
        raise ValueError("La cantidad debe ser un entero mayor a 0")

    item = buscar_item_por_id_carrito(id_carrito)
    if item is None:
        raise ValueError("El ítem no existe en el carrito")
    
    if item["id_usuario"] != id_usuario:
        raise PermissionError("No tienes permiso para modificar este ítem del carrito")

    if nueva_cantidad > item["stock"]:
        raise ValueError(f"Stock insuficiente, stock disponible: {item['stock']}")

    actualizado = actualizar_item_en_carrito(id_carrito, nueva_cantidad, id_usuario)
    if not actualizado:
        raise ValueError("No se pudo actualizar el articulo del carrito")
    
    return {
        "mensaje" : "producto actualizado con éxito",
        "id_carrito" : id_carrito,
        "nueva_cantidad" : nueva_cantidad 
        
    }

def eliminar_producto_carrito(id_carrito, id_usuario):
    if not id_carrito or id_carrito <= 0:
        raise ValueError("El ID del carrito no es válido")
    item = buscar_item_por_id_carrito(id_carrito)
    if item is None:
        raise ValueError("Producto no encotrado en el carrito")
    if item["id_usuario"] != id_usuario:
        raise PermissionError("No tienes permiso para eliminar este item del carrito")
    eliminado = eliminar_item_del_carrito(id_carrito)
    if not eliminado:
        raise ValueError("Producto no encontrado en el carrito")
    return {
        "mensaje" : "Producto eliminado exitosamente",
        "id_carrito" : id_carrito
    }

def vaciar_carrito(id_usuario):
    if not id_usuario or id_usuario <= 0:
        raise ValueError("El ID de usuario es inválido")
    cantidad_eliminada = vaciar_carrito_usuario(id_usuario)
    return {
        "mensaje" : "Carrito vaciado con éxito",
        "cantidad_eliminada" : cantidad_eliminada
    }