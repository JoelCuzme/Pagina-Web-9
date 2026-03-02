import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for

# 1. IMPORTACIONES MODULARES
from inventario.bd import db, configurar_db
from inventario.productos import Medicina
from inventario.inventario import guardar_formatos_planos
from gestion import GestionMedica
from modelos import ServicioMedico

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Aseguramos que la DB esté en una ruta absoluta clara
path_sqlite = os.path.join(basedir, 'inventario', 'bd.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path_sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. INICIALIZACIÓN DE COMPONENTES
configurar_db(app)
sistema = GestionMedica()

# Crear carpetas y tablas ANTES de que el servidor empiece a recibir tráfico
with app.app_context():
    os.makedirs(os.path.join(basedir, 'inventario', 'data'), exist_ok=True)
    db.create_all()

# --- RUTAS ---

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

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            precio = float(request.form.get('precio', 0))
            cantidad = int(request.form.get('cantidad', 0))

            nueva = Medicina(nombre=nombre, precio=precio, cantidad=cantidad)
            db.session.add(nueva)
            db.session.commit()

            guardar_formatos_planos(nombre, precio, cantidad)
            return redirect(url_for('ver_datos'))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}", 500
    return render_template('producto_form.html')

@app.route('/datos')
def ver_datos():
    # Simplificamos la lógica de lectura para evitar bloqueos de I/O
    try:
        medicinas_sql = Medicina.query.all()
        
        # Rutas de archivos planos
        data_path = os.path.join(basedir, 'inventario', 'data')
        
        datos_json = []
        rj = os.path.join(data_path, "datos.json")
        if os.path.exists(rj) and os.path.getsize(rj) > 0:
            with open(rj, "r", encoding="utf-8") as f:
                datos_json = json.load(f)

        datos_csv = []
        rc = os.path.join(data_path, "datos.csv")
        if os.path.exists(rc):
            with open(rc, "r", encoding="utf-8") as f:
                datos_csv = list(csv.DictReader(f))

        return render_template('datos.html', medicinas=medicinas_sql, datos_json=datos_json, datos_csv=datos_csv)
    except Exception as e:
        return f"Error al cargar datos: {e}", 500

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        servicio = ServicioMedico(0, "Consulta", subtotal)
        total = servicio.calcular_iva()
    return render_template('factura.html', total=total)

# IMPORTANTE PARA RENDER:
if __name__ == '__main__':
    # Usamos el puerto que Render nos asigne, o 5000 por defecto localmente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)