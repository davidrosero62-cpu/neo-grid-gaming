# ==============================================================================
# RUTAS PARA LA GESTION DEL CARRITO
# ==============================================================================

import os
from flask import Blueprint, jsonify, request
from services.cart_service import (
    agregar_producto_al_carrito,
    obtener_carrito_usuario,
    actualizar_cantidad_en_carrito,
    eliminar_producto_carrito,
    vaciar_carrito
)

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

    # Error de producto no encontrado en la base de datos
    except KeyError as e:
        return jsonify({"error": "El producto especificado no existe"}), 404

    # Errores no controlados de la base de datos
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
    

@cart_bp.route('/cart/<int:id_usuario>', methods =['GET'])
def obtener_carrito(id_usuario):
    try:
        carrito_usuario = obtener_carrito_usuario(id_usuario)
        return jsonify(carrito_usuario), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Error del servidor:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

@cart_bp.route('/cart/update/<int:id_carrito>', methods =["PUT"])
def actualizar_cantidad(id_carrito):
    try:
        data = request.get_json(silent=True)
        if data is None or "cantidad" not in data:
            return jsonify({"error": "El cuerpo de la petición debe ser un JSON válido"}), 400
        nueva_cantidad = data["cantidad"]
        resultado = actualizar_cantidad_en_carrito(id_carrito, nueva_cantidad)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Error del servidor:", e)
        return jsonify({"error": "Error interno al actualizar el carrito"}), 500

@cart_bp.route('/cart/remove/<int:id_carrito>', methods = ["DELETE"])
def elimininar_item(id_carrito):
    try:
        resultado = eliminar_producto_carrito(id_carrito)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Error del servidor:", e)
        return jsonify({"error": "Error interno al actualiza el carrito"}), 500

@cart_bp.route('/cart/clear/<int:id_usuario>', methods=["DELETE"])
def limpiar_carrito(id_usuario):
    try:
        resultado = vaciar_carrito(id_usuario)
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print("Error del servidor", e)
        return jsonify({"error": "Error interno al actualizar el carrito"}), 500