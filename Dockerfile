FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para datos
RUN mkdir -p /app/data

# Configurar cron para la actualización diaria
RUN echo "0 1 * * * cd /app && python scripts/update_db.py >> /app/logs/update_db.log 2>&1" > /etc/cron.d/dgii_update
RUN chmod 0644 /etc/cron.d/dgii_update
RUN crontab /etc/cron.d/dgii_update

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer el puerto
EXPOSE 5001

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
