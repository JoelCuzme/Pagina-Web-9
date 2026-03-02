from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def configurar_db(app):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Subimos un nivel para que la base de datos quede en la carpeta 'inventario'
    path_db = os.path.join(basedir, 'bd.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)