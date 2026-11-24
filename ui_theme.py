import tkinter as tk
from tkinter import ttk


COLORS = {
    "background": "#f3f6fb",
    "navy": "#17324d",
    "blue": "#2463a6",
    "blue_hover": "#1b4f87",
    "text": "#213247",
    "muted": "#66778b",
    "border": "#d8e1eb",
    "white": "#ffffff",
    "error": "#b42318",
    "success": "#18794e",
    "warning": "#b54708",
}


def configurar_estilo(root):
    root.configure(background=COLORS["background"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        "TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
    )
    style.configure(
        "TButton",
        background=COLORS["blue"],
        foreground=COLORS["white"],
        padding=(14, 8),
        font=("TkDefaultFont", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "TButton",
        background=[
            ("active", COLORS["blue_hover"]),
            ("disabled", "#a9bbcf"),
        ],
        foreground=[("disabled", COLORS["white"])],
    )
    style.configure(
        "App.TFrame",
        background=COLORS["background"],
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["white"],
        bordercolor=COLORS["border"],
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "Header.TFrame",
        background=COLORS["navy"],
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["navy"],
        foreground=COLORS["white"],
        font=("TkDefaultFont", 20, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["navy"],
        foreground="#d8e6f4",
        font=("TkDefaultFont", 10),
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["white"],
        foreground=COLORS["navy"],
        font=("TkDefaultFont", 12, "bold"),
    )
    style.configure(
        "Field.TLabel",
        background=COLORS["white"],
        foreground=COLORS["text"],
        font=("TkDefaultFont", 10),
    )
    style.configure(
        "Hint.TLabel",
        background=COLORS["white"],
        foreground=COLORS["muted"],
        font=("TkDefaultFont", 9),
    )
    style.configure(
        "Error.TLabel",
        background=COLORS["white"],
        foreground=COLORS["error"],
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "Success.TLabel",
        background=COLORS["white"],
        foreground=COLORS["success"],
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["blue"],
        foreground=COLORS["white"],
        padding=(16, 9),
        font=("TkDefaultFont", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["blue_hover"]), ("disabled", "#a9bbcf")],
        foreground=[("disabled", COLORS["white"])],
    )
    style.configure(
        "Secondary.TButton",
        background=COLORS["white"],
        foreground=COLORS["navy"],
        padding=(14, 8),
        bordercolor=COLORS["border"],
        font=("TkDefaultFont", 10),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#eaf0f7"), ("disabled", "#f3f6fb")],
        foreground=[("disabled", COLORS["muted"])],
    )
    style.configure(
        "TEntry",
        padding=7,
        fieldbackground=COLORS["white"],
        bordercolor=COLORS["border"],
    )
    style.map(
        "TEntry",
        fieldbackground=[("disabled", "#f3f6fb")],
        foreground=[("disabled", COLORS["muted"])],
    )
    style.configure(
        "TCombobox",
        padding=6,
        fieldbackground=COLORS["white"],
        bordercolor=COLORS["border"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", COLORS["white"]),
            ("disabled", "#f3f6fb"),
        ],
        foreground=[("disabled", COLORS["muted"])],
    )
    style.configure(
        "Treeview",
        background=COLORS["white"],
        fieldbackground=COLORS["white"],
        foreground=COLORS["text"],
        rowheight=30,
        bordercolor=COLORS["border"],
    )
    style.configure(
        "Treeview.Heading",
        background="#eaf0f7",
        foreground=COLORS["navy"],
        font=("TkDefaultFont", 10, "bold"),
        padding=7,
    )
    style.map(
        "Treeview",
        background=[("selected", "#d9e8f8")],
        foreground=[("selected", COLORS["navy"])],
    )


def mostrar_dialogo(root, titulo, mensaje, tipo="info"):
    dialog = tk.Toplevel(root)
    dialog.title(titulo)
    dialog.configure(background=COLORS["white"])
    dialog.resizable(False, False)
    dialog.transient(root)

    color_por_tipo = {
        "error": COLORS["error"],
        "warning": COLORS["warning"],
        "info": COLORS["blue"],
    }
    color = color_por_tipo.get(tipo, COLORS["blue"])
    style = ttk.Style(dialog)
    style.configure(
        f"{tipo}.DialogIcon.TLabel",
        background=COLORS["white"],
        foreground=color,
        font=("TkDefaultFont", 22, "bold"),
    )
    style.configure(
        f"{tipo}.DialogMessage.TLabel",
        background=COLORS["white"],
        foreground=COLORS["text"],
        font=("TkDefaultFont", 10),
    )

    content = ttk.Frame(dialog, style="Card.TFrame", padding=20)
    content.pack(fill="both", expand=True)
    ttk.Label(
        content,
        text="!" if tipo != "info" else "i",
        style=f"{tipo}.DialogIcon.TLabel",
    ).pack(side="left", anchor="n", padx=(0, 16))
    ttk.Label(
        content,
        text=mensaje,
        style=f"{tipo}.DialogMessage.TLabel",
        wraplength=420,
        justify="left",
    ).pack(side="left", fill="x", expand=True)

    ttk.Button(
        content,
        text="Aceptar",
        style="Primary.TButton",
        command=dialog.destroy,
    ).pack(side="bottom", anchor="e", pady=(18, 0))

    dialog.bind("<Escape>", lambda _event: dialog.destroy())
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - dialog.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dialog.grab_set()
    dialog.wait_window()
