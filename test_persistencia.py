import sqlite3
import tempfile
import unittest
from pathlib import Path

from init_db import init_db
from persistencia import (
    obtener_docentes,
    obtener_equipos,
    obtener_materias,
    registrar_solicitud,
)


class PersistenciaSolicitudTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "prestamos.db"
        init_db(self.db_path)
        self.equipos = obtener_equipos(self.db_path)
        self.materias = obtener_materias(self.db_path)
        self.docentes = obtener_docentes(self.db_path)

    def test_catalog_seeds_demo_items_once(self):
        self.assertEqual(len(self.equipos), 3)
        self.assertEqual(
            [equipo["nombre"] for equipo in self.equipos],
            ["Camara Pro", "Microfono Media", "Tripode"],
        )
        self.assertEqual(len(obtener_equipos(self.db_path)), 3)

    def test_request_persists_equipment_and_approval_status(self):
        equipo = next(item for item in self.equipos if item["gama"] == "media")
        materia = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, materia["id"])[0]
        solicitud_id, estado = registrar_solicitud(
            usuario_rol="Alumno",
            equipos=[{**equipo, "cantidad": 2}],
            fecha_retiro="2026-12-01",
            fecha_devolucion="2026-12-03",
            materia_id=materia["id"],
            docente_id=docente["id"],
            justificacion="Practica de audio en laboratorio",
            db_path=self.db_path,
        )

        with sqlite3.connect(self.db_path) as connection:
            solicitud = connection.execute(
                """
                SELECT tipo, estado, materia_id, docente_id, materia_proyecto,
                       docente_cargo
                FROM solicitud WHERE id = ?
                """,
                (solicitud_id,),
            ).fetchone()
            relacion = connection.execute(
                """
                SELECT equipo_id, cantidad FROM solicitud_equipo
                WHERE solicitud_id = ?
                """,
                (solicitud_id,),
            ).fetchone()
            reserva = connection.execute(
                "SELECT cantidad FROM reserva WHERE solicitud_id = ?", (solicitud_id,)
            ).fetchone()

        self.assertEqual(estado, "APROBADA")
        self.assertEqual(
            solicitud,
            (
                "media",
                "APROBADA",
                materia["id"],
                docente["id"],
                materia["nombre"],
                docente["nombre"],
            ),
        )
        self.assertEqual(relacion, (equipo["id"], 2))
        self.assertEqual(reserva, (2,))

    def test_academic_catalog_filters_both_directions(self):
        project = next(
            item for item in self.materias if item["es_materia_proyecto"]
        )
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        teachers_for_regular = obtener_docentes(self.db_path, regular["id"])
        self.assertEqual(
            [teacher["nombre"] for teacher in teachers_for_regular],
            ["Docente Demo A", "Docente Demo B"],
        )
        materia_names_for_teacher_a = [
            item["nombre"]
            for item in obtener_materias(
                self.db_path, teachers_for_regular[0]["id"]
            )
        ]
        self.assertEqual(materia_names_for_teacher_a, [regular["nombre"]])
        self.assertEqual(
            [teacher["nombre"] for teacher in obtener_docentes(
                self.db_path, project["id"]
            )],
            ["Docente Demo B"],
        )

    def test_demo_records_are_not_mixed_with_existing_academic_data(self):
        separate_path = Path(self.temp_dir.name) / "existing_academic_data.db"
        init_db(separate_path)
        with sqlite3.connect(separate_path) as connection:
            connection.execute(
                "INSERT INTO materia (nombre, es_materia_proyecto) VALUES (?, ?)",
                ("Materia Institucional", 0),
            )
            connection.execute(
                "INSERT INTO docente (nombre) VALUES (?)", ("Docente Institucional",)
            )

        subjects = obtener_materias(separate_path)
        teachers = obtener_docentes(separate_path)
        self.assertEqual(
            [item["nombre"] for item in subjects], ["Materia Institucional"]
        )
        self.assertEqual(
            [item["nombre"] for item in teachers], ["Docente Institucional"]
        )

    def test_project_request_is_pending_unless_submitted_by_teacher(self):
        media_equipo = next(item for item in self.equipos if item["gama"] == "media")
        project = next(
            item for item in self.materias if item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, project["id"])[0]
        common = {
            "equipos": [{**media_equipo, "cantidad": 1}],
            "fecha_retiro": "2026-12-01",
            "fecha_devolucion": "2026-12-02",
            "materia_id": project["id"],
            "docente_id": docente["id"],
            "justificacion": "Registro de practica del proyecto",
            "db_path": self.db_path,
        }
        _, student_status = registrar_solicitud(usuario_rol="Alumno", **common)
        _, teacher_status = registrar_solicitud(usuario_rol="Docente", **common)

        self.assertEqual(student_status, "PENDIENTE")
        self.assertEqual(teacher_status, "APROBADA")

    def test_regular_subject_and_high_end_status(self):
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, regular["id"])[0]
        high_equipment = next(item for item in self.equipos if item["gama"] == "alta")
        common = {
            "usuario_rol": "Alumno",
            "fecha_retiro": "2026-12-01",
            "fecha_devolucion": "2026-12-03",
            "materia_id": regular["id"],
            "docente_id": docente["id"],
            "justificacion": "Practica de laboratorio",
            "db_path": self.db_path,
        }
        _, regular_status = registrar_solicitud(
            equipos=[{**next(item for item in self.equipos if item["gama"] == "media"),
                      "cantidad": 1}],
            **common,
        )
        _, high_status = registrar_solicitud(
            equipos=[{**high_equipment, "cantidad": 1}],
            **common,
        )
        self.assertEqual(regular_status, "APROBADA")
        self.assertEqual(high_status, "PENDIENTE")

    def test_overlapping_requests_cannot_exceed_stock(self):
        equipment = next(item for item in self.equipos if item["gama"] == "alta")
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, regular["id"])[0]
        request = {
            "usuario_rol": "Docente",
            "fecha_retiro": "2026-12-01",
            "fecha_devolucion": "2026-12-03",
            "materia_id": regular["id"],
            "docente_id": docente["id"],
            "justificacion": "Grabacion de practica de laboratorio",
            "db_path": self.db_path,
        }
        registrar_solicitud(
            equipos=[{**equipment, "cantidad": equipment["stock"] - 1}],
            **request,
        )

        with self.assertRaisesRegex(ValueError, "Stock insuficiente"):
            registrar_solicitud(equipos=[{**equipment, "cantidad": 2}], **request)

    def test_failed_request_does_not_leave_partial_rows(self):
        equipment = next(item for item in self.equipos if item["gama"] == "media")
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, regular["id"])[0]
        with self.assertRaisesRegex(ValueError, "Stock insuficiente"):
            registrar_solicitud(
                usuario_rol="Alumno",
                equipos=[{**equipment, "cantidad": equipment["stock"] + 1}],
                fecha_retiro="2026-12-01",
                fecha_devolucion="2026-12-02",
                materia_id=regular["id"],
                docente_id=docente["id"],
                justificacion="Practica de audio",
                db_path=self.db_path,
            )

        with sqlite3.connect(self.db_path) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM solicitud").fetchone()[0], 0
            )

    def test_persistence_rejects_missing_invalid_and_past_dates(self):
        equipment = next(item for item in self.equipos if item["gama"] == "media")
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, regular["id"])[0]
        for retiro, devolucion in (
            ("", "2026-12-02"),
            ("2026-12-01", ""),
            ("2026-2-1", "2026-12-02"),
            ("2020-12-01", "2020-12-02"),
        ):
            with self.subTest(retiro=retiro, devolucion=devolucion):
                with self.assertRaises(ValueError):
                    registrar_solicitud(
                        usuario_rol="Alumno",
                        equipos=[{**equipment, "cantidad": 1}],
                        fecha_retiro=retiro,
                        fecha_devolucion=devolucion,
                        materia_id=regular["id"],
                        docente_id=docente["id"],
                        justificacion="Solicito el equipo para una practica",
                        db_path=self.db_path,
                    )

        with sqlite3.connect(self.db_path) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM solicitud").fetchone()[0], 0
            )

    def test_required_academic_fields_and_relationship_are_enforced(self):
        equipment = next(item for item in self.equipos if item["gama"] == "media")
        regular = next(
            item for item in self.materias if not item["es_materia_proyecto"]
        )
        docente = obtener_docentes(self.db_path, regular["id"])[0]
        base = {
            "usuario_rol": "Alumno",
            "equipos": [{**equipment, "cantidad": 1}],
            "fecha_retiro": "2026-12-01",
            "fecha_devolucion": "2026-12-02",
            "materia_id": regular["id"],
            "docente_id": docente["id"],
            "justificacion": "Practica de laboratorio",
            "db_path": self.db_path,
        }
        for field, value, message in (
            ("materia_id", None, "Materia/Proyecto"),
            ("docente_id", None, "docente a cargo"),
            ("justificacion", "  ", "justificación"),
            (
                "docente_id",
                999999,
                "asignacion valida",
            ),
        ):
            request = {**base, field: value}
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(ValueError, message):
                    registrar_solicitud(**request)

        with sqlite3.connect(self.db_path) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM solicitud").fetchone()[0], 0
            )


if __name__ == "__main__":
    unittest.main()
