FROM python:3.12.3-slim

# Instalar libgomp1 (necesario para LightGBM)
RUN apt-get update && \
    apt-get install -y libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Establecer variables de entorno para la conexión a la base de datos
# ¡ADVERTENCIA: Para producción, considera usar Docker Secrets o variables de entorno de Render!
ENV MONGO_URI="mongodb://host.docker.internal:27017/"
ENV MONGO_DB="SistemaTestVocacionalDB"

# Establecer el directorio de trabajo base dentro del contenedor
WORKDIR /app

# Copiar requirements.txt e instalar dependencias
# Asegúrate de que uvicorn[standard] y fastapi estén en requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el parche para frozendict (si aún es necesario)
COPY patched_frozendict_init.py /usr/local/lib/python3.12/site-packages/frozendict/__init__.py

# Copiar el código de tu aplicación y el modelo
COPY app/ ./app/
COPY model/ ./model/

# Opcional: Verifica el contenido del directorio del modelo durante la construcción
RUN ls -l /app/model

# Establecer el directorio de trabajo donde se encuentra tu archivo main.py de FastAPI
# Si tu app está en /app/app/main.py, este es el lugar correcto
WORKDIR /app/app

# Exponer el puerto en el que Uvicorn escuchará
EXPOSE 8000

# Comando para iniciar la aplicación FastAPI con Uvicorn
# 'main:app' asume que tienes 'app = FastAPI()' en 'main.py'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]