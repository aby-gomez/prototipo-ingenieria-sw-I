import sqlite3
import tkinter as tk
from tkinter import ttk

from gui_cu07 import AppCU07
from persistencia import obtener_equipos
from ui_theme import configurar_estilo, mostrar_dialogo


class AppCatalogo:
    def __init__(self, root, db_path=None):
        self.root = root
        self.db_path = db_path
        self.equipos = []
        self.root.title("Catálogo de equipamiento | CU-04")
        self.root.minsize(760, 520)
        configurar_estilo(root)

        header = ttk.Frame(root, style="Header.TFrame", padding=(28, 22))
        header.pack(fill="x")
        ttk.Label(
            header, text="Catálogo de equipamiento", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Busque equipos disponibles y agregue su selección a una solicitud.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        container = ttk.Frame(root, style="App.TFrame", padding=(24, 18))
        container.pack(fill="both", expand=True)
        card = ttk.Frame(container, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        ttk.Label(card, text="Equipos", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            card,
            text="Puede seleccionar más de un equipo de la misma gama.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(3, 10))

        search_frame = ttk.Frame(card, style="Card.TFrame")
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            search_frame,
            text="Buscar por nombre, categoría o gama",
            style="Field.TLabel",
        ).pack(side="left")
        self.search = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search)
        search_entry.pack(side="left", fill="x", expand=True, padx=(14, 0))
        self.search.trace_add("write", self.filtrar_equipos)

        columns = ("nombre", "categoria", "gama", "stock")
        self.tree = ttk.Treeview(
            card, columns=columns, show="headings", selectmode="extended", height=10
        )
        for column, title, width in (
            ("nombre", "Nombre", 220),
            ("categoria", "Categoría", 150),
            ("gama", "Gama", 100),
            ("stock", "Stock", 80),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.iniciar_solicitud)

        footer = ttk.Frame(card, style="Card.TFrame")
        footer.pack(fill="x", pady=(12, 0))
        self.status = ttk.Label(footer, text="", style="Hint.TLabel")
        self.status.pack(side="left", fill="x", expand=True)
        ttk.Button(
            footer,
            text="Solicitar préstamo",
            style="Primary.TButton",
            command=self.iniciar_solicitud,
        ).pack(side="right")

        self.cargar_equipos()

    def cargar_equipos(self):
        try:
            self.equipos = obtener_equipos(self.db_path)
        except sqlite3.Error as error:
            mostrar_dialogo(self.root, "Error de catálogo", str(error), "error")
            self.root.destroy()
            return
        self.filtrar_equipos()

    def filtrar_equipos(self, *_):
        query = self.search.get().strip().casefold()
        self.tree.delete(*self.tree.get_children())
        visibles = [
            equipo
            for equipo in self.equipos
            if query
            in " ".join(
                (equipo["nombre"], equipo["categoria"] or "", equipo["gama"])
            ).casefold()
        ]
        for equipo in visibles:
            self.tree.insert(
                "", "end", iid=str(equipo["id"]),
                values=(
                    equipo["nombre"],
                    equipo["categoria"] or "",
                    equipo["gama"],
                    equipo["stock"],
                ),
            )
        self.status.configure(text=f"{len(visibles)} equipo(s) disponible(s)")

    def iniciar_solicitud(self, _event=None):
        selected_ids = self.tree.selection()
        if not selected_ids:
            mostrar_dialogo(
                self.root,
                "Seleccione equipos",
                "Seleccione al menos un equipo del catálogo.",
                "warning",
            )
            return

        equipos_seleccionados = [
            equipo
            for equipo in self.equipos
            if str(equipo["id"]) in selected_ids
        ]
        for widget in self.root.winfo_children():
            widget.destroy()
        self.form = AppCU07(self.root, equipos_seleccionados, self.db_path)


if __name__ == "__main__":
    root = tk.Tk()
    AppCatalogo(root)
    root.mainloop()
