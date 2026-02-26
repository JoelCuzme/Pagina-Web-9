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

if __name__ == '__main__':
    app.run(debug=True)