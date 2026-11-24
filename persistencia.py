import sqlite3
from contextlib import closing
from datetime import date

from init_db import DB_PATH, init_db
from validaciones import ValidadorSolicitud


def _connect(db_path):
    connection = sqlite3.connect(db_path, timeout=5)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def obtener_equipos(db_path=None):
    db_path = db_path or DB_PATH
    init_db(db_path)
    with closing(_connect(db_path)) as connection:
        with connection:
            if connection.execute("SELECT COUNT(*) FROM equipo").fetchone()[0] == 0:
                connection.executemany(
                    """
                    INSERT INTO equipo (id, nombre, categoria, gama, stock)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        (1, "Camara Pro", "Video", "alta", 5),
                        (2, "Microfono Media", "Audio", "media", 10),
                        (3, "Tripode", "Soporte", "media", 8),
                    ),
                )
            rows = connection.execute(
                """
                SELECT id, nombre, categoria, gama, stock
                FROM equipo
                ORDER BY nombre
                """
            ).fetchall()
    return [
        {
            "id": row[0],
            "nombre": row[1],
            "categoria": row[2],
            "gama": row[3],
            "stock": row[4],
        }
        for row in rows
    ]


def _insertar_catalogos_academicos_demo(connection):
    if connection.execute("SELECT COUNT(*) FROM materia").fetchone()[0] != 0:
        return
    if connection.execute("SELECT COUNT(*) FROM docente").fetchone()[0] != 0:
        return

    connection.executemany(
        """
        INSERT INTO materia (id, nombre, es_materia_proyecto)
        VALUES (?, ?, ?)
        """,
        (
            (1, "Sonido e Iluminación (DEMO)", 0),
            (2, "Proyecto Audiovisual (DEMO)", 1),
        ),
    )
    connection.executemany(
        "INSERT INTO docente (id, nombre) VALUES (?, ?)",
        ((1, "Docente Demo A"), (2, "Docente Demo B")),
    )
    connection.executemany(
        "INSERT INTO docente_materia (docente_id, materia_id) VALUES (?, ?)",
        ((1, 1), (2, 1), (2, 2)),
    )


def obtener_materias(db_path=None, docente_id=None):
    db_path = db_path or DB_PATH
    init_db(db_path)
    with closing(_connect(db_path)) as connection:
        with connection:
            _insertar_catalogos_academicos_demo(connection)
            if docente_id is None:
                rows = connection.execute(
                    """
                    SELECT id, nombre, es_materia_proyecto
                    FROM materia
                    WHERE activa = 1
                    ORDER BY nombre
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT m.id, m.nombre, m.es_materia_proyecto
                    FROM materia m
                    JOIN docente_materia dm ON dm.materia_id = m.id
                    JOIN docente d ON d.id = dm.docente_id
                    WHERE m.activa = 1 AND d.activo = 1 AND d.id = ?
                    ORDER BY m.nombre
                    """,
                    (int(docente_id),),
                ).fetchall()
    return [
        {"id": row[0], "nombre": row[1], "es_materia_proyecto": bool(row[2])}
        for row in rows
    ]


def obtener_docentes(db_path=None, materia_id=None):
    db_path = db_path or DB_PATH
    init_db(db_path)
    with closing(_connect(db_path)) as connection:
        with connection:
            _insertar_catalogos_academicos_demo(connection)
            if materia_id is None:
                rows = connection.execute(
                    """
                    SELECT id, nombre
                    FROM docente
                    WHERE activo = 1
                    ORDER BY nombre
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT d.id, d.nombre
                    FROM docente d
                    JOIN docente_materia dm ON dm.docente_id = d.id
                    JOIN materia m ON m.id = dm.materia_id
                    WHERE d.activo = 1 AND m.activa = 1 AND m.id = ?
                    ORDER BY d.nombre
                    """,
                    (int(materia_id),),
                ).fetchall()
    return [{"id": row[0], "nombre": row[1]} for row in rows]


def registrar_solicitud(
    *,
    usuario_rol,
    equipos,
    fecha_retiro,
    fecha_devolucion,
    materia_id=None,
    docente_id=None,
    justificacion="",
    db_path=None,
):
    if not equipos:
        raise ValueError("La solicitud debe incluir al menos un equipo.")

    tipo = equipos[0]["gama"]
    if any(equipo["gama"] != tipo for equipo in equipos):
        raise ValueError("No es posible mezclar gamas en una solicitud.")
    validacion_fechas, mensaje_fechas = ValidadorSolicitud().validar_plazos(
        fecha_retiro,
        fecha_devolucion,
        tipo,
    )
    if not validacion_fechas:
        raise ValueError(mensaje_fechas)

    cantidades_por_equipo = {}
    for equipo in equipos:
        equipo_id = int(equipo["id"])
        cantidad = int(equipo["cantidad"])
        if cantidad <= 0:
            raise ValueError("La cantidad solicitada debe ser mayor que cero.")
        cantidades_por_equipo[equipo_id] = (
            cantidades_por_equipo.get(equipo_id, 0) + cantidad
        )

    if materia_id is None:
        raise ValueError("Seleccione Materia/Proyecto.")
    if docente_id is None:
        raise ValueError("Seleccione el docente a cargo.")
    if not justificacion.strip():
        raise ValueError("La justificación es obligatoria.")

    db_path = db_path or DB_PATH
    init_db(db_path)

    with closing(_connect(db_path)) as connection:
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            academic_row = connection.execute(
                """
                SELECT m.nombre, m.es_materia_proyecto, d.nombre
                FROM materia m
                JOIN docente_materia dm ON dm.materia_id = m.id
                JOIN docente d ON d.id = dm.docente_id
                WHERE m.id = ? AND d.id = ? AND m.activa = 1 AND d.activo = 1
                """,
                (int(materia_id), int(docente_id)),
            ).fetchone()
            if academic_row is None:
                raise ValueError(
                    "La materia y el docente seleccionados no tienen una asignacion valida."
                )
            materia_nombre, es_materia_proyecto, docente_nombre = academic_row
            if tipo == "alta" or (
                es_materia_proyecto and usuario_rol != "Docente"
            ):
                estado = "PENDIENTE"
            else:
                estado = "APROBADA"

            equipos_db = {}
            for equipo_id, cantidad in cantidades_por_equipo.items():
                row = connection.execute(
                    """
                    SELECT
                        e.nombre,
                        e.gama,
                        e.stock - COALESCE(SUM(
                            CASE
                                WHEN s.estado NOT IN (
                                    'RECHAZADA', 'CANCELADA', 'DEVUELTA', 'FINALIZADA'
                                ) THEN r.cantidad
                                ELSE 0
                            END
                        ), 0) AS disponible
                    FROM equipo e
                    LEFT JOIN reserva r
                        ON r.equipo_id = e.id
                        AND r.fecha_retiro <= ?
                        AND r.fecha_devolucion >= ?
                    LEFT JOIN solicitud s ON s.id = r.solicitud_id
                    WHERE e.id = ?
                    GROUP BY e.id
                    """,
                    (fecha_devolucion, fecha_retiro, equipo_id),
                ).fetchone()
                if row is None:
                    raise ValueError(f"El equipo con identificador {equipo_id} no existe.")
                nombre, gama, disponible = row
                if gama != tipo:
                    raise ValueError("La selección contiene equipos de gamas distintas.")
                if cantidad > disponible:
                    raise ValueError(
                        f"Stock insuficiente para {nombre}: disponibles {disponible}, "
                        f"solicitados {cantidad}."
                    )
                equipos_db[equipo_id] = (nombre, cantidad)

            cursor = connection.execute(
                """
                INSERT INTO solicitud (
                    usuario_id, tipo, materia_proyecto, docente_cargo, materia_id,
                    docente_id, justificacion, fecha_retiro, fecha_devolucion,
                    estado, fecha_creacion
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tipo,
                    materia_nombre,
                    docente_nombre,
                    int(materia_id),
                    int(docente_id),
                    justificacion.strip(),
                    fecha_retiro,
                    fecha_devolucion,
                    estado,
                    date.today().isoformat(),
                ),
            )
            solicitud_id = cursor.lastrowid
            for equipo_id, (_, cantidad) in equipos_db.items():
                connection.execute(
                    """
                    INSERT INTO solicitud_equipo (solicitud_id, equipo_id, cantidad)
                    VALUES (?, ?, ?)
                    """,
                    (solicitud_id, equipo_id, cantidad),
                )
                connection.execute(
                    """
                    INSERT INTO reserva (
                        equipo_id, solicitud_id, fecha_retiro, fecha_devolucion, cantidad
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        equipo_id,
                        solicitud_id,
                        fecha_retiro,
                        fecha_devolucion,
                        cantidad,
                    ),
                )

    return solicitud_id, estado
