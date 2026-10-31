import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from services.cart_service import agregar_producto_al_carrito

#Datos de prueba


USER_ID_TEST = 1
PRODUCT_ID_VALIDO = 4
PRODUCT_ID_INEXISTENTE = 9999


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