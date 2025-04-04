"""
Módulo de autenticación para la API DGII.
Proporciona funcionalidades para proteger endpoints sensibles.
"""
import os
from functools import wraps
from flask import request, jsonify, g, current_app
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from datetime import datetime
from app.models import db, Usuario, Token

# Configurar logger
logger = logging.getLogger('api.auth')

# Crear instancias de autenticación
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """Verificar credenciales de usuario para autenticación básica."""
    # Buscar el usuario en la base de datos
    usuario = Usuario.query.filter_by(username=username, activo=True).first()
    
    if usuario and usuario.check_password(password):
        # Actualizar última actividad
        usuario.ultima_actividad = datetime.now()
        db.session.commit()
        
        logger.info(f"Autenticación básica exitosa para el usuario: {username}")
        g.current_user = usuario
        return usuario
    
    # Fallback a usuarios estáticos para desarrollo/pruebas
    if current_app.config.get('TESTING', False) or current_app.config.get('DEBUG', False):
        # Usuarios para desarrollo/pruebas
        USERS = {
            "admin": generate_password_hash(os.getenv("ADMIN_PASSWORD", "admin123")),
            "api": generate_password_hash(os.getenv("API_PASSWORD", "api123"))
        }
        
        if username in USERS and check_password_hash(USERS.get(username), password):
            logger.info(f"Autenticación básica exitosa para usuario estático: {username}")
            g.current_user = {"username": username, "rol": "admin" if username == "admin" else "usuario"}
            return username
    
    logger.warning(f"Intento fallido de autenticación básica para el usuario: {username}")
    return False

@token_auth.verify_token
def verify_token(token):
    """Verificar token para autenticación por token."""
    # Buscar el token en la base de datos
    usuario = Token.check_token(token)
    
    if usuario:
        # Actualizar última actividad
        usuario.ultima_actividad = datetime.now()
        db.session.commit()
        
        logger.info(f"Autenticación por token exitosa para el usuario: {usuario.username}")
        g.current_user = usuario
        return usuario
    
    # Fallback a tokens estáticos para desarrollo/pruebas
    if current_app.config.get('TESTING', False) or current_app.config.get('DEBUG', False):
        # Tokens para desarrollo/pruebas
        TOKENS = {
            "api-token-1": "admin",
            "api-token-2": "api"
        }
        
        if token in TOKENS:
            username = TOKENS.get(token)
            logger.info(f"Autenticación por token estático exitosa para el usuario: {username}")
            g.current_user = {"username": username, "rol": "admin" if username == "admin" else "usuario"}
            return username
    
    if token:
        logger.warning(f"Intento fallido de autenticación por token: {token[:10]}...")
    return False

def admin_required(f):
    """Decorador para requerir rol de administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si g.current_user es un objeto Usuario
        if hasattr(g.current_user, 'is_admin'):
            if not g.current_user.is_admin():
                logger.warning(f"Acceso denegado a función administrativa para el usuario: {g.current_user.username}")
                return jsonify({"error": "Se requieren privilegios de administrador"}), 403
        # Si g.current_user es un diccionario (para usuarios estáticos)
        elif isinstance(g.current_user, dict) and g.current_user.get("rol") != "admin":
            logger.warning(f"Acceso denegado a función administrativa para el usuario: {g.current_user.get('username')}")
            return jsonify({"error": "Se requieren privilegios de administrador"}), 403
        # Si g.current_user es una cadena (para compatibilidad con versiones anteriores)
        elif isinstance(g.current_user, str) and g.current_user != "admin":
            logger.warning(f"Acceso denegado a función administrativa para el usuario: {g.current_user}")
            return jsonify({"error": "Se requieren privilegios de administrador"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def get_api_key():
    """Obtener API key del encabezado de la solicitud."""
    api_key = request.headers.get('X-API-Key')
    
    # Verificar si es un token válido en la base de datos
    usuario = Token.check_token(api_key) if api_key else None
    
    if usuario:
        # Actualizar última actividad
        usuario.ultima_actividad = datetime.now()
        db.session.commit()
        
        logger.info(f"Autenticación por API key exitosa para el usuario: {usuario.username}")
        g.current_user = usuario
        return True
    
    # Fallback a tokens estáticos para desarrollo/pruebas
    if current_app.config.get('TESTING', False) or current_app.config.get('DEBUG', False):
        # Tokens para desarrollo/pruebas
        TOKENS = {
            "api-token-1": "admin",
            "api-token-2": "api"
        }
        
        if api_key in TOKENS:
            username = TOKENS.get(api_key)
            logger.info(f"Autenticación por API key estática exitosa para el usuario: {username}")
            g.current_user = {"username": username, "rol": "admin" if username == "admin" else "usuario"}
            return True
    
    if api_key:
        logger.warning(f"Intento fallido de autenticación por API key: {api_key[:10]}...")
    return False
