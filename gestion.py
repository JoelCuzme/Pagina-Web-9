import sqlite3
from modelos import ServicioMedico
class GestionMedica:
    def __init__(self):
        self.db_name = "salud_total.db"
        self._inicializar_db()
        # COLECCIÓN: Diccionario para búsqueda rápida por ID
        self.servicios = {} 
        self.cargar_desde_db()

    def _inicializar_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS servicios 
                         (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL, stock INTEGER)""")

    def cargar_desde_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute("SELECT * FROM servicios")
            for row in cursor:
                s = ServicioMedico(row[0], row[1], row[2], row[3])
                self.servicios[s.id] = s

    def agregar_servicio(self, id_s, nombre, precio):
        nuevo = ServicioMedico(id_s, nombre, precio)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("INSERT INTO servicios VALUES (?,?,?,?)", 
                         (nuevo.id, nuevo.nombre, nuevo.precio, nuevo.stock_disponible))
        self.servicios[nuevo.id] = nuevo # Sincronizar con la colección