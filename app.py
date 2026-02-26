from flask import Flask, render_template, request, redirect
from gestion import GestionMedica
from modelos import ServicioMedico

app = Flask(__name__)
sistema = GestionMedica()

# Función de utilidad (Lógica de Presentación)
def normalizar_nombre(texto):
    return texto.replace("_", " ")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cita/<paciente>')
def ver_cita(paciente):
    nombre = normalizar_nombre(paciente)
    # Reutilizamos about.html como tenías en tu código original
    return render_template('about.html', nombre=nombre)

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        
        # POO en acción: Creamos un objeto temporal para usar su lógica de impuestos
        # En un sistema real, aquí buscarías el servicio en la base de datos
        servicio_temp = ServicioMedico(0, "Consulta", subtotal)
        total = servicio_temp.calcular_iva() 
        
    return render_template('factura.html', total=total)
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        paciente = request.form.get('paciente')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
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

if __name__ == '__main__':
    app.run(debug=True)