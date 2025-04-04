"""
Inicialización de la aplicación Flask y la base de datos.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crear instancia de SQLAlchemy
db = SQLAlchemy()

def create_app():
    """
    Crea y configura la aplicación Flask.
    
    Returns:
        Flask: Aplicación Flask configurada.
    """
    # Crear la aplicación Flask
    app = Flask(__name__)
    
    # Configuración de la base de datos
    if os.getenv('DB_TYPE') == 'sqlite':
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.getenv('DB_PATH', 'data/dgii_contribuyentes.db')}"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar la base de datos con la aplicación
    db.init_app(app)
    
    return app
