import sqlite3
from modelos import ServicioMedico
class GestionMedica:
    def __init__(self):
        self.db_name = "salud_total.db"
        # Llamamos a ambos para asegurar que las tablas existan siempre
        self._inicializar_db()
        self.inicializar_citas_db() 
        
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

    def inicializar_citas_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS citas 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente TEXT, fecha TEXT, hora TEXT)""")

    def agendar_cita(self, paciente, fecha, hora):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.execute("INSERT INTO citas (paciente, fecha, hora) VALUES (?,?,?)", 
                             (paciente, fecha, hora))
            return cursor.lastrowid

    def obtener_citas(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT * FROM citas").fetchall()

    def actualizar_cita(self, id_cita, nueva_fecha):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE citas SET fecha = ? WHERE id = ?", (nueva_fecha, id_cita))