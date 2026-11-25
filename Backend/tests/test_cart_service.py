import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from services.cart_service import (
agregar_producto_al_carrito,
obtener_carrito_usuario,
actualizar_cantidad_en_carrito,
eliminar_producto_carrito,
vaciar_carrito,
insertar_en_carrito,
obtener_items_en_carrito
)

#Datos de prueba


USER_ID_TEST = 5
PRODUCT_ID_VALIDO = 4
PRODUCT_ID_INEXISTENTE = 9999
USER_ID_VACIO = 99999
PRODUCT_ID_TEST = 2

def test_agregar_cantidad_invalida():
    """ Verificar que lance error si la cantidad es <= 0."""
    with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
        agregar_producto_al_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, cantidad=0)

        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            agregar_producto_al_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, cantidad=-1)

def test_agregar_producto_inexistente():
    """Verificar que lance KeyError si el producto no existe en la BD."""
    with pytest.raises(KeyError):
        agregar_producto_al_carrito(USER_ID_TEST, PRODUCT_ID_INEXISTENTE, cantidad=1)


def test_agregar_superando_stock():
    """Verificar que lance ValueError si la cantidad supera el stock."""
    with pytest.raises(ValueError):
        agregar_producto_al_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, cantidad=100)

def test_obtener_carrito_usuario_invalido():
    """Verifica que se lance ValueError si el di_usuario es <= 0."""
    with pytest.raises(ValueError) as exc_info:
        obtener_carrito_usuario(0)

    assert "no es válido" in str(exc_info.value)

def test_obtener_carrito_calculos_correctos():
    """Verifica la estructura del diccionario y la exactitud matemática de subtotales"""
    resultado = obtener_carrito_usuario(USER_ID_TEST)

    assert isinstance(resultado, dict)
    assert resultado["id_usuario"] == USER_ID_TEST
    assert isinstance(resultado["items"], list)
    assert "cantidad_total" in resultado
    assert "total" in resultado

    #Verificar que la suma manueal de los subtotales coincida con el total retornado
    suma_subtotales = round(sum(item["subtotal"] for item in resultado ["items"]), 2)
    suma_cantidades = sum(item["cantidad"] for item in resultado["items"])

    assert resultado["total"] == suma_subtotales
    assert resultado["cantidad_total"] == suma_cantidades

    # Verificar que los precios y subtotales sean Floats.
    for item in resultado["items"]:
        assert isinstance(item["precio"], float)
        assert isinstance(item["subtotal"], float)
        assert item["subtotal"] == round(item["precio"] * item["cantidad"], 2)

def test_obtener_carrito_vacio():
    """Verifica que un usuario sin productos reciba una estructura limpia en ceros."""
    resultado = obtener_carrito_usuario(USER_ID_VACIO)

    assert resultado == {
        "id_usuario": USER_ID_VACIO,
        "items": [],
        "cantidad_total": 0,
        "total": 0.0
    }

def test_actualizar_cantidad_invalida():
    #Verifica que se lance error si la cantidad es invalida
    with pytest.raises(ValueError) as exc_info:
        actualizar_cantidad_en_carrito(1, 0, USER_ID_TEST)

    with pytest.raises(ValueError) as exc_info:
        actualizar_cantidad_en_carrito(1, -3, USER_ID_TEST)

def test_actualizar_item_inexistente():
    #Verifica que lance el error si el ID de usuario es invalido
    with pytest.raises(ValueError) as exc_info:
        actualizar_cantidad_en_carrito(9999, 2, USER_ID_TEST)

def test_actualizar_superando_el_stock():
    #Comprueba que se ejecute correctamente la verificación de stock existente en la base de datos
    items = obtener_items_en_carrito(USER_ID_TEST)
    if not items:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, 1)
    items = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = items[0]["id_carrito"]

    with pytest.raises(ValueError) as exc_info:
        actualizar_cantidad_en_carrito(id_carrito_real, 99999, USER_ID_TEST)

def test_actualizar_cantidad_exitosa():
    # Comprueba la respuesta si todo es correcto
    items = obtener_items_en_carrito(USER_ID_TEST)
    if not items:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, 1)
    items = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = items[0]["id_carrito"]

    resultado = actualizar_cantidad_en_carrito(id_carrito_real, 2, USER_ID_TEST)

    assert "mensaje" in resultado
    assert resultado["id_carrito"] == id_carrito_real
    assert resultado["nueva_cantidad"] == 2

def test_eliminar_producto_invalido_o_inexistente():
    with pytest.raises(ValueError) as exec_info:
        eliminar_producto_carrito(0, USER_ID_TEST)

    with pytest.raises(ValueError) as exec_info:
        eliminar_producto_carrito(99999, USER_ID_TEST)

def test_eliminar_producto_exitoso():
    item =obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, 1)
    item = obtener_items_en_carrito(USER_ID_TEST)
    id_a_borrar = item[0]["id_carrito"]
    resultado = eliminar_producto_carrito(id_a_borrar, USER_ID_TEST)

    assert "mensaje" in resultado
    assert resultado["id_carrito"] == id_a_borrar

def test_vaciar_carrito_usuario_invalido():
    with pytest.raises(ValueError) as exec_info:
        vaciar_carrito(0)

def test_vaciar_carrito_exitoso():
    insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, 1)
    resultado = vaciar_carrito(USER_ID_TEST)

    assert "mensaje" in resultado
    assert resultado["cantidad_eliminada"] >= 1
    assert obtener_items_en_carrito(USER_ID_TEST) == []

def test_actualizar_item_de_otro_usuario():
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST,PRODUCT_ID_TEST, 1)
    item = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = item[0]["id_carrito"]

    with pytest.raises(PermissionError):
        actualizar_cantidad_en_carrito(id_carrito_real, 2, 9999)

def test_borrar_producto_de_otro_usuario():
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, 1)
    item = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = item[0]["id_carrito"]

    with pytest.raises(PermissionError):
        eliminar_producto_carrito(id_carrito_real, 9999)