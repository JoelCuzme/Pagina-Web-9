class ServicioMedico:
    def __init__(self, id_servicio=None, nombre="", precio=0.0, stock_disponible=100):
        self.__id = id_servicio  
        self.nombre = nombre
        self.precio = float(precio)
        self.stock_disponible = stock_disponible

    @property
    def id(self):
        return self.__id

    def calcular_iva(self, tasa=0.15):
        return round(self.precio * (1 + tasa), 2)