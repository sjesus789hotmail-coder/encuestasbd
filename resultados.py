from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from database import get_db
import csv
import io

# ⬇️ Imports para PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

resultados_bp = Blueprint("resultados", __name__, url_prefix="/resultados")

# =========================
#  Índice: lista encuestas
# =========================
@resultados_bp.route("/")
def resultados_index():
    db = get_db()
    encuestas = db.execute("SELECT * FROM encuestas").fetchall()
    return render_template("resultados_index.html", encuestas=encuestas)

# ======================================
#  Ver resultados de una encuesta (HTML)
# ======================================
@resultados_bp.route("/ver/<int:id_encuesta>")
def ver_resultados(id_encuesta):
    db = get_db()

    encuesta = db.execute("SELECT * FROM encuestas WHERE id=?", (id_encuesta,)).fetchone()
    if encuesta is None:
        flash("❌ La encuesta solicitada no existe.", "danger")
        return redirect(url_for("resultados.resultados_index"))

    preguntas = db.execute("""
        SELECT p.id, p.texto_pregunta,
               AVG(r.valor) as promedio
        FROM preguntas p
        LEFT JOIN respuestas r ON p.id = r.id_pregunta
        WHERE p.id_encuesta=?
        GROUP BY p.id
    """, (id_encuesta,)).fetchall()

    return render_template("resultados.html", encuesta=encuesta, preguntas=preguntas)

# ============================
#  Exportar resultados en CSV
# ============================
@resultados_bp.route("/export_csv/<int:id_encuesta>")
def export_csv(id_encuesta):
    db = get_db()

    encuesta = db.execute("SELECT * FROM encuestas WHERE id=?", (id_encuesta,)).fetchone()
    if encuesta is None:
        flash("❌ No se puede exportar: la encuesta no existe.", "danger")
        return redirect(url_for("resultados.resultados_index"))

    preguntas = db.execute("""
        SELECT p.texto_pregunta, AVG(r.valor) as promedio
        FROM preguntas p
        LEFT JOIN respuestas r ON p.id = r.id_pregunta
        WHERE p.id_encuesta=?
        GROUP BY p.id
    """, (id_encuesta,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Pregunta", "Promedio"])
    for p in preguntas:
        writer.writerow([p["texto_pregunta"], p["promedio"] if p["promedio"] is not None else 0])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"resultados_encuesta_{id_encuesta}.csv"
    )

# ============================
#  Exportar resultados en PDF
# ============================
@resultados_bp.route("/export_pdf/<int:id_encuesta>")
def export_pdf(id_encuesta):
    db = get_db()

    encuesta = db.execute("SELECT * FROM encuestas WHERE id=?", (id_encuesta,)).fetchone()
    if encuesta is None:
        flash("❌ No se puede exportar: la encuesta no existe.", "danger")
        return redirect(url_for("resultados.resultados_index"))

    preguntas = db.execute("""
        SELECT p.texto_pregunta, AVG(r.valor) as promedio
        FROM preguntas p
        LEFT JOIN respuestas r ON p.id = r.id_pregunta
        WHERE p.id_encuesta=?
        GROUP BY p.id
    """, (id_encuesta,)).fetchall()

    # Construir PDF en memoria
    buffer_pdf = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer_pdf,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story = []

    # Título y metadatos
    story.append(Paragraph("Resultados de la Encuesta", styles["Title"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"<b>Título:</b> {encuesta['titulo']}", styles["Normal"]))
    if encuesta["descripcion"]:
        story.append(Paragraph(f"<b>Descripción:</b> {encuesta['descripcion']}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # Tabla de promedios
    data = [["Pregunta", "Promedio"]]
    for p in preguntas:
        prom = p["promedio"] if p["promedio"] is not None else 0
        data.append([p["texto_pregunta"], f"{prom:.2f}"])

    if len(data) == 1:
        data.append(["(Sin preguntas aún)", "-"])

    table = Table(data, colWidths=[11*cm, 3*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 11),
        ("FONTSIZE", (0,1), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.aliceblue]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Documento generado automáticamente por EncuestasBD.", styles["Italic"]))

    # Generar documento
    doc.build(story)

    buffer_pdf.seek(0)
    return send_file(
        buffer_pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"resultados_encuesta_{id_encuesta}.pdf"
    )
