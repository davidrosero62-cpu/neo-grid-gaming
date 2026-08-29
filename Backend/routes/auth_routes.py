# ==============================================================================
# RUTAS DE AUTENTICACIÓN Y REGISTRO DE USUARIOS
# ==============================================================================

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import re
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errorcodes

# Importaciones locales del proyecto
from database import obtener_conexion
from utils.cookies import set_cookie_token, ES_PRODUCCION
from extensions import limiter  # <--- IMPORTANTE: Importamos el limiter

# Creación del Blueprint de Autenticación
auth_bp = Blueprint('auth', __name__)

# Expresión regular para validar el formato de correo electrónico
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@auth_bp.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    """Ruta para inciar sesión y generar el token JWT """
    data = request.json
    correo = data.get("correo")
    password = data.get("password")

    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios."}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT idusuario, password, rol FROM usuario WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        # Validación de la contraseña encriptada
        if usuario and check_password_hash(usuario["password"], password):
            # Generacion de token JWT válido por 24 horas
            token = jwt.encode({
                'idusuario': usuario['idusuario'],
                'rol': usuario['rol'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, os.environ.get('SECRET_KEY'), algorithm='HS256')

            response = jsonify({
                "mensaje": "inicio de sesión exitoso",
                "rol": usuario["rol"],
                "idusuario": usuario["idusuario"]
            })
            return set_cookie_token(response, token), 200
        else:
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    except psycopg2.Error as err:
        print("Error en login:", err)
        return jsonify ({"error": "error en la base de datos"}), 500

@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    """Ruta para cerrar sesión eliminando la cookie del token"""
    response = jsonify({"mensaje": "Sesión cerrada correctamente"})
    response.set_cookie(
        key="token",
        value="",
        httponly=True,
        secure=ES_PRODUCCION,
        samesite="None" if ES_PRODUCCION else "Lax",
        max_age=0,
        expires=0
    )
    return response, 200

@auth_bp.route("/api/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    """ Ruta para registrar nuevos usuarios clientes en el sistema."""
    datos = request.get_json()

    if not datos or not all(k in datos for k in ("nombre", "email", "password")):
        return jsonify({"error": "Faltan datos requeridos (nombre, email, password)"}), 400

    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "El formato del correo no es valido"}), 400

    if len(password) < 8:
        return jsonify({"error": "La contraseña debe contener almenos 8 caracteres."}), 400

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        password_seguro = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuario (nombres, correo, password, rol) VALUES (%s, %s, %s, 'cliente')",
            (nombre, email, password_seguro)
        )
        conexion.commit()

        return jsonify({
            "status": "success",
            "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada"
        }), 201

    except psycopg2.Error as err:
        if conexion:
            conexion.rollback()
            # Manejo de error para correo duplicado (Código SQLSTATE 23505)
            if err.pgcode == errorcodes.UNIQUE_VIOLATION:
                return jsonify({
                    "status": "success",
                    "mensaje": "Si el correo no estaba registrado, tu cuenta ha sido creada"
                }), 201
            else:
                print("Error inesperado en registro", err)
                return jsonify({"error", "Ocurrió un error al procesar el registro"}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()