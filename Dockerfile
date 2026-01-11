# 1. Usamos una imagen base oficial de Python ligera
FROM python:3.14-slim

# 2. Evitamos que Python genere archivos .pyc y activamos logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar dependencias del sistema necesarias para compilar (Postgres driver, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar dependencias de Python e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiar el código fuente
COPY . .

# 7. Exponer el puerto donde corre FastAPI
EXPOSE 8000

# 8. Comando para arrancar la aplicación
# Usamos '0.0.0.0' para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]