from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def configurar_db(app):
    # Usamos las variables que ya configuramos en Render/Aiven
    user = os.getenv('MYSQLUSER', 'avnadmin')
    password = os.getenv('MYSQLPASSWORD',)
    host = os.getenv('MYSQLHOST', 'mysql-3a27fee2-urssn90-b49f.f.aivencloud.com')
    port = os.getenv('MYSQLPORT', '16398')
    database = os.getenv('MYSQLDATABASE', 'hospital') # La que creaste en phpMyAdmin

    # Cambiamos el URI de SQLite a MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)