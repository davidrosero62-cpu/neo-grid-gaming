import os
import psycopg2

def obtener_conexion():
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conexion = psycopg2.connect(database_url)
        else:
            conexion = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT", "5432")
            )
            return conexion
    except psycopg2.Error as err:
        print(f"Error detallado de conexión: {err}")
        raise err