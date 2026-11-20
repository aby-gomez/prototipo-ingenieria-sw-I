import tkinter as tk
from tkinter import messagebox
from validaciones import ValidadorSolicitud

class AppCU07:
    def __init__(self, root):
        self.root = root
        self.root.title("Solicitud de Préstamo (CU-07)")
        
        self.validador = ValidadorSolicitud()
        
        # Inputs
        tk.Label(root, text="Rol (Alumno/Docente):").pack()
        self.rol = tk.Entry(root)
        self.rol.pack()
        
        tk.Label(root, text="Año (1-5):").pack()
        self.año = tk.Entry(root)
        self.año.pack()
        
        tk.Label(root, text="Gama (alta/media):").pack()
        self.gama = tk.Entry(root)
        self.gama.pack()
        
        tk.Button(root, text="Solicitar", command=self.solicitar).pack()

    def solicitar(self):
        rol = self.rol.get()
        año = int(self.año.get())
        gama = self.gama.get()
        
        equipos = [{'nombre': 'Equipo Test', 'gama': gama}]
        
        # Validar
        ok1, msg1 = self.validador.validar_gama(equipos)
        ok2, msg2 = self.validador.validar_restriccion_alta(año, equipos)
        
        if not ok1: messagebox.showerror("Error", msg1)
        elif not ok2: messagebox.showerror("Error", msg2)
        else: messagebox.showinfo("Éxito", "Solicitud validada correctamente.")

if __name__ == '__main__':
    root = tk.Tk()
    app = AppCU07(root)
    root.mainloop()
