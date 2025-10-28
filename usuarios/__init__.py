from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

def email_valido(correo: str) -> bool:
    # Validación simple (sin regex pesada, pero suficiente para uso básico)
    return "@" in correo and "." in correo and len(correo.split("@")[0]) > 0

@usuarios_bp.route("/")
def usuarios_index():
    db = get_db()
    usuarios = db.execute("SELECT * FROM usuarios").fetchall()
    return render_template("usuarios_index.html", usuarios=usuarios)

@usuarios_bp.route("/add", methods=["GET", "POST"])
def usuarios_add():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        rol = request.form.get("rol", "").strip()

        if not nombre or not correo or not rol:
            flash("❌ Debes completar Nombre, Correo y Rol.", "danger")
            usuario = {"nombre": nombre, "correo": correo, "rol": rol}
            return render_template("usuarios_add.html", usuario=usuario)

        if not email_valido(correo):
            flash("❌ Ingrese un correo válido.", "danger")
            usuario = {"nombre": nombre, "correo": correo, "rol": rol}
            return render_template("usuarios_add.html", usuario=usuario)

        db = get_db()
        db.execute("INSERT INTO usuarios (nombre, correo, rol) VALUES (?, ?, ?)", (nombre, correo, rol))
        db.commit()
        flash("✅ Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.usuarios_index"))

    return render_template("usuarios_add.html", usuario=None)

@usuarios_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def usuarios_edit(id):
    db = get_db()
    usuario = db.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        rol = request.form.get("rol", "").strip()

        if not nombre or not correo or not rol:
            flash("❌ Debes completar Nombre, Correo y Rol.", "danger")
            usuario = {"id": id, "nombre": nombre, "correo": correo, "rol": rol}
            return render_template("usuarios_add.html", usuario=usuario)

        if not email_valido(correo):
            flash("❌ Ingrese un correo válido.", "danger")
            usuario = {"id": id, "nombre": nombre, "correo": correo, "rol": rol}
            return render_template("usuarios_add.html", usuario=usuario)

        db.execute("UPDATE usuarios SET nombre=?, correo=?, rol=? WHERE id=?", (nombre, correo, rol, id))
        db.commit()
        flash("✏️ Usuario actualizado correctamente.", "info")
        return redirect(url_for("usuarios.usuarios_index"))

    return render_template("usuarios_add.html", usuario=usuario)

@usuarios_bp.route("/delete/<int:id>")
def usuarios_delete(id):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id=?", (id,))
    db.commit()
    flash("⚠️ Usuario eliminado.", "warning")
    return redirect(url_for("usuarios.usuarios_index"))
