#!/usr/bin/env python
"""
Script para inicializar usuarios en la base de datos.
Crea usuarios predeterminados si no existen.
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('init_usuarios')

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Agregar el directorio raíz al path para poder importar los módulos de la aplicación
sys.path.append(BASE_DIR)

# Asegurar que la variable de entorno DB_TYPE esté configurada como sqlite
os.environ['DB_TYPE'] = 'sqlite'

# Configurar la ruta absoluta a la base de datos
db_path = os.path.join(BASE_DIR, 'data', 'dgii_contribuyentes.db')
os.environ['DB_PATH'] = db_path

logger.info(f"Usando base de datos SQLite en: {db_path}")

from app import create_app
from app.models import db, Usuario

def init_usuarios():
    """Inicializar usuarios en la base de datos."""
    try:
        # Crear la aplicación Flask
        app = create_app()
        
        # Usar el contexto de la aplicación
        with app.app_context():
            # Verificar si ya existe el usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if not admin:
                # Crear usuario admin
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                admin = Usuario(
                    username='admin',
                    rol='admin',
                    activo=True,
                    fecha_creacion=datetime.now(),
                    ultima_actividad=datetime.now()
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                logger.info("Usuario admin creado correctamente")
            else:
                logger.info("El usuario admin ya existe")
            
            # Verificar si ya existe el usuario api
            api_user = Usuario.query.filter_by(username='api').first()
            
            if not api_user:
                # Crear usuario api
                api_password = os.getenv('API_PASSWORD', 'api123')
                api_user = Usuario(
                    username='api',
                    rol='usuario',
                    activo=True,
                    fecha_creacion=datetime.now(),
                    ultima_actividad=datetime.now()
                )
                api_user.set_password(api_password)
                db.session.add(api_user)
                logger.info("Usuario api creado correctamente")
            else:
                logger.info("El usuario api ya existe")
            
            # Guardar cambios en la base de datos
            db.session.commit()
            
            logger.info("Inicialización de usuarios completada")
            
            # Mostrar información de los usuarios
            usuarios = Usuario.query.all()
            logger.info(f"Total de usuarios en la base de datos: {len(usuarios)}")
            for usuario in usuarios:
                logger.info(f"Usuario: {usuario.username}, Rol: {usuario.rol}, Activo: {usuario.activo}")
            
            return True
    
    except Exception as e:
        logger.error(f"Error al inicializar usuarios: {str(e)}")
        return False

if __name__ == '__main__':
    init_usuarios()
