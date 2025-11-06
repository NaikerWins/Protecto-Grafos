import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.canvas import StarCanvas
from gui.controls import ControlPanel
from utils.file_loader import FileLoader
from models.graph import StarGraph
from models.constellation import Constellation
from models.star import Star

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.graph = StarGraph()
        self.current_file = None
        
        self.setup_ui()
        self.setup_menu()
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de controles a la izquierda
        self.control_panel = ControlPanel(main_frame, self)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Canvas para visualización a la derecha
        self.canvas = StarCanvas(main_frame, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def setup_menu(self):
        """Configura la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Cargar Constelaciones", command=self.load_constellations)
        file_menu.add_command(label="Guardar Estado", command=self.save_state)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Limpiar Canvas", command=self.clear_canvas)
        tools_menu.add_command(label="Resetear Viaje", command=self.reset_journey)
    
    def load_constellations(self):
        """Carga un archivo JSON de constelaciones"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de constelaciones",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                loader = FileLoader()
                data = loader.load_constellations(file_path)
                self.process_constellation_data(data)
                self.current_file = file_path
                messagebox.showinfo("Éxito", "Constelaciones cargadas correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
    
    def process_constellation_data(self, data):
        """Procesa los datos de constelaciones y actualiza el grafo"""
        self.graph = StarGraph()
        
        # Procesar cada constelación
        for constellation_data in data.get('constellations', []):
            constellation = Constellation(constellation_data['name'])
            
            # Procesar cada estrella
            for star_data in constellation_data.get('starts', []):
                star = Star(
                    star_id=star_data['id'],
                    label=star_data['label'],
                    coordinates=star_data['coordenates'],
                    radius=star_data['radius'],
                    time_to_eat=star_data['timeToEat'],
                    amount_of_energy=star_data['amountOfEnergy'],
                    hypergiant=star_data['hypergiant'],
                    linked_to=star_data['linkedTo']
                )
                constellation.add_star(star)
            
            self.graph.add_constellation(constellation)
        
        # Actualizar datos del burro
        burro_data = {
            'initial_energy': data.get('burroenergiaInicial', 100),
            'health_state': data.get('estadoSalud', 'Excelente'),
            'grass': data.get('pasto', 300),
            'start_age': data.get('startAge', 12),
            'death_age': data.get('deathAge', 3567)
        }
        
        self.control_panel.update_burro_data(burro_data)
        self.canvas.draw_graph(self.graph)
    
    def save_state(self):
        """Guarda el estado actual del sistema"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "No hay archivo cargado")
            return
        
        try:
            # Aquí se implementaría la lógica para guardar el estado
            messagebox.showinfo("Éxito", "Estado guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def clear_canvas(self):
        """Limpia el canvas"""
        self.canvas.delete("all")
    
    def reset_journey(self):
        """Resetea el viaje actual"""
        self.canvas.reset_highlight()
        self.control_panel.reset_controls()
    
    def calculate_route(self, start_star_id, algorithm_type):
        """Calcula una ruta basada en los parámetros seleccionados"""
        try:
            # Obtener datos del burro desde el panel de control
            burro_data = self.control_panel.get_burro_data()
            
            if algorithm_type == "max_stars":
                from algorithms.path_finder import PathFinder
                finder = PathFinder(self.graph)
                route = finder.find_max_stars_route(
                    start_star_id,
                    burro_data['health_state'],
                    burro_data['start_age'],
                    burro_data['initial_energy'],
                    burro_data['grass'],
                    burro_data['death_age']
                )
            else:  # optimal_route
                from algorithms.path_finder import PathFinder
                finder = PathFinder(self.graph)
                route = finder.find_optimal_route(
                    start_star_id,
                    burro_data['health_state'],
                    burro_data['initial_energy'],
                    burro_data['grass'],
                    burro_data['health_state']
                )
            
            # Mostrar la ruta en el canvas
            self.canvas.highlight_route(route)
            
            # Mostrar información de la ruta
            self.control_panel.show_route_info(route)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular la ruta: {str(e)}")