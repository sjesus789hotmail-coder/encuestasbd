from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db

respuestas_bp = Blueprint("respuestas", __name__, url_prefix="/respuestas")

@respuestas_bp.route("/")
def respuestas_index():
    db = get_db()
    respuestas = db.execute("""
        SELECT r.id, 
               u.nombre AS usuario, 
               p.texto_pregunta AS pregunta,
               r.respuesta_texto, 
               r.valor
        FROM respuestas r
        JOIN usuarios u ON r.id_usuario = u.id
        JOIN preguntas p ON r.id_pregunta = p.id
    """).fetchall()
    return render_template("respuestas_index.html", respuestas=respuestas)

@respuestas_bp.route("/add", methods=["GET", "POST"])
def respuestas_add():
    db = get_db()
    preguntas = db.execute("SELECT * FROM preguntas").fetchall()
    usuarios = db.execute("SELECT * FROM usuarios").fetchall()

    if request.method == "POST":
        id_pregunta = request.form.get("id_pregunta", "").strip()
        id_usuario = request.form.get("id_usuario", "").strip()
        respuesta_texto = request.form.get("respuesta_texto", "").strip()
        valor_raw = request.form.get("valor", "").strip()

        # Validaciones
        if not id_pregunta or not id_usuario or not respuesta_texto:
            flash("❌ Debes completar Pregunta, Usuario y Texto de la respuesta.", "danger")
            respuesta = {
                "id_pregunta": id_pregunta or "",
                "id_usuario": id_usuario or "",
                "respuesta_texto": respuesta_texto,
                "valor": valor_raw
            }
            return render_template("respuestas_add.html", respuesta=respuesta, preguntas=preguntas, usuarios=usuarios)

        valor = None
        if valor_raw != "":
            try:
                valor = int(valor_raw)
            except ValueError:
                flash("❌ El valor debe ser numérico (o déjalo vacío).", "danger")
                respuesta = {
                    "id_pregunta": id_pregunta or "",
                    "id_usuario": id_usuario or "",
                    "respuesta_texto": respuesta_texto,
                    "valor": valor_raw
                }
                return render_template("respuestas_add.html", respuesta=respuesta, preguntas=preguntas, usuarios=usuarios)

        db.execute("""
            INSERT INTO respuestas (id_pregunta, id_usuario, respuesta_texto, valor)
            VALUES (?, ?, ?, ?)
        """, (id_pregunta, id_usuario, respuesta_texto, valor))
        db.commit()
        flash("✅ Respuesta registrada correctamente.", "success")
        return redirect(url_for("respuestas.respuestas_index"))

    return render_template("respuestas_add.html", respuesta=None, preguntas=preguntas, usuarios=usuarios)

@respuestas_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def respuestas_edit(id):
    db = get_db()
    respuesta = db.execute("SELECT * FROM respuestas WHERE id=?", (id,)).fetchone()
    preguntas = db.execute("SELECT * FROM preguntas").fetchall()
    usuarios = db.execute("SELECT * FROM usuarios").fetchall()

    if request.method == "POST":
        id_pregunta = request.form.get("id_pregunta", "").strip()
        id_usuario = request.form.get("id_usuario", "").strip()
        respuesta_texto = request.form.get("respuesta_texto", "").strip()
        valor_raw = request.form.get("valor", "").strip()

        if not id_pregunta or not id_usuario or not respuesta_texto:
            flash("❌ Debes completar Pregunta, Usuario y Texto de la respuesta.", "danger")
            respuesta = {
                "id": id,
                "id_pregunta": id_pregunta or "",
                "id_usuario": id_usuario or "",
                "respuesta_texto": respuesta_texto,
                "valor": valor_raw
            }
            return render_template("respuestas_add.html", respuesta=respuesta, preguntas=preguntas, usuarios=usuarios)

        valor = None
        if valor_raw != "":
            try:
                valor = int(valor_raw)
            except ValueError:
                flash("❌ El valor debe ser numérico (o déjalo vacío).", "danger")
                respuesta = {
                    "id": id,
                    "id_pregunta": id_pregunta or "",
                    "id_usuario": id_usuario or "",
                    "respuesta_texto": respuesta_texto,
                    "valor": valor_raw
                }
                return render_template("respuestas_add.html", respuesta=respuesta, preguntas=preguntas, usuarios=usuarios)

        db.execute("""
            UPDATE respuestas 
            SET id_pregunta=?, id_usuario=?, respuesta_texto=?, valor=?
            WHERE id=?
        """, (id_pregunta, id_usuario, respuesta_texto, valor, id))
        db.commit()
        flash("✏️ Respuesta actualizada correctamente.", "info")
        return redirect(url_for("respuestas.respuestas_index"))

    return render_template("respuestas_add.html", respuesta=respuesta, preguntas=preguntas, usuarios=usuarios)

@respuestas_bp.route("/delete/<int:id>")
def respuestas_delete(id):
    db = get_db()
    db.execute("DELETE FROM respuestas WHERE id=?", (id,))
    db.commit()
    flash("⚠️ Respuesta eliminada.", "warning")
    return redirect(url_for("respuestas.respuestas_index"))
