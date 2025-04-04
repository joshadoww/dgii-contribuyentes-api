#!/usr/bin/env python
"""
Script para migrar la base de datos y crear las nuevas tablas.
Funciona con SQLite (configuración predeterminada).
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('migrate_db')

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
from app.models import db

def migrate_database():
    """Migrar la base de datos y crear las nuevas tablas."""
    try:
        # Crear la aplicación Flask
        app = create_app()
        
        # Usar el contexto de la aplicación
        with app.app_context():
            # Crear las tablas que no existen
            db.create_all()
            logger.info("Migración de base de datos completada correctamente")
            
            # Mostrar las tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tablas en la base de datos: {', '.join(tables)}")
            
            return True
    
    except Exception as e:
        logger.error(f"Error al migrar la base de datos: {str(e)}")
        return False

if __name__ == '__main__':
    migrate_database()
