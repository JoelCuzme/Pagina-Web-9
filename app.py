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
    # Consulta apuntando a la base 'hospital'
    res = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM hospital.usuarios WHERE id_usuario = %s", (user_id,), es_consulta=True)
    if res:
        u = res[0]
        return Usuario(id=u['id'], nombre=u['nombre'], email=u['email'], password=u['password'])
    return None

# --- FUNCIONES DE APOYO (DB CENTRALIZADA) ---
def ejecutar_query(sql, params=None, es_consulta=False):
    """Ejecuta comandos SQL en MariaDB de forma segura."""
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
        finally:
            db_mysql.close()
    return resultado

# 2. INICIALIZACIÓN DE COMPONENTES
sistema_citas = GestionMedica()

# ==========================================
#        RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        # Ajustado para buscar en hospital.usuarios
        user_data = ejecutar_query("SELECT id_usuario as id, nombre, mail as email, password FROM hospital.usuarios WHERE mail = %s", (mail,), es_consulta=True)        
        
        if user_data and user_data[0]['password'] == password:
            user_obj = Usuario(
                id=user_data[0]['id'], 
                nombre=user_data[0]['nombre'], 
                email=user_data[0]['email'], 
                password=user_data[0]['password']
            )
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
        
        existe = ejecutar_query("SELECT * FROM hospital.usuarios WHERE mail = %s", (mail,), es_consulta=True)
        if existe:
            flash('El correo ya está registrado.', 'warning')
            return redirect(url_for('registrar_usuario'))

        sql = "INSERT INTO hospital.usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        ejecutar_query(sql, (nombre, mail, password))
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return render_template('usuario_form.html')

@app.route('/usuarios')
@login_required
def listar_usuarios():
    # Consulta corregida con prefijo de base de datos
    usuarios_db = ejecutar_query("SELECT id_usuario, nombre, mail FROM hospital.usuarios", es_consulta=True)
    return render_template('usuarios_lista.html', usuarios=usuarios_db or [])

# ==========================================
#        RUTAS DE CITAS MÉDICAS
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
            # Nota: Si sistema_citas da error, revisa gestion.py para usar hospital.citas
            sistema_citas.agendar_cita(paciente, fecha, hora)
            flash('Cita agendada con éxito.', 'success')
            return redirect(url_for('ver_todas_las_citas')) 
    return render_template('agendar.html')

@app.route('/citas')
@login_required
def ver_todas_las_citas():
    citas = sistema_citas.obtener_citas()
    return render_template('lista_citas.html', citas=citas)

@app.route('/cambiar_cita', methods=['POST'])
@login_required
def cambiar_cita():
    id_cita = request.form.get('id_cita')
    nueva_fecha = request.form.get('nueva_fecha')
    
    if id_cita and nueva_fecha:
        sql = "UPDATE hospital.citas SET fecha = %s WHERE id = %s"
        ejecutar_query(sql, (nueva_fecha, id_cita))
        flash("¡Fecha actualizada correctamente!", "success")
    else:
        flash("No se pudo actualizar la cita.", "danger")
    return redirect(url_for('ver_todas_las_citas'))

# ==========================================
#        RUTAS DE INVENTARIO Y FACTURACIÓN
# ==========================================

@app.route('/inventario/nuevo', methods=['GET', 'POST'])
@login_required
def producto_form():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        try:
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('cantidad', 0))
            
            ejecutar_query("INSERT INTO hospital.servicios (nombre, precio, stock_disponible) VALUES (%s, %s, %s)", (nombre, precio, stock))
            guardar_formatos_planos(nombre, precio, stock)
            
            flash('Producto agregado al inventario.', 'success')
            return redirect(url_for('ver_datos'))
        except ValueError:
            flash('Error en los datos numéricos introducidos.', 'danger')
    return render_template('producto_form.html')

@app.route('/datos')
@login_required
def ver_datos():
    servicios_mysql = ejecutar_query("SELECT id_servicio, nombre, precio, stock_disponible FROM hospital.servicios", es_consulta=True) or []
    return render_template('datos.html', servicios=servicios_mysql)

@app.route('/inventario/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    sql = "DELETE FROM hospital.servicios WHERE id_servicio = %s"
    ejecutar_query(sql, (id,))
    flash('Producto eliminado correctamente.', 'warning')
    return redirect(url_for('ver_datos'))

@app.route('/factura', methods=['GET', 'POST'])
@login_required
def factura():
    total = None
    if request.method == 'POST':
        try:
            subtotal = float(request.form.get('subtotal', 0))
            iva = subtotal * 0.15
            total = "{:.2f}".format(subtotal + iva)
            flash(f"Cálculo realizado: Subtotal ${subtotal} + IVA", "success")
        except ValueError:
            flash("Por favor, ingresa un número válido.", "danger")
    return render_template('factura.html', total=total)

# ==========================================
#        EJECUCIÓN DEL SERVIDOR (RENDER)
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)