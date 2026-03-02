import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for

# 1. IMPORTACIONES DE CONFIGURACIÓN Y MODELOS
from inventario.bd import db, configurar_db
from inventario.productos import Medicina, Cita  # Asegúrate de haber agregado Cita en productos.py

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS UNIFICADA ---
# Usamos la configuración modular que apunta a inventario/bd.db [cite: 7, 10]
configurar_db(app) 

# Inicializar SQLAlchemy con la aplicación [cite: 12]
db.init_app(app)

# Crear todas las tablas (Medicina y Cita) al iniciar [cite: 375]
with app.app_context():
    db.create_all()

# --- RUTAS DE NAVEGACIÓN GENERAL ---

@app.route('/')
def home():
    return render_template('index.html') [cite: 379]

# --- SECCIÓN DE GESTIÓN DE CITAS (SQLAlchemy) ---

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        # Captura de datos del formulario agendar.html [cite: 383, 384, 385]
        paciente = request.form.get('paciente')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        
        if paciente and fecha:
            # Guardado directo en SQLite usando el modelo Cita
            nueva_cita = Cita(paciente=paciente, fecha=fecha, hora=hora)
            db.session.add(nueva_cita)
            db.session.commit()
            return redirect(url_for('ver_todas_las_citas')) [cite: 388]
            
    return render_template('agendar.html') [cite: 389]

@app.route('/citas')
def ver_todas_las_citas():
    # Consulta de todas las citas en la base de datos [cite: 479]
    citas = Cita.query.all()
    return render_template('lista_citas.html', citas=citas) [cite: 393]

@app.route('/cambiar_cita', methods=['POST'])
def cambiar_cita():
    id_cita = request.form.get('id_cita')
    nueva_fecha = request.form.get('nueva_fecha')
    
    cita = Cita.query.get(id_cita)
    if cita:
        cita.fecha = nueva_fecha
        db.session.commit() [cite: 482]
    return redirect(url_for('ver_todas_las_citas'))

# --- SECCIÓN DE INVENTARIO (PERSISTENCIA MULTIFORMATO) ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre') [cite: 399]
            precio = float(request.form.get('precio', 0)) [cite: 400]
            cantidad = int(request.form.get('cantidad', 0)) [cite: 401]

            # 1. Guardar en SQLite (Base de datos principal) [cite: 402]
            nueva_medicina = Medicina(nombre=nombre, precio=precio, cantidad=cantidad)
            db.session.add(nueva_medicina)
            db.session.commit() [cite: 405]

            # 2. Guardar en TXT, JSON y CSV (Sincronización de archivos)
            # Importamos la función desde tu módulo de inventario [cite: 357]
            from inventario.inventario import guardar_formatos_planos
            guardar_formatos_planos(nombre, precio, cantidad) [cite: 407]

            return redirect(url_for('ver_datos')) [cite: 408]
        except Exception as e:
            print(f"Error al guardar: {e}") [cite: 410]
            return f"Error al procesar el formulario: {e}", 500
            
    return render_template('producto_form.html') [cite: 412]

@app.route('/datos')
def ver_datos():
    try:
        # 1. Leer de SQL (Medicinas) [cite: 417]
        medicinas_sql = Medicina.query.all()

        # 2. Leer de JSON para la vista comparativa [cite: 420]
        datos_json = []
        basedir = os.path.abspath(os.path.dirname(__file__))
        ruta_json = os.path.join(basedir, 'data', 'datos.json') [cite: 19]
        
        if os.path.exists(ruta_json) and os.path.getsize(ruta_json) > 0:
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos_json = json.load(f) [cite: 423]

        # 3. Leer de CSV [cite: 426]
        datos_csv = []
        ruta_csv = os.path.join(basedir, 'data', 'datos.csv')
        if os.path.exists(ruta_csv):
            with open(ruta_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                datos_csv = list(reader) [cite: 430]

        return render_template('datos.html', 
                               medicinas=medicinas_sql, 
                               datos_json=datos_json, 
                               datos_csv=datos_csv) [cite: 434]
    except Exception as e:
        return f"Error al cargar la tabla de datos: {e}", 500 [cite: 437]

# --- SECCIÓN DE FACTURACIÓN ---

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0)) [cite: 233]
        total = round(subtotal * 1.15, 2) # Cálculo de IVA 15% [cite: 495]
    return render_template('factura.html', total=total) [cite: 247]

if __name__ == '__main__':
    app.run(debug=True) [cite: 439]