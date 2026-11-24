import sqlite3
import tempfile
import unittest
from pathlib import Path

from init_db import init_db


class InitDbTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "test_prestamos.db"
        init_db(self.db_path)

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def test_creates_rfc_tables_and_columns(self):
        with self.connect() as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            self.assertTrue(
                {"equipo", "solicitud", "solicitud_equipo", "reserva"} <= tables
            )

            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(solicitud)")
            }
            self.assertTrue(
                {
                    "usuario_id",
                    "tipo",
                    "materia_proyecto",
                    "docente_cargo",
                    "justificacion",
                    "fecha_retiro",
                    "fecha_devolucion",
                    "estado",
                    "fecha_creacion",
                }
                <= columns
            )
            self.assertTrue({"materia_id", "docente_id"} <= columns)
            materia_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(materia)")
            }
            self.assertIn("es_materia_proyecto", materia_columns)

    def test_initialization_is_idempotent_and_preserves_rows(self):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO equipo (nombre, gama, stock) VALUES (?, ?, ?)",
                ("Tripode", "media", 3),
            )

        init_db(self.db_path)

        with self.connect() as connection:
            self.assertEqual(
                connection.execute("SELECT nombre FROM equipo").fetchone()[0],
                "Tripode",
            )

    def test_constraints_and_references(self):
        with self.connect() as connection:
            invalid_equipment = [
                (None, "media", 1),
                ("Tripode", "premium", 1),
                ("Tripode", "media", -1),
            ]
            for name, gama, stock in invalid_equipment:
                with self.subTest(name=name, gama=gama, stock=stock):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            "INSERT INTO equipo (nombre, gama, stock) VALUES (?, ?, ?)",
                            (name, gama, stock),
                        )

            connection.execute(
                "INSERT INTO equipo (id, nombre, gama, stock) VALUES (1, ?, ?, ?)",
                ("Tripode", "media", 3),
            )
            connection.execute(
                """
                INSERT INTO solicitud (
                    id, usuario_id, tipo, fecha_retiro, fecha_devolucion,
                    estado, fecha_creacion
                ) VALUES (1, 100, 'media', '2026-11-24', '2026-11-25',
                          'APROBADA', '2026-11-24')
                """
            )
            connection.execute(
                "INSERT INTO solicitud_equipo VALUES (1, 1, 2)"
            )
            connection.execute(
                """
                INSERT INTO reserva (
                    equipo_id, solicitud_id, fecha_retiro, fecha_devolucion, cantidad
                ) VALUES (1, 1, '2026-11-24', '2026-11-25', 2)
                """
            )

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO solicitud_equipo VALUES (2, 1, 1)")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO solicitud_equipo VALUES (1, 2, 1)")
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("INSERT INTO solicitud_equipo VALUES (1, 1, 0)")

    def test_migrates_existing_request_table_without_dropping_rows(self):
        legacy_path = Path(self.temp_dir.name) / "legacy.db"
        with sqlite3.connect(legacy_path) as connection:
            connection.execute(
                """
                CREATE TABLE solicitud (
                    id INTEGER PRIMARY KEY,
                    usuario_id INTEGER,
                    docente_cargo TEXT,
                    fecha_retiro TEXT,
                    fecha_devolucion TEXT,
                    materia_proyecto TEXT,
                    estado TEXT
                )
                """
            )
            connection.execute(
                """
                INSERT INTO solicitud VALUES (
                    1, 100, 'Docente Legacy', '2026-12-01', '2026-12-02',
                    'Materia Legacy', 'APROBADA'
                )
                """
            )

        init_db(legacy_path)

        with sqlite3.connect(legacy_path) as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(solicitud)")
            }
            self.assertTrue({"materia_id", "docente_id"} <= columns)
            self.assertEqual(
                connection.execute(
                    "SELECT materia_proyecto, docente_cargo, estado FROM solicitud"
                ).fetchone(),
                ("Materia Legacy", "Docente Legacy", "APROBADA"),
            )


if __name__ == "__main__":
    unittest.main()
