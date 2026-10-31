import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

# Importar instacia de Flask
from app import app

USER_ID_TEST = 5
PRODUCT_ID_VALIDO = 5
PRODUCTO_ID_INEXISTENTE = 900

@pytest.fixture
def client():
    """Configura el cliente de pruebas de Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_route_agregar_producto_exitoso(client):
    """Verifica que el endpoint responda 200 ok con un JSON valido """
    payload = {
        "id_usuario": USER_ID_TEST,
        "id_producto": PRODUCT_ID_VALIDO,
        "cantidad": 1
    }
    response = client.post('/api/cart/add', json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert "mensaje" in json_data

def test_route_agregar_cantidad_invalida(client):
    """Verifica que responda 400 Bad Request si la cantidad es <= 0. """
    payload = {
        "id_usuario": USER_ID_TEST,
        "id_producto": PRODUCT_ID_VALIDO,
        "cantidad": 0

    }
    response = client.post('/api/cart/add', json=payload)

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_route_agregar_producto_inexistente(client):
    """Verifica que responda 404 Not Found si el producto no existe"""
    payload = {
        "id_usuario": USER_ID_TEST,
        "id_producto": PRODUCTO_ID_INEXISTENTE,
        "cantidad": 1
    }
    response = client.post('/api/cart/add', json=payload)

    assert response.status_code == 404
    json_data = response.get_json()
    assert "error" in json_data