import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Tabla Usuarios
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

# Tabla Encuestas
c.execute("""
CREATE TABLE IF NOT EXISTS encuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla Preguntas
c.execute("""
CREATE TABLE IF NOT EXISTS preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_encuesta INTEGER NOT NULL,
    texto_pregunta TEXT NOT NULL,
    tipo TEXT NOT NULL,
    FOREIGN KEY(id_encuesta) REFERENCES encuestas(id)
)
""")

# Tabla Respuestas
c.execute("""
CREATE TABLE IF NOT EXISTS respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pregunta INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    respuesta_texto TEXT,
    valor INTEGER,
    FOREIGN KEY(id_pregunta) REFERENCES preguntas(id),
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
)
""")

conn.commit()
conn.close()
print("✅ Tablas creadas correctamente.")
