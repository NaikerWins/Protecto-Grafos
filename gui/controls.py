import tkinter as tk
from tkinter import ttk
from utils.constants import Constants

class ControlPanel(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.selected_star = None
        self.burro_data = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura el panel de controles"""
        # Título
        title_label = ttk.Label(self, text="Control de Misión", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Información del burro
        self.setup_burro_section()
        
        # Selección de estrella inicial
        self.setup_star_selection()
        
        # Configuración de algoritmo
        self.setup_algorithm_section()
        
        # Controles de viaje
        self.setup_travel_controls()
        
        # Información de ruta
        self.setup_route_info()
    
    def setup_burro_section(self):
        """Configura la sección de información del burro"""
        burro_frame = ttk.LabelFrame(self, text="Estado del Burro", padding=10)
        burro_frame.pack(fill=tk.X, pady=5)
        
        # Estado de salud
        ttk.Label(burro_frame, text="Estado de Salud:").grid(row=0, column=0, sticky=tk.W)
        self.health_var = tk.StringVar(value=Constants.HEALTH_EXCELLENT)
        health_combo = ttk.Combobox(burro_frame, textvariable=self.health_var,
                                   values=[Constants.HEALTH_EXCELLENT, Constants.HEALTH_GOOD, 
                                          Constants.HEALTH_POOR, Constants.HEALTH_DYING])
        health_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5)
        
        # Energía inicial
        ttk.Label(burro_frame, text="Energía Inicial:").grid(row=1, column=0, sticky=tk.W)
        self.energy_var = tk.StringVar(value="100")
        energy_entry = ttk.Entry(burro_frame, textvariable=self.energy_var, width=10)
        energy_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5)
        
        # Cantidad de pasto
        ttk.Label(burro_frame, text="Pasto (kg):").grid(row=2, column=0, sticky=tk.W)
        self.grass_var = tk.StringVar(value="300")
        grass_entry = ttk.Entry(burro_frame, textvariable=self.grass_var, width=10)
        grass_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5)
        
        # Edad inicial
        ttk.Label(burro_frame, text="Edad Inicial:").grid(row=3, column=0, sticky=tk.W)
        self.start_age_var = tk.StringVar(value="12")
        start_age_entry = ttk.Entry(burro_frame, textvariable=self.start_age_var, width=10)
        start_age_entry.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5)
        
        # Edad de muerte
        ttk.Label(burro_frame, text="Edad de Muerte:").grid(row=4, column=0, sticky=tk.W)
        self.death_age_var = tk.StringVar(value="3567")
        death_age_entry = ttk.Entry(burro_frame, textvariable=self.death_age_var, width=10)
        death_age_entry.grid(row=4, column=1, sticky=tk.W+tk.E, padx=5)
        
        burro_frame.columnconfigure(1, weight=1)
    
    def setup_star_selection(self):
        """Configura la selección de estrella inicial"""
        star_frame = ttk.LabelFrame(self, text="Selección de Estrella Inicial", padding=10)
        star_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(star_frame, text="Estrella Seleccionada:").pack(anchor=tk.W)
        
        self.selected_star_var = tk.StringVar(value="Ninguna")
        selected_label = ttk.Label(star_frame, textvariable=self.selected_star_var, 
                                  font=("Arial", 10, "bold"))
        selected_label.pack(fill=tk.X, pady=5)
        
        ttk.Label(star_frame, text="Haz clic en una estrella en el mapa para seleccionarla", 
                 font=("Arial", 8), foreground="gray").pack(anchor=tk.W)
    
    def setup_algorithm_section(self):
        """Configura la selección de algoritmo"""
        algo_frame = ttk.LabelFrame(self, text="Configuración de Ruta", padding=10)
        algo_frame.pack(fill=tk.X, pady=5)
        
        # Tipo de algoritmo
        ttk.Label(algo_frame, text="Tipo de Ruta:").grid(row=0, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="max_stars")
        
        max_stars_radio = ttk.Radiobutton(algo_frame, text="Máximo de Estrellas", 
                                         variable=self.algorithm_var, value="max_stars")
        max_stars_radio.grid(row=1, column=0, sticky=tk.W)
        
        optimal_radio = ttk.Radiobutton(algo_frame, text="Ruta Óptima", 
                                       variable=self.algorithm_var, value="optimal_route")
        optimal_radio.grid(row=2, column=0, sticky=tk.W)
    
    def setup_travel_controls(self):
        """Configura los controles de viaje"""
        control_frame = ttk.LabelFrame(self, text="Controles de Viaje", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Botón para calcular ruta
        self.calculate_btn = ttk.Button(control_frame, text="Calcular Ruta", 
                                       command=self.calculate_route)
        self.calculate_btn.pack(fill=tk.X, pady=2)
        
        # Botón para simular viaje
        self.simulate_btn = ttk.Button(control_frame, text="Simular Viaje", 
                                      command=self.simulate_journey)
        self.simulate_btn.pack(fill=tk.X, pady=2)
        
        # Botón para resetear
        self.reset_btn = ttk.Button(control_frame, text="Resetear Viaje", 
                                   command=self.reset_journey)
        self.reset_btn.pack(fill=tk.X, pady=2)
    
    def setup_route_info(self):
        """Configura la sección de información de ruta"""
        info_frame = ttk.LabelFrame(self, text="Información de Ruta", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Text area para información
        self.route_text = tk.Text(info_frame, height=15, width=30, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.route_text.yview)
        self.route_text.configure(yscrollcommand=scrollbar.set)
        
        self.route_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar texto inicial
        self.route_text.insert(tk.END, "Información de la ruta aparecerá aquí...\n\n")
        self.route_text.config(state=tk.DISABLED)
    
    def set_selected_star(self, star_id):
        """Establece la estrella seleccionada"""
        self.selected_star = star_id
        if self.main_app.graph:
            star = self.main_app.graph.get_star_by_id(star_id)
            if star:
                self.selected_star_var.set(f"{star.label} (ID: {star.id})")
    
    def update_burro_data(self, data):
        """Actualiza los datos del burro desde el archivo cargado"""
        self.burro_data = data
        
        # Actualizar controles
        self.health_var.set(data.get('health_state', Constants.HEALTH_EXCELLENT))
        self.energy_var.set(str(data.get('initial_energy', 100)))
        self.grass_var.set(str(data.get('grass', 300)))
        self.start_age_var.set(str(data.get('start_age', 12)))
        self.death_age_var.set(str(data.get('death_age', 3567)))
    
    def get_burro_data(self):
        """Obtiene los datos actuales del burro"""
        return {
            'health_state': self.health_var.get(),
            'initial_energy': float(self.energy_var.get()),
            'grass': float(self.grass_var.get()),
            'start_age': float(self.start_age_var.get()),
            'death_age': float(self.death_age_var.get())
        }
    
    def calculate_route(self):
        """Calcula la ruta basada en los parámetros actuales"""
        if not self.selected_star:
            tk.messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero")
            return
        
        algorithm_type = self.algorithm_var.get()
        self.main_app.calculate_route(self.selected_star, algorithm_type)
    
    def simulate_journey(self):
        """Simula el viaje completo"""
        if not self.selected_star:
            tk.messagebox.showwarning("Advertencia", "Selecciona una estrella inicial primero")
            return
        
        # Aquí se implementaría la simulación completa del viaje
        self.show_route_info(["Simulación", "en", "desarrollo..."])
    
    def reset_journey(self):
        """Resetea el viaje actual"""
        self.selected_star = None
        self.selected_star_var.set("Ninguna")
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        self.route_text.insert(tk.END, "Información de la ruta aparecerá aquí...\n\n")
        self.route_text.config(state=tk.DISABLED)
        
        if hasattr(self.main_app, 'canvas'):
            self.main_app.canvas.reset_highlight()
    
    def show_route_info(self, route):
        """Muestra información sobre la ruta calculada"""
        self.route_text.config(state=tk.NORMAL)
        self.route_text.delete(1.0, tk.END)
        
        if not route:
            self.route_text.insert(tk.END, "No se pudo calcular una ruta válida.\n")
            self.route_text.config(state=tk.DISABLED)
            return
        
        self.route_text.insert(tk.END, f"RUTA CALCULADA\n")
        self.route_text.insert(tk.END, f"{'='*30}\n\n")
        
        self.route_text.insert(tk.END, f"Total de estrellas: {len(route)}\n")
        self.route_text.insert(tk.END, f"Tipo de algoritmo: {self.algorithm_var.get()}\n\n")
        
        self.route_text.insert(tk.END, "Secuencia de estrellas:\n")
        for i, star_id in enumerate(route):
            star = self.main_app.graph.get_star_by_id(star_id)
            if star:
                prefix = "🚀 INICIO → " if i == 0 else f"{i}. "
                suffix = " ← FINAL 🏁" if i == len(route)-1 else ""
                self.route_text.insert(tk.END, f"{prefix}{star.label}{suffix}\n")
        
        self.route_text.config(state=tk.DISABLED)
    
    def reset_controls(self):
        """Resetea todos los controles"""
        self.reset_journey()