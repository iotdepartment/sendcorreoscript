# Imagen base ligera de Python
FROM python:3.11-slim

# Variables de entorno para evitar problemas de buffer y prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear usuario no root
RUN useradd -m appuser

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar tu script principal al contenedor
COPY ./sendcorreoscript.py /app/

# Instalar dependencias necesarias
RUN pip install --no-cache-dir paho-mqtt

# Cambiar a usuario no root
USER appuser

# Comando por defecto para ejecutar tu script
CMD ["python", "sendcorreoscript.py"]