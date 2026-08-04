# 🎮 Neo Grid Gaming

**Neo Grid Gaming** es una plataforma de comercio electrónico orientada al sector gamer, desarrollada bajo una **arquitectura desacoplada** que separa la capa de presentación de la lógica de negocio mediante una API REST.

Actualmente el proyecto está compuesto por un **frontend desarrollado en React**, un **backend desarrollado en Flask** y una **base de datos MySQL**, permitiendo una arquitectura escalable y preparada para la integración con múltiples clientes, como aplicaciones web y móviles.

---

## 📌 Características

- 🔐 Autenticación segura mediante JSON Web Tokens (JWT).
- 🛒 Catálogo dinámico de productos.
- 🧑‍💼 Panel administrativo con operaciones CRUD.
- 🗂️ Gestión de categorías.
- 🌐 API REST desacoplada.
- ♿ Funciones básicas de accesibilidad.
- 🔒 Protección mediante Rate Limiting y sanitización de archivos.
- 🖼️ Carga segura de imágenes.
- 📱 Arquitectura preparada para clientes web y móviles.

---

# 🏗️ Arquitectura del Sistema

```text
┌────────────────────┐
│    React (SPA)     │
└─────────┬──────────┘
          │
      Fetch API
          │
┌─────────▼──────────┐
│   Flask REST API   │
└─────────┬──────────┘
          │
    mysql.connector
          │
┌─────────▼──────────┐
│       MySQL        │
└────────────────────┘
```

---

# 🛠️ Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Frontend** | React, JavaScript, React Router DOM, Fetch API, pnpm |
| **Backend** | Python 3, Flask, Flask-JWT-Extended, Flask-CORS, Flask-Limiter |
| **Base de Datos** | MySQL |
| **Control de Versiones** | Git, GitHub |

---

# 🔒 Seguridad

El proyecto implementa diversas medidas para proteger la aplicación y la información de los usuarios.

- Autenticación mediante **JSON Web Tokens (JWT)**.
- Firma de tokens utilizando el algoritmo **HS256**.
- Expiración automática de tokens.
- Hashing seguro de contraseñas mediante `werkzeug.security`.
- Protección contra ataques de fuerza bruta mediante **Flask-Limiter**.
- Sanitización de nombres de archivos utilizando `secure_filename`.
- Validación mediante listas blancas para la carga de archivos.
- Manejo seguro de errores evitando exponer información sensible del servidor.

---

# 🗄️ Diseño de la Base de Datos

El sistema utiliza una base de datos relacional en **MySQL**.

### Entidades principales

### 👤 Usuario

Almacena la información de autenticación y los roles del sistema.

- id_usuario
- nombre
- correo
- contraseña
- rol (`admin` o `cliente`)

---

### 📂 Categoría

Permite organizar los productos.

- id_categoria
- nombre_categoria

---

### 🎮 Producto

Representa los artículos disponibles en la tienda.

- id_producto
- nombre
- descripción
- precio
- stock
- imagen
- categoria_id_categoria

Relación:

```
Categoria (1)
      │
      │
      ▼
Producto (N)
```

---

# 🚀 Instalación

## Requisitos

- Python 3.10 o superior.
- Node.js 18 o superior.
- pnpm.
- MySQL Server.

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/davidrosero62-cpu/neo-grid-gaming.git

cd neo-grid-gaming
```

---

## 2. Configurar el Backend

```bash
cd Backend

python -m venv venv
```

### Activar entorno virtual

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Variables de entorno

Crear un archivo llamado **.env** dentro de la carpeta **Backend/**

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=db_neo_grid_gaming
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Descripción

| Variable | Descripción |
|----------|-------------|
| DB_HOST | Servidor MySQL |
| DB_USER | Usuario de MySQL |
| DB_PASSWORD | Contraseña de MySQL |
| DB_NAME | Nombre de la base de datos |
| SECRET_KEY | Clave para firmar los JWT |

---

## 4. Ejecutar el Backend

```bash
python app.py
```

El servidor estará disponible en

```
http://localhost:5000
```

---

## 5. Configurar el Frontend

```bash
cd ../Frontend

pnpm install
```

---

## 6. Ejecutar el Frontend

```bash
pnpm run dev
```

La aplicación estará disponible en

```
http://localhost:5173
```

---

# 🌐 API REST

Las rutas protegidas requieren un **JWT** válido enviado mediante el encabezado:

```http
Authorization: Bearer <token>
```

## Endpoints disponibles

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| POST | `/api/register` | Registrar un usuario |
| POST | `/api/login` | Iniciar sesión y obtener un JWT |
| GET | `/api/products` | Obtener todos los productos |
| GET | `/api/products/{id}` | Obtener un producto específico |
| POST | `/api/products` | Crear un producto (Administrador) |
| PUT | `/api/products/{id}` | Actualizar un producto (Administrador) |
| DELETE | `/api/products/{id}` | Eliminar un producto (Administrador) |

---

# 🚧 Estado del Proyecto

Actualmente la plataforma web se encuentra completamente funcional.

La aplicación móvil desarrollada en **Kotlin** consume la misma API REST mediante **Retrofit** y se encuentra en desarrollo.

| Componente | Estado |
|------------|--------|
| Backend Flask | ✅ Finalizado |
| API REST | ✅ Finalizado |
| Frontend React | ✅ Finalizado |
| CRUD Administrativo | ✅ Finalizado |
| Autenticación JWT | ✅ Finalizado |
| Gestión de Categorías | ✅ Finalizado |
| Accesibilidad | ✅ Finalizado |
| Aplicación Android (Kotlin + Retrofit) | 🚧 En desarrollo |

---

# 📌 Buenas Prácticas Implementadas

- Arquitectura desacoplada entre frontend y backend.
- API REST reutilizable.
- Componentes reutilizables en React.
- Manejo de estados mediante Hooks (`useState` y `useEffect`).
- Separación de responsabilidades.
- Manejo seguro de errores.
- Protección mediante JWT.
- Validación de archivos.
- Rate Limiting.
- Variables sensibles mediante `.env`.
- Uso de Git para control de versiones.
- Documentación técnica del proyecto.

---

# 📅 Roadmap

- ✅ Backend Flask
- ✅ API REST
- ✅ CRUD de productos
- ✅ CRUD de categorías
- ✅ JWT
- ✅ React SPA
- ✅ Accesibilidad
- ✅ Migración de npm a pnpm
- 🚧 Aplicación Android (Kotlin + Retrofit)
- ⏳ Carrito de compras móvil
- ⏳ Panel administrativo móvil
- ⏳ Despliegue en producción

---

# 👨‍💻 Autor

**David Sebastián Rosero Manotas**

**Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA**

GitHub:
> https://github.com/davidrosero62-cpu

---

# 📄 Licencia

Este proyecto fue desarrollado con fines educativos y como parte de mi portafolio profesional. Su objetivo es demostrar conocimientos en desarrollo Full Stack, arquitectura de software, APIs REST y buenas prácticas de desarrollo.
