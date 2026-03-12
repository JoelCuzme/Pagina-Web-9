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
from Conexion.conexion import obtener_conexion

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, 'inventario', 'data')
os.makedirs(data_path, exist_ok=True)

# Configuración de SQLite
path_sqlite = os.path.join(basedir, 'inventario', 'bd.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path_sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. INICIALIZACIÓN DE COMPONENTES
configurar_db(app)
sistema = GestionMedica()

with app.app_context():
    db.create_all()

# --- RUTAS DE NAVEGACIÓN GENERAL ---

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

# --- RUTAS DE INVENTARIO (SQLITE Y FORMATOS PLANOS) ---

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
    try:
        medicinas_sql = Medicina.query.all()
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

# --- RUTAS MYSQL: SERVICIOS ---

@app.route('/servicios_mysql')
def listar_servicios():
    db_mysql = obtener_conexion()
    if db_mysql:
        cursor = db_mysql.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicios")
        servicios_data = cursor.fetchall()
        cursor.close()
        db_mysql.close()
        return render_template('datos.html', servicios=servicios_data)
    return "Error en la conexión a MySQL", 500

@app.route('/servicios_mysql/nuevo', methods=['POST'])
def nuevo_servicio_mysql():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    stock = request.form.get('stock', 100)

    db_mysql = obtener_conexion()
    if db_mysql:
        cursor = db_mysql.cursor()
        sql = "INSERT INTO servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, precio, stock))
        db_mysql.commit()
        cursor.close()
        db_mysql.close()
        return redirect(url_for('listar_servicios'))
    return "Error al guardar en MySQL", 500

@app.route('/servicios_mysql/eliminar/<int:id>')
def eliminar_servicio(id):
    db_mysql = obtener_conexion()
    if db_mysql:
        cursor = db_mysql.cursor()
        cursor.execute("DELETE FROM servicios WHERE id_servicio = %s", (id,))
        db_mysql.commit()
        cursor.close()
        db_mysql.close()
    return redirect(url_for('listar_servicios'))

@app.route('/servicios_mysql/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    db_mysql = obtener_conexion()
    if not db_mysql:
        return "Error de conexión", 500
        
    cursor = db_mysql.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        
        sql = "UPDATE servicios SET nombre=%s, precio=%s, stock_disponible=%s WHERE id_servicio=%s"
        cursor.execute(sql, (nombre, precio, stock, id))
        db_mysql.commit()
        cursor.close()
        db_mysql.close()
        return redirect(url_for('listar_servicios'))
    
    cursor.execute("SELECT * FROM servicios WHERE id_servicio = %s", (id,))
    servicio = cursor.fetchone()
    cursor.close()
    db_mysql.close()
    return render_template('producto_form.html', servicio=servicio)

# --- RUTAS MYSQL: USUARIOS ---

@app.route('/usuarios')
def listar_usuarios():
    db_mysql = obtener_conexion()
    usuarios_data = []
    if db_mysql:
        cursor = db_mysql.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, mail FROM usuarios")
        usuarios_data = cursor.fetchall()
        cursor.close()
        db_mysql.close()
    return render_template('usuarios.html', usuarios=usuarios_data)

@app.route('/usuarios/registrar', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        db_mysql = obtener_conexion()
        if db_mysql:
            cursor = db_mysql.cursor()
            sql = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, mail, password))
            db_mysql.commit()
            cursor.close()
            db_mysql.close()
            return redirect(url_for('listar_usuarios'))
    return render_template('usuario_form.html')

# --- INICIO DE LA APP ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)