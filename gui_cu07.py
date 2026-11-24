import sqlite3
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from persistencia import (
    obtener_docentes,
    obtener_equipos,
    obtener_materias,
    registrar_solicitud,
)
from ui_theme import COLORS, configurar_estilo, mostrar_dialogo
from validaciones import ValidadorSolicitud


class AppCU07:
    def __init__(self, root, equipos_seleccionados=None, db_path=None):
        self.root = root
        self.db_path = db_path
        self.equipos = equipos_seleccionados or []
        self.cantidades = {}
        self.validador = ValidadorSolicitud()
        self.materias = []
        self.docentes = []
        self._materias_por_nombre = {}
        self._docentes_por_nombre = {}
        self.root.title("Solicitud de préstamo | CU-07")
        self.root.minsize(850, 730)
        configurar_estilo(root)

        self._construir_interfaz()
        self._cargar_catalogos_academicos()

    def _construir_interfaz(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(28, 22))
        header.pack(fill="x")
        ttk.Label(
            header, text="Solicitud de préstamo", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Complete los datos académicos, revise los equipos y confirme las fechas.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        content = ttk.Frame(self.root, style="App.TFrame", padding=(24, 18))
        content.pack(fill="both", expand=True)

        academic_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        academic_card.pack(fill="x")
        ttk.Label(
            academic_card, text="Datos de la solicitud", style="Section.TLabel"
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(
            academic_card,
            text="Los campos marcados con * son obligatorios.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(3, 14))

        for column in (1, 3):
            academic_card.columnconfigure(column, weight=1)

        self.rol = ttk.Combobox(
            academic_card, values=("Alumno", "Docente"), state="readonly"
        )
        self.rol.bind("<<ComboboxSelected>>", self._al_cambiar_rol)
        self.año = ttk.Combobox(
            academic_card,
            values=("1", "2", "3", "4", "5"),
            state="readonly",
        )
        self.materia_proyecto = ttk.Combobox(
            academic_card, state="readonly"
        )
        self.materia_proyecto.bind(
            "<<ComboboxSelected>>", self._al_cambiar_materia
        )
        self.docente_cargo = ttk.Combobox(
            academic_card, state="readonly"
        )
        self.docente_cargo.bind(
            "<<ComboboxSelected>>", self._al_cambiar_docente
        )

        self._agregar_campo(academic_card, "Rol *", self.rol, 2, 0)
        self._agregar_campo(academic_card, "Año académico *", self.año, 2, 2)
        self._agregar_campo(
            academic_card, "Materia / Proyecto *", self.materia_proyecto, 4, 0
        )
        self.etiqueta_docente = ttk.Label(
            academic_card, text="Docente a cargo *", style="Field.TLabel"
        )
        self.etiqueta_docente.grid(row=4, column=2, sticky="w", pady=(10, 4))
        self.docente_cargo.grid(
            row=5, column=2, columnspan=2, sticky="ew", padx=(0, 10)
        )

        ttk.Label(
            academic_card, text="Fecha de retiro * (AAAA-MM-DD)", style="Field.TLabel"
        ).grid(row=6, column=0, sticky="w", pady=(14, 4))
        ttk.Label(
            academic_card, text="Fecha de devolución * (AAAA-MM-DD)", style="Field.TLabel"
        ).grid(row=6, column=2, sticky="w", pady=(14, 4))
        default_retiro = date.today() + timedelta(days=2)
        default_devolucion = default_retiro + timedelta(days=2)
        self.fecha_retiro = ttk.Entry(academic_card)
        self.fecha_retiro.insert(0, default_retiro.isoformat())
        self.fecha_retiro.grid(
            row=7, column=0, columnspan=2, sticky="ew", padx=(0, 14)
        )
        self.fecha_devolucion = ttk.Entry(academic_card)
        self.fecha_devolucion.insert(0, default_devolucion.isoformat())
        self.fecha_devolucion.grid(
            row=7, column=2, columnspan=2, sticky="ew", padx=(0, 10)
        )

        ttk.Label(
            academic_card, text="Justificación *", style="Field.TLabel"
        ).grid(row=8, column=0, columnspan=4, sticky="w", pady=(14, 4))
        self.justificacion = tk.Text(
            academic_card,
            height=3,
            wrap="word",
            font=("TkDefaultFont", 10),
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["blue"],
            padx=8,
            pady=6,
        )
        self.justificacion.grid(
            row=9, column=0, columnspan=4, sticky="ew", padx=(0, 10)
        )

        self.error = ttk.Label(
            academic_card, text="", style="Error.TLabel", wraplength=760
        )
        self.error.grid(row=10, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self.estado = ttk.Label(
            academic_card, text="", style="Success.TLabel", wraplength=760
        )
        self.estado.grid(row=11, column=0, columnspan=4, sticky="w", pady=(8, 0))

        equipment_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        equipment_card.pack(fill="both", expand=True, pady=(16, 0))
        ttk.Label(
            equipment_card,
            text="Equipos seleccionados",
            style="Section.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            equipment_card,
            text="Ajuste la cantidad para cada equipo antes de confirmar.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(3, 10))

        columns = ("equipo", "gama", "disponible", "cantidad")
        self.equipment_tree = ttk.Treeview(
            equipment_card, columns=columns, show="headings", height=5
        )
        for column, title, width in (
            ("equipo", "Equipo", 360),
            ("gama", "Gama", 110),
            ("disponible", "Stock total", 110),
            ("cantidad", "Cantidad solicitada", 170),
        ):
            self.equipment_tree.heading(column, text=title)
            self.equipment_tree.column(column, width=width, anchor="w")
        self.equipment_tree.pack(fill="both", expand=True)
        self._cargar_equipos()

        actions = ttk.Frame(content, style="App.TFrame")
        actions.pack(fill="x", pady=(16, 0))
        ttk.Button(
            actions,
            text="Volver al catálogo",
            style="Secondary.TButton",
            command=self.volver_al_catalogo,
        ).pack(side="left")
        ttk.Button(
            actions,
            text="Confirmar solicitud",
            style="Primary.TButton",
            command=self.solicitar,
        ).pack(side="right")

    @staticmethod
    def _agregar_campo(parent, label, widget, row, column):
        ttk.Label(parent, text=label, style="Field.TLabel").grid(
            row=row, column=column, sticky="w", pady=(10, 4)
        )
        widget.grid(
            row=row + 1,
            column=column,
            sticky="ew",
            padx=(0, 14 if column == 0 else 10),
        )

    def _cargar_equipos(self):
        if not self.equipos:
            self.equipos = obtener_equipos(self.db_path)
        for equipo in self.equipos:
            item_id = str(equipo["id"])
            self.cantidades[equipo["id"]] = tk.StringVar(value="1")
            self.equipment_tree.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    equipo["nombre"],
                    equipo["gama"].capitalize(),
                    equipo["stock"],
                    "1",
                ),
            )
            self.equipment_tree.set(item_id, "cantidad", "1")
        self.equipment_tree.bind("<Double-1>", self._editar_cantidad)
        self.equipment_tree.bind("<Button-1>", self._mostrar_spinbox)

    def _editar_cantidad(self, event):
        self._mostrar_spinbox(event)

    def _mostrar_spinbox(self, event):
        region = self.equipment_tree.identify("region", event.x, event.y)
        column = self.equipment_tree.identify_column(event.x)
        item_id = self.equipment_tree.identify_row(event.y)
        if region != "cell" or column != "#4" or not item_id:
            return

        box = self.equipment_tree.bbox(item_id, column)
        if not box:
            return
        x, y, width, height = box
        equipo = next(
            equipo for equipo in self.equipos if str(equipo["id"]) == item_id
        )
        variable = self.cantidades[equipo["id"]]
        editor = ttk.Spinbox(
            self.equipment_tree,
            from_=1,
            to=max(1, equipo["stock"]),
            textvariable=variable,
            width=8,
            command=lambda: self.equipment_tree.set(
                item_id, "cantidad", variable.get()
            ),
        )
        editor.place(x=x, y=y, width=width, height=height)
        editor.focus_set()
        editor.bind(
            "<Return>",
            lambda _event: (
                self.equipment_tree.set(item_id, "cantidad", variable.get()),
                editor.destroy(),
            ),
        )
        editor.bind(
            "<FocusOut>",
            lambda _event: (
                self.equipment_tree.set(item_id, "cantidad", variable.get()),
                editor.destroy(),
            ),
        )

    def _cargar_catalogos_academicos(self):
        try:
            self.materias = obtener_materias(self.db_path)
            self.docentes = obtener_docentes(self.db_path)
        except sqlite3.Error as error:
            self._mostrar_error(f"No se pudieron cargar las materias y docentes: {error}")
            return
        self._materias_por_nombre = {
            materia["nombre"]: materia for materia in self.materias
        }
        self._docentes_por_nombre = {
            docente["nombre"]: docente for docente in self.docentes
        }
        self._actualizar_opciones_materia()
        self._actualizar_opciones_docente()

    def _actualizar_opciones_materia(self, docente_id=None, conservar=True):
        materias = obtener_materias(self.db_path, docente_id)
        nombres = [materia["nombre"] for materia in materias]
        actual = self.materia_proyecto.get()
        self.materia_proyecto.configure(values=nombres)
        self.materias = obtener_materias(self.db_path)
        self._materias_por_nombre = {
            materia["nombre"]: materia for materia in self.materias
        }
        if conservar and actual in nombres:
            self.materia_proyecto.set(actual)
        elif actual not in nombres:
            self.materia_proyecto.set("")

    def _actualizar_opciones_docente(self, materia_id=None, conservar=True):
        docentes = obtener_docentes(self.db_path, materia_id)
        nombres = [docente["nombre"] for docente in docentes]
        actual = self.docente_cargo.get()
        self.docente_cargo.configure(values=nombres)
        self.docentes = obtener_docentes(self.db_path)
        self._docentes_por_nombre = {
            docente["nombre"]: docente for docente in self.docentes
        }
        if conservar and actual in nombres:
            self.docente_cargo.set(actual)
        elif actual not in nombres:
            self.docente_cargo.set("")
        if len(nombres) == 1 and self.rol.get() != "Docente":
            self.docente_cargo.set(nombres[0])

    def _al_cambiar_rol(self, _event=None):
        es_docente = self.rol.get() == "Docente"
        self.año.configure(state="disabled" if es_docente else "readonly")
        if es_docente:
            self.año.set("")
            self.etiqueta_docente.configure(text="Docente solicitante *")
        else:
            self.etiqueta_docente.configure(text="Docente a cargo *")
        self.docente_cargo.configure(state="readonly")
        self.docente_cargo.set("")
        self.materia_proyecto.set("")
        self._actualizar_opciones_materia(conservar=False)
        self._actualizar_opciones_docente(conservar=False)

    def _al_cambiar_materia(self, _event=None):
        materia = self._materias_por_nombre.get(self.materia_proyecto.get())
        if materia is None:
            self._actualizar_opciones_docente(conservar=False)
            return
        self._actualizar_opciones_docente(materia["id"], conservar=True)

    def _al_cambiar_docente(self, _event=None):
        docente = self._docentes_por_nombre.get(self.docente_cargo.get())
        if docente is None:
            self._actualizar_opciones_materia(conservar=False)
            return
        if self.rol.get() == "Docente":
            self.docente_cargo.configure(state="disabled")
        self._actualizar_opciones_materia(docente["id"], conservar=True)

    def _mostrar_error(self, message):
        self.estado.configure(text="")
        self.error.configure(text=message)

    def _validar_obligatorios(self):
        self.error.configure(text="")
        self.estado.configure(text="")
        checks = (
            (bool(self.rol.get()), "Seleccione el rol del solicitante.", self.rol),
            (
                self.rol.get() == "Docente" or bool(self.año.get()),
                "El año académico es obligatorio para alumnos.",
                self.año,
            ),
            (
                bool(self.materia_proyecto.get()),
                "Seleccione Materia/Proyecto.",
                self.materia_proyecto,
            ),
            (
                bool(self.docente_cargo.get()),
                "Seleccione el docente a cargo.",
                self.docente_cargo,
            ),
            (
                bool(self.fecha_retiro.get().strip()),
                "La fecha de retiro es obligatoria.",
                self.fecha_retiro,
            ),
            (
                bool(self.fecha_devolucion.get().strip()),
                "La fecha de devolución es obligatoria.",
                self.fecha_devolucion,
            ),
            (
                bool(self.justificacion.get("1.0", "end").strip()),
                "La justificación es obligatoria.",
                self.justificacion,
            ),
            (
                bool(self.equipos),
                "Seleccione al menos un equipo en el catálogo.",
                self.equipment_tree,
            ),
        )
        for valid, message, widget in checks:
            if not valid:
                self._mostrar_error(message)
                widget.focus_set()
                return False
        return True

    def volver_al_catalogo(self):
        from catalogo_cu04 import AppCatalogo

        for widget in self.root.winfo_children():
            widget.destroy()
        AppCatalogo(self.root, self.db_path)

    def solicitar(self):
        if not self._validar_obligatorios():
            return

        rol = self.rol.get()
        año = int(self.año.get()) if rol == "Alumno" else 99
        materia = self._materias_por_nombre.get(self.materia_proyecto.get())
        docente = self._docentes_por_nombre.get(self.docente_cargo.get())
        if materia is None:
            self._mostrar_error("Seleccione una Materia/Proyecto válida.")
            self.materia_proyecto.focus_set()
            return
        if docente is None:
            self._mostrar_error("Seleccione un docente válido.")
            self.docente_cargo.focus_set()
            return

        equipos = []
        try:
            for equipo in self.equipos:
                cantidad = int(self.cantidades[equipo["id"]].get())
                if cantidad <= 0 or cantidad > equipo["stock"]:
                    raise ValueError(
                        f"La cantidad para {equipo['nombre']} debe estar entre 1 y "
                        f"{equipo['stock']}."
                    )
                equipos.append({**equipo, "cantidad": cantidad})
        except ValueError as error:
            self._mostrar_error(str(error))
            return

        gama = equipos[0]["gama"]
        validations = (
            self.validador.validar_gama(equipos),
            self.validador.validar_restriccion_alta(año, equipos),
            self.validador.validar_plazos(
                self.fecha_retiro.get().strip(),
                self.fecha_devolucion.get().strip(),
                gama,
            ),
            self.validador.validar_cuenta_activa(1),
        )
        for valid, message in validations:
            if not valid:
                self._mostrar_error(message)
                if "fecha" in message.casefold() or "plazo" in message.casefold():
                    self.fecha_retiro.focus_set()
                return

        try:
            solicitud_id, estado = registrar_solicitud(
                usuario_rol=rol,
                equipos=equipos,
                fecha_retiro=self.fecha_retiro.get().strip(),
                fecha_devolucion=self.fecha_devolucion.get().strip(),
                materia_id=materia["id"],
                docente_id=docente["id"],
                justificacion=self.justificacion.get("1.0", "end").strip(),
                db_path=self.db_path,
            )
        except (ValueError, sqlite3.Error) as error:
            self._mostrar_error(str(error))
            return

        message = f"Solicitud #{solicitud_id} creada con estado {estado}."
        self.estado.configure(text=message)
        mostrar_dialogo(self.root, "Solicitud registrada", message)


if __name__ == "__main__":
    root = tk.Tk()
    AppCU07(root)
    root.mainloop()
