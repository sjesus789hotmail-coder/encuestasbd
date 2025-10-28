import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Ruta a la base de datos SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tu_clave_secreta_aqui'  # necesaria si usamos formularios
