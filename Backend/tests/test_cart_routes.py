import sys
import os
import pytest
import jwt
import datetime

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

@pytest.fixture
def auth_client():
    secret = app.config['SECRET_KEY']
    token = jwt.encode({
        'idusuario': USER_ID_TEST,
        'rol': 'cliente',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, secret, algorithm='HS256')
    app.config['TESTING'] = True
    with app.test_client() as client:
        client.set_cookie('token', token)
        yield client



def test_route_agregar_producto_exitoso(auth_client):
    """Verifica que el endpoint responda 200 ok con un JSON valido """
    payload = {
        "id_producto": PRODUCT_ID_VALIDO,
        "cantidad": 1
    }
    response = auth_client.post('/api/cart/add', json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert "mensaje" in json_data

def test_route_agregar_cantidad_invalida(auth_client):
    """Verifica que responda 400 Bad Request si la cantidad es <= 0. """
    payload = {
        "id_producto": PRODUCT_ID_VALIDO,
        "cantidad": 0

    }
    response = auth_client.post('/api/cart/add', json=payload)

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_route_agregar_producto_inexistente(auth_client):
    """Verifica que responda 404 Not Found si el producto no existe"""
    payload = {
        "id_producto": PRODUCTO_ID_INEXISTENTE,
        "cantidad": 1
    }
    response = auth_client.post('/api/cart/add', json=payload)

    assert response.status_code == 404
    json_data = response.get_json()
    assert "error" in json_data

def test_route_obtener_carrito_exitoso(auth_client):
    """Verifica que GET /api/cart/<id_usuario> retorne 200 ok y la estructura esperada"""
    response = auth_client.get("/api/cart")

    assert response.status_code == 200
    data = response.get_json()

    assert data["id_usuario"] == USER_ID_TEST
    assert isinstance(data["items"], list)
    assert "cantidad_total" in data
    assert "total" in data

def test_route_actualizar_cantidad_exitoso(auth_client):
    items = obtener_items_en_carrito(USER_ID_TEST)
    if not items:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
        items = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = items[0]["id_carrito"]
    response = auth_client.put(f"/api/cart/update/{id_carrito_real}", json={"cantidad": 2})

    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["nueva_cantidad"] == 2

def test_route_actualizar_cantidad_invalida(auth_client):
    response = auth_client.put("/api/cart/update/1", json={"cantidad": 0})
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data

def test_route_eliminar_item_exitoso(auth_client):
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
        item = obtener_items_en_carrito(USER_ID_TEST)
    id_a_borrar = item[0]["id_carrito"]
    response = auth_client.delete(f"/api/cart/remove/{id_a_borrar}")
    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["id_carrito"] == id_a_borrar

def test_route_eliminar_item_inexistente(auth_client):
    response = auth_client.delete("/api/cart/remove/9999")
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data

def test_route_vaciar_carrito_exitoso (auth_client):
    insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 1)
    response = auth_client.delete("/api/cart/clear")
    data = response.get_json()

    assert response.status_code == 200
    assert "mensaje" in data
    assert data["cantidad_eliminada"] >= 1
    assert obtener_items_en_carrito(USER_ID_TEST) == []

def test_agregar_carrito_sin_autenticacion(client):
    response = client.post("/api/cart/add", json={"id_producto": PRODUCT_ID_VALIDO, "cantidad": 1})
    assert response.status_code == 401
    assert "error" in response.get_json()

def test_ver_carrito_sin_autenticacion(client):
    response = client.get("/api/cart")
    assert response.status_code == 401
    assert "error" in response.get_json()

def test_route_actualizar_item_ajeno_forbidden(auth_client):
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 2)
    item = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = item[0]["id_carrito"]

    secret = app.config['SECRET_KEY']
    token_no_autorizado = jwt.encode({
        'idusuario': 9999,
        'rol': 'cliente',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

    }, secret, algorithm='HS256')

    auth_client.set_cookie('token', token_no_autorizado)

    response = auth_client.put(f"/api/cart/update/{id_carrito_real}", json={"cantidad": 3})

    assert response.status_code == 403
    assert "error" in response.get_json()

def test_route_eliminar_item_ajeno_forbidden(auth_client):
    item = obtener_items_en_carrito(USER_ID_TEST)
    if not item:
        insertar_en_carrito(USER_ID_TEST, PRODUCT_ID_VALIDO, 2)
    item = obtener_items_en_carrito(USER_ID_TEST)
    id_carrito_real = item[0]["id_carrito"]

    secret = app.config['SECRET_KEY']
    token_no_autorizado = jwt.encode({
        'idusuario': 999,
        'rol': 'cliente',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, secret, algorithm='HS256')

    auth_client.set_cookie('token', token_no_autorizado)

    response = auth_client.delete(f"/api/cart/remove/{id_carrito_real}")

    assert response.status_code == 403
    assert "error" in response.get_json()
    