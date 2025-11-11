import tkinter as tk
from tkinter import ttk

class ResearchEditor:
    def __init__(self, parent, graph, on_save_callback):
        self.parent = parent
        self.graph = graph
        self.on_save_callback = on_save_callback
        self.star_vars = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Editor de Efectos de Investigación")
        self.window.geometry("600x400")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Modificar Efectos de Investigación", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        desc_label = ttk.Label(main_frame, 
                              text="Puedes modificar los efectos de investigación para cada estrella.\n"
                                   "Valores positivos: ganan vida, Valores negativos: pierden vida",
                              font=("Arial", 10))
        desc_label.pack(pady=5)
        
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('Estrella', 'Galaxia', 'Efecto Actual', 'Nuevo Efecto')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Guardar Cambios", 
                  command=self.save_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.load_stars_data()
    
    def load_stars_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for star in self.graph.get_all_stars():
            star_id = star.id
            effect_var = tk.StringVar(value=str(star.research_effect))
            self.star_vars[star_id] = effect_var
            
            self.tree.insert('', tk.END, values=(
                f"{star.label} (ID: {star.id})",
                getattr(star, 'galaxy', 'Vía Láctea'),
                star.research_effect,
                effect_var.get()
            ), tags=(star_id,))
        
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def on_double_click(self, event):
        item = self.tree.selection()[0]
        star_id = self.tree.item(item, 'tags')[0]
        
        self.edit_effect(star_id, item)
    
    def edit_effect(self, star_id, tree_item):
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Editar Efecto")
        edit_window.geometry("300x150")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        star = self.graph.get_star_by_id(star_id)
        
        ttk.Label(edit_window, text=f"Editar efecto para {star.label}", 
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        ttk.Label(edit_window, text="Efecto de investigación:").pack()
        
        effect_var = tk.StringVar(value=str(star.research_effect))
        effect_entry = ttk.Entry(edit_window, textvariable=effect_var, width=10)
        effect_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Positivo: gana vida, Negativo: pierde vida").pack()
        
        def save_effect():
            try:
                new_effect = float(effect_var.get())
                self.star_vars[star_id].set(str(new_effect))
                
                current_values = list(self.tree.item(tree_item, 'values'))
                current_values[3] = str(new_effect)
                self.tree.item(tree_item, values=current_values)
                
                edit_window.destroy()
            except ValueError:
                tk.messagebox.showerror("Error", "Por favor ingresa un número válido")
        
        ttk.Button(edit_window, text="Guardar", command=save_effect).pack(pady=5)
    
    def save_changes(self):
        changes = {}
        for star_id, effect_var in self.star_vars.items():
            try:
                new_effect = float(effect_var.get())
                star = self.graph.get_star_by_id(star_id)
                if star and star.research_effect != new_effect:
                    changes[star_id] = new_effect
                    star.research_effect = new_effect
            except ValueError:
                pass
        
        if changes:
            self.on_save_callback(changes)
            tk.messagebox.showinfo("Éxito", f"Se guardaron {len(changes)} cambios")
        else:
            tk.messagebox.showinfo("Información", "No se realizaron cambios")
        
        self.window.destroy()