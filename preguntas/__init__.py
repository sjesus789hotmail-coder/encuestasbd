from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db

preguntas_bp = Blueprint("preguntas", __name__, url_prefix="/preguntas")

@preguntas_bp.route("/")
def preguntas_index():
    db = get_db()
    preguntas = db.execute("""
        SELECT p.id, p.texto_pregunta, p.tipo, e.titulo AS encuesta_titulo
        FROM preguntas p
        JOIN encuestas e ON p.id_encuesta = e.id
    """).fetchall()
    return render_template("preguntas_index.html", preguntas=preguntas)

@preguntas_bp.route("/add", methods=["GET", "POST"])
def preguntas_add():
    db = get_db()
    encuestas = db.execute("SELECT * FROM encuestas").fetchall()

    if request.method == "POST":
        id_encuesta = request.form.get("id_encuesta", "").strip()
        texto = request.form.get("texto_pregunta", "").strip()
        tipo = request.form.get("tipo", "").strip()

        if not id_encuesta or not texto or not tipo:
            flash("❌ Debes completar todos los campos.", "danger")
            # Mantener valores
            pregunta = {"id_encuesta": id_encuesta or "", "texto_pregunta": texto, "tipo": tipo}
            return render_template("preguntas_add.html", pregunta=pregunta, encuestas=encuestas)

        db.execute(
            "INSERT INTO preguntas (id_encuesta, texto_pregunta, tipo) VALUES (?, ?, ?)",
            (id_encuesta, texto, tipo)
        )
        db.commit()
        flash("✅ Pregunta creada correctamente.", "success")
        return redirect(url_for("preguntas.preguntas_index"))

    return render_template("preguntas_add.html", pregunta=None, encuestas=encuestas)

@preguntas_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def preguntas_edit(id):
    db = get_db()
    pregunta = db.execute("SELECT * FROM preguntas WHERE id=?", (id,)).fetchone()
    encuestas = db.execute("SELECT * FROM encuestas").fetchall()

    if request.method == "POST":
        id_encuesta = request.form.get("id_encuesta", "").strip()
        texto = request.form.get("texto_pregunta", "").strip()
        tipo = request.form.get("tipo", "").strip()

        if not id_encuesta or not texto or not tipo:
            flash("❌ Debes completar todos los campos.", "danger")
            pregunta = {"id": id, "id_encuesta": id_encuesta or "", "texto_pregunta": texto, "tipo": tipo}
            return render_template("preguntas_add.html", pregunta=pregunta, encuestas=encuestas)

        db.execute(
            "UPDATE preguntas SET id_encuesta=?, texto_pregunta=?, tipo=? WHERE id=?",
            (id_encuesta, texto, tipo, id)
        )
        db.commit()
        flash("✏️ Pregunta actualizada correctamente.", "info")
        return redirect(url_for("preguntas.preguntas_index"))

    return render_template("preguntas_add.html", pregunta=pregunta, encuestas=encuestas)

@preguntas_bp.route("/delete/<int:id>")
def preguntas_delete(id):
    db = get_db()
    db.execute("DELETE FROM preguntas WHERE id=?", (id,))
    db.commit()
    flash("⚠️ Pregunta eliminada.", "warning")
    return redirect(url_for("preguntas.preguntas_index"))
