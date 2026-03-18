import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for, flash # Añadido flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user # NUEVO

# 1. IMPORTACIONES MODULARES
from inventario.inventario import guardar_formatos_planos
from gestion import GestionMedica
from modelos import ServicioMedico, Usuario, db # Añadido Usuario y db
from Conexion.conexion import obtener_conexion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura_123' # NUEVO: Necesario para sesiones

# --- CONFIGURACIÓN DE FLASK-LOGIN --- # NUEVO
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirige aquí si no hay sesión iniciada

@login_manager.user_loader
def load_user(user_id):
    # Buscamos al usuario en MySQL usando tu función de apoyo
    res = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM usuarios WHERE id_usuario = %s", (user_id,), es_consulta=True)
    if res:
        u = res[0]
        # Creamos un objeto Usuario compatible con Flask-Login
        return Usuario(id=u['id'], nombre=u['nombre'], email=u['email'], password=u['password'])
    return None

# --- CONFIGURACIÓN DE RUTAS DE DATOS ---
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, 'inventario', 'data')
os.makedirs(data_path, exist_ok=True)

# 2. INICIALIZACIÓN DE COMPONENTES
sistema_citas = GestionMedica()

# --- FUNCIONES DE APOYO ---
def ejecutar_query(sql, params=None, es_consulta=False):
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

# --- RUTAS DE AUTENTICACIÓN (NUEVO) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        user_data = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM usuarios WHERE mail = %s", (mail,), es_consulta=True)
        
        if user_data and user_data[0]['password'] == password: # Nota: En producción usar bcrypt
            user_obj = Usuario(id=user_data[0]['id'], nombre=user_data[0]['nombre'], email=user_data[0]['email'], password=user_data[0]['password'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            
    return render_template('login.html') # Asegúrate de crear este archivo

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS DE NAVEGACIÓN GENERAL ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/agendar', methods=['GET', 'POST'])
@login_required # PROTEGIDO
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
@login_required # PROTEGIDO
def ver_todas_las_citas():
    citas = sistema_citas.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

# --- RUTAS DE INVENTARIO ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required # PROTEGIDO
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = float(request.form.get('precio', 0))
        stock = int(request.form.get('cantidad', 0))

        ejecutar_query("INSERT INTO servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)", (nombre, precio, stock))
        guardar_formatos_planos(nombre, precio, stock)
        
        return redirect(url_for('ver_datos'))
    return render_template('producto_form.html')

@app.route('/datos')
@login_required # PROTEGIDO
def ver_datos():
    servicios_mysql = ejecutar_query("SELECT * FROM servicios", es_consulta=True) or []
    # (Tu lógica de carga de JSON/CSV se mantiene igual...)
    return render_template('datos.html', servicios=servicios_mysql)

# --- RUTAS DE USUARIOS ---

@app.route('/usuarios')
@login_required # Solo un admin (o alguien logueado) debería ver la lista
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
        return redirect(url_for('login')) # Redirigir al login tras registrarse
    return render_template('usuario_form.html')

# (Resto de tus rutas de servicios y factura se mantienen igual...)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)