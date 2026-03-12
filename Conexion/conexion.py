import mysql.connector
from mysql.connector import Error
import os

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv('MYSQLHOST', 'mysql-3a27fee2-urssn90-b49f.f.aivencloud.com'),
            user=os.getenv('MYSQLUSER', 'avnadmin'),
            password=os.getenv('MYSQLPASSWORD'), # Se deja vacío para usar la variable de Render
            database=os.getenv('MYSQLDATABASE', 'hospital'),
            port=int(os.getenv('MYSQLPORT', 16398))
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None