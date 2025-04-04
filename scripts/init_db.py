#!/usr/bin/env python3
"""
Script para inicializar la base de datos de contribuyentes DGII.
"""
import os
import sys
import sqlite3
from dotenv import load_dotenv

# Agregar el directorio raíz al path para poder importar los módulos de la aplicación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

def init_database():
    """
    Inicializa la base de datos y crea las tablas necesarias.
    """
    # Obtener las variables de entorno
    db_type = os.getenv('DB_TYPE', 'sqlite')
    
    if db_type == 'sqlite':
        db_path = os.getenv('DB_PATH', 'data/dgii_contribuyentes.db')
        # Asegurar que el directorio data existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        try:
            # Crear el archivo de la base de datos SQLite si no existe
            conn = sqlite3.connect(db_path)
            conn.close()
            
            print(f"Base de datos SQLite '{db_path}' creada o verificada correctamente.")
            print("Inicialización de la base de datos completada con éxito.")
            print("Las tablas se crearán automáticamente al iniciar la aplicación.")
            
            return True
        except Exception as e:
            print(f"Error al inicializar la base de datos SQLite: {e}")
            return False
    else:
        # Si se quiere usar MySQL, se necesitaría instalar mysqlclient
        print("La configuración actual requiere MySQL, pero estamos usando SQLite para pruebas.")
        print("Cambie la variable DB_TYPE a 'sqlite' en el archivo .env para continuar.")
        return False

if __name__ == '__main__':
    print("Inicializando la base de datos...")
    success = init_database()
    
    if success:
        print("Proceso completado con éxito.")
    else:
        print("Proceso completado con errores.")
        sys.exit(1)
