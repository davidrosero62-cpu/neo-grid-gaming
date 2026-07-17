**Neo Grid Gaming** es una plataforma de comercio electrónico orientada al sector gamer, estructurada bajo una arquitectura desacoplada que separa de manera estricta las capas de presentación y lógica de negocio. El proyecto cuenta con un catálogo dinámico orientado al usuario final, un sistema robusto de autenticación basado en tokens, herramientas de accesibilidad nativas y un panel administrativo completo (CRUD) para la gestión física del inventario multimedia.

---

## 🛠️ Arquitectura y Tecnologías Clave

### Backend (API REST)
*   **Core:** Python 3 + Flask (Estructuración modular de endpoints de consumo exclusivo JSON).
*   **Seguridad:** 
    *   **Autenticación:** Implementación de **JSON Web Tokens (JWT)** con algoritmo de firma `HS256` y expiración automatizada a 24 horas.
    *   **Rate Limiting:** Control de flujo mediante `Flask-Limiter` en rutas críticas (`/api/register`) restringido a un máximo de 3 peticiones por minuto por IP para evitar ataques de fuerza bruta o de denegación de servicio (DoS).
    *   **Cifrado de Contraseñas:** Hashing criptográfico mediante funciones seguras de derivación de claves (`werkzeug.security`).
    *   **Sanitización de Archivos:** Implementación de `secure_filename` y listas blancas explícitas para mitigar vulnerabilidades de Path Traversal o ejecución remota de comandos en la carga de archivos multimedia.
*   **Base de Datos:** MySQL integrado mediante el conector nativo relacional `mysql.connector`.
*   **CORS:** Habilitación de políticas de intercambio de recursos de origen cruzado (`Flask-CORS`) para permitir la comunicación fluida con clientes SPA (Single Page Applications).

### Frontend (SPA)
*   **Core:** React + JavaScript estructurado en componentes modulares, funcionales y altamente reutilizables[cite: 2, 3, 4, 5].
*   **Enrutamiento:** `react-router-dom` para la gestión interna de rutas del lado del cliente, previniendo recargas completas del navegador y optimizando la experiencia de usuario[cite: 2, 7, 8].
*   **Gestión de Estado:** Manejo de estados locales (`useState`) y efectos secundarios (`useEffect`) para sincronizar consumos asíncronos distribuidos a la API (`fetch`)[cite: 2, 9].
*   **Accesibilidad (A11y):** Incorporación de un menú nativo para el control dinámico del tamaño de fuente en toda la aplicación y switch de contraste para cumplimiento básico de accesibilidad visual[cite: 8].

---

## 📐 Diseño de la Base de Datos (Esquema Relacional)

La base de datos se rige por la consistencia transaccional y relaciones estrictas:

*   **`usuario`**: Almacena credenciales, datos de identidad y roles de acceso (`'admin'`, `'cliente'`)[cite: 1].
*   **`categoria`**: Clasificación jerárquica para la indexación de los artículos[cite: 1].
*   **`producto`**: Catálogo físico de la tienda. Mantiene una llave foránea (`categoria_id_categoria`) apuntando hacia la entidad `categoria` (`1:N`)[cite: 1].

---

## 🚀 Instalación y Configuración Local

### Prerrequisitos
*   Python 3.10 o superior instalado.
*   Node.js v18 o superior instalado.
*   Servidor MySQL activo (Local o en la nube).

### 1. Clonar el Repositorio e Instalar el Backend
```bash
# Clonar proyecto
git clone [https://github.com/tu-usuario/neo-grid-gaming.git](https://github.com/tu-usuario/neo-grid-gaming.git)
cd neo-grid-gaming/backend

# Crear un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias requeridas
pip install -r requirements.txt

### 2. Configurar Variables de Entorno (.env)
Crea un archivo llamado `.env` en la raíz de la carpeta `backend/` y configura tus credenciales de la siguiente manera:
```env
DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=neo_grid_gaming
SECRET_KEY=una_clave_secreta_muy_segura_para_jwt
```

### 3. Instalar y Levantar el Frontend
```bash
# Navegar a la carpeta del frontend
cd ../frontend

# Instalar las dependencias de Node.js
npm install

# Iniciar el servidor de desarrollo local
npm run dev
```
El cliente React estará disponible en `http://localhost:5173`.

---

## 🚀 Especificación de la API (Endpoints REST)

Todas las peticiones de escritura y rutas protegidas requieren las cabeceras `Content-Type: application/json` y el token de autenticación según corresponda.

### 🔐 Autenticación y Usuarios
*   `POST /api/register` -> Registro de nuevos clientes. (Protegido con Rate Limiting: max 3 peticiones/min per IP).
*   `POST /api/login` -> Autenticación de usuarios. Retorna un objeto JSON con el token JWT si las credenciales coinciden con el hash criptográfico.

### 🛒 Gestión del Catálogo (Público)
*   `GET /api/products` -> Obtiene la lista completa de productos gamers indexados con su respectiva categoría.
*   `GET /api/products/<id>` -> Retorna el detalle físico y multimedia de un producto específico.

### 🛠️ Operaciones CRUD Administrativas (Protegidas)
*Las siguientes rutas requieren el rol `'admin'` dentro del token JWT para ser ejecutadas:*
*   `POST /api/products` -> Inserta un nuevo artículo gamer en el catálogo (Soporta carga de imágenes sanitizadas).
*   `PUT /api/products/<id>` -> Actualiza de forma parcial o total la información del producto.
*   `DELETE /api/products/<id>` -> Eliminación persistente del registro en MySQL.

---

## 🔒 Buenas Prácticas y Estándares Implementados
*   **Manejo de Errores Limpio:** Las fallas del servidor (500) y de base de datos no exponen trazas internas (*stack traces*) al cliente; retornan mensajes genéricos sanitizados para mitigar fugas de información.
*   **Separación de Conceptos:** Estricto desacoplamiento de capas; el frontend se comunica exclusivamente con la API mediante peticiones asíncronas (`fetch`).
