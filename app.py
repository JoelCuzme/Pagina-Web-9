import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for

# 1. IMPORTACIONES MODULARES (Semana 12)
from inventario.bd import db, init_db
from inventario.productos import Medicina
from inventario.inventario import guardar_en_archivos

# Importaciones de tus clases de lógica previa
from gestion import GestionMedica
from modelos import ServicioMedico

app = Flask(__name__)
sistema = GestionMedica()

# --- CONFIGURACIÓN DE RUTAS Y PERSISTENCIA ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Carpeta del paquete inventario
INVENTARIO_DIR = os.path.join(basedir, 'inventario')
# Carpeta física para los archivos planos (TXT, JSON, CSV)
DATA_PATH = os.path.join(INVENTARIO_DIR, 'data')

# Asegurar que la estructura de carpetas exista para evitar errores en Render
os.makedirs(DATA_PATH, exist_ok=True)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(INVENTARIO_DIR, 'bd.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy y crear tablas automáticamente
init_db(app)
with app.app_context():
    db.create_all()

# --- FUNCIONES DE UTILIDAD ---
def normalizar_nombre(texto):
    return texto.replace("_", " ")

# --- RUTAS DE NAVEGACIÓN Y CITAS ---

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

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        servicio_temp = ServicioMedico(0, "Consulta", subtotal)
        total = servicio_temp.calcular_iva() 
    return render_template('factura.html', total=total)

# --- RUTAS DE INVENTARIO Y PERSISTENCIA AUTOMÁTICA ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            precio = float(request.form.get('precio', 0))
            cantidad = int(request.form.get('cantidad', 0))

            # A. Persistencia en SQLite (SQLAlchemy)
            nueva_medicina = Medicina(nombre=nombre, precio=precio, cantidad=cantidad)
            db.session.add(nueva_medicina)
            db.session.commit()

            # B. Persistencia en Formatos Planos (Modularizada en inventario.py)
            # Se guardan automáticamente en datos.txt, datos.json y datos.csv
            guardar_en_archivos(nombre, precio, cantidad, DATA_PATH)

            return redirect(url_for('ver_datos'))
        
        except Exception as e:
            print(f"Error en persistencia: {e}")
            return f"Error interno: {e}", 500
    
    return render_template('producto_form.html')

@app.route('/datos')
def ver_datos():
    # 1. Lectura desde SQLite
    medicinas_sql = Medicina.query.all()

    # 2. Lectura desde JSON para la vista
    ruta_json = os.path.join(DATA_PATH, "datos.json")
    datos_json = []
    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos_json = json.load(f)

    # 3. Lectura desde CSV para la vista
    ruta_csv = os.path.join(DATA_PATH, "datos.csv")
    datos_csv = []
    if os.path.exists(ruta_csv):
        with open(ruta_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            datos_csv = list(reader)

    return render_template('datos.html', 
                           medicinas=medicinas_sql, 
                           datos_json=datos_json, 
                           datos_csv=datos_csv)

if __name__ == '__main__':
    app.run(debug=True)