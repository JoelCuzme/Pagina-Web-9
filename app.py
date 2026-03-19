import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# 1. IMPORTACIONES MODULARES
from inventario.inventario import guardar_formatos_planos
from gestion import GestionMedica
from modelos import ServicioMedico, Usuario, db
from Conexion.conexion import obtener_conexion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura_123'

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    # Usamos id_usuario como alias 'id' para que Flask-Login no se confunda
    res = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM usuarios WHERE id_usuario = %s", (user_id,), es_consulta=True)
    if res:
        u = res[0]
        return Usuario(id=u['id'], nombre=u['nombre'], email=u['email'], password=u['password'])
    return None

# --- FUNCIONES DE APOYO (CENTRALIZADAS) ---
def ejecutar_query(sql, params=None, es_consulta=False):
    """Ejecuta comandos SQL en la base de datos MariaDB de Aiven."""
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
            flash(f"Error de base de datos: {e}", "danger")
        finally:
            db_mysql.close()
    return resultado

# 2. INICIALIZACIÓN DE COMPONENTES
# Pasamos la función ejecutar_query si fuera necesario, o la importamos en gestion.py
sistema_citas = GestionMedica()

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        user_data = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM usuarios WHERE mail = %s", (mail,), es_consulta=True)        
        # Validación de usuario y contraseña (Texto plano según tu solicitud actual)
        if user_data and user_data[0]['password'] == password:
            user_obj = Usuario(
                id=user_data[0]['id'], 
                nombre=user_data[0]['nombre'], 
                email=user_data[0]['email'], 
                password=user_data[0]['password']
            )
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

@app.route('/usuarios/registrar', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        # Verificamos si el correo ya existe para evitar errores 500
        existe = ejecutar_query("SELECT * FROM usuarios WHERE mail = %s", (mail,), es_consulta=True)
        if existe:
            flash('El correo ya está registrado.', 'warning')
            return redirect(url_for('registrar_usuario'))

        sql = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        ejecutar_query(sql, (nombre, mail, password))
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return render_template('usuario_form.html')

# --- RUTAS DE NAVEGACIÓN GENERAL ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        paciente = request.form.get('paciente')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        if paciente and fecha:
            # Ahora sistema_citas usa MariaDB internamente
            sistema_citas.agendar_cita(paciente, fecha, hora)
            flash('Cita agendada con éxito.', 'success')
            return redirect(url_for('ver_todas_las_citas')) 
    return render_template('agendar.html')

@app.route('/citas')
@login_required
def ver_todas_las_citas():
    citas = sistema_citas.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

# --- RUTAS DE INVENTARIO ---

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        try:
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('cantidad', 0))
            
            # Guardamos en MariaDB (Aiven)
            ejecutar_query("INSERT INTO servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)", (nombre, precio, stock))
            
            # Mantenemos tu guardado en archivos planos si lo necesitas
            guardar_formatos_planos(nombre, precio, stock)
            
            flash('Producto agregado al inventario.', 'success')
            return redirect(url_for('ver_datos'))
        except ValueError:
            flash('Error en los datos numéricos introducidos.', 'danger')
            
    return render_template('producto_form.html')

@app.route('/datos')
@login_required
def ver_datos():
    servicios_mysql = ejecutar_query("SELECT * FROM servicios", es_consulta=True) or []
    return render_template('datos.html', servicios=servicios_mysql)

if __name__ == '__main__':
    # Usar puerto de variable de entorno para despliegues (Render/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)