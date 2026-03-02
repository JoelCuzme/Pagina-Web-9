import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for

# 1. IMPORTACIONES MODULARES
# Importamos Medicina para que las consultas SQL funcionen
from inventario.bd import db, configurar_db
from inventario.productos import Medicina
from inventario.inventario import guardar_formatos_planos

# Importaciones de tu lógica previa
from gestion import GestionMedica
from modelos import ServicioMedico

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS Y PERSISTENCIA ---
basedir = os.path.abspath(os.path.dirname(__file__))
INVENTARIO_DIR = os.path.join(basedir, 'inventario')
DATA_PATH = os.path.join(INVENTARIO_DIR, 'data')

# Asegurar directorios (Crucial para Render)
os.makedirs(DATA_PATH, exist_ok=True)

# Inicializar sistema de gestión de citas
sistema = GestionMedica()

# Inicializar y configurar base de datos SQLAlchemy
configurar_db(app)

# Crear tablas si no existen (SQLite)
with app.app_context():
    db.create_all()

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        paciente = request.form.get('paciente')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        if paciente and fecha:
            sistema.agendar_cita(paciente, fecha, hora)
            return redirect(url_for('ver_todas_las_citas')) 
    return render_template('agendar.html')

@app.route('/citas')
def ver_todas_las_citas():
    citas = sistema.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

# --- RUTAS DE INVENTARIO (PERSISTENCIA MULTIFORMATO) ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            precio = float(request.form.get('precio', 0))
            cantidad = int(request.form.get('cantidad', 0))

            # 1. Guardar en SQLite (SQLAlchemy)
            nueva = Medicina(nombre=nombre, precio=precio, cantidad=cantidad)
            db.session.add(nueva)
            db.session.commit()

            # 2. Guardar en TXT, JSON y CSV (Función modular corregida)
            # Pasamos DATA_PATH si tu función lo requiere, 
            # de lo contrario ella usa su propio BASE_DIR
            guardar_formatos_planos(nombre, precio, cantidad)

            return redirect(url_for('ver_datos'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar: {e}")
            return f"Error al procesar el formulario: {e}", 500
    return render_template('producto_form.html')

@app.route('/datos')
def ver_datos():
    try:
        # 1. Leer de SQL
        medicinas_sql = Medicina.query.all()

        # 2. Leer de JSON
        datos_json = []
        ruta_json = os.path.join(DATA_PATH, "datos.json")
        if os.path.exists(ruta_json) and os.path.getsize(ruta_json) > 0:
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos_json = json.load(f)

        # 3. Leer de CSV
        datos_csv = []
        ruta_csv = os.path.join(DATA_PATH, "datos.csv")
        if os.path.exists(ruta_csv):
            with open(ruta_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                datos_csv = list(reader)

        return render_template('datos.html', 
                               medicinas=medicinas_sql, 
                               datos_json=datos_json, 
                               datos_csv=datos_csv)
    except Exception as e:
        print(f"Error en vista de datos: {e}")
        return f"Error al cargar la tabla de datos: {e}", 500

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        # Uso de la lógica del modelo
        servicio = ServicioMedico(0, "Consulta", subtotal)
        total = servicio.calcular_iva()
    return render_template('factura.html', total=total)

if __name__ == '__main__':
    app.run(debug=True)