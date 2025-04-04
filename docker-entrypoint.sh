#!/bin/bash
set -e

# Iniciar el servicio cron
service cron start
echo "Servicio cron iniciado"

# Ejecutar el comando pasado a este script
exec "$@"
