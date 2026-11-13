#1. Trae un Sistema Linux minimalista con Python 3.12 ya instalado
FROM python:3.12-slim

#2. Crea y se posiciona dentro de una carpeta interna llamada /app
WORKDIR /app

#3. Instala dependencias necesarias para compilar librerías de C (psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalar Poetry de manera global dentro del contenedor
RUN pip install --no-cache-dir poetry

# 5. Copiar los archivos de configuracion dentro del contenedor de poetry
COPY pyproject.toml poetry.lock ./

# 6. configurar Poetry para que no cree entornos virtuales internos e instale todo de golpe
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction

#7. Copia el resto del codigo del backend en el interior del contenedor.
COPY . .

#6. Exponer el puerto donde escucha Flask
EXPOSE 8000

# 7. Variables de entorno por defecto para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# 8. Comando para arrancar el servidor de desarrollo
CMD [ "flask", "run" ]
