import tkinter as tk
from tkinter import ttk, messagebox

# Datos de prueba (deberían venir de la BD)
equipos_db = [
    {'id': 1, 'nombre': 'Cámara Pro', 'gama': 'alta', 'stock': 5},
    {'id': 2, 'nombre': 'Micrófono Media', 'gama': 'media', 'stock': 10},
    {'id': 3, 'nombre': 'Tripode', 'gama': 'media', 'stock': 8}
]

class AppCatalogo:
    def __init__(self, root):
        self.root = root
        self.root.title("Catálogo de Equipamiento (CU-04)")
        
        self.tree = ttk.Treeview(root, columns=('nombre', 'gama', 'stock'), show='headings')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('gama', text='Gama')
        self.tree.heading('stock', text='Stock')
        self.tree.pack()
        
        for e in equipos_db:
            self.tree.insert('', 'end', values=(e['nombre'], e['gama'], e['stock']), tags=(e,))
            
        tk.Button(root, text="Solicitar Préstamo", command=self.ir_a_solicitud).pack()

    def ir_a_solicitud(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione al menos un equipo")
            return
            
        # Obtener datos del equipo seleccionado
        item = self.tree.item(seleccion[0])
        equipo = {'nombre': item['values'][0], 'gama': item['values'][1]}
        
        messagebox.showinfo("Redirección", f"Redirigiendo al CU-07 con: {equipo['nombre']}")
        # Aquí llamaríamos al CU-07 pasando el equipo
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = AppCatalogo(root)
    root.mainloop()
