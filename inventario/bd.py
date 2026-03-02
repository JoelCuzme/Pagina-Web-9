from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def configurar_db(app):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # SQLite en Render necesita una ruta absoluta
    path_db = os.path.join(basedir, 'bd.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)