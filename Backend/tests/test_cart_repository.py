import sys
import os
import pytest


# Asegura que Python encuentre las carpetas del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from dotenv import load_dotenv
load_dotenv()


from services.cart_repository import (
    buscar_item,
    insertar_en_carrito,
    actualizar_item_en_carrito,
    obtener_items_en_carrito
)


# Datos de prueba para aislar el test
USER_ID_TEST = 5
PRODUCT_ID_TEST = 5

def test_insertar_y_buscar_item():
    """Prueba si un item existe, buscar_item lo retorna correctamente"""
    item = buscar_item(USER_ID_TEST, PRODUCT_ID_TEST)

    #Si no existe, lo inserta para asegurar la prueba
    if item is None:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, cantidad=2)
        item = buscar_item(USER_ID_TEST, PRODUCT_ID_TEST)


    assert item is not None
    assert 'id_carrito' in item
    assert 'cantidad' in item

def test_actualizar_cantidad_item():
    """Prueba que se actualice la cantidad de un item existente por su id_carrito"""
    item = buscar_item(USER_ID_TEST, PRODUCT_ID_TEST)

    #Asegurar de tener el id_carrito
    if item is None:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_TEST, cantidad=2)
        item = buscar_item(USER_ID_TEST, PRODUCT_ID_TEST)

    id_carrito = item['id_carrito']


    # Actualizar a una nueva cantidad conocida
    actualizar_item_en_carrito(id_carrito, nueva_cantidad=5)

    # Verificar que la BD tenga exactamente el valor 5
    item_actualizado = buscar_item(USER_ID_TEST, PRODUCT_ID_TEST)
    assert item_actualizado['cantidad'] == 5

def test_obtener_items_en_carrito():
    """ Verifica que la consulta con INNER JOIN retorne los items con los datos del producto """
    items = obtener_items_en_carrito (USER_ID_TEST)

    assert isinstance(items, list)

    # Validar la estructura del RealDictCursor (Si hay productos en carrito)
    if len(items) > 0:
        primer_item = items[0]
        assert "id_carrito" in primer_item
        assert "nombre" in primer_item
        assert "precio" in primer_item
        assert "imagen" in primer_item
        assert "cantidad" in primer_item

