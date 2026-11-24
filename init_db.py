from contextlib import closing
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().with_name("prestamos.db")


def init_db(db_path=DB_PATH):
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS equipo (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    categoria TEXT,
                    gama TEXT NOT NULL CHECK (gama IN ('alta', 'media')),
                    stock INTEGER NOT NULL CHECK (stock >= 0)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS materia (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL UNIQUE,
                    es_materia_proyecto INTEGER NOT NULL DEFAULT 0
                        CHECK (es_materia_proyecto IN (0, 1)),
                    activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1))
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS docente (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL UNIQUE,
                    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS docente_materia (
                    docente_id INTEGER NOT NULL,
                    materia_id INTEGER NOT NULL,
                    PRIMARY KEY (docente_id, materia_id),
                    FOREIGN KEY (docente_id) REFERENCES docente(id),
                    FOREIGN KEY (materia_id) REFERENCES materia(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS solicitud (
                    id INTEGER PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    materia_proyecto TEXT,
                    docente_cargo TEXT,
                    materia_id INTEGER REFERENCES materia(id),
                    docente_id INTEGER REFERENCES docente(id),
                    justificacion TEXT,
                    fecha_retiro TEXT NOT NULL,
                    fecha_devolucion TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    fecha_creacion TEXT NOT NULL
                )
                """
            )
            solicitud_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(solicitud)")
            }
            if "materia_id" not in solicitud_columns:
                connection.execute(
                    "ALTER TABLE solicitud ADD COLUMN materia_id INTEGER REFERENCES materia(id)"
                )
            if "docente_id" not in solicitud_columns:
                connection.execute(
                    "ALTER TABLE solicitud ADD COLUMN docente_id INTEGER REFERENCES docente(id)"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS solicitud_equipo (
                    solicitud_id INTEGER NOT NULL,
                    equipo_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                    PRIMARY KEY (solicitud_id, equipo_id),
                    FOREIGN KEY (solicitud_id) REFERENCES solicitud(id),
                    FOREIGN KEY (equipo_id) REFERENCES equipo(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reserva (
                    id INTEGER PRIMARY KEY,
                    equipo_id INTEGER NOT NULL,
                    solicitud_id INTEGER NOT NULL,
                    fecha_retiro TEXT NOT NULL,
                    fecha_devolucion TEXT NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                    FOREIGN KEY (solicitud_id) REFERENCES solicitud(id),
                    FOREIGN KEY (equipo_id) REFERENCES equipo(id)
                )
                """
            )


if __name__ == "__main__":
    init_db()
