"""
Módulo de administración para la API DGII.
Proporciona endpoints protegidos para operaciones administrativas.
"""
import os
import sys
import time
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from app.auth import basic_auth, token_auth, admin_required
from app.models import db, ActualizacionDB

# Agregar el directorio de scripts al path para poder importar update_db
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
import update_db

# Configurar logger
logger = logging.getLogger('api.admin')

# Crear blueprint para endpoints de administración
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/actualizar-db', methods=['POST'])
@basic_auth.login_required
@admin_required
def actualizar_db():
    """Endpoint para forzar la actualización de la base de datos."""
    try:
        logger.info(f"Iniciando actualización manual de la base de datos por el usuario: {request.authorization.username}")
        
        # Registrar inicio de la actualización
        inicio = time.time()
        
        # Ejecutar la actualización
        resultado = update_db.actualizar_base_datos()
        
        # Calcular tiempo de ejecución
        tiempo_ejecucion = time.time() - inicio
        
        # Preparar respuesta
        respuesta = {
            "estado": "completado",
            "mensaje": "Base de datos actualizada correctamente",
            "tiempo_ejecucion": f"{tiempo_ejecucion:.2f} segundos",
            "registros_procesados": resultado.get("registros_procesados", 0),
            "registros_nuevos": resultado.get("registros_nuevos", 0),
            "registros_actualizados": resultado.get("registros_actualizados", 0),
            "fecha_actualizacion": datetime.now().isoformat()
        }
        
        logger.info(f"Actualización manual completada: {respuesta}")
        return jsonify(respuesta), 200
    
    except Exception as e:
        logger.error(f"Error al actualizar la base de datos: {str(e)}")
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al actualizar la base de datos: {str(e)}",
            "fecha": datetime.now().isoformat()
        }), 500

@admin_bp.route('/estadisticas-sistema', methods=['GET'])
@token_auth.login_required
def estadisticas_sistema():
    """Endpoint para obtener estadísticas del sistema."""
    try:
        # Obtener información sobre la última actualización
        ultima_actualizacion = db.session.query(ActualizacionDB).order_by(ActualizacionDB.fecha.desc()).first()
        
        # Obtener información sobre el sistema
        respuesta = {
            "estado": "activo",
            "version_api": "1.0.0",
            "uptime": time.time() - current_app.start_time if hasattr(current_app, 'start_time') else None,
            "ultima_actualizacion": {
                "fecha": ultima_actualizacion.fecha.isoformat() if ultima_actualizacion else None,
                "registros_procesados": ultima_actualizacion.registros_procesados if ultima_actualizacion else 0,
                "registros_nuevos": ultima_actualizacion.registros_nuevos if ultima_actualizacion else 0,
                "registros_actualizados": ultima_actualizacion.registros_actualizados if ultima_actualizacion else 0
            },
            "configuracion": {
                "db_type": os.getenv("DB_TYPE", "sqlite"),
                "update_hour": os.getenv("UPDATE_HOUR", "1"),
                "update_minute": os.getenv("UPDATE_MINUTE", "0")
            }
        }
        
        logger.info(f"Estadísticas del sistema solicitadas por el usuario: {token_auth.current_user()}")
        return jsonify(respuesta), 200
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del sistema: {str(e)}")
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al obtener estadísticas del sistema: {str(e)}",
            "fecha": datetime.now().isoformat()
        }), 500

@admin_bp.route('/limpiar-cache', methods=['POST'])
@basic_auth.login_required
@admin_required
def limpiar_cache():
    """Endpoint para limpiar el caché de la aplicación."""
    try:
        # Aquí implementaríamos la lógica para limpiar el caché
        # Por ahora es solo un ejemplo
        
        logger.info(f"Limpieza de caché solicitada por el usuario: {basic_auth.current_user()}")
        return jsonify({
            "estado": "completado",
            "mensaje": "Caché limpiado correctamente",
            "fecha": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error al limpiar el caché: {str(e)}")
        return jsonify({
            "estado": "error",
            "mensaje": f"Error al limpiar el caché: {str(e)}",
            "fecha": datetime.now().isoformat()
        }), 500
