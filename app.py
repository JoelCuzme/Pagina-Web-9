import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# 1. IMPORTACIONES MODULARES (Manteniendo tus nombres)
from inventario.inventario import guardar_formatos_planos
from services.gestion import GestionMedica
from models.modelos import Usuario
# Ya no importamos 'db' de SQLAlchemy aquí para evitar conflictos con tu conexión manual

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura_123'

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"

# 2. INICIALIZACIÓN DEL SERVICIO (El cerebro del sistema)
sistema_medico = GestionMedica()

@login_manager.user_loader
def load_user(user_id):
    # Usamos el servicio para buscar al usuario
    res = sistema_medico.ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM hospital.usuarios WHERE id_usuario = %s", (user_id,), es_consulta=True)
    if res:
        u = res[0]
        return Usuario(id=u['id'], nombre=u['nombre'], email=u['email'], password=u['password'])
    return None

# ==========================================
#         RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        user_data = sistema_medico.ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM hospital.usuarios WHERE mail = %s", (mail,), es_consulta=True)        
        if user_data and user_data[0]['password'] == password:
            user_obj = Usuario(id=user_data[0]['id'], nombre=user_data[0]['nombre'], email=user_data[0]['email'], password=user_data[0]['password'])
            login_user(user_obj)
            flash(f'Bienvenido de nuevo, {user_obj.nombre}', 'success')
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
        existe = sistema_medico.ejecutar_query("SELECT * FROM hospital.usuarios WHERE mail = %s", (mail,), es_consulta=True)
        if existe:
            flash('El correo ya está registrado.', 'warning')
            return redirect(url_for('registrar_usuario'))
        sistema_medico.ejecutar_query("INSERT INTO hospital.usuarios (nombre, mail, password) VALUES (%s, %s, %s)", (nombre, mail, password))
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('usuario_form.html')

@app.route('/usuarios')
@login_required
def listar_usuarios():
    usuarios_db = sistema_medico.ejecutar_query("SELECT id_usuario, nombre, mail FROM hospital.usuarios", es_consulta=True)
    return render_template('usuarios_lista.html', usuarios=usuarios_db or [])

# ==========================================
#         RUTAS DE CITAS MÉDICAS
# ==========================================

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
            sistema_medico.agendar_cita(paciente, fecha, hora)
            flash('Cita agendada con éxito.', 'success')
            return redirect(url_for('ver_todas_las_citas')) 
    return render_template('agendar.html')

@app.route('/citas')
@login_required
def ver_todas_las_citas():
    citas = sistema_medico.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

@app.route('/cambiar_cita', methods=['POST'])
@login_required
def cambiar_cita():
    id_cita = request.form.get('id_cita')
    nueva_fecha = request.form.get('nueva_fecha')
    if id_cita and nueva_fecha:
        sistema_medico.actualizar_fecha_cita(id_cita, nueva_fecha)
        flash("¡Fecha actualizada correctamente!", "success")
    return redirect(url_for('ver_todas_las_citas'))

# ==========================================
#         INVENTARIO Y REPORTES
# ==========================================

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        try:
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('cantidad', 0))
            sistema_medico.insertar_servicio(nombre, precio, stock)
            guardar_formatos_planos(nombre, precio, stock)
            flash('Producto agregado al inventario.', 'success')
            return redirect(url_for('ver_datos'))
        except ValueError:
            flash('Error en los datos numéricos.', 'danger')
    return render_template('producto_form.html')

@app.route('/datos')
@login_required
def ver_datos():
    servicios_mysql = sistema_medico.obtener_servicios()
    return render_template('datos.html', servicios=servicios_mysql)

@app.route('/inventario/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    sistema_medico.eliminar_servicio(id)
    flash('Producto eliminado correctamente.', 'warning')
    return redirect(url_for('ver_datos'))

# NUEVA RUTA: Generar Reporte PDF
@app.route('/reporte/pdf')
@login_required
def descargar_reporte():
    return sistema_medico.generar_reporte_pdf()

@app.route('/factura', methods=['GET', 'POST'])
@login_required
def factura():
    total = None
    if request.method == 'POST':
        try:
            subtotal = float(request.form.get('subtotal', 0))
            iva = subtotal * 0.15
            total = "{:.2f}".format(subtotal + iva)
        except ValueError:
            flash("Ingresa un número válido.", "danger")
    return render_template('factura.html', total=total)

if __name__ == '__main__':
    # Render asigna un puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    # Importante: usar 0.0.0.0 para que sea accesible externamente
    app.run(host='0.0.0.0', port=port)