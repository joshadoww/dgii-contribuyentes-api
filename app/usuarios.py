"""
Módulo de gestión de usuarios para la API DGII.
Proporciona endpoints para administrar usuarios y tokens.
"""
import logging
from flask import Blueprint, jsonify, request, g
from app.models import db, Usuario, Token
from app.auth import basic_auth, admin_required
from datetime import datetime, timedelta

# Configurar logger
logger = logging.getLogger('api.usuarios')

# Crear blueprint para endpoints de usuarios
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
@basic_auth.login_required
@admin_required
def listar_usuarios():
    """Endpoint para listar todos los usuarios."""
    try:
        usuarios = Usuario.query.all()
        resultado = []
        
        for usuario in usuarios:
            resultado.append({
                'id': usuario.id,
                'username': usuario.username,
                'rol': usuario.rol,
                'activo': usuario.activo,
                'fecha_creacion': usuario.fecha_creacion.isoformat(),
                'ultima_actividad': usuario.ultima_actividad.isoformat() if usuario.ultima_actividad else None
            })
        
        logger.info(f"Listado de usuarios solicitado por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"Error al listar usuarios: {str(e)}")
        return jsonify({
            'error': 'Error al listar usuarios',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@basic_auth.login_required
@admin_required
def obtener_usuario(usuario_id):
    """Endpoint para obtener información detallada de un usuario."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener tokens activos
        tokens_activos = Token.query.filter_by(usuario_id=usuario.id).filter(Token.fecha_expiracion > datetime.now()).all()
        tokens = []
        
        for token in tokens_activos:
            tokens.append({
                'id': token.id,
                'token': token.token,
                'fecha_creacion': token.fecha_creacion.isoformat(),
                'fecha_expiracion': token.fecha_expiracion.isoformat(),
                'ultimo_uso': token.ultimo_uso.isoformat() if token.ultimo_uso else None
            })
        
        resultado = {
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol,
            'activo': usuario.activo,
            'fecha_creacion': usuario.fecha_creacion.isoformat(),
            'ultima_actividad': usuario.ultima_actividad.isoformat() if usuario.ultima_actividad else None,
            'tokens_activos': tokens
        }
        
        logger.info(f"Información de usuario {usuario.username} solicitada por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"Error al obtener información del usuario: {str(e)}")
        return jsonify({
            'error': 'Error al obtener información del usuario',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('', methods=['POST'])
@basic_auth.login_required
@admin_required
def crear_usuario():
    """Endpoint para crear un nuevo usuario."""
    try:
        datos = request.get_json()
        
        # Validar datos requeridos
        if not datos or not datos.get('username') or not datos.get('password'):
            return jsonify({'error': 'Se requieren username y password'}), 400
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=datos['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 409
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=datos['username'],
            rol=datos.get('rol', 'usuario'),
            activo=datos.get('activo', True)
        )
        nuevo_usuario.set_password(datos['password'])
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        logger.info(f"Usuario {nuevo_usuario.username} creado por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify({
            'mensaje': 'Usuario creado correctamente',
            'id': nuevo_usuario.id,
            'username': nuevo_usuario.username,
            'rol': nuevo_usuario.rol
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear usuario: {str(e)}")
        return jsonify({
            'error': 'Error al crear usuario',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
@basic_auth.login_required
@admin_required
def actualizar_usuario(usuario_id):
    """Endpoint para actualizar un usuario existente."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        datos = request.get_json()
        
        # Actualizar campos si están presentes en la solicitud
        if 'username' in datos and datos['username'] != usuario.username:
            # Verificar si el nuevo username ya existe
            if Usuario.query.filter_by(username=datos['username']).first():
                return jsonify({'error': 'El nombre de usuario ya existe'}), 409
            usuario.username = datos['username']
        
        if 'password' in datos:
            usuario.set_password(datos['password'])
        
        if 'rol' in datos:
            usuario.rol = datos['rol']
        
        if 'activo' in datos:
            usuario.activo = datos['activo']
        
        db.session.commit()
        
        logger.info(f"Usuario {usuario.username} actualizado por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify({
            'mensaje': 'Usuario actualizado correctamente',
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol,
            'activo': usuario.activo
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar usuario: {str(e)}")
        return jsonify({
            'error': 'Error al actualizar usuario',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@basic_auth.login_required
@admin_required
def eliminar_usuario(usuario_id):
    """Endpoint para eliminar un usuario."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # No permitir eliminar al usuario que está realizando la solicitud
        if hasattr(g.current_user, 'id') and g.current_user.id == usuario.id:
            return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 403
        
        # Guardar el nombre de usuario para el registro
        username = usuario.username
        
        # Eliminar el usuario (esto también eliminará sus tokens debido a la relación cascade)
        db.session.delete(usuario)
        db.session.commit()
        
        logger.info(f"Usuario {username} eliminado por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify({
            'mensaje': 'Usuario eliminado correctamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar usuario: {str(e)}")
        return jsonify({
            'error': 'Error al eliminar usuario',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/<int:usuario_id>/tokens', methods=['POST'])
@basic_auth.login_required
@admin_required
def generar_token(usuario_id):
    """Endpoint para generar un nuevo token para un usuario."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        datos = request.get_json() or {}
        
        # Duración del token en segundos (por defecto 30 días)
        duracion = datos.get('duracion', 3600 * 24 * 30)
        
        # Generar token
        token = usuario.generate_token(duracion)
        
        logger.info(f"Token generado para el usuario {usuario.username} por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify({
            'mensaje': 'Token generado correctamente',
            'token': token.token,
            'fecha_expiracion': token.fecha_expiracion.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al generar token: {str(e)}")
        return jsonify({
            'error': 'Error al generar token',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/<int:usuario_id>/tokens/<int:token_id>', methods=['DELETE'])
@basic_auth.login_required
@admin_required
def revocar_token(usuario_id, token_id):
    """Endpoint para revocar un token específico."""
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        token = Token.query.filter_by(id=token_id, usuario_id=usuario_id).first()
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 404
        
        db.session.delete(token)
        db.session.commit()
        
        logger.info(f"Token revocado para el usuario {usuario.username} por: {g.current_user.username if hasattr(g.current_user, 'username') else g.current_user}")
        return jsonify({
            'mensaje': 'Token revocado correctamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al revocar token: {str(e)}")
        return jsonify({
            'error': 'Error al revocar token',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/perfil', methods=['GET'])
@basic_auth.login_required
def obtener_perfil():
    """Endpoint para que un usuario obtenga su propio perfil."""
    try:
        # Si g.current_user es un objeto Usuario
        if hasattr(g.current_user, 'id'):
            usuario = g.current_user
            
            # Obtener tokens activos
            tokens_activos = Token.query.filter_by(usuario_id=usuario.id).filter(Token.fecha_expiracion > datetime.now()).all()
            tokens = []
            
            for token in tokens_activos:
                tokens.append({
                    'id': token.id,
                    'token': token.token,
                    'fecha_creacion': token.fecha_creacion.isoformat(),
                    'fecha_expiracion': token.fecha_expiracion.isoformat(),
                    'ultimo_uso': token.ultimo_uso.isoformat() if token.ultimo_uso else None
                })
            
            resultado = {
                'id': usuario.id,
                'username': usuario.username,
                'rol': usuario.rol,
                'fecha_creacion': usuario.fecha_creacion.isoformat(),
                'ultima_actividad': usuario.ultima_actividad.isoformat() if usuario.ultima_actividad else None,
                'tokens_activos': tokens
            }
            
            logger.info(f"Perfil solicitado por el usuario: {usuario.username}")
            return jsonify(resultado), 200
        
        # Si g.current_user es un diccionario (para usuarios estáticos)
        elif isinstance(g.current_user, dict):
            resultado = {
                'username': g.current_user.get('username'),
                'rol': g.current_user.get('rol')
            }
            
            logger.info(f"Perfil solicitado por el usuario estático: {g.current_user.get('username')}")
            return jsonify(resultado), 200
        
        # Si g.current_user es una cadena (para compatibilidad con versiones anteriores)
        else:
            resultado = {
                'username': g.current_user,
                'rol': 'admin' if g.current_user == 'admin' else 'usuario'
            }
            
            logger.info(f"Perfil solicitado por el usuario: {g.current_user}")
            return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"Error al obtener perfil: {str(e)}")
        return jsonify({
            'error': 'Error al obtener perfil',
            'mensaje': str(e)
        }), 500

@usuarios_bp.route('/perfil/token', methods=['POST'])
@basic_auth.login_required
def generar_token_propio():
    """Endpoint para que un usuario genere un token para sí mismo."""
    try:
        # Si g.current_user es un objeto Usuario
        if hasattr(g.current_user, 'id'):
            usuario = g.current_user
            
            datos = request.get_json() or {}
            
            # Duración del token en segundos (por defecto 30 días)
            duracion = datos.get('duracion', 3600 * 24 * 30)
            
            # Generar token
            token = usuario.generate_token(duracion)
            
            logger.info(f"Token generado por el usuario: {usuario.username}")
            return jsonify({
                'mensaje': 'Token generado correctamente',
                'token': token.token,
                'fecha_expiracion': token.fecha_expiracion.isoformat()
            }), 201
        
        # Para usuarios estáticos, no permitir generar tokens
        else:
            return jsonify({
                'error': 'Esta funcionalidad solo está disponible para usuarios registrados en la base de datos'
            }), 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al generar token propio: {str(e)}")
        return jsonify({
            'error': 'Error al generar token',
            'mensaje': str(e)
        }), 500
