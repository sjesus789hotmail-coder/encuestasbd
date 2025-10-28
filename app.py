from flask import Flask, render_template
from encuestas import encuestas_bp
from preguntas import preguntas_bp
from respuestas import respuestas_bp
from usuarios import usuarios_bp
from resultados import resultados_bp   # ✅ aquí
from database import close_db

app = Flask(__name__)
app.secret_key = "clave_super_secreta_016"

# ✅ Registrar blueprints ANTES de run()
app.register_blueprint(usuarios_bp)
app.register_blueprint(encuestas_bp)
app.register_blueprint(preguntas_bp)
app.register_blueprint(respuestas_bp)
app.register_blueprint(resultados_bp)  # ✅ aquí

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
