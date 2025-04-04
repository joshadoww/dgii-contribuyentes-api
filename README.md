# API DGII - Consulta de Contribuyentes

API para consultar los contribuyentes de la DGII (Dirección General de Impuestos Internos) de la República Dominicana.

## Descripción

Esta API permite:

- Descargar diariamente el listado de contribuyentes desde la DGII
- Almacenar la información en una base de datos (SQLite o MySQL)
- Consultar contribuyentes por RNC (Registro Nacional del Contribuyente)
- Realizar búsquedas avanzadas de contribuyentes
- Obtener estadísticas sobre los contribuyentes

## Requisitos

- Python 3.8+
- SQLite (opcional, también soporta MySQL)
- Docker y Docker Compose (para ejecución dockerizada)

## Instalación

### Método 1: Instalación local

1. Clonar el repositorio
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configurar variables de entorno en un archivo `.env` (ver `.env.example`)
4. Iniciar la base de datos:
   ```
   python scripts/init_db.py
   ```

### Método 2: Usando Docker (recomendado)

1. Clonar el repositorio
2. Construir y ejecutar los contenedores:
   ```
   docker-compose up -d
   ```

## Uso

### Ejecución local

1. Iniciar el servidor:
   ```
   python app.py
   ```
2. Actualizar manualmente la base de datos:
   ```
   python scripts/update_db.py
   ```

### Ejecución con Docker

1. Iniciar los servicios:
   ```
   docker-compose up -d
   ```
2. Ver logs:
   ```
   docker-compose logs -f api
   ```
3. Detener los servicios:
   ```
   docker-compose down
   ```

## Documentación de la API

La API cuenta con documentación interactiva utilizando Swagger UI:

- Accede a la documentación en: `http://localhost:5001/docs`
- Explora y prueba todos los endpoints directamente desde la interfaz
- Consulta los esquemas de datos y parámetros requeridos

## Endpoints

- `GET /api/contribuyente/<rnc>` - Consultar contribuyente por RNC
- `GET /api/contribuyentes?nombre=<texto>` - Buscar contribuyentes por nombre
- `GET /api/contribuyentes/estado/<estado>` - Listar contribuyentes por estado
- `GET /api/contribuyentes/actividad?actividad=<texto>` - Buscar por actividad económica
- `GET /api/estadisticas` - Obtener estadísticas generales
- `GET /api/validar/<rnc>` - Validar un RNC
- `GET /api/busqueda-avanzada` - Realizar búsqueda con múltiples criterios
- `GET /api/status` - Verificar el estado de la base de datos

## Rate Limiting

La API implementa límites de tasa para prevenir abusos:

- 30 solicitudes por minuto por dirección IP

## CORS

La API tiene habilitado CORS (Cross-Origin Resource Sharing) para permitir solicitudes desde otros dominios. Esto facilita la integración con aplicaciones web frontend.

## Sistema de Logs

La API cuenta con un sistema de logs completo que registra:

- Todas las solicitudes recibidas
- Respuestas enviadas con códigos de estado
- Errores y excepciones
- Actualizaciones de la base de datos

Los logs se almacenan en el directorio `/logs` y se rotan automáticamente para evitar archivos demasiado grandes.

## Actualizaciones Automáticas

La base de datos se actualiza automáticamente todos los días a la 1:00 AM mediante una tarea cron configurada en el contenedor Docker. Esto garantiza que siempre tengas los datos más recientes de contribuyentes.

## Configuración con MySQL

Para usar MySQL en lugar de SQLite, descomente la sección correspondiente en el archivo `docker-compose.yml` y modifique las variables de entorno en `.env`:

```
DB_TYPE=mysql
DB_HOST=db
DB_NAME=dgii
DB_USER=dgiiuser
DB_PASSWORD=dgiipassword
```

## Solución de Problemas

### Problemas de Importación Circular

Si encuentras errores relacionados con importaciones circulares, verifica que estés utilizando la estructura de importación correcta. La aplicación utiliza el patrón de fábrica de aplicaciones (Application Factory Pattern) para evitar estos problemas.

### Logs de Errores

Revisa los archivos de log en el directorio `/logs` para obtener información detallada sobre cualquier error:

- `api.log` - Logs relacionados con las solicitudes a la API
- `db.log` - Logs relacionados con operaciones de base de datos
- `update.log` - Logs relacionados con las actualizaciones de la base de datos

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios propuestos o envía un pull request.
