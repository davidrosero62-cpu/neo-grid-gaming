import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from services.cart_service import (
agregar_producto_al_carrito,
obtener_carrito_usuario
)

#Datos de prueba


USER_ID_TEST = 1
PRODUCT_ID_VALIDO = 4
PRODUCT_ID_INEXISTENTE = 9999
USER_ID_VACIO = 99999


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
    """Verifica la estrucira del diccionario y la exactitud matemática de subtotales"""
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
