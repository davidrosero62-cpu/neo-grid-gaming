import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from services.cart_service import (
    insertar_en_carrito,
    obtener_items_en_carrito
)

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

def test_route_obtener_carrito_exitoso(client):
    """Verifica que GET /api/cart/<id_usuario> retorne 200 ok y la estructura esperada"""
    response = client.get(f"/api/cart/{USER_ID_TEST}")

    assert response.status_code == 200
    data = response.get_json()

    assert data["id_usuario"] == USER_ID_TEST
    assert isinstance(data["items"], list)
    assert "cantidad_total" in data
    assert "total" in data

def test_route_obtener_carrito_usuario_invalido(client):
    """Verifica qie un ID de usuario igual a 0 restorne Bad Request"""
    response = client.get("/api/cart/0")

    assert response.status_code ==400
    data = response.get_json()
    assert "error" in data

def test_route_actualizar_cantidad_exitoso(client):
    items = obtener_items_en_carrito(USER_ID_TEST)
    if not items:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
        items = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = items[0]["id_carrito"]
    response = client.put(f"/api/cart/update/{id_carrito_real}", json={"cantidad": 2})

    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["nueva_cantidad"] == 2

def test_route_actualizar_cantidad_invalida(client):
    response = client.put("/api/cart/update/1", json={"cantidad": 0})
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data

def test_route_eliminar_item_exitoso(client):
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
        item = obtener_items_en_carrito(USER_ID_TEST)
    id_a_borrar = item[0]["id_carrito"]
    response = client.delete(f"/api/cart/remove/{id_a_borrar}")
    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["id_carrito"] == id_a_borrar

def test_route_eliminar_item_inexistente(client):
    response = client.delete("/api/cart/remove/9999")
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data

def test_route_vaciar_carrito_exitoso (client):
    insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
    response = client.delete(f"/api/cart/clear/{USER_ID_TEST}")
    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["cantidad_eliminada"] >= 1
    assert obtener_items_en_carrito(USER_ID_TEST) == []

def test_route_vaciar_carrito_usuario_invalido(client):
    response = client.delete("/api/cart/clear/0")
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data