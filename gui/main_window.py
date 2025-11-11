import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

try:
    from models.graph import StarGraph
    from models.constellation import Constellation
    from models.star import Star
    from utils.file_loader import FileLoader
except ImportError as e:
    print(f"Error importando módulos: {e}")
    class StarGraph:
        def __init__(self): 
            self.constellations = []
            self.all_stars = {}
    class Constellation: 
        def __init__(self, name): 
            self.name = name
            self.stars = []
    class Star: 
        def __init__(self, **kwargs): 
            pass
    class FileLoader:
        @staticmethod
        def load_constellations(file_path):
            return {"constellations": []}

from gui.canvas import StarCanvas
from gui.controls import ControlPanel

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.graph = StarGraph()
        self.current_file = None
        
        self.setup_ui()
        self.setup_menu()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.control_panel = ControlPanel(main_frame, self)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.canvas = StarCanvas(main_frame, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas.control_panel = self.control_panel

    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Cargar Constelaciones", command=self.load_constellations)
        file_menu.add_command(label="Guardar Estado", command=self.save_state)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Limpiar Canvas", command=self.clear_canvas)
        tools_menu.add_command(label="Resetear Viaje", command=self.reset_journey)
    
    def load_constellations(self):
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
        self.graph = StarGraph()
        
        for constellation_data in data.get('constellations', []):
            constellation = Constellation(constellation_data['name'])
            galaxy = constellation_data.get('galaxy', 'Vía Láctea')  
            
            for star_data in constellation_data.get('starts', []):
                star = Star(
                    star_id=star_data['id'],
                    label=star_data['label'],
                    coordinates=star_data['coordenates'],
                    radius=star_data['radius'],
                    time_to_eat=star_data['timeToEat'],
                    amount_of_energy=star_data['amountOfEnergy'],
                    research_effect=star_data.get('researchEffect', 0),
                    hypergiant=star_data.get('hypergiant', False),
                    linked_to=star_data['linkedTo'],
                    galaxy=galaxy  
                )
                constellation.add_star(star)
            
            self.graph.add_constellation(constellation)
        
        burro_data = {
            'initial_energy': data.get('burroenergiaInicial', 100),
            'health_state': data.get('estadoSalud', 'Excelente'),
            'grass': data.get('pasto', 300),
            'start_age': data.get('startAge', 12),
            'death_age': data.get('deathAge', 3567)
        }
        
        self.control_panel.update_burro_data(burro_data)
        self.canvas.graph = self.graph
        self.canvas.draw_graph(self.graph)
    
    def save_state(self):
        messagebox.showinfo("Información", "Funcionalidad de guardado en desarrollo")
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.graph = StarGraph()
    
    def reset_journey(self):
        self.canvas.reset_highlight()
        self.control_panel.reset_journey()
    
    def calculate_route(self, start_star_id, algorithm_type, end_star_id=None):
        try:
            if not start_star_id:
                messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero")
                return []
            
            burro_data = self.control_panel.get_burro_data()
            
            from src.algorithms.path_finder import PathFinder
            finder = PathFinder(self.graph)
            
            route = []
            
            if algorithm_type == "max_stars":
                route = finder.find_max_stars_route(
                    start_star_id,
                    burro_data['health_state'],
                    burro_data['start_age'],
                    burro_data['initial_energy'],
                    burro_data['grass'],
                    burro_data['death_age']
                )
            elif algorithm_type == "to_destination":
                if not end_star_id:
                    messagebox.showwarning("Advertencia", "Selecciona una estrella destino primero (clic derecho)")
                    return []
                route = finder.find_route_to_destination(start_star_id, end_star_id)
            elif algorithm_type == "optimal_route":
                route = finder.find_optimal_route(
                    start_star_id,
                    burro_data['health_state'],
                    burro_data['initial_energy'],
                    burro_data['grass'],
                    burro_data['health_state']
                )
            
            if route:
                self.canvas.highlight_route(route)
                
                total_distance = self.calculate_route_distance(route)
                
                self.control_panel.show_route_info(route, total_distance)
                
                return route
            else:
                messagebox.showwarning("Advertencia", "No se pudo calcular una ruta válida")
                return []
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular la ruta: {str(e)}")
            return []
    
    def calculate_route_distance(self, route):
        total_distance = 0
        for i in range(len(route) - 1):
            star1 = self.graph.get_star_by_id(route[i])
            star2 = self.graph.get_star_by_id(route[i+1])
            if star1 and star2:
                for conn in star1.linked_to:
                    if str(conn['starId']) == route[i+1]:
                        total_distance += conn['distance']
                        break
        return total_distance
    
    def start_journey(self, start_star_id, end_star_id=None):
        try:
            if not start_star_id:
                messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero")
                return
            
            burro_data = self.control_panel.get_burro_data()
            from src.algorithms.path_finder import PathFinder
            finder = PathFinder(self.graph)
            
            if end_star_id:
                route = finder.find_route_to_destination(start_star_id, end_star_id)
            else:
                route = finder.find_optimal_route(
                    start_star_id,
                    burro_data['health_state'],
                    burro_data['initial_energy'],
                    burro_data['grass'],
                    burro_data['health_state']
                )
            
            if route:
                self.canvas.animate_journey(route, speed=1000)
            else:
                messagebox.showwarning("Advertencia", "No se pudo calcular una ruta para el viaje")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar el viaje: {str(e)}")