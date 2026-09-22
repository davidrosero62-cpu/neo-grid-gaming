# 🎮 Neo Grid Gaming

**Neo Grid Gaming** es una plataforma de comercio electrónico orientada al sector gamer, desarrollada bajo una **arquitectura desacoplada** que separa la capa de presentación de la lógica de negocio mediante una API REST en Flask.

El proyecto está compuesto por un **frontend SPA en React**, un **backend en Flask** estructurado modularmente mediante Blueprints y Services, y una **base de datos relacional en PostgreSQL alojada en la nube**, ofreciendo una arquitectura escalable, segura y lista para el consumo de clientes web y móviles.

Actualmente, el backend de producción se encuentra desplegado en **Render** y conectado a la base de datos de **Supabase**.

---

## 📌 Características

- 🔐 **Autenticación basada en Cookies HttpOnly:** Almacenamiento seguro de JWT para mitigar ataques de tipo XSS.
- 🛡️ **Prevención de Enumeración de Usuarios:** Respuestas genéricas en el registro para evitar fugas de información.
- 🛒 **Catálogo Dinámico de Productos:** Consulta pública y vista detallada del catálogo.
- 🧑‍💼 **Panel Administrativo:** Operaciones CRUD protegidas por rol de usuario mediante middlewares.
- 🗂️ **Gestión de Categorías:** Organización modular de productos.
- 🖼️ **Validación Binaria de Imágenes:** Inspección de tipo binario mediante **Pillow** y sanitización de nombres de archivo con `secure_filename`.
- ⚡ **Limitación de Tasa (Rate Limiting):** Protección contra ataques de fuerza bruta utilizando **Flask-Limiter** (soporta almacenamiento en memoria o Redis).
- ☁️ **Despliegue en la Nube:** Backend hospedado en **Render** y persistencia relacional en **Supabase**.
- 🐳 **Contenedorización con Docker:** `Dockerfile` listo para entornos de desarrollo y producción.

---

# 🏗️ Arquitectura del Sistema

```text
┌────────────────────────┐
│      React (SPA)       │
└───────────┬────────────┘
            │
  Fetch API (credentials: 'include')
            │
┌───────────▼────────────┐
│ Flask REST API (Render)│  ◄── [Blueprints & Services Layer]
└───────────┬────────────┘
            │
  psycopg2 (DATABASE_URL)
            │
┌───────────▼────────────┐
│ PostgreSQL (Supabase)  │
└────────────────────────┘ 

Capa,Tecnologías / Servicios
Frontend,"React, JavaScript, React Router DOM, Fetch API, pnpm"
Backend,"Python 3.11, Flask, PyJWT, Flask-CORS, Flask-Limiter, Pillow, Gunicorn"
Base de Datos,PostgreSQL (psycopg2-binary)
Infraestructura / Cloud,"Render (Backend Hosting), Supabase (Database Hosting)"
Contenedorización,"Docker, Dockerfile"
Control de Versiones,"Git, GitHub"