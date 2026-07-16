from werkzeug.security import generate_password_hash
import mysql.connector

# Conexión a tu base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",      # Cambia esto
    password="280916S@ra",  # Cambia esto
    database="db_neo_grid_gaming"
)

cursor = conexion.cursor(dictionary=True)

# 1. Traemos todos los usuarios
cursor.execute("SELECT idusuario, password FROM usuario")
usuarios = cursor.fetchall()

# 2. Convertimos y actualizamos
for u in usuarios:
    # Solo las convertimos si no parecen un hash ya (no empiezan con 'pbkdf2:')
    if not u['password'].startswith('pbkdf2:'):
        nuevo_hash = generate_password_hash(u['password'])
        cursor.execute("UPDATE usuario SET password = %s WHERE idusuario = %s", (nuevo_hash, u['idusuario']))
        print(f"Usuario {u['idusuario']} actualizado.")

conexion.commit()
cursor.close()
conexion.close()
print("¡Migración completada con éxito!")