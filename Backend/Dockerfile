#1. Trae un Sistema Linux minimalista con Python 3.11 ya instalado
FROM python:3.11-slim

#2. Crea y se posiciona dentro de una carpeta interna llamada /app
WORKDIR /app

#3. Copiar e instalar dependencias primero para aprovechar el caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#5. Copia el resto del codigo del backend en el interior del contenedor.
COPY . .

#6. Exponer el puerto donde escucha Flask
EXPOSE 8000

# 7. Variables de entorno por defecto para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# 8. Comando para arrancar el servidor de desarrollo
CMD [ "flask", "run" ]
