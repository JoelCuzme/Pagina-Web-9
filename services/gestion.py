import os
from Conexion.conexion import obtener_conexion
from fpdf import FPDF
from flask import make_response

class GestionMedica:
    def __init__(self):
        # La conexión se gestiona por cada llamada para evitar hilos caídos
        pass

    def ejecutar_query(self, sql, params=None, es_consulta=False):
        """Ejecuta comandos SQL en MariaDB/MySQL de forma segura."""
        db_mysql = obtener_conexion()
        resultado = None
        if db_mysql:
            try:
                cursor = db_mysql.cursor(dictionary=True)
                cursor.execute(sql, params or ())
                if es_consulta:
                    resultado = cursor.fetchall()
                else:
                    db_mysql.commit()
                cursor.close()
            except Exception as e:
                print(f"Error en la base de datos: {e}")
            finally:
                db_mysql.close()
        return resultado

    # ==========================================
    #       CRUD DE SERVICIOS (INVENTARIO)
    # ==========================================
    def obtener_servicios(self):
        return self.ejecutar_query("SELECT * FROM hospital.servicios", es_consulta=True) or []

    def insertar_servicio(self, nombre, precio, stock):
        sql = "INSERT INTO hospital.servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)"
        return self.ejecutar_query(sql, (nombre, precio, stock))

    def eliminar_servicio(self, id_servicio):
        sql = "DELETE FROM hospital.servicios WHERE id_servicio = %s"
        return self.ejecutar_query(sql, (id_servicio,))

    # ==========================================
    #       CRUD DE CITAS MÉDICAS
    # ==========================================
    def obtener_citas(self):
        return self.ejecutar_query("SELECT * FROM hospital.citas", es_consulta=True) or []

    def agendar_cita(self, paciente, fecha, hora):
        sql = "INSERT INTO hospital.citas (paciente, fecha, hora) VALUES (%s, %s, %s)"
        return self.ejecutar_query(sql, (paciente, fecha, hora))

    def actualizar_fecha_cita(self, id_cita, nueva_fecha):
        sql = "UPDATE hospital.citas SET fecha = %s WHERE id = %s"
        return self.ejecutar_query(sql, (nueva_fecha, id_cita))

    # ==========================================
    #       GENERACIÓN DE REPORTE PDF
    # ==========================================
    def generar_reporte_pdf(self):
        servicios = self.obtener_servicios()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "REPORTE DE INVENTARIO - HOSPITAL", ln=True, align='C')
        pdf.ln(10)

        # Encabezados de tabla
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(80, 10, "Nombre del Servicio", 1)
        pdf.cell(40, 10, "Precio", 1)
        pdf.cell(40, 10, "Stock", 1, ln=True)

        # Contenido
        pdf.set_font("Arial", '', 12)
        for s in servicios:
            pdf.cell(80, 10, str(s['nombre']), 1)
            pdf.cell(40, 10, f"${s['precio']}", 1)
            pdf.cell(40, 10, str(s['stock_disponible']), 1, ln=True)

        # Retornar el PDF como una respuesta de Flask
        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers.set('Content-Disposition', 'attachment', filename='reporte_inventario.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response