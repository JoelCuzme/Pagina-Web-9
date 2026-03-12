from .bd import db

class Medicina(db.Model):
    __tablename__ = 'servicios' # Ajustado a la tabla que creaste en Aiven
    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock_disponible = db.Column(db.Integer, default=0)