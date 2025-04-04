"""
Endpoints de la API para consulta de contribuyentes DGII.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc
from app.models import Contribuyente, ActualizacionDB
from app import db
from app.utils.logger import api_logger as logger

api_bp = Blueprint('api', __name__)

# Los decoradores de límite se aplicarán desde app.py

@api_bp.route('/contribuyente/<rnc>', methods=['GET'])
def get_contribuyente(rnc):
    """
    Endpoint para consultar un contribuyente por RNC.
    
    Args:
        rnc (str): RNC del contribuyente a consultar.
        
    Returns:
        JSON con la información del contribuyente o un mensaje de error.
    """
    # Limpiar el RNC (eliminar guiones y espacios)
    rnc_limpio = rnc.replace('-', '').replace(' ', '')
    
    logger.info(f"Consultando contribuyente con RNC: {rnc_limpio}")
    
    # Buscar el contribuyente en la base de datos
    contribuyente = Contribuyente.query.filter_by(rnc=rnc_limpio).first()
    
    if not contribuyente:
        logger.info(f"Contribuyente con RNC {rnc_limpio} no encontrado")
        return jsonify({
            'error': 'Contribuyente no encontrado',
            'rnc': rnc_limpio
        }), 404
    
    # Devolver la información del contribuyente
    logger.info(f"Contribuyente con RNC {rnc_limpio} encontrado: {contribuyente.nombre}")
    return jsonify({
        'contribuyente': contribuyente.to_dict(),
        'status': 'success'
    })

@api_bp.route('/contribuyentes', methods=['GET'])
def buscar_contribuyentes():
    """
    Endpoint para buscar contribuyentes por nombre o nombre comercial.
    
    Query params:
        nombre (str): Texto a buscar en el nombre o nombre comercial.
        limit (int): Límite de resultados (por defecto 10, máximo 100).
        offset (int): Desplazamiento para paginación.
        
    Returns:
        JSON con la lista de contribuyentes que coinciden con la búsqueda.
    """
    # Obtener parámetros de la consulta
    nombre = request.args.get('nombre', '')
    limit = min(int(request.args.get('limit', 10)), 100)  # Máximo 100 resultados
    offset = int(request.args.get('offset', 0))
    
    logger.info(f"Búsqueda de contribuyentes con nombre: '{nombre}', limit: {limit}, offset: {offset}")
    
    if not nombre or len(nombre) < 3:
        logger.warning(f"Búsqueda con texto muy corto: '{nombre}'")
        return jsonify({
            'error': 'El texto de búsqueda debe tener al menos 3 caracteres',
            'status': 'error'
        }), 400
    
    # Construir la consulta
    query = Contribuyente.query.filter(
        (Contribuyente.nombre.ilike(f'%{nombre}%')) | 
        (Contribuyente.nombre_comercial.ilike(f'%{nombre}%'))
    ).order_by(Contribuyente.nombre).limit(limit).offset(offset)
    
    # Ejecutar la consulta
    contribuyentes = query.all()
    total = Contribuyente.query.filter(
        (Contribuyente.nombre.ilike(f'%{nombre}%')) | 
        (Contribuyente.nombre_comercial.ilike(f'%{nombre}%'))
    ).count()
    
    logger.info(f"Búsqueda completada. Se encontraron {len(contribuyentes)} de {total} resultados")
    
    # Devolver los resultados
    return jsonify({
        'contribuyentes': [c.to_dict() for c in contribuyentes],
        'total': total,
        'limit': limit,
        'offset': offset,
        'status': 'success'
    })

@api_bp.route('/status', methods=['GET'])
def get_status():
    """
    Endpoint para consultar el estado de la base de datos.
    
    Returns:
        JSON con información sobre la última actualización de la base de datos.
    """
    logger.info("Consultando estado de la API")
    
    # Obtener la última actualización
    ultima_actualizacion = ActualizacionDB.query.order_by(desc(ActualizacionDB.fecha)).first()
    
    if not ultima_actualizacion:
        logger.info("No se ha realizado ninguna actualización")
        return jsonify({
            'mensaje': 'No se ha realizado ninguna actualización',
            'status': 'warning'
        })
    
    # Contar el total de contribuyentes
    total_contribuyentes = Contribuyente.query.count()
    
    logger.info(f"Última actualización: {ultima_actualizacion.fecha}")
    
    # Devolver la información de estado
    return jsonify({
        'ultima_actualizacion': {
            'fecha': ultima_actualizacion.fecha.isoformat(),
            'registros_procesados': ultima_actualizacion.registros_procesados,
            'registros_nuevos': ultima_actualizacion.registros_nuevos,
            'registros_actualizados': ultima_actualizacion.registros_actualizados,
            'estado': ultima_actualizacion.estado,
            'mensaje': ultima_actualizacion.mensaje
        },
        'total_contribuyentes': total_contribuyentes,
        'status': 'success'
    })

@api_bp.route('/contribuyentes/estado/<estado>', methods=['GET'])
def contribuyentes_por_estado(estado):
    """
    Endpoint para obtener contribuyentes por estado (ACTIVO, SUSPENDIDO, etc.).
    
    Args:
        estado (str): Estado de los contribuyentes a buscar.
        
    Query params:
        limit (int): Límite de resultados (por defecto 10, máximo 100).
        offset (int): Desplazamiento para paginación.
        
    Returns:
        JSON con la lista de contribuyentes que tienen el estado especificado.
    """
    # Normalizar el estado (convertir a mayúsculas)
    estado = estado.upper()
    
    logger.info(f"Buscando contribuyentes con estado: {estado}")
    
    # Validar que el estado sea uno de los valores permitidos
    estados_validos = ['ACTIVO', 'SUSPENDIDO', 'INACTIVO']
    if estado not in estados_validos:
        logger.warning(f"Estado no válido: {estado}")
        return jsonify({
            'error': f'Estado no válido. Los valores permitidos son: {", ".join(estados_validos)}',
            'status': 'error'
        }), 400
    
    # Obtener parámetros de paginación
    limit = min(int(request.args.get('limit', 10)), 100)
    offset = int(request.args.get('offset', 0))
    
    logger.info(f"Buscando contribuyentes con estado {estado}, limit: {limit}, offset: {offset}")
    
    # Buscar contribuyentes por estado
    query = Contribuyente.query.filter_by(estado=estado).order_by(Contribuyente.nombre)
    
    # Obtener el total de resultados
    total = query.count()
    
    logger.info(f"Se encontraron {total} contribuyentes con estado {estado}")
    
    # Aplicar paginación
    contribuyentes = query.limit(limit).offset(offset).all()
    
    logger.info(f"Se devuelven {len(contribuyentes)} contribuyentes con estado {estado}")
    
    # Devolver los resultados
    return jsonify({
        'contribuyentes': [c.to_dict() for c in contribuyentes],
        'total': total,
        'limit': limit,
        'offset': offset,
        'estado': estado,
        'status': 'success'
    })

@api_bp.route('/contribuyentes/actividad', methods=['GET'])
def contribuyentes_por_actividad():
    """
    Endpoint para buscar contribuyentes por actividad económica.
    
    Query params:
        actividad (str): Texto a buscar en la actividad económica.
        limit (int): Límite de resultados (por defecto 10, máximo 100).
        offset (int): Desplazamiento para paginación.
        
    Returns:
        JSON con la lista de contribuyentes que coinciden con la actividad económica.
    """
    actividad = request.args.get('actividad', '')
    limit = min(int(request.args.get('limit', 10)), 100)
    offset = int(request.args.get('offset', 0))
    
    logger.info(f"Buscando contribuyentes con actividad: {actividad}, limit: {limit}, offset: {offset}")
    
    if not actividad or len(actividad) < 3:
        logger.warning(f"Búsqueda con texto muy corto: '{actividad}'")
        return jsonify({
            'error': 'El parámetro "actividad" es requerido y debe tener al menos 3 caracteres',
            'status': 'error'
        }), 400
    
    # Buscar contribuyentes que contengan el texto en la actividad económica
    query = Contribuyente.query.filter(
        Contribuyente.actividad_economica.like(f'%{actividad}%')
    ).order_by(Contribuyente.nombre)
    
    # Obtener el total de resultados
    total = query.count()
    
    logger.info(f"Se encontraron {total} contribuyentes con actividad {actividad}")
    
    # Aplicar paginación
    contribuyentes = query.limit(limit).offset(offset).all()
    
    logger.info(f"Se devuelven {len(contribuyentes)} contribuyentes con actividad {actividad}")
    
    # Devolver los resultados
    return jsonify({
        'contribuyentes': [c.to_dict() for c in contribuyentes],
        'total': total,
        'limit': limit,
        'offset': offset,
        'actividad': actividad,
        'status': 'success'
    })

@api_bp.route('/estadisticas', methods=['GET'])
def get_estadisticas():
    """
    Endpoint para obtener estadísticas generales de los contribuyentes.
    
    Returns:
        JSON con estadísticas sobre los contribuyentes en la base de datos.
    """
    logger.info("Consultando estadísticas de contribuyentes")
    
    try:
        # Estadísticas por estado
        estados = Contribuyente.query.with_entities(
            Contribuyente.estado, 
            func.count(Contribuyente.id).label('total')
        ).group_by(Contribuyente.estado).all()
        
        # Estadísticas por régimen de pagos
        regimenes = Contribuyente.query.with_entities(
            Contribuyente.regimen_pagos, 
            func.count(Contribuyente.id).label('total')
        ).group_by(Contribuyente.regimen_pagos).all()
        
        # Top 10 actividades económicas más comunes
        actividades = Contribuyente.query.with_entities(
            Contribuyente.actividad_economica, 
            func.count(Contribuyente.id).label('total')
        ).group_by(Contribuyente.actividad_economica).order_by(desc('total')).limit(10).all()
        
        logger.info("Estadísticas obtenidas")
        
        # Devolver las estadísticas
        return jsonify({
            'estadisticas': {
                'por_estado': {estado: total for estado, total in estados if estado},
                'por_regimen': {regimen: total for regimen, total in regimenes if regimen},
                'top_actividades': {actividad: total for actividad, total in actividades if actividad}
            },
            'total_contribuyentes': Contribuyente.query.count(),
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return jsonify({
            'error': 'Error al obtener estadísticas',
            'mensaje': str(e),
            'status': 'error'
        }), 500

@api_bp.route('/validar/<rnc>', methods=['GET'])
def validar_rnc(rnc):
    """
    Endpoint para validar si un RNC es válido y está registrado.
    
    Args:
        rnc (str): RNC a validar.
        
    Returns:
        JSON con información sobre la validez del RNC.
    """
    # Limpiar el RNC (eliminar guiones y espacios)
    rnc_limpio = rnc.replace('-', '').replace(' ', '')
    
    logger.info(f"Validando RNC: {rnc_limpio}")
    
    # Validar formato básico del RNC
    if not rnc_limpio.isdigit():
        logger.warning(f"RNC no válido: {rnc_limpio}")
        return jsonify({
            'valido': False,
            'registrado': False,
            'error': 'El RNC debe contener solo dígitos',
            'rnc': rnc_limpio,
            'status': 'error'
        })
    
    # Validar longitud del RNC (9 o 11 dígitos)
    if len(rnc_limpio) not in [9, 11]:
        logger.warning(f"RNC no válido: {rnc_limpio}")
        return jsonify({
            'valido': False,
            'registrado': False,
            'error': 'El RNC debe tener 9 u 11 dígitos',
            'rnc': rnc_limpio,
            'status': 'error'
        })
    
    # Buscar el contribuyente en la base de datos
    contribuyente = Contribuyente.query.filter_by(rnc=rnc_limpio).first()
    
    if not contribuyente:
        logger.info(f"RNC {rnc_limpio} no encontrado")
        return jsonify({
            'valido': True,
            'registrado': False,
            'mensaje': 'El RNC tiene un formato válido pero no está registrado en la DGII',
            'rnc': rnc_limpio,
            'status': 'warning'
        })
    
    # Devolver la información del contribuyente
    logger.info(f"RNC {rnc_limpio} válido y registrado")
    return jsonify({
        'valido': True,
        'registrado': True,
        'contribuyente': contribuyente.to_dict(),
        'status': 'success'
    })

@api_bp.route('/busqueda-avanzada', methods=['GET'])
def busqueda_avanzada():
    """
    Endpoint para realizar búsquedas avanzadas con múltiples criterios.
    
    Query params:
        nombre (str): Texto a buscar en el nombre.
        nombre_comercial (str): Texto a buscar en el nombre comercial.
        actividad (str): Texto a buscar en la actividad económica.
        estado (str): Estado del contribuyente (ACTIVO, SUSPENDIDO, etc.).
        regimen (str): Régimen de pagos.
        limit (int): Límite de resultados (por defecto 10, máximo 100).
        offset (int): Desplazamiento para paginación.
        
    Returns:
        JSON con la lista de contribuyentes que cumplen con los criterios de búsqueda.
    """
    # Obtener parámetros de búsqueda
    nombre = request.args.get('nombre', '')
    nombre_comercial = request.args.get('nombre_comercial', '')
    actividad = request.args.get('actividad', '')
    estado = request.args.get('estado', '')
    regimen = request.args.get('regimen', '')
    
    logger.info(f"Búsqueda avanzada con parámetros: nombre={nombre}, nombre_comercial={nombre_comercial}, actividad={actividad}, estado={estado}, regimen={regimen}")
    
    # Obtener parámetros de paginación
    limit = min(int(request.args.get('limit', 10)), 100)
    offset = int(request.args.get('offset', 0))
    
    # Validar que al menos un criterio de búsqueda esté presente
    if not any([nombre, nombre_comercial, actividad, estado, regimen]):
        logger.warning("No se especificó ningún criterio de búsqueda")
        return jsonify({
            'error': 'Debe especificar al menos un criterio de búsqueda',
            'status': 'error'
        }), 400
    
    # Construir la consulta base
    query = Contribuyente.query
    
    # Aplicar filtros según los parámetros proporcionados
    if nombre and len(nombre) >= 3:
        query = query.filter(Contribuyente.nombre.like(f'%{nombre}%'))
    
    if nombre_comercial and len(nombre_comercial) >= 3:
        query = query.filter(Contribuyente.nombre_comercial.like(f'%{nombre_comercial}%'))
    
    if actividad and len(actividad) >= 3:
        query = query.filter(Contribuyente.actividad_economica.like(f'%{actividad}%'))
    
    if estado:
        query = query.filter(Contribuyente.estado == estado.upper())
    
    if regimen:
        query = query.filter(Contribuyente.regimen_pagos == regimen.upper())
    
    # Ordenar por nombre
    query = query.order_by(Contribuyente.nombre)
    
    # Obtener el total de resultados
    total = query.count()
    
    logger.info(f"Búsqueda avanzada completada. Se encontraron {total} resultados")
    
    # Aplicar paginación
    contribuyentes = query.limit(limit).offset(offset).all()
    
    logger.info(f"Se devuelven {len(contribuyentes)} contribuyentes")
    
    # Devolver los resultados
    return jsonify({
        'contribuyentes': [c.to_dict() for c in contribuyentes],
        'total': total,
        'limit': limit,
        'offset': offset,
        'criterios': {
            'nombre': nombre if nombre else None,
            'nombre_comercial': nombre_comercial if nombre_comercial else None,
            'actividad': actividad if actividad else None,
            'estado': estado if estado else None,
            'regimen': regimen if regimen else None
        },
        'status': 'success'
    })
