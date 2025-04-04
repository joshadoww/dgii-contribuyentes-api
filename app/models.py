"""
Modelos de la base de datos para la API de contribuyentes DGII.
"""
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Contribuyente(db.Model):
    """Modelo para almacenar la información de los contribuyentes."""
    __tablename__ = 'contribuyentes'
    
    id = db.Column(db.Integer, primary_key=True)
    rnc = db.Column(db.String(11), unique=True, index=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    nombre_comercial = db.Column(db.String(255), nullable=True)
    categoria = db.Column(db.String(50), nullable=True)
    regimen_pagos = db.Column(db.String(50), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    actividad_economica = db.Column(db.String(255), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Contribuyente {self.rnc}: {self.nombre}>"
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para la respuesta JSON."""
        return {
            'id': self.id,
            'rnc': self.rnc,
            'nombre': self.nombre,
            'nombre_comercial': self.nombre_comercial,
            'categoria': self.categoria,
            'regimen_pagos': self.regimen_pagos,
            'estado': self.estado,
            'actividad_economica': self.actividad_economica,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

class ActualizacionDB(db.Model):
    """Modelo para almacenar información sobre las actualizaciones de la base de datos."""
    __tablename__ = 'actualizaciones_db'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    registros_procesados = db.Column(db.Integer, default=0)
    registros_nuevos = db.Column(db.Integer, default=0)
    registros_actualizados = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(50), default='completado')
    mensaje = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<ActualizacionDB {self.fecha}>'

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    rol = db.Column(db.String(20), default='usuario')  # 'admin' o 'usuario'
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    ultima_actividad = db.Column(db.DateTime, default=datetime.now)
    tokens = db.relationship('Token', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.rol == 'admin'
    
    def generate_token(self, expires_in=3600*24*30):  # 30 días por defecto
        return Token.generate_token(self.id, expires_in)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_expiracion = db.Column(db.DateTime)
    ultimo_uso = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Token {self.token[:8]}...>'
    
    @staticmethod
    def generate_token(usuario_id, expires_in=3600*24*30):
        token_value = str(uuid.uuid4())
        expiracion = datetime.now().timestamp() + expires_in
        token = Token(
            token=token_value,
            usuario_id=usuario_id,
            fecha_expiracion=datetime.fromtimestamp(expiracion)
        )
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def check_token(token_value):
        token = Token.query.filter_by(token=token_value).first()
        if token is None:
            return None
        
        # Verificar si el token ha expirado
        if token.fecha_expiracion < datetime.now():
            db.session.delete(token)
            db.session.commit()
            return None
        
        # Actualizar último uso
        token.ultimo_uso = datetime.now()
        db.session.commit()
        
        return token.usuario
