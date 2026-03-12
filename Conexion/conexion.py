import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',       # Usuario por defecto de phpMyAdmin
            password='',       # Por defecto XAMPP no tiene contraseña
            database='gestion_medica' # El nombre que le diste en phpMyAdmin
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None