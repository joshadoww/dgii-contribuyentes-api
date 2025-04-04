#!/usr/bin/env python3
"""
Script para descargar y actualizar la base de datos de contribuyentes DGII.
"""
import os
import sys
import requests
import zipfile
import io
import pandas as pd
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask

# Agregar el directorio raíz al path para poder importar los módulos de la aplicación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar después de agregar el path
from app.models import db, Contribuyente, ActualizacionDB
from app.utils.logger import update_logger as logger

# Cargar variables de entorno
load_dotenv()

# Crear una instancia de Flask para este script
app = Flask(__name__)

# Configuración de la base de datos
if os.getenv('DB_TYPE') == 'sqlite':
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.getenv('DB_PATH', 'data/dgii_contribuyentes.db')}"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con esta aplicación
db.init_app(app)

def descargar_archivo_dgii():
    """
    Descarga el archivo ZIP de contribuyentes desde la DGII.
    
    Returns:
        BytesIO: Objeto con el contenido del archivo ZIP.
    """
    url = os.getenv('DGII_URL', 'https://www.dgii.gov.do/app/WebApps/Consultas/RNC/DGII_RNC.zip')
    
    try:
        logger.info(f"Descargando archivo desde {url}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # Lanzar excepción si hay error HTTP
        
        # Devolver el contenido como un objeto BytesIO
        logger.info(f"Archivo descargado correctamente ({len(response.content)} bytes)")
        return io.BytesIO(response.content)
    except Exception as e:
        logger.error(f"Error al descargar el archivo: {e}")
        return None

def procesar_archivo_zip(zip_content):
    """
    Procesa el archivo ZIP y extrae los datos de contribuyentes.
    
    Args:
        zip_content (BytesIO): Contenido del archivo ZIP.
        
    Returns:
        DataFrame: DataFrame de pandas con los datos procesados.
    """
    try:
        # Crear un objeto ZipFile
        with zipfile.ZipFile(zip_content) as z:
            # Listar los archivos en el ZIP
            file_list = z.namelist()
            logger.info(f"Archivos en el ZIP: {file_list}")
            
            # Buscar el archivo TXT (normalmente hay solo uno)
            txt_files = [f for f in file_list if f.lower().endswith('.txt')]
            
            if not txt_files:
                logger.error("No se encontró ningún archivo TXT en el ZIP.")
                return None
            
            logger.info(f"Archivo TXT encontrado: {txt_files[0]}")
            
            # Extraer el primer archivo TXT a un directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                txt_file = z.extract(txt_files[0], temp_dir)
                
                # Mostrar las primeras líneas del archivo para depuración
                with open(txt_file, 'r', encoding='latin1') as f:
                    logger.debug("Primeras 5 líneas del archivo:")
                    for i, line in enumerate(f):
                        if i < 5:
                            logger.debug(line.strip())
                        else:
                            break
                    f.seek(0)  # Volver al inicio del archivo
                
                # Leer el archivo con pandas - IMPORTANTE: El archivo no tiene encabezados
                df = pd.read_csv(
                    txt_file, 
                    sep='|', 
                    encoding='latin1',
                    dtype=str,  # Todos los campos como string
                    keep_default_na=False,  # No convertir valores vacíos a NaN
                    header=None  # No usar la primera fila como encabezados
                )
                
                logger.info(f"Forma del DataFrame: {df.shape}")
                logger.debug(f"Primeras filas del DataFrame:")
                logger.debug(df.head().to_string())
                
                # Asignar nombres de columnas basados en la estructura del archivo
                # Basado en la estructura observada en las primeras líneas
                column_names = [
                    'rnc', 'nombre', 'nombre_comercial', 'actividad_economica', 
                    'col5', 'col6', 'col7', 'col8', 'fecha_constitucion', 
                    'estado', 'regimen_pagos'
                ]
                
                # Asignar nombres solo a las columnas que existen
                if len(df.columns) <= len(column_names):
                    df.columns = column_names[:len(df.columns)]
                else:
                    # Si hay más columnas de las esperadas, nombrar las adicionales
                    df.columns = column_names + [f'col{i+1}' for i in range(len(column_names), len(df.columns))]
                
                logger.info(f"Columnas asignadas: {df.columns.tolist()}")
                
                # Asegurarse de que existan todas las columnas necesarias
                required_columns = ['rnc', 'nombre']
                for col in required_columns:
                    if col not in df.columns:
                        logger.error(f"Error: Columna requerida '{col}' no encontrada en el archivo.")
                        logger.error(f"Columnas disponibles: {df.columns.tolist()}")
                        return None
                
                # Columnas opcionales (si no existen, crear con valores vacíos)
                optional_columns = ['nombre_comercial', 'categoria', 'regimen_pagos', 'estado', 'actividad_economica']
                for col in optional_columns:
                    if col not in df.columns:
                        df[col] = ''
                
                # Limpiar RNC (eliminar guiones y espacios)
                df['rnc'] = df['rnc'].str.replace('-', '').str.replace(' ', '')
                
                # Limpiar otros campos
                for col in df.columns:
                    if col in df and isinstance(df[col], pd.Series):
                        df[col] = df[col].str.strip()
                
                logger.info(f"DataFrame procesado exitosamente con {len(df)} registros")
                return df
    except Exception as e:
        logger.error(f"Error al procesar el archivo ZIP: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def actualizar_base_datos(df):
    """
    Actualiza la base de datos con los datos procesados.
    
    Args:
        df (DataFrame): DataFrame con los datos de contribuyentes.
        
    Returns:
        dict: Estadísticas de la actualización.
    """
    if df is None or df.empty:
        logger.error("No hay datos para actualizar")
        return {
            'estado': 'error',
            'mensaje': 'No hay datos para actualizar',
            'registros_procesados': 0,
            'registros_nuevos': 0,
            'registros_actualizados': 0
        }
    
    try:
        # Inicializar contadores
        registros_procesados = len(df)
        registros_nuevos = 0
        registros_actualizados = 0
        
        # Procesar por lotes para evitar problemas de memoria
        batch_size = 1000
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        logger.info(f"Procesando {registros_procesados} registros en {total_batches} lotes...")
        
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            logger.info(f"Procesando lote {i+1}/{total_batches} ({start_idx+1}-{end_idx})...")
            
            # Procesar cada registro del lote
            for _, row in batch_df.iterrows():
                # Buscar si el contribuyente ya existe
                contribuyente = Contribuyente.query.filter_by(rnc=row['rnc']).first()
                
                if contribuyente:
                    # Actualizar contribuyente existente
                    contribuyente.nombre = row['nombre']
                    contribuyente.nombre_comercial = row['nombre_comercial']
                    contribuyente.categoria = row['categoria']
                    contribuyente.regimen_pagos = row['regimen_pagos']
                    contribuyente.estado = row['estado']
                    contribuyente.actividad_economica = row['actividad_economica']
                    contribuyente.fecha_actualizacion = datetime.utcnow()
                    registros_actualizados += 1
                else:
                    # Crear nuevo contribuyente
                    nuevo_contribuyente = Contribuyente(
                        rnc=row['rnc'],
                        nombre=row['nombre'],
                        nombre_comercial=row['nombre_comercial'],
                        categoria=row['categoria'],
                        regimen_pagos=row['regimen_pagos'],
                        estado=row['estado'],
                        actividad_economica=row['actividad_economica']
                    )
                    db.session.add(nuevo_contribuyente)
                    registros_nuevos += 1
            
            # Guardar cambios del lote
            db.session.commit()
            logger.info(f"Lote {i+1}/{total_batches} procesado. Nuevos: {registros_nuevos}, Actualizados: {registros_actualizados}")
        
        # Registrar la actualización
        actualizacion = ActualizacionDB(
            registros_procesados=registros_procesados,
            registros_nuevos=registros_nuevos,
            registros_actualizados=registros_actualizados,
            estado='success',
            mensaje='Actualización completada con éxito'
        )
        db.session.add(actualizacion)
        db.session.commit()
        
        logger.info(f"Actualización completada con éxito. Total: {registros_procesados}, Nuevos: {registros_nuevos}, Actualizados: {registros_actualizados}")
        return {
            'estado': 'success',
            'mensaje': 'Actualización completada con éxito',
            'registros_procesados': registros_procesados,
            'registros_nuevos': registros_nuevos,
            'registros_actualizados': registros_actualizados
        }
    except Exception as e:
        db.session.rollback()
        
        # Registrar el error
        error_msg = str(e)
        actualizacion = ActualizacionDB(
            registros_procesados=registros_procesados if 'registros_procesados' in locals() else 0,
            registros_nuevos=registros_nuevos if 'registros_nuevos' in locals() else 0,
            registros_actualizados=registros_actualizados if 'registros_actualizados' in locals() else 0,
            estado='error',
            mensaje=f"Error al actualizar la base de datos: {error_msg}"
        )
        db.session.add(actualizacion)
        db.session.commit()
        
        logger.error(f"Error al actualizar la base de datos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'estado': 'error',
            'mensaje': f"Error al actualizar la base de datos: {error_msg}",
            'registros_procesados': registros_procesados if 'registros_procesados' in locals() else 0,
            'registros_nuevos': registros_nuevos if 'registros_nuevos' in locals() else 0,
            'registros_actualizados': registros_actualizados if 'registros_actualizados' in locals() else 0
        }

def update_database():
    """
    Función principal para actualizar la base de datos.
    Descarga el archivo, lo procesa y actualiza la base de datos.
    
    Returns:
        dict: Estadísticas de la actualización.
    """
    logger.info("Iniciando actualización de la base de datos...")
    
    # Descargar el archivo
    zip_content = descargar_archivo_dgii()
    if not zip_content:
        logger.error("Error al descargar el archivo")
        return {
            'estado': 'error',
            'mensaje': 'Error al descargar el archivo',
            'registros_procesados': 0,
            'registros_nuevos': 0,
            'registros_actualizados': 0
        }
    
    # Procesar el archivo
    df = procesar_archivo_zip(zip_content)
    if df is None:
        logger.error("Error al procesar el archivo")
        return {
            'estado': 'error',
            'mensaje': 'Error al procesar el archivo',
            'registros_procesados': 0,
            'registros_nuevos': 0,
            'registros_actualizados': 0
        }
    
    # Actualizar la base de datos
    with app.app_context():
        resultado = actualizar_base_datos(df)
    
    logger.info(f"Actualización completada: {resultado['estado']}")
    logger.info(f"Registros procesados: {resultado['registros_procesados']}")
    logger.info(f"Registros nuevos: {resultado['registros_nuevos']}")
    logger.info(f"Registros actualizados: {resultado['registros_actualizados']}")
    
    return resultado

if __name__ == '__main__':
    # Ejecutar la actualización
    resultado = update_database()
    
    # Salir con código de error si hubo problemas
    if resultado['estado'] != 'success':
        sys.exit(1)
