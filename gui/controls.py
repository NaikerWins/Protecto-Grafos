import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

try:
    from utils.constants import Constants
    from models.burro import Burro
    from gui.research_editor import ResearchEditor
except ImportError:
    class Constants:
        HEALTH_EXCELLENT = "Excelente"
        HEALTH_GOOD = "Buena"
        HEALTH_POOR = "Mala"
        HEALTH_DYING = "Moribundo"
        HEALTH_DEAD = "Muerto"

class ControlPanel(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.selected_start_star = None
        self.selected_end_star = None
        self.burro_data = {}
        self.obstacle_mode = False
        self.current_burro = None
        self.current_route = []
        self.current_star_index = 0
        self._last_health_state = None
        self._last_energy = 0
        
        self.research_changes = {}  
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.setup_controls_content()
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_controls_content(self):
        title_label = ttk.Label(self.scrollable_frame, text="Control de Misión", font=("Arial", 14, "bold"))
        title_label.pack(pady=10, fill=tk.X)
        
        self.setup_burro_section()
        self.setup_star_selection()
        self.setup_algorithm_section()
        self.setup_obstacle_controls()
        self.setup_research_controls()
        self.setup_galaxy_controls()
        self.setup_travel_controls()
        self.setup_burro_status()
        self.setup_route_info()
    
    def setup_burro_section(self):
        burro_frame = ttk.LabelFrame(self.scrollable_frame, text="Estado del Burro", padding=10)
        burro_frame.pack(fill=tk.X, pady=5, padx=5)
        
        burro_frame.columnconfigure(1, weight=1)
        
        ttk.Label(burro_frame, text="Estado de Salud:").grid(row=0, column=0, sticky=tk.W)
        self.health_var = tk.StringVar(value=Constants.HEALTH_EXCELLENT)
        health_combo = ttk.Combobox(burro_frame, textvariable=self.health_var,
                                   values=[Constants.HEALTH_EXCELLENT, Constants.HEALTH_GOOD, 
                                          Constants.HEALTH_POOR, Constants.HEALTH_DYING])
        health_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5)
        
        ttk.Label(burro_frame, text="Energía Inicial:").grid(row=1, column=0, sticky=tk.W)
        self.energy_var = tk.StringVar(value="100")
        energy_entry = ttk.Entry(burro_frame, textvariable=self.energy_var, width=15)
        energy_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5)
        
        ttk.Label(burro_frame, text="Pasto (kg):").grid(row=2, column=0, sticky=tk.W)
        self.grass_var = tk.StringVar(value="300")
        grass_entry = ttk.Entry(burro_frame, textvariable=self.grass_var, width=15)
        grass_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5)
        
        ttk.Label(burro_frame, text="Edad Inicial:").grid(row=3, column=0, sticky=tk.W)
        self.start_age_var = tk.StringVar(value="12")
        start_age_entry = ttk.Entry(burro_frame, textvariable=self.start_age_var, width=15)
        start_age_entry.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5)
        
        ttk.Label(burro_frame, text="Edad de Muerte:").grid(row=4, column=0, sticky=tk.W)
        self.death_age_var = tk.StringVar(value="3567")
        death_age_entry = ttk.Entry(burro_frame, textvariable=self.death_age_var, width=15)
        death_age_entry.grid(row=4, column=1, sticky=tk.W+tk.E, padx=5)
    
    def setup_star_selection(self):
        star_frame = ttk.LabelFrame(self.scrollable_frame, text="Selección de Estrellas", padding=10)
        star_frame.pack(fill=tk.X, pady=5, padx=5)
        
        star_frame.columnconfigure(1, weight=1)
        
        ttk.Label(star_frame, text="Estrella Inicial:").grid(row=0, column=0, sticky=tk.W)
        self.start_star_var = tk.StringVar(value="No seleccionada")
        start_label = ttk.Label(star_frame, textvariable=self.start_star_var, 
                               font=("Arial", 9), foreground="green")
        start_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(star_frame, text="Estrella Final:").grid(row=1, column=0, sticky=tk.W)
        self.end_star_var = tk.StringVar(value="No seleccionada")
        end_label = ttk.Label(star_frame, textvariable=self.end_star_var, 
                             font=("Arial", 9), foreground="blue")
        end_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(star_frame, text="Clic izquierdo: Seleccionar inicio\nClic derecho: Seleccionar destino", 
                 font=("Arial", 8), foreground="gray").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def setup_algorithm_section(self):
        algo_frame = ttk.LabelFrame(self.scrollable_frame, text="Configuración de Ruta", padding=10)
        algo_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(algo_frame, text="Tipo de Ruta:").grid(row=0, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="max_stars")
        
        max_stars_radio = ttk.Radiobutton(algo_frame, text="Máximo de Estrellas", 
                                         variable=self.algorithm_var, value="max_stars")
        max_stars_radio.grid(row=1, column=0, sticky=tk.W)
        
        optimal_radio = ttk.Radiobutton(algo_frame, text="Ruta Óptima", 
                                       variable=self.algorithm_var, value="optimal_route")
        optimal_radio.grid(row=2, column=0, sticky=tk.W)
        
        to_destination_radio = ttk.Radiobutton(algo_frame, text="A Destino Específico", 
                                              variable=self.algorithm_var, value="to_destination")
        to_destination_radio.grid(row=3, column=0, sticky=tk.W)
    
    def setup_obstacle_controls(self):
        obstacle_frame = ttk.LabelFrame(self.scrollable_frame, text="Control de Obstáculos", padding=10)
        obstacle_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.obstacle_btn = ttk.Button(obstacle_frame, text="Activar Modo Obstáculos", 
                                      command=self.toggle_obstacle_mode)
        self.obstacle_btn.pack(fill=tk.X, pady=2)
        
        self.clear_obstacles_btn = ttk.Button(obstacle_frame, text="Limpiar Todos los Obstáculos", 
                                            command=self.clear_all_obstacles)
        self.clear_obstacles_btn.pack(fill=tk.X, pady=2)
        
        ttk.Label(obstacle_frame, text="En modo obstáculos, haz clic en las conexiones para bloquear/desbloquear", 
                 font=("Arial", 8), foreground="gray").pack(anchor=tk.W, pady=5)
    
    def setup_research_controls(self):
        research_frame = ttk.LabelFrame(self.scrollable_frame, text="Control de Investigación", padding=10)
        research_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.research_btn = ttk.Button(research_frame, text="Modificar Efectos de Investigación", 
                                      command=self.open_research_editor)
        self.research_btn.pack(fill=tk.X, pady=2)
        
        ttk.Label(research_frame, 
                 text="Puedes modificar cómo la investigación afecta la vida del burro", 
                 font=("Arial", 8), foreground="gray").pack(anchor=tk.W, pady=5)
    
    def setup_galaxy_controls(self):
        galaxy_frame = ttk.LabelFrame(self.scrollable_frame, text="Navegación entre Galaxias", padding=10)
        galaxy_frame.pack(fill=tk.X, pady=5, padx=5)
        
        galaxy_frame.columnconfigure(1, weight=1)
        
        ttk.Label(galaxy_frame, text="Galaxia Actual:").grid(row=0, column=0, sticky=tk.W)
        self.galaxy_var = tk.StringVar(value="Vía Láctea")
        ttk.Label(galaxy_frame, textvariable=self.galaxy_var, 
                 font=("Arial", 9, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(galaxy_frame, text="Hipergigantes disponibles:").grid(row=1, column=0, sticky=tk.W)
        self.hypergiant_var = tk.StringVar(value="0")
        ttk.Label(galaxy_frame, textvariable=self.hypergiant_var).grid(row=1, column=1, sticky=tk.W)
    
    def setup_travel_controls(self):
        control_frame = ttk.LabelFrame(self.scrollable_frame, text="Controles de Viaje", padding=10)
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.calculate_btn = ttk.Button(control_frame, text="Calcular Ruta", 
                                       command=self.calculate_route)
        self.calculate_btn.pack(fill=tk.X, pady=2)
        
        self.simulate_btn = ttk.Button(control_frame, text="Iniciar Viaje Paso a Paso", 
                                      command=self.start_step_by_step_journey)
        self.simulate_btn.pack(fill=tk.X, pady=2)
        
        self.next_step_btn = ttk.Button(control_frame, text="Siguiente Paso", 
                                       command=self.next_step, state=tk.DISABLED)
        self.next_step_btn.pack(fill=tk.X, pady=2)
        
        self.feed_btn = ttk.Button(control_frame, text="Alimentar Burro", 
                                  command=self.feed_burro, state=tk.DISABLED)
        self.feed_btn.pack(fill=tk.X, pady=2)
        
        self.reset_btn = ttk.Button(control_frame, text="Resetear Viaje", 
                                   command=self.reset_journey)
        self.reset_btn.pack(fill=tk.X, pady=2)
    
    def setup_burro_status(self):
        status_frame = ttk.LabelFrame(self.scrollable_frame, text="Estado Actual del Burro", padding=10)
        status_frame.pack(fill=tk.X, pady=5, padx=5)
        
        status_frame.columnconfigure(1, weight=1)
        
        self.health_status_var = tk.StringVar(value="No iniciado")
        ttk.Label(status_frame, text="Salud:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.health_status_var).grid(row=0, column=1, sticky=tk.W)
        
        self.energy_status_var = tk.StringVar(value="0%")
        ttk.Label(status_frame, text="Energía:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.energy_status_var).grid(row=1, column=1, sticky=tk.W)
        
        self.grass_status_var = tk.StringVar(value="0 kg")
        ttk.Label(status_frame, text="Pasto:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.grass_status_var).grid(row=2, column=1, sticky=tk.W)
        
        self.life_status_var = tk.StringVar(value="0 años luz")
        ttk.Label(status_frame, text="Vida Restante:").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.life_status_var).grid(row=3, column=1, sticky=tk.W)
    
    def setup_route_info(self):
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="Información de Ruta", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.route_text = tk.Text(info_frame, height=12, width=30, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.route_text.yview)
        self.route_text.configure(yscrollcommand=scrollbar.set)
        
        self.route_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.route_text.insert(tk.END, "Información de la ruta aparecerá aquí...\n\n")
        self.route_text.config(state=tk.DISABLED)

    def set_selected_star(self, star_id, is_right_click=False):
        if self.main_app.graph:
            star = self.main_app.graph.get_star_by_id(star_id)
            if star:
                if is_right_click:
                    self.selected_end_star = star_id
                    self.end_star_var.set(f"{star.label} (ID: {star.id})")
                else:
                    self.selected_start_star = star_id
                    self.start_star_var.set(f"{star.label} (ID: {star.id})")
                
                if hasattr(self.main_app, 'canvas'):
                    self.main_app.canvas.highlight_selected_stars(
                        self.selected_start_star, 
                        self.selected_end_star
                    )
    
    def toggle_obstacle_mode(self):
        self.obstacle_mode = not self.obstacle_mode
        if self.obstacle_mode:
            self.obstacle_btn.config(text="Desactivar Modo Obstáculos")
            if hasattr(self.main_app, 'canvas'):
                self.main_app.canvas.obstacle_mode = True
        else:
            self.obstacle_btn.config(text="Activar Modo Obstáculos")
            if hasattr(self.main_app, 'canvas'):
                self.main_app.canvas.obstacle_mode = False
    
    def clear_all_obstacles(self):
        if hasattr(self.main_app, 'graph'):
            self.main_app.graph.blocked_edges.clear()
            if hasattr(self.main_app, 'canvas'):
                self.main_app.canvas.draw_graph(self.main_app.graph)
    
    def update_burro_data(self, data):
        self.burro_data = data
        self.health_var.set(data.get('health_state', Constants.HEALTH_EXCELLENT))
        self.energy_var.set(str(data.get('initial_energy', 100)))
        self.grass_var.set(str(data.get('grass', 300)))
        self.start_age_var.set(str(data.get('start_age', 12)))
        self.death_age_var.set(str(data.get('death_age', 3567)))
    
    def get_burro_data(self):
        return {
            'health_state': self.health_var.get(),
            'initial_energy': float(self.energy_var.get()),
            'grass': float(self.grass_var.get()),
            'start_age': float(self.start_age_var.get()),
            'death_age': float(self.death_age_var.get())
        }
    
    def open_research_editor(self):
        if not hasattr(self.main_app, 'graph') or not self.main_app.graph:
            messagebox.showwarning("Advertencia", "Primero carga un archivo de constelaciones")
            return
        
        def on_save_changes(changes):
            self.research_changes.update(changes)
        
        editor = ResearchEditor(self, self.main_app.graph, on_save_changes)
    
    def calculate_route(self):
        if not self.selected_start_star:
            messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero (clic izquierdo)")
            return
        
        algorithm_type = self.algorithm_var.get()
        
        if algorithm_type == "to_destination" and not self.selected_end_star:
            messagebox.showwarning("Advertencia", "Para 'A Destino Específico' selecciona también una estrella destino (clic derecho)")
            return
        
        end_star = self.selected_end_star if algorithm_type == "to_destination" else None
        
        self.main_app.calculate_route(self.selected_start_star, algorithm_type, end_star)
    
    def start_step_by_step_journey(self):
        if not self.selected_start_star:
            messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero")
            return
        
        try:
            burro_data = self.get_burro_data()
            self.current_burro = Burro(
                burro_data['health_state'],
                burro_data['initial_energy'],
                burro_data['grass'],
                burro_data['start_age'],
                burro_data['death_age']
            )
            
            algorithm_type = self.algorithm_var.get()
            self.current_route = self.main_app.calculate_route(
                self.selected_start_star, 
                algorithm_type, 
                self.selected_end_star if algorithm_type == "to_destination" else None
            )
            
            if not self.current_route:
                messagebox.showwarning("Advertencia", "No se pudo calcular una ruta válida")
                return
            
            self.current_star_index = 0
            self.next_step_btn.config(state=tk.NORMAL)
            self.feed_btn.config(state=tk.NORMAL)
            self.update_burro_status()
            
            self.visit_current_star()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar viaje: {str(e)}")
    
    def next_step(self):
        if not self.current_burro or self.current_star_index >= len(self.current_route) - 1:
            self.end_journey()
            return
        
        if self.current_burro.is_dead():
            self.burro_died()
            return
        
        current_star_id = self.current_route[self.current_star_index]
        next_star_id = self.current_route[self.current_star_index + 1]
        
        distance = self.calculate_distance(current_star_id, next_star_id)
        if distance is None:
            messagebox.showerror("Error", "No se puede calcular la distancia entre estrellas")
            return
        
        if not self.current_burro.travel(distance):
            self.burro_died()
            return
        
        self.current_star_index += 1
        
        star = self.main_app.graph.get_star_by_id(next_star_id)
        if star:
            research_effect_override = self.research_changes.get(star.id, None)
            
            research_time = star.time_to_eat * 0.5
            self.current_burro.visit_star(star, research_time, research_effect_override)
        
        self.update_burro_status()
        
        if hasattr(self.main_app, 'canvas'):
            self.main_app.canvas.highlight_star(next_star_id, "yellow")
            self.main_app.canvas.draw_burro(
                self.main_app.canvas.star_objects[next_star_id]['x'],
                self.main_app.canvas.star_objects[next_star_id]['y']
            )
        
        if star and star.hypergiant:
            self.handle_hypergiant(star)
        
        self.show_current_step_info(star)
    
    def visit_current_star(self):
        if self.current_star_index >= len(self.current_route):
            return
        
        current_star_id = self.current_route[self.current_star_index]
        star = self.main_app.graph.get_star_by_id(current_star_id)
        
        if not star:
            return
        
        if hasattr(self.main_app, 'canvas'):
            self.main_app.canvas.highlight_star(current_star_id, "yellow")
            self.main_app.canvas.draw_burro(
                self.main_app.canvas.star_objects[current_star_id]['x'],
                self.main_app.canvas.star_objects[current_star_id]['y']
            )
        
        self.current_burro.visit_star(star)
        
        # Display information in the route panel
        self.show_current_step_info(star)
        
        if star.hypergiant:
            self.handle_hypergiant(star)
    
    def feed_burro(self):
        #Can feed manually
        if not self.current_burro or self.current_star_index >= len(self.current_route):
            return
        
        current_star_id = self.current_route[self.current_star_index]
        star = self.main_app.graph.get_star_by_id(current_star_id)
        
        if not star:
            return
        
        grass_window = tk.Toplevel(self)
        grass_window.title("Alimentar Burro")
        grass_window.geometry("300x200")
        grass_window.transient(self)
        grass_window.grab_set()
        
        ttk.Label(grass_window, text=f"¿Cuánto pasto dar al burro en {star.label}?", 
                 font=("Arial", 10)).pack(pady=10)
        
        ttk.Label(grass_window, text=f"Pasto disponible: {self.current_burro.grass:.1f} kg").pack()
        ttk.Label(grass_window, text=f"Tiempo para comer: {star.time_to_eat} unidades").pack()
        
        grass_var = tk.DoubleVar(value=0)
        max_grass = min(50, self.current_burro.grass)
        grass_scale = ttk.Scale(grass_window, from_=0, to=max_grass, 
                               variable=grass_var, orient=tk.HORIZONTAL)
        grass_scale.pack(pady=10, fill=tk.X, padx=20)
        
        grass_value_label = ttk.Label(grass_window, text="0 kg")
        grass_value_label.pack()
        
        def update_grass_value(*args):
            grass_value_label.config(text=f"{grass_var.get():.1f} kg")
        
        grass_var.trace('w', update_grass_value)
        
        def confirm_feed():
            grass_kg = grass_var.get()
            if grass_kg > 0:
                energy_gained = self.current_burro.feed_grass(grass_kg, star.time_to_eat)
                messagebox.showinfo("Alimentación", 
                                  f"El burro ha comido {grass_kg:.1f} kg de pasto\n"
                                  f"Energía ganada: +{energy_gained:.1f}%")
                self.update_burro_status()
            grass_window.destroy()
        
        ttk.Button(grass_window, text="Alimentar", command=confirm_feed).pack(pady=5)
        ttk.Button(grass_window, text="Cancelar", command=grass_window.destroy).pack(pady=5)
    
    def handle_hypergiant(self, star):
        # It handles the use of hypergiant stars between galaxies
        if not star.hypergiant:
            return
        
        available_galaxies = list(self.main_app.graph.galaxies)
        if star.galaxy in available_galaxies:
            available_galaxies.remove(star.galaxy)
        
        if not available_galaxies:
            messagebox.showinfo("Hipergigante", 
                              "¡Estrella hipergigante encontrada!\n"
                              "No hay otras galaxias disponibles para viajar.")
            self.current_burro.use_hypergiant()
            return
        
        galaxy_window = tk.Toplevel(self)
        galaxy_window.title("Viaje Intergaláctico")
        galaxy_window.geometry("400x300")
        galaxy_window.transient(self)
        galaxy_window.grab_set()
        
        ttk.Label(galaxy_window, 
                 text=f"¡Estrella hipergigante {star.label} encontrada!\n"
                      "Selecciona una galaxia destino:",
                 font=("Arial", 11), justify=tk.CENTER).pack(pady=15)
        

        galaxy_frame = ttk.Frame(galaxy_window)
        galaxy_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        selected_galaxy = tk.StringVar(value=available_galaxies[0])
        
        for i, galaxy in enumerate(available_galaxies):
          
            target_stars = self.main_app.graph.get_stars_by_galaxy(galaxy)
            hypergiants_in_galaxy = [s for s in target_stars if s.hypergiant]
            
            radio_text = f"{galaxy} ({len(target_stars)} estrellas"
            if hypergiants_in_galaxy:
                radio_text += f", {len(hypergiants_in_galaxy)} hipergigantes"
            radio_text += ")"
            
            ttk.Radiobutton(galaxy_frame, text=radio_text,
                           variable=selected_galaxy, value=galaxy).pack(anchor=tk.W, pady=5)
        
        def confirm_travel():
            target_galaxy = selected_galaxy.get()
            self.current_burro.use_hypergiant(target_galaxy)
            
            messagebox.showinfo("Viaje Intergaláctico", 
                              f"¡Viaje exitoso a {target_galaxy}!\n\n"
                              f"Efectos:\n"
                              f"- Energía recargada: {self.current_burro.current_energy:.1f}%\n"
                              f"- Pasto duplicado: {self.current_burro.grass:.1f} kg\n"
                              f"- Nueva galaxia: {target_galaxy}")
            

            self.galaxy_var.set(target_galaxy)
            hypergiants_count = len(self.main_app.graph.get_hypergiant_stars(target_galaxy))
            self.hypergiant_var.set(str(hypergiants_count))
            
            self.update_burro_status()
            galaxy_window.destroy()
        
        ttk.Button(galaxy_window, text="Viajar", command=confirm_travel).pack(pady=10)
        ttk.Button(galaxy_window, text="Cancelar", command=galaxy_window.destroy).pack(pady=5)
    
    def calculate_distance(self, star1_id, star2_id):

        star1 = self.main_app.graph.get_star_by_id(star1_id)
        star2 = self.main_app.graph.get_star_by_id(star2_id)
        
        if star1 and star2:
            for connection in star1.linked_to:
                if str(connection['starId']) == star2_id:
                    return connection['distance']
        return None
    
    def update_burro_status(self):

        if self.current_burro:
            status = self.current_burro.get_status()
            
            self.health_status_var.set(status['health_state'])
            self.energy_status_var.set(f"{status['current_energy']:.1f}%")
            self.grass_status_var.set(f"{status['grass']:.1f} kg")
            self.life_status_var.set(f"{status['remaining_life']:.1f} años luz")
            
            if 'current_galaxy' in status:
                self.galaxy_var.set(status['current_galaxy'])
            
            self._log_status_change(status)
    
    def _log_status_change(self, status):
        self.route_text.config(state=tk.NORMAL)
        
        if hasattr(self, '_last_health_state') and self._last_health_state != status['health_state']:
            self.route_text.insert(tk.END, f"⚡ Cambio de estado: {self._last_health_state} → {status['health_state']}\n")
        
        if status['current_energy'] < 25 and status['current_energy'] > 0:
            self.route_text.insert(tk.END, f"⚠️  Energía crítica: {status['current_energy']:.1f}%\n")
        
        if hasattr(self, '_last_energy') and status['current_energy'] > self._last_energy + 5:
            self.route_text.insert(tk.END, f"🌿 El burro comió automáticamente. Energía: {status['current_energy']:.1f}%\n")
        
        self._last_health_state = status['health_state']
        self._last_energy = status['current_energy']
        
        self.route_text.see(tk.END)
        self.route_text.config(state=tk.DISABLED)
    
    def show_current_step_info(self, star):
        if not self.current_burro:
            return
        
        status = self.current_burro.get_status()
        
        self.route_text.config(state=tk.NORMAL)
        self.route_text.insert(tk.END, f"\n--- Visitando {star.label} ---\n")
        self.route_text.insert(tk.END, f"Energía: {status['current_energy']:.1f}%\n")
        self.route_text.insert(tk.END, f"Pasto: {status['grass']:.1f} kg\n")
        self.route_text.insert(tk.END, f"Vida restante: {status['remaining_life']:.1f} años luz\n")
        
        if status['research_effects']:
            last_effect = status['research_effects'][-1]
            if last_effect['star'] == star.label:
                effect_str = f"+{last_effect['effect']}" if last_effect['effect'] > 0 else str(last_effect['effect'])
                self.route_text.insert(tk.END, f"🔬 Investigación: {effect_str} años luz\n")
        
        if status['current_energy'] < 50 and hasattr(self, '_last_energy'):
            if status['current_energy'] > self._last_energy:
                self.route_text.insert(tk.END, f"🌿 Comió automáticamente: +{(status['current_energy'] - self._last_energy):.1f}% energía\n")
        
        if star.hypergiant:
            self.route_text.insert(tk.END, "⭐ ESTRELLA HIPERGIGANTE ⭐\n")
        
        self.route_text.see(tk.END)
        self.route_text.config(state=tk.DISABLED)
        
        self._last_energy = status['current_energy']
    
    def burro_died(self):
        if self.current_burro:
            self.current_burro.play_death_sound()
            
            self.route_text.config(state=tk.NORMAL)
            self.route_text.insert(tk.END, f"\n💀 ¡EL BURRO HA MUERTO! 💀\n")
            self.route_text.insert(tk.END, "Se escucha un triste rebuzno en el espacio...\n")
            self.route_text.see(tk.END)
            self.route_text.config(state=tk.DISABLED)
            
            self.next_step_btn.config(state=tk.DISABLED)
            self.feed_btn.config(state=tk.DISABLED)
            
            self.show_final_report()
    
    def end_journey(self):
        self.route_text.config(state=tk.NORMAL)
        self.route_text.insert(tk.END, f"\n🎉 ¡Viaje completado exitosamente! 🎉\n")
        self.route_text.see(tk.END)
        self.route_text.config(state=tk.DISABLED)
        
        self.next_step_btn.config(state=tk.DISABLED)
        self.feed_btn.config(state=tk.DISABLED)
        
        self.show_final_report()
    
    def show_final_report(self):
        if not self.current_burro:
            return
        
        status = self.current_burro.get_status()
        
        report_window = tk.Toplevel(self)
        report_window.title("Reporte Final del Viaje Científico - NASA")
        report_window.geometry("600x500")
        
        main_frame = ttk.Frame(report_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report_text = tk.Text(main_frame, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        report_text.insert(tk.END, "🚀 REPORTE FINAL DE MISIÓN ESPACIAL 🚀\n")
        report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        emoji = "💀" if not status['is_alive'] else "🎉"
        report_text.insert(tk.END, f"Estado final: {emoji} {'MISIÓN FALLIDA' if not status['is_alive'] else 'MISIÓN EXITOSA'}\n\n")
        
        report_text.insert(tk.END, "📊 ESTADÍSTICAS GENERALES\n")
        report_text.insert(tk.END, f"• Estrellas visitadas: {status['visited_stars_count']}\n")
        report_text.insert(tk.END, f"• Distancia total recorrida: {status['total_distance']:.1f} años luz\n")
        report_text.insert(tk.END, f"• Galaxia final: {status.get('current_galaxy', 'Vía Láctea')}\n")
        
        report_text.insert(tk.END, "\n📦 CONSUMO DE RECURSOS\n")
        report_text.insert(tk.END, f"• Pasto consumido: {status['total_food_consumed']:.1f} kg\n")
        report_text.insert(tk.END, f"• Pasto restante: {status['grass']:.1f} kg\n")
        report_text.insert(tk.END, f"• Tiempo de investigación: {status['total_research_time']:.1f} unidades\n")
        report_text.insert(tk.END, f"• Energía final: {status['current_energy']:.1f}%\n")
        report_text.insert(tk.END, f"• Vida restante: {status['remaining_life']:.1f} años luz\n")
        
        if status['research_effects']:
            report_text.insert(tk.END, "\n🔬 EFECTOS DE INVESTIGACIÓN\n")
            total_gain = sum(effect['effect'] for effect in status['research_effects'] if effect['effect'] > 0)
            total_loss = sum(effect['effect'] for effect in status['research_effects'] if effect['effect'] < 0)
            
            report_text.insert(tk.END, f"• Ganancia total de vida: +{total_gain:.1f} años luz\n")
            report_text.insert(tk.END, f"• Pérdida total de vida: {total_loss:.1f} años luz\n")
            report_text.insert(tk.END, f"• Balance neto: {total_gain + total_loss:+.1f} años luz\n")
            
            report_text.insert(tk.END, "\nÚltimos experimentos:\n")
            for effect in status['research_effects'][-5:]: 
                effect_str = f"+{effect['effect']}" if effect['effect'] > 0 else str(effect['effect'])
                report_text.insert(tk.END, f"  • {effect['star']}: {effect_str} años luz\n")
        
        report_text.insert(tk.END, "\n⭐ ESTRELLAS VISITADAS\n")
        constellations_visited = {}
        for star in self.current_burro.visited_stars:
            constellation = self.main_app.graph.get_constellation_for_star(star.id)
            const_name = constellation.name if constellation else "Desconocida"
            if const_name not in constellations_visited:
                constellations_visited[const_name] = []
            constellations_visited[const_name].append(star)
        
        for const_name, stars in constellations_visited.items():
            report_text.insert(tk.END, f"\n{const_name}:\n")
            for i, star in enumerate(stars, 1):
                galaxy = getattr(star, 'galaxy', 'Vía Láctea')
                effect = getattr(star, 'research_effect', 0)
                effect_str = f" (+{effect})" if effect > 0 else f" ({effect})" if effect < 0 else ""
                report_text.insert(tk.END, f"  {i}. {star.label} - {galaxy}{effect_str}\n")
        
        hypergiants_used = [star for star in self.current_burro.visited_stars if star.hypergiant]
        if hypergiants_used:
            report_text.insert(tk.END, "\n🌠 ESTRELLAS HIPERGIGANTES UTILIZADAS\n")
            for star in hypergiants_used:
                galaxy = getattr(star, 'galaxy', 'Vía Láctea')
                report_text.insert(tk.END, f"• {star.label} - {galaxy}\n")
        
        report_text.config(state=tk.DISABLED)
        
        def export_report():
            messagebox.showinfo("Exportar", "Funcionalidad de exportación en desarrollo")
        
        ttk.Button(report_window, text="Exportar Reporte", command=export_report).pack(pady=10)
    
    def show_route_info(self, route, total_distance=0):
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        
        if not route:
            self.route_text.insert(tk.END, "No se pudo calcular una ruta válida.\n")
            self.route_text.insert(tk.END, "Puede que haya obstáculos en el camino.\n")
            self.route_text.config(state=tk.DISABLED)
            return
        
        algorithm_type = self.algorithm_var.get()
        
        self.route_text.insert(tk.END, f"RUTA CALCULADA - {algorithm_type.upper()}\n")
        self.route_text.insert(tk.END, f"{'='*40}\n\n")
        
        self.route_text.insert(tk.END, f"Total de estrellas: {len(route)}\n")
        self.route_text.insert(tk.END, f"Distancia total: {total_distance:.1f} años luz\n")
        
        if algorithm_type == "max_stars":
            self.route_text.insert(tk.END, "Objetivo: Visitar la mayor cantidad de estrellas antes de morir\n")
        elif algorithm_type == "to_destination":
            self.route_text.insert(tk.END, "Objetivo: Ruta más corta al destino específico\n")
        elif algorithm_type == "optimal_route":
            self.route_text.insert(tk.END, "Objetivo: Máxima eficiencia de recursos (estrellas/consumo)\n")
        
        self.route_text.insert(tk.END, f"\nSecuencia de estrellas:\n")
        for i, star_id in enumerate(route):
            star = self.main_app.graph.get_star_by_id(star_id)
            if star:
                if i == 0:
                    prefix = "🚀 INICIO → "
                elif i == len(route)-1:
                    prefix = f"{i}. "
                    if algorithm_type == "optimal_route":
                        prefix += "🏁 FINAL (ÓPTIMO) → "
                    else:
                        prefix += "🏁 FINAL → "
                else:
                    prefix = f"{i}. "
                
                extra_info = ""
                if algorithm_type == "optimal_route" and i > 0:
                    prev_star_id = route[i-1]
                    distance = self.calculate_distance(prev_star_id, star_id)
                    if distance:
                        extra_info = f" [{distance} años luz]"
                
                self.route_text.insert(tk.END, f"{prefix}{star.label}{extra_info}\n")
        
        self.route_text.config(state=tk.DISABLED)
    
    def reset_journey(self):
        self.current_burro = None
        self.current_route = []
        self.current_star_index = 0
        self.next_step_btn.config(state=tk.DISABLED)
        self.feed_btn.config(state=tk.DISABLED)
        self.research_changes = {} 
        
        self.selected_start_star = None
        self.selected_end_star = None
        self.start_star_var.set("No seleccionada")
        self.end_star_var.set("No seleccionada")
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        self.route_text.insert(tk.END, "Información de la ruta aparecerá aquí...\n\n")
        self.route_text.config(state=tk.DISABLED)
        
        self.health_status_var.set("No iniciado")
        self.energy_status_var.set("0%")
        self.grass_status_var.set("0 kg")
        self.life_status_var.set("0 años luz")
        self.galaxy_var.set("Vía Láctea")
        self.hypergiant_var.set("0")
        
        if hasattr(self.main_app, 'canvas'):
            self.main_app.canvas.reset_highlight()
            self.main_app.canvas.delete("burro")