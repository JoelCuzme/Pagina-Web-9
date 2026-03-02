import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Importaciones de tus archivos existentes
from gestion import GestionMedica
from modelos import ServicioMedico

app = Flask(__name__)
sistema = GestionMedica()

# --- CONFIGURACIÓN DE PERSISTENCIA (Semana 12) ---

# 1. Configuración de SQLAlchemy (SQLite) para Inventario
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventario/bd.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. Rutas para archivos locales
DATA_PATH = os.path.join(basedir, 'inventario/data/')

# Asegurar que las carpetas existan
os.makedirs(DATA_PATH, exist_ok=True)

# --- MODELO DE DATOS (SQLAlchemy) ---
class Medicina(db.Model):
    __tablename__ = 'medicinas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

# Crear la base de datos de SQLAlchemy
with app.app_context():
    db.create_all()

# --- FUNCIONES DE UTILIDAD ---
def normalizar_nombre(texto):
    return texto.replace("_", " ")

# --- RUTAS EXISTENTES (CITAS Y FACTURACIÓN) ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cita/<paciente>')
def ver_cita(paciente):
    nombre = normalizar_nombre(paciente)
    return render_template('about.html', nombre=nombre)

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        servicio_temp = ServicioMedico(0, "Consulta", subtotal)
        total = servicio_temp.calcular_iva() 
    return render_template('factura.html', total=total)

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        paciente = request.form.get('paciente')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        if not paciente or not fecha:
            return "Error: Faltan datos", 400
        sistema.agendar_cita(paciente, fecha, hora)
        return redirect('/citas') 
    return render_template('agendar.html')

@app.route('/citas')
def ver_todas_las_citas():
    citas = sistema.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

@app.route('/cambiar_cita', methods=['POST'])
def cambiar_cita():
    id_cita = request.form.get('id_cita')
    nueva_fecha = request.form.get('nueva_fecha')
    sistema.actualizar_cita(id_cita, nueva_fecha)
    return redirect('/citas')

# --- NUEVAS RUTAS: INVENTARIO Y PERSISTENCIA (Semana 12) ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        metodo = request.form.get('metodo') # SQL, JSON, CSV, TXT

        # Persistencia según el método seleccionado
        if metodo == 'SQL':
            nueva = Medicina(nombre=nombre, precio=float(precio), cantidad=int(cantidad))
            db.session.add(nueva)
            db.session.commit()

        elif metodo == 'TXT':
            with open(os.path.join(DATA_PATH, "datos.txt"), "a") as f:
                f.write(f"Producto: {nombre} | Precio: {precio} | Cantidad: {cantidad}\n")

        elif metodo == 'JSON':
            ruta_json = os.path.join(DATA_PATH, "datos.json")
            datos = []
            if os.path.exists(ruta_json):
                with open(ruta_json, "r") as f:
                    datos = json.load(f)
            datos.append({"nombre": nombre, "precio": precio, "cantidad": cantidad})
            with open(ruta_json, "w") as f:
                json.dump(datos, f, indent=4)

        elif metodo == 'CSV':
            ruta_csv = os.path.join(DATA_PATH, "datos.csv")
            existe = os.path.isfile(ruta_csv)
            with open(ruta_csv, "a", newline="") as f:
                writer = csv.writer(f)
                if not existe:
                    writer.writerow(["Nombre", "Precio", "Cantidad"])
                writer.writerow([nombre, precio, cantidad])

        return redirect(url_for('ver_datos'))
    
    return render_template('producto_form.html')

@app.route('/datos')
def ver_datos():
    # 1. Leer de SQL
    medicinas_sql = Medicina.query.all()

    # 2. Leer de TXT
    datos_txt = []
    if os.path.exists(os.path.join(DATA_PATH, "datos.txt")):
        with open(os.path.join(DATA_PATH, "datos.txt"), "r") as f:
            datos_txt = f.readlines()

    # 3. Leer de JSON
    datos_json = []
    if os.path.exists(os.path.join(DATA_PATH, "datos.json")):
        with open(os.path.join(DATA_PATH, "datos.json"), "r") as f:
            datos_json = json.load(f)

    # 4. Leer de CSV
    datos_csv = []
    if os.path.exists(os.path.join(DATA_PATH, "datos.csv")):
        with open(os.path.join(DATA_PATH, "datos.csv"), "r") as f:
            reader = csv.DictReader(f)
            datos_csv = list(reader)

    return render_template('datos.html', 
                           medicinas=medicinas_sql, 
                           datos_txt=datos_txt, 
                           datos_json=datos_json, 
                           datos_csv=datos_csv)

if __name__ == '__main__':
    app.run(debug=True)