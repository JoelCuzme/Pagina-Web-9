# gestion.py
from modelos import ServicioMedico

class GestionMedica:
    def __init__(self):
        # Ya no necesitamos self.db_name porque usamos MariaDB en la nube
        self.servicios = {}
        # Cargamos los servicios desde MariaDB al iniciar
        self.cargar_desde_db()

    def cargar_desde_db(self):
        # Importamos aquí para evitar importación circular con app.py
        from app import ejecutar_query
        
        rows = ejecutar_query("SELECT id, nombre, precio, stock_disponible FROM servicios", es_consulta=True)
        if rows:
            for row in rows:
                # row ahora es un diccionario gracias a dictionary=True en tu ejecutar_query
                s = ServicioMedico(
                    id=row['id'], 
                    nombre=row['nombre'], 
                    precio=row['precio'], 
                    stock_disponible=row['stock_disponible']
                )
                self.servicios[s.id] = s

    def agendar_cita(self, paciente, fecha, hora):
        from app import ejecutar_query
        sql = "INSERT INTO citas (paciente, fecha, hora) VALUES (%s, %s, %s)"
        ejecutar_query(sql, (paciente, fecha, hora))
        # Para obtener el ID insertado en MariaDB
        res = ejecutar_query("SELECT LAST_INSERT_ID() as id", es_consulta=True)
        return res[0]['id'] if res else None

    def obtener_citas(self):
        from app import ejecutar_query
        # Retornamos las citas como una lista de diccionarios
        return ejecutar_query("SELECT * FROM citas", es_consulta=True) or []

    def actualizar_cita(self, id_cita, nueva_fecha):
        from app import ejecutar_query
        sql = "UPDATE citas SET fecha = %s WHERE id = %s"
        ejecutar_query(sql, (nueva_fecha, id_cita))