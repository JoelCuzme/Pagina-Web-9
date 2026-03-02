from .bd import db

class Medicina(db.Model):
    __tablename__ = 'medicinas'
    id = db.Column(db.Integer, primary_key=True) [cite: 49]
    nombre = db.Column(db.String(100), nullable=False) [cite: 50]
    precio = db.Column(db.Float, nullable=False) [cite: 51]
    cantidad = db.Column(db.Integer, nullable=False) [cite: 52]

class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) [cite: 471]
    paciente = db.Column(db.String(100), nullable=False) [cite: 115, 116]
    fecha = db.Column(db.String(20), nullable=False) [cite: 121]
    hora = db.Column(db.String(20), nullable=False) [cite: 125]

class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True) [cite: 455]
    nombre = db.Column(db.String(100), nullable=False) [cite: 455]
    precio = db.Column(db.Float, nullable=False) [cite: 455]
    stock = db.Column(db.Integer, default=100) [cite: 455]