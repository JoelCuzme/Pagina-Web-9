import mysql.connector
from mysql.connector import Error
import os

def obtener_conexion():
    # Buscamos el certificado ca.pem en la carpeta raíz del proyecto
    # Este archivo DEBE estar subido a tu repositorio de GitHub
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(base_dir, '..', 'ca.pem')

    try:
        conexion = mysql.connector.connect(
            host=os.getenv('MYSQLHOST', 'mysql-3a27fee2-urssn90-b49f.f.aivencloud.com'),
            user=os.getenv('MYSQLUSER', 'avnadmin'),
            # Recomendación: Configura MYSQLPASSWORD en la pestaña Environment de Render
            password=os.getenv('MYSQLPASSWORD', 'TU_CONTRASEÑA_AQUÍ'), 
            database='hospital', # Confirmado que se llama así
            port=int(os.getenv('MYSQLPORT', 16398)),
            ssl_ca=cert_path,
            ssl_verify_cert=True # Obligatorio para MariaDB en Aiven
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error crítico al conectar a MariaDB: {e}")
        return None