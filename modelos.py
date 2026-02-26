class ServicioMedico:
    def __init__(self, id_servicio, nombre, precio, stock_disponible=100):
        self.__id = id_servicio  # Encapsulamiento
        self.nombre = nombre
        self.precio = float(precio)
        self.stock_disponible = stock_disponible # Cantidad de citas/insumos

    @property
    def id(self):
        return self.__id

    def calcular_iva(self, tasa=0.15):
        """Lógica de negocio: Calcular el total con impuestos"""
        return round(self.precio * (1 + tasa), 2)