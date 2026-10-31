# ==============================================================================
# RUTAS PARA LA GESTION DEL CARRITO
# ==============================================================================

import os
from flask import Blueprint, jsonify, request
from services.cart_service import agregar_producto_al_carrito

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/add', methods=['POST'])
def agregar_al_carrito_route():
    data= request.get_json()

    if not data:
        return jsonify({"error": "El cuerpo de la petición debe ser un JSON válido"}), 400

    id_usuario = data.get('id_usuario')
    id_producto = data.get('id_producto')
    cantidad = data.get('cantidad')

    try:
        resultado = agregar_producto_al_carrito(id_usuario, id_producto, cantidad)
        return jsonify({
            "mensaje": "Producto agregado al carrito exitosamente",
            "item": resultado
        }), 200
    # Errores de validación de cantidad
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Error de producto no encontrado ebn la base de datos
    except KeyError as e:
        return jsonify({"error": "El producto especificado no existe"}), 404

    # Errores no controlados de la base de datos
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500