"""
Módulo para la configuración centralizada de logs.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Asegurarse de que el directorio de logs exista
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Configuración de formatos
CONSOLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FILE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

# Configurar el nivel de log global
logging.basicConfig(level=logging.INFO)

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura y devuelve un logger con el nombre especificado.
    
    Args:
        name (str): Nombre del logger.
        log_file (str, optional): Archivo donde se guardarán los logs. 
                                 Si es None, solo se usará la consola.
        level (int, optional): Nivel de log. Por defecto, INFO.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # Crear formatter
    console_formatter = logging.Formatter(CONSOLE_FORMAT)
    file_formatter = logging.Formatter(FILE_FORMAT)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Configurar handler para archivo si se especifica
    if log_file:
        file_path = os.path.join(LOG_DIR, log_file)
        try:
            file_handler = RotatingFileHandler(
                file_path, 
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5,
                delay=False
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            # Escribir un mensaje de prueba para verificar que el archivo se puede escribir
            logger.info(f"Logger {name} inicializado correctamente. Escribiendo en {file_path}")
        except Exception as e:
            logger.error(f"Error al configurar el archivo de log {file_path}: {e}")
            # Intentar crear el archivo manualmente
            try:
                with open(file_path, 'a') as f:
                    f.write(f"Logger {name} inicializado manualmente\n")
                logger.info(f"Archivo de log {file_path} creado manualmente")
            except Exception as e:
                logger.error(f"No se pudo crear el archivo de log {file_path} manualmente: {e}")
    
    return logger

# Loggers predefinidos para diferentes componentes
api_logger = setup_logger('api', 'api.log')
db_logger = setup_logger('db', 'db.log')
update_logger = setup_logger('update', 'update.log')
