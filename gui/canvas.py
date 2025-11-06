import tkinter as tk
import math
from utils.constants import Constants

class StarCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.graph = None
        self.star_objects = {}
        self.connection_objects = {}
        self.scale_factor = 1.0
        self.offset_x = Constants.CANVAS_MARGIN
        self.offset_y = Constants.CANVAS_MARGIN
        
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)
    
    def on_resize(self, event):
        """Maneja el redimensionamiento del canvas"""
        self.calculate_scale_factor()
        if self.graph:
            self.draw_graph(self.graph)
    
    def calculate_scale_factor(self):
        """Calcula el factor de escala para ajustar las coordenadas"""
        canvas_width = self.winfo_width() - 2 * Constants.CANVAS_MARGIN
        canvas_height = self.winfo_height() - 2 * Constants.CANVAS_MARGIN
        
        if canvas_width > 0 and canvas_height > 0:
            self.scale_x = canvas_width / 200.0  # 200 um de ancho
            self.scale_y = canvas_height / 200.0  # 200 um de alto
            self.scale_factor = min(self.scale_x, self.scale_y)
    
    def draw_graph(self, graph):
        """Dibuja el grafo completo en el canvas"""
        self.graph = graph
        self.delete("all")
        self.star_objects.clear()
        self.connection_objects.clear()
        
        self.calculate_scale_factor()
        
        # Primero dibujar las conexiones
        self.draw_connections()
        
        # Luego dibujar las estrellas
        self.draw_stars()
    
    def draw_connections(self):
        """Dibuja las conexiones entre estrellas"""
        for constellation in self.graph.constellations:
            color = Constants.CONSTELLATION_COLORS[
                self.graph.constellations.index(constellation) % len(Constants.CONSTELLATION_COLORS)
            ]
            
            for star in constellation.stars:
                x1, y1 = self.transform_coordinates(star.coordinates['x'], star.coordinates['y'])
                
                for connection in star.linked_to:
                    connected_star = self.graph.get_star_by_id(connection['starId'])
                    if connected_star:
                        x2, y2 = self.transform_coordinates(
                            connected_star.coordinates['x'], 
                            connected_star.coordinates['y']
                        )
                        
                        # Verificar si la conexión está bloqueada
                        line_width = 1
                        line_color = color
                        dash_pattern = None
                        
                        if self.graph.is_edge_blocked(star.id, connected_star.id):
                            line_color = "red"
                            dash_pattern = (5, 2)
                        
                        # Dibujar la línea de conexión
                        line_id = self.create_line(
                            x1, y1, x2, y2,
                            width=line_width,
                            fill=line_color,
                            dash=dash_pattern,
                            tags="connection"
                        )
                        
                        # Guardar referencia
                        key = tuple(sorted([star.id, connected_star.id]))
                        self.connection_objects[key] = line_id
    
    def draw_stars(self):
        """Dibuja las estrellas en el canvas"""
        # Primero identificar estrellas en las mismas coordenadas
        coordinate_groups = {}
        for star in self.graph.get_all_stars():
            coord_key = (star.coordinates['x'], star.coordinates['y'])
            if coord_key not in coordinate_groups:
                coordinate_groups[coord_key] = []
            coordinate_groups[coord_key].append(star)
        
        # Dibujar las estrellas
        for constellation in self.graph.constellations:
            color = Constants.CONSTELLATION_COLORS[
                self.graph.constellations.index(constellation) % len(Constants.CONSTELLATION_COLORS)
            ]
            
            for star in constellation.stars:
                x, y = self.transform_coordinates(star.coordinates['x'], star.coordinates['y'])
                
                # CORRECCIÓN: Escalar mejor los radios pequeños
                base_radius = 8  # Radio base mínimo
                scaled_radius = base_radius + (star.radius * 10)  # Escalar radios pequeños
                
                # Determinar color
                fill_color = color
                
                # Si hay múltiples estrellas en la misma coordenada, usar rojo
                coord_key = (star.coordinates['x'], star.coordinates['y'])
                if len(coordinate_groups[coord_key]) > 1:
                    fill_color = "red"
                    scaled_radius += 3  # Hacerlas un poco más grandes
                
                # Si es hipergigante, hacerla más grande
                if star.hypergiant:
                    scaled_radius *= 1.8
                    outline_color = "gold"
                    outline_width = 3
                else:
                    outline_color = "black"
                    outline_width = 1
                
                # Asegurar tamaño mínimo
                scaled_radius = max(scaled_radius, 6)
                
                # Dibujar la estrella
                star_id = self.create_oval(
                    x - scaled_radius, y - scaled_radius,
                    x + scaled_radius, y + scaled_radius,
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width,
                    tags=f"star_{star.id}"
                )
                
                # Añadir etiqueta
                label_id = self.create_text(
                    x, y - scaled_radius - 12,
                    text=f"{star.label} (ID:{star.id})",
                    font=("Arial", 8),
                    tags=f"label_{star.id}"
                )
                
                self.star_objects[star.id] = {
                    'circle': star_id,
                    'label': label_id,
                    'x': x,
                    'y': y
                }
    
    def transform_coordinates(self, x, y):
        """Transforma coordenadas del mundo real a coordenadas del canvas"""
        canvas_x = self.offset_x + (x * self.scale_factor)
        canvas_y = self.offset_y + (y * self.scale_factor)
        return canvas_x, canvas_y
    
    def on_click(self, event):
        """Maneja clics en el canvas"""
        # Buscar si se hizo clic en una estrella
        clicked_star = self.find_star_at_position(event.x, event.y)
        if clicked_star:
            self.highlight_star(clicked_star)
            # Notificar al panel de control
            if hasattr(self.master, 'control_panel'):
                self.master.control_panel.set_selected_star(clicked_star)
    
    def find_star_at_position(self, x, y, tolerance=15):
        """Encuentra una estrella en la posición dada"""
        for star_id, star_data in self.star_objects.items():
            distance = math.sqrt((star_data['x'] - x)**2 + (star_data['y'] - y)**2)
            if distance <= tolerance:
                return star_id
        return None
    
    def highlight_star(self, star_id):
        """Resalta una estrella específica"""
        self.reset_highlight()
        
        if star_id in self.star_objects:
            star_data = self.star_objects[star_id]
            self.itemconfig(star_data['circle'], outline="yellow", width=3)
    
    def highlight_route(self, route):
        """Resalta una ruta completa"""
        self.reset_highlight()
        
        if not route:
            return
        
        # Resaltar estrellas de la ruta
        for i, star_id in enumerate(route):
            if star_id in self.star_objects:
                star_data = self.star_objects[star_id]
                color = "green" if i == 0 else "blue" if i == len(route)-1 else "orange"
                self.itemconfig(star_data['circle'], outline=color, width=3)
        
        # Resaltar conexiones de la ruta
        for i in range(len(route) - 1):
            star1_id, star2_id = route[i], route[i+1]
            key = tuple(sorted([star1_id, star2_id]))
            if key in self.connection_objects:
                self.itemconfig(self.connection_objects[key], fill="green", width=3)
    
    def reset_highlight(self):
        """Elimina todos los resaltados"""
        for star_data in self.star_objects.values():
            self.itemconfig(star_data['circle'], outline="black", width=1)
        
        for conn_id in self.connection_objects.values():
            self.itemconfig(conn_id, width=1)