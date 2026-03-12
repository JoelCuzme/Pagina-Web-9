import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for

# 1. IMPORTACIONES MODULARES
# Mantener estas importaciones asegura que el guardado de archivos planos funcione
from inventario.inventario import guardar_formatos_planos
from gestion import GestionMedica
from modelos import ServicioMedico
from Conexion.conexion import obtener_conexion

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS DE DATOS ---
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, 'inventario', 'data')
os.makedirs(data_path, exist_ok=True)

# 2. INICIALIZACIÓN DE COMPONENTES
sistema_citas = GestionMedica()

# --- FUNCIONES DE APOYO (HELPER FUNCTIONS) ---
def ejecutar_query(sql, params=None, es_consulta=False):
    """Función para reducir código repetitivo de MySQL"""
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
        finally:
            db_mysql.close()
    return resultado

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
            sistema_citas.agendar_cita(paciente, fecha, hora)
            return redirect(url_for('ver_todas_las_citas')) 
    return render_template('agendar.html')

@app.route('/citas')
def ver_todas_las_citas():
    citas = sistema_citas.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

# --- RUTAS DE INVENTARIO (UNIFICADO A MYSQL + ARCHIVOS) ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio', 0))
        stock = int(request.form.get('cantidad', 0))

        # 1. Guardar en MySQL (Aiven)
        sql = "INSERT INTO servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)"
        ejecutar_query(sql, (nombre, precio, stock))

        # 2. Guardar en Formatos Planos (Respaldo)
        guardar_formatos_planos(nombre, precio, stock)
        
        return redirect(url_for('ver_datos'))
    return render_template('producto_form.html')

@app.route('/datos')
def ver_datos():
    # Obtenemos datos de MySQL
    servicios_mysql = ejecutar_query("SELECT * FROM servicios", es_consulta=True) or []
    
    # Cargar datos de JSON
    datos_json = []
    rj = os.path.join(data_path, "datos.json")
    if os.path.exists(rj) and os.path.getsize(rj) > 0:
        with open(rj, "r", encoding="utf-8") as f:
            datos_json = json.load(f)

    # Cargar datos de CSV
    datos_csv = []
    rc = os.path.join(data_path, "datos.csv")
    if os.path.exists(rc):
        with open(rc, "r", encoding="utf-8") as f:
            datos_csv = list(csv.DictReader(f))

    return render_template('datos.html', servicios=servicios_mysql, datos_json=datos_json, datos_csv=datos_csv)

# --- RUTAS DE USUARIOS ---

@app.route('/usuarios')
def listar_usuarios():
    usuarios = ejecutar_query("SELECT id_usuario, nombre, mail FROM usuarios", es_consulta=True) or []
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/registrar', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        sql = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        ejecutar_query(sql, (nombre, mail, password))
        return redirect(url_for('listar_usuarios'))
    return render_template('usuario_form.html')

# --- OPERACIONES DE SERVICIOS (CRUD) ---

@app.route('/servicios/eliminar/<int:id>')
def eliminar_servicio(id):
    ejecutar_query("DELETE FROM servicios WHERE id_servicio = %s", (id,))
    return redirect(url_for('ver_datos'))

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        servicio = ServicioMedico(0, "Consulta", subtotal)
        total = servicio.calcular_iva()
    return render_template('factura.html', total=total)

# --- INICIO DE LA APP ---
if __name__ == '__main__':
    # Esto es vital: Render asigna el puerto mediante una variable de entorno
    port = int(os.environ.get("PORT", 5000))
    # Debes usar host='0.0.0.0' para que sea accesible externamente
    app.run(host='0.0.0.0', port=port)