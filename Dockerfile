FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema (Postgres, compiladores)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Directorios para montar volúmenes
RUN mkdir -p /app/notebooks
RUN mkdir -p /app/src

# Exponemos el puerto de la API (Documentación)
EXPOSE 8000

# Por defecto bash (Jupyter y Feature Builder usan esto o sobreescriben)
CMD ["bash"]