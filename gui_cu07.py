import tkinter as tk
from tkinter import ttk, messagebox
from validaciones import ValidadorSolicitud

class AppCU07:
    def __init__(self, root):
        self.root = root
        self.root.title("Solicitud de Préstamo (CU-07)")
        
        self.validador = ValidadorSolicitud()
        
        # Inputs
        tk.Label(root, text="Rol:").pack()
        self.rol = ttk.Combobox(root, values=["Alumno", "Docente"], state="readonly")
        self.rol.pack()
        self.rol.bind("<<ComboboxSelected>>", self.toggle_año)
        
        tk.Label(root, text="Año:").pack()
        self.año = ttk.Combobox(root, values=["1", "2", "3", "4", "5"], state="readonly")
        self.año.pack()
        
        tk.Label(root, text="Gama:").pack()
        self.gama = ttk.Combobox(root, values=["alta", "media"], state="readonly")
        self.gama.pack()
        
        tk.Label(root, text="Fecha Retiro (YYYY-MM-DD):").pack()
        self.fecha_retiro = tk.Entry(root)
        self.fecha_retiro.insert(0, "2026-11-20")
        self.fecha_retiro.pack()

        tk.Label(root, text="Fecha Devolución (YYYY-MM-DD):").pack()
        self.fecha_devolucion = tk.Entry(root)
        self.fecha_devolucion.insert(0, "2026-11-22")
        self.fecha_devolucion.pack()

        tk.Button(root, text="Solicitar", command=self.solicitar).pack()

    def toggle_año(self, event=None):
        if self.rol.get() == "Docente":
            self.año.set("")
            self.año.configure(state="disabled")
        else:
            self.año.configure(state="readonly")

    def solicitar(self):
        rol = self.rol.get()
        año_raw = self.año.get()
        gama = self.gama.get()
        fecha_retiro = self.fecha_retiro.get()
        fecha_devolucion = self.fecha_devolucion.get()
        
        if not rol or not gama or not fecha_retiro or not fecha_devolucion:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if rol == "Alumno":
            if not año_raw:
                messagebox.showerror("Error", "El campo Año es obligatorio para alumnos.")
                return
            año = int(año_raw)
        else:
            año = 99

        equipos = [{'nombre': 'Equipo Test', 'gama': gama}]
        
        # Validar
        ok1, msg1 = self.validador.validar_gama(equipos)
        ok2, msg2 = self.validador.validar_restriccion_alta(año, equipos)
        ok3, msg3 = self.validador.validar_rnf_07_08(False, fecha_retiro, fecha_devolucion)
        # Integrar validación de plazos real usando las fechas ingresadas
        ok5, msg5 = self.validador.validar_plazos(fecha_retiro, fecha_devolucion, gama)
        ok4, msg4 = self.validador.validar_cuenta_activa(1)

        if not ok1: messagebox.showerror("Error", msg1)
        elif not ok2: messagebox.showerror("Error", msg2)
        elif not ok5: messagebox.showerror("Error", msg5)
        elif not ok3: messagebox.showerror("Error", msg3)
        elif not ok4: messagebox.showerror("Error", msg4)
        else: messagebox.showinfo("Éxito", "Solicitud validada correctamente.")

if __name__ == '__main__':
    root = tk.Tk()
    app = AppCU07(root)
    root.mainloop()
