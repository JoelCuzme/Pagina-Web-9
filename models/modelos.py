from flask_login import UserMixin

# ==========================================
#       MODELO: USUARIO (Para Auth)
# ==========================================
class Usuario(UserMixin):
    """
    Representa a un usuario del sistema hospitalario.
    Implementa UserMixin para integrarse con Flask-Login.
    """
    def __init__(self, id, nombre, email, password):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password

# ==========================================
#       MODELO: SERVICIO MÉDICO
# ==========================================
class ServicioMedico:
    """
    Representa un servicio o producto del inventario.
    """
    def __init__(self, id_servicio, nombre, precio, stock_disponible):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.precio = precio
        self.stock_disponible = stock_disponible

    def calcular_iva(self, tasa=0.15):
        """Calcula el precio final con IVA incluido."""
        return round(self.precio * (1 + tasa), 2)

# ==========================================
#       MODELO: CITA MÉDICA
# ==========================================
class CitaMedica:
    """
    Representa una cita agendada en el sistema.
    """
    def __init__(self, id_cita, paciente, fecha, hora):
        self.id_cita = id_cita
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora