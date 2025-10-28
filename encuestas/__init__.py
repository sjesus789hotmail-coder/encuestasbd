from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db

encuestas_bp = Blueprint("encuestas", __name__, url_prefix="/encuestas")

@encuestas_bp.route("/")
def encuestas_index():
    db = get_db()
    encuestas = db.execute("SELECT * FROM encuestas").fetchall()
    return render_template("encuestas_index.html", encuestas=encuestas)

@encuestas_bp.route("/add", methods=["GET", "POST"])
def encuestas_add():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not titulo:
            flash("❌ El título es obligatorio.", "danger")
            # Re-render con los valores que el usuario escribió
            return render_template("encuestas_add.html", encuesta={"titulo": titulo, "descripcion": descripcion})

        db = get_db()
        db.execute("INSERT INTO encuestas (titulo, descripcion) VALUES (?, ?)", (titulo, descripcion))
        db.commit()
        flash("✅ Encuesta creada correctamente.", "success")
        return redirect(url_for("encuestas.encuestas_index"))

    return render_template("encuestas_add.html", encuesta=None)

@encuestas_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def encuestas_edit(id):
    db = get_db()
    encuesta = db.execute("SELECT * FROM encuestas WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not titulo:
            flash("❌ El título es obligatorio.", "danger")
            # Mantener lo que el usuario escribió
            encuesta = {"id": id, "titulo": titulo, "descripcion": descripcion}
            return render_template("encuestas_add.html", encuesta=encuesta)

        db.execute("UPDATE encuestas SET titulo=?, descripcion=? WHERE id=?", (titulo, descripcion, id))
        db.commit()
        flash("✏️ Encuesta actualizada correctamente.", "info")
        return redirect(url_for("encuestas.encuestas_index"))

    return render_template("encuestas_add.html", encuesta=encuesta)

@encuestas_bp.route("/delete/<int:id>")
def encuestas_delete(id):
    db = get_db()
    db.execute("DELETE FROM encuestas WHERE id=?", (id,))
    db.commit()
    flash("⚠️ Encuesta eliminada.", "warning")
    return redirect(url_for("encuestas.encuestas_index"))
