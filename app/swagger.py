"""
Configuración de Swagger para la API DGII.
Define la documentación de la API utilizando el formato OpenAPI/Swagger.
"""
import json

def get_swagger_json():
    """
    Genera la documentación de la API en formato JSON para Swagger.
    
    Returns:
        str: Documentación de la API en formato JSON.
    """
    swagger_doc = {
        "swagger": "2.0",
        "info": {
            "title": "API DGII Contribuyentes",
            "description": "API para consultar información de contribuyentes de la DGII (Dirección General de Impuestos Internos) de República Dominicana.",
            "version": "1.0.0",
            "contact": {
                "email": "admin@example.com"
            }
        },
        "basePath": "/api",
        "schemes": ["http", "https"],
        "tags": [
            {
                "name": "Contribuyentes",
                "description": "Operaciones relacionadas con contribuyentes"
            },
            {
                "name": "Estadísticas",
                "description": "Operaciones relacionadas con estadísticas y reportes"
            },
            {
                "name": "Sistema",
                "description": "Operaciones relacionadas con el estado y mantenimiento del sistema"
            },
            {
                "name": "Usuarios",
                "description": "Gestión de usuarios y autenticación"
            },
            {
                "name": "Tokens",
                "description": "Gestión de tokens de autenticación"
            },
            {
                "name": "Administración",
                "description": "Operaciones administrativas"
            }
        ],
        "paths": {
            "/contribuyente/{rnc}": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Obtener información de un contribuyente por RNC",
                    "description": "Devuelve la información detallada de un contribuyente a partir de su RNC",
                    "parameters": [
                        {
                            "name": "rnc",
                            "in": "path",
                            "description": "RNC del contribuyente",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Información del contribuyente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "rnc": {"type": "string"},
                                    "nombre": {"type": "string"},
                                    "nombre_comercial": {"type": "string"},
                                    "categoria": {"type": "string"},
                                    "regimen_pagos": {"type": "string"},
                                    "estado": {"type": "string"},
                                    "actividad_economica": {"type": "string"},
                                    "fecha_actualizacion": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "404": {
                            "description": "Contribuyente no encontrado",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "rnc": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/contribuyentes": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Listar contribuyentes",
                    "description": "Devuelve una lista paginada de contribuyentes",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Número de página",
                            "required": False,
                            "type": "integer",
                            "default": 1
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Número de elementos por página",
                            "required": False,
                            "type": "integer",
                            "default": 20
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de contribuyentes",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "contribuyentes": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "rnc": {"type": "string"},
                                                "nombre": {"type": "string"},
                                                "nombre_comercial": {"type": "string"},
                                                "categoria": {"type": "string"},
                                                "regimen_pagos": {"type": "string"},
                                                "estado": {"type": "string"},
                                                "actividad_economica": {"type": "string"},
                                                "fecha_actualizacion": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    },
                                    "total": {"type": "integer"},
                                    "page": {"type": "integer"},
                                    "per_page": {"type": "integer"},
                                    "total_pages": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            "/contribuyentes/estado/{estado}": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Listar contribuyentes por estado",
                    "description": "Devuelve una lista paginada de contribuyentes filtrados por estado",
                    "parameters": [
                        {
                            "name": "estado",
                            "in": "path",
                            "description": "Estado del contribuyente",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Número de página",
                            "required": False,
                            "type": "integer",
                            "default": 1
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Número de elementos por página",
                            "required": False,
                            "type": "integer",
                            "default": 20
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de contribuyentes",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "contribuyentes": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    },
                                    "total": {"type": "integer"},
                                    "page": {"type": "integer"},
                                    "per_page": {"type": "integer"},
                                    "total_pages": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            "/contribuyentes/actividad": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Listar actividades económicas",
                    "description": "Devuelve una lista de actividades económicas disponibles",
                    "responses": {
                        "200": {
                            "description": "Lista de actividades económicas",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "actividades": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "total": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            "/estadisticas": {
                "get": {
                    "tags": ["Estadísticas"],
                    "summary": "Obtener estadísticas",
                    "description": "Devuelve estadísticas generales sobre los contribuyentes",
                    "responses": {
                        "200": {
                            "description": "Estadísticas",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "total_contribuyentes": {"type": "integer"},
                                    "por_estado": {"type": "object"},
                                    "por_categoria": {"type": "object"},
                                    "ultima_actualizacion": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            },
            "/validar/{rnc}": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Validar RNC",
                    "description": "Valida si un RNC es válido y existe en la base de datos",
                    "parameters": [
                        {
                            "name": "rnc",
                            "in": "path",
                            "description": "RNC a validar",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resultado de la validación",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "rnc": {"type": "string"},
                                    "valido": {"type": "boolean"},
                                    "existe": {"type": "boolean"},
                                    "mensaje": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/busqueda-avanzada": {
                "get": {
                    "tags": ["Contribuyentes"],
                    "summary": "Búsqueda avanzada de contribuyentes",
                    "description": "Permite realizar búsquedas avanzadas de contribuyentes con múltiples criterios",
                    "parameters": [
                        {
                            "name": "nombre",
                            "in": "query",
                            "description": "Nombre o parte del nombre del contribuyente",
                            "required": False,
                            "type": "string"
                        },
                        {
                            "name": "actividad",
                            "in": "query",
                            "description": "Actividad económica",
                            "required": False,
                            "type": "string"
                        },
                        {
                            "name": "estado",
                            "in": "query",
                            "description": "Estado del contribuyente",
                            "required": False,
                            "type": "string"
                        },
                        {
                            "name": "categoria",
                            "in": "query",
                            "description": "Categoría del contribuyente",
                            "required": False,
                            "type": "string"
                        },
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Número de página",
                            "required": False,
                            "type": "integer",
                            "default": 1
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Número de elementos por página",
                            "required": False,
                            "type": "integer",
                            "default": 20
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resultados de la búsqueda",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "contribuyentes": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    },
                                    "total": {"type": "integer"},
                                    "page": {"type": "integer"},
                                    "per_page": {"type": "integer"},
                                    "total_pages": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            "/status": {
                "get": {
                    "tags": ["Sistema"],
                    "summary": "Estado de la API",
                    "description": "Devuelve información sobre el estado de la API y la última actualización de la base de datos",
                    "responses": {
                        "200": {
                            "description": "Estado de la API",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "mensaje": {"type": "string"},
                                    "ultima_actualizacion": {"type": "string", "format": "date-time"},
                                    "registros_procesados": {"type": "integer"},
                                    "registros_nuevos": {"type": "integer"},
                                    "registros_actualizados": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            },
            "/usuarios": {
                "get": {
                    "tags": ["Usuarios"],
                    "summary": "Listar todos los usuarios",
                    "description": "Devuelve una lista de usuarios",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de usuarios",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "username": {"type": "string"},
                                        "rol": {"type": "string"},
                                        "activo": {"type": "boolean"},
                                        "fecha_creacion": {"type": "string", "format": "date-time"},
                                        "ultima_actividad": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        }
                    }
                },
                "post": {
                    "tags": ["Usuarios"],
                    "summary": "Crear un nuevo usuario",
                    "description": "Crea un nuevo usuario",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                    "rol": {"type": "string", "enum": ["admin", "usuario"]},
                                    "activo": {"type": "boolean"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Usuario creado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"},
                                    "id": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "rol": {"type": "string"}
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos"
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "409": {
                            "description": "El nombre de usuario ya existe"
                        }
                    }
                }
            },
            "/usuarios/{usuario_id}": {
                "get": {
                    "tags": ["Usuarios"],
                    "summary": "Obtener información detallada de un usuario",
                    "description": "Devuelve información detallada de un usuario",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "usuario_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del usuario"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Información del usuario",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "rol": {"type": "string"},
                                    "activo": {"type": "boolean"},
                                    "fecha_creacion": {"type": "string", "format": "date-time"},
                                    "ultima_actividad": {"type": "string", "format": "date-time"},
                                    "tokens_activos": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "token": {"type": "string"},
                                                "fecha_creacion": {"type": "string", "format": "date-time"},
                                                "fecha_expiracion": {"type": "string", "format": "date-time"},
                                                "ultimo_uso": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "404": {
                            "description": "Usuario no encontrado"
                        }
                    }
                },
                "put": {
                    "tags": ["Usuarios"],
                    "summary": "Actualizar un usuario existente",
                    "description": "Actualiza un usuario existente",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "usuario_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del usuario"
                        },
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                    "rol": {"type": "string", "enum": ["admin", "usuario"]},
                                    "activo": {"type": "boolean"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Usuario actualizado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"},
                                    "id": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "rol": {"type": "string"},
                                    "activo": {"type": "boolean"}
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "404": {
                            "description": "Usuario no encontrado"
                        },
                        "409": {
                            "description": "El nombre de usuario ya existe"
                        }
                    }
                },
                "delete": {
                    "tags": ["Usuarios"],
                    "summary": "Eliminar un usuario",
                    "description": "Elimina un usuario",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "usuario_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del usuario"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Usuario eliminado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"}
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "404": {
                            "description": "Usuario no encontrado"
                        }
                    }
                }
            },
            "/usuarios/{usuario_id}/tokens": {
                "post": {
                    "tags": ["Usuarios"],
                    "summary": "Generar un nuevo token para un usuario",
                    "description": "Genera un nuevo token para un usuario",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "usuario_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del usuario"
                        },
                        {
                            "name": "body",
                            "in": "body",
                            "required": False,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "duracion": {"type": "integer", "description": "Duración del token en segundos (por defecto 30 días)"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Token generado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"},
                                    "token": {"type": "string"},
                                    "fecha_expiracion": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "404": {
                            "description": "Usuario no encontrado"
                        }
                    }
                }
            },
            "/usuarios/{usuario_id}/tokens/{token_id}": {
                "delete": {
                    "tags": ["Usuarios"],
                    "summary": "Revocar un token específico",
                    "description": "Revoca un token específico",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "usuario_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del usuario"
                        },
                        {
                            "name": "token_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "description": "ID del token"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Token revocado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"}
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        },
                        "403": {
                            "description": "Prohibido - Se requieren privilegios de administrador"
                        },
                        "404": {
                            "description": "Usuario o token no encontrado"
                        }
                    }
                }
            },
            "/usuarios/perfil": {
                "get": {
                    "tags": ["Usuarios"],
                    "summary": "Obtener el perfil del usuario autenticado",
                    "description": "Devuelve el perfil del usuario autenticado",
                    "security": [
                        {"BasicAuth": []},
                        {"BearerAuth": []},
                        {"ApiKeyAuth": []}
                    ],
                    "responses": {
                        "200": {
                            "description": "Perfil del usuario",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "rol": {"type": "string"},
                                    "fecha_creacion": {"type": "string", "format": "date-time"},
                                    "ultima_actividad": {"type": "string", "format": "date-time"},
                                    "tokens_activos": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "token": {"type": "string"},
                                                "fecha_creacion": {"type": "string", "format": "date-time"},
                                                "fecha_expiracion": {"type": "string", "format": "date-time"},
                                                "ultimo_uso": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No autorizado"
                        }
                    }
                }
            },
            "/usuarios/perfil/token": {
                "post": {
                    "tags": ["Usuarios"],
                    "summary": "Generar un token para el usuario autenticado",
                    "description": "Genera un token para el usuario autenticado",
                    "security": [
                        {"BasicAuth": []}
                    ],
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": False,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "duracion": {"type": "integer", "description": "Duración del token en segundos (por defecto 30 días)"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Token generado correctamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "mensaje": {"type": "string"},
                                    "token": {"type": "string"},
                                    "fecha_expiracion": {"type": "string", "format": "date-time"}
                                }
                            }
                        },
                        "400": {
                            "description": "Esta funcionalidad solo está disponible para usuarios registrados en la base de datos"
                        },
                        "401": {
                            "description": "No autorizado"
                        }
                    }
                }
            }
        },
        "securityDefinitions": {
            "BasicAuth": {
                "type": "basic",
                "description": "Autenticación básica HTTP"
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Autenticación por API Key"
            },
            "BearerAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Autenticación por token Bearer. Ejemplo: 'Bearer {token}'"
            }
        },
        "definitions": {
            "Contribuyente": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "rnc": {"type": "string"},
                    "nombre": {"type": "string"},
                    "nombre_comercial": {"type": "string"},
                    "categoria": {"type": "string"},
                    "regimen_pagos": {"type": "string"},
                    "estado": {"type": "string"},
                    "actividad_economica": {"type": "string"},
                    "fecha_actualizacion": {"type": "string", "format": "date-time"}
                }
            }
        }
    }
    
    # Añadir documentación para endpoints administrativos
    admin_paths = {
        "/admin/actualizar-db": {
            "post": {
                "tags": ["Administración"],
                "summary": "Actualizar base de datos",
                "description": "Fuerza una actualización de la base de datos de contribuyentes",
                "security": [
                    {"BasicAuth": []}
                ],
                "responses": {
                    "200": {
                        "description": "Actualización completada",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "mensaje": {"type": "string"},
                                "tiempo_ejecucion": {"type": "string"},
                                "registros_procesados": {"type": "integer"},
                                "registros_nuevos": {"type": "integer"},
                                "registros_actualizados": {"type": "integer"},
                                "fecha_actualizacion": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "401": {
                        "description": "No autorizado",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            }
                        }
                    },
                    "403": {
                        "description": "Prohibido",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            }
                        }
                    },
                    "500": {
                        "description": "Error del servidor",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "mensaje": {"type": "string"},
                                "fecha": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            }
        },
        "/admin/estadisticas-sistema": {
            "get": {
                "tags": ["Administración"],
                "summary": "Estadísticas del sistema",
                "description": "Obtiene estadísticas detalladas sobre el sistema y la base de datos",
                "security": [
                    {"BearerAuth": []}
                ],
                "responses": {
                    "200": {
                        "description": "Estadísticas del sistema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "version_api": {"type": "string"},
                                "uptime": {"type": "number"},
                                "ultima_actualizacion": {
                                    "type": "object",
                                    "properties": {
                                        "fecha": {"type": "string", "format": "date-time"},
                                        "registros_procesados": {"type": "integer"},
                                        "registros_nuevos": {"type": "integer"},
                                        "registros_actualizados": {"type": "integer"}
                                    }
                                },
                                "configuracion": {
                                    "type": "object",
                                    "properties": {
                                        "db_type": {"type": "string"},
                                        "update_hour": {"type": "string"},
                                        "update_minute": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "No autorizado",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            }
                        }
                    },
                    "500": {
                        "description": "Error del servidor",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "mensaje": {"type": "string"},
                                "fecha": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            }
        },
        "/admin/limpiar-cache": {
            "post": {
                "tags": ["Administración"],
                "summary": "Limpiar caché",
                "description": "Limpia el caché de la aplicación",
                "security": [
                    {"BasicAuth": []}
                ],
                "responses": {
                    "200": {
                        "description": "Caché limpiado",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "mensaje": {"type": "string"},
                                "fecha": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "401": {
                        "description": "No autorizado",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            }
                        }
                    },
                    "403": {
                        "description": "Prohibido",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"}
                            }
                        }
                    },
                    "500": {
                        "description": "Error del servidor",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "estado": {"type": "string"},
                                "mensaje": {"type": "string"},
                                "fecha": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Añadir paths de administración al documento Swagger
    swagger_doc["paths"].update(admin_paths)
    
    return json.dumps(swagger_doc)
