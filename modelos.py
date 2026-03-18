from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Inicializamos la base de datos (se vinculará en app.py)
db = SQLAlchemy()

# NUEVA CLASE: Usuario (Para el sistema de autenticación)
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    # Flask-Login requiere que el campo se llame 'id' o que uses get_id()
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# CLASE MODIFICADA: ServicioMedico (Ahora como tabla de SQLAlchemy)
class ServicioMedico(db.Model):
    __tablename__ = 'servicios_medicos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock_disponible = db.Column(db.Integer, default=100)

    def calcular_iva(self, tasa=0.15):
        return round(self.precio * (1 + tasa), 2)