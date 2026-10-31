# 🎮 Neo Grid Gaming

**Neo Grid Gaming** es una plataforma de comercio electrónico orientada al sector gamer, desarrollada bajo una **arquitectura desacoplada y en capas (Clean Architecture)** que separa la capa de presentación de la lógica de negocio mediante una API RESTful en Flask.

El proyecto está compuesto por un frontend SPA en React, un backend en Flask estructurado modularmente mediante Blueprints, Services y Repositorios, y una base de datos relacional en PostgreSQL alojada en la nube, ofreciendo una arquitectura escalable, segura y totalmente probada mediante un conjunto de pruebas automatizadas con **Pytest**.

Actualmente, el backend de producción se encuentra desplegado en **Render** y conectado a la base de datos de **Supabase**.

---

## 📌 Características

- 🔐 **Autenticación basada en Cookies HttpOnly:** Almacenamiento seguro de JWT para mitigar ataques de tipo XSS.
- 🛡️ **Prevención de Enumeración de Usuarios:** Respuestas genéricas en el registro para evitar fugas de información.
- 🛒 **Módulo Completo de Carrito de Compras:** Gestión en tres capas con acumulación de productos y validación estricta de stock en tiempo real.
- 🧪 **Suite de Pruebas Automatizadas (Pytest):** Cobertura total a nivel de datos (SQL), servicios (lógica de negocio) y controladores HTTP (Flask `test_client`).
- 🛒 **Catálogo Dinámico de Productos:** Consulta pública y vista detallada del catálogo.
- 🧑‍💼 **Panel Administrativo:** Operaciones CRUD protegidas por rol de usuario mediante middlewares.
- 🗂️ **Gestión de Categorías:** Organización modular de productos.
- 🖼️ **Validación Binaria de Imágenes:** Inspección de tipo binario mediante **Pillow** y sanitización de nombres de archivo con `secure_filename`.
- ⚡ **Limitación de Tasa (Rate Limiting):** Protección contra ataques de fuerza bruta utilizando **Flask-Limiter** (soporta almacenamiento en memoria o Redis).
- ☁️ **Despliegue en la Nube:** Backend hospedado en **Render** y persistencia relacional en **Supabase**.
- 🐳 **Contenedorización con Docker:** `Dockerfile` listo para entornos de desarrollo y producción.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue los principios de **Clean Architecture**, aislando la infraestructura y las peticiones HTTP de la lógica de negocio y las consultas SQL nativas:

```text
┌─────────────────────────────────────────────────────────────┐
│                    React SPA (Frontend)                     │
│        Components | Hooks | Context API | React Router      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Peticiones HTTP/REST (JSON)
                (credentials: 'include')
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask API REST - Capa Controladores            │
│          (Blueprints: cart_routes, productos_routes)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Flask Services - Lógica de Negocio              │
│       (cart_service: validación de stock, excepciones)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Flask Repository - Acceso a Datos               │
│         (cart_repository: consultas SQL psycopg2)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL DB (Supabase Cloud)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológico

| Capa | Tecnologías / Servicios |
| :--- | :--- |
| **Frontend** | React, JavaScript (ES6+), React Router DOM, Fetch API, pnpm |
| **Backend** | Python 3.12, Flask, Flask Blueprints, PyJWT, Flask-CORS, Flask-Limiter, Pillow, Gunicorn |
| **Base de Datos** | PostgreSQL (`psycopg2-binary`, SQL nativo) |
| **Testing** | Pytest, Pytest Fixtures |
| **Infraestructura / Cloud** | Render (Backend Hosting), Supabase (Database Hosting) |
| **Contenedorización** | Docker, Dockerfile |
| **Control de Versiones** | Git, GitHub (Conventional Commits) |

---

## 🧪 Pruebas Automatizadas (Pytest)

El backend incorpora una suite de pruebas automatizadas dividida en 3 capas de cobertura:

1. **Integración BD (`test_cart_repository.py`):** Valida la ejecución correcta de las consultas SQL (`SELECT`, `INSERT`, `UPDATE`) directamente en PostgreSQL.
2. **Lógica de Negocio (`test_cart_service.py`):** Verifica reglas de dominio (cantidades mayores a 0, disponibilidad de stock) y el lanzamiento de excepciones (`ValueError`, `KeyError`).
3. **Controladores HTTP (`test_cart_routes.py`):** Simula peticiones HTTP reales usando el cliente de pruebas de Flask (`test_client`) validando códigos de estado (`200 OK`, `400 Bad Request`, `404 Not Found`) y estructura JSON.

Para ejecutar la suite de pruebas desde la raíz de la carpeta `Backend/`:

```bash
pytest -v
```

---

## 🔒 Seguridad

El backend implementa diversas capas de seguridad para entornos productivos:

- **Cookies HttpOnly & SameSite:** El token JWT viaja de manera transparente en cookies no accesibles desde scripts del cliente (`document.cookie`), protegiendo contra ataques XSS.
- **Firma de JWT (HS256):** Expiración automática de tokens configurada a 24 horas.
- **Hashing de Contraseñas:** Encriptación segura mediante `werkzeug.security`.
- **Inspección Binaria de Archivos:** Mediante la librería Pillow, se verifica que los archivos subidos sean imágenes reales y no ejecutables maliciosos disfrazados.
- **Protección contra Fuerza Bruta:** Rate limiting en rutas críticas como `/api/login` (5 peticiones/min) y `/api/register` (3 peticiones/min).
- **Inyección SQL:** Consultas parametrizadas utilizando `psycopg2`.

---

## 🗄️ Diseño de la Base de Datos (PostgreSQL en Supabase)

### Entidades Principales

#### 👤 Usuario (`usuario`)
- `idusuario` (PK, Serial)
- `nombres`
- `correo` (Unique)
- `password` (Hashed)
- `rol` (`admin` | `cliente`)

#### 📂 Categoría (`categoria`)
- `id_categoria` (PK, Serial)
- `nombre_categoria`

#### 🎮 Producto (`producto`)
- `id_producto` (PK, Serial)
- `nombre`
- `precio`
- `stock`
- `imagen`
- `descripcion`
- `categoria_id_categoria` (FK -> `categoria.id_categoria`)

#### 🛒 Carrito de Compras (`carrito`)
- `id_carrito` (PK, Serial)
- `id_usuario` (FK -> `usuario.idusuario`)
- `id_producto` (FK -> `producto.id_producto`)
- `cantidad`

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.12+
- Node.js 18+ y pnpm / npm
- Instancia de PostgreSQL (Local o en Supabase)
- Docker (Opcional)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/davidrosero62-cpu/neo-grid-gaming.git
cd neo-grid-gaming
```

### 2. Configurar el Backend

```bash
cd Backend
python3 -m venv venv
```

**Activar entorno virtual:**
- Linux / macOS: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

**Instalar dependencias:**
```bash
pip install -r requirements.txt
```

### 3. Variables de Entorno del Backend

Crear un archivo `.env` dentro de la carpeta `Backend/`:

```env
# URL de conexión (Producción en Supabase o Render)
DATABASE_URL=postgresql://usuario:password@host.supabase.co:5432/postgres

# O Configuración individual para PostgreSQL local
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=tu_password
DB_NAME=db_neo_grid_gaming

# Claves de Seguridad y CORS
SECRET_KEY=tu_clave_secreta_super_segura
FRONTEND_URL=http://localhost:5173

# Opcional: Redis para Flask-Limiter
REDIS_URL=memory://
```

### 4. Ejecutar el Backend

**Opción A: Desarrollo Local con Flask**
```bash
python3 app.py
```
El servidor estará corriendo en: `http://localhost:5000`

**Opción B: Servidor de Producción WSGI (Gunicorn)**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Opción C: Ejecución mediante Docker**
```bash
docker build -t neo-grid-backend .
docker run -p 8000:8000 --env-file .env neo-grid-backend
```

### 5. Configurar el Frontend

```bash
cd ../Frontend
pnpm install
pnpm run dev
```
La aplicación estará disponible en: `http://localhost:5173`

---

## 🌐 API REST - Endpoints

*Nota: La autenticación se maneja automáticamente mediante cookies HttpOnly enviadas por el navegador.*

| Método | Endpoint | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/login` | Público | Inicia sesión y establece la cookie con el JWT |
| **POST** | `/api/logout` | Autenticado | Elimina la cookie del token para cerrar sesión |
| **POST** | `/api/register` | Público | Registra nuevos usuarios con rol cliente |
| **GET** | `/` | Público | Consulta el catálogo público de productos |
| **GET** | `/api/categorias` | Público | Obtiene el listado de categorías |
| **GET** | `/api/productos` | Admin | Obtiene productos con sus detalles de categoría |
| **POST** | `/api/productos` | Admin | Registra un nuevo producto y procesa su imagen |
| **DELETE** | `/api/productos/<id>` | Admin | Elimina un producto por su ID |
| **POST** | `/api/cart/add` | Autenticado / Cliente | Agrega un producto al carrito o acumula su cantidad |

---

## 🚧 Estado del Proyecto

| Componente | Estado |
| :--- | :--- |
| Backend Flask (Blueprints & Services) | ✅ Finalizado |
| Base de Datos PostgreSQL (Supabase) | ✅ Finalizado |
| Autenticación por Cookies HttpOnly | ✅ Finalizado |
| API REST en Producción (Render) | ✅ Finalizado |
| Arquitectura en 3 Capas (Repo, Service, Route) | ✅ Finalizado |
| Suite de Pruebas Automatizadas (Pytest) | ✅ Finalizado |
| Frontend React | ✅ Finalizado |
| CRUD Administrativo | ✅ Finalizado |
| Contenedorización (Docker) | ✅ Finalizado |
| Aplicación Android (Kotlin + Retrofit) | 🚧 En desarrollo |

---

## 👨‍💻 Autor

**David Sebastián Rosero Manotas**  
Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA  
GitHub: [davidrosero62-cpu](https://github.com/davidrosero62-cpu)

---

## 🌿 Estrategia de Ramas

- `main`: Versión estable del proyecto utilizada como base académica.
- `deploy/production`: Rama destinada a la preparación, despliegue en Render y mantenimiento del entorno de producción.

---

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos y como parte de mi portafolio profesional.