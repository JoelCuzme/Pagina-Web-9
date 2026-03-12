import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',       # Asegúrate de que este sea tu usuario
            password='',       # Tu contraseña de MySQL
            database='gestion_medica' # Nombre de la BD que crearás
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None