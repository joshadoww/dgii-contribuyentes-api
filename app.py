"""
API para consultar contribuyentes de la DGII (Dirección General de Impuestos Internos).
Permite consultar información de contribuyentes por RNC.
"""
import os
from dotenv import load_dotenv
from flask import jsonify, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from app import create_app, db
from app.utils.logger import api_logger as logger

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = create_app()

# Importar modelos
from app.models import Contribuyente, ActualizacionDB

# Importar y registrar blueprint de la API
from app.api import api_bp
from app.admin import admin_bp
from app.usuarios import usuarios_bp
from app.swagger import swagger_bp

# Registrar blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(swagger_bp, url_prefix='/docs')

# Configurar CORS para permitir solicitudes desde otros dominios
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Almacenar tiempo de inicio para cálculos de uptime
app.start_time = time.time()

# Configurar Swagger UI para la documentación de la API
from flask_swagger_ui import get_swaggerui_blueprint
from app.swagger import get_swagger_json

# Crear endpoint para el archivo swagger.json
@app.route('/swagger.json')
def swagger_json():
    return app.response_class(
        response=get_swagger_json(),
        status=200,
        mimetype='application/json'
    )

# Registrar blueprint de Swagger UI
SWAGGER_URL = '/docs'  # URL para acceder a la documentación
API_URL = '/swagger.json'  # URL del archivo swagger.json

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API DGII Contribuyentes"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Configurar el limitador de tasa
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri="memory://",
    strategy="fixed-window",
    retry_after="delta-seconds"
)

# Middleware para registrar todas las solicitudes
@app.before_request
def before_request():
    g.start_time = time.time()
    logger.info(f"Solicitud recibida: {request.method} {request.path} - IP: {get_remote_address()}")

@app.after_request
def after_request(response):
    diff = time.time() - g.start_time
    status_code = response.status_code
    
    # Registrar información sobre la respuesta
    if status_code >= 500:
        logger.error(f"Respuesta: {status_code} - Tiempo: {diff:.4f}s - Ruta: {request.path}")
    elif status_code >= 400:
        logger.warning(f"Respuesta: {status_code} - Tiempo: {diff:.4f}s - Ruta: {request.path}")
    else:
        logger.info(f"Respuesta: {status_code} - Tiempo: {diff:.4f}s - Ruta: {request.path}")
    
    return response

# Manejador de errores para límite de tasa excedido
@app.errorhandler(429)
def ratelimit_handler(e):
    """Manejador para errores de límite de tasa excedido."""
    logger.warning(f"Límite de tasa excedido para IP: {get_remote_address()}")
    return jsonify({
        'error': 'Límite de solicitudes excedido',
        'mensaje': 'Has excedido el límite de solicitudes por minuto. Por favor, intenta de nuevo más tarde.',
        'status': 'error',
        'retry_after': 60
    }), 429, {'Retry-After': '60'}

# Manejador de errores para rutas no encontradas (404)
@app.errorhandler(404)
def not_found(e):
    """Manejador para rutas no encontradas."""
    logger.info(f"Ruta no encontrada: {request.url}")
    return jsonify({
        'error': 'Endpoint no encontrado',
        'mensaje': 'La ruta solicitada no existe en esta API.',
        'status': 'error',
        'url': request.url
    }), 404

# Manejador de errores para errores internos (500)
@app.errorhandler(500)
def internal_error(e):
    """Manejador para errores internos del servidor."""
    logger.error(f"Error interno del servidor: {str(e)}")
    return jsonify({
        'error': 'Error interno del servidor',
        'mensaje': 'Ha ocurrido un error interno en el servidor. Por favor, intenta de nuevo más tarde.',
        'status': 'error'
    }), 500

# Ruta principal
@app.route('/')
def index():
    return jsonify({
        'api': 'DGII Contribuyentes API',
        'version': '1.0.0',
        'endpoints': [
            '/api/contribuyente/<rnc>',
            '/api/contribuyentes',
            '/api/contribuyentes/estado/<estado>',
            '/api/contribuyentes/actividad',
            '/api/estadisticas',
            '/api/validar/<rnc>',
            '/api/busqueda-avanzada',
            '/api/status'
        ]
    })

def run():
    """Función para ejecutar la aplicación."""
    # Crear todas las tablas si no existen
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada correctamente")
    
    # Ejecutar la aplicación
    logger.info(f"API iniciada en {os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', 5001)}")
    app.run(host=os.getenv('API_HOST', '0.0.0.0'), 
            port=int(os.getenv('API_PORT', 5001)),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')

if __name__ == '__main__':
    run()
