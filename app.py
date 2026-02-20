from flask import Flask, render_template, request

app = Flask(__name__)

# --- LÓGICA DE NEGOCIO (Dominio) ---
# Aislada de Flask, usa vocabulario de experto
def calcular_total_con_impuestos(monto_base):
    """Regla: Calcular el total de una factura incluyendo los impuestos (15%)"""
    IVA = 0.15
    return round(monto_base * (1 + IVA), 2)

def normalizar_nombre(texto):
    """Regla: Convertir formato de URL a nombre legible"""
    return texto.replace("_", " ")

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cita/<paciente>')
def ver_cita(paciente):
    nombre = normalizar_nombre(paciente)
    return render_template('about.html', nombre=nombre, es_cita=True)

@app.route('/factura', methods=['GET', 'POST'])
def factura():
    total = None
    if request.method == 'POST':
        subtotal = float(request.form.get('subtotal', 0))
        total = calcular_total_con_impuestos(subtotal)
    return render_template('factura.html', total=total)

if __name__ == '__main__':
    app.run(debug=True)