Documentacion tecnica: Neo Grid Gaming

1. Arquitectura del sistema

El proyecto esta construido bajo una arqutectura desacoplada Cliente-Servidor (Full Stack), separando completamente la lógica del negocio del diseño visual:

- Frontend(Cliente): Desarrollado en React (utilizando Vite como empaquetador), encargado de renderizar la interfaz de usuario en el puerto 5173.

-Backend(Servidor/API REST): Desarrollado con Python con Flask, encargado de gestionar las reglas de negocio, la seguridad (Criptografia, limitador de peticiones) y servir los daots puros en formato JSON en el puerto 5000.

-Base de datos: Relacional, gestionada en MySQL, encargada del almacenamiento persistente del inventario, usuarios y transacciones.

2. Requisitos Previos Y Dependencias

Para desplegar el entorno de desarrollo profesional, el sistema requiere las sieguientes herramientas:

Backend(Python 3.x)
- flask: Microframework para la creacion de la API.
- flask-cors: Extension para habilitar el intercambio de recursos de origen cruzado (CORS) y permitir que React (puerto 5173) consuma recursos de Flask (puerto 5000).
- flask-limiter: Modulo de seguridad para mitigar ataques de fuerza bruta limitando las peticiones por IP.
- mysql-connector-python: Controlador oficial para conectar Python con el servidor MySQL.
-python-dotenv: Gestor de variables de entorno para proteger credenciales sensibles de la base de datos.

Frontend (Node.js & npm)
- react & react-dom: Libreria base para la construccion de insterfaces mediante componentes.
- vite: Herramienta de construccion rapida para el entorno de desarrollo.

3. Variables de entorno (.env)

Por seguridad y buenas practicas de desarrollo, las credenciales de acceso no se hardcodean en el codigo. El archivo .env en la raiz de la carpeta Backend debe tener la siguiente estructura estandarizada:

DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=neo_grid_gaming
SECRET_KEY=una_clave_secreta_muy_segura

4. Historial de Endpoints de la API (Backend)

GET/
- Descripcion: Consulta el inventario general de articulos disponibles en la tienda.
- Codigo de respuesta exitosa: 200 OK (devuelve un arreglo de objetos JSON).
- Codigo de respuesta erronea: 500 Internal Server Error (Devuelve un JSON coon el detalle tecnico del fallo en MySQL).


