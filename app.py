from flask import Flask

app = Flask(__name__)

# Estilo CSS básico para mejorar la apariencia
estilo_comun = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 50px; }
        .card { box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 15px; }
        .btn-medical { background-color: #007bff; color: white; border-radius: 20px; }
    </style>
"""

@app.route('/')
def home():
    return f"""
    {estilo_comun}
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <div class="card p-5">
                    <h1 class="text-primary"> SaludTotal</h1>
                    <p class="lead">Sistema de Gestión de Citas Médicas</p>
                    <hr>
                    <p>Bienvenido al portal administrativo. Use las rutas para gestionar pacientes.</p>
                    <a href="/cita/Paciente_Ejemplo" class="btn btn-medical px-4">Probar Ruta Dinámica</a>
                </div>
            </div>
        </div>
    </div>
    """

@app.route('/cita/<paciente>')
def ver_cita(paciente):
    # Limpiamos el nombre para que se vea bien (cambia guiones por espacios)
    nombre_limpio = paciente.replace("_", " ")
    return f"""
    {estilo_comun}
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card p-4 border-start border-primary border-5">
                    <h3 class="text-secondary">Detalle de la Cita</h3>
                    <hr>
                    <p><strong>Paciente:</strong> {nombre_limpio}</p>
                    <div class="alert alert-success">
                         Su cita médica está <strong>confirmada</strong>. Consulta exitosa.
                    </div>
                    <a href="/" class="btn btn-sm btn-outline-secondary mt-3">Volver al Inicio</a>
                </div>
            </div>
        </div>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)